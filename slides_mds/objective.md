# Objectives 

## Slide 0:
Thesis Title- from the report
Cover slide

2110099 Imdadullah Raji
2110062 Abdullah Al Mamun
BUET logo
Supervisor: Dr Md Ali
Dept of MechE 
BUET

## Slide 1: Introduction

### Content
The Feynman Lecture on Physics, Volume II Lecture 41(The Flow of Wet Water)
> The Test of science is its ability to predict. Had you never visited the earth, could you predict the thunderstorms, the volcanoes, the ocean waves, the auroras and the colorful sunset

- A video of leading edge vortex rolling up. `/home/raji/Research/Thesis/reports/predefense/assets/intro_viz.mp4`

- Thesis Title on Top

## Speaker Notes 

Navier-Stokes equation give us the higest fidelity representation of fluid flows. However, they give us surprisingly little insight into the flow physics in question. As Feynman asks, "could we predict the auroras?"
The question that concerns us here that could we see the 
vortices roll up like that by just looking at the equation? No, but we can indeed calculate: like this animation which came out of a calculation that took 2 hours on 6 cores. 


## Slide 2: Objective- Reduced-Order Models 


### Contents 
- A video of POD to which the speaker points to`/home/raji/ddse/pod_recon/outputs/academic_cycles`  
* The video background needs changing for slide integration.  The color palette might need changing, to match the report color palette. A contour overlay would be great, just like the report. `..assets/static_vorticity.png`

- Bullet points summarizing speech.

### Speaker Notes
However, we can only afford fractions of miliseconds when it comes to active flow control. Therefore the goal is to obtain some simplified model. One way to do it is trying to resolve the flow into observed patterns in space. Proper orthogonal decomposition shown here is one such technique. It describes flow as a summation of most energetic flow modes. The simulation data takes gigabytes in our computers, but this POD takes only 10 megabytes, and fractions of miliseconds to compute, $19 \mu s$ on a single core of my machine, to be exact. 

## Slide 3: Model based Active flow control

### Contents 
- The navier stokes eqn, $\dot{x} = f(x, u, t)$ and $\dot{x} = Ax+Bu$
- Then a $u = \text{controller}(x)$
- Some bullet points summarizing the taling point
- A reference to SINDy paper at the bottom.

### Speaker Notes 
After reducing the flow to a smaller  state vector x, we need a model for how those variables evolve under actuation, the f. (*points to the board*)
We first investigate whether a simple linear model is sufficient.(*point to the linear eqn*) 
As the dynamics are in fact nonlinear we can expect that to fail. Then nonlinear system identification tools can be employed. 
For example, Sparse Identification of Nonlinear Dynamics, or SINDy for short, identifies a nonlinear model directly from simulation data. The ultimate purpose is to obtain controller that maps state x to an actuation u.(*again points to the relevant eqn*)
