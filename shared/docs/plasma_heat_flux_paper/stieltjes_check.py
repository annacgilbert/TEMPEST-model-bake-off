"""Numerical check of the Stieltjes structure of the quasi-static closure.

For z = k^2 off the negative real axis, a Stieltjes function chi(z) has
Im chi(z) <= 0 when Im z > 0, is nonincreasing on z > 0, and z chi(z) is
nondecreasing there.  This script tests those signs for

  - closed forms: 1D BGK, 1D and 3D Dougherty (potential drive), 3D
    Dougherty (thermal drive), continued analytically in z (the Dougherty
    integrals only where they converge, Re z > -1/2 here);
  - Galerkin solves: like-particle Landau and the electron operator, both
    drives;
  - a seeded random finite-dimensional model of the abstract theorem;

and the Pade bounds for the thermal Dougherty response, whose k^4
coefficient is computed here.

  python stieltjes_check.py results/<new-dir>      # refuses to overwrite
"""
import hashlib
import json
import platform
import sys
import time
from fractions import Fraction
from pathlib import Path

import numpy as np
from scipy.integrate import quad

HERE = Path(__file__).resolve().parent
SHARED = HERE.parents[1] / 'scripts' / 'landau_closure'
ELECTRON = HERE.parent / 'electron_heat_flux_extension'
sys.path.insert(0, str(SHARED))
sys.path.insert(0, str(ELECTRON))
from closure3d import vecs, dougherty  # noqa: E402
from electron_numerics import lorentz_matrix, electron_operator  # noqa: E402


def cquad(f, a, b, **kw):
    return quad(f, a, b, complex_func=True, epsabs=0, epsrel=1e-11, limit=800, **kw)[0]


# ---- closed forms, nu = 1, as functions of complex z = k^2 --------------
def dint(p, z):
    """int_0^1 p(s) exp(z [s + log(1-s)]) ds."""
    return cquad(lambda s: p(s)*np.exp(z*(s+np.log1p(-s))), 0, 1)


def dougherty_1d(z):
    return dint(lambda s: s, z)/dint(lambda s: 1.0, z)


def dougherty_3d_pot(z):
    return dint(lambda s: s*(3-2*s), z)/dint(lambda s: 1.0, z)


def dougherty_3d_th(z):
    return 3*dint(lambda s: s*(3-2*s), z)/dint(lambda s: 5-4*s, z)


def bgk_1d(z):
    s = 1/z
    w = lambda v: np.exp(-v*v/2)
    num = cquad(lambda v: w(v)*(v**3-3*v)**2/(v*v+s), -np.inf, np.inf)
    den = cquad(lambda v: w(v)*(v*v-1)**2/(v*v+s), -np.inf, np.inf)
    return (1+s)/(2*(3+s))*num/den


# ---- Galerkin responses ---------------------------------------------------
def galerkin(L, d):
    B, ix, one, vx, E2, th, Q, Vx = vecs(d)
    zeta = E2/3

    def thermal(z):
        k = np.sqrt(complex(z))
        return 1/(z*(zeta@np.linalg.solve(1j*k*Vx+L, zeta.astype(complex))))

    def potential(z):
        k = np.sqrt(complex(z))
        return -1/(z*(zeta@np.linalg.solve(1j*k*Vx+L, one.astype(complex))))
    return thermal, potential


# ---- random finite-dimensional model of the theorem ------------------------
def random_model(rng, ne, no):
    X = rng.standard_normal((ne, ne-1))
    A = X@X.T                                  # collision form, 1-dim kernel
    Y = rng.standard_normal((no, no))
    Lo = Y@Y.T+0.1*np.eye(no)                  # odd block, positive definite
    V = rng.standard_normal((ne, no))          # streaming, even <- odd
    Bm = V@np.linalg.solve(Lo, V.T)            # streaming form
    ell = rng.standard_normal(ne)
    return lambda z: 1/(z*(ell@np.linalg.solve(A+z*Bm, ell.astype(complex))))


def sign_test(chi, cfg, real_scale=1.0, min_real=None):
    """Largest Im chi / |chi| in the upper half plane and the real-axis trends.

    min_real: the closed-form Dougherty integrals converge only for
    Re z > -1, so those tests skip sample points with Re z <= min_real.
    """
    worst, where, violations, sampled, skipped = -np.inf, None, [], 0, 0
    for r in cfg['radii']:
        for a in cfg['angles_over_pi']:
            z = real_scale*r*np.exp(1j*np.pi*a)
            if min_real is not None and z.real <= min_real:
                skipped += 1
                continue
            sampled += 1
            c = chi(z)
            if c.imag/abs(c) > worst:
                worst, where = float(c.imag/abs(c)), [r, a]
            if c.imag/abs(c) > cfg['tolerance']:
                violations.append([r, a, float(c.imag/abs(c))])
    t = real_scale*np.array(cfg['real_axis'])
    c = np.array([chi(x).real for x in t])
    imag_real_axis = max(abs(chi(x).imag) for x in t)
    return dict(points_sampled=sampled, points_skipped=skipped,
                sign_violations=violations,
                max_imag_over_abs=worst, at_radius_angle=where,
                max_increase_chi=float(np.max(np.diff(c)/c[:-1])),
                max_decrease_z_chi=float(np.max(-np.diff(t*c)/(t*c)[:-1])),
                min_chi=float(c.min()), imag_on_real_axis=float(imag_real_axis))


def passes(r, tol):
    return (r['max_imag_over_abs'] <= tol and r['max_increase_chi'] <= tol
            and r['max_decrease_z_chi'] <= tol and r['min_chi'] > 0)


def dougherty_exact():
    """Exact K and K_2 of the thermal Dougherty response, in rationals.

    With u = 1-s: L = 1-u+log u, p = (1-u)(1+2u), r = 1+4u, and
    int_0^1 u^j log^m u du = (-1)^m m!/(j+1)^(m+1).
    """
    from math import factorial
    from numpy.polynomial import polynomial as P

    def integral(poly, m):                     # int poly(u) log^m u du
        return sum(Fraction(int(c))*(-1)**m*factorial(m)/Fraction(j+1)**(m+1)
                   for j, c in enumerate(poly))

    def moments(w):                            # int w, int w L, int w L^2
        a = [1, -1]
        w = [int(c) for c in w]
        wa = [int(c) for c in P.polymul(w, a)]
        waa = [int(c) for c in P.polymul(wa, a)]
        return (integral(w, 0), integral(wa, 0)+integral(w, 1),
                integral(waa, 0)+2*integral(wa, 1)+integral(w, 2))
    N0, N1, N2 = moments([1, 1, -2])
    D0, D1, D2 = moments([1, 4])
    K = -(N1/N0-D1/D0)
    K2 = N2/(2*N0)-D2/(2*D0)-(N1/N0)*(D1/D0)+(D1/D0)**2
    return K, K2


def dougherty_pade():
    """k^4 coefficient of the thermal Dougherty response and the Pade bounds."""
    L = lambda s: s+np.log1p(-s)
    p = lambda s: s*(3-2*s)
    r = lambda s: 5-4*s
    I = lambda f: quad(f, 0, 1, epsabs=0, epsrel=1e-13, limit=400)[0]
    N0, N1, N2 = I(p), I(lambda s: p(s)*L(s)), I(lambda s: p(s)*L(s)**2)
    D0, D1, D2 = I(r), I(lambda s: r(s)*L(s)), I(lambda s: r(s)*L(s)**2)
    K = -(N1/N0-D1/D0)
    K2 = N2/(2*N0)-D2/(2*D0)-(N1/N0)*(D1/D0)+(D1/D0)**2
    rows = []
    for z in [0.01, 0.1, 0.3, 1.0, 3.0, 10.0, 100.0]:
        ratio = dougherty_3d_th(z).real*6/5
        lower = 1/(1+K*z)
        upper = 1-K*z/(1+z*K2/K)
        rows.append(dict(z=z, chi_over_kappa=ratio, pade_lower=lower, pade_upper=upper,
                         ok=bool(lower <= ratio+1e-10 and ratio <= upper+1e-10)))
    Kx, K2x = dougherty_exact()
    return dict(K_quadrature=K, K_exact=str(Kx), K2_quadrature=K2, K2_exact=str(K2x),
                exact_minus_quadrature=[abs(float(Kx)-K), abs(float(K2x)-K2)],
                rows=rows)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main(out):
    out = Path(out)
    if out.exists():
        raise SystemExit(f'{out} exists; result directories are never overwritten')
    cfg = json.loads((HERE/'config_stieltjes.json').read_text())
    tol = cfg['tolerance']
    start = time.time()
    proved, observed, failures = {}, {}, []

    def record(group, name, chi, **kw):
        try:
            r = sign_test(chi, cfg, **kw)
            r['stieltjes_signs_hold'] = bool(passes(r, tol))
        except Exception as exc:               # reported, never dropped
            r = dict(error=repr(exc), stieltjes_signs_hold=False)
        group[name] = r
        if group is proved and not r['stieltjes_signs_hold']:
            failures.append(name)

    record(proved, 'bgk_1d_potential', bgk_1d)
    record(proved, 'dougherty_1d_potential', dougherty_1d, min_real=-0.5)
    record(proved, 'dougherty_3d_thermal', dougherty_3d_th, min_real=-0.5)
    record(observed, 'dougherty_3d_potential', dougherty_3d_pot, min_real=-0.5)
    hashes = {}
    for d in cfg['galerkin_degrees']:
        cache = SHARED/'cache'/f'landau_d{d}.npy'
        hashes[cache.name] = sha(cache)
        Lee = np.load(cache)
        th, pot = galerkin(dougherty(d), d)
        record(proved, f'dougherty_galerkin_d{d}_thermal', th)
        record(observed, f'dougherty_galerkin_d{d}_potential', pot)
        th, pot = galerkin(Lee, d)
        record(proved, f'landau_d{d}_thermal', th)
        record(observed, f'landau_d{d}_potential', pot)
        M = lorentz_matrix(d)[0]
        for Z in cfg['ion_charges']:
            th, _ = galerkin(electron_operator(Lee, M, Z), d)
            # electron lengths shrink like 1/Z; sample the same k*lambda_e range
            record(proved, f'electron_Z{Z}_d{d}_thermal', th, real_scale=Z*Z)
    rng = np.random.default_rng(cfg['seed'])
    rm = cfg['random_model']
    for i in range(rm['trials']):
        record(proved, f'random_model_{i}', random_model(rng, rm['even_dim'], rm['odd_dim']))
    pade = dougherty_pade()
    if not all(r['ok'] for r in pade['rows']):
        failures.append('dougherty_pade')
    metrics = dict(schema_version=cfg['schema_version'], config=cfg,
                   status='complete' if not failures else 'complete_with_failures',
                   failures=failures, covered_by_theorem=proved,
                   not_covered_by_theorem=observed, dougherty_thermal_pade=pade,
                   input_hashes=hashes, script_sha256=sha(__file__),
                   environment=dict(python=platform.python_version(), numpy=np.__version__,
                                    platform=platform.platform()),
                   runtime_seconds=time.time()-start)
    out.mkdir(parents=True)
    (out/'metrics.json').write_text(json.dumps(metrics, indent=1))
    print(json.dumps(dict(status=metrics['status'], failures=failures,
                          runtime=metrics['runtime_seconds']), indent=1))
    for g in (proved, observed):
        for k, v in g.items():
            print(f"{k:32s} {v.get('max_imag_over_abs', float('nan')):+.2e} "
                  f"{v.get('max_increase_chi', float('nan')):+.2e} "
                  f"{v.get('max_decrease_z_chi', float('nan')):+.2e} {v['stieltjes_signs_hold']}")
    print(json.dumps(pade, indent=1))


if __name__ == '__main__':
    main(sys.argv[1])
