"""Large ion charge: the radial limit problem and its comparison with
finite-Z electron Galerkin solves.  Units v_t = tau_ee = 1.

Radial reduction of the like-particle Landau form (3 sqrt(pi)/4 normalization):
for radial f, h with derivatives f', h',

  D(f, h) = (3 sqrt(pi)/2) [ <A f' h'> - (2/3) E_a E_b f'(a) h'(b) r_< / r_>^2 ],
  A(a) = (8 pi/3) int_0^inf M_3(b) b^4 / max(a, b)^3 db,

because v^.U(v-v')v^' = a b (1-mu^2)/|v-v'|^3 and its angular mean is
(2/3) r_</r_>^2.  The limit problem is

  C_inf = <b0, Lambda_ee^+ b0>,   b0 = (|v|^2-3)/3 - sqrt(pi/2)|v|^5(|v|^2-8)/384,
  T_red(s) = <zeta, (Lambda_ee + s w)^-1 zeta>,  w = |v|^5/(9 sqrt(pi)),
  X(s) = 1/(s T_red(s)),  X(0) = kappa_L = 64 sqrt(2)/(3 pi).

  python large_z.py run results/<new-dir>          # refuses to overwrite
  python large_z.py figures results/<dir>/metrics.json figures
"""
import hashlib
import json
import os
import platform
import sys
import time
from pathlib import Path

import numpy as np
from numpy.polynomial.legendre import leggauss
from scipy.special import erf

HERE = Path(__file__).resolve().parent
SHARED = HERE.parents[1] / 'scripts' / 'landau_closure'
ELECTRON = HERE.parent / 'electron_heat_flux_extension'
sys.path.insert(0, str(SHARED))
sys.path.insert(0, str(ELECTRON))

KAPPA_L = 64*np.sqrt(2)/(3*np.pi)
C_LANDAU = 3*np.sqrt(np.pi)/4


def grid(vmax, panels, nodes):
    """Composite Gauss-Legendre grid on [0, vmax]: nodes, plain weights, and
    the per-panel matrix S[q, j] = int_{-1}^{xi_q} l_j, for running integrals."""
    from numpy.polynomial import legendre as leg
    x, w = leggauss(nodes)
    edges = np.linspace(0, vmax, panels+1)
    h = np.diff(edges)/2
    X = (edges[:-1, None]+h[:, None]*(x[None]+1)).ravel()
    V = leg.legvander(x, nodes-1)
    Pint = np.stack([leg.legval(x, leg.legint(np.eye(nodes)[m], lbnd=-1)) for m in range(nodes)], 1)
    return X, (h[:, None]*w[None]).ravel(), Pint@np.linalg.inv(V), h, w


def running(g, S, h, w):
    """int_0^{x_q} g for every node q; g has shape (n_functions, n_nodes)."""
    n = len(w)
    G = g.reshape(g.shape[0], -1, n)
    full = np.cumsum((G*w).sum(2)*h, 1)
    before = np.concatenate([np.zeros((g.shape[0], 1)), full[:, :-1]], 1)
    return (before[:, :, None]+h[None, :, None]*(G@S.T)).reshape(g.shape), full[:, -1]


def diffusion_A(x):
    """Radial eigenvalue of int M_3(v') U(v-v') dv'."""
    big = x >= 0.5
    out = np.empty_like(x)
    xb = x[big]
    I4 = 3*np.sqrt(np.pi/2)*erf(xb/np.sqrt(2))-(xb**3+3*xb)*np.exp(-xb**2/2)
    out[big] = I4/xb**3
    xs = x[~big]
    ser, term = np.zeros_like(xs), np.ones_like(xs)
    for n in range(40):                        # int_0^x b^4 e^{-b^2/2} db / x^3
        ser += term*xs**2/(2*n+5)
        term = term*(-xs**2/2)/(n+1)
    out[~big] = ser
    return (8*np.pi/3)/(2*np.pi)**1.5*(out+np.exp(-x**2/2))


def orthopoly(t, dtdx, W, N):
    """Orthonormal polynomials in t (degree 0..N) for weights W; values and d/dx."""
    P = np.zeros((N+1, len(t)))
    dP = np.zeros_like(P)
    P[0] = 1/np.sqrt(W.sum())
    for n in range(N):
        q = t*P[n]
        dq = P[n]+t*dP[n]                      # derivative with respect to t
        for _ in range(2):                     # Gram-Schmidt, twice
            c = P[:n+1]@(W*q)
            q = q-c@P[:n+1]
            dq = dq-c@dP[:n+1]
        nrm = np.sqrt(W@(q*q))
        P[n+1], dP[n+1] = q/nrm, dq/nrm
    return P, dP*dtdx


def radial_form(G, dP):
    """The kernel r_</r_>^2 has a kink at a = b; the inner integral is split
    there and done with running integrals, so the quadrature stays spectral."""
    X, wq, S, h, w = G
    M = np.exp(-X**2/2)/(2*np.pi)**1.5
    rho = 4*np.pi*X**2*M
    U1, _ = running(rho*X*dP, S, h, w)
    U2, tot2 = running(4*np.pi*M*dP, S, h, w)
    inner = U1/X**2+X*(tot2[:, None]-U2)
    cross = (2/3)*(dP*(wq*rho))@inner.T
    local = (dP*(wq*rho*diffusion_A(X)))@dP.T
    return 2*C_LANDAU*(local-(cross+cross.T)/2), float(np.abs(cross-cross.T).max())


def b0(x):
    return (x**2-3)/3-np.sqrt(np.pi/2)*x**5*(x**2-8)/384


def radial_solve(cfg, panels, N, s_values, even=False):
    r = cfg['radial']
    G_ = grid(r['v_max'], panels, r['nodes_per_panel'])
    X = G_[0]
    W = G_[1]*4*np.pi*X**2*np.exp(-X**2/2)/(2*np.pi)**1.5
    P, dP = orthopoly(X**2, 2*X, W, N) if even else orthopoly(X, np.ones_like(X), W, N)
    D, cross_asym = radial_form(G_, dP)
    if even:
        return np.linalg.eigvalsh(D)
    proj = lambda f: P@(W*f)
    one, sq = proj(np.ones_like(X)), proj(X**2)
    Kq, _ = np.linalg.qr(np.stack([one, sq], 1))
    zeta, b = proj((X**2-3)/3), proj(b0(X))
    w = X**5/(9*np.sqrt(np.pi))
    Ww = (P*(W*w))@P.T
    G = np.linalg.solve(D+Kq@Kq.T, b)
    out = dict(panels=panels, degree=N,
               kernel_residual=float(np.abs(D@Kq).max()),
               asymmetry=cross_asym,
               min_eigenvalue=float(np.linalg.eigvalsh(D).min()),
               source_residual=float(np.abs(Kq.T@b).max()),
               source_norm_defect=float(abs(W@b0(X)**2-b@b)),
               kappa_L_quadrature=float(W@(w*((X**2-8)/2)**2)),
               C_inf=float(b@G))
    T = np.array([zeta@np.linalg.solve(D+s*Ww, zeta) for s in s_values])
    out['X'] = (1/(np.asarray(s_values)*T)).tolist()
    return out


def cached_radial_spectrum(d):
    from electron_numerics import lorentz_matrix
    L = np.load(SHARED/'cache'/f'landau_d{d}.npy')
    ev, V = np.linalg.eigh(lorentz_matrix(d)[0])
    Nrad = V[:, ev < 1e-9*ev.max()]
    return np.linalg.eigvalsh(Nrad.T@L@Nrad), Nrad.shape[1]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def run(out):
    from electron_numerics import lorentz_matrix, electron_operator, transport, thermal_response
    out = Path(out)
    if out.exists():
        raise SystemExit(f'{out} exists; result directories are never overwritten')
    cfg = json.loads((HERE/'config_large_z.json').read_text())
    start = time.time()
    failures = []
    g = cfg['s_grid']
    s_curve = np.logspace(g['log10_min'], g['log10_max'], g['points'])
    s_all = np.concatenate([s_curve, cfg['s_table'], cfg['s_small'], cfg['s_large']])
    r = cfg['radial']

    # 1. radial limit problem, refinement in degree and in the velocity grid
    radial = []
    for panels in r['panels']:
        for N in r['degrees']:
            if panels != r['panels'][-1] and N != r['degrees'][-1]:
                continue
            radial.append(radial_solve(cfg, panels, N, s_all))
    best = radial[-1]
    for x in radial:
        if not (x['kernel_residual'] < 1e-8 and x['asymmetry'] < 1e-8
                and x['min_eigenvalue'] > -1e-9 and x['source_residual'] < 1e-9):
            failures.append(f"radial sanity N={x['degree']} panels={x['panels']}")
    if abs(best['kappa_L_quadrature']-KAPPA_L) > 1e-9:
        failures.append('kappa_L quadrature')

    # 2. cross-check against the radial block of the cached Landau matrices
    cross = []
    for d in cfg['galerkin_degrees']:
        ref, n = cached_radial_spectrum(d)
        mine = radial_solve(cfg, r['panels'][-1], n-1, [], even=True)
        diff = float(np.abs(ref-mine).max())
        cross.append(dict(degree=d, radial_dimension=n, cached=ref.tolist(),
                          radial_solver=mine.tolist(), max_abs_difference=diff))
        if diff > 1e-6:
            failures.append(f'radial spectrum d={d}')

    # 3. finite-Z electron Galerkin constants and curves
    slope = best['C_inf']/KAPPA_L
    constants, curves, hashes = [], [], {}
    for d in cfg['galerkin_degrees']:
        cache = SHARED/'cache'/f'landau_d{d}.npy'
        hashes[cache.name] = sha(cache)
        Lee = np.load(cache)
        M = lorentz_matrix(d)[0]
        for Z in cfg['ion_charges_constants']:
            t = transport(electron_operator(Lee, M, Z), d, False)
            constants.append(dict(degree=d, Z=Z, Z_kappa=Z*t['kappa'], C=t['C'],
                                  thermoelectric=t['L12']/t['L11'],
                                  K_over_kappa2=t['C']/t['kappa'],
                                  K_over_kappa2_Z=t['C']/t['kappa']/Z))
        for Z in cfg['ion_charges_curves']:
            Lz = electron_operator(Lee, M, Z)
            chi = [thermal_response(Lz, d, float(np.sqrt(Z*s)))['chi'] for s in s_curve]
            curves.append(dict(degree=d, Z=Z, Z_chi=(Z*np.array(chi)).tolist()))

    n = g['points']
    nt, ns = len(cfg['s_table']), len(cfg['s_small'])
    limit = dict(s=s_curve.tolist(), X=best['X'][:n],
                 X_coarser_degree=radial[-2]['X'][:n],
                 s_table=cfg['s_table'], X_table=best['X'][n:n+nt])
    Xs = np.array(best['X'][n+nt:n+nt+ns])
    Xl = np.array(best['X'][n+nt+ns:])
    small = ((1-Xs/KAPPA_L)/np.array(cfg['s_small'])).tolist()
    tail = (np.diff(np.log(Xl))/np.diff(np.log(cfg['s_large']))).tolist()
    Xl_coarse = np.array(radial[-2]['X'][n+nt+ns:])
    metrics = dict(schema_version=cfg['schema_version'], config=cfg,
                   status='complete' if not failures else 'complete_with_failures',
                   failures=failures, kappa_L=KAPPA_L, thermoelectric_L=1.5,
                   C_inf=best['C_inf'], slope_C_inf_over_kappa_L=slope,
                   kappa_L_C_inf=KAPPA_L*best['C_inf'],
                   small_s_deficit_over_s=small,
                   large_s_local_loglog_slopes=tail,
                   large_s_degree_difference=float(np.abs(Xl/Xl_coarse-1).max()),
                   radial_refinement=[{k: v for k, v in x.items() if k != 'X'} for x in radial],
                   radial_cross_check=cross, limit=limit,
                   galerkin_constants=constants, galerkin_curves=curves,
                   input_hashes=hashes, script_sha256=sha(__file__),
                   environment=dict(python=platform.python_version(), numpy=np.__version__,
                                    platform=platform.platform()),
                   runtime_seconds=time.time()-start)
    out.mkdir(parents=True)
    (out/'metrics.json').write_text(json.dumps(metrics, indent=1))
    print(json.dumps({k: metrics[k] for k in ('status', 'failures', 'C_inf',
          'slope_C_inf_over_kappa_L', 'kappa_L_C_inf', 'small_s_deficit_over_s',
          'large_s_local_loglog_slopes', 'large_s_degree_difference', 'runtime_seconds')}, indent=1))
    for x in metrics['radial_refinement']:
        print(x)
    for c in cross:
        print(c['degree'], c['radial_dimension'], c['max_abs_difference'])
    for c in constants:
        print(c)


def figures(metrics_path, outdir):
    os.environ.setdefault('MPLCONFIGDIR', '/private/tmp/plasma-paper-matplotlib')
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    plt.rcParams.update({'font.family': 'serif', 'font.size': 8.5, 'axes.spines.top': False,
                         'axes.spines.right': False, 'axes.labelsize': 9, 'legend.fontsize': 7.5,
                         'axes.titlesize': 9, 'pdf.fonttype': 42, 'savefig.bbox': 'tight',
                         'axes.grid': True, 'grid.alpha': .2})
    colors = ['#155f85', '#c15b22', '#32845b', '#734b9a']
    m = json.loads(Path(metrics_path).read_text())
    outdir = Path(outdir)
    s = np.array(m['limit']['s'])
    X = np.array(m['limit']['X'])
    kL = m['kappa_L']
    dmax = max(m['config']['galerkin_degrees'])
    fig, ax = plt.subplots(1, 2, figsize=(6.5, 2.65), constrained_layout=True)
    for c, col in zip([c for c in m['galerkin_curves'] if c['degree'] == dmax], colors):
        ax[0].semilogx(s, np.array(c['Z_chi'])/kL, color=col, lw=1.2, label=f"$Z={c['Z']}$")
        lo = next(x for x in m['galerkin_curves'] if x['degree'] != dmax and x['Z'] == c['Z'])
        ax[0].semilogx(s, np.array(lo['Z_chi'])/kL, color=col, lw=1.0, ls=':')
    ax[0].semilogx(s, X/kL, 'k', lw=1.8, label='limit $X(s)/\\kappa_{\\rm L}$')
    ax[0].set(xlim=(1e-3, 1e1), ylim=(0, 1.03), xlabel=r'$s=k^2/Z$',
              ylabel=r'$Z\chi_{\rm th}/\kappa_{\rm L}$', title='(a) Collapse at large ion charge')
    ax[0].legend(frameon=False, loc='upper right')
    ax[1].loglog(s, X/kL, 'k', lw=1.8, label='limit')
    ax[1].loglog(s, 1/(1+m['kappa_L_C_inf']*s), color=colors[1], lw=1.2, ls='--',
                 label=r'lower bound $1/(1+\kappa_{\rm L}C_\infty s)$')
    ax[1].set(xlim=(1e-3, 1e3), xlabel=r'$s=k^2/Z$', ylabel=r'$X(s)/\kappa_{\rm L}$',
              title='(b) The limit function')
    ax[1].legend(frameon=False, loc='lower left')
    fig.savefig(outdir/'large_z.pdf')
    plt.close(fig)

    rows = [r'\begin{tabular}{rrrrrrr}\toprule',
            r'$Z$ & $Z\kappa_{12}/\kappa_{\rm L}$ & $Z\kappa_{16}/\kappa_{\rm L}$ & $C_{\thr,12}$ & $C_{\thr,16}$'
            r' & $K_{12}/(\kappa^2Z)$ & $K_{16}/(\kappa^2Z)$\\\midrule']
    by = {(c['degree'], c['Z']): c for c in m['galerkin_constants']}
    for Z in m['config']['ion_charges_constants']:
        a, b = by[(12, Z)], by[(16, Z)]
        rows.append(f"{Z} & {a['Z_kappa']/kL:.4f} & {b['Z_kappa']/kL:.4f} & {a['C']:.3f} & {b['C']:.3f}"
                    f" & {a['K_over_kappa2_Z']:.3f} & {b['K_over_kappa2_Z']:.3f} \\\\")
    rows += [r'\midrule', f"$\\infty$ & \\multicolumn{{2}}{{c}}{{1}} & \\multicolumn{{2}}{{c}}{{{m['C_inf']:.3f}}}"
             f" & \\multicolumn{{2}}{{c}}{{{m['slope_C_inf_over_kappa_L']:.3f}}} \\\\", r'\bottomrule\end{tabular}']
    (outdir/'large_z.tex').write_text('\n'.join(rows)+'\n')
    (outdir/'provenance_large_z.json').write_text(json.dumps(
        dict(metrics=str(metrics_path), metrics_sha256=sha(metrics_path),
             script_sha256=sha(__file__)), indent=1)+'\n')


if __name__ == '__main__':
    {'run': run, 'figures': figures}[sys.argv[1]](*sys.argv[2:])
