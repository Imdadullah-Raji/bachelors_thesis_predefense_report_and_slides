# Literature Review

## Slide 1: 2D Wake Structure at Ultra Low Re

### Content:
- Five Kurtulus Modes taken right out of the paper. See `assets` folder. I know the color of the original paper plots are terrible, we need to live with it. Do some crops/clean ups where need be. 
- An animation of mode 2 and 3. You can make it from aoa14 and aoa26 in the `/home/raji/Research/Thesis/static_airfoil`. The tools are at the `flowkit` conda env, and `research` env. Feel free to use the other envs too.
- Reference. Kurtulus D.F. On the wake pattern of symmetric airfoils for different incidence angles at Re = 1000. IJMAV 2016. (match the references.tex)

### Speakers Note. 
Violent mixing of turbulent flow is absent at low Reynolds number laminar flows. As a result, large vortices can exist for long without breaking up into smaller ones. In this regime, the shear layer is thick, the wake is broad and large vortices interact with each other to produce such intricate flow structure. This structure was computationally studied by Kurtulus. She studied a NACA0012 airfoil and classified the observed flow structures into 5 modes according to the wake vorticity pattern. 
First, the attached flow. Second, von-karman like vortex street. Third, alternating vortex pair shedding mode. Fourth, alternate vortex with single vortex shedding; Fifth bluff body vortex shedding. 


## Slide 2: Dynamic Systems lens, period doubling, tripling, chaos

### Content
- No video here, just images. Take the images directly from the paper. A period doubled force history, a single period one, a period doubled. Corresponding fourier and phase portrait. And a chaotic one.
- Reference of course. 

### Speakers Note

Looking at the force histories also reveal the temporal pattern. Durante et al looked the time series of force coefficient at Re = 1000, its phase portrait and fourier amplitudes. 

Initially the force peaks are single, the phase portrait is a single loop. Then it transitions into a small and large peak near $\alpha=22^\circ$, the phase potrait contains two loops. The fourier mode develops an amplitude at the subharmonic.

 Additionally period three and aperiodic chaotic flow is also observed.



## Slide 3: Reality of 2D simulation and Stability analysis.

### Content
- Add the flow regimes map from the paper.
- CHK Williamsons Vortex Dynamics review paper photo. Find that at `/home/raji/research/Notes/airfoil_notes/`
- References. Keep CHK williams one line, and for the other the usual format. 

### Speakers Note
In reality, 3D spanwise instability develops, in the same way the symmetric wake of a symmetric cylinder goes unsteady and develops the von-Karman vortex street. 

This instability develops as a corrugations of different wavelengths in the spanwise direction. The photo here is from Williamsons 1996 review paper on cylinder wake vortex dynamics. 
[*pointing Photo from Williamsons 1996 Annu Rev Fluid Mech paper*]

Gupta et al investigated  3D instability at Re=1000 by numerical study and water channel experiments. They observed similar instability mechanisms like that of cylinder wakes.  They found that onset of 3D instability varies as the inverse square root of reynolds number. Which sits before all the period doubling bifurcations reported in 2D simulations. 


## Silde 4: Pitching Airfoil and LEV

### Content. 
- Reference eldredge
- Kutta Joukowski theorem eqn
- The video, `assets/lev_exp_vid.mp4`
- The figure: assets/pitching_plate. 


### Speakers Note. 

- Brief explanation of added mass lift, circulatory lift from the video. 
- The fact that rapid manuver produces tighter vortex and higher lift. 
- or i will make it up. I mean I am so sleepy now that I am high. 