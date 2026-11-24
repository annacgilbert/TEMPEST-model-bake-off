#!/usr/bin/env python3
"""Monte Carlo check of the kinetic limit of a tagged particle in a prescribed
Ornstein-Uhlenbeck field (docs/orbit_kinetic_limit_theorem.tex).

Model:  dx = v dt,  dv = eps F(x,t) dt,
        F(x,t) = sum_k Re( f_k a_k(t) exp(i k.x) ),
        da_k = -(gamma_k + i omega_k) a_k dt + sqrt(2 gamma_k) dB_k.
Kinetic time: t = tau / eps^2.  Limit generator (Theorem 1 of the note):
        L = div_v( D(v) grad_v ) + c(v).grad_v,
        D = (1/2) sum_k Re(1/lambda_k) Re(f_k (x) conj f_k),
        c_i = -(1/2) sum_k Im( f_k^i (k.conj f_k) ) Re(1/lambda_k^2),
        lambda_k(v) = gamma_k + i (omega_k - k.v).

Experiments (all seeded):
  A  d=1, stationary field, tau=1, several eps: E psi(v) against a grid
     solution of the limit equation with drift theta*D'(v), theta = 1
     (divergence form, the theorem), 0 and 2 (the two wrong candidates); and
     the measured error against eps^2 K2, K2 being the coefficient predicted
     by the second-order theorem.  Run for a "broad" model (gamma ~ 1.5-2),
     where the eps^2 asymptotics are reached, and for a "sharp" one
     (gamma ~ 0.5-0.9), where they are not at the eps that can be afforded.
     One observable depends on X = eps^2 x.
  B  d=1, field started from a deterministic state: the O(eps) initial-layer
     term and the next O(eps^2) term against their predicted coefficients.
  C  d=2, circularly polarised non-solenoidal modes, for which c != 0:
     the particle against the limit diffusion with drift div D + c (theorem),
     div D alone, and zero.
  D  time-step error of the particle integrator (coarse against fine step,
     same field path).  The scheme is weakly second order; pathwise the two
     runs differ at O(dt), so the comparison is limited by its own standard
     error, which is reported.
Error sources are reported separately: Monte Carlo standard errors, particle
time-step error, limit-solver discretisation error, and the eps-dependent
model error that the theorems bound.

Only numpy and the standard library are used.  Output: one JSON file in
results/orbit_kinetic_limit/ (an existing file is never overwritten).
"""
import argparse
import json
import math
import os
import time
from multiprocessing import Pool

import numpy as np

MASTER_SEED = 20261124
N_CHUNKS = 24          # fixed, so results do not depend on the worker count

# --------------------------------------------------------------------------
# models
# --------------------------------------------------------------------------


def model_1d_broad():
    k = np.array([[1.0], [-0.8], [1.5]])
    phi = np.array([1.8, 2.2, 1.4])
    f = -1j * phi[:, None] * k                 # potential field
    return dict(k=k, f=f.astype(complex),
                gam=np.array([1.5, 2.0, 1.2]),
                om=np.array([0.5, 0.3, -1.0]))


def model_1d_sharp():
    k = np.array([[1.0], [-0.7], [1.6]])
    phi = np.array([1.2, 1.0, 0.8])
    f = -1j * phi[:, None] * k                 # potential field
    return dict(k=k, f=f.astype(complex),
                gam=np.array([0.6, 0.9, 0.5]),
                om=np.array([0.5, 0.3, -1.0]))


def model_2d():
    ang = np.array([-0.5, -0.15, 0.2, 0.55])
    kn = np.array([2.0, 1.8, 2.2, 1.9])
    khat = np.stack([np.cos(ang), np.sin(ang)], axis=1)
    kperp = np.stack([-np.sin(ang), np.cos(ang)], axis=1)
    k = kn[:, None] * khat
    f = khat + 1j * kperp                      # circular, k.f != 0: c != 0
    return dict(k=k, f=f.astype(complex),
                gam=np.array([2.0, 1.8, 2.2, 2.0]),
                om=np.array([0.6, 0.2, 0.5, 0.3]))


def coefficients(model, v):
    """D (n,d,d), div D (n,d), c (n,d) and sqrt(r_k) (n,K) at velocities v (n,d)."""
    k, f, gam, om = model["k"], model["f"], model["gam"], model["om"]
    s = om[None, :] - v @ k.T                              # (n,K)
    den = gam[None, :] ** 2 + s ** 2
    r = gam[None, :] / den                                 # Re 1/lambda
    re2 = (gam[None, :] ** 2 - s ** 2) / den ** 2          # Re 1/lambda^2
    im2 = -2.0 * gam[None, :] * s / den ** 2               # Im 1/lambda^2
    S = np.real(f[:, :, None] * np.conj(f[:, None, :]))    # (K,d,d)
    D = 0.5 * np.einsum("nk,kij->nij", r, S)
    kf = f * np.sum(k * np.conj(f), axis=1)[:, None]       # f^i (k.conj f), (K,d)
    divD = 0.5 * np.einsum("nk,ki->ni", -im2, np.real(kf))
    c = -0.5 * np.einsum("nk,ki->ni", re2, np.imag(kf))
    return D, divD, c, np.sqrt(r)


# --------------------------------------------------------------------------
# observables
# --------------------------------------------------------------------------

OBS_1D = ["tanh(v)", "exp(-v^2/2)", "cos(X)", "v (unbounded)"]
OBS_2D = ["tanh(v1)", "tanh(v2)", "exp(-|v|^2/2)", "v1 (unbounded)", "v2 (unbounded)"]


def observe(X, v):
    """Rows: observables; columns: samples."""
    if v.shape[1] == 1:
        w = v[:, 0]
        return np.stack([np.tanh(w), np.exp(-0.5 * w * w), np.cos(X[:, 0]), w])
    return np.stack([np.tanh(v[:, 0]), np.tanh(v[:, 1]),
                     np.exp(-0.5 * np.sum(v * v, axis=1)), v[:, 0], v[:, 1]])


# --------------------------------------------------------------------------
# particle Monte Carlo (exact OU updates, velocity-Verlet for the particle)
# --------------------------------------------------------------------------


def _force(model, x, a):
    ph = a * np.exp(1j * (x @ model["k"].T))
    return np.real(ph @ model["f"])


def _particle_chunk(args):
    (model, eps, tau, dt, n, seed, v0, a0, dt_check) = args
    rng = np.random.default_rng(seed)
    k, gam, om = model["k"], model["gam"], model["om"]
    K, d = k.shape
    t_end = tau / eps ** 2
    nsteps = max(1, int(round(t_end / dt)))
    nsub = 2 if dt_check else 1
    h = t_end / (nsteps * nsub)                 # OU step
    rho = np.exp(-(gam + 1j * om) * h)[None, :]
    sig = np.sqrt((1.0 - np.exp(-2.0 * gam * h)) / 2.0)[None, :]

    def cnormal():
        return rng.standard_normal((n, 2 * K)).view(np.complex128)

    if a0 is None:
        a = cnormal() / math.sqrt(2.0)
    else:
        a = np.tile(np.asarray(a0, dtype=complex)[None, :], (n, 1))
    x = np.zeros((n, d))
    v = np.tile(np.asarray(v0, float)[None, :], (n, 1))
    if dt_check:
        xc, vc = x.copy(), v.copy()
        Fc = _force(model, xc, a)
    F = _force(model, x, a)
    for _ in range(nsteps):
        if dt_check:
            vc += 0.5 * (2 * h) * eps * Fc
            xc += (2 * h) * vc
        for _ in range(nsub):
            v += 0.5 * h * eps * F
            x += h * v
            a = rho * a + sig * cnormal()
            F = _force(model, x, a)
            v += 0.5 * h * eps * F
        if dt_check:
            Fc = _force(model, xc, a)
            vc += 0.5 * (2 * h) * eps * Fc
    o = observe(eps ** 2 * x, v)
    out = dict(n=n, s1=o.sum(axis=1), s2=(o * o).sum(axis=1))
    if dt_check:
        dlt = observe(eps ** 2 * xc, vc) - o      # coarse minus fine
        out.update(d1=dlt.sum(axis=1), d2=(dlt * dlt).sum(axis=1))
    return out


def particle_mc(pool, model, eps, tau, dt, n, seed_seq, v0, a0=None, dt_check=False):
    seeds = seed_seq.spawn(N_CHUNKS)
    nc = n // N_CHUNKS
    res = pool.map(_particle_chunk,
                   [(model, eps, tau, dt, nc, s, v0, a0, dt_check) for s in seeds])
    ntot = sum(r["n"] for r in res)
    s1 = sum(r["s1"] for r in res)
    s2 = sum(r["s2"] for r in res)
    mean = s1 / ntot
    se = np.sqrt(np.maximum(s2 / ntot - mean ** 2, 0.0) / ntot)
    out = dict(mean=mean, se=se, n=ntot)
    if dt_check:
        d1 = sum(r["d1"] for r in res)
        d2 = sum(r["d2"] for r in res)
        dm = d1 / ntot
        out.update(dmean=dm, dse=np.sqrt(np.maximum(d2 / ntot - dm ** 2, 0.0) / ntot))
    return out


# --------------------------------------------------------------------------
# limit diffusion by Euler-Maruyama (any d), with a selectable drift
# --------------------------------------------------------------------------


def _limit_chunk(args):
    (model, tau, h, n, seed, v0, drift) = args
    rng = np.random.default_rng(seed)
    f = model["f"]
    K, d = f.shape
    p, q = np.real(f), np.imag(f)
    nsteps = int(round(tau / h))
    h = tau / nsteps
    X = np.zeros((n, d))
    V = np.tile(np.asarray(v0, float)[None, :], (n, 1))
    for _ in range(nsteps):
        _, divD, c, sr = coefficients(model, V)
        if drift == "divD+c":
            b = divD + c
        elif drift == "divD":
            b = divD
        elif drift == "zero":
            b = 0.0
        else:
            raise ValueError(drift)
        xi = rng.standard_normal((n, K)) * sr
        et = rng.standard_normal((n, K)) * sr
        X += h * V
        V += h * b + math.sqrt(h) * (xi @ p + et @ q)
    o = observe(X, V)
    return dict(n=n, s1=o.sum(axis=1), s2=(o * o).sum(axis=1))


def limit_sde(pool, model, tau, h, n, seed_seq, v0, drift):
    seeds = seed_seq.spawn(N_CHUNKS)
    nc = n // N_CHUNKS
    res = pool.map(_limit_chunk, [(model, tau, h, nc, s, v0, drift) for s in seeds])
    ntot = sum(r["n"] for r in res)
    mean = sum(r["s1"] for r in res) / ntot
    se = np.sqrt(np.maximum(sum(r["s2"] for r in res) / ntot - mean ** 2, 0.0) / ntot)
    return dict(mean=mean, se=se, n=ntot)


# --------------------------------------------------------------------------
# d=1 grid solver for  u_tau = (D u')' + (theta-1) D' u'
# --------------------------------------------------------------------------


def grid_generator(model, vg, theta):
    h = vg[1] - vg[0]
    n = len(vg)
    vh = 0.5 * (vg[1:] + vg[:-1])
    Dh = coefficients(model, vh[:, None])[0][:, 0, 0]
    _, divD, _, _ = coefficients(model, vg[:, None])
    M = np.zeros((n, n))
    i = np.arange(n - 1)
    M[i, i + 1] += Dh / h ** 2
    M[i, i] -= Dh / h ** 2
    M[i + 1, i] += Dh / h ** 2
    M[i + 1, i + 1] -= Dh / h ** 2            # zero-flux ends; symmetric
    if theta != 1.0:
        e = (theta - 1.0) * divD[1:-1, 0] / (2 * h)
        j = np.arange(1, n - 1)
        M[j, j + 1] += e
        M[j, j - 1] -= e
    return M


def grid_propagate(M, psi, tau, nsteps=None):
    """exp(tau M) psi: exact in time by eigh when M is symmetric and nsteps is
    None, otherwise Crank-Nicolson with 2^m steps by repeated squaring."""
    if nsteps is None:
        lam, U = np.linalg.eigh(M)
        return U @ (np.exp(tau * lam) * (U.T @ psi))
    m = int(round(math.log2(nsteps)))
    hh = tau / 2 ** m
    eye = np.eye(len(M))
    S = np.linalg.solve(eye - 0.5 * hh * M, eye + 0.5 * hh * M)
    for _ in range(m):
        S = S @ S
    return S @ psi


# --------------------------------------------------------------------------
# d=1 corrector hierarchy on a grid: L, B and L_1 of the note, computed from
# their definitions  L = -Pi G Q G,  B = Pi G Q^2 G,
# L_1 = -Pi G Q ( G Q G Q G + Q G L )   (no X dependence)
# Functions of (v,b) are stored as {monomial exponents: coefficient array}.
# --------------------------------------------------------------------------


class Hierarchy:
    def __init__(self, model, vg):
        self.f = model["f"][:, 0]
        self.K = len(self.f)
        self.gam = model["gam"]
        self.lam = (model["gam"][:, None]
                    + 1j * (model["om"][:, None] - model["k"][:, 0][:, None] * vg[None, :]))
        self.h = vg[1] - vg[0]

    def dv(self, c):                       # 4th-order central difference
        h = self.h
        return (-np.roll(c, -2) + 8 * np.roll(c, -1)
                - 8 * np.roll(c, 1) + np.roll(c, 2)) / (12 * h)

    def G(self, pol):
        out = {}
        for mon, c in pol.items():
            dc = self.dv(c)
            for j in range(self.K):
                for off, fac in ((2 * j, 0.5 * self.f[j]), (2 * j + 1, 0.5 * np.conj(self.f[j]))):
                    m2 = list(mon)
                    m2[off] += 1
                    m2 = tuple(m2)
                    out[m2] = out.get(m2, 0) + fac * dc
        return out

    def Pi(self, pol):
        tot = 0
        for mon, c in pol.items():
            if all(mon[2 * j] == mon[2 * j + 1] for j in range(self.K)):
                tot = tot + c * math.prod(math.factorial(mon[2 * j]) for j in range(self.K))
        return tot

    def Q(self, pol):
        src = dict(pol)
        zero = (0,) * (2 * self.K)
        src.pop(zero, None)
        if not src:
            return {}
        deg = max(sum(m) for m in src)
        phi = {}
        for dg in range(deg, 0, -1):
            for mon in [m for m in list(src) if sum(m) == dg]:
                mu = sum(mon[2 * j] * self.lam[j] + mon[2 * j + 1] * np.conj(self.lam[j])
                         for j in range(self.K))
                c = -src[mon] / mu
                phi[mon] = c
                for j in range(self.K):
                    mj, nj = mon[2 * j], mon[2 * j + 1]
                    if mj > 0 and nj > 0:
                        low = list(mon)
                        low[2 * j] -= 1
                        low[2 * j + 1] -= 1
                        low = tuple(low)
                        if low != zero:
                            src[low] = src.get(low, 0) - 2 * self.gam[j] * mj * nj * c
        phi[zero] = -self.Pi(phi)             # Pi(Q chi) = 0
        return phi

    def scalar(self, w):
        return {(0,) * (2 * self.K): w.astype(complex)}

    def L(self, w):
        return np.real(-self.Pi(self.G(self.Q(self.G(self.scalar(w))))))

    def B(self, w):
        return np.real(self.Pi(self.G(self.Q(self.Q(self.G(self.scalar(w)))))))

    def L1(self, w):
        qg = lambda p: self.Q(self.G(p))
        t1 = self.G(qg(qg(self.scalar(w))))
        t2 = self.Q(self.G(self.scalar(self.L(w))))
        s = dict(t1)
        for m, c in t2.items():
            s[m] = s.get(m, 0) + c
        return np.real(-self.Pi(self.G(self.Q(s))))


def second_order_coefficient(model, vg, psi, tau, i0, nquad=32, b0=None):
    """K2 = [ int_0^tau P_{tau-s} L_1 P_s psi ds - P_tau B psi ](v0), the
    residual of the hierarchy's L against the grid generator and, if a field
    state b0 is given, the correctors Phi_1 = -Q G u and Phi_2 = Q G Q G u of
    u = P_tau psi evaluated at (v0, b0)."""
    M = grid_generator(model, vg, 1.0)
    lam, U = np.linalg.eigh(M)
    P = lambda s, w: U @ (np.exp(s * lam) * (U.T @ w))
    H = Hierarchy(model, vg)
    inner = np.abs(vg) < vg[-1] - 1.5          # discard wrap-around rows
    clip = lambda w: np.where(inner, w, 0.0)
    resid = float(np.max(np.abs(clip(H.L(psi) - M @ psi))))
    # composite Simpson in s
    ss = np.linspace(0.0, tau, nquad + 1)
    wts = np.ones(nquad + 1)
    wts[1:-1:2] = 4
    wts[2:-1:2] = 2
    wts *= tau / (3 * nquad)
    acc = 0.0
    for s, wq in zip(ss, wts):
        acc += wq * P(tau - s, clip(H.L1(P(s, psi))))[i0]
    mem = P(tau, clip(H.B(psi)))[i0]
    out = dict(K2=float(acc - mem), generator_part=float(acc),
               terminal_part=float(-mem), L_residual=resid)
    if b0 is not None:
        b0 = np.asarray(b0, dtype=complex)

        def at(pol):
            tot = 0.0
            for mon, c in pol.items():
                z = c[i0] if np.ndim(c) else c
                for j in range(H.K):
                    z = z * b0[j] ** mon[2 * j] * np.conj(b0[j]) ** mon[2 * j + 1]
                tot += z
            return float(np.real(tot))

        qgu = H.Q(H.G(H.scalar(P(tau, psi))))
        out["Phi1"] = -at(qgu)
        out["Phi2"] = at(H.Q(H.G(qgu)))
    return out


# --------------------------------------------------------------------------
# experiments
# --------------------------------------------------------------------------


def _dump_model(model):
    return {k: dict(re=np.real(v).tolist(), im=np.imag(v).tolist())
            if np.iscomplexobj(v) else v.tolist() for k, v in model.items()}


def experiment_1d(pool, ss, quick, model, eps_list, n, with_B, with_D):
    v0, tau, dt = 1.2, 1.0, 0.05
    psis = [np.tanh, lambda v: np.exp(-0.5 * v * v)]
    names = OBS_1D[:2]
    D0, dD0, _, _ = coefficients(model, np.array([[v0]]))
    out = dict(model=_dump_model(model), v0=v0, tau=tau, observables=OBS_1D,
               D_at_v0=float(D0[0, 0, 0]), dD_at_v0=float(dD0[0, 0]))
    s_lim, s_A, s_B, s_D = ss.spawn(4)

    # ---- limit solver: grid, with its own discretisation error
    def solve(npts, theta, nsteps=None):
        vg = np.linspace(-12.0, 12.0, npts)
        i0 = int(round((v0 - vg[0]) / (vg[1] - vg[0])))
        assert abs(vg[i0] - v0) < 1e-12
        M = grid_generator(model, vg, theta)
        vals, ders = [], []
        for psi in psis:
            u = grid_propagate(M, psi(vg), tau, nsteps)
            vals.append(u[i0])
            ders.append((u[i0 + 1] - u[i0 - 1]) / (vg[i0 + 1] - vg[i0 - 1]))
        return np.array(vals), np.array(ders)

    nfine, ncoarse = (961, 481) if not quick else (481, 241)
    u1, du1 = solve(nfine, 1.0)
    u1c, _ = solve(ncoarse, 1.0)
    u1cn, _ = solve(nfine, 1.0, nsteps=256)
    lim = {"names": names,
           "theta=1 (divergence form)": u1.tolist(),
           "grid_error_theta1": np.abs(u1 - u1c).tolist(),
           "crank_nicolson_256_minus_exact_in_time": (u1cn - u1).tolist()}
    for th in (0.0, 2.0):
        a, _ = solve(nfine, th, nsteps=256)
        b, _ = solve(ncoarse, th, nsteps=128)
        lim["theta=%g" % th] = a.tolist()
        lim["grid_and_time_error_theta%g" % th] = np.abs(a - b).tolist()
    out["limit_grid"] = lim

    # ---- limit solver: independent Euler-Maruyama cross-check (also gives cos X)
    nl = 960000 if not quick else 96000
    h = 1.0 / 200
    s_a, s_b = s_lim.spawn(2)
    em = limit_sde(pool, model, tau, h, nl, s_a, [v0], "divD+c")
    em2 = limit_sde(pool, model, tau, 2 * h, nl, s_b, [v0], "divD+c")
    out["limit_sde"] = dict(h=h, n=nl, mean=em["mean"].tolist(), se=em["se"].tolist(),
                            mean_2h=em2["mean"].tolist(), se_2h=em2["se"].tolist(),
                            step_error_estimate=(em2["mean"] - em["mean"]).tolist(),
                            sde_minus_grid=(em["mean"][:2] - u1).tolist())

    # ---- second-order coefficient from the corrector hierarchy
    a0 = np.array([1.5, -1.0j, 0.8 + 0.6j])      # x0 = 0, so b0 = a0
    vg = np.linspace(-12.0, 12.0, nfine)
    i0 = int(round((v0 - vg[0]) / (vg[1] - vg[0])))
    k2 = [second_order_coefficient(model, vg, psi(vg), tau, i0, b0=a0) for psi in psis]
    vgc = np.linspace(-12.0, 12.0, ncoarse)
    i0c = int(round((v0 - vgc[0]) / (vgc[1] - vgc[0])))
    k2c = [second_order_coefficient(model, vgc, psi(vgc), tau, i0c, nquad=16, b0=a0)
           for psi in psis]
    out["second_order"] = dict(names=names, fine=k2, coarse=k2c)
    K2 = np.array([c["K2"] for c in k2])

    # ---- A: stationary field, several eps
    rows = []
    for eps, s in zip(eps_list, s_A.spawn(len(eps_list))):
        t0 = time.time()
        r = particle_mc(pool, model, eps, tau, dt, n, s, [v0])
        rows.append(dict(eps=eps, t=tau / eps ** 2, n=r["n"], dt=dt,
                         mean=r["mean"].tolist(), se=r["se"].tolist(),
                         err_vs_theta1=(r["mean"][:2] - u1).tolist(),
                         err_over_eps2=((r["mean"][:2] - u1) / eps ** 2).tolist(),
                         se_over_eps2=(r["se"][:2] / eps ** 2).tolist(),
                         K2_predicted=K2.tolist(),
                         err_cosX_vs_limit_sde=float(r["mean"][2] - em["mean"][2]),
                         se_cosX=float(math.hypot(r["se"][2], em["se"][2])),
                         seconds=time.time() - t0))
        print("A eps=%.4f err/eps^2" % eps, np.round(rows[-1]["err_over_eps2"], 4),
              "+-", np.round(rows[-1]["se_over_eps2"], 4), "K2", np.round(K2, 4),
              "%.1fs" % rows[-1]["seconds"], flush=True)
    out["A_stationary"] = rows

    # ---- B: deterministic initial field
    if with_B:
        lam0 = model["gam"] + 1j * (model["om"] - model["k"][:, 0] * v0)
        dv_shift = float(np.sum(np.real(a0 * model["f"][:, 0] / lam0)))
        c1 = np.array([c["Phi1"] for c in k2])
        c2 = np.array([c["Phi2"] for c in k2]) + K2
        rowsB = []
        epsB = [0.3536, 0.25, 0.1768] if not quick else [0.3536, 0.25]
        nB = (2 * n) // 5
        for eps, s in zip(epsB, s_B.spawn(len(epsB))):
            r = particle_mc(pool, model, eps, tau, dt, nB, s, [v0], a0=a0)
            diff = r["mean"][:2] - u1
            rowsB.append(dict(eps=eps, n=r["n"], mean=r["mean"].tolist(), se=r["se"].tolist(),
                              diff=diff.tolist(),
                              predicted_first_order=(eps * c1).tolist(),
                              predicted_second_order=(eps * c1 + eps ** 2 * c2).tolist(),
                              diff_over_eps=(diff / eps).tolist(),
                              se_over_eps=(r["se"][:2] / eps).tolist()))
            print("B eps=%.4f diff" % eps, np.round(diff, 4), "+-", np.round(r["se"][:2], 4),
                  "pred1", np.round(eps * c1, 4), "pred2",
                  np.round(eps * c1 + eps ** 2 * c2, 4), flush=True)
        out["B_deterministic_initial_field"] = dict(
            a0=[[z.real, z.imag] for z in a0], velocity_shift=dv_shift,
            order_eps_coefficient=c1.tolist(),
            order_eps_coefficient_closed_form=(dv_shift * du1).tolist(),
            order_eps2_coefficient=c2.tolist(), rows=rowsB)

    # ---- D: time-step error (dt = 0.1 against dt = 0.05, same field path)
    if with_D:
        epsD = 0.3536
        r = particle_mc(pool, model, epsD, tau, 0.05, (2 * n) // 5, s_D, [v0], dt_check=True)
        out["D_time_step"] = dict(eps=epsD, n=r["n"], dt_fine=0.05, dt_coarse=0.1,
                                  coarse_minus_fine=r["dmean"].tolist(),
                                  se=r["dse"].tolist(),
                                  note="weakly second-order scheme: the error at dt=0.05 "
                                       "is about one third of this difference")
        print("D", np.round(r["dmean"], 5), "+-", np.round(r["dse"], 5), flush=True)
    return out


def experiment_2d(pool, ss, quick):
    model = model_2d()
    v0, tau = [0.2, 0.0], 1.0
    out = dict(model=_dump_model(model), v0=v0, tau=tau, observables=OBS_2D)
    D0, divD, c, _ = coefficients(model, np.array([v0]))
    out["D_at_v0"] = D0[0].tolist()
    out["divD_at_v0"] = divD[0].tolist()
    out["c_at_v0"] = c[0].tolist()
    nl = 960000 if not quick else 96000
    h = 1.0 / 200
    lim = {}
    seeds = ss.spawn(5)
    for drift, s in zip(("divD+c", "divD", "zero"), seeds[:3]):
        r = limit_sde(pool, model, tau, h, nl, s, v0, drift)
        lim[drift] = dict(mean=r["mean"].tolist(), se=r["se"].tolist())
    r2 = limit_sde(pool, model, tau, 2 * h, nl, seeds[3], v0, "divD+c")
    lim["step_error_estimate_divD+c"] = (r2["mean"] - np.array(lim["divD+c"]["mean"])).tolist()
    lim["h"] = h
    lim["n"] = nl
    out["limit_sde"] = lim
    n = 960000 if not quick else 96000
    rows = []
    epsC = [0.5, 0.3536, 0.25] if not quick else [0.5, 0.3536]
    for eps, s in zip(epsC, seeds[4].spawn(len(epsC))):
        t0 = time.time()
        r = particle_mc(pool, model, eps, tau, 0.05, n, s, v0)
        rows.append(dict(eps=eps, n=r["n"], mean=r["mean"].tolist(), se=r["se"].tolist(),
                         seconds=time.time() - t0))
        print("C eps=%.4f" % eps, np.round(rows[-1]["mean"], 4), "%.1fs" % rows[-1]["seconds"],
              flush=True)
    out["C_particle"] = rows
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true", help="smaller sample sizes")
    ap.add_argument("--workers", type=int, default=min(10, os.cpu_count() or 1))
    ap.add_argument("--out", default=None)
    args = ap.parse_args()
    here = os.path.dirname(os.path.abspath(__file__))
    outdir = os.path.join(here, "..", "results", "orbit_kinetic_limit")
    os.makedirs(outdir, exist_ok=True)
    path = args.out or os.path.join(outdir, "orbit_kinetic_limit_check.json")
    base, ext = os.path.splitext(path)
    i = 2
    while os.path.exists(path):                 # never overwrite a result
        path = "%s_run%d%s" % (base, i, ext)
        i += 1
    t0 = time.time()
    root = np.random.SeedSequence(MASTER_SEED)
    s1, s2, s3 = root.spawn(3)
    q = args.quick
    with Pool(args.workers) as pool:
        res = dict(script="orbit_kinetic_limit_check.py", master_seed=MASTER_SEED,
                   n_chunks=N_CHUNKS, quick=q, numpy=np.__version__)
        res["d1_broad"] = experiment_1d(
            pool, s1, q, model_1d_broad(), [0.5, 0.3536, 0.25],
            2400000 if not q else 96000, with_B=True, with_D=True)
        res["d1_sharp"] = experiment_1d(
            pool, s2, q, model_1d_sharp(),
            [0.5, 0.3536, 0.25, 0.1768] if not q else [0.5, 0.3536, 0.25],
            1200000 if not q else 96000, with_B=False, with_D=False)
        res["d2"] = experiment_2d(pool, s3, q)
    res["runtime_seconds"] = time.time() - t0
    with open(path, "w") as fh:
        json.dump(res, fh, indent=1)
    print("wrote", path, "in %.1fs" % res["runtime_seconds"])


if __name__ == "__main__":
    main()
