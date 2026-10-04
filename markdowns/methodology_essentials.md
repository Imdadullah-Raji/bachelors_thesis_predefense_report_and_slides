# Methodology

## Numerical setup

The flow around a static NACA 0012 airfoil is simulated as two-dimensional,
incompressible and laminar at $Re = U_\infty c/\nu = 500$. The code is OpenFOAM
(development build), using the `foamRun` application with the
`incompressibleFluid` solver module. All quantities are nondimensionalised by
the chord $c$ and freestream speed $U_\infty$. The angle of attack is imposed by
rotating the freestream vector, so one mesh serves every angle.

| item | setting |
|---|---|
| pressure–velocity coupling | PISO (PIMPLE, 1 outer corrector), 2 pressure correctors, 1 non-orthogonal corrector |
| time derivative | second-order implicit backward |
| convection | second-order linear upwind |
| gradient, Laplacian | second-order central (Gauss linear, non-orthogonal correction) |
| linear solvers | $p$: GAMG, tolerance $10^{-8}$ on the final corrector; $\mathbf U$: symmetric Gauss–Seidel, tolerance $10^{-9}$ |
| boundary conditions | airfoil: no-slip; far field: freestream velocity and pressure; span: 2D (`empty`) |

## Time stepping

The time step is fixed within each run; adaptive time stepping is disabled.
Each run has three phases:

1. **Start-up.** An impulsive start at $\Delta t = 4\times10^{-5}$ up to $t = 0.5$.
2. **Transient.** The step is chosen from the Courant number measured at the end
   of start-up, capped at $\Delta t \le 6\times10^{-4}$. The run advances until
   the lift history reaches a limit cycle: over two consecutive windows, its
   mean, amplitude and frequency must agree to 1%.
3. **Snapshot record.** Twenty limit-cycle periods, with 32 snapshots per
   shedding period.

Production time steps were $\Delta t = 4.3$–$6.3\times10^{-4}$, and the maximum
Courant number stayed below 0.8.

## Mesh

The computational domain is a circle of radius $30c$. It is discretised by a
structured, all-quadrilateral three-block O-grid (Fig. 1). The trailing edge
is truncated to a blunt base $0.0082c$ thick.

| quantity | value |
|---|---|
| total cells | 63 360 |
| cells on each surface / across the TE base / radial | 160 / 32 / 180 |
| first-cell height | $2.24\times10^{-3}c$ |
| radial growth ratio | 1.035 |
| cells inside the boundary layer ($\delta_{99} = 0.224c$ at $x = c$) | 44–49 per wall-normal line |
| max non-orthogonality / skewness / aspect ratio | 64° / 0.82 / 7.5 |

```latex
\begin{figure*}[t]
  \centering
  \includegraphics[width=\textwidth]{figs/mesh_figure.pdf}
  \caption{Computational mesh (63\,360 cells). (a) Full O-grid domain of
  radius $30c$; the three structured blocks are shaded. (b) Near field, with
  close-ups of the leading edge and the blunt trailing edge.}
  \label{fig:mesh}
\end{figure*}
```
