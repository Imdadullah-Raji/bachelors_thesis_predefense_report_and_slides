 

# 1 Background and Literature Review

## 1.1 Low Reynolds Number Airfoil Aerodynamics 
Traditionally the study of aerodynamic forces has been focused around large, fixed wings at high Reynolds numbers. However,  of late, there is a growing interest in the low Reynolds number regime $10^2<\text{Re}<10^4$ due to the development of mirco-aerial vehicles(MAVs) which naturally operate in a low Re regime. 

High Re flows over typical airfoils produce a thin boundary layer  and a thin wake. Historically this problem has been quite successfully tackled with potential flow theory. Most of the flow modeling and control has been done around the physics that is observed at these Reynolds numbers: laminar seperation, turbulent reattachment and stall at a critical angle.  By contrast, low Re flows are characterized by relatively thick boundary layers  and large wake behind the bodies. More importantly, at this flow regime, large coherent vortices are released from the leading edge that affect lift and drag significantly. As a consequence of these features the flow physics here is markedly different.  

![flightRegime](../figs/flightRegimeMap.png)


The above figure has been adapted from  Eldregde et al [[ARFM 2019 by Eldredge and Jones on LEV]] . It shows that steady flow over insect wings at low Reynolds number. Notably, on the left, the steady flow maximum lift coefficient on insect wings are almost half, or even quarter, of the unsteady maximum lift value.  This suggests that unsteady fluid dynamical effects are of consequence in lift generation. 

Research effort in the investigation of low Re laminar flows over airfoils have been on the rise for last two decades. Our review of the problem can be summarized in three seperate threads: dynamical  description of stationary airfoil from experimental and numerical studies, leading-edge vortex(LEV) dynamics of manuvering airfoils and reduced-order modeling of dynamics.   

## 1.2 Dynamical Regimes of Stationary Airfoil Wake

### 1.2.1 Studies with 2D Numerical Simulations
In low Re, the boundary layer easily seperates and forms a free shear layers, which roll up into vortices due to Kelvin-Helmholtz instability. *Alam* et al. (2010) studied the NACA0012 wake characteristics at Re= 5300 using Laser-induced Fluoroscence(LIF) visualization. They observed that suction side boundary layer seperation point moves up to the leading edge as angle of attack is increased. Kurtuluş(2016) carried out 2D numerical investigations on NACA0012 airfoil profile at Re = 1000 using the finite volume code ANSYS Fluent. She identified five modes in the flow based on wake vortex patterns.
-  **Mode 1:** continuous vortex sheet mode ($0<\alpha<8^{\circ}$) 
-  **Mode 2:** alernating vortex shedding mode $(8^\circ<\alpha<22^\circ)$
-  **Mode 3:** alternating vortex pair shedding mode $(31^\circ<\alpha<41^\circ)$
- **Mode 4:**: alternating single vortex with vortex pair shedding mode($29^\circ<\alpha<30^\circ$$)
- **Mode 5:** bluff body vortex shedding mode $( 50^\circ<\alpha<90^\circ )$

Durante et al(2020) studied this further using Discrete Vortex Hydrodynamics(DVH) numerical method and analyzed the results in a dynamical systems framework-- using phase portraits constructed from time varying aerodynamic loads. They found period tripling and transition to chaos within Kurtulus Mode 3.  However, at these higher angles of attack 3D spanwise instabilities develop and the very physicality of 2D Navier-Stokes is in question. There are recent studies addressing this very question, which is discussed in $\S 1.2.2$ 
### 1.2.2 3D Numerical Simulations and Experiments

[[Gupta,Zhao,2D3D Wake Transition of NACA0012 Airfoil]] Gupta et al(2023)  investigated whether the flow patterns suggested from 2D simulations by previously mentioned papers are realizable in 3D at all. They used water-channel experiments and numerical Floquet stability analysis using a 2D spectral element method(SEM) code.  

![Gupta3DInstability](../figs/guptaSpanwiseInstability.png)

>Figure Caption: 3D spanwise instability and corresponding 2D solution. Reused from Gupta et al(2023)

Their principal find is that the onset of 3D spanwise instability sits within the von Karman vortex shedding zone( Kurtulus mode 2), just before i transitions to a vortex pair shedding zone(Kurtulus mode 3) via a period doubling bifurcation of cycles.  For example, for $\text{Re} = 500$ the onset of 3D instability is at $\alpha_{3D} \approx 18.5$, but the 2D period doubling bifurcation happens at around $24^\circ \textasciitilde 25^\circ$ .  Their results suggest that the critical angle for the onset of 3D instability varies as the inverse square root of Re, $\alpha_{3D} \textasciitilde \text{Re}^{-0.5}$.  They classified the spanwise instability following the floquet analysis done in the 90s on wake stability of circular cylinder by Charles Willamson(1994),  Barkley and Henderson [[Barkley and Henderson 1996 JFM  cylinder 3D instability]]. These instabilities causes the vortex tube to develop waviness along their centerline, different wavelengths have different growth characteristics.
Williamson ordered these 3D instability modes of circular cylinders as mode A, B and C, by the order of their emergence.  His mode A corresponded to a spanwise instability wavelength of the order of 3-4 cylinder diameters; mode B corresponds to a shorter wavelength, both are synchronous with the base 2D vortex shedding period $T$. Mode C instability, by contrast, is period doubled and repeats after $2T$. Interestingly, for the airfoils it is the mode C instability that appears first, whereas mode A appears first for the cylinder.   

![ModeC](../figs/williamsonModeC.png)

![ModeAB](../figs/williamsonModeAB.png)
>Fig Caption: Spanwise instabilities in flow past a cylinder. The airfoil 3D instabilities develops by mode C, as discussed by Gupta et al. Taken from *Williamson* 1996 Annu. Rev. Fluid. Mech. Vortex Dynamics in the Cylinder Wake 
## 1.3 Rapid Motions of Airfoil and Leading Edge Vortex Dynamics 


### 1.4 Reduced-Order Modeling and Data-driven Techniques

Reduced-order models, that can be used in real time to predict the aerodynamic response in real time is essential for active flow control. 
Such models can be developed from either first prinicples or from empirical, data-driven apporaches. 



