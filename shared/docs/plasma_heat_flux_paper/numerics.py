"""Deterministic manuscript calculations, with physical energy flux in 1D/3D."""
from pathlib import Path
import sys
import numpy as np
from scipy.integrate import quad, quad_vec
from scipy.sparse import diags
from scipy.sparse.linalg import expm_multiply

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'shared/scripts/landau_closure'))
from closure3d import constants, dougherty, theta, temperatures  # noqa: E402
from landau3d import landau_matrix  # noqa: E402

def average(fun, tol=2e-11):
    """Gaussian integral; all present scalar integrands are even."""
    return quad(lambda v: np.exp(-v*v/2)*fun(v)*np.sqrt(2/np.pi),
                0, np.inf, epsabs=1e-12, epsrel=tol, limit=400)[0]

def dougherty_theta(k, dim=1, tol=2e-11):
    """Stable exact quasi-static energy-flux coefficient, nu=1, k>0."""
    k = abs(float(k))
    scale = max(1.0, k)
    end = min(scale, 14.0)
    def integrand(t, moment=False):
        s = t/scale
        if s >= 1:
            return 0.0
        weight = np.exp(k*k*(s+np.log1p(-s)))
        p = s if dim == 1 else s*(3-2*s)
        return weight*(p if moment else 1)
    den = quad(integrand, 0, end, epsabs=0, epsrel=tol, limit=400)[0]
    num = quad(lambda t: integrand(t, True), 0, end,
               epsabs=0, epsrel=tol, limit=400)[0]
    return k*num/den

def bgk_theta(k, tol=2e-11):
    y = 1/abs(k)
    num = average(lambda v: (v**3-3*v)**2/(v*v+y*y), tol)
    den = average(lambda v: (v*v-1)**2/(v*v+y*y), tol)
    return (1+y*y)/(2*y*(3+y*y))*num/den

def bgk_constants(variable=False, tol=2e-11):
    nu = (lambda v: 1/(1+abs(v)**3)) if variable else (lambda v: 1.0)
    Q = lambda v: (v**3-3*v)/2
    kappa = average(lambda v: Q(v)**2/nu(v), tol)
    alpha = average(lambda v: v*Q(v)/nu(v), tol)
    source = lambda v: 1-v*v+v*(Q(v)/nu(v)-alpha*v)/kappa
    C = average(lambda v: source(v)**2/nu(v), tol)
    return dict(kappa=kappa, C=C, K=kappa*C)

def variable_bgk_theta(k, variable=True, tol=2e-11):
    """Independent weighted-conserving rank-three quadrature solve."""
    def pieces(v):
        H = np.array([1.0, v, v*v])
        nu = 1/(1+abs(v)**3) if variable else 1.0
        den = nu+1j*k*v
        weight = np.exp(-v*v/2)/np.sqrt(2*np.pi)
        # Form the difference analytically rather than subtracting two matrices.
        D = np.outer(H,H)*(nu*1j*k*v/den)
        b = H*nu/den
        return weight*np.concatenate((D.ravel(), b, [1/den], nu*H/den))
    vals, err = quad_vec(lambda v: pieces(v)+pieces(-v), 0, 14,
                         epsabs=1e-13, epsrel=tol, limit=400)
    p = np.linalg.solve(vals[:9].reshape(3,3), vals[9:12])
    n = vals[12]+vals[13:16]@p
    return float(1/(abs(k)*n.real)), float(err)

def hermite_response(k, degree):
    V = np.diag(np.sqrt(np.arange(1,degree+1)),1)
    V += V.T
    rates = np.arange(degree+1, dtype=float)
    rates[:3] = 0
    rhs = np.eye(degree+1)[0]
    g = np.linalg.solve(np.diag(rates)+1j*k*V, rhs)
    return float(1/(k*g[0].real))

def kinetic_rollout(k, degree, times):
    rates = np.arange(degree+1, dtype=float)
    rates[:3] = 0
    off = -1j*k*np.sqrt(np.arange(1,degree+1))
    A = diags([off, -rates, off], [-1,0,1], dtype=complex).tocsr()
    h0 = np.zeros(degree+1, dtype=complex)
    h0[2] = 1/np.sqrt(2)  # h=He_2/2, so T(0)=1
    h = expm_multiply(A, h0, start=times[0], stop=times[-1], num=len(times),
                      traceA=-rates.sum())
    moments = np.column_stack((h[:,0], h[:,1], np.sqrt(2)*h[:,2]))
    energy = np.sum(abs(h)**2, axis=1)/2
    q = np.sqrt(6)*h[:,3]/2
    return moments, energy, q

def moment_rollout(k, chi, times):
    A = np.array([[0,-1j*k,0], [-1j*k,0,-1j*k],
                  [0,-2j*k,-2*k*k*chi]], dtype=complex)
    U = expm_multiply(A, np.array([0,0,1],dtype=complex),
                      start=times[0], stop=times[-1], num=len(times),
                      traceA=np.trace(A))
    energy = (abs(U[:,0])**2+abs(U[:,1])**2+abs(U[:,2])**2/2)/2
    return U, energy

def relative_history_error(candidate, reference, times):
    return float(np.sqrt(np.trapezoid(np.sum(abs(candidate-reference)**2,axis=1),times)
                         /np.trapezoid(np.sum(abs(reference)**2,axis=1),times)))
