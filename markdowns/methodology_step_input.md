# Methodology — step change in angle of attack

## Numerical setup

A NACA 0012 airfoil is pitched nose-up about its quarter chord from
$\alpha = 0^\circ$, and the flow is followed as it relaxes. The flow is
two-dimensional, incompressible and laminar at $Re = 1000$ ($\nu = 10^{-3}$).
It is solved with OpenFOAM `foamRun` (`incompressibleFluid`) on a moving mesh.
The whole domain rotates as a rigid body about $x = 0.25c$ (arbitrary
Lagrangian–Eulerian, ALE), while the freestream stays fixed along $+x$. The
motion is a smootherstep ramp:

$$
\alpha(t) = \Delta\alpha\, s^{3}\left(6s^{2} - 15s + 10\right), \qquad s = \min(t/T,\ 1),
$$

which has $\dot\alpha = \ddot\alpha = 0$ at both ends of the ramp.

| case | $\Delta\alpha$ | ramp time $T$ | peak reduced pitch rate $k = \dot\alpha c/2U_\infty$ | simulated to |
|---|---|---|---|---|
| small step | $9.74^\circ$ (0.17 rad) | 0.5 | 0.319 | $t = 20$ |
| deep stall | $45^\circ$ | 2 | 0.368 | $t = 16.5$ |

Both runs start from the same converged $\alpha = 0^\circ$ flow field.

| item | setting |
|---|---|
| pressure–velocity coupling | PIMPLE: 2 outer correctors, 2 pressure correctors, 2 non-orthogonal correctors; flux corrected for mesh motion |
| time step | fixed, $\Delta t = 5\times10^{-4}$ |
| time derivative / convection / diffusion | second-order backward / linear upwind / central (Gauss linear, non-orthogonal correction) |
| linear solvers | $p$: GAMG, tolerance $10^{-7}$ on the final corrector; $\mathbf U$: symmetric Gauss–Seidel, tolerance $10^{-6}$ |
| boundary conditions | airfoil: no-slip; far field: freestream velocity and pressure; span: 2D (`empty`) |
| output | forces every time step; flow fields every 0.05 (every 0.0125 during the 45° ramp) |

## Mesh

The mesh is identical to the static-airfoil mesh (same file; point coordinates
agree to $10^{-13}$): a 63 360-cell structured O-grid of radius $30c$
(Fig. \ref{fig:mesh}). It was sized for $Re = 500$, so at $Re = 1000$ the
first-cell height ($2.24\times10^{-3}c$) is $\sqrt2$ coarser than the design rule
$h_1 = 0.05/\sqrt{Re}$ calls for. The boundary layer is still resolved by 36–42
cells per wall-normal line inside the Blasius $\delta_{99}(c) = 0.158c$.
