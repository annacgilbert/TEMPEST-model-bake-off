"""Save all metrics for the extension note. Refuses to overwrite an existing run directory."""
import argparse
import hashlib
import json
import platform
import sys
import time
from pathlib import Path
import numpy as np
import scipy
import electron_numerics as en
from closure3d import constants  # on sys.path after importing electron_numerics

HERE = Path(__file__).resolve().parent
CACHE = en.ROOT/'shared/scripts/landau_closure/cache'
REFERENCE = dict(
    braginskii_gamma0={'1': '3.1616', '2': '4.890', '3': '6.064', '4': '6.920'},
    braginskii_sigma_Z1=1/0.5129,
    lorentz_limit_sigma=32/(3*np.pi), lorentz_limit_kappa=128/(3*np.pi),
    dougherty_K_thermal=16/45, dougherty_K_potential=2/15,
    dougherty_collisionless_thermal=1.8*np.sqrt(2/np.pi),
    note='kappa and sigma in units of n T tau_e/m and n e^2 tau_e/m')


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def grid(spec):
    return np.geomspace(spec['min'], spec['max'], spec['points'])


def run(config, output, rebuild=False):
    output.mkdir(parents=True, exist_ok=False)
    start = time.perf_counter()
    cfg = json.loads(Path(config).read_text())
    np.random.seed(cfg['seed'])
    m = dict(schema_version=cfg['schema_version'], config=cfg, status='running',
             uncertainty=dict(ensemble_estimation='not applicable: deterministic',
                              discretization='degree refinement; not a certified continuum bound',
                              learned_model='not applicable: no training'),
             environment=dict(python=sys.version, numpy=np.__version__, scipy=scipy.__version__,
                              platform=platform.platform(), machine=platform.machine()),
             reference=REFERENCE, input_hashes={}, failures=[], checks={}, matrices=[],
             like_particle=[], dougherty=[], electron_constants=[], lorentz_limit=[],
             electron_curves=[], embedded=[])
    out = output/'metrics.json'

    def save():
        m['runtime_seconds'] = time.perf_counter()-start
        out.write_text(json.dumps(m, indent=1, allow_nan=False)+'\n')
    try:
        for name in ('config.json', 'electron_numerics.py', 'reproduce.py', 'test_electron_numerics.py'):
            m['input_hashes'][name] = digest(HERE/name)
        for name in ('landau3d.py', 'closure3d.py'):
            m['input_hashes'][f'shared/scripts/landau_closure/{name}'] = digest(CACHE.parent/name)
        tol = cfg['quadrature_relative_tolerance']
        Lee, Mei = {}, {}
        for d in cfg['degrees']:
            path = CACHE/f'landau_d{d}.npy'
            t0 = time.perf_counter()
            if path.exists() and not rebuild:
                Lee[d] = np.load(path)
                origin = 'existing cache'
                m['input_hashes'][str(path.relative_to(en.ROOT))] = digest(path)
            else:
                _, Lee[d], _ = en.landau_matrix(d)
                origin = 'fresh'
            Mei[d], chk = en.lorentz_matrix(d)
            B, ix, one, vx, E2, th, Q, Vx = en.vecs(d)
            m['matrices'].append(dict(
                degree=d, basis_size=len(B), landau_origin=origin,
                seconds=time.perf_counter()-t0,
                lorentz_normalization_error=abs(chk-np.sqrt(2/np.pi)),
                lorentz_asymmetry=float(np.abs(Mei[d]-Mei[d].T).max()),
                lorentz_kernel_residual=float(max(np.abs(Mei[d]@one).max(), np.abs(Mei[d]@E2).max())),
                lorentz_min_eigenvalue=float(np.linalg.eigvalsh(Mei[d]).min()),
                momentum_loss_error=float(abs(vx@Mei[d]@vx-2/3*np.sqrt(2/np.pi)))))
        if 6 in Lee:
            _, fresh, _ = en.landau_matrix(6)
            m['checks']['fresh_vs_used_landau_d6_max_abs'] = float(np.abs(fresh-Lee[6]).max())
        save()

        # Like-particle operators: the two drives share kappa but not K.
        for d in cfg['degrees']:
            for name, L in (('landau', Lee[d]), ('dougherty', en.dougherty(d))):
                c = en.transport(L, d, True)
                cp = constants(L, d)
                entry = dict(operator=name, degree=d, thermal=c,
                             K_potential=float(cp['Kexact']), eta=float(cp['eta']), responses=[])
                for k in grid(cfg['like_particle_k']):
                    r = en.thermal_response(L, d, k)
                    Mk = en.anisotropic_matrix(L, d, k)
                    chi_pot, chi_th = en.responses_from_matrix(Mk, k)
                    entry['responses'].append(dict(
                        k=float(k), chi_thermal=r['chi'], chi_potential=float(chi_pot),
                        matrix=[float(Mk[0, 0]), float(Mk[0, 1]), float(Mk[1, 1])],
                        matrix_asymmetry=float(abs(Mk[0, 1]-Mk[1, 0])),
                        matrix_consistency=float(abs(chi_th-r['chi'])),
                        flux_residual=r['flux_residual'],
                        lower_bound=c['kappa']/(1+c['K']*k*k),
                        bounds_hold=bool(c['kappa']/(1+c['K']*k*k)*(1-1e-10) <= r['chi']
                                         <= c['kappa']*(1+1e-10))))
                m['like_particle'].append(entry)
        for k in grid(cfg['dougherty_k']):
            m['dougherty'].append(dict(k=float(k),
                                       theta_thermal=en.dougherty_thermal_theta(k, tol),
                                       theta_potential=en.dougherty_potential_theta(k, tol)))
        dmax = max(cfg['degrees'])
        m['checks']['dougherty_formula_vs_galerkin_max_abs'] = max(
            abs(en.dougherty_thermal_theta(k, tol)/k
                - en.thermal_response(en.dougherty(dmax), dmax, k)['chi']) for k in (.05, .1, .3))
        save()

        # Electrons: constants at every degree and charge.
        for Z in cfg['ion_charges']+cfg['lorentz_limit_charges']:
            for d in cfg['degrees']:
                c = en.transport(en.electron_operator(Lee[d], Mei[d], Z), d, False)
                te = en.tau_e(Z)
                row = dict(Z=Z, degree=d, tau_e=te, constants=c,
                           kappa_over_tau_e=c['kappa']/te, sigma_over_tau_e=c['L11']/te,
                           thermoelectric_ratio=c['L12']/c['L11'],
                           K_over_lambda_e_squared=c['K']/te**2,
                           curvature=c['K']/c['kappa']**2)
                (m['lorentz_limit'] if Z in cfg['lorentz_limit_charges']
                 else m['electron_constants']).append(row)
        save()

        # Electron response curves, with the bounds checked at every point.
        for Z in cfg['ion_charges']:
            for d in cfg['curve_degrees']:
                L = en.electron_operator(Lee[d], Mei[d], Z)
                c = en.transport(L, d, False)
                te = en.tau_e(Z)
                pts = []
                for kl in grid(cfg['electron_k_lambda']):
                    k = kl/te
                    r = en.thermal_response(L, d, k)
                    lower = c['kappa']/(1+c['K']*k*k)
                    pts.append(dict(k_lambda=float(kl), ratio=r['chi']/c['kappa'],
                                    lower_bound_ratio=lower/c['kappa'],
                                    flux_residual=r['flux_residual'],
                                    current_residual=r['current_residual'],
                                    bounds_hold=bool(lower*(1-1e-10) <= r['chi'] <= c['kappa']*(1+1e-10))))
                m['electron_curves'].append(dict(Z=Z, degree=d, points=pts))
        m['checks']['all_bounds_hold'] = bool(
            all(p['bounds_hold'] for c in m['electron_curves'] for p in c['points'])
            and all(r['bounds_hold'] for e in m['like_particle'] for r in e['responses']))
        save()

        # Embedded test: quasi-neutral kinetic decay versus the closed temperature equation.
        dlo, dhi = cfg['embedded_degrees']
        for Z in cfg['embedded_charges']:
            ops = {d: en.electron_operator(Lee[d], Mei[d], Z) for d in (dlo, dhi)}
            c = en.transport(ops[dhi], dhi, False)
            te = en.tau_e(Z)
            for kl in cfg['embedded_k_lambda']:
                k = kl/te
                chi = en.thermal_response(ops[dhi], dhi, k)['chi']
                slow, slow_imag = en.slowest_mode_chi(ops[dhi], dhi, k)
                times = np.linspace(0, cfg['embedded_decay_times']/(2/3*k*k*chi),
                                    cfg['embedded_samples'])
                ref = en.zero_current_rollout(ops[dhi], dhi, k, times)
                low = en.zero_current_rollout(ops[dlo], dlo, k, times)
                item = dict(Z=Z, k_lambda=kl, k=k, decay_time_over_tau_e=1/(2/3*k*k*chi)/te,
                            scaled_time=(times*(2/3*k*k*chi)).tolist(),
                            kinetic_T=ref['T'].real.tolist(),
                            numerical_refinement_error=en.relative_history_error(low['T'], ref['T'], times),
                            density_max_abs=float(np.abs(ref['n']).max()),
                            current_max_abs=float(np.abs(ref['u']).max()),
                            kinetic_energy_max_increase=float(np.diff(ref['energy']).max()),
                            slowest_mode_imaginary_part=slow_imag, models={})
                for name, value in (('quasistatic', chi), ('fourier', c['kappa']), ('slowest_mode', slow)):
                    T = en.temperature_decay(k, value, times)
                    item['models'][name] = dict(
                        chi_over_kappa=value/c['kappa'],
                        relative_history_error=en.relative_history_error(T, ref['T'], times),
                        T=T.tolist())
                m['embedded'].append(item)
                save()
        m['status'] = 'complete'
    except Exception as error:
        m['status'] = 'failed'
        m['failures'].append(dict(type=type(error).__name__, message=str(error)))
        raise
    finally:
        save()
    print(f"Saved {out}; status {m['status']}; runtime {m['runtime_seconds']:.1f}s", flush=True)


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--config', default=str(HERE/'config.json'))
    p.add_argument('--output', required=True)
    p.add_argument('--rebuild-landau', action='store_true')
    a = p.parse_args()
    run(a.config, Path(a.output), a.rebuild_landau)
