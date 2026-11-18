"""Thermally driven heat-flux response with electron-ion collisions.

Units: v_t = sqrt(T/m) = 1 and the like-particle (electron-electron) Landau
time tau_ee = 1, as in shared/scripts/landau_closure/landau3d.py.  The
Braginskii electron time is tau_e = tau_ee/(sqrt(2) Z).  Basis functions
psi_n(v_x) L_m(v_perp^2/2) are orthonormal in L^2(Maxwellian), so coefficient
dot products are Maxwellian averages.
"""
from pathlib import Path
import sys
import numpy as np
from numpy.polynomial.laguerre import laggauss
from numpy.polynomial.legendre import leggauss
from scipy.integrate import quad
from scipy.linalg import expm

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'shared/scripts/landau_closure'))
from landau3d import basis, grads, landau_matrix  # noqa: E402,F401
from closure3d import vecs, dougherty, pinv_on_complement, theta  # noqa: E402,F401


def tau_e(Z):
    """Braginskii electron collision time in units of tau_ee."""
    return 1/(np.sqrt(2)*Z)


def lorentz_matrix(d):
    """Maxwellian average of grad f . U(v) grad h, U = (|v|^2 I - v v^T)/|v|^3.

    The integrand is a polynomial in t = |v|^2/2 and in the direction of v
    after the factor 1/|v| is absorbed in the measure, so the quadrature is
    exact in exact arithmetic.  Returns the matrix and the check E[1/|v|].
    """
    B = basis(d)
    nt, nc, nph = d//2+2, d+3, 2*d+6
    t, wt = laggauss(nt)
    c, wc = leggauss(nc)
    ph = 2*np.pi*np.arange(nph)/nph
    T_, C_, P_ = np.meshgrid(t, c, ph, indexing='ij')
    r = np.sqrt(2*T_).ravel()
    st = np.sqrt(1-C_**2).ravel()
    uh = np.stack([C_.ravel(), st*np.cos(P_.ravel()), st*np.sin(P_.ravel())], 1)
    w = (wt[:, None, None]*wc[None, :, None]*np.ones(nph)[None, None, :]).ravel()
    w = w*(2*np.pi/nph)/(2*np.pi)**1.5
    G = grads(B, r[:, None]*uh)
    G = G-np.einsum('bpi,pi->bp', G, uh)[:, :, None]*uh[None]
    return np.tensordot(G*w[None, :, None], G, axes=([1, 2], [1, 2])), float(w.sum())


def electron_operator(Lee, M, Z):
    """Electron-electron Landau plus Lorentz scattering on immobile ions.

    Lambda_ei = (3 sqrt(pi) Z / 2) |v|^-3 L^2, so that a drifting Maxwellian
    loses momentum at the rate 1/tau_e = sqrt(2) Z.
    """
    return Lee+1.5*np.sqrt(np.pi)*Z*M


def transport(L, d, conserving):
    """Local constants of the thermal response.

    kappa is the conductivity at zero current: <Q, L^+ Q> if momentum is
    conserved, and the Schur complement L22 - L12^2/L11 otherwise.
    K = kappa*C is the leading deficit coefficient.
    """
    B, ix, one, vx, E2, th, Q, Vx = vecs(d)
    H = [one, vx, E2] if conserving else [one, E2]
    Lp = pinv_on_complement(L, H)
    S = E2/3
    if conserving:
        L11 = L12 = None
        J = Q
    else:
        L11 = float(vx@Lp@vx)
        L12 = float(vx@Lp@Q)
        J = Q-L12/L11*vx
    Xi = Lp@J
    kappa = float(Q@Xi)
    b = S-Vx@Xi/kappa
    C = float(b@Lp@b)
    return dict(kappa=kappa, L11=L11, L12=L12, L22=float(Q@Lp@Q), C=C, K=kappa*C,
                source_residual=float(max(abs(b@one), abs(b@E2))),
                current_residual=float(abs(vx@Xi)),
                kernel_residual=float(max(np.abs(L@h).max() for h in H)),
                min_eigenvalue=float(np.linalg.eigvalsh(L).min()),
                asymmetry=float(np.abs(L-L.T).max()))


def thermal_response(L, d, k):
    """Solve (i k v_x + L) g = zeta, zeta = (|v|^2-3)/3; chi = 1/(k^2 <zeta g>)."""
    B, ix, one, vx, E2, th, Q, Vx = vecs(d)
    S = E2/3
    g = np.linalg.solve(1j*k*Vx+L, S.astype(complex))
    T1 = S@g
    return dict(chi=float(1/(k*k*T1.real)), T1=float(T1.real),
                T1_imag=float(abs(T1.imag)),
                flux_residual=float(abs(Q@g-1/(1j*k))),
                current_residual=float(abs(vx@g)))


def anisotropic_matrix(L, d, k):
    """M_ij = <a_i, A^-1 a_j> for a_par = v_x^2-1, a_perp = v_perp^2/2-1."""
    B, ix, one, vx, E2, th, Q, Vx = vecs(d)
    apar = np.zeros(len(B)); apar[ix[(2, 0)]] = np.sqrt(2)
    aperp = np.zeros(len(B)); aperp[ix[(0, 1)]] = -1.0
    a = np.stack([apar, aperp], 1)
    g = np.linalg.solve(1j*k*Vx+L, a.astype(complex))
    return (a.T@g).real


def responses_from_matrix(M, k):
    """Potential-driven and thermally driven conductivities from the 2x2 matrix."""
    return (3/(k*k*(M[0, 0]+2*M[0, 1])),
            9/(k*k*(M[0, 0]+4*M[0, 1]+4*M[1, 1])))


def _dougherty_integral(k, p, tol):
    """int_0^1 p(s) exp(k^2 [s + log(1-s)]) ds, up to a common scale factor."""
    scale = max(1.0, k)
    end = min(scale, 14.0)

    def f(t):
        s = t/scale
        return 0.0 if s >= 1 else np.exp(k*k*(s+np.log1p(-s)))*p(s)
    return quad(f, 0, end, epsabs=0, epsrel=tol, limit=400)[0]


def dougherty_thermal_theta(k, tol=2e-11):
    """Exact thermally driven Dougherty coefficient theta = |k| chi, nu = 1, d = 3.

    theta = 3 k int s(3-2s) E / int (5-4s) E, E = exp(k^2 [s + log(1-s)]).
    The integration variable is rescaled to resolve the layer at s = 0.
    """
    k = abs(float(k))
    return (3*k*_dougherty_integral(k, lambda s: s*(3-2*s), tol)
            / _dougherty_integral(k, lambda s: 5-4*s, tol))


def dougherty_potential_theta(k, tol=2e-11):
    """Potential-driven coefficient of the manuscript, d = 3: k int s(3-2s) E / int E."""
    k = abs(float(k))
    return (k*_dougherty_integral(k, lambda s: s*(3-2*s), tol)
            / _dougherty_integral(k, lambda s: 1.0, tol))


def zero_current_generator(L, d, k):
    """Generator of the quasi-neutral kinetic model: -P (i k v_x + L) P, P = 1 - |v_x><v_x|.

    The force a(t) v_x that P removes is the ambipolar field holding the
    current at zero; density then stays constant.
    """
    B, ix, one, vx, E2, th, Q, Vx = vecs(d)
    P = np.eye(len(B))-np.outer(vx, vx)
    return -P@(1j*k*Vx+L)@P


def zero_current_rollout(L, d, k, times):
    """Decay of h(0) = (|v|^2-3)/2, i.e. T(0) = 1, n = u = 0. times must be uniform."""
    B, ix, one, vx, E2, th, Q, Vx = vecs(d)
    G = zero_current_generator(L, d, k)
    step = expm(G*(times[1]-times[0]))
    h = (E2/2).astype(complex)
    out = np.empty((len(times), 4), dtype=complex)
    energy = np.empty(len(times))
    for i in range(len(times)):
        out[i] = (E2@h/3, one@h, vx@h, Q@h)
        energy[i] = np.sum(abs(h)**2)/2
        h = step@h
    return dict(T=out[:, 0], n=out[:, 1], u=out[:, 2], q=out[:, 3], energy=energy)


def slowest_mode_chi(L, d, k):
    """Conductivity read off the least-damped mode that carries temperature.

    If T decays like exp(-gamma t) then (3/2) gamma = k^2 chi.  Modes with
    negligible temperature content and the constrained null directions are
    excluded.
    """
    B, ix, one, vx, E2, th, Q, Vx = vecs(d)
    vals, vecs_r = np.linalg.eig(-zero_current_generator(L, d, k))
    weight = np.abs((E2/3)@vecs_r)/np.linalg.norm(vecs_r, axis=0)
    ok = (weight > 1e-6) & (vals.real > 1e-12)
    gamma = vals[ok][np.argmin(vals[ok].real)]
    return float(1.5*gamma.real/(k*k)), float(abs(gamma.imag))


def temperature_decay(k, chi, times):
    """Closed model (3/2) dT/dt = -k^2 chi T."""
    return np.exp(-(2/3)*k*k*chi*times)


def relative_history_error(candidate, reference, times):
    num = np.trapezoid(abs(candidate-reference)**2, times)
    return float(np.sqrt(num/np.trapezoid(abs(reference)**2, times)))
