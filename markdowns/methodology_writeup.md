
Two kinds of numerical investigations were undertaken: steady airfoil at different angles of attack, pitching airfoil according to a prescribed rotational motion $\alpha(t)$. The finite-volume code OpenFOAM( specifically Foundation OpenFOAMv13) was used to set up both kinds of simulation.{Ref to original 1998 paper by Weller et al} . 
## Static NACA0012 Airfoil
### Mesh 
Both for the stationary and pitching airfoils the computational domain is a disk of radius $30c$. The mesh is discretized using transfinite interpolation, with all quadrilateral elements throughout.  An overview and close up is provided in Fig < fig num>.  

![mesh_fig](figs/mesh_figure.png)

To keep the boundary layer sufficiently resolved the first cell height is taken as a function of the Reynolds number, $h1 = 0.05/\sqrt{\text{Re}}$, which is approximately the 1/100th of the Blasius boundary layer thickness for a flat plate. 

| quantity | value |
|---|---|
| total cells | 63 360 |
| cells on each surface / across the TE base / radial | 160 / 32 / 180 |
| first-cell height | $2.24\times10^{-3}c$ |
| radial growth ratio | 1.035 |
| cells inside the boundary layer ($\delta_{99} = 0.224c$ at $x = c$) | 44–49 per wall-normal line |
| max non-orthogonality / skewness / aspect ratio | 64° / 0.82 / 7.5 |

For the steady cases, the angle of attack $\alpha$ is changed by rotating the freestream direction. For pitching cases the whole mesh is rotated rigidly around a pivot. 

### Solver Setup

As the flow regime is laminar, the smallest relevant scale to resolve is the shear layer near the no-slip wall. The governing equations were solved directly, no turbulence models were employed. 

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

## Pitching NACA0012 

### Airfoil Motion Using Arbitrary Langrangian Eulerian
The same mesh topology as the static case is reused for the pitching airfoil. The circular symmetry of the O-grid is exploited to implement pitching motion. The entire mesh rotates relative to the flow and the time derivatives in the moving mesh are converted to the stationary coordinate frame, a technique known as Arbitrary Lagrangian Eulerian(ALE).

$$ \left. \frac{\partial \phi}{\partial t} \right|_\xi = \left. \frac{\partial \phi}{\partial t} \right|_x + \sum_{i} \frac{\partial \phi}{\partial x_i} \left. \frac{\partial x_i}{\partial t} \right|_\xi = \left. \frac{\partial \phi}{\partial t} \right|_x +\mathbb{u_m}\cdot\nabla\phi$$

Here $\mathbb{u_m}$ is the mesh motion, in the rigid body rotation case this is given by 
$$\mathbb{u_m} = \mathbb{\Omega}\times\mathbb{r}$$

For our 2D case $\mathbb{\Omega}(t) = \alpha(t)\hat{k}$
, where $\alpha(t)$ is a prescribed rotational dispplacement function. 

This transformation changes the material derivative $D\mathbb{u}/Dt$ and hence the Navier Stokes momentum equation as follows. 
$$\frac{\partial u}{\partial t} +((u-u_m)\cdot\nabla)u = -\nabla p + \mu \nabla^2u$$


### Solver Setup 

Each unsteady simulation is started from a converged 
steady flow solution at $\alpha=0$, which is obtained using the steady state SIMPLE algorithm. Then the transient PIMPLE algorithm is used to calculate the time evolving pressure and velocity fields. 

For the pitch-up input function a continously differentiable approximation to unit step function is used. 
$$
\alpha(t) = \Delta\alpha\, s^{3}\left(6s^{2} - 15s + 10\right), \qquad s = \min(t/T,\ 1) 
$$
This $\alpha(t)$ has $\dot{\alpha}=\ddot{\alpha}=0$ at the beginning and at the end of the manuver, which avoids the singularity associated with the step function, ensuring numerical stability. 

| item | setting |
|---|---|
| pressure–velocity coupling | PIMPLE: 2 outer correctors, 2 pressure correctors, 2 non-orthogonal correctors; flux corrected for mesh motion |
| time step | fixed, $\Delta t = 5\times10^{-4}$ |
| time derivative / convection / diffusion | second-order backward / linear upwind / central (Gauss linear, non-orthogonal correction) |
| linear solvers | $p$: GAMG, tolerance $10^{-7}$ on the final corrector; $\mathbf U$: symmetric Gauss–Seidel, tolerance $10^{-6}$ |
| boundary conditions | airfoil: no-slip; far field: freestream velocity and pressure; span: 2D (`empty`) |
| output | forces every time step; flow fields every 0.05 (every 0.0125 during the 45° ramp) |