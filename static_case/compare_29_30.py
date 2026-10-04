#!/usr/bin/env python3
"""Compare the converged 29° and 30° force/surface outputs."""
import csv
import json
import os
from pathlib import Path

import numpy as np
os.environ.setdefault('MPLCONFIGDIR','/tmp/thesis-matplotlib')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

import make_figures as base

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
DATA=HERE/'data'
FIGS=HERE/'figures'
ANGLES=(29,30)
COLORS={29:'#D55E00',30:'#0072B2'}

def pressure_force(angle,surface):
    root=base.SERIES[angle][3]/'surfaces'
    raw=np.loadtxt(next(root.glob('*/airfoil.xy')))
    fx=fy=0.
    for side in ('upper','lower'):
        x,cp,_=surface[side]
        points=raw[(raw[:,1]>0 if side=='upper' else raw[:,1]<0)&(raw[:,0]<1-1e-8)]
        points=points[np.argsort(points[:,0])]
        if not np.allclose(points[:,0],x,atol=1e-8):
            raise ValueError('Surface coordinates disagree with mean profile')
        slope=np.gradient(points[:,1],points[:,0],edge_order=2)
        fx+=np.trapezoid(cp*slope,x)*(1 if side=='upper' else -1)
        fy+=np.trapezoid(cp,x)*(-1 if side=='upper' else 1)
    theta=np.deg2rad(angle)
    return (-fx*np.sin(theta)+fy*np.cos(theta),fx*np.cos(theta)+fy*np.sin(theta))

def folded_lift(angle):
    a,_,d,_=base.SERIES[angle]
    period=1/d['St_orbit']
    phase=np.linspace(0,1,1024,endpoint=False)
    start=d['t_end']-4*period
    y=np.stack([np.interp(start+(k+phase)*period,a[:,0],a[:,2]) for k in range(4)])
    average=y.mean(axis=0)
    shifted=np.roll(average,-np.argmax(average))
    return np.r_[phase,1],np.r_[shifted,shifted[0]],float(np.max(np.ptp(y,axis=0)))

def main():
    rows={int(r['alpha']):r for r in csv.DictReader((DATA/'angle_statistics.csv').open())}
    for angle in ANGLES:
        d={k:(float(v) if k not in ('alpha','source','source_path','window_source','stationary') else v)
           for k,v in rows[angle].items()}
        d['alpha']=angle
        d['orbits']=int(d['orbits'])
        folder=ROOT/d['source_path']
        a,_=base.load_force(folder)
        base.SERIES[angle]=(a,base.cut(a,d['t_start'],d['t_end']),d,folder)
    surfaces={angle:base.surface_mean(angle) for angle in ANGLES}
    for side in ('upper','lower'):
        if not np.allclose(surfaces[29][side][0],surfaces[30][side][0],atol=1e-8):
            raise ValueError('29° and 30° surface grids differ')

    famps={angle:base.fft_data(angle) for angle in ANGLES}
    pressure={angle:pressure_force(angle,surfaces[angle]) for angle in ANGLES}
    dcl=float(rows[30]['cl_mean'])-float(rows[29]['cl_mean'])
    dcd=float(rows[30]['cd_mean'])-float(rows[29]['cd_mean'])
    dclp=pressure[30][0]-pressure[29][0]
    dcdp=pressure[30][1]-pressure[29][1]

    base.style()
    fig,axes=plt.subplots(2,2,figsize=(7.1,6.0))
    ax=axes[0,0]
    for angle in ANGLES:
        f,amp,d=famps[angle]
        m=(f>0)&(f<1.4)
        ax.semilogy(f[m],amp[m],color=COLORS[angle],lw=1.0,label=rf'${angle}^\circ$')
        ax.axvline(d['St_orbit'],color=COLORS[angle],ls=':',lw=.8)
        ax.axvline(d['St_carrier'],color=COLORS[angle],ls='--',lw=.8)
    ax.set(xlim=(0,1.4),ylim=(1e-5,1),xlabel=r'$f c/U_\infty$',ylabel=r'Lift amplitude $A_{C_L}$',title='(a) Converged lift spectra')
    ax.legend(loc='upper right',title=r'Dotted: $f_0$; dashed: $f_c$',title_fontsize=7)
    ax.grid(alpha=.15)

    ax=axes[0,1]
    for angle in ANGLES:
        for side,ls in [('upper','-'),('lower','--')]:
            x,cp,_=surfaces[angle][side]
            ax.plot(x,cp,color=COLORS[angle],ls=ls,lw=1.3,label=rf'${angle}^\circ$ {side}')
    ax.invert_yaxis();ax.set(xlim=(0,1),xlabel=r'$x/c$',ylabel=r'$\overline{C}_p$',title='(b) Mean pressure distribution')
    ax.legend(ncol=2,fontsize=6.6);ax.grid(alpha=.15)

    ax=axes[1,0]
    for side,color,ls in [('upper',base.BLUE,'-'),('lower',base.RED,'--')]:
        x,c29,_=surfaces[29][side]
        _,c30,_=surfaces[30][side]
        ax.plot(x,c30-c29,color=color,ls=ls,lw=1.35,label=side.capitalize())
    ax.axhline(0,color='0.45',lw=.65)
    ax.set(xlim=(0,1),xlabel=r'$x/c$',ylabel=r'$\Delta\overline{C}_p$ (30° − 29°)',title='(c) Pressure change across the chord')
    ax.legend();ax.grid(alpha=.15)

    ax=axes[1,1]
    for angle in ANGLES:
        phase,y,_=folded_lift(angle)
        ax.plot(phase,y,color=COLORS[angle],lw=1.4,label=rf'${angle}^\circ$')
    ax.set(xlim=(0,1),xlabel=r'Orbit phase (largest lift peak at 0)',ylabel=r'$C_L$',title='(d) Lift waveform over one orbit')
    ax.legend();ax.grid(alpha=.15)
    fig.subplots_adjust(left=.11,right=.98,bottom=.10,top=.92,hspace=.40,wspace=.32)
    fig.suptitle(r'Re=500: the 29° → 30° change',fontsize=11)
    fig.savefig(FIGS/'07_29_vs_30.pdf')
    fig.savefig(FIGS/'07_29_vs_30.png',dpi=600)
    plt.close(fig)

    info={'angles':{a:{'cl_mean':float(rows[a]['cl_mean']),'cd_mean':float(rows[a]['cd_mean']),
                       'f_orbit':float(rows[a]['St_orbit']),'f_carrier':float(rows[a]['St_carrier']),
                       'A_half_over_A_carrier':float(rows[a]['half_carrier_amplitude_ratio']),
                       'pressure_lift_without_trailing_edge':pressure[a][0],
                       'pressure_drag_without_trailing_edge':pressure[a][1],
                       'surface_window':surfaces[a]['window'],
                       'phase_orbit_scatter_max':folded_lift(a)[2]} for a in ANGLES},
          'delta_total_lift':dcl,'delta_total_drag':dcd,
          'delta_pressure_lift_without_trailing_edge':dclp,
          'delta_pressure_drag_without_trailing_edge':dcdp,
          'pressure_fraction_of_lift_jump':dclp/dcl,
          'pressure_fraction_of_drag_jump':dcdp/dcd,
          'surface_grid_match':True}
    (DATA/'comparison_29_30.json').write_text(json.dumps(info,indent=2))
    print(json.dumps(info,indent=2))

if __name__=='__main__':main()
