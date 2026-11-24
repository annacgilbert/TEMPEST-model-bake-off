#!/usr/bin/env python3
"""Monte Carlo check of docs/orbit_backreaction_theorem.tex (numpy only).

Model (dressed variables, lab frame), for k in K, eps = N^{-1/2}:

    dx = v dt,
    dv = eps * sum_k Re(f_k a_k e^{i k.x}) dt,          f_k = -i c_k k,
    da_k = [-(gamma_k + i omega_k) a_k
            - i eps kappa (k.v) conj(c_k)/(2T) e^{-i k.x}] dt
           + sqrt(2 gamma_k) dB_k.

kappa = 1 is the Hamiltonian particle-field model with a thermostat on the
field (written in the dressed variable); kappa = 0 is the prescribed-field
model of orbit_decorrelation_theorem.tex.  Initial data: a_k(0) standard
complex Gaussian, independent over k ("dressed" start).

Numerical method.  a_k = ahat_k + eps r_k exactly, where ahat_k is the
stationary Ornstein-Uhlenbeck process driven by the same noise (sampled
exactly on the grid) and r_k solves a pathwise ODE.  (x, v, r) are advanced
by a kick-drift-kick step with an exponential integrator for r.  The runs
with kappa = 0 and kappa = 1 share ahat (common random numbers).

Checks.
 (a) mean velocity drift:  E w_t ~ eps^2 t m(v0),
       m = div_v D - kappa D v0 / T                        (Theorem B),
     separately for kappa = 0 (div D), and for the paired difference
     kappa = 1 minus kappa = 0 (polarization drag -D v0/T).
 (b) E exp(i q.Y_t) ~ exp(-s^3 q.Dq/3) at t = s N^{1/3} for both kappa
     (Theorem A), and E Y_t ~ eps^2 t^2 m/2.
 (c) time-step error: paired comparison of step h and step 2h on the same
     Ornstein-Uhlenbeck paths.

Three errors are reported separately: Monte Carlo standard error, time-step
error (c), and the theoretical error terms of the theorems (not estimated
here; see the note).

Usage:  python orbit_backreaction_check.py [--out DIR] [--quick]
Refuses to overwrite an existing results file.
"""
import argparse
import json
import os
import sys
import time

import numpy as np

SEED = 20261124

# ---------------------------------------------------------------- parameters
K = np.array([[1.0, 0.0], [0.0, 1.0], [1.0, 1.0], [1.0, -1.0], [2.0, 1.0]])
C = np.array([0.9, 0.8 * np.exp(0.7j), 0.6 * np.exp(-1.1j), 0.5, 0.35j])
GAMMA = np.array([0.6, 0.8, 0.7, 0.9, 1.0])
OMEGA = np.array([1.3, -0.4, 1.9, 0.2, 2.6])
TEMP = 0.5
X0 = np.array([0.3, -0.2])
V0 = np.array([0.8, 0.3])
Q = np.array([1.0, 0.5])


def coefficients(v):
    """D(v), div_v D(v), and D(v) v / T from the closed formulas of the note."""
    delta = OMEGA - K @ v
    den = GAMMA**2 + delta**2
    c2 = np.abs(C) ** 2
    re_inv = GAMMA / den                       # Re(1/lambda_k(v))
    D = 0.5 * np.einsum("k,ki,kj->ij", c2 * re_inv, K, K)
    k2 = np.sum(K**2, axis=1)
    divD = np.einsum("k,ki->i", c2 * k2 * GAMMA * delta / den**2, K)
    return D, divD, D @ v / TEMP


def divD_fd(v, h=1e-5):
    """Finite-difference divergence of D, an independent check of divD."""
    out = np.zeros(2)
    for j in range(2):
        e = np.zeros(2)
        e[j] = h
        out += (coefficients(v + e)[0][:, j] - coefficients(v - e)[0][:, j]) / (2 * h)
    return out


def drift(v, kappa):
    """m_kappa(v) = div D(v) - kappa D(v) v / T."""
    _, dv, fr = coefficients(v)
    return dv - kappa * fr


def second_order(v, kappa, h=1e-3):
    """L_kappa m_kappa at v by central differences, where
    L_kappa = D_ij d_i d_j + m_kappa . grad.  Used only for the heuristic
    estimate  E w_t ~ eps^2 t m + (eps^4 t^2 / 2) L m  of the theoretical
    error; this second term is not proved in the note."""
    D = coefficients(v)[0]
    m0 = drift(v, kappa)
    e = np.eye(2) * h
    grad = np.array([(drift(v + e[j], kappa) - drift(v - e[j], kappa)) / (2 * h) for j in range(2)])
    out = m0 @ grad
    for i in range(2):
        for j in range(2):
            d2 = (drift(v + e[i] + e[j], kappa) - drift(v + e[i] - e[j], kappa)
                  - drift(v - e[i] + e[j], kappa) + drift(v - e[i] - e[j], kappa)) / (4 * h * h)
            out = out + D[i, j] * d2
    return out


def force(x, a):
    """sum_k Re(f_k a_k e^{i k.x}), f_k = -i c_k k; shape (n, 2)."""
    amp = (-1j * C) * a * np.exp(1j * (x @ K.T))
    return amp.real @ K


def simulate(eps, t_records, h, n, rng, variants):
    """Simulate n samples.  variants: list of (kappa, stride).  A variant with
    stride m advances the particle with step m*h, using the common
    Ornstein-Uhlenbeck path sampled every h.  Returns, per record time and
    variant, the arrays w (n,2) and Y (n,2); also the first-iterate control
    variate w1 (exact mean zero), computed with the trapezoid rule at step h.
    """
    lam0 = GAMMA + 1j * OMEGA
    nk = len(GAMMA)
    steps_rec = [int(round(t / h)) for t in t_records]
    nsteps = max(steps_rec)
    dec = np.exp(-lam0 * h)
    sig = np.sqrt(1.0 - np.exp(-2.0 * GAMMA * h))
    ahat = (rng.standard_normal((n, nk)) + 1j * rng.standard_normal((n, nk))) / np.sqrt(2)
    st = []
    for kappa, stride in variants:
        dt = stride * h
        st.append(dict(kappa=kappa, stride=stride, dt=dt,
                       x=np.tile(X0, (n, 1)), v=np.tile(V0, (n, 1)),
                       r=np.zeros((n, nk), dtype=complex),
                       edec=np.exp(-lam0 * dt), phi=(1 - np.exp(-lam0 * dt)) / lam0))
    # first iterate along the ballistic orbit
    w1 = np.zeros((n, 2))
    g_prev = force(np.tile(X0, (n, 1)), ahat)
    f_prev = [force(s["x"], ahat + eps * s["r"]) for s in st]
    out = {}
    for step in range(1, nsteps + 1):
        ahat_new = dec * ahat + sig * (
            rng.standard_normal((n, nk)) + 1j * rng.standard_normal((n, nk))) / np.sqrt(2)
        t_new = step * h
        g_new = force(X0 + V0 * t_new, ahat_new)
        w1 += 0.5 * h * eps * (g_prev + g_new)
        g_prev = g_new
        for i, s in enumerate(st):
            if step % s["stride"]:
                continue
            dt = s["dt"]
            s["v"] += 0.5 * dt * eps * f_prev[i]
            xm = s["x"] + 0.5 * dt * s["v"]
            s["x"] += dt * s["v"]
            if s["kappa"] != 0.0:
                src = (-1j * s["kappa"] / (2 * TEMP)) * (s["v"] @ K.T) * np.conj(C) \
                    * np.exp(-1j * (xm @ K.T))
                s["r"] = s["edec"] * s["r"] + s["phi"] * src
            f_new = force(s["x"], ahat_new + eps * s["r"])
            s["v"] += 0.5 * dt * eps * f_new
            f_prev[i] = f_new
        ahat = ahat_new
        if step in steps_rec:
            t = step * h
            out[t_records[steps_rec.index(step)]] = dict(
                w=[s["v"] - V0 for s in st],
                Y=[s["x"] - X0 - V0 * t for s in st],
                w1=w1.copy())
    return out


def mean_se(a):
    a = np.asarray(a)
    return a.mean(axis=0), a.std(axis=0, ddof=1) / np.sqrt(a.shape[0])


def cv_mean_se(a, cvar):
    """Mean of a with the zero-mean control variate cvar (per component,
    regression coefficient estimated from the same sample)."""
    m = np.zeros(a.shape[1])
    se = np.zeros(a.shape[1])
    for j in range(a.shape[1]):
        cv = np.cov(a[:, j], cvar[:, j])
        b = cv[0, 1] / cv[1, 1]
        res = a[:, j] - b * cvar[:, j]
        m[j] = res.mean()
        se[j] = res.std(ddof=1) / np.sqrt(len(res))
    return m, se


def lst(a):
    return [float(u) for u in np.asarray(a).ravel()]


def main():
    ap = argparse.ArgumentParser()
    here = os.path.dirname(os.path.abspath(__file__))
    ap.add_argument("--out", default=os.path.join(here, "..", "results", "orbit_backreaction"))
    ap.add_argument("--quick", action="store_true", help="small sample smoke run")
    args = ap.parse_args()
    outfile = os.path.join(args.out, "orbit_backreaction_check.json")
    if os.path.exists(outfile):
        sys.exit("refusing to overwrite " + outfile)
    os.makedirs(args.out, exist_ok=True)

    t_start = time.time()
    rng = np.random.default_rng(SEED)
    scale = 0.05 if args.quick else 1.0
    D, divD, fric = coefficients(V0)
    qDq = float(Q @ D @ Q)
    res = dict(seed=SEED, quick=bool(args.quick),
               parameters=dict(K=K.tolist(), c_abs=lst(np.abs(C)), c_arg=lst(np.angle(C)),
                               gamma=lst(GAMMA), omega=lst(OMEGA), T=TEMP,
                               x0=lst(X0), v0=lst(V0), q=lst(Q)),
               formulas=dict(D=D.tolist(), divD=lst(divD), divD_finite_difference=lst(divD_fd(V0)),
                             D_v0_over_T=lst(fric), q_D_q=qDq,
                             m_kappa0=lst(divD), m_kappa1=lst(divD - fric)))
    print("D =", D.tolist())
    print("div D =", divD, " (finite difference:", divD_fd(V0), ")")
    print("D v0/T =", fric, "  q.Dq =", qDq)

    # ---------------- (a) mean velocity drift
    so0 = second_order(V0, 0.0)
    sod = second_order(V0, 1.0) - so0
    res["formulas"]["second_order_heuristic_kappa0"] = lst(so0)
    res["formulas"]["second_order_heuristic_paired_diff"] = lst(sod)
    res["a_mean_drift"] = []
    for eps, n0 in [(0.02, 100000), (0.01, 50000)]:
        h = 0.05
        n = int(n0 * scale)
        trec = [10.0, 20.0, 30.0, 40.0]
        sim = simulate(eps, trec, h, n, rng, [(0.0, 1), (1.0, 1)])
        rows = []
        for t in trec:
            w0, w1k = sim[t]["w"]
            cv = sim[t]["w1"]
            m0, s0 = mean_se(w0)
            m0c, s0c = cv_mean_se(w0, cv)
            md, sd = mean_se(w1k - w0)
            e2t = eps**2 * t
            rows.append(dict(t=t, eps=eps, n=n, h=h,
                             kappa0_raw=lst(m0 / e2t), kappa0_raw_se=lst(s0 / e2t),
                             kappa0_cv=lst(m0c / e2t), kappa0_cv_se=lst(s0c / e2t),
                             predicted_kappa0=lst(divD),
                             heuristic_second_order_kappa0=lst(divD + 0.5 * e2t * so0),
                             paired_diff=lst(md / e2t), paired_diff_se=lst(sd / e2t),
                             predicted_diff=lst(-fric),
                             heuristic_second_order_diff=lst(-fric + 0.5 * e2t * sod)))
            print("eps=%.2f t=%5.1f  E w/(eps^2 t), kappa=0 (cv): %s +- %s | pred %s"
                  % (eps, t, m0c / e2t, s0c / e2t, divD))
            print("         paired kappa1-kappa0: %s +- %s | pred %s | with heuristic 2nd order %s"
                  % (md / e2t, sd / e2t, -fric, -fric + 0.5 * e2t * sod))
        # increment between t=10 and t=40 (removes the O(eps^2) transient constant)
        wa, wb = sim[trec[0]], sim[trec[-1]]
        dt_ = trec[-1] - trec[0]
        inc0 = wb["w"][0] - wa["w"][0]
        ms, ss = cv_mean_se(inc0, wb["w1"] - wa["w1"])
        md, sd = mean_se((wb["w"][1] - wb["w"][0]) - (wa["w"][1] - wa["w"][0]))
        so_fac = 0.5 * eps**2 * (trec[-1] ** 2 - trec[0] ** 2) / dt_
        slope = dict(t_from=trec[0], t_to=trec[-1],
                     kappa0_slope=lst(ms / (eps**2 * dt_)), kappa0_slope_se=lst(ss / (eps**2 * dt_)),
                     predicted_kappa0=lst(divD),
                     heuristic_second_order_kappa0=lst(divD + so_fac * so0),
                     paired_diff_slope=lst(md / (eps**2 * dt_)),
                     paired_diff_slope_se=lst(sd / (eps**2 * dt_)),
                     predicted_diff=lst(-fric),
                     heuristic_second_order_diff=lst(-fric + so_fac * sod))
        print("  slope kappa=0:", ms / (eps**2 * dt_), "+-", ss / (eps**2 * dt_), " pred", divD,
              " 2nd order", divD + so_fac * so0)
        print("  slope paired :", md / (eps**2 * dt_), "+-", sd / (eps**2 * dt_), " pred", -fric,
              " 2nd order", -fric + so_fac * sod)
        res["a_mean_drift"].append(dict(eps=eps, rows=rows, slope=slope))
        del sim

    # ---------------- (b) the N^{1/3} law with and without back-reaction
    rows = []
    for N in [1e3, 1e4, 1e5]:
        eps = N ** -0.5
        svals = [1.0, 1.5]
        h = 0.05
        trec = [round(s * N ** (1 / 3) / h) * h for s in svals]
        n = int(40000 * scale)
        sim = simulate(eps, trec, h, n, rng, [(0.0, 1), (1.0, 1)])
        for s, t in zip(svals, trec):
            Y0, Y1 = sim[t]["Y"]
            p0 = np.exp(1j * (Y0 @ Q))
            p1 = np.exp(1j * (Y1 @ Q))
            pred = float(np.exp(-eps**2 * t**3 * qDq / 3))
            se = lambda z: float(np.sqrt((z.real.var(ddof=1) + z.imag.var(ddof=1)) / len(z)))
            dY, dYse = mean_se(Y1 - Y0)
            EY0, EY0se = mean_se(Y0)
            dphi = p1 - p0
            rows.append(dict(N=N, s=s, t=t, n=n, h=h, predicted=pred,
                             kappa0_re=float(p0.real.mean()), kappa0_im=float(p0.imag.mean()),
                             kappa0_se=se(p0),
                             kappa1_re=float(p1.real.mean()), kappa1_im=float(p1.imag.mean()),
                             kappa1_se=se(p1),
                             paired_diff_re=float(dphi.real.mean()), paired_diff_im=float(dphi.imag.mean()),
                             paired_diff_se=se(dphi),
                             heuristic_diff_im=float(-pred * eps**2 * t**2 * (Q @ fric) / 2),
                             EY_kappa0=lst(EY0), EY_kappa0_se=lst(EY0se),
                             EY_kappa0_predicted=lst(eps**2 * t**2 * divD / 2),
                             EY_paired_diff=lst(dY), EY_paired_diff_se=lst(dYse),
                             EY_paired_diff_predicted=lst(-eps**2 * t**2 * fric / 2)))
            print("N=%.0e s=%.1f t=%6.2f pred %.4f | k0 %.4f%+.4fi | k1 %.4f%+.4fi | se %.4f | "
                  "paired diff %.5f%+.5fi +- %.5f (heur. Im %.5f)"
                  % (N, s, t, pred, p0.real.mean(), p0.imag.mean(), p1.real.mean(), p1.imag.mean(),
                     se(p0), dphi.real.mean(), dphi.imag.mean(), se(dphi),
                     -pred * eps**2 * t**2 * (Q @ fric) / 2))
            print("      E(Y1-Y0) =", dY, "+-", dYse, " pred", -eps**2 * t**2 * fric / 2)
        del sim
    res["b_char_function"] = dict(rows=rows)

    # ---------------- (c) time-step error, paired on the same OU paths
    eps, h = 0.02, 0.05
    n = int(20000 * scale)
    trec = [20.0, 40.0]
    sim = simulate(eps, trec, h, n, rng, [(0.0, 1), (1.0, 1), (0.0, 2), (1.0, 2)])
    rows = []
    for t in trec:
        w = sim[t]["w"]
        Y = sim[t]["Y"]
        e2t = eps**2 * t
        d0, d0se = mean_se(w[2] - w[0])
        dd, ddse = mean_se((w[3] - w[2]) - (w[1] - w[0]))
        c0 = np.exp(1j * (Y[2] @ Q)) - np.exp(1j * (Y[0] @ Q))
        rows.append(dict(t=t, eps=eps, n=n, h=h,
                         drift_kappa0_step2h_minus_h=lst(d0 / e2t), se=lst(d0se / e2t),
                         paired_diff_step2h_minus_h=lst(dd / e2t), paired_diff_se=lst(ddse / e2t),
                         charfn_kappa0_step2h_minus_h=[float(c0.real.mean()), float(c0.imag.mean())],
                         charfn_se=float(np.sqrt((c0.real.var() + c0.imag.var()) / n))))
        print("dt check t=%4.1f: drift/(eps^2 t) (2h)-(h), kappa0: %s +- %s ; paired: %s +- %s"
              % (t, d0 / e2t, d0se / e2t, dd / e2t, ddse / e2t))
    res["c_time_step"] = dict(rows=rows)

    res["runtime_seconds"] = time.time() - t_start
    with open(outfile, "w") as fh:
        json.dump(res, fh, indent=1)
    print("wrote", outfile, " runtime %.1f s" % res["runtime_seconds"])


if __name__ == "__main__":
    main()
