"""3D quasi-static closure quantities in the polynomial Galerkin space."""
import numpy as np
from landau3d import basis
def vecs(d):
    B = basis(d); ix = {b: i for i, b in enumerate(B)}; nb = len(B)
    def e(*terms):
        v = np.zeros(nb)
        for c, n, m in terms: v[ix[(n, m)]] += c
        return v
    one = e((1, 0, 0)); vx = e((1, 1, 0))
    E2 = e((np.sqrt(2), 2, 0), (-2, 0, 1))            # |v|^2 - 3
    th = e((-2, 0, 1), (-2 * np.sqrt(2), 2, 0))       # theta = v_perp^2 - 2 v_x^2
    Q = e((0.5 * np.sqrt(6), 3, 0), (-1.0, 1, 1))     # v_x (|v|^2 - 5)/2
    Vx = np.zeros((nb, nb))
    for (n, m), i in ix.items():
        if (n + 1, m) in ix: Vx[ix[(n + 1, m)], i] = Vx[i, ix[(n + 1, m)]] = np.sqrt(n + 1)
    return B, ix, one, vx, E2, th, Q, Vx
def dougherty(d, nu=1.0):
    B, ix, one, vx, E2, th, Q, Vx = vecs(d)
    L = np.diag([nu * (n + 2 * m) for n, m in B]); E = E2 / np.sqrt(6)
    return L - nu * np.outer(vx, vx) - 2 * nu * np.outer(E, E)
def pinv_on_complement(L, H):
    Hq, _ = np.linalg.qr(np.array(H).T); P = np.eye(len(L)) - Hq @ Hq.T
    return P @ np.linalg.pinv(P @ L @ P, rcond=1e-11, hermitian=True) @ P
def constants(L, d):
    B, ix, one, vx, E2, th, Q, Vx = vecs(d); Lp = pinv_on_complement(L, [one, vx, E2])
    Xi = Lp @ Q; kF = Q @ Xi; eta = th @ Lp @ th / 12
    vx2 = Vx @ Vx @ one                                # v_x^2 (exact while degree <= d)
    chis = one - vx2 + Vx @ Xi / kF                    # chi_* = 1 - v_x^2 + v_x Xi/kF
    resid = [abs(chis @ one), abs(chis @ E2)]
    Cs = chis @ Lp @ chis; X0 = th @ Lp @ chis
    return dict(kF=kF, eta=eta, Cs=Cs, X0=X0, Kexact=kF * (Cs - X0 / 3), Kbound=kF * (Cs + np.sqrt(12 * eta * Cs) / 3),
                kern=max(np.abs(L @ one).max(), np.abs(L @ vx).max(), np.abs(L @ E2).max()), resid=max(resid), mineig=np.linalg.eigvalsh(L).min())
def theta(L, d, k):
    B, ix, one, vx, E2, th, Q, Vx = vecs(d)
    g = np.linalg.solve(1j * k * Vx + L, one.astype(complex))
    n1 = one @ g; T1 = (E2 @ g) / 3; q1 = Q @ g
    return (-1 / (k * T1)).real, n1.real, abs(1j * k * (vx @ g) - 1), abs(q1 - 1j / k), (th @ g).real
