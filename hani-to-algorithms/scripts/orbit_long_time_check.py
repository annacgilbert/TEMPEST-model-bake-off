#!/usr/bin/env python3
"""Monte Carlo check of docs/orbit_long_time_theorem.tex (numpy only).

Model (same as docs/orbit_decorrelation_theorem.tex):

    dY = w dtau,   dw = eps * G(Y, b) dtau,
    G(Y, b) = sum_k Re(f_k b_k exp(i k.Y)),
    db_k = -lambda_k b_k dtau + sqrt(2 gamma_k) dB_k   (stationary, E|b_k|^2 = 1),
    lambda_k = gamma_k + i (omega_k - k.v0).

What is tested
--------------
A. Scaling t = s N^{1/3}, eps = N^{-1/2}, fixed q, potential field:
   E exp(i q.Y_t) against
     (i)  the Gaussian law  K = exp(-eps^2 t^3 q.Dq / 3)        (old Theorem 1)
     (ii) the first correction (Theorem "first correction" of the new note)
          K * [1 + eps^2 t^2 (q.D2 q + i q.beta)/2
                 - (2i/15) eps^4 t^5 (Dq).grad_v(q.Dq)].
   Also: the joint characteristic function of (Y_t, w_t) at (q, pi N^{1/3})
   against the Kolmogorov law; E|w_t|^2 against 2 eps^2 t tr D (diffusive
   bound) and against the trivial bound (eps t)^2 E Gamma^2; and the mean
   velocity E w_t against eps^2 t beta.
B. Natural scaling at eps = 0.1 up to the kinetic time t = eps^-2:
   E exp(i kappa.Y_t / (eps t^{3/2})) against exp(-kappa.D kappa/3); shows
   where the Gaussian law fails.
C. As A for a non-potential field (beta != div D).
D. As A at N = 10^3 with half the time step (discretisation check).

A further quantity is recorded and labelled "heuristic": the next-order
offset of the mean velocity, E w_t ~ eps^2 (t beta - beta2).  It is not part
of any theorem in the note (see the Remark there) and is reported only to
explain the size of the residual after the first correction.

Numerical scheme
----------------
The mode amplitudes b_k and their time integrals over a step,
I1 = int_0^h b, I2 = int_0^h (h - s) b(s) ds, are sampled exactly (jointly
Gaussian).  The phase exp(i k.Y) is advanced inside a step to first order in
the Doppler shift k.w h.  Block D measures the step-size sensitivity.

Monte Carlo standard errors are reported separately from every theoretical
quantity.  All seeds derive from MASTER_SEED; chunks have independent seeds,
so the numbers do not depend on the number of worker processes.  Runtime is
about 40 s with 8 workers and about 3.5 min with --workers 1.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time

import numpy as np

MASTER_SEED = 20261124


# --------------------------------------------------------------------------
# Model and closed-form coefficients
# --------------------------------------------------------------------------
def make_model(kind: str = "potential") -> dict:
    k = np.array([[1.0, 0.0], [0.0, 1.0], [1.0, 1.0]])
    omega = np.array([0.6, -0.5, 0.5])
    gamma = np.array([0.8, 1.0, 0.7])
    phi = np.array([1.0, 0.8, 0.6])
    v0 = np.array([0.3, -0.2])
    if kind == "potential":
        f = (-1j * phi)[:, None] * k
    elif kind == "nonpotential":
        # generic complex polarisations, not parallel to k
        f = np.array([[0.9 - 0.3j, 0.4 + 0.5j],
                      [-0.3 + 0.6j, 0.7 - 0.2j],
                      [0.5 + 0.2j, -0.4 + 0.5j]])
    else:
        raise ValueError(kind)
    return dict(kind=kind, k=k, omega=omega, gamma=gamma, f=f, v0=v0)


def mu(model: dict, v: np.ndarray) -> np.ndarray:
    """Doppler-shifted rates mu_k = gamma_k + i (omega_k - k.v)."""
    return model["gamma"] + 1j * (model["omega"] - model["k"] @ v)


def D_matrix(model: dict, v: np.ndarray) -> np.ndarray:
    m = mu(model, v)
    f = model["f"]
    ff = np.real(f[:, :, None] * np.conj(f[:, None, :]))
    return 0.5 * np.einsum("k,kij->ij", np.real(1.0 / m), ff)


def coefficients(model: dict, q: np.ndarray) -> dict:
    """Closed-form coefficients at v0 entering the first correction."""
    v0, f, k = model["v0"], model["f"], model["k"]
    lam = mu(model, v0)
    D = D_matrix(model, v0)
    qf = f @ q
    d = float(q @ D @ q)
    m1 = float(0.5 * np.sum(np.abs(qf) ** 2 * np.real(1.0 / lam ** 2)))
    kfbar = np.einsum("kj,kj->k", k, np.conj(f))
    beta = 0.5 * np.real(np.einsum("k,ki->i", 1j * kfbar / lam ** 2, f))
    # grad_v (q.D(v)q), analytic: d/dv Re(1/mu) = Re(i k / mu^2)
    grad_d = 0.5 * np.einsum("k,ki->i", np.abs(qf) ** 2 * np.real(1j / lam ** 2), k)
    # finite-difference cross-check of the gradient and of div D
    hfd = 1e-5
    grad_fd = np.zeros(2)
    divD = np.zeros(2)
    for j in range(2):
        e = np.zeros(2)
        e[j] = hfd
        Dp, Dm = D_matrix(model, v0 + e), D_matrix(model, v0 - e)
        grad_fd[j] = (q @ Dp @ q - q @ Dm @ q) / (2 * hfd)
        divD += (Dp[:, j] - Dm[:, j]) / (2 * hfd)
    assert np.allclose(grad_fd, grad_d, atol=1e-7), (grad_fd, grad_d)
    skew = float((D @ q) @ grad_d)
    # heuristic next-order offset of the mean velocity (Remark in the note)
    beta2 = np.real(np.einsum("k,ki->i", 1j * kfbar / lam ** 3, f))
    # E Gamma^2 for the trivial bound |w| <= eps t Gamma, Gamma = sum |f_k||b_k|
    fn = np.linalg.norm(f, axis=1)
    M2sq = float(np.sum(fn ** 2) + (np.pi / 4.0) * (np.sum(fn) ** 2 - np.sum(fn ** 2)))
    return dict(D=D, d=d, m1=m1, beta=beta, q_beta=float(q @ beta),
                beta2=beta2, q_beta2=float(q @ beta2), M2sq=M2sq,
                grad_d=grad_d, skew=skew, divD=divD, trD=float(np.trace(D)))


def predict(model: dict, q: np.ndarray, eps: float, t: float) -> dict:
    c = coefficients(model, q)
    K = np.exp(-eps ** 2 * t ** 3 * c["d"] / 3.0)
    corr = (0.5 * eps ** 2 * t ** 2 * (c["m1"] + 1j * c["q_beta"])
            - (2j / 15.0) * eps ** 4 * t ** 5 * c["skew"])
    offset = -1j * eps ** 2 * t * c["q_beta2"]   # heuristic, not proved
    return dict(gauss=K, corrected=K * (1.0 + corr),
                corrected_offset=K * (1.0 + corr + offset))


def kolmogorov_joint(model: dict, q, p, eps: float, t: float) -> float:
    D = D_matrix(model, model["v0"])
    lam = t * (p @ D @ p) + t ** 2 * (p @ D @ q) + t ** 3 * (q @ D @ q) / 3.0
    return float(np.exp(-eps ** 2 * lam))


# --------------------------------------------------------------------------
# Exact one-step law of (b(h), I1, I2) for a complex OU mode
# --------------------------------------------------------------------------
def step_matrices(lam: np.ndarray, gam: np.ndarray, h: float):
    """Return E (K,3) and Cholesky factors L (K,3,3) with
    (b(h), I1, I2) = E * b(0) + L @ n,  n standard complex normal in C^3."""
    x, wq = np.polynomial.legendre.leggauss(60)
    u = 0.5 * h * (x + 1.0)
    wq = 0.5 * h * wq
    E = np.zeros((len(lam), 3), dtype=complex)
    L = np.zeros((len(lam), 3, 3), dtype=complex)
    for j, (l, g) in enumerate(zip(lam, gam)):
        def kern(uu):
            k0 = np.exp(-l * uu)
            k1 = (1.0 - k0) / l
            k2 = (uu - k1) / l
            return np.stack([k0, k1, k2])
        E[j] = kern(np.array([h]))[:, 0]
        ker = kern(u)
        C = 2.0 * g * np.einsum("iu,ju,u->ij", ker, np.conj(ker), wq)
        L[j] = np.linalg.cholesky(C)
    return E, L


OBS_NAMES = ("cf_Y", "cf_joint", "w2", "w_0", "w_1", "Y_0", "Y_1")


def _run_chunk(task):
    """Simulate one chunk of samples.  Returns (m, sums) where sums has shape
    (n_out, n_obs, 3) holding sum(z), sum(Re z ^2), sum(Im z ^2)."""
    kind, eps, h, out_steps, m, seed, qs, ps = task
    model = make_model(kind)
    kvec = model["k"].astype(np.float32)
    f = model["f"].astype(np.complex64)
    lam = mu(model, model["v0"])
    E, L = step_matrices(lam, model["gamma"], h)
    E = E.astype(np.complex64)
    L = L.astype(np.complex64)                              # lower triangular
    nK = len(lam)
    out_index = {s: i for i, s in enumerate(out_steps)}
    sums = np.zeros((len(out_steps), len(OBS_NAMES), 3), dtype=np.complex128)
    rng = np.random.default_rng(seed)
    rt2 = np.float32(np.sqrt(0.5))
    eps32, h32 = np.float32(eps), np.float32(h)
    b = (rng.standard_normal((m, nK, 2), dtype=np.float32)
         .view(np.complex64)[..., 0]) * rt2
    Y = np.zeros((m, 2), dtype=np.float32)
    w = np.zeros((m, 2), dtype=np.float32)
    for step in range(1, max(out_steps) + 1):
        n = (rng.standard_normal((3, m, nK, 2), dtype=np.float32)
             .view(np.complex64)[..., 0]) * rt2              # (3, m, K)
        I1 = E[:, 1] * b + L[:, 1, 0] * n[0] + L[:, 1, 1] * n[1]
        I2 = E[:, 2] * b + L[:, 2, 0] * n[0] + L[:, 2, 1] * n[1] + L[:, 2, 2] * n[2]
        b = E[:, 0] * b + L[:, 0, 0] * n[0]
        ph = np.exp(1j * (Y @ kvec.T))
        kw = w @ kvec.T
        c1 = ph * (I1 + 1j * kw * (h32 * I1 - I2))
        c2 = ph * I2
        Y = Y + h32 * w + eps32 * np.real(c2 @ f)
        w = w + eps32 * np.real(c1 @ f)
        if step in out_index:
            i = out_index[step]
            Yd, wd = Y.astype(np.float64), w.astype(np.float64)
            vals = (np.exp(1j * (Yd @ qs[i])),
                    np.exp(1j * (Yd @ qs[i] + wd @ ps[i])),
                    np.sum(wd ** 2, axis=1), wd[:, 0], wd[:, 1], Yd[:, 0], Yd[:, 1])
            for j, z in enumerate(vals):
                z = np.asarray(z, dtype=np.complex128)
                sums[i, j] = (z.sum(), np.sum(z.real ** 2), np.sum(z.imag ** 2))
    return m, sums


def simulate(pool, kind, eps, h, out_steps, n_samples, seed_seq, qs, ps,
             chunk=50_000):
    """Monte Carlo means and standard errors at the steps in out_steps.
    qs[i], ps[i]: wave vectors used at output i.  Chunks have independent,
    reproducible seeds; the result does not depend on the number of workers."""
    n_chunks = int(np.ceil(n_samples / chunk))
    sizes = [chunk] * (n_chunks - 1) + [n_samples - chunk * (n_chunks - 1)]
    tasks = [(kind, eps, h, list(out_steps), m, s, qs, ps)
             for m, s in zip(sizes, seed_seq.spawn(n_chunks))]
    parts = pool.map(_run_chunk, tasks) if pool is not None else [_run_chunk(t) for t in tasks]
    n = sum(p[0] for p in parts)
    tot = np.zeros_like(parts[0][1])
    for p in parts:           # fixed order: deterministic floating-point sum
        tot += p[1]
    out = []
    for i in range(len(out_steps)):
        d = {}
        for j, name in enumerate(OBS_NAMES):
            mean = tot[i, j, 0] / n
            vr = max(tot[i, j, 1].real / n - mean.real ** 2, 0.0)
            vi = max(tot[i, j, 2].real / n - mean.imag ** 2, 0.0)
            d[name] = dict(re=float(mean.real), im=float(mean.imag),
                           se_re=float(np.sqrt(vr / n)), se_im=float(np.sqrt(vi / n)),
                           n=int(n))
        out.append(d)
    return out


def cplx(z) -> dict:
    return dict(re=float(np.real(z)), im=float(np.imag(z)))


def as_c(d) -> complex:
    return complex(d["re"], d["im"])


def make_row(model, q, p, eps, t, h, n_samples, r) -> dict:
    """Compare one Monte Carlo output with the theoretical predictions."""
    c = coefficients(model, q)
    pr = predict(model, q, eps, t)
    meas = as_c(r["cf_Y"])
    Kj = kolmogorov_joint(model, q, p, eps, t)
    drift = eps ** 2 * (t * c["beta"])
    drift2 = eps ** 2 * (t * c["beta"] - c["beta2"])
    return dict(
        eps=eps, t=t, h=h, n_samples=n_samples, q=np.asarray(q).tolist(),
        measured=r["cf_Y"],
        predicted_gaussian=float(pr["gauss"]),
        predicted_corrected=cplx(pr["corrected"]),
        predicted_corrected_plus_heuristic_offset=cplx(pr["corrected_offset"]),
        err_gaussian=cplx(meas - pr["gauss"]),
        err_corrected=cplx(meas - pr["corrected"]),
        err_corrected_plus_heuristic_offset=cplx(meas - pr["corrected_offset"]),
        joint_p=np.asarray(p).tolist(), joint_measured=r["cf_joint"],
        joint_kolmogorov=Kj, joint_err=cplx(as_c(r["cf_joint"]) - Kj),
        w2_measured=r["w2"]["re"], w2_se=r["w2"]["se_re"],
        w2_diffusive=2 * eps ** 2 * t * c["trD"],
        w2_trivial_bound=(eps * t) ** 2 * c["M2sq"],
        mean_w_measured=[r["w_0"]["re"], r["w_1"]["re"]],
        mean_w_se=[r["w_0"]["se_re"], r["w_1"]["se_re"]],
        mean_w_leading=drift.tolist(),
        mean_w_with_heuristic_offset=drift2.tolist(),
        mean_Y_measured=[r["Y_0"]["re"], r["Y_1"]["re"]],
        mean_Y_se=[r["Y_0"]["se_re"], r["Y_1"]["se_re"]],
        mean_Y_leading=(eps ** 2 * t ** 2 * c["beta"] / 2).tolist(),
    )


# --------------------------------------------------------------------------
# Experiments
# --------------------------------------------------------------------------
def block_scaling(pool, kind, q, pi_vec, Ns, s_values, n_samples, h, seed_seq):
    model = make_model(kind)
    rows = []
    for N, ns, ss in zip(Ns, n_samples, seed_seq.spawn(len(Ns))):
        eps = N ** -0.5
        steps = [int(round(s * N ** (1.0 / 3.0) / h)) for s in s_values]
        times = [st * h for st in steps]
        p = pi_vec * N ** (1.0 / 3.0)
        res = simulate(pool, kind, eps, h, steps, ns, ss,
                       [q] * len(steps), [p] * len(steps))
        for s, t, r in zip(s_values, times, res):
            row = make_row(model, q, p, eps, t, h, ns, r)
            row.update(N=N, s_nominal=s)
            rows.append(row)
    return rows


def block_natural(pool, kind, kappa, eps, t_values, n_samples, h, seed_seq):
    model = make_model(kind)
    steps = [int(round(t / h)) for t in t_values]
    times = [st * h for st in steps]
    qs = [kappa / (eps * t ** 1.5) for t in times]
    ps = [np.zeros(2)] * len(times)
    res = simulate(pool, kind, eps, h, steps, n_samples, seed_seq, qs, ps)
    rows = []
    for t, qn, r in zip(times, qs, res):
        row = make_row(model, qn, np.zeros(2), eps, t, h, n_samples, r)
        row.update(kappa=kappa.tolist(), inv_t=1.0 / t, eps_sqrt_t=eps * np.sqrt(t))
        rows.append(row)
    return rows


def main() -> int:
    import multiprocessing as mp

    here = os.path.dirname(os.path.abspath(__file__))
    default_out = os.path.join(here, "..", "results", "orbit_long_time",
                               "orbit_long_time_check.json")
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out", default=default_out)
    ap.add_argument("--scale", type=float, default=1.0,
                    help="multiply all sample counts (use <1 for a quick smoke run)")
    ap.add_argument("--workers", type=int, default=min(8, os.cpu_count() or 1),
                    help="processes; the numbers do not depend on this")
    args = ap.parse_args()
    out = os.path.abspath(args.out)
    if os.path.exists(out):
        print(f"refusing to overwrite existing result file {out}", file=sys.stderr)
        return 1
    os.makedirs(os.path.dirname(out), exist_ok=True)

    t0 = time.time()
    root = np.random.SeedSequence(MASTER_SEED)
    sA, sB, sC, sD = root.spawn(4)
    sc = args.scale
    q = np.array([1.0, 0.5])
    pi_vec = np.array([0.5, -0.3])

    def n_(x):
        return max(int(x * sc), 1000)

    result = dict(
        script="hani-to-algorithms/scripts/orbit_long_time_check.py",
        note="hani-to-algorithms/docs/orbit_long_time_theorem.tex",
        master_seed=MASTER_SEED, numpy_version=np.__version__, sample_scale=sc,
        q=q.tolist(), pi=pi_vec.tolist(), models={})
    for name in ("potential", "nonpotential"):
        mdl = make_model(name)
        c = coefficients(mdl, q)
        result["models"][name] = dict(
            k=mdl["k"].tolist(), omega=mdl["omega"].tolist(),
            gamma=mdl["gamma"].tolist(), v0=mdl["v0"].tolist(),
            f_re=np.real(mdl["f"]).tolist(), f_im=np.imag(mdl["f"]).tolist(),
            D=c["D"].tolist(), q_D_q=c["d"], q_D2_q=c["m1"],
            beta=c["beta"].tolist(), div_D=c["divD"].tolist(), q_beta=c["q_beta"],
            beta2_heuristic=c["beta2"].tolist(),
            grad_v_qDq=c["grad_d"].tolist(), Dq_dot_grad=c["skew"], trD=c["trD"])

    pool = mp.Pool(args.workers) if args.workers > 1 else None
    try:
        hA = 0.2
        result["A_scaling_potential"] = block_scaling(
            pool, "potential", q, pi_vec, [10 ** 3, 10 ** 4, 10 ** 5], [1.0, 1.5],
            [n_(400_000), n_(400_000), n_(400_000)], hA, sA)
        print(f"block A done, {time.time() - t0:.1f}s", flush=True)
        result["B_natural_scaling"] = block_natural(
            pool, "potential", np.array([1.0, 0.5]), 0.1,
            [4.0, 9.0, 16.0, 25.0, 49.0, 100.0], n_(160_000), 0.1, sB)
        print(f"block B done, {time.time() - t0:.1f}s", flush=True)
        result["C_scaling_nonpotential"] = block_scaling(
            pool, "nonpotential", q, pi_vec, [10 ** 3, 10 ** 4], [1.0, 1.5],
            [n_(400_000), n_(400_000)], hA, sC)
        print(f"block C done, {time.time() - t0:.1f}s", flush=True)
        # D: step-size sensitivity at N = 10^3 (largest Doppler shift per step)
        result["D_step_size_check"] = block_scaling(
            pool, "potential", q, pi_vec, [10 ** 3], [1.0, 1.5],
            [n_(400_000)], 0.1, sD)
    finally:
        if pool is not None:
            pool.close()
            pool.join()
    result["runtime_seconds"] = time.time() - t0
    result["workers"] = args.workers
    with open(out, "w") as fh:
        json.dump(result, fh, indent=1)
    print(f"wrote {out}  ({result['runtime_seconds']:.1f}s)")

    def show(title, rows):
        print(title)
        for r in rows:
            m, pc = r["measured"], r["predicted_corrected"]
            po = r["predicted_corrected_plus_heuristic_offset"]
            print(f"  eps={r['eps']:.4g} t={r['t']:6.2f}  meas={m['re']:+.4f}{m['im']:+.4f}i"
                  f" (se {m['se_re']:.4f},{m['se_im']:.4f})"
                  f"  gauss={r['predicted_gaussian']:.4f}"
                  f"  corr={pc['re']:+.4f}{pc['im']:+.4f}i"
                  f"  corr+off={po['re']:+.4f}{po['im']:+.4f}i"
                  f"  joint={r['joint_measured']['re']:+.4f} vs {r['joint_kolmogorov']:.4f}"
                  f"  w2/diff={r['w2_measured'] / r['w2_diffusive']:.3f}")

    show("A (potential field, t = s N^{1/3})", result["A_scaling_potential"])
    show("B (natural scaling, eps = 0.1)", result["B_natural_scaling"])
    show("C (non-potential field)", result["C_scaling_nonpotential"])
    show("D (as A at N = 10^3 with half the step)", result["D_step_size_check"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
