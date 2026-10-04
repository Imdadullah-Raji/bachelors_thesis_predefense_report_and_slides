#!/usr/bin/env python3
"""Reproduce the fixed-angle Re=500 predefense figures from raw outputs."""
from pathlib import Path
import os, sys, json, csv, re
os.environ.setdefault('MPLCONFIGDIR', '/tmp/thesis-matplotlib')
import numpy as np
from scipy.optimize import minimize_scalar
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.backends.backend_pdf import PdfPages

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT/'static_airfoil/analysis'))
from limit_cycle import spectral_structure
OUT = HERE/'figures'
DATA = HERE/'data'
BLUE, RED, GREEN = '#0072B2', '#D55E00', '#009E73'
SERIES = {}
STATS = []

def load_force(folder):
    files = sorted((folder/'forceCoeffs').glob('*/*.dat'), key=lambda p: float(p.parent.name))
    chunks = []
    for file in files:
        with file.open() as stream:
            header=''.join(next(stream) for _ in range(9))
        for key,expected in [('magUInf',1.),('lRef',1.),('Aref',.1)]:
            match=re.search(rf'#\s*{key}\s*:\s*(\S+)',header)
            if match is None or not np.isclose(float(match[1]),expected):
                raise ValueError(f'Unexpected {key} normalization in {file}')
        a = np.loadtxt(file, usecols=(0, 2, 3), ndmin=2)
        if not np.isfinite(a).all():
            raise ValueError(f'Nonfinite force data: {file}')
        # A later restart supersedes any old samples at/after its first time.
        if chunks:
            chunks = [c[c[:, 0] < a[0, 0]] for c in chunks]
        chunks.append(a)
    a = np.concatenate(chunks)
    a = a[np.argsort(a[:, 0], kind='stable')]
    a = a[np.r_[np.diff(a[:, 0]) > 0, True]]
    return a, files

def mean(t, v):
    return np.trapezoid(v, t, axis=0)/(t[-1]-t[0])

def cut(a, start, end):
    times = np.r_[start, a[(a[:,0]>start)&(a[:,0]<end),0], end]
    return np.column_stack([times]+[np.interp(times,a[:,0],a[:,i]) for i in (1,2)])

def analyze():
    cases = [(int(p.name.split('aoa')[1]),p/'postProcessing','even')
             for p in (ROOT/'static_airfoil').glob('re500_aoa*') if p.is_dir()]
    cases += [(int(p.name.split('aoa')[1]),p,'odd')
              for p in (ROOT/'downloads/Re500/postProcessBundleOddAngles').glob('re500_aoa*')]
    for alpha, folder, source in sorted(cases):
        a, files = load_force(folder)
        end = a[-1,0]
        marker = folder.parent/'.phase2'
        if source == 'even' and marker.exists():
            start = float(dict(x.split('=',1) for x in marker.read_text().splitlines())['T_CONV'])
            window_source = '.phase2 T_CONV'
        elif source == 'even':
            start = {20:60.5,30:120.5}[alpha]
            window_source = 'campaign documented phase-2 start'
        else:
            start = float(files[-1].parent.name)
            window_source = 'last restart segment; stationarity checked below'
        z = cut(a, start, end)
        shedding = np.ptp(z[:,2]) > 1e-3
        f0 = fc = ratio = 0.
        order = cycles = 0
        residual = 0.
        if shedding:
            tu = np.arange(start,end,.005)
            yu = np.interp(tu,a[:,0],a[:,2])
            f0,fc,order,ratio = spectral_structure(tu,yu)
            trial_t = np.linspace(start,end-1.15/f0,10000)
            def objective(period):
                return np.mean((np.interp(trial_t,a[:,0],a[:,2])-np.interp(trial_t+period,a[:,0],a[:,2]))**2)
            fit = minimize_scalar(objective,bounds=(.90/f0,1.10/f0),method='bounded',options={'xatol':1e-10})
            f0 = 1/fit.x
            fc = order*f0
            residual = np.sqrt(fit.fun)/np.ptp(z[:,2])
            cycles = int((end-start)*f0)//2*2
            if cycles<4: raise ValueError(f'Too few complete orbits: {alpha}')
            start = end-cycles/f0
            z = cut(a,start,end)
        half = (start+end)/2
        za,zb = cut(a,start,half),cut(a,half,end)
        cl,cd = mean(z[:,0],z[:,2]),mean(z[:,0],z[:,1])
        mean_drift = abs(mean(za[:,0],za[:,2])-mean(zb[:,0],zb[:,2]))/max(abs(cl),1e-8)
        amp_drift = abs(np.ptp(za[:,2])-np.ptp(zb[:,2]))/max(np.ptp(z[:,2]),1e-8) if shedding else 0
        carrier_residual=0.
        half_ratio=0.
        if shedding:
            tq=np.linspace(start,end-1/fc,8000)
            carrier_residual=np.sqrt(np.mean((np.interp(tq,a[:,0],a[:,2])-np.interp(tq+1/fc,a[:,0],a[:,2]))**2))/np.ptp(z[:,2])
            tq=np.linspace(start,end,8192,endpoint=False)
            angles=2*np.pi*(tq-tq[0])*fc/2
            design=np.column_stack([np.ones(len(tq))]+[fun(n*angles) for n in range(1,9) for fun in (np.sin,np.cos)])
            coef=np.linalg.lstsq(design,np.interp(tq,a[:,0],a[:,2]),rcond=None)[0]
            half_ratio=np.hypot(coef[1],coef[2])/np.hypot(coef[3],coef[4])
        d=dict(alpha=alpha, source=source, source_path=str(folder.relative_to(ROOT)),
               window_source=window_source,t_start=start,t_end=end,orbits=cycles,order=order,
               St_carrier=fc,St_orbit=f0,cl_mean=cl,cd_mean=cd,ld_mean=mean(z[:,0],z[:,2]/z[:,1]),
               cl_min=z[:,2].min(),cl_max=z[:,2].max(),cd_min=z[:,1].min(),cd_max=z[:,1].max(),
               mean_drift_relative=mean_drift,amplitude_drift_relative=amp_drift,orbit_recurrence_error=residual,
               carrier_recurrence_error=carrier_residual,half_carrier_amplitude_ratio=half_ratio,
               stationary=bool(mean_drift<.01 and amp_drift<.01 and residual<.02))
        STATS.append(d)
        SERIES[alpha]=(a,z,d,folder)
        print(f'{alpha:2d} order={order} St={fc:.6f} meanCL={cl:.6f} window={start:.2f}:{end:.2f} orbits={cycles} drift={mean_drift:.2g}/{amp_drift:.2g} recurrence={residual:.2g}',flush=True)
    with (DATA/'angle_statistics.csv').open('w') as f:
        w=csv.DictWriter(f,fieldnames=list(STATS[0])); w.writeheader(); w.writerows(STATS)
    base=[]
    for p in sorted((p for p in (ROOT/'static_airfoil').glob('steady_aoa*') if p.is_dir()),key=lambda p:int(p.name.split('aoa')[1])):
        a,_=load_force(p/'postProcessing')
        z=a[a[:,0]>=.9*a[-1,0]]
        base.append(dict(alpha=int(p.name.split('aoa')[1]),cl=float(z[:,2].mean()),cd=float(z[:,1].mean()),
                         cl_range=float(np.ptp(z[:,2])),converged=bool(np.ptp(z[:,2])<1e-5)))
    (DATA/'steady_solver_statistics.json').write_text(json.dumps(base,indent=2))
    return base

def style():
    plt.rcParams.update({'font.family':'serif','font.serif':['DejaVu Serif'],
        'mathtext.fontset':'dejavuserif','font.size':9,'axes.labelsize':10,'axes.titlesize':10,
        'legend.fontsize':8,'axes.spines.top':False,'axes.spines.right':False,
        'axes.linewidth':.7,'lines.linewidth':1.25,'xtick.direction':'in','ytick.direction':'in',
        'pdf.fonttype':42,'ps.fonttype':42,'savefig.dpi':600})

BOOK=None
def save(fig,name):
    fig.savefig(OUT/f'{name}.pdf')
    fig.savefig(OUT/f'{name}.png',dpi=600)
    BOOK.savefig(fig)
    plt.close(fig)

def pd_band(ax):
    ax.axvspan(24,25,facecolor='0.92',edgecolor='0.55',hatch='///',linewidth=0,zorder=0)

def coefficients(base):
    specs=[('cl_mean','cl',r'$C_L$'),('cd_mean','cd',r'$C_D$'),('ld_mean',None,r'$C_L/C_D$')]
    def panel(ax,spec,lift_errorbars=False):
        key,bkey,lab=spec
        ok=[b for b in base if b['converged']]
        ax.plot([b['alpha'] for b in ok],[b[bkey] if bkey else b['cl']/b['cd'] for b in ok],
                '-',color='0.45',lw=1,label='Steady solver (converged)')
        fixed=[d for d in STATS if d['order']==0]
        ax.plot([0]+[d['alpha'] for d in fixed],[0 if key!='cd_mean' else base[0]['cd']]+[d[key] for d in fixed],
                '-o',color='k',ms=3,label='Steady physical state')
        shed=[d for d in STATS if d['order']>0]
        angles=np.array([d['alpha'] for d in shed])
        averages=np.array([d[key] for d in shed])
        ax.plot(angles,averages,'-' if lift_errorbars else ':',color=BLUE,lw=1.8,label='Post-shedding time average')
        if key=='cl_mean':
            lower=np.array([d['cl_min'] for d in shed])
            upper=np.array([d['cl_max'] for d in shed])
            if lift_errorbars:
                ax.errorbar(angles,averages,yerr=np.vstack([averages-lower,upper-averages]),
                            fmt='none',ecolor=RED,elinewidth=.9,capsize=2.5,capthick=.9,zorder=2)
            else:
                ax.plot(angles,lower,'-',color=RED,lw=1.1)
                ax.plot(angles,upper,'-',color=RED,lw=1.1)
        for order,mk in [(1,'o'),(2,'s')]:
            subset=[d for d in shed if d['order']==order]
            ax.plot([d['alpha'] for d in subset],[d[key] for d in subset],linestyle='none',marker=mk,ms=3.5,color=BLUE)
        pd_band(ax)
        ax.set(xlim=(-.5,31),xlabel=r'$\alpha\ (\mathrm{deg})$',ylabel=lab)
        ax.set_xticks(np.arange(0,31,5))
        ax.grid(axis='y',alpha=.18,lw=.5)
    handles=[Line2D([],[],color='k',marker='o',ms=3,label='Steady physical state'),
             Line2D([],[],color='0.45',label='Converged steady solver'),
             Line2D([],[],color=BLUE,ls=':',lw=1.8,marker='o',ms=3,label='Shedding mean: period 1'),
             Line2D([],[],color=BLUE,ls=':',lw=1.8,marker='s',ms=3,label='Shedding mean: period 2')]
    range_handle=Line2D([],[],color=RED,lw=1.1,label='Lift: instantaneous min / max')
    fig,axes=plt.subplots(1,3,figsize=(7.1,3.35))
    for i,(ax,spec) in enumerate(zip(axes,specs)):
        panel(ax,spec); ax.set_title(f'({chr(97+i)})',loc='left')
    fig.subplots_adjust(left=.09,right=.985,bottom=.32,top=.83,wspace=.4)
    fig.legend(handles=handles+[range_handle],loc='lower center',ncol=2,bbox_to_anchor=(.5,.005))
    fig.text(.5,.95,r'NACA0012, $Re=500$   |   Period-doubling bracket: $24^\circ<\alpha\leq25^\circ$',ha='center',fontsize=9)
    save(fig,'01_force_coefficients')
    for name,spec in zip(['lift','drag','lift_to_drag'],specs):
        fig,ax=plt.subplots(figsize=(5.4,3.8));panel(ax,spec)
        fig.subplots_adjust(bottom=.32 if name=='lift' else .28,top=.9,left=.15,right=.97)
        fig.legend(handles=handles+([range_handle] if name=='lift' else []),loc='lower center',ncol=2)
        ax.set_title(r'$Re=500$; period doubling in $(24^\circ,25^\circ]$',fontsize=10)
        save(fig,'01_'+name)
    fig,ax=plt.subplots(figsize=(5.4,3.8));panel(ax,specs[0],lift_errorbars=True)
    alternative_handles=handles[:2]+[
        Line2D([],[],color=BLUE,ls='-',marker='o',ms=3,label='Shedding mean: period 1'),
        Line2D([],[],color=BLUE,ls='-',marker='s',ms=3,label='Shedding mean: period 2'),
        Line2D([],[],color=RED,marker='|',ms=8,lw=0,label='Bars: instantaneous min to max')]
    fig.subplots_adjust(bottom=.32,top=.9,left=.15,right=.97)
    fig.legend(handles=alternative_handles,loc='lower center',ncol=2)
    ax.set_title(r'$Re=500$; period doubling in $(24^\circ,25^\circ]$',fontsize=10)
    save(fig,'01_lift_errorbars')

def strouhal():
    fig,ax=plt.subplots(figsize=(5.4,3.5))
    s=[d for d in STATS if d['order']>0]
    ax.plot([d['alpha'] for d in s],[d['St_carrier'] for d in s],'-o',color=BLUE,ms=3.5,label=r'Shedding carrier $f_c c/U_\infty$')
    p=[d for d in s if d['order']==2]
    ax.plot([d['alpha'] for d in p],[d['St_orbit'] for d in p],'--s',color=RED,ms=3.5,label=r'Orbit fundamental $f_0 c/U_\infty$')
    pd_band(ax)
    ax.set(xlabel=r'$\alpha\ (\mathrm{deg})$',ylabel=r'$St$',xlim=(10.5,30.5))
    ax.grid(alpha=.18);ax.legend(loc='lower left')
    fig.tight_layout();save(fig,'02_strouhal')

def fft_data(alpha):
    a,z,d,_=SERIES[alpha]
    n=int(d['orbits']*d['order']*512)
    t=np.linspace(d['t_start'],d['t_end'],n,endpoint=False)
    y=np.interp(t,a[:,0],a[:,2]);y-=y.mean()
    w=np.hanning(n)
    f=np.fft.rfftfreq(n,(t[-1]-t[0])/(n-1))
    amp=2*np.abs(np.fft.rfft(y*w))/w.sum()
    np.savetxt(DATA/f'spectrum_{alpha:02d}.csv',np.c_[f,amp],delimiter=',',header='frequency_c_over_U,lift_amplitude',comments='')
    return f,amp,d

def spectra():
    fig,axes=plt.subplots(1,3,figsize=(7.1,2.9),sharey=True)
    for ax,alpha in zip(axes,[24,25,26]):
        f,amp,d=fft_data(alpha);fc=d['St_carrier']
        mask=(f>0)&(f<=2.5*fc)
        ax.semilogy(f[mask]/fc,amp[mask],color=BLUE,lw=1)
        for v in [.5,1,1.5,2]: ax.axvline(v,color='0.8',ls=':',lw=.7,zorder=0)
        ax.text(.5, .96,r'$f_c/2$',transform=ax.get_xaxis_transform(),ha='center',va='top',fontsize=8)
        ax.text(1,.96,r'$f_c$',transform=ax.get_xaxis_transform(),ha='center',va='top',fontsize=8)
        ax.set(xlim=(0,2.4),ylim=(1e-7,1),xlabel=r'$f/f_c$',title=rf'$\alpha={alpha}^\circ$: period {d["order"]}')
        ax.set_xticks([0,.5,1,1.5,2])
    axes[0].set_ylabel(r'Lift amplitude $A_{C_L}$')
    fig.subplots_adjust(left=.10,right=.99,bottom=.2,top=.85,wspace=.12)
    save(fig,'03_fourier_period_doubling')

def surface_mean(alpha):
    a,z,d,folder=SERIES[alpha]
    files=sorted((folder/'surfaces').glob('*/airfoil.xy'),key=lambda p:float(p.parent.name))
    t=np.array([float(p.parent.name) for p in files])
    # Use snapshots bracketing the force-statistics window, interpolating the endpoints.
    start,end=d['t_start'],min(d['t_end'],t[-1])
    if d['order']:
        cycles=int((end-max(start,t[0]))*d['St_orbit'])
        start=end-cycles/d['St_orbit']
    ids=np.arange(max(0,np.searchsorted(t,start)-1),min(len(t),np.searchsorted(t,end)+1))
    arrays=[];coords=None
    for i in ids:
        q=np.loadtxt(files[i]);q=q[np.lexsort((q[:,2],q[:,1],q[:,0]))]
        if coords is None:coords=q[:,:3]
        if not np.allclose(coords,q[:,:3],atol=1e-8):raise ValueError('Surface grid changed')
        if not np.allclose(q[:,3],2*q[:,4],rtol=3e-5,atol=2e-6):raise ValueError('Cp normalization mismatch')
        arrays.append(q[:,[3,5,6]])
    v=np.array(arrays);ts=t[ids]
    if d['order'] and np.max(np.diff(ts))>2*np.median(np.diff(ts)):
        raise ValueError(f'Surface snapshot gap in averaging window: {alpha}')
    ti=np.r_[start,ts[(ts>start)&(ts<end)],end]
    vi=np.stack([np.interp(ti,ts,v[:,i,j]) for i in range(v.shape[1]) for j in range(3)],axis=1).reshape(len(ti),v.shape[1],3)
    vm=mean(ti,vi)
    result={}
    for side,sgn in [('upper',1),('lower',-1)]:
        # Exclude the blunt trailing-edge face; the surface tangent points LE to TE.
        m=(coords[:,1]*sgn>0)&(coords[:,0]<1-1e-8)
        xx=coords[m,0]; yy=coords[m,1];vv=vm[m]
        if np.any(np.diff(xx)<=0):raise ValueError('Duplicate surface x coordinates')
        slope=np.gradient(yy,xx,edge_order=2)
        tau=-(vv[:,1]+slope*vv[:,2])/np.sqrt(1+slope*slope)
        result[side]=(xx,vv[:,0],tau)
        np.savetxt(DATA/f'surface_{alpha:02d}_{side}.csv',np.c_[xx,vv[:,0],tau],delimiter=',',
                   header='x_over_c,mean_Cp,mean_tau_t_over_rho_U2',comments='')
    result['window']=[float(start),float(end),len(ids)]
    return result

def surfaces():
    selection=[11,20,26]
    sm={alpha:surface_mean(alpha) for alpha in selection}
    (DATA/'surface_windows.json').write_text(json.dumps({a:s['window'] for a,s in sm.items()},indent=2))
    for column,name,ylabel in [(1,'04_mean_pressure',r'$\overline{C_p}$'),(2,'05_mean_wall_shear',r'$\overline{\tau}_{w,t}/(\rho U_\infty^2)$')]:
        fig,axes=plt.subplots(1,3,figsize=(7.1,3.0),sharey=True)
        for ax,alpha,title in zip(axes,selection,['Before shedding','After shedding','After period doubling']):
            for side,color,ls in [('upper',BLUE,'-'),('lower',RED,'--')]:
                v=sm[alpha][side];ax.plot(v[0],v[column],color=color,ls=ls,label=side.capitalize()+' surface')
            if column==2:ax.axhline(0,color='0.5',lw=.6)
            ax.set(xlabel=r'$x/c$',xlim=(0,1),title=title+'\n'+rf'$\alpha={alpha}^\circ$')
            ax.set_xticks([0,.5,1],['0','0.5','1']);ax.grid(alpha=.16)
            if column==2:
                inset=ax.inset_axes([.20,.12,.71,.27])
                xx,_,tau=sm[alpha]['upper']
                inset.plot(xx,tau,color=BLUE,lw=1)
                inset.axhline(0,color='0.35',ls=':',lw=.6)
                inset.set(xlim=(.05,1),ylim=(-.018,.018),xticks=[.1,.5,.9],yticks=[-.01,0,.01])
                inset.tick_params(labelsize=6,pad=1,length=2)
                inset.set_title('Upper surface (zoom)',fontsize=6.5,pad=2)
        if column==1:axes[0].invert_yaxis()
        axes[0].set_ylabel(ylabel)
        fig.subplots_adjust(left=.11,right=.97,bottom=.25,top=.8,wspace=.12)
        fig.legend(*axes[0].get_legend_handles_labels(),loc='lower center',ncol=2)
        save(fig,name)

def phase_spaces():
    for dimensions in [2,3]:
        selection=[24,25,26] if dimensions==2 else [26]
        fig=plt.figure(figsize=(7.1,3.1) if dimensions==2 else (5.4,4.2))
        for i,alpha in enumerate(selection):
            a,z,d,_=SERIES[alpha];delay=.25/d['St_carrier']
            t=np.linspace(d['t_end']-4/d['St_orbit'],d['t_end'],3500)
            q=[np.interp(t-j*delay,a[:,0],a[:,2]) for j in range(dimensions)]
            ax=fig.add_subplot(1,len(selection),i+1,projection='3d' if dimensions==3 else None)
            if dimensions==2:
                ax.plot(*q,color=BLUE,lw=.8);ax.set_aspect('equal',adjustable='box')
                ax.grid(alpha=.15)
            else:
                ax.plot(*q,color=BLUE,lw=1);ax.set_zlabel(r'$C_L(t-2\tau)$',fontsize=10,labelpad=5)
                ax.view_init(elev=24,azim=-52);ax.tick_params(labelsize=7,pad=0)
            ax.set_xlabel(r'$C_L(t)$',fontsize=9,labelpad=3)
            ax.set_ylabel(r'$C_L(t-\tau)$',fontsize=9,labelpad=3)
            ax.set_title(rf'$\alpha={alpha}^\circ$: period {d["order"]}'+'\n'+rf'$\tau={delay:.3f}\,c/U_\infty$',fontsize=9,pad=10)
        fig.subplots_adjust(left=.09,right=.97 if dimensions==2 else .82,bottom=.19,top=.78,wspace=.48)
        save(fig,f'06_lift_delay_{dimensions}d')

def main():
    global BOOK
    OUT.mkdir(exist_ok=True);DATA.mkdir(exist_ok=True)
    base=analyze()
    if '--analyze-only' in sys.argv:return
    style()
    with PdfPages(HERE/'steady_case_figures.pdf') as BOOK:
        coefficients(base);strouhal();spectra();surfaces();phase_spaces()
    print('Wrote figures to',OUT)

if __name__=='__main__':main()
