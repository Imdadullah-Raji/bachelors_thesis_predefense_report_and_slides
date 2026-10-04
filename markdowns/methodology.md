# Pre-defense report — Methodology

*Static NACA 0012, 2D laminar, Re = 500. Draft, 2026-09-27.*

All quantities are nondimensionalised by chord $c = 1$ and freestream speed
$U_\infty = 1$; time is in convective units $c/U_\infty$. Every number below was
read from the production case files or measured on the production mesh; the
source of each is listed in §6.

---

## 1. Flow solver

| item | setting |
|---|---|
| code | OpenFOAM (openfoam.org, development build `dev-84333c37c7aa`) |
| application | `foamRun`, solver module `incompressibleFluid` |
| flow model | incompressible, laminar (`simulationType laminar; model Stokes`) |
| kinematic viscosity | $\nu = 2\times10^{-3}$, i.e. $Re = U_\infty c/\nu = 500$ |
| dimensionality | 2D: one cell across a span of $0.1c$, front/back patches `empty` |
| pressure–velocity coupling | PIMPLE with `nOuterCorrectors 1` (PISO mode), `nCorrectors 2`, `nNonOrthogonalCorrectors 1`, `momentumPredictor yes` |
| pressure reference | `pRefCell 0`, `pRefValue 0` (kinematic pressure) |
| parallelisation | 6 MPI ranks, `scotch` decomposition |

### 1.1 Spatial discretisation (`fvSchemes`)

| term | scheme | order |
|---|---|---|
| time derivative | `backward` | 2nd, implicit |
| gradient | `Gauss linear` | 2nd |
| convection $\nabla\cdot(\phi\,\mathbf{U})$ | `Gauss linearUpwind grad(U)` | 2nd, upwind-biased |
| Laplacian | `Gauss linear corrected` | 2nd, explicit non-orthogonal correction |
| face interpolation | `linear` | 2nd |
| surface-normal gradient | `corrected` | 2nd |

### 1.2 Linear solvers (`fvSolution`)

| field | solver | smoother | tolerance | relTol |
|---|---|---|---|---|
| $p$ | GAMG | GaussSeidel | $10^{-7}$ | 0.01 |
| $p$ (final corrector) | GAMG | GaussSeidel | $10^{-8}$ | 0 |
| $\mathbf{U}$ | smoothSolver | symGaussSeidel | $10^{-8}$ | 0.01 |
| $\mathbf{U}$ (final) | smoothSolver | symGaussSeidel | $10^{-9}$ | 0 |

### 1.3 Why these settings

The settings were benchmarked, not taken as defaults. Each variant ran 50 steps
from an identical restart state on 4 cores, using the earlier 110k-cell
development mesh:

| variant | s/step | GAMG iterations/step |
|---|---|---|
| `nOuter 2, nCorr 2, nNonOrth 1` | 0.416 | 159 |
| `nOuter 2, nCorr 2, nNonOrth 0` | 0.650 | 143 |
| **`nOuter 1, nCorr 2, nNonOrth 1` (adopted)** | **0.176** | **53** |
| `nOuter 1, nCorr 3, nNonOrth 0` | 0.402 | 84 |
| adopted + GAMG coarsest-level / `pFinal` tuning | 0.176 | 50 |

* PISO (one outer corrector) is 2.4× cheaper than two outer correctors. It has no
  accuracy penalty at $Co<1$ with `backward` time differencing.
* Dropping the non-orthogonal corrector makes the run *slower*. The pressure solve
  converges worse on the 64° cells, so one corrector is kept.
* Tuning GAMG gave no measurable gain.

### 1.4 Boundary conditions and angle of attack

| patch | $\mathbf{U}$ | $p$ |
|---|---|---|
| `airfoil` (wall) | `noSlip` | `zeroGradient` |
| `farfield` | `freestreamVelocity`, $\mathbf{U}_\infty = (\cos\alpha,\ \sin\alpha)$ | `freestreamPressure`, $p_\infty = 0$ |
| `frontAndBack` | `empty` | `empty` |

The angle of attack is imposed by **rotating the freestream vector, not the
mesh**, so one mesh serves every angle. The angle enters in three places, all
written from one computation: the initial/far-field velocity, the
`liftDir`/`dragDir` vectors of `forceCoeffs`, and the `UInf` of the $C_p$
function object.

Force coefficients use $\rho_\infty = 1$, $|U_\infty| = 1$, $l_\text{ref} = c = 1$
and $A_\text{ref} = c \times \text{span} = 0.1$. They are written **every time step**,
through the initial transient as well.

### 1.5 Steady base flows (SIMPLE)

The 13 steady solutions ($\alpha = 0^\circ$–$24^\circ$ in $2^\circ$ steps) use the same case with
exactly two changes:

1. `ddtSchemes steadyState`, which runs SIMPLE for 6000 iterations.
2. Under-relaxation $\mathbf{U}$ 0.7 (equation) and $p$ 0.3 (field), with
   `nNonOrthogonalCorrectors 2`.

The convection scheme is kept at `linearUpwind` rather than the more robust
first-order `upwind`. The quantity of interest is $C_{L,\text{mean}} - C_{L,\text{steady}}$, and a
first- vs second-order mismatch would contaminate it directly. Convergence is
judged on the force history, not on residuals. As a check, the symmetric section
returns $C_L = 0.000000$ at $\alpha = 0^\circ$.

---

## 2. Time stepping

### 2.1 Policy

* **Fixed time step within every run** (`adjustTimeStep no`). $\Delta t$ changes
  only *between* restart chunks, never inside a running solve. The adaptive-$\Delta t$
  controller corrupted an earlier campaign.
* **Write times are exact multiples of $\Delta t$.** `writeInterval` is snapped
  *down* to an integer multiple of $\Delta t$ (`writeControl runTime`). This avoids
  `adjustableRunTime`, which would perturb $\Delta t$.
* Each $\Delta t$ change costs one first-order (Euler) step, because `backward`
  needs two old time levels and a restart supplies one.

### 2.2 Three-phase run

| phase | purpose | $\Delta t$ | fields written | length |
|---|---|---|---|---|
| 0 — impulsive start | uniform flow → $t = 0.5$; measure the settled Courant number | $4\times10^{-5}$ (12 500 steps) | none | $t \in [0, 0.5]$ |
| 1 — transient | reach the limit cycle | from phase-0 $Co$ (below) | one restart write per 20-unit chunk | until converged; $t \ge 60$, cap $t = 240$ |
| 2 — limit cycle | POD snapshot record | frozen at the phase-1 value | every $\approx T_\text{carrier}/32$ | 20 fundamental orbits |

**Choice of $\Delta t$.** The Courant number is measured at $t = 0.5$, never during
the impulsive start: $Co$ peaks near $t \approx 10^{-3}$ at about 7× its settled
value. The phase-1 step is then

$$\Delta t = 4\times10^{-5}\,\frac{0.35}{Co_\text{max}(t=0.5)},$$

clamped to $[2\times10^{-5},\ 6\times10^{-4}]$. Measured $Co_\text{max}(t=0.5)$ was
0.022–0.039. Between phase-1 chunks $\Delta t$ is re-tuned so that the chunk's maximum
Courant number sits at 0.75:

* it shrinks if $Co_\text{max} > 0.80$;
* it grows if $Co_\text{max} < 0.45$, by at most 1.5× per re-tune.

A diverged chunk is retried from its restart point at $\Delta t/2$, at most twice.

**The Courant number is not the stability limit on this mesh; the $\Delta t$ ceiling is.**
Mean $Co$ is about 1/166 of max $Co$, because the maximum is set by a handful
of trailing-edge cells. One run diverged at $Co_\text{max} = 0.60$ with
$\Delta t = 10^{-3}$. The failure came from the lagged non-orthogonal pressure
correction on the 64° cells, which grows with $\Delta t$ while $Co$ barely moves.
The ceiling $6\times10^{-4}$ sits below the largest step ever run to convergence
($6.33\times10^{-4}$).

**Onset-sweep angles ($12^\circ$–$18^\circ$)** run at one frozen
$\Delta t = 5.5726\times10^{-4}$ with re-tuning disabled. Growth rates are compared
across angles, and the scheme's numerical damping depends on $\Delta t$.

**Convergence gate (end of phase 1).** The trailing $C_L$ history is cut to a whole
number of fundamental periods and split at its midpoint. The mean, peak-to-peak
amplitude and frequency of the two halves must agree to 1%.

### 2.3 Per-angle values (production transient runs)

| $\alpha$ | $\Delta t$ | max $Co$ (phase 2) | write interval | samples / carrier period | orbit order | orbits | snapshots |
|---|---|---|---|---|---|---|---|
| 12° | 5.573e-4 | 0.27 | 90 Δt = 0.05015 | 32.3 | 1 | 20 | 645 |
| 14° | 5.573e-4 | 0.29 | 92 Δt = 0.05127 | 32.1 | 1 | 20 | 641 |
| 16° | 5.573e-4 | 0.32 | 95 Δt = 0.05294 | 32.3 | 1 | 19 | 645 |
| 18° | 5.573e-4 | 0.34 | 100 Δt = 0.05573 | 32.2 | 1 | 19 | 643 |
| 20° | 4.591e-4 | 0.35 | 130 Δt = 0.05968 | 32.1 | 1 | 31 | 1025 |
| 22° | 5.402e-4 | 0.51 | 122 Δt = 0.06590 | 32.2 | 1 | 20 | 644 |
| 24° | 5.488e-4 | 0.62 | 136 Δt = 0.07464 | 32.0 | 1 | 20 | 641 |
| 26° | 6.331e-4 | 0.78 | 124 Δt = 0.07850 | 32.2 | 2 | 20 | 1289 |
| 28° | 4.542e-4 | 0.51 | 183 Δt = 0.08311 | 32.1 | 2 | 20 | 1282 |
| 30° | 4.338e-4 | 0.73 | 224 Δt = 0.09717 | 32.2 | 2 | 20 | 1288 |

Mean $Co$ in phase 2 is 0.0016–0.0023 for every angle. "Orbit order" 2 means a
period-doubled wake: the orbit closes after two $C_L$ oscillations, so phase 2
runs twice as many carrier periods. The phase-1 restart write at $t_\text{conv}$
lies off the uniform snapshot grid and is excluded from the snapshot count and
from the POD set.

---

## 3. Computational mesh

### 3.1 Geometry and topology

* **Section.** NACA 0012 generated on a 200-point cosine distribution over
  $x \in [0, 0.98]$, then rescaled to unit chord. The result is a **blunt trailing
  edge of thickness $0.0082c$**, which lets a structured grid close around it.
* **Topology.** A structured three-block O-grid (upper, lower and wake blocks),
  built with gmsh transfinite surfaces, recombined to quadrilaterals and extruded
  one cell ($0.1c$) in span. The grid is **all-hexahedral**.
* **Domain.** A circle of radius $R = 30c$ centred at the quarter chord
  $(0.25c, 0)$.
* **Wake block.** Its half-angle at the far field is
  $\theta_w = \pi n_{te}/(2n_s + n_{te}) = 16.36^\circ$. That choice makes the far-field
  spacing uniform (0.536c everywhere) with no kink at the block interfaces.
* **One mesh for every angle.** The same mesh serves every $\alpha$ at $Re = 500$
  (identical `points`/`faces` checksums across all transient cases). The
  first-cell height scales as $h_1 = 0.05/\sqrt{Re}$, so the mesh is specific to
  $Re$.

### 3.2 Mesh statistics (production mesh `M2_ns160_nr180_b025`)

| quantity | value |
|---|---|
| cells | **63 360** hexahedra, $(2n_s + n_{te})\,n_r = (2\cdot160 + 32)\cdot180$ |
| — upper / lower / wake block | 28 800 / 28 800 / 5 760 |
| points / faces | 127 424 / 253 792 |
| cells along each airfoil surface, $n_s$ | 160 per side, clustered toward the LE and TE (gmsh `Bump`, coefficient 0.25) |
| cells across the blunt TE, $n_{te}$ | 32 |
| wall faces (airfoil patch) | 352 |
| radial cells, $n_r$ | 180 |
| first-cell wall-normal height, $h_1$ | $2.24\times10^{-3}c$ (design $0.05/\sqrt{500}$; measured 2.236–2.272 $\times10^{-3}c$ over all 352 wall stations) |
| radial growth ratio | 1.0347 (LE cut), 1.0346 (TE cuts), constant along each grid line |
| outermost radial cell | $\approx 1.0c$ |
| surface spacing | $2.07\times10^{-3}c$ at the LE, $7.95\times10^{-3}c$ maximum |
| TE-base spacing | $2.57\times10^{-4}c$, the smallest cell dimension in the mesh; sets $Co_\text{max}$ |
| far-field spacing | $0.536c$, uniform |
| max / mean non-orthogonality | 64.08° / 15.40° |
| max skewness | 0.821 |
| max aspect ratio | 7.50 |
| cell volume range | $5.98\times10^{-8}$ – $5.30\times10^{-2}$ ($c^2 \times$ span) |
| `checkMesh` | Mesh OK (1 region, all topology and geometry checks pass) |

### 3.3 Boundary-layer resolution

Reference thickness: the Blasius flat-plate estimate
$\delta_{99}(x) = 5x/\sqrt{Re_x}$, which gives $\delta_{99}(c) = 5/\sqrt{500} = 0.224c$ at
the trailing edge. Counts are **cells per wall-normal grid line** whose centroid
lies within $\delta_{99}$ of the wall. The mesh is structured, so every one of
the 352 wall stations has its own radial line of exactly 180 cells.

| station (upper surface) | local $\delta_{99}$ | cells inside $\delta_{99}$ |
|---|---|---|
| $x/c = 0.01$ | 0.022c | 10 |
| $x/c = 0.05$ | 0.051c | 22 |
| $x/c = 0.10$ | 0.070c | 28 |
| $x/c = 0.25$ | 0.112c | 33 |
| $x/c = 0.50$ | 0.158c | 36 |
| $x/c = 0.75$ | 0.194c | 42 |
| $x/c = 0.95$ | 0.218c | 47 |

* **Inside $\delta_{99}(c) = 0.224c$:** 44–49 cells per grid line, median 46,
  over all 352 stations.
* **Whole mesh:** 16 220 cells (26% of the mesh) lie within $0.224c$ of the
  wall.
* **Wider bands:** 22 946 cells lie within $0.5c$ and 29 274 within $1c$.

*Caveat for the committee:* Blasius is a zero-pressure-gradient, attached-flow
estimate. For $\alpha \gtrsim 12^\circ$ the boundary layer separates and the relevant
thickness is that of the separated shear layer, which is thicker. The figures
above are a resolution reference, not a measured boundary-layer thickness.

### 3.4 Figures

Each figure is saved as vector PDF and as a 600-dpi PNG in `figs/`. They are
regenerated by `scripts/render_mesh.py`, which reads the production `.msh`
directly. Block colours: blue = upper, orange = lower, green = wake.

![Full domain](figs/mesh_overview.png)
**Figure 1** — Full computational domain: 30c-radius O-grid, three structured blocks.

![Near field](figs/mesh_near.png)
**Figure 2** — Near field around the airfoil, showing the wake block leaving the blunt trailing edge.

![Leading edge](figs/mesh_le.png)
**Figure 3** — Leading-edge close-up: surface clustering and wall-normal stretching.

![Trailing edge](figs/mesh_te.png)
**Figure 4** — Trailing-edge region: the three blocks meet at the blunt base.

![Trailing-edge base](figs/mesh_te_base.png)
**Figure 5** — Blunt trailing-edge base: 32 cells across $0.0082c$. These are the smallest cells in the mesh.

![Boundary layer](figs/mesh_bl.png)
**Figure 6** — Mid-chord boundary layer with the Blasius $\delta_{99}(x)$ reference; 36 cells lie inside it at $x/c = 0.5$.

---

## 4. Initialisation and warm starts

* **Cold starts** begin from uniform freestream at the target angle.
* **Warm starts** copy a converged solution from another angle at the same $Re$
  with `mapFields -consistent`. This is an exact cell-to-cell copy, because the
  meshes are identical, and it is verified by checksum rather than assumed.
  The target keeps its own far-field boundary conditions; the velocity field is
  not rotated. The far field re-adjusts by advection within a few convective
  times.
* **Warm-start ladder.** Period-1 angles were marched 20° → 22° → 24°, and
  period-2 angles 30° → 28° → 26°.

---

## 5. Open items the committee is likely to raise

* **Mesh and time-step independence are not yet demonstrated at $Re = 500$ on
  this mesh.** The campaign log lists both as deferred. The only mesh study is
  in the upstream $Re = 1000$, $\alpha = 10^\circ$ campaign; I have not checked it
  for this report.
* **The period-2 angles were warm-started from the period-2 branch.** Bistability
  is therefore not excluded, and the onset bracket rests on the 24° and 25° cases.
* **Domain-size independence** ($R = 30c$) has not been tested. The mesher holds
  $h_1$ fixed when $R$ changes, so the test is ready to run.

---

## 6. Sources

| fact | file (relative to `Thesis/static_airfoil/`) |
|---|---|
| solver, schemes, linear solvers, BCs | `re500_aoa20/system/{controlDict,fvSchemes,fvSolution,functions}`, `0/U`, `0/p`, `constant/*` |
| steady settings | `steady_aoa20/system/*`, `make_steady.sh` |
| mesh file used | `re500_aoa20/log.gmshToFoam` → `meshes/M2_ns160_nr180_b025.msh` |
| mesh quality | `re500_aoa20/log.checkMesh` |
| mesh construction | `meshing/{mesher.py,mesh_math.py,airfoil.py}` |
| BL counts, spacings, growth ratios | computed from the `.msh` (column walk over the structured grid) |
| $\Delta t$ policy, thresholds | `run_staged.sh`, `FINDINGS.md` §1, §5, §15 |
| per-angle $\Delta t$, write interval, $Co$ | each case's `system/controlDict`, `log.phase0`, `log.phase2` |
| frequencies, orbits | `analysis/campaign_data.py` output |
| solver benchmarks | `FINDINGS.md` §2 |
