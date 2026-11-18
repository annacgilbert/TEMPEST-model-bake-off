"""Generate every numerical table/figure strictly from saved metrics."""
import argparse
import json
import os
from pathlib import Path
os.environ.setdefault('MPLCONFIGDIR','/private/tmp/plasma-paper-matplotlib')
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

plt.rcParams.update({'font.family':'serif','font.size':8.5,'axes.spines.top':False,
    'axes.spines.right':False,'axes.labelsize':9,'legend.fontsize':7.5,
    'axes.titlesize':9,
    'pdf.fonttype':42,'savefig.bbox':'tight','axes.grid':True,'grid.alpha':.2})
COLORS=['#155f85','#c15b22','#32845b','#734b9a']

def make(path, output):
    m=json.loads(Path(path).read_text())
    output.mkdir(parents=True,exist_ok=True)
    k=np.array([r['k'] for r in m['curves']])
    curves={key:np.array([r[key] for r in m['curves']]) for key in
            ('bgk1','variable_bgk1','dougherty1','dougherty3')}
    kv=m['bgk_constants']['variable']['kappa']
    fig,ax=plt.subplots(1,2,figsize=(6.5,2.65),constrained_layout=True)
    for key,kf,name,color in (('bgk1',1.5,'Constant BGK',COLORS[0]),
          ('dougherty1',.5,'Dougherty',COLORS[2]),
          ('variable_bgk1',kv,'Speed-dependent BGK',COLORS[1])):
        s=k*kf
        r=curves[key]/k/kf
        ax[0].semilogx(s,r,label=name,color=color,lw=1.8)
        harm=1/(1+s/np.sqrt(2/np.pi))
        ax[1].semilogx(s,harm/r-1,label=name,color=color,lw=1.8)
    ax[0].set(xlim=(.01,10),ylim=(0,1.03),xlabel=r'$s=|k|\kappa_{\rm F}$',
              ylabel=r'$\chi/\kappa_{\rm F}$',title='(a) One velocity dimension')
    ax[1].axhline(0,color='k',lw=.7)
    ax[1].set(xlim=(.01,10),xlabel=r'$s=|k|\kappa_{\rm F}$',
              ylabel=r'$\chi_{\rm H}/\chi-1$',title='(b) Harmonic interpolation error')
    ax[0].legend(frameon=False,loc='lower left')
    fig.savefig(output/'relaxation_comparison.pdf'); plt.close(fig)

    fig,ax=plt.subplots(1,2,figsize=(6.5,2.65),constrained_layout=True)
    last=m['landau'][-1]; c=last['constants']
    kl=np.array([r['k'] for r in last['responses']]); s=kl*c['kF']
    r=np.array([r['ratio'] for r in last['responses']])
    ax[0].semilogx(k*5/6,curves['dougherty3']/k/(5/6),color=COLORS[2],label='Dougherty (exact)',lw=1.8)
    for dentry,style in ((m['landau'][-2],'--'),(last,'-')):
        ax[0].semilogx(s,[v['ratio'] for v in dentry['responses']],style,
             marker='o' if style=='-' else None,ms=3,color=COLORS[0],
             label=f"Landau (degree {dentry['degree']})")
    ax[0].set(xlim=(.015,4),ylim=(.25,1.03),xlabel=r'$s=|k|\kappa_{\rm F}$',
              ylabel=r'$\chi/\kappa_{\rm F}$',title='(a) Three velocity dimensions')
    ax[0].legend(frameon=False)
    ax[1].semilogx(kl,[v['Tperp_over_n'] for v in last['responses']],'-o',
                  ms=3,color=COLORS[0],label=r'$T_{\perp 1}/n_1$')
    ax[1].semilogx(kl,[v['minus_T_over_n'] for v in last['responses']],'-s',
                  ms=3,color=COLORS[1],label=r'$-T_1/n_1$')
    ax[1].axhline(0,color='k',lw=.7)
    ax[1].set(xlabel=r'$|k|\tau$ ($v_t=1$)',title='(b) Landau temperature response',ylim=(-1.06,1.06))
    ax[1].legend(frameon=False)
    fig.savefig(output/'landau_comparison.pdf'); plt.close(fig)

    fig,axs=plt.subplots(1,3,figsize=(6.5,2.55),constrained_layout=True)
    for ax,item in zip(axs,m['embedded']):
        t=np.array(item['time'])*item['k']
        ax.plot(t,item['kinetic_T'],color='black',lw=1.8,label='Kinetic')
        for name,label,color,style in (('quasistatic','Quasi-static',COLORS[0],'--'),
              ('fourier','Fourier',COLORS[1],':'),('harmonic','Harmonic',COLORS[2],'-.')):
            ax.plot(t,item['models'][name]['T'],style,color=color,lw=1.5,label=label)
        ax.set(xlim=(0,12),xlabel=r'$|k|t$',title=rf"$k/\nu={item['k']:g}$")
    axs[0].set_ylabel(r'$T(t)/T(0)$')
    handles,labels=axs[0].get_legend_handles_labels()
    fig.legend(handles,labels,loc='outside upper center',ncol=4,frameon=False)
    fig.savefig(output/'embedded_rollouts.pdf'); plt.close(fig)

    var=m['bgk_constants']['variable']; lc=last['constants']
    rows=[r'\begin{tabular}{llrrr}\toprule',
          r'$d$ & Collision model & $\F$ & $K$ & $c=K/\F^2$\\\midrule',
          r'1 & Constant BGK & $3/2$ & $4$ & $16/9$\\',
          r'1 & Dougherty & $1/2$ & $1/3$ & $4/3$\\',
          r'1 & BGK, $\nu(v)=(1+|v|^3)^{-1}$ & '
          +f"{var['kappa']:.4f} & {var['K']:.1f} & {var['K']/var['kappa']**2:.2f} "+r'\\',
          r'\midrule 3 & Dougherty & $5/6$ & $2/15$ & $24/125=0.192$\\',
          f"3 & Like-particle Landau & {lc['kF']:.4f} & {lc['Kexact']:.2f} & {lc['Kexact']/lc['kF']**2:.3f} "+r'\\',
          r'\bottomrule\end{tabular}']
    (output/'curvature.tex').write_text('\n'.join(rows)+'\n')
    rows=[r'\begin{tabular}{rrrrrr}\toprule',
          r'$D$ & $\kappa_{\rm F}/\tau$ & $\eta/\tau$ & $C/\tau$ & $X_0/\tau$ & $K/\tau^2$\\\midrule']
    for entry in m['landau']:
        c=entry['constants']; rows.append(f"{entry['degree']} & {c['kF']:.6f} & {c['eta']:.6f} & {c['Cs']:.5f} & {c['X0']:.5f} & {c['Kexact']:.5f} \\\\")
    rows += [r'\bottomrule\end{tabular}']
    (output/'landau_constants.tex').write_text('\n'.join(rows)+'\n')
    rows=[r'\begin{tabular}{rrrrr}\toprule',
          r'$|k|\tau$ & $\chi_{12}/\kappa_{12}$ & $\chi_{16}/\kappa_{16}$ & Difference & $1-K_{16}k^2$\\\midrule']
    for a,b in zip(m['landau'][-2]['responses'],last['responses']):
        expansion=1-last['constants']['Kexact']*b['k']**2
        estr=f'{expansion:.6f}' if b['k']<=.1 else r'---'
        rows.append(f"{b['k']:.3f} & {a['ratio']:.6f} & {b['ratio']:.6f} & {abs(a['ratio']-b['ratio']):.1e} & {estr} \\\\")
    rows += [r'\bottomrule\end{tabular}']
    (output/'landau_refinement.tex').write_text('\n'.join(rows)+'\n')
    rows=[r'\begin{tabular}{rrrrr}\toprule',
          r'$k/\nu$ & Quasi-static & Fourier & Harmonic & Kinetic refinement\\\midrule']
    for entry in m['embedded']:
        errs=[entry['models'][n]['relative_history_error'] for n in ('quasistatic','fourier','harmonic')]
        rows.append(f"{entry['k']:.1f} & {errs[0]:.5f} & {errs[1]:.5f} & {errs[2]:.5f} & {entry['numerical_refinement_error']:.1e} \\\\")
    rows += [r'\bottomrule\end{tabular}']
    (output/'embedded_errors.tex').write_text('\n'.join(rows)+'\n')
    (output/'provenance.json').write_text(json.dumps({'metrics_source':str(path),
          'note':'All plotted values and numerical tables derive from this saved metrics file.'},indent=2)+'\n')

if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('metrics'); p.add_argument('--output',default='figures')
    a=p.parse_args(); make(a.metrics,Path(a.output))
