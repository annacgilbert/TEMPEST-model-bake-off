"""Numerical checks for the rate of the Landau collisionless limit.

Three independent parts; none of them is a proof.

A. Monte Carlo check of the exact splitting of the Landau form
     D[f] = a[f] - 12 pi c int M^2 f^2
            - c iint M M' f f' ( v.U(v-v')v' - 2/|v-v'| ) dv dv',
   c = 3 sqrt(pi)/(2 tau), which replaces the epsilon-form of (W5).
   Every term is an expectation over independent Gaussians v, v'.
B. Rate of approach to the collisionless limit for the exact Dougherty
   formulas (Theorem 4.3, Theorem 7.7): first correction is O(nu/|k|).
C. One-dimensional Dougherty: the Airy-layer trial functions of Appendix D
   inserted in the dual certificates, compared with the exact n_1.  For
   Dougherty the collision form is exactly local, so this isolates the
   error of the trial functions.

Run:  python rate_check.py
Writes results/2026-11-18-rate/metrics.json and refuses to overwrite.
"""
import json
import sys
import time
from pathlib import Path

import numpy as np
from scipy.integrate import quad, simpson, cumulative_simpson

OUT = Path(__file__).resolve().parent / "results" / "2026-11-18-rate"
CONFIG = {
    "seed": 20261118,
    "mc_samples": 40_000_000,
    "mc_chunk": 2_000_000,
    "dougherty_y": [0.2, 0.1, 0.05, 0.02, 0.01, 0.005],
    "trial_k": [10.0, 30.0, 100.0, 300.0, 1000.0, 3000.0, 10000.0],
    "nu": 1.0,
    "du": 0.004,
    "vmax": 8.0,
    "vcut": 6.0,
    "t_nodes": 2400,
    "t_max": 7.0,
}
C0 = np.sqrt(np.pi/2)


# ---------------------------------------------------------------- part A
def _apply_U(z, r, w):
    """U(z) w for rows of z, with r = |z|."""
    zw = np.sum(z*w, axis=1)
    return (w - z*(zw/r**2)[:, None])/r[:, None]


TESTS = {
    "vx*vy": (lambda v: v[:, 0]*v[:, 1],
              lambda v: np.stack([v[:, 1], v[:, 0], 0*v[:, 0]], axis=1)),
    "vx^3": (lambda v: v[:, 0]**3,
             lambda v: np.stack([3*v[:, 0]**2, 0*v[:, 0], 0*v[:, 0]], axis=1)),
    "sin(vx)+vy^2*vz": (
        lambda v: np.sin(v[:, 0])+v[:, 1]**2*v[:, 2],
        lambda v: np.stack([np.cos(v[:, 0]), 2*v[:, 1]*v[:, 2],
                            v[:, 1]**2], axis=1)),
    "|v|^2 (invariant)": (lambda v: np.sum(v*v, axis=1), lambda v: 2*v),
}


def splitting_check(rng):
    """Mean of (lhs - rhs) per sample, in units of c."""
    n_tot, chunk = CONFIG["mc_samples"], CONFIG["mc_chunk"]
    acc = {k: np.zeros(4) for k in TESTS}   # sum d, sum d^2, sum lhs, sum rhs
    done = 0
    while done < n_tot:
        v = rng.standard_normal((chunk, 3))
        vp = rng.standard_normal((chunk, 3))
        z = v-vp
        r = np.linalg.norm(z, axis=1)
        M = (2*np.pi)**-1.5*np.exp(-0.5*np.sum(v*v, axis=1))
        Uv = _apply_U(z, r, v)
        for name, (f, df) in TESTS.items():
            fv, fp, g, gp = f(v), f(vp), df(v), df(vp)
            dg = g-gp
            lhs = 0.5*np.sum(dg*_apply_U(z, r, dg), axis=1)
            Ug = _apply_U(z, r, g)
            a_loc = (np.sum(g*Ug, axis=1)-fv*np.sum(v*Ug, axis=1)
                     + 0.5*np.sum(v*Uv, axis=1)*fv**2)
            q = np.sum(vp*Uv, axis=1)-2/r
            rhs = a_loc-12*np.pi*M*fv**2-fv*fp*q
            d = lhs-rhs
            acc[name] += [d.sum(), (d*d).sum(), lhs.sum(), rhs.sum()]
        done += chunk
    out = {}
    for name, s in acc.items():
        mean = s[0]/done
        se = np.sqrt(max(s[1]/done-mean**2, 0)/done)
        out[name] = {"D_over_c": s[2]/done, "rhs_over_c": s[3]/done,
                     "difference": mean, "stderr": se}
    return out


# ---------------------------------------------------------------- part B
def dougherty_moments(a):
    """S0 = int E_a, S1 = int (1-s) E_a, with the layer s ~ a^{-1/2} resolved."""
    E = lambda s: np.exp(a*(s+np.log1p(-s)))
    pts = sorted({min(c/np.sqrt(a), 0.999) for c in (0.5, 1, 2, 4, 8, 16)})
    S0 = quad(E, 0, 1, points=pts, epsabs=1e-15, epsrel=1e-13, limit=800)[0]
    sE = quad(lambda s: s*E(s), 0, 1, points=pts, epsabs=1e-16,
              epsrel=1e-13, limit=800)[0]
    return S0, sE


def dougherty_rates():
    rows = []
    for y in CONFIG["dougherty_y"]:
        a = y**-2
        S0, sE = dougherty_moments(a)
        S1 = S0-sE
        one_minus_S0 = a*sE                      # integration by parts
        kn1_1d = S0/one_minus_S0/y               # |k| n_1 in one dimension
        num3 = 3-5*S0+4*sE                       # 3 - S0 - 4 S1
        theta3 = y*num3/S0                       # potential drive, d = 3
        nuT1 = -S0/num3
        kTperp = 2*S1*nuT1/y                     # |k| T_perp1 = c(k) |k| T_1
        kn1_3d = (S0*(1-nuT1))/y
        chith = 3*y*num3/(S0+4*S1)               # |k| chi_th
        rows.append({
            "y": y,
            "k_n1_1d": kn1_1d,
            "(k_n1_1d - c0)/y": (kn1_1d-C0)/y,
            "theta3": theta3,
            "(theta3/(3/c0) - 1)/y": (theta3*C0/3-1)/y,
            "k_n1_3d": kn1_3d,
            "(k_n1_3d - c0)/y": (kn1_3d-C0)/y,
            "k_Tperp1/y": kTperp/y,
            "k_chi_th": chith,
            "(k_chi_th/(9/(5c0)) - 1)/y": (chith*5*C0/9-1)/y,
        })
    pred = {
        "(k_n1_1d - c0)/y": np.pi/2-2/3,
        "(theta3/(3/c0) - 1)/y": -(5*C0/3-2/(3*C0)),
        "(k_chi_th/(9/(5c0)) - 1)/y": -(5*C0/3-22/(15*C0)),
        "k_Tperp1/y": -2*C0**2/3,
    }
    return rows, pred


# ---------------------------------------------------------------- part C
def profile(u):
    """F, F', W, W' at the points u by Gauss-Legendre in t."""
    x, w = np.polynomial.legendre.leggauss(CONFIG["t_nodes"])
    t = 0.5*CONFIG["t_max"]*(x+1)
    w = 0.5*CONFIG["t_max"]*w*np.exp(-t**3/3)
    F = np.empty_like(u); dF = np.empty_like(u)
    W = np.empty_like(u); dW = np.empty_like(u)
    for i in range(0, len(u), 4000):
        ph = np.outer(u[i:i+4000], t)
        c, s = np.cos(ph), np.sin(ph)
        F[i:i+4000] = c@w
        W[i:i+4000] = -(s@w)
        dF[i:i+4000] = -(s@(w*t))
        dW[i:i+4000] = -(c@(w*t))
    return F, dF, W, dW


def tail_flux(b, M, v):
    """Phi(v) = M^{-1} int_v^vmax b M ds on the grid v >= 0."""
    cum = cumulative_simpson(b*M, x=v, initial=0.0)
    return (cum[-1]-cum)/M


def trial_gaps():
    nu, rows = CONFIG["nu"], []
    for k in CONFIG["trial_k"]:
        delta = (nu/k)**(1/3)
        n = int(round(CONFIG["vmax"]/(delta*CONFIG["du"])))
        n += n % 2                                # even number of intervals
        v = np.linspace(0.0, CONFIG["vmax"], n+1)
        cut = v <= CONFIG["vcut"]
        M = np.exp(-0.5*v*v)/np.sqrt(2*np.pi)
        F, dF, W, dW = profile(v/delta)
        av = lambda g: 2*simpson(g*M, x=v)        # even integrands on v >= 0
        avc = lambda g: 2*simpson((g*M)[cut], x=v[cut])

        # even trial phi = F(u)/delta
        phi, dphi = F/delta, dF/delta**2
        t = av(v*v*phi)
        D_phi = nu*(av(dphi**2)-av((v*v-1)*phi)**2)
        Phi = tail_flux(v*(phi-t), M, v)
        Q = D_phi+k*k*avc(Phi**2)/nu
        lower = (av(phi)-t)**2/Q

        # odd trial psi = -W(u)/(k delta) + (alpha v + beta v^3)/k
        psi0, dpsi0 = -W/(k*delta), -dW/(k*delta**2)
        m1, m3 = k*av(v*psi0), k*av(v**3*psi0)
        alpha, beta = np.linalg.solve([[1, 3], [3, 15]], [1-m1, 1-m3])
        psi = psi0+(alpha*v+beta*v**3)/k
        dpsi = dpsi0+(alpha+3*beta*v*v)/k
        b = 1-k*v*psi
        D_psi = nu*(av(dpsi**2)-av(v*psi)**2)
        Phib = tail_flux(b, M, v)
        upper = D_psi+avc(Phib**2)/nu

        S0, sE = dougherty_moments((k/nu)**2)
        n1 = S0/((k/nu)**2*sE)/nu
        rows.append({
            "k": k, "delta": delta, "grid": n+1,
            "k_n1_exact": k*n1, "k_lower": k*lower, "k_upper": k*upper,
            "rel_gap_lower": (n1-lower)/n1, "rel_gap_upper": (upper-n1)/n1,
            "rel_dist_to_limit": (k*n1-C0)/C0,
            "constraint_residuals": [av(b), av(v*v*b)],
        })
    ks = np.array([r["k"] for r in rows])
    fit = {}
    for key in ("rel_gap_lower", "rel_gap_upper", "rel_dist_to_limit"):
        y = np.array([abs(r[key]) for r in rows])
        sel = ks >= 100
        fit[key] = float(np.polyfit(np.log(ks[sel]), np.log(y[sel]), 1)[0])
    return rows, fit


def main():
    if OUT.exists():
        sys.exit(f"refusing to overwrite {OUT}")
    t0 = time.time()
    rng = np.random.default_rng(CONFIG["seed"])
    split = splitting_check(rng)
    t1 = time.time()
    rates, pred = dougherty_rates()
    gaps, fit = trial_gaps()
    t2 = time.time()
    metrics = {
        "config": CONFIG,
        "A_splitting_identity_mc": split,
        "B_dougherty_exact": {"rows": rates, "predicted_first_coefficients": pred},
        "C_dougherty_1d_trials": {"rows": gaps, "loglog_slopes_k_ge_100": fit},
        "runtime_seconds": {"A": t1-t0, "B_C": t2-t1},
        "failures": [],
    }
    OUT.mkdir(parents=True)
    with open(OUT / "metrics.json", "w") as fh:
        json.dump(metrics, fh, indent=1)
    print(json.dumps(metrics, indent=1))


if __name__ == "__main__":
    main()
