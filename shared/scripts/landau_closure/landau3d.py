"""Linearized like-particle Landau operator in 3D (axisymmetric about x), Galerkin in
polynomials psi_n(v_x) L_m(v_perp^2/2), n + 2m <= d.  Units: n = m = v_t = 1, Braginskii time tau = 1.
Weak form:  <g, Lam h> = (3 sqrt(pi)/4) * E_{v,v'}[ (grad g - grad' g') . U(v-v') . (grad h - grad' h') ],
U(w) = (I - w w^T/|w|^2)/|w|.  Exact Gaussian quadrature in (V,u) = ((v+v')/sqrt2, (v-v')/sqrt2)."""
import numpy as np, sys, time
from numpy.polynomial.hermite_e import hermegauss
from numpy.polynomial.laguerre import laggauss
from numpy.polynomial.legendre import leggauss
from scipy.special import eval_hermitenorm, eval_laguerre, eval_genlaguerre, gammaln

def basis(d): return [(n, m) for m in range(d // 2 + 1) for n in range(d - 2 * m + 1)]
def psi(n, x): return eval_hermitenorm(n, x) / np.exp(0.5 * gammaln(n + 1)) if n >= 0 else 0 * x
def grads(B, v):
    """v: (npts,3) -> array (nb, npts, 3) of gradients of basis functions."""
    x = v[:, 0]; s2 = 0.5 * (v[:, 1] ** 2 + v[:, 2] ** 2); out = np.empty((len(B), len(x), 3))
    for i, (n, m) in enumerate(B):
        Lm = eval_laguerre(m, s2); dL = -eval_genlaguerre(m - 1, 1, s2) if m >= 1 else 0 * s2
        out[i, :, 0] = np.sqrt(n) * psi(n - 1, x) * Lm if n >= 1 else 0.0
        p = psi(n, x) * dL; out[i, :, 1] = p * v[:, 1]; out[i, :, 2] = p * v[:, 2]
    return out
def landau_matrix(d, verbose=False):
    B = basis(d); nb = len(B)
    xv, wv = hermegauss(d + 1); wv = wv / np.sqrt(2 * np.pi)
    V = np.array(np.meshgrid(xv, xv, xv, indexing="ij")).reshape(3, -1).T
    WV = (wv[:, None, None] * wv[None, :, None] * wv[None, None, :]).ravel()
    nt, nc, nph = d // 2 + 2, d + 3, 2 * d + 6
    t, wt = laggauss(nt); c, wc = leggauss(nc); ph = 2 * np.pi * np.arange(nph) / nph
    T_, C_, P_ = np.meshgrid(t, c, ph, indexing="ij"); r = np.sqrt(2 * T_).ravel(); st = np.sqrt(1 - C_ ** 2).ravel()
    uh = np.stack([C_.ravel(), st * np.cos(P_.ravel()), st * np.sin(P_.ravel())], 1)
    U = r[:, None] * uh
    WU = (wt[:, None, None] * wc[None, :, None] * np.ones(nph)[None, None, :]).ravel() * (2 * np.pi / nph) / (2 * np.pi) ** 1.5
    Lam = np.zeros((nb, nb)); chk = 0.0
    for iv in range(len(V)):
        v1 = (V[iv][None, :] + U) / np.sqrt(2); v2 = (V[iv][None, :] - U) / np.sqrt(2)
        D = grads(B, v1) - grads(B, v2)                      # (nb, npts, 3)
        D = D - np.einsum("bpi,pi->bp", D, uh)[:, :, None] * uh[None]   # project perpendicular to u
        w = WV[iv] * WU / np.sqrt(2)                          # 1/|w| = 1/(sqrt2 |u|); 1/|u| is in the measure
        Dw = D * w[None, :, None]
        Lam += np.tensordot(Dw, D, axes=([1, 2], [1, 2])); chk += WV[iv] * WU.sum()
    return B, 0.75 * np.sqrt(np.pi) * Lam, chk
if __name__ == "__main__":
    # usage: python landau3d.py DEGREE OUTPUT_DIR
    d = int(sys.argv[1]); t0 = time.time(); B, Lam, chk = landau_matrix(d)
    np.save(f"{sys.argv[2]}/landau_d{d}.npy", Lam)
    print(f"d={d} nb={len(B)}  E[1/|u|] check {chk:.10f} vs {np.sqrt(2/np.pi):.10f}   {time.time()-t0:.0f}s  asym {abs(Lam-Lam.T).max():.1e}")
