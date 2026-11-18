"""Generate every numerical table and figure of the note strictly from saved metrics."""
import argparse
import json
import os
from pathlib import Path
os.environ.setdefault('MPLCONFIGDIR', '/private/tmp/electron-extension-matplotlib')
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

plt.rcParams.update({'font.family': 'serif', 'font.size': 8.5, 'axes.spines.top': False,
                     'axes.spines.right': False, 'axes.labelsize': 9, 'legend.fontsize': 7.5,
                     'axes.titlesize': 9, 'pdf.fonttype': 42, 'savefig.bbox': 'tight',
                     'axes.grid': True, 'grid.alpha': .2})
COLORS = ['#155f85', '#c15b22', '#32845b', '#734b9a', '#8a6d1c', '#555555', '#b03060']


def table(path, header, rows, columns):
    lines = [r'\begin{tabular}{%s}\toprule' % columns, header+r'\\\midrule']
    lines += [' & '.join(r)+r' \\' for r in rows]
    path.write_text('\n'.join(lines+[r'\bottomrule\end{tabular}'])+'\n')


def big(x):
    return f'{x:.0f}' if x >= 1000 else f'{x:.4g}'


def make(path, output):
    m = json.loads(Path(path).read_text())
    if m['status'] != 'complete':
        raise SystemExit(f"run status is {m['status']}; refusing to make figures")
    output.mkdir(parents=True, exist_ok=True)
    cfg = m['config']
    dlo, dhi = cfg['curve_degrees']
    like = {(e['operator'], e['degree']): e for e in m['like_particle']}
    econ = {(r['Z'], r['degree']): r for r in m['electron_constants']}

    # Figure 1: drive dependence and charge dependence.
    fig, ax = plt.subplots(1, 2, figsize=(6.5, 2.75), constrained_layout=True)
    k = np.array([r['k'] for r in m['dougherty']])
    s = k*5/6
    for key, style, name in (('theta_thermal', '-', 'Dougherty, thermal'),
                             ('theta_potential', '--', 'Dougherty, potential')):
        ax[0].semilogx(s, np.array([r[key] for r in m['dougherty']])/k/(5/6), style,
                       color=COLORS[2], lw=1.6, label=name)
    e = like[('landau', dhi)]
    kap = e['thermal']['kappa']
    kk = np.array([r['k'] for r in e['responses']])
    for key, style, name in (('chi_thermal', '-', 'Landau, thermal'),
                             ('chi_potential', '--', 'Landau, potential')):
        ax[0].semilogx(kk*kap, np.array([r[key] for r in e['responses']])/kap, style,
                       color=COLORS[0], lw=1.6, label=name)
    ax[0].set(xlim=(.01, 10), ylim=(0, 1.03), xlabel=r'$s=|k|\kappa$', ylabel=r'$\chi/\kappa$',
              title='(a) Like-particle collisions, two drives')
    ax[0].legend(frameon=False, loc='lower left')
    for color, Z in zip(COLORS, cfg['ion_charges']):
        for d, style in ((dhi, '-'), (dlo, ':')):
            c = next(c for c in m['electron_curves'] if c['Z'] == Z and c['degree'] == d)
            ax[1].semilogx([p['k_lambda'] for p in c['points']], [p['ratio'] for p in c['points']],
                           style, color=color, lw=1.5 if d == dhi else 1.0,
                           label=f'$Z={Z}$' if d == dhi else None)
    ax[1].set(xlim=(1e-3, 1), ylim=(0, 1.03), xlabel=r'$|k|\lambda_e$',
              ylabel=r'$\chi_{\rm th}/\kappa_{\rm SH}$',
              title=f'(b) Electrons; solid $D={dhi}$, dotted $D={dlo}$')
    ax[1].legend(frameon=False, loc='lower left', ncol=2)
    fig.savefig(output/'responses.pdf'); plt.close(fig)

    # Figure 2: embedded decay at the second-largest wavenumber of the test.
    kl_show = cfg['embedded_k_lambda'][-2]
    shown = [e for e in m['embedded'] if e['k_lambda'] == kl_show]
    fig, ax = plt.subplots(1, len(shown), figsize=(6.5, 2.6), constrained_layout=True, squeeze=False)
    for a, e in zip(ax[0], shown):
        t = np.array(e['scaled_time'])
        a.semilogy(t, e['kinetic_T'], color='k', lw=2.2, label='Kinetic, zero current')
        for (name, label), color, style in zip((('quasistatic', 'Quasi-static thermal'),
                                                ('fourier', 'Spitzer-Harm'),
                                                ('slowest_mode', 'Least-damped mode')),
                                               COLORS, ('--', '-.', ':')):
            a.semilogy(t, e['models'][name]['T'], style, color=color, lw=1.5, label=label)
        a.set(xlim=(0, 4), ylim=(1e-2, 1.1), xlabel=r'$t\,/\,t_{\rm decay}$', ylabel=r'$T(t)/T(0)$',
              title=rf"$Z={e['Z']}$, $|k|\lambda_e={kl_show}$")
    ax[0][0].legend(frameon=False, loc='lower left')
    fig.savefig(output/'embedded_decay.pdf'); plt.close(fig)

    # Table: electron transport constants.
    ref = m['reference']['braginskii_gamma0']
    rows = []
    for Z in cfg['ion_charges']:
        lo, mid, hi = econ[(Z, 6)], econ[(Z, dlo)], econ[(Z, dhi)]
        rows.append([str(Z), f"{lo['kappa_over_tau_e']:.4f}", ref.get(str(Z), '---'),
                     f"{mid['kappa_over_tau_e']:.4f}", f"{hi['kappa_over_tau_e']:.4f}",
                     f"{hi['sigma_over_tau_e']:.4f}",
                     big(mid['K_over_lambda_e_squared']), big(hi['K_over_lambda_e_squared']),
                     f"{hi['curvature']:.2f}"])
    table(output/'electron_constants.tex',
          r'$Z$ & $\kappa_6$ & Brag. & $\kappa_{%d}$ & $\kappa_{%d}$ & $\sigma_{%d}$ & '
          r'$K_{%d}/\lambda_e^2$ & $K_{%d}/\lambda_e^2$ & $K/\kappa^2$' % (dlo, dhi, dhi, dlo, dhi),
          rows, 'rrrrrrrrr')

    # Table: Lorentz limit.
    rows = [[str(r['Z']), str(r['degree']), f"{r['kappa_over_tau_e']:.4f}", f"{r['sigma_over_tau_e']:.4f}"]
            for r in m['lorentz_limit'] if r['degree'] in (dlo, dhi)]
    rows.append([r'$\infty$', 'exact', f"{m['reference']['lorentz_limit_kappa']:.4f}",
                 f"{m['reference']['lorentz_limit_sigma']:.4f}"])
    table(output/'lorentz_limit.tex', r'$Z$ & $D$ & $\kappa/\tau_e$ & $\sigma/\tau_e$', rows, 'rrrr')

    # Table: like-particle Landau, the two leading coefficients.
    rows = []
    for d in cfg['degrees']:
        e = like[('landau', d)]
        rows.append([str(d), f"{e['thermal']['kappa']:.6f}", f"{e['K_potential']:.4f}",
                     f"{e['thermal']['K']:.4f}", f"{e['thermal']['K']/e['K_potential']:.4f}"])
    table(output/'landau_drives.tex',
          r'$D$ & $\kappa/\tau$ & $K_{\rm pot}/\tau^2$ & $K_{\rm th}/\tau^2$ & ratio', rows, 'rrrrr')

    # Table: embedded history errors.
    rows = []
    for e in m['embedded']:
        mo = e['models']
        rows.append([str(e['Z']), f"{e['k_lambda']:g}", big(e['decay_time_over_tau_e']),
                     f"{mo['quasistatic']['chi_over_kappa']:.4f}",
                     f"{mo['quasistatic']['relative_history_error']:.4f}",
                     f"{mo['fourier']['relative_history_error']:.4f}",
                     f"{mo['slowest_mode']['relative_history_error']:.4f}",
                     f"{e['numerical_refinement_error']:.1e}"])
    table(output/'embedded_errors.tex',
          r'$Z$ & $|k|\lambda_e$ & $t_{\rm decay}/\tau_e$ & $\chi_{\rm th}/\kappa$ & Quasi-static & '
          r'Spitzer--H\"arm & Least-damped & Refinement', rows, 'rrrrrrrr')
    (output/'provenance.json').write_text(json.dumps(
        dict(metrics=str(Path(path)), schema_version=m['schema_version'],
             runtime_seconds=m['runtime_seconds']), indent=1)+'\n')


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('metrics')
    p.add_argument('--output', default=str(Path(__file__).resolve().parent/'figures'))
    a = p.parse_args()
    make(a.metrics, Path(a.output))
