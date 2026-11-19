"""Parallel/perpendicular response matrix for like-particle Landau collisions.

M_ij(k) = <a_i, (i k v_x + Lambda)^-1 a_j>, a_par = v_x^2 - 1,
a_perp = v_perp^2/2 - 1, in the polynomial Galerkin space of
shared/scripts/landau_closure (cached Landau matrices, units v_t = tau = 1).

  python response_matrix.py run results/<new-dir>      # refuses to overwrite
  python response_matrix.py constants results/<dir>     # adds constants.json
  python response_matrix.py table results/<dir>/metrics.json figures
"""
import argparse
import hashlib
import json
import platform
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
SHARED = HERE.parents[1] / 'scripts' / 'landau_closure'
sys.path.insert(0, str(SHARED))
from closure3d import vecs, theta, pinv_on_complement  # noqa: E402


def matrix(L, d, k):
    B, ix, one, vx, E2, th, Q, Vx = vecs(d)
    apar = np.zeros(len(B)); apar[ix[(2, 0)]] = np.sqrt(2)
    aperp = np.zeros(len(B)); aperp[ix[(0, 1)]] = -1.0
    a = np.stack([apar, aperp], 1)
    g = np.linalg.solve(1j*k*Vx+L, a.astype(complex))
    return (a.T@g).real, float(np.abs((a.T@g).imag).max())


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def run(out):
    out = Path(out)
    if out.exists():
        raise SystemExit(f'{out} exists; result directories are never overwritten')
    cfg = json.loads((HERE/'config_matrix.json').read_text())
    start = time.time()
    rows, failures = [], []
    for d in cfg['degrees']:
        cache = SHARED/'cache'/f'landau_d{d}.npy'
        L = np.load(cache)
        for k in cfg['k']:
            M, imag = matrix(L, d, k)
            th_pot, n1 = theta(L, d, k)[:2]
            chi_pot = 3/(k*k*(M[0, 0]+2*M[0, 1]))
            checks = dict(asymmetry=float(abs(M[0, 1]-M[1, 0])),
                          imaginary=imag,
                          min_eigenvalue=float(np.linalg.eigvalsh((M+M.T)/2).min()),
                          n1_mismatch=float(abs(M[0, 0]-n1)),
                          potential_mismatch=float(abs(chi_pot-th_pot/k)))
            ok = (checks['asymmetry'] < 1e-9 and imag < 1e-9
                  and checks['min_eigenvalue'] > 0
                  and checks['n1_mismatch'] < 1e-9*max(1, n1)
                  and checks['potential_mismatch'] < 1e-9*max(1, chi_pot))
            if not ok:
                failures.append(dict(degree=d, k=k, checks=checks))
            rows.append(dict(degree=d, k=k, M_par_par=float(M[0, 0]),
                             M_par_perp=float(M[0, 1]), M_perp_perp=float(M[1, 1]),
                             N_theta=float(4*(M[0, 0]-2*M[0, 1]+M[1, 1])),
                             checks=checks, passed=bool(ok)))
    out.mkdir(parents=True)
    metrics = dict(schema_version=cfg['schema_version'], config=cfg,
                   status='complete' if not failures else 'complete_with_failures',
                   uncertainty=dict(ensemble_estimation='none: deterministic',
                                    discretization='difference between degrees 12 and 16; a diagnostic, not a certified bound',
                                    learned_model='none'),
                   environment=dict(python=platform.python_version(), numpy=np.__version__,
                                    platform=platform.platform()),
                   input_hashes={'config_matrix.json': sha(HERE/'config_matrix.json'),
                                 'response_matrix.py': sha(__file__),
                                 **{f'cache/landau_d{d}.npy': sha(SHARED/'cache'/f'landau_d{d}.npy')
                                    for d in cfg['degrees']},
                                 'closure3d.py': sha(SHARED/'closure3d.py')},
                   collisionless_limit=dict(k_M_diagonal=float(np.sqrt(np.pi/2)),
                                            k_M_offdiagonal=0.0, N_theta_over_9n1=8/9),
                   failures=failures, rows=rows, runtime_seconds=time.time()-start)
    (out/'metrics.json').write_text(json.dumps(metrics, indent=1)+'\n')
    print(f"wrote {out/'metrics.json'}; status {metrics['status']}; {len(failures)} failures")


def constants(outdir):
    """Collision-solve constants of the perpendicular criterion (negative result).

    -3 T_1 = c.M c - M_perp,perp with c = (1, 1); the certificates give
    c.M c >= 4/(k^2 kF) and M_perp,perp <= 1/(k^2 kF) + C_perp, so positivity
    would follow from k^2 kF C_perp < 3.  Compared with k^2 kF eta < 3.
    """
    out = Path(outdir)/'constants.json'
    if out.exists():
        raise SystemExit(f'{out} exists; not overwritten')
    cfg = json.loads((HERE/'config_matrix.json').read_text())
    rows = []
    for d in cfg['degrees']:
        L = np.load(SHARED/'cache'/f'landau_d{d}.npy')
        B, ix, one, vx, E2, th, Q, Vx = vecs(d)
        Lp = pinv_on_complement(L, [one, vx, E2])
        Xi = Lp@Q; kF = float(Q@Xi); eta = float(th@Lp@th/12)
        aperp = np.zeros(len(B)); aperp[ix[(0, 1)]] = -1.0
        b = aperp-Vx@Xi/kF
        Cperp = float(b@Lp@b)
        rows.append(dict(degree=d, kappa_F=kF, eta=eta, C_perp=Cperp,
                         source_residual=float(max(abs(b@one), abs(b@E2))),
                         k_max_eta=float(np.sqrt(3/(kF*eta))),
                         k_max_C_perp=float(np.sqrt(3/(kF*Cperp)))))
    out.write_text(json.dumps(dict(schema_version=cfg['schema_version'], rows=rows,
        input_hashes={'response_matrix.py': sha(__file__)}), indent=1)+'\n')
    print(json.dumps(rows, indent=1))


def table(metrics_path, figdir):
    m = json.loads(Path(metrics_path).read_text())
    by = {(r['degree'], r['k']): r for r in m['rows']}
    lo, hi = m['config']['degrees'][0], m['config']['degrees'][-1]
    lines = [r'\begin{tabular}{rrrrrrr}\toprule',
             r'$|k|\tau$ & $|k|M_{\parallel\parallel}$ & $|k|M_{\parallel\perp}$ & '
             r'$|k|M_{\perp\perp}$ & $T_{\perp1}/n_1$ & $N_\vartheta/(9n_1)$ & Refinement\\\midrule']
    for k in m['config']['k']:
        r, s = by[(hi, k)], by[(lo, k)]
        ref = max(abs(r[key]-s[key])/abs(r['M_par_par'])
                  for key in ('M_par_par', 'M_par_perp', 'M_perp_perp'))
        lines.append(f"{k:.1f} & {k*r['M_par_par']:.3f} & {k*r['M_par_perp']:.3f} & "
                     f"{k*r['M_perp_perp']:.3f} & {-r['M_par_perp']/r['M_par_par']:.3f} & "
                     f"{r['N_theta']/(9*r['M_par_par']):.3f} & {ref:.1e} \\\\")
    c = m['collisionless_limit']
    lines += [r'\midrule', f"$\\infty$ & {c['k_M_diagonal']:.3f} & 0 & {c['k_M_diagonal']:.3f} & 0 & "
              f"{c['N_theta_over_9n1']:.3f} & --- \\\\", r'\bottomrule\end{tabular}']
    Path(figdir).mkdir(exist_ok=True)
    (Path(figdir)/'landau_matrix.tex').write_text('\n'.join(lines)+'\n')
    (Path(figdir)/'provenance_matrix.json').write_text(json.dumps(
        dict(metrics_source=str(metrics_path), metrics_sha256=sha(metrics_path),
             note='landau_matrix.tex derives from this saved metrics file.'), indent=2)+'\n')
    print('\n'.join(lines))


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest='cmd', required=True)
    a = sub.add_parser('run'); a.add_argument('out')
    b = sub.add_parser('table'); b.add_argument('metrics'); b.add_argument('figdir')
    c = sub.add_parser('constants'); c.add_argument('out')
    args = p.parse_args()
    if args.cmd == 'run':
        run(args.out)
    elif args.cmd == 'constants':
        constants(args.out)
    else:
        table(args.metrics, args.figdir)
