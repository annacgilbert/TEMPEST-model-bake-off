"""Counterexamples for the potential-driven closure in three velocity dimensions.

Relaxation operators with separate rates (v_t = 1):

  Lambda = nu (I - Pi_H) - (nu - nu_s) Pi_theta - (nu - nu_q) Pi_Q,

Pi_theta, Pi_Q the projections on the stress mode theta = v_perp^2 - 2 v_x^2
and the heat-flux mode Q = v_x (|v|^2 - 5)/2.  nu_q = nu is the linearized
ellipsoidal-statistical (ES) BGK operator.  Three independent evaluations of
the stationary response are compared:

  closed     explicit rational formulas in c(a) = <nu^2/(nu^2 + k^2 v_x^2)>;
  finite     the finite-rank linear system in polynomials of degree <= 4 with
             Gaussian integrals of 1/(nu + i k v_x) done by quadrature;
  galerkin   the polynomial Galerkin solve of shared/scripts/landau_closure.

Galerkin degree differences are diagnostics, not error bars.

  python potential_counterexample.py results/<new-dir>   # refuses to overwrite
"""
import hashlib
import json
import platform
import sys
import time
import warnings
from pathlib import Path

import numpy as np
import scipy
from numpy.polynomial.hermite_e import hermegauss
from numpy.polynomial.laguerre import laggauss
from scipy.integrate import quad
from scipy.optimize import brentq, minimize_scalar
from scipy.special import erfcx, eval_laguerre

HERE = Path(__file__).resolve().parent
SHARED = HERE.parents[1] / 'scripts' / 'landau_closure'
sys.path.insert(0, str(SHARED))
from closure3d import vecs, dougherty, constants, second_order, pinv_on_complement  # noqa: E402
from landau3d import basis, psi  # noqa: E402

GAUSS = 1/np.sqrt(2*np.pi)


# ---- polynomial vectors ----------------------------------------------------
def project(f, d):
    """Coefficients of f(v_x, t), t = v_perp^2/2, in psi_n(v_x) L_m(t)."""
    x, w = hermegauss(48)
    t, wt = laggauss(48)
    X, T = np.meshgrid(x, t, indexing='ij')
    W = np.outer(w*GAUSS, wt)*f(X, T)
    return np.array([(W*psi(n, X)*eval_laguerre(m, T)).sum() for n, m in basis(d)])


def sources(d):
    B, ix, one, vx, E2, th, Q, Vx = vecs(d)
    apar = np.zeros(len(B)); apar[ix[(2, 0)]] = np.sqrt(2)
    aperp = np.zeros(len(B)); aperp[ix[(0, 1)]] = -1.0
    return apar, aperp


def relaxation(d, nu, nus=None, nuq=None, block=None):
    """Galerkin matrix of the relaxation operator at degree d.

    block: 2x2 positive definite matrix on the orthonormal l = 2 modes
    e0 = theta/sqrt(12), e1 = theta (|v|^2 - 7)/sqrt(168); overrides nus.
    """
    B, ix, one, vx, E2, th, Q, Vx = vecs(d)
    nb = len(B)
    L = nu*np.eye(nb)
    for h in (one, vx, E2/np.sqrt(6)):
        L -= nu*np.outer(h, h)
    e0 = th/np.sqrt(12)
    if block is not None:
        e1 = project(lambda x, t: (2*t-2*x*x)*(x*x+2*t-7), d)/np.sqrt(168)
        P = np.stack([e0, e1], 1)
        L += P@(np.asarray(block)-nu*np.eye(2))@P.T
    elif nus is not None:
        L += (nus-nu)*np.outer(e0, e0)
    if nuq is not None:
        eq = Q/np.sqrt(2.5)
        L += (nuq-nu)*np.outer(eq, eq)
    return L


def galerkin_response(L, d, k):
    """n1, T1, Tperp and the 2x2 matrix M from a Galerkin solve."""
    B, ix, one, vx, E2, th, Q, Vx = vecs(d)
    apar, aperp = sources(d)
    S = np.stack([one, apar, aperp], 1).astype(complex)
    g = np.linalg.solve(1j*k*Vx+L, S)
    n1 = (one@g[:, 0]).real
    return dict(n1=n1, T1=(E2@g[:, 0]).real/3, Tperp=(aperp@g[:, 0]).real,
                Mpp=(apar@g[:, 1]).real, Mpq=(apar@g[:, 2]).real,
                Mqq=(aperp@g[:, 2]).real)


# ---- finite-rank solve with Gaussian integrals -----------------------------
_JCACHE = {}


def jmatrix(k, nu):
    """j[n, n'] = <psi_n psi_n' / (nu + i k v)>, n, n' <= 4, by quadrature."""
    key = (float(k), float(nu))
    if key in _JCACHE:
        return _JCACHE[key]
    w = min(nu/abs(k), 6.0)
    pts = sorted({0.0, w, 10*w if 10*w < 12 else 6.0, 1.0, 3.0})
    j = np.zeros((5, 5), complex)
    for n in range(5):
        for m in range(n, 5):
            def base(v):
                return GAUSS*np.exp(-v*v/2)*psi(n, v)*psi(m, v)/(nu*nu+k*k*v*v)
            if (n+m) % 2 == 0:      # even product: real part
                val = 2*nu*quad(base, 0, 12, points=pts, epsabs=0, epsrel=1e-12, limit=400)[0]
            else:                   # odd product: imaginary part
                val = -2j*k*quad(lambda v: v*base(v), 0, 12, points=pts,
                                 epsabs=0, epsrel=1e-12, limit=400)[0]
            j[n, m] = j[m, n] = val
    _JCACHE[key] = j
    return j


def finite_rank_response(L4, nu, k):
    """Exact response of Lambda = nu - K, K of finite rank in degree <= 4.

    (nu + i k v_x) g = s + K Pi_4 g; the coefficients m of Pi_4 g solve
    (I - J K) m = J s with J the Gram matrix of 1/(nu + i k v_x).
    """
    B = basis(4)
    j = jmatrix(k, nu)
    J = np.array([[j[n, n2] if m == m2 else 0 for (n2, m2) in B] for (n, m) in B])
    K = nu*np.eye(len(B))-L4
    _, ix, one, vx, E2, th, Q, Vx = vecs(4)
    apar, aperp = sources(4)
    S = np.stack([one, apar, aperp], 1).astype(complex)
    m = np.linalg.solve(np.eye(len(B))-J@K, J@S)
    out = dict(n1=(one@m[:, 0]).real, T1=(E2@m[:, 0]).real/3, Tperp=(aperp@m[:, 0]).real,
               Mpp=(apar@m[:, 1]).real, Mpq=(apar@m[:, 2]).real, Mqq=(aperp@m[:, 2]).real)
    out['residuals'] = float(max(abs(1j*k*(vx@m[:, 0])-1), abs(Q@m[:, 0]-1j/k),
                                 abs(m[:, 0].real@(one+apar)),       # <v_x^2 g> = 0
                                 abs(out['Mpq']-(aperp@m[:, 1]).real),
                                 abs(out['Mpp']-out['n1']), abs(out['Mpq']+out['Tperp'])))
    return out


# ---- closed forms ----------------------------------------------------------
def c_delta_D(a):
    """c = <1/(1 + a v^2)>, delta = 1 - c, D = c - delta/a, from positive integrals."""
    pts = sorted({min(1/np.sqrt(a), 6.0), min(10/np.sqrt(a), 8.0), 1.0, 3.0})
    kw = dict(points=pts, epsabs=0, epsrel=1e-13, limit=400)
    delta = 2*quad(lambda v: GAUSS*np.exp(-v*v/2)*a*v*v/(1+a*v*v), 0, 12, **kw)[0]
    D = 2*a/(1+a)*quad(lambda v: GAUSS*np.exp(-v*v/2)*(v*v-1)**2/(1+a*v*v), 0, 12, **kw)[0]
    return 1-delta, delta, D


def c_complex(a):
    y = 1/np.sqrt(complex(a))
    return np.sqrt(np.pi/2)*y*erfcx(y/np.sqrt(2))


def closed_potential(k, nu, nus, nuq):
    """Potential-driven response of the three-rate operator (nu_q = nu: ES)."""
    a = (k/nu)**2
    c, dl, D = c_delta_D(a)
    sg, rho = nus/nu, nuq/nu
    om = 2*(1-rho)/(5*a)
    Dl = 3*dl+c*sg
    W = 2*dl*Dl-D*(3*dl+sg*(3*c-2))
    N = (2*D*Dl-2*sg*om*dl*D+om*Dl*(D-2*dl))/W
    tp = (3*om*dl-c*sg*N)/Dl
    n1, Tperp = N/nu, tp/nu
    return dict(n1=n1, Tperp=Tperp, T1=(2*Tperp-n1)/3)


def closed_es_matrix(k, nu, nus):
    """Response matrix of the ES operator."""
    a = (k/nu)**2
    c, dl, D = c_delta_D(a)
    sg = nus/nu
    Dl = 3*dl+c*sg
    W = 2*dl*Dl-D*(3*dl+sg*(3*c-2))
    E = 6*dl-D*(3-2*sg)
    return dict(Mpp=2*Dl*D/W/nu, Mpq=2*c*sg*D/W/nu, Mqq=c*E/W/nu, c=c, delta=dl, D=D, W=W)


def es_chi_complex(z, sg):
    """nu chi_pot of the ES operator at complex a = k^2/nu^2 = z."""
    c = c_complex(z)
    dl = 1-c
    D = c-dl/z
    W = 2*dl*(3*dl+c*sg)-D*(3*dl+sg*(3*c-2))
    return W/(2*z*D*(dl+c*sg))


def chis(M, k):
    pot = 3/(k*k*(M['Mpp']+2*M['Mpq']))
    th = 9/(k*k*(M['Mpp']+4*M['Mpq']+4*M['Mqq']))
    return pot, th


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def rel(x, y):
    return float(abs(x-y)/max(abs(x), abs(y), 1e-300))


# ---- main -------------------------------------------------------------------
def main(out):
    out = Path(out)
    if out.exists():
        raise SystemExit(f'{out} exists; result directories are never overwritten')
    cfg = json.loads((HERE/'config_counterexample.json').read_text())
    np.random.seed(cfg['seed'])
    start = time.time()
    checks, failures, nonconverged, findings = {}, [], [], {}
    caught = []
    warnings.showwarning = lambda msg, cat, fn, ln, *a: caught.append(f'{cat.__name__} line {ln}: {str(msg).split(chr(10))[0]}')
    warnings.simplefilter('always')

    def check(name, ok, **details):
        checks[name] = dict(passed=bool(ok), **details)
        if not ok:
            failures.append(name)

    degs = cfg['galerkin_degrees']
    dmax = max(degs)

    # 1. exact polynomial identities used in the proofs (Galerkin vectors, d = 8)
    B, ix, one, vx, E2, th, Q, Vx = vecs(8)
    vx2 = Vx@Vx@one
    bstar = one-vx2+0.4*Vx@Q
    vth, vQ = Vx@th, Vx@Q
    S = [one, vx, E2/np.sqrt(6), th/np.sqrt(12), Q/np.sqrt(2.5)]
    perp = lambda u: u-sum((s@u)*s for s in S)
    ident = dict(theta_norm2=float(th@th), Q_norm2=float(Q@Q),
                 theta_bstar=float(th@bstar), bstar_norm2=float(bstar@bstar),
                 bstar_rest_norm2=float((bstar-th/5)@(bstar-th/5)),
                 vx_theta_on_vx=float(vth@vx), vx_theta_on_Q=float(vth@Q),
                 vxQ_on_E2=float(vQ@E2), vxQ_on_theta=float(vQ@th),
                 perp_vx_theta_norm2=float(perp(vth)@perp(vth)),
                 perp_vxQ_norm2=float(perp(vQ)@perp(vQ)))
    expect = dict(theta_norm2=12, Q_norm2=2.5, theta_bstar=2.4, bstar_norm2=44/25,
                  bstar_rest_norm2=32/25, vx_theta_on_vx=-4, vx_theta_on_Q=-4,
                  vxQ_on_E2=5, vxQ_on_theta=-4, perp_vx_theta_norm2=108/5, perp_vxQ_norm2=8)
    err = max(abs(ident[k]-expect[k]) for k in expect)
    check('polynomial_identities', err < 1e-10, values=ident, expected=expect, max_error=err)

    # 2. transport constants: Galerkin collision solves against the formulas
    rows = []
    worst = 0.0
    params = [(1.0, s, 1.0) for s in cfg['constants_sigma']]+[tuple(p) for p in cfg['constants_three_rate']]
    for nu, nus, nuq in params:
        for d in degs:
            L = relaxation(d, nu, nus, nuq)
            cst = constants(L, d)
            so = second_order(L, d)
            _, _, one, vx, E2, th, Q, Vx = vecs(d)
            Lp = pinv_on_complement(L, [one, vx, E2])
            bth = E2/3-Vx@(Lp@Q)/cst['kF']
            Kth = cst['kF']*(bth@Lp@bth)
            f = dict(kF=5/(2*nuq), eta=1/nus, Cs=12/(25*nus)+32/(25*nu), X0=12/(5*nus),
                     Kexact=4/(5*nuq)*(4/nu-1/nus))
            f_Kth = 8/(15*nuq*nus)+16/(5*nuq*nu)
            e = max(max(abs(cst[k]-f[k]) for k in f), abs(Kth-f_Kth),
                    abs(Kth-cst['Kexact']-cst['kF']*(4*cst['eta']-cst['X0'])/3))
            worst = max(worst, e)
            rows.append(dict(nu=nu, nu_s=nus, nu_q=nuq, degree=d, K_galerkin=float(cst['Kexact']),
                             K_formula=f['Kexact'], K_th_galerkin=float(Kth), K_th_formula=f_Kth,
                             B_second_order=float(so['B']), kernel=float(cst['kern']),
                             min_eigenvalue=float(cst['mineig']), max_error=float(e)))
    check('constants_three_rate_and_es', worst < 1e-9, max_error=worst, rows=rows)
    Kbgk = [r for r in rows if r['nu_s'] == 1.0 and r['nu_q'] == 1.0 and r['nu'] == 1.0][0]
    cd = constants(dougherty(dmax), dmax)
    check('K_bgk_3d_is_12_over_5', abs(Kbgk['K_galerkin']-2.4) < 1e-10,
          K_galerkin=Kbgk['K_galerkin'], K_formula=2.4)
    check('K_dougherty_is_2_over_15', abs(cd['Kexact']-2/15) < 1e-10, K_galerkin=float(cd['Kexact']))

    # 3. the universal stress component <theta, b_*> = 12/5 and K_th - K_pot
    uni = []
    ops = {'dougherty': lambda d: dougherty(d), 'bgk': lambda d: relaxation(d, 1.0),
           'landau': lambda d: np.load(SHARED/'cache'/f'landau_d{d}.npy'),
           'offdiagonal': lambda d: relaxation(d, cfg['offdiagonal_example']['nu'], block=_block(cfg))}
    hashes = {}
    for name, make in ops.items():
        for d in cfg['landau_degrees']:
            L = make(d)
            _, _, one, vx, E2, th, Q, Vx = vecs(d)
            Lp = pinv_on_complement(L, [one, vx, E2])
            Xi = Lp@Q; kF = Q@Xi
            bs = one-Vx@Vx@one+Vx@Xi/kF
            bth = E2/3-Vx@Xi/kF
            eta, X0 = th@Lp@th/12, th@Lp@bs
            Kpot, Kth = kF*(bs@Lp@bs-X0/3), kF*(bth@Lp@bth)
            uni.append(dict(operator=name, degree=d, theta_bstar=float(th@bs), kappa=float(kF),
                            eta=float(eta), X0=float(X0), K_pot=float(Kpot), K_th=float(Kth),
                            K_th_minus_K_pot=float(Kth-Kpot),
                            identity_rhs=float(kF*(4*eta-X0)/3),
                            four_eta_minus_X0=float(4*eta-X0)))
    e1 = max(abs(r['theta_bstar']-2.4) for r in uni)
    e2 = max(abs(r['K_th_minus_K_pot']-r['identity_rhs'])/max(1, abs(r['K_th'])) for r in uni)
    check('universal_stress_component_and_K_identity', e1 < 1e-8 and e2 < 1e-8,
          max_error_theta_bstar=e1, max_error_identity=e2, rows=uni)
    for d in cfg['landau_degrees']:
        hashes[f'cache/landau_d{d}.npy'] = sha(SHARED/'cache'/f'landau_d{d}.npy')

    # 4. cross-checks: closed form, finite-rank quadrature, Galerkin
    cross, worst_exact = [], 0.0
    jobs = [(1.0, s, 1.0, k) for s in cfg['crosscheck_es']['sigma'] for k in cfg['crosscheck_es']['k']]
    jobs += [(p[0], p[1], p[2], k) for p in cfg['crosscheck_three_rate']['params']
             for k in cfg['crosscheck_three_rate']['k']]
    for nu, nus, nuq, k in jobs:
        cl = closed_potential(k, nu, nus, nuq)
        fr = finite_rank_response(relaxation(4, nu, nus, nuq), nu, k)
        e = max(rel(cl[q], fr[q]) for q in ('n1', 'Tperp', 'T1'))
        row = dict(nu=nu, nu_s=nus, nu_q=nuq, k=k, closed=cl,
                   finite_rank={q: fr[q] for q in ('n1', 'Tperp', 'T1', 'Mpp', 'Mpq', 'Mqq')},
                   finite_rank_residuals=fr['residuals'], closed_vs_finite_rank=e)
        if nuq == nu:
            Mc = closed_es_matrix(k, nu, nus)
            e = max(e, max(rel(Mc[q], fr[q]) for q in ('Mpp', 'Mpq', 'Mqq')))
            row['closed_matrix'] = {q: Mc[q] for q in ('Mpp', 'Mpq', 'Mqq')}
            row['closed_vs_finite_rank'] = e
        worst_exact = max(worst_exact, e, fr['residuals'])
        row['galerkin_vs_finite_rank'] = {}
        for d in degs:
            ga = galerkin_response(relaxation(d, nu, nus, nuq), d, k)
            dg = max(rel(ga[q], fr[q]) for q in ('n1', 'T1', 'Mpq', 'Mqq'))
            row['galerkin_vs_finite_rank'][str(d)] = dg
            if d == dmax and dg > 1e-6:
                nonconverged.append(dict(what='galerkin_vs_finite_rank', nu=nu, nu_s=nus,
                                         nu_q=nuq, k=k, degree=d, relative_difference=dg))
        cross.append(row)
    check('closed_form_vs_finite_rank', worst_exact < cfg['crosscheck_tolerance_exact'],
          max_relative_difference=worst_exact, rows=cross)

    # 5. small-k slope of the ES closed form against K
    slope = []
    for s in cfg['constants_sigma']:
        K = 16/5-4/(5*s)
        for k in cfg['small_k_slope_k']:
            cl = closed_potential(k, 1.0, s, 1.0)
            chi = -1/(k*k*cl['T1'])
            slope.append(dict(sigma=s, k=k, K_formula=K, deficit_over_k2=(1-chi/2.5)/(k*k),
                              chi_over_kappa=chi/2.5))
    e = max(abs(r['deficit_over_k2']-r['K_formula']) for r in slope if r['k'] == min(cfg['small_k_slope_k']))
    check('es_small_k_slope', e < 0.02, max_difference_at_smallest_k=e, rows=slope)
    findings['fourier_bound_violated_small_k'] = [
        dict(sigma=r['sigma'], k=r['k'], chi_over_kappa=r['chi_over_kappa'])
        for r in slope if r['chi_over_kappa'] > 1]

    # 6. the ES plane (k/nu, nu_s/nu): closed form
    lo, hi = cfg['es_k_log10_range']
    ks = np.logspace(lo, hi, cfg['es_k_points'])
    es_rows, th_ok, a2_ok, cond_a_ok, pos_ok = [], True, True, True, True
    for s in cfg['es_sigma']:
        chi, chit, tau, nth, crit = [], [], [], [], []
        for k in ks:
            M = closed_es_matrix(k, 1.0, s)
            p, t = chis(M, k)
            chi.append(p); chit.append(t); tau.append(-M['Mpq']/M['Mpp'])
            nth.append(4*(M['Mpp']-2*M['Mpq']+M['Mqq'])/(9*M['Mpp']))
            c, dl, D = M['c'], M['delta'], M['D']
            crit.append(24*c*dl-12*c*D-30*dl*D-18*c*s*D)
        chi, chit, tau, nth, crit = map(np.array, (chi, chit, tau, nth, crit))
        Kth = 16/5+8/(15*s)
        ok_th = bool(np.all(chit <= 2.5*(1+1e-10)) and np.all(chit >= 2.5/(1+Kth*ks*ks)*(1-1e-10)))
        th_ok &= ok_th
        a2_ok &= bool(np.all(chi > chit))
        cond_a_ok &= bool(np.all((tau > -1) & (tau < 0)))
        pos_ok &= bool(np.all(chi > 0))
        bad = ks[nth >= 1]
        above = ks[chi > 2.5]
        i = int(np.argmax(chi))
        es_rows.append(dict(
            sigma=s, max_chi_over_kappa=float(chi[i]/2.5), k_at_max=float(ks[i]),
            k_range_chi_above_kappa=[float(above.min()), float(above.max())] if len(above) else None,
            min_theta=float((ks*chi).min()), Tperp_over_n1_range=[float(tau.min()), float(tau.max())],
            max_Ntheta_over_9n1=float(nth.max()),
            k_range_Ntheta_ge_9n1=[float(bad.min()), float(bad.max())] if len(bad) else None,
            criterion_sign_agrees=bool(np.all((crit >= 0) == (nth >= 1))),
            chi_nonincreasing=bool(np.all(np.diff(chi) <= 1e-12*chi[:-1])),
            k2chi_nondecreasing=bool(np.all(np.diff(ks*ks*chi) >= -1e-12*(ks*ks*chi)[:-1])),
            min_chi_pot_minus_chi_th_over_kappa=float(((chi-chit)/2.5).min()),
            thermal_bounds_hold=ok_th, thermal_K=Kth))
    findings['es_plane'] = dict(k_grid=[float(ks[0]), float(ks[-1]), len(ks)], rows=es_rows)
    check('es_thermal_bounds_cor_7_3', th_ok)
    check('es_condition_a_holds_on_grid', cond_a_ok)
    check('es_chi_pot_positive_on_grid', pos_ok)
    check('es_chi_pot_exceeds_chi_th_on_grid', a2_ok)
    check('es_Ntheta_criterion_matches', all(r['criterion_sign_agrees'] for r in es_rows))
    # sigma -> 0 limit of chi/kappa at fixed a and the coefficient 12 a^2
    lim = []
    for a in (1e-3, 1e-2, 1e-1, 1.0):
        c, dl, D = c_delta_D(a)
        lim.append(dict(a=a, chi_over_kappa_sigma_to_0=float(3*(2*dl-D)/(5*a*D)),
                        Ntheta_criterion_sigma0_over_a2=float((24*c*dl-12*c*D-30*dl*D)/a**2)))
    findings['es_sigma_to_zero'] = lim

    # 7. Stieltjes signs of the ES potential response (closed form, complex k^2)
    st = cfg['stieltjes']
    st_rows = []
    radii = np.logspace(st['radii_log10_range'][0], st['radii_log10_range'][1], st['radii_points'])
    for s in st['sigma']:
        worst, where, nviol = -np.inf, None, 0
        for r in radii:
            for ang in st['angles_over_pi']:
                x = es_chi_complex(r*np.exp(1j*np.pi*ang), s)
                v = float(x.imag/abs(x))
                nviol += v > st['tolerance']
                if v > worst:
                    worst, where = v, [r, ang]
        row = [e for e in es_rows if e['sigma'] == s][0]
        st_rows.append(dict(sigma=s, max_imag_over_abs=worst, at_radius_angle=where,
                            sign_violations=int(nviol),
                            points=len(radii)*len(st['angles_over_pi']),
                            chi_nonincreasing=row['chi_nonincreasing'],
                            k2chi_nondecreasing=row['k2chi_nondecreasing'],
                            stieltjes_signs_hold=bool(nviol == 0 and row['chi_nonincreasing']
                                                      and row['k2chi_nondecreasing'])))
    findings['es_stieltjes'] = st_rows
    e = max(rel(es_chi_complex(k*k, s).real, -1/(k*k*closed_potential(k, 1.0, s, 1.0)['T1']))
            for s in (0.1, 1.0) for k in (0.3, 1.0, 3.0))
    check('es_complex_formula_matches_real', e < 1e-9, max_relative_difference=e)
    check('es_not_stieltjes_up_to_quarter',
          all(not r['stieltjes_signs_hold'] for r in st_rows if r['sigma'] <= 0.25),
          note='proved for nu_s <= nu/4: K <= 0 excludes a Stieltjes function; this checks the sampled signs agree')

    # 8. three-rate family: sign of T_1 (finite-rank solve; closed form compared)
    sc = cfg['three_rate_scan']
    ks3 = np.logspace(sc['k_log10_range'][0], sc['k_log10_range'][1], sc['k_points'])
    scan, worst3, th3_ok = [], 0.0, True
    switch = sc['galerkin_below_k_over_nu']
    worst_overlap, worst_refine = 0.0, 0.0
    for nu in sc['nu_over_nus']:
        for nuq in sc['nuq_over_nus']:
            L4 = relaxation(4, nu, 1.0, nuq)
            Lg = {d: relaxation(d, nu, 1.0, nuq) for d in degs}
            kap = 5/(2*nuq)
            Kth = 8/(15*nuq)+16/(5*nuq*nu)
            T1, tau, n9, dpt, thb = [], [], [], [], True
            for k in ks3:
                # The finite-rank system is conditioned like (nu/k)^2, the Galerkin
                # solve converges geometrically in k/nu: use each where it is accurate.
                if k/nu < switch:
                    fr = galerkin_response(Lg[dmax], dmax, k)
                    lo_ = galerkin_response(Lg[min(degs)], min(degs), k)
                    worst_refine = max(worst_refine, max(rel(fr[q], lo_[q]) for q in ('n1', 'Mpq', 'Mqq')),
                                       abs(fr['T1']-lo_['T1'])/fr['n1'])
                else:
                    fr = finite_rank_response(L4, nu, k)
                    cl = closed_potential(k, nu, 1.0, nuq)
                    worst3 = max(worst3, abs(cl['T1']-fr['T1'])/fr['n1'], rel(cl['n1'], fr['n1']),
                                 fr['residuals']*k*k)
                    if k/nu < 2*switch:
                        ga = galerkin_response(Lg[dmax], dmax, k)
                        worst_overlap = max(worst_overlap, max(rel(fr[q], ga[q]) for q in ('n1', 'Mpq', 'Mqq')),
                                            abs(fr['T1']-ga['T1'])/fr['n1'])
                T1.append(fr['T1']); tau.append(fr['Tperp']/fr['n1'])
                n9.append(4*(fr['Mpp']-2*fr['Mpq']+fr['Mqq'])/(9*fr['Mpp']))
                cth = 9/(k*k*(fr['Mpp']+4*fr['Mpq']+4*fr['Mqq']))
                thb &= bool(cth <= kap*(1+1e-9) and cth >= kap/(1+Kth*k*k)*(1-1e-9))
                dpt.append(2*fr['Mqq']-fr['Mpp']-fr['Mpq'])
            T1, tau, n9, dpt = map(np.array, (T1, tau, n9, dpt))
            th3_ok &= thb
            neg = ks3[T1 >= 0]
            pos_a = ks3[tau > 0]
            a2bad = ks3[(T1 < 0) & (dpt < 0)]
            scan.append(dict(
                nu=nu, nu_s=1.0, nu_q=nuq, K_pot=4/(5*nuq)*(4/nu-1),
                max_T1=float(T1.max()), k_at_max_T1=float(ks3[int(np.argmax(T1))]),
                chi_pot_negative=bool(len(neg) > 0),
                k_range_chi_pot_negative=[float(neg.min()), float(neg.max())] if len(neg) else None,
                grad_limit_sign_change_k=float(np.sqrt(5*nuq/4)),
                max_Tperp_over_n1=float(tau.max()), min_Tperp_over_n1=float(tau.min()),
                k_range_Tperp_positive=[float(pos_a.min()), float(pos_a.max())] if len(pos_a) else None,
                max_Ntheta_over_9n1=float(n9.max()),
                k_range_chi_th_above_positive_chi_pot=[float(a2bad.min()), float(a2bad.max())] if len(a2bad) else None,
                thermal_bounds_hold=thb))
    findings['three_rate_scan'] = dict(k_grid=[float(ks3[0]), float(ks3[-1]), len(ks3)], rows=scan)
    check('three_rate_closed_vs_finite_rank', worst3 < 1e-7, max_difference=worst3,
          note=f'compared where k/nu >= {switch}; the closed form cancels digits at smaller k/nu')
    check('three_rate_galerkin_overlap', worst_overlap < 1e-8 and worst_refine < 1e-8,
          finite_rank_vs_galerkin_in_overlap=worst_overlap,
          galerkin_degree_difference_below_switch=worst_refine,
          note=f'Galerkin (degree {dmax}) is used for k/nu < {switch}; overlap is {switch} <= k/nu < {2*switch}')
    check('three_rate_thermal_bounds_cor_7_3', th3_ok)

    # threshold in nu/nu_s for a sign change (closed form, numerical)
    def max_T1(nu, nuq):
        f = lambda lk: -closed_potential(np.exp(lk), nu, 1.0, nuq)['T1']
        best = min((minimize_scalar(f, bounds=(lk0, lk0+1.0), method='bounded',
                                    options=dict(xatol=1e-10))
                    for lk0 in np.arange(-2.0, 4.0, 1.0)), key=lambda r: r.fun)
        return -best.fun, float(np.exp(best.x))
    thr = []
    for nuq in sc['nuq_over_nus']:
        try:
            if max_T1(2000.0, nuq)[0] <= 0 or max_T1(1.0001, nuq)[0] >= 0:
                raise ValueError('no sign change of max_k T_1 between nu = 1.0001 and 2000')
            nu0 = brentq(lambda nu: max_T1(nu, nuq)[0], 1.0001, 2000.0, xtol=1e-9)
            thr.append(dict(nu_q=nuq, nu_threshold=float(nu0), k_at_threshold=max_T1(nu0, nuq)[1]))
        except Exception as exc:                      # reported, never dropped
            thr.append(dict(nu_q=nuq, error=repr(exc)))
            nonconverged.append(dict(what='three_rate_threshold', nu_q=nuq, error=repr(exc)))
    findings['three_rate_threshold_nu_over_nus'] = thr

    # 9. the proved bound |T_1 - T_G| <= (4/5)(sqrt(3/5)|k|/nu_s + sqrt 2) sqrt(n_1/nu)
    ex = cfg['rigorous_example']
    bound_rows = []
    for nu in (ex['nu'], 10*ex['nu'], 100*ex['nu']):
        nus, nuq, k = ex['nu_s'], ex['nu_q'], ex['k']
        fr = finite_rank_response(relaxation(4, nu, nus, nuq), nu, k)
        TG = 8/(25*nus)-2*nuq/(5*k*k)
        n1_upper = 2*nuq/(5*k*k)+12/(25*nus)+32/(25*nu)
        pref = 0.8*(np.sqrt(0.6)*k/nus+np.sqrt(2))
        bound_rows.append(dict(nu=nu, nu_s=nus, nu_q=nuq, k=k, T1=fr['T1'], T_grad=TG, n1=fr['n1'],
                               n1_upper=n1_upper, bound_with_n1=pref*np.sqrt(fr['n1']/nu),
                               bound_a_priori=pref*np.sqrt(n1_upper/nu),
                               T1_lower_a_priori=TG-pref*np.sqrt(n1_upper/nu),
                               chi_pot=-1/(k*k*fr['T1'])))
    check('rigorous_bound_holds',
          all(abs(r['T1']-r['T_grad']) <= r['bound_with_n1'] <= r['bound_a_priori']*(1+1e-12)
              and r['n1'] <= r['n1_upper'] for r in bound_rows), rows=bound_rows)
    check('rigorous_example_certifies_negative_chi_pot',
          bound_rows[0]['T1_lower_a_priori'] > 0 and bound_rows[0]['T1'] > 0, row=bound_rows[0])
    gal = []
    for d in degs:
        ga = galerkin_response(relaxation(d, ex['nu'], ex['nu_s'], ex['nu_q']), d, ex['k'])
        gal.append(dict(degree=d, T1=ga['T1'], n1=ga['n1'], difference_T1=abs(ga['T1']-bound_rows[0]['T1'])))
    findings['rigorous_example_galerkin'] = gal

    # 10. A2: chi_pot >= chi_th
    #  BGK/ES inequality 2c(1-c) - D = 2 s^2 Var[1/(s+t)], s = 1/a
    alo, ahi = cfg['bgk_inequality_a_log10_range']
    worst_id, min_margin = 0.0, np.inf
    for a in np.logspace(alo, ahi, cfg['bgk_inequality_points']):
        c, dl, D = c_delta_D(a)
        s = 1/a
        kw = dict(epsabs=0, epsrel=1e-13, limit=400,
                  points=sorted({min(np.sqrt(s), 6.0), min(10*np.sqrt(s), 8.0), 1.0, 3.0}))
        G1 = 2*quad(lambda v: GAUSS*np.exp(-v*v/2)/(s+v*v), 0, 12, **kw)[0]
        G2 = 2*quad(lambda v: GAUSS*np.exp(-v*v/2)/(s+v*v)**2, 0, 12, **kw)[0]
        lhs, rhs = (dl*(1+2*a*c)-a*c), 2*s*(G2-G1*G1)
        scale = a*c
        worst_id = max(worst_id, abs(lhs-rhs)/scale)
        min_margin = min(min_margin, rhs/scale)
    check('bgk_variance_identity', worst_id < 1e-7 and min_margin > 0,
          max_identity_error_relative_to_ac=worst_id, min_margin_relative_to_ac=float(min_margin),
          note='margin is small at small a, where it is 4 a^2 (1 + O(a)) relative to a c')
    #  Dougherty: closed forms of M and the sign of 2 S_1 - S_0
    drows, worst_d, dok = [], 0.0, True
    for k in cfg['dougherty_k']:
        a = k*k
        Ea = lambda s: np.exp(a*(s+np.log1p(-s)))
        I = lambda f: quad(f, 0, 1, epsabs=0, epsrel=1e-13, limit=400)[0]
        S0, S1 = I(Ea), I(lambda s: (1-s)*Ea(s))
        Z = 3-S0-4*S1
        Mc = dict(Mpp=S0*(3-4*S1)/Z, Mpq=2*S0*S1/Z, Mqq=S1*(3-S0)/Z)
        row = dict(k=k, two_S1_minus_S0=2*S1-S0, closed=Mc, galerkin_vs_closed={})
        p, t = chis(Mc, k)
        row.update(chi_pot=p, chi_th=t)
        dok &= bool(2*S1-S0 > 0 and p > t)
        for d in degs:
            ga = galerkin_response(dougherty(d), d, k)
            dg = max(rel(ga[q], Mc[q]) for q in Mc)
            row['galerkin_vs_closed'][str(d)] = dg
            if d == dmax and dg > 1e-6:
                nonconverged.append(dict(what='dougherty_galerkin_vs_closed', k=k, degree=d,
                                         relative_difference=dg))
        worst_d = max(worst_d, min(row['galerkin_vs_closed'].values()) if k <= 1 else 0.0)
        drows.append(row)
    check('dougherty_matrix_closed_form_and_ordering', dok and worst_d < 1e-6,
          max_galerkin_difference_k_le_1=worst_d, rows=drows)
    #  Landau (cached Galerkin matrices)
    lrows = []
    for d in cfg['landau_degrees']:
        L = np.load(SHARED/'cache'/f'landau_d{d}.npy')
        for k in cfg['landau_k']:
            ga = galerkin_response(L, d, k)
            p, t = chis(ga, k)
            lrows.append(dict(degree=d, k=k, Mpp=ga['Mpp'], Mpq=ga['Mpq'], Mqq=ga['Mqq'],
                              chi_pot=p, chi_th=t, two_Mqq_minus_Mpp_minus_Mpq=2*ga['Mqq']-ga['Mpp']-ga['Mpq'],
                              Mqq_ge_Mpp_ge_Mpq=bool(ga['Mqq'] >= ga['Mpp'] >= ga['Mpq'])))
    findings['landau_comparison'] = dict(
        rows=lrows, chi_pot_ge_chi_th_all=bool(all(r['chi_pot'] >= r['chi_th'] for r in lrows)),
        Mqq_ge_Mpp_ge_Mpq_all=bool(all(r['Mqq_ge_Mpp_ge_Mpq'] for r in lrows)),
        note='finite-degree Galerkin observation; degree differences are diagnostics')
    #  an operator with K_th < K_pot: coupled l = 2 modes
    od = cfg['offdiagonal_example']
    blk = _block(cfg)
    Binv = np.linalg.inv(blk)
    kap = 5/(2*od['nu'])
    pred = kap/3*(1.6*Binv[0, 0]+0.8*np.sqrt(14)*Binv[0, 1])
    L4 = relaxation(4, od['nu'], block=blk)
    orow = [r for r in uni if r['operator'] == 'offdiagonal' and r['degree'] == max(cfg['landau_degrees'])][0]
    okrows = []
    for k in od['k']:
        fr = finite_rank_response(L4, od['nu'], k)
        p, t = chis(fr, k)
        ga = {str(d): rel(galerkin_response(relaxation(d, od['nu'], block=blk), d, k)['Mqq'], fr['Mqq'])
              for d in degs}
        okrows.append(dict(k=k, chi_pot_over_kappa=p/kap, chi_th_over_kappa=t/kap,
                           difference_over_kappa_k2=(p-t)/(kap*k*k), Tperp_over_n1=fr['Tperp']/fr['n1'],
                           residuals=fr['residuals'], galerkin_vs_finite_rank_Mqq=ga))
    findings['offdiagonal_example'] = dict(
        block=blk.tolist(), block_eigenvalues=np.linalg.eigvalsh(blk).tolist(),
        K_th_minus_K_pot_formula=float(pred), K_th_minus_K_pot_galerkin=orow['K_th_minus_K_pot'],
        K_pot=orow['K_pot'], K_th=orow['K_th'], rows=okrows)
    check('offdiagonal_K_difference_formula', abs(pred-orow['K_th_minus_K_pot']) < 1e-8,
          formula=float(pred), galerkin=orow['K_th_minus_K_pot'])
    check('offdiagonal_chi_th_exceeds_chi_pot_at_small_k',
          pred < 0 and all(r['chi_th_over_kappa'] > r['chi_pot_over_kappa'] > 0
                           for r in okrows if r['k'] <= 0.2), rows=okrows)

    metrics = dict(
        schema_version=cfg['schema_version'], config=cfg,
        status='complete' if not failures else 'complete_with_failures',
        failures=failures, nonconverged=nonconverged, checks=checks, findings=findings,
        quadrature_warnings=dict(count=len(caught), distinct=sorted(set(caught))),
        uncertainty=dict(ensemble_estimation='none: deterministic',
                         discretization='closed forms and the finite-rank system use adaptive quadrature '
                                        '(requested relative tolerance 1e-12 to 1e-13; roundoff warnings are counted in quadrature_warnings); Galerkin degree differences are '
                                        'diagnostics, not certified bounds',
                         learned_model='none'),
        script_sha256=sha(__file__),
        input_hashes={'config_counterexample.json': sha(HERE/'config_counterexample.json'),
                      'closure3d.py': sha(SHARED/'closure3d.py'),
                      'landau3d.py': sha(SHARED/'landau3d.py'), **hashes},
        environment=dict(python=platform.python_version(), numpy=np.__version__,
                         scipy=scipy.__version__, platform=platform.platform()),
        runtime_seconds=time.time()-start)
    out.mkdir(parents=True)
    (out/'metrics.json').write_text(json.dumps(metrics, indent=1, default=float)+'\n')
    print(json.dumps(dict(status=metrics['status'], failures=failures,
                          nonconverged=len(nonconverged), quadrature_warnings=len(caught),
                          checks={k: v['passed'] for k, v in checks.items()},
                          runtime=metrics['runtime_seconds']), indent=1))


def _block(cfg):
    od = cfg['offdiagonal_example']
    return np.array([[od['b0'], od['beta']], [od['beta'], od['b1']]])


if __name__ == '__main__':
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    main(sys.argv[1])
