"""Frequency-dependent (memory) closure and transfer bounds for the embedded tests.

With P the L^2(M) projection on the retained moments and Y the orthogonal
complement of span{1, v_x, |v|^2}, the compressed operator is
B_k = Qc (i k v_x + Lambda) Qc on Y and

    chi(k, s) = <Q, (B_k + s)^{-1} Q>,      s = -i omega,

is the exact frequency-dependent conductivity: q^ = -i k chi(k, s) T^ for
data in the range of P (1D, and 3D with zero flow).  In 3D with flow the
kernel is the 2x2 matrix of <b_i, (B_k + s)^{-1} b_j>, b = (Q, sigma),
sigma = v_x^2 - |v|^2/3.

This script checks, in Galerkin truncations,
  - the 1D BGK kernel against the closed form eq. (bgkfrequency);
  - the memory identities against the kinetic resolvent, in frequency space
    and (electrons) against the saved kinetic trajectory;
  - Re chi >= 0 on the imaginary axis, and positivity of the Hermitian part
    of the 3D matrix kernel;
  - the static contractions chi_th = K_qq, chi_pot = K_qq/(1 - i k K_qs);
and evaluates the transfer bounds of the manuscript fragment next to the
errors saved by the two embedded tests.

  python3 frequency_response.py results/<new-dir>      # refuses to overwrite

Galerkin degree differences are diagnostics, not error bars.
"""
import hashlib
import json
import platform
import sys
import time
from pathlib import Path

import numpy as np
import scipy
from scipy.linalg import expm, null_space, solve_banded, solve_continuous_lyapunov
from scipy.optimize import minimize_scalar
from scipy.special import wofz

HERE = Path(__file__).resolve().parent
SHARED = HERE.parents[1] / 'scripts' / 'landau_closure'
ELECTRON = HERE.parent / 'electron_heat_flux_extension'
sys.path.insert(0, str(SHARED))
sys.path.insert(0, str(ELECTRON))
sys.path.insert(0, str(HERE))
from closure3d import vecs, dougherty, theta as potential_theta  # noqa: E402
import electron_numerics as en  # noqa: E402
import numerics as nm  # noqa: E402


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


# ---------------------------------------------------------------- kernels
class Kernel:
    """chi(s) = b_i . (B + s)^{-1} b_j for a dense compressed operator B."""

    def __init__(self, B, b):
        self.B = np.asarray(B, dtype=complex)
        self.b = np.atleast_2d(np.asarray(b, dtype=float).T).T      # (n, m)
        if self.b.shape[0] != len(self.B):
            self.b = self.b.T
        self.I = np.eye(len(self.B))

    def matrix(self, s):
        return self.b.T @ np.linalg.solve(self.B + s*self.I, self.b.astype(complex))

    def __call__(self, s):
        return self.matrix(s)[0, 0]

    def on_axis(self, omega, chunk=256):
        """chi(-i omega) for an array of real omega (first source only)."""
        omega = np.asarray(omega, dtype=float)
        out = np.empty(len(omega), dtype=complex)
        b = self.b[:, 0].astype(complex)
        for i in range(0, len(omega), chunk):
            w = omega[i:i+chunk]
            A = self.B[None]-1j*w[:, None, None]*self.I[None]
            out[i:i+chunk] = np.linalg.solve(A, np.broadcast_to(b, (len(w), len(b)))[..., None])[..., 0] @ self.b[:, 0]
        return out


def hermite_blocks(k, degree, model='dougherty'):
    """1D operator in normalized Hermite functions, nu = 1; returns A, B, Q on Y."""
    V = np.diag(np.sqrt(np.arange(1, degree+1)), 1)
    V = V+V.T
    rates = np.arange(degree+1, dtype=float) if model == 'dougherty' else np.ones(degree+1)
    rates[:3] = 0
    A = 1j*k*V+np.diag(rates)
    Q = np.zeros(degree-2)
    Q[0] = np.sqrt(6)/2                    # Q = He_3/2, |He_3|^2 = 6
    return A, A[3:, 3:], Q


def complement(d):
    """Orthonormal basis of Y = {1, v_x, |v|^2}^perp in the 3D Galerkin space."""
    B_, ix, one, vx, E2, th, Q, Vx = vecs(d)
    Y = null_space(np.array([one, vx, E2]))
    return Y, dict(one=one, vx=vx, zeta=E2/3, Q=Q, sigma=-th/3, Vx=Vx)


# ------------------------------------------------------------ grids, sups
def tan_grid(scale, half_points):
    """omega = scale tan(phi), phi uniform on (-pi/2, pi/2), symmetric."""
    phi = np.linspace(-np.pi/2, np.pi/2, 2*half_points+1)[1:-1]
    return phi, scale*np.tan(phi)


def integral_over_omega(values, phi, scale):
    """(1/2 pi) int values d omega by the trapezoidal rule in phi, on the grid and on every other point."""
    f = values*scale/np.cos(phi)**2
    fine = np.trapezoid(f, phi)/(2*np.pi)
    coarse = np.trapezoid(f[1::2], phi[1::2])/(2*np.pi)
    return float(fine), float(abs(fine-coarse)/abs(fine)) if fine else 0.0


def sup_on_axis(fun, omega0, values0):
    """Refine the maximum of fun(omega) found on a grid; returns (sup, argsup)."""
    order = np.argsort(omega0)
    omega0, values0 = np.asarray(omega0)[order], np.asarray(values0)[order]
    i = int(np.argmax(values0))
    lo, hi = omega0[max(i-1, 0)], omega0[min(i+1, len(omega0)-1)]
    r = minimize_scalar(lambda w: -fun(w), bounds=(lo, hi), method='bounded',
                        options=dict(xatol=1e-12*max(1.0, abs(omega0[i]))))
    if -r.fun >= values0[i]:
        return float(-r.fun), float(r.x)
    return float(values0[i]), float(omega0[i])


# ---------------------------------------------------------------- BGK check
def bgk_phi(z):
    W = 1j*np.sqrt(np.pi/2)*wofz(z/np.sqrt(2))
    R = 1+z*W
    E = 1-R+z*z*R
    return z*(1-3*R+z*z*R)/(2*E)


def bgk_kernel_tridiagonal(k, s, degree):
    """chi(k, s) for constant-frequency BGK: B + s = i k Qc v Qc + (1 + s) on He_n, n >= 3."""
    n = degree-2
    off = 1j*k*np.sqrt(np.arange(4, degree+1))
    ab = np.zeros((3, n), dtype=complex)
    ab[0, 1:] = off
    ab[1] = 1+s
    ab[2, :-1] = off
    rhs = np.zeros(n, dtype=complex)
    rhs[0] = np.sqrt(6)/2
    return np.sqrt(6)/2*solve_banded((1, 1), ab, rhs)[0]


def bgk_check(cfg):
    rows = []
    for k in cfg['k']:
        for wr, wi in cfg['omega']:
            omega = wr+1j*wi
            lhs = -1j*k*bgk_kernel_tridiagonal(k, -1j*omega, cfg['degree'])
            rhs = np.sign(k)*bgk_phi((omega+1j)/abs(k))
            rows.append(dict(k=k, omega=[wr, wi], abs_difference=float(abs(lhs-rhs)),
                             value=[float(rhs.real), float(rhs.imag)]))
    return dict(rows=rows, max_abs_difference=max(r['abs_difference'] for r in rows))


# -------------------------------------------------------- 1D sound-wave test
def sound_case(k, degree, cfg, saved, tol):
    A, B, Q = hermite_blocks(k, degree)
    n = degree+1
    ker = Kernel(B, Q)
    chi0c = ker(0)
    chi0 = float(chi0c.real)
    y0 = np.linalg.solve(B, Q.astype(complex))
    chi0_tau = float((y0@y0).real)                    # -d chi/ds at 0
    lam = float(np.linalg.eigvalsh((B+B.conj().T).real/2).min())
    tau_gap = float(np.sqrt(Q@Q)*np.linalg.norm(y0)/(lam*chi0))
    M0 = np.array([[0, 1j*k, 0], [1j*k, 0, 1j*k], [0, 2j*k, 2*k*k*chi0]])
    U0 = np.array([0, 0, 1.0])
    C = np.zeros((3, n))
    C[0, 0] = C[1, 1] = 1
    C[2, 2] = np.sqrt(2)
    h0 = np.zeros(n, dtype=complex)
    h0[2] = 1/np.sqrt(2)
    qrow = np.zeros(n)
    qrow[3] = np.sqrt(6)/2
    I3, In = np.eye(3), np.eye(n)
    out = dict(k=k, degree=degree, chi0=chi0, chi0_imag=float(abs(chi0c.imag)),
               chi0_minus_galerkin_static=float(chi0-nm.hermite_response(k, degree)/k),
               chi0_minus_closed_form=float(chi0-nm.dougherty_theta(k)/k),
               memory_time=chi0_tau/chi0, collision_gap_on_complement=lam, tau_gap=tau_gap)

    # memory identities at Laplace samples: free decay and forcing a(t) v
    ident = 0.0
    for sr, si in cfg['laplace_samples']:
        s = sr+1j*si
        c = ker(s)
        Ms = M0.copy()
        Ms[2, 2] = 2*k*k*c
        hk = np.linalg.solve(A+s*In, h0)
        Uk = C@hk
        Um = np.linalg.solve(Ms+s*I3, U0)
        ident = max(ident, np.abs(Uk-Um).max()/np.abs(Uk).max(),
                    abs(qrow@hk+1j*k*c*Uk[2])/abs(qrow@hk))
        hf = np.linalg.solve(A+s*In, np.eye(n)[1].astype(complex))       # source v
        Uf = C@hf
        ident = max(ident, abs(qrow@hf+1j*k*c*Uf[2])/abs(qrow@hf),
                    np.abs(Uf-np.linalg.solve(Ms+s*I3, np.array([0, 1.0, 0]))).max()/np.abs(Uf).max(),
                    abs(ker(np.conj(s))-np.conj(c))/abs(c))
    out['memory_identity_max_relative_residual'] = float(ident)

    # frequency grid: positivity and the multipliers of the transfer bound
    fg = cfg['frequency_grid']
    phi, om = tan_grid(abs(k), fg['half_points'])
    logw = abs(k)*np.logspace(*fg['log_decades'], fg['log_points'])
    om_all = np.concatenate([om, -logw, logw])
    chi_all = ker.on_axis(om_all)
    out['min_real_chi_on_axis'] = float(chi_all.real.min())

    def resolvent(w):
        return np.linalg.inv(M0-1j*w*I3)

    Rall = np.linalg.inv(M0[None]-1j*om_all[:, None, None]*I3[None])
    dgam = 2*k*k*np.abs(chi_all-chi0)
    rnorm = np.linalg.norm(Rall[:, :, 2], axis=1)
    out['eta_U'], out['eta_U_argsup_over_k'] = sup_on_axis(
        lambda w: 2*k*k*abs(ker(-1j*w)-chi0)*np.linalg.norm(resolvent(w)[:, 2]), om_all, dgam*rnorm)
    out['eta_U_argsup_over_k'] /= k
    out['eta_T'], _ = sup_on_axis(
        lambda w: 2*k*k*abs(ker(-1j*w)-chi0)*abs(resolvent(w)[2, 2]), om_all, dgam*np.abs(Rall[:, 2, 2]))
    out['Omega'], _ = sup_on_axis(
        lambda w: 2*k*k*chi0*abs(w)*np.linalg.norm(resolvent(w)[:, 2]), om_all,
        2*k*k*chi0*np.abs(om_all)*rnorm)

    # exact L^2(0, infinity) norms from a Lyapunov equation for kinetic (+) closed
    G = np.zeros((n+3, n+3), dtype=complex)
    G[:n, :n] = A
    G[n:, n:] = M0
    x0 = np.concatenate([h0, U0])
    X = solve_continuous_lyapunov(G, np.outer(x0, x0.conj()))
    Ck = np.hstack([C, np.zeros((3, 3))])
    Cc = np.hstack([np.zeros((3, n)), I3])
    norm2 = lambda Cm: float(np.trace(Cm@X@Cm.conj().T).real)
    nk, nc, ne, nT = norm2(Ck), norm2(Cc), norm2(Ck-Cc), norm2(Ck[2:3])
    out.update(kinetic_norm_squared=nk, closed_norm_squared=nc, kinetic_T_norm_squared=nT,
               error_infinite_window=float(np.sqrt(ne/nk)),
               lyapunov_residual=float(np.abs(G@X+X@G.conj().T-np.outer(x0, x0.conj())).max()))

    # Plancherel: the same error from the exact frequency-space identity
    m = len(om)
    chi_g, R_g = chi_all[:m], Rall[:m]
    Tc_hat = R_g[:, 2, 2]                                    # e_T . (M0 - i w)^{-1} U0
    Tk_hat = Tc_hat/(1+2*k*k*(chi_g-chi0)*R_g[:, 2, 2])
    w2 = (2*k*k*np.abs(chi_g-chi0))**2*np.linalg.norm(R_g[:, :, 2], axis=1)**2
    ne_freq, q1 = integral_over_omega(w2*np.abs(Tk_hat)**2, phi, abs(k))
    W2, q2 = integral_over_omega(w2*np.abs(Tc_hat)**2, phi, abs(k))
    out.update(plancherel_relative_mismatch=float(abs(ne_freq-ne)/ne),
               quadrature_refinement=max(q1, q2), W_squared=W2)

    # the bounds, all relative to the kinetic norm on (0, infinity)
    out['bound_sup'] = out['eta_U']*np.sqrt(nT/nk)                  # part (i)
    out['bound_sup_crude'] = out['eta_U']
    out['bound_weighted'] = (float(np.sqrt(W2/nk)/(1-out['eta_T']))
                             if out['eta_T'] < 1 else None)          # part (ii)
    out['bound_memory_time'] = out['Omega']*tau_gap
    out['Omega_times_memory_time'] = out['Omega']*out['memory_time']

    # the finite-window error of the saved test, recomputed with the paper's functions
    times = np.linspace(0, cfg['sound']['scaled_final_time']/k, cfg['sound']['samples'])
    ref = nm.kinetic_rollout(k, degree, times)[0]
    mod = nm.moment_rollout(k, chi0, times)[0]
    out['error_finite_window_recomputed'] = nm.relative_history_error(mod, ref, times)
    out['finite_window_kinetic_norm_fraction'] = float(
        np.trapezoid(np.sum(abs(ref)**2, axis=1), times)/nk)
    item = [x for x in saved if abs(x['k']-k) < 1e-12][0]
    out['error_saved'] = item['models']['quasistatic']['relative_history_error']
    out['saved_T_max_abs_difference'] = float(np.abs(ref[:, 2].real-np.array(item['kinetic_T'])).max())
    return out


# --------------------------------------------------- quasi-neutral electrons
def electron_case(Z, kl, d, Lee, Mei, cfg, saved):
    L = en.electron_operator(Lee, Mei, Z)
    te = en.tau_e(Z)
    k = kl/te
    Y, v = complement(d)
    nb = len(L)
    B = Y.T@(1j*k*v['Vx']+L)@Y
    Qy = Y.T@v['Q']
    ker = Kernel(B, Qy)
    chi0c = ker(0)
    chi0 = float(chi0c.real)
    gamma0 = 2/3*k*k*chi0
    y0 = np.linalg.solve(B, Qy.astype(complex))
    lam = float(np.linalg.eigvalsh(Y.T@L@Y).min())
    out = dict(Z=Z, k_lambda=kl, k=k, degree=d, chi0=chi0, chi0_imag=float(abs(chi0c.imag)),
               chi0_minus_thermal_response=float(chi0-en.thermal_response(L, d, k)['chi']),
               gamma0=gamma0, decay_time_over_tau_e=1/gamma0/te,
               memory_time_over_tau_e=float((y0@y0).real/chi0/te),
               gamma0_memory_time=float(gamma0*(y0@y0).real/chi0),
               galerkin_collision_gap_on_complement=lam,
               tau_gap_over_tau_e=float(np.sqrt(Qy@Qy)*np.linalg.norm(y0)/(lam*chi0)/te),
               projection_residual=float(max(
                   np.abs(Y.T@(v['Vx']@v['zeta'])-2/3*Qy).max(),
                   abs(np.linalg.norm(Qy)**2-2.5))))
    out['bound_memory_time'] = gamma0*out['tau_gap_over_tau_e']*te

    # memory identity against the resolvent of the paper's zero-current generator
    G = en.zero_current_generator(L, d, k)                     # dh/dt = G h
    h0 = (1.5*v['zeta']).astype(complex)
    ident = 0.0
    for sr, si in cfg['laplace_samples']:
        s = (sr+1j*si)*gamma0
        c = ker(s)
        hk = np.linalg.solve(s*np.eye(nb)-G, h0)
        Tk, qk = v['zeta']@hk, v['Q']@hk
        ident = max(ident, abs(Tk-1/(s+2/3*k*k*c))/abs(Tk), abs(qk+1j*k*c*Tk)/abs(qk),
                    abs(v['one']@hk)/abs(Tk), abs(v['vx']@hk)/abs(Tk),
                    abs(ker(np.conj(s))-np.conj(c))/abs(c))
    out['memory_identity_max_relative_residual'] = float(ident)

    # reduced system x = (T, y), h_perp = -i k y:  T' = -(2/3) k^2 Q.y,  y' = -B y + Q T
    m = len(B)
    Gr = np.zeros((m+2, m+2), dtype=complex)                   # x' = -Gr x; last entry: closed model
    Gr[0, 1:m+1] = 2/3*k*k*Qy
    Gr[1:m+1, 0] = -Qy
    Gr[1:m+1, 1:m+1] = B
    Gr[m+1, m+1] = gamma0
    x0 = np.zeros(m+2, dtype=complex)
    x0[0] = x0[m+1] = 1
    X = solve_continuous_lyapunov(Gr, np.outer(x0, x0.conj()))
    nk, nc = float(X[0, 0].real), float(X[m+1, m+1].real)
    ne = float((X[0, 0]+X[m+1, m+1]-2*X[0, m+1].real).real)
    out.update(kinetic_norm_squared=nk, closed_norm_squared=nc,
               closed_norm_squared_exact=1/(2*gamma0),
               error_infinite_window=float(np.sqrt(ne/nk)),
               lyapunov_residual=float(np.abs(Gr@X+X@Gr.conj().T-np.outer(x0, x0.conj())).max()
                                       / np.abs(X).max()/np.abs(Gr).max()))

    # frequency grid
    fg = cfg['frequency_grid']
    phi, om = tan_grid(gamma0, fg['half_points'])
    logw = gamma0*np.logspace(*fg['log_decades'], fg['log_points'])
    om_all = np.concatenate([om, -logw, logw])
    chi_all = ker.on_axis(om_all)
    out['min_real_chi_on_axis'] = float(chi_all.real.min())
    mult = np.abs(chi_all-chi0)/chi0/np.sqrt(1+(om_all/gamma0)**2)
    out['eta'], w_sup = sup_on_axis(
        lambda w: abs(ker(-1j*w)-chi0)/chi0/np.sqrt(1+(w/gamma0)**2), om_all, mult)
    out['eta_argsup_over_gamma0'] = w_sup/gamma0
    n_ = len(om)
    mm = mult[:n_]**2
    Tc2 = 1/(gamma0**2+om**2)
    Tk_hat = 1/(-1j*om+2/3*k*k*chi_all[:n_])
    eta2sq, q1 = integral_over_omega(mm*Tc2, phi, gamma0)
    ne_freq, q2 = integral_over_omega(mm*np.abs(Tk_hat)**2, phi, gamma0)
    out['eta_2'] = float(np.sqrt(eta2sq*2*gamma0))               # relative to the closed norm
    out.update(plancherel_relative_mismatch=float(abs(ne_freq-ne)/ne),
               quadrature_refinement=max(q1, q2))
    out['bound_sup'] = out['eta']                                 # relative to kinetic norm
    out['bound_weighted'] = (float(out['eta_2']*np.sqrt(nc/nk)/(1-out['eta']))
                             if out['eta'] < 1 else None)

    # finite window of the saved test
    times = np.linspace(0, cfg['electron']['decay_times']/gamma0, cfg['electron']['samples'])
    step = expm(-Gr[:m+1, :m+1]*(times[1]-times[0]))
    x = x0[:m+1].copy()
    Tred = np.empty(len(times), dtype=complex)
    for i in range(len(times)):
        Tred[i] = x[0]
        x = step@x
    ref = en.zero_current_rollout(L, d, k, times)['T']
    out['reduced_vs_kinetic_rollout_max_abs'] = float(np.abs(Tred-ref).max())
    out['error_finite_window_recomputed'] = en.relative_history_error(
        en.temperature_decay(k, chi0, times), ref, times)
    out['finite_window_kinetic_norm_fraction'] = float(np.trapezoid(abs(ref)**2, times)/nk)
    item = [x_ for x_ in saved if x_['Z'] == Z and abs(x_['k_lambda']-kl) < 1e-12][0]
    out['error_saved'] = item['models']['quasistatic']['relative_history_error']
    out['saved_refinement_error'] = item['numerical_refinement_error']
    out['saved_T_max_abs_difference'] = float(np.abs(ref.real-np.array(item['kinetic_T'])).max())
    return out


# ------------------------------------------------------- 3D matrix kernel
def matrix_case(name, L, d, k, cfg):
    Y, v = complement(d)
    nb = len(L)
    A = 1j*k*v['Vx']+L
    b = np.stack([Y.T@v['Q'], Y.T@v['sigma']], 1)
    ker = Kernel(Y.T@A@Y, b)
    K0 = ker.matrix(0)
    chi_th = en.thermal_response(L, d, k)['chi']
    chi_pot = potential_theta(L, d, k)[0]/k
    out = dict(operator=name, degree=d, k=k,
               K_qq=float(K0[0, 0].real), K_ss=float(K0[1, 1].real),
               K_qs_over_i=float(K0[0, 1].imag),
               static_structure_residual=float(max(abs(K0[0, 0].imag), abs(K0[1, 1].imag),
                                                   abs(K0[0, 1].real), abs(K0[0, 1]-K0[1, 0]))),
               chi_th=chi_th, chi_pot=chi_pot,
               chi_th_residual=float(abs(K0[0, 0]-chi_th)/chi_th),
               chi_pot_residual=float(abs(K0[0, 0]/(1-1j*k*K0[0, 1])-chi_pot)/abs(chi_pot)),
               projection_residual=float(max(
                   np.abs(Y.T@(v['Vx']@v['zeta'])-2/3*b[:, 0]).max(),
                   np.abs(Y.T@(v['Vx']@v['vx'])-b[:, 1]).max(),
                   np.abs(Y.T@(v['Vx']@v['one'])).max())))
    h0 = (0.3*v['one']+0.5*v['vx']+1.5*v['zeta']).astype(complex)   # (n, u, T)(0) = (0.3, 0.5, 1)
    ident, herm = 0.0, np.inf
    for sr, si in cfg['laplace_samples']:
        s = sr+1j*si
        Ks = ker.matrix(s)
        hk = np.linalg.solve(A+s*np.eye(nb), h0)
        n_, u, T, q, pi = (v[x]@hk for x in ('one', 'vx', 'zeta', 'Q', 'sigma'))
        pred = -1j*k*Ks@np.array([T, u])
        ident = max(ident, abs(pred[0]-q)/abs(q), abs(pred[1]-pi)/abs(pi),
                    abs(s*n_-0.3+1j*k*u)/abs(n_), abs(s*u-0.5+1j*k*(n_+T+pi))/abs(u),
                    abs(1.5*(s*T-1)+1j*k*(u+q))/abs(T))
    for w in np.concatenate([[0.0], np.logspace(-3, 3, 61), -np.logspace(-3, 3, 61)]):
        Ks = ker.matrix(-1j*w)
        herm = min(herm, float(np.linalg.eigvalsh((Ks+Ks.conj().T)/2).min()))
    out['memory_identity_max_relative_residual'] = float(ident)
    out['min_eigenvalue_hermitian_part_on_axis'] = herm
    return out


# -------------------------------------------------------------------- main
def main(outdir):
    start = time.time()
    out = Path(outdir)
    if out.exists():
        raise SystemExit(f'refusing to overwrite existing result directory {out}')
    cfg_path = HERE/'config_frequency.json'
    cfg = json.loads(cfg_path.read_text())
    np.random.seed(cfg['seed'])            # nothing below is random
    tol = cfg['tolerances']
    failures, checks = [], {}
    hashes = {cfg_path.name: sha(cfg_path)}

    def check(name, value, ok):
        checks[name] = dict(value=value, passed=bool(ok))
        if not ok:
            failures.append(name)

    def guarded(label, fun, *args):
        try:
            return fun(*args)
        except Exception as exc:                    # reported, never dropped
            failures.append(f'{label}: {exc!r}')
            return dict(label=label, error=repr(exc))

    bgk = guarded('bgk', bgk_check, cfg['bgk'])
    if 'error' not in bgk:
        check('bgk_kernel_matches_closed_form', bgk['max_abs_difference'],
              bgk['max_abs_difference'] < cfg['bgk']['tolerance'])

    def common_checks(tag, r, eta_key):
        check(f'{tag}_memory_identity', r['memory_identity_max_relative_residual'],
              r['memory_identity_max_relative_residual'] < tol['identity'])
        check(f'{tag}_positive_real', r['min_real_chi_on_axis'],
              r['min_real_chi_on_axis'] > tol['positivity'])
        check(f'{tag}_plancherel', r['plancherel_relative_mismatch'],
              r['plancherel_relative_mismatch'] < tol['plancherel'])
        check(f'{tag}_saved_error_reproduced', abs(r['error_finite_window_recomputed']-r['error_saved']),
              abs(r['error_finite_window_recomputed']-r['error_saved']) < tol['saved_error_reproduction'])
        check(f'{tag}_sup_bound_holds', r['bound_sup']-r['error_infinite_window'],
              r['bound_sup'] >= r['error_infinite_window']-tol['bound_slack'])
        if r['bound_weighted'] is None:
            checks[f'{tag}_weighted_bound_holds'] = dict(
                value=None, passed=None, note=f'not applicable: {eta_key} >= 1')
        else:
            check(f'{tag}_weighted_bound_holds', r['bound_weighted']-r['error_infinite_window'],
                  r['bound_weighted'] >= r['error_infinite_window']-tol['bound_slack'])
        # finite window: |U - U_c|_(0,t_f) <= |U - U_c|_(0,inf), so divide by the kinetic norm fraction
        frac = np.sqrt(r['finite_window_kinetic_norm_fraction'])
        r['bound_sup_finite_window'] = r['bound_sup']/frac
        r['bound_weighted_finite_window'] = (None if r['bound_weighted'] is None
                                             else r['bound_weighted']/frac)
        r['bound_sup_finite_window_over_saved_error'] = r['bound_sup_finite_window']/r['error_saved']
        r['bound_weighted_finite_window_over_saved_error'] = (
            None if r['bound_weighted'] is None else r['bound_weighted_finite_window']/r['error_saved'])
        check(f'{tag}_finite_window_bound_holds', r['bound_sup_finite_window']-r['error_finite_window_recomputed'],
              r['bound_sup_finite_window'] >= r['error_finite_window_recomputed']-tol['bound_slack'])
        r['bound_sup_over_error'] = r['bound_sup']/r['error_infinite_window']
        r['bound_weighted_over_error'] = (None if r['bound_weighted'] is None
                                          else r['bound_weighted']/r['error_infinite_window'])

    sound = []
    sp = HERE/cfg['sound']['saved_metrics']
    hashes[str(cfg['sound']['saved_metrics'])] = sha(sp)
    saved = json.loads(sp.read_text())['embedded']
    for k in cfg['sound']['k']:
        for deg in cfg['sound']['degrees']:
            r = guarded(f'sound_k{k}_N{deg}', sound_case, k, deg, cfg, saved, tol)
            sound.append(r)
            if 'error' in r:
                continue
            tag = f'sound_k{k}_N{deg}'
            common_checks(tag, r, 'eta_T')
            check(f'{tag}_static_limit', abs(r['chi0_minus_closed_form']),
                  abs(r['chi0_minus_closed_form']) < tol['identity'])
            check(f'{tag}_memory_time_bound_holds', r['bound_memory_time']-r['eta_U'],
                  r['bound_memory_time'] >= r['eta_U']-tol['bound_slack'])
            print(f"sound k={k} N={deg}: saved {r['error_saved']:.4f} E_inf {r['error_infinite_window']:.4f} "
                  f"sup {r['bound_sup']:.4f} weighted {r['bound_weighted']} Omega*tau {r['bound_memory_time']:.4f}",
                  flush=True)

    electron = []
    ep = (HERE/cfg['electron']['saved_metrics']).resolve()
    hashes[str(cfg['electron']['saved_metrics'])] = sha(ep)
    saved_e = json.loads(ep.read_text())['embedded']
    ops = {}
    for d in sorted(set(cfg['electron']['degrees']) | set(cfg['matrix_kernel']['degrees'])):
        cache = SHARED/'cache'/f'landau_d{d}.npy'
        hashes[cache.name] = sha(cache)
        ops[d] = (np.load(cache), en.lorentz_matrix(d)[0])
    for Z in cfg['electron']['charges']:
        for kl in cfg['electron']['k_lambda']:
            for d in cfg['electron']['degrees']:
                tag = f'electron_Z{Z}_kl{kl}_D{d}'
                r = guarded(tag, electron_case, Z, kl, d, ops[d][0], ops[d][1], cfg, saved_e)
                electron.append(r)
                if 'error' in r:
                    continue
                if d != max(cfg['electron']['degrees']):
                    # the saved reference uses the highest degree; lower degrees are diagnostics
                    r['error_saved_is_for_degree'] = max(cfg['electron']['degrees'])
                    saved_err = r['error_saved']
                    r['error_saved'] = r['error_finite_window_recomputed']
                    common_checks(tag, r, 'eta')
                    r['error_saved'] = saved_err
                    del checks[f'{tag}_saved_error_reproduced']
                else:
                    common_checks(tag, r, 'eta')
                    check(f'{tag}_saved_trajectory_reproduced', r['saved_T_max_abs_difference'],
                          r['saved_T_max_abs_difference'] < tol['saved_error_reproduction'])
                check(f'{tag}_static_limit', abs(r['chi0_minus_thermal_response'])/r['chi0'],
                      abs(r['chi0_minus_thermal_response'])/r['chi0'] < tol['identity'])
                check(f'{tag}_reduced_rollout', r['reduced_vs_kinetic_rollout_max_abs'],
                      r['reduced_vs_kinetic_rollout_max_abs'] < 1e-7)
                check(f'{tag}_memory_time_bound_holds', r['bound_memory_time']-r['eta'],
                      r['bound_memory_time'] >= r['eta']-tol['bound_slack'])
                print(f"electron Z={Z} kl={kl} D={d}: saved {r['error_saved']:.4f} "
                      f"E_inf {r['error_infinite_window']:.4f} eta {r['eta']:.4f} "
                      f"weighted {r['bound_weighted']:.4f} gamma*tau_m {r['gamma0_memory_time']:+.4f}",
                      flush=True)

    matrix = []
    for name in cfg['matrix_kernel']['operators']:
        for d in cfg['matrix_kernel']['degrees']:
            L = dougherty(d) if name == 'dougherty' else ops[d][0]
            for k in cfg['matrix_kernel']['k']:
                tag = f'matrix_{name}_D{d}_k{k}'
                r = guarded(tag, matrix_case, name, L, d, k, cfg)
                matrix.append(r)
                if 'error' in r:
                    continue
                worst = max(r['memory_identity_max_relative_residual'], r['chi_th_residual'],
                            r['chi_pot_residual'], r['static_structure_residual'])
                check(f'{tag}_identities', worst, worst < tol['identity'])
                check(f'{tag}_positive_real', r['min_eigenvalue_hermitian_part_on_axis'],
                      r['min_eigenvalue_hermitian_part_on_axis'] > tol['positivity'])

    metrics = dict(schema_version=cfg['schema_version'], config=cfg,
                   status='complete' if not failures else 'complete_with_failures',
                   failures=failures, checks=checks,
                   uncertainty=('deterministic; Galerkin degree differences are diagnostics, not '
                                'error bars; suprema over frequency are taken on a grid and refined locally'),
                   bgk=bgk, sound_wave=sound, electron=electron, matrix_kernel=matrix,
                   input_hashes=hashes, script_sha256=sha(__file__),
                   environment=dict(python=platform.python_version(), numpy=np.__version__,
                                    scipy=scipy.__version__, platform=platform.platform()),
                   command=' '.join(['python3']+sys.argv),
                   runtime_seconds=time.time()-start)
    out.mkdir(parents=True)
    (out/'metrics.json').write_text(json.dumps(metrics, indent=1))
    print(json.dumps(dict(status=metrics['status'], failures=failures, checks=len(checks),
                          runtime=metrics['runtime_seconds']), indent=1))


if __name__ == '__main__':
    main(sys.argv[1])
