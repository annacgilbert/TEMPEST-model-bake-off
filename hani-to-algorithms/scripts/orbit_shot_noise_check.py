#!/usr/bin/env python3
"""Monte Carlo check of docs/orbit_shot_noise_theorem.tex.

A tagged particle on the torus T = R/2 pi Z (d = 1) moves in the field of N
independent free-streaming gas particles,

    x'' = -(1/N) sum_j phi'(x - x_j - v_j tau),
    phi(x) = sum_{k in K} phi_k exp(i k x),  K = {+-1, +-2},

with x_j uniform on T and v_j standard normal.  The gas is simulated
exactly (it is free); only the tagged orbit is discretized (velocity Verlet).

Quantities compared with the note:

* E exp(i q Y_t), Y_t = x_t - x_0 - v_0 t, at t = s N^{1/3}, against the
  Landau prediction exp(-s^3 q^2 D(v_0) / 3),
  D(v_0) = pi sum_k |k| phi_k^2 M(v_0)            (Theorem 2 of the note);
* the same for the first iterate Y^(1), against exp(-V_N(t) q^2 / 2) with the
  exact finite-N variance V_N(t) computed by quadrature (Proposition 6);
* E|Y - Y^(1)| against the s^3 scaling of Theorem 7;
* the correlation of the departures of two tagged particles: same velocity at
  separation pi/2 (resonant; compared with a direct simulation of the limiting
  two-point diffusion of Theorem 9) and velocities differing by 1
  (non-resonant; predicted asymptotically independent).

Sources of error are reported separately: Monte Carlo standard errors (over
independent gases), the time-step error (rerun with dt/2 on the same gases),
and the finite-N error, which is what the theorems bound.

numpy only.  Run:  python orbit_shot_noise_check.py
Writes results/orbit_shot_noise/orbit_shot_noise_check.json (refuses to
overwrite an existing file).
"""
from __future__ import annotations

import json
import math
import sys
import time
from pathlib import Path

import numpy as np

SEED = 20261124
PHI = {1: 1.0, 2: 0.5}          # phi_k = phi_{-k}, k = 1, 2
V0 = 0.5                        # tagged velocity
QS = (1.0, 2.0)
S_VALUES = (0.5, 1.0, 1.5)
SEP = math.pi / 2               # separation of the resonant pair
DV = 1.0                        # velocity offset of the non-resonant particle
OFFSETS = (0.0, 0.5 * math.pi, math.pi, 1.5 * math.pi)  # resonant tagged set
# (N, number of independent gases, target time step)
RUNS = ((250, 40000, 0.1), (2000, 20000, 0.1), (16000, 3000, 0.1), (128000, 240, 0.1))
DT_CHECK = ((250, 40000), (2000, 4000))     # reruns with dt/2, same gases
CHUNK_ELEMS = 1_000_000


def maxwellian(v: float) -> float:
    return math.exp(-0.5 * v * v) / math.sqrt(2.0 * math.pi)


def landau_D(v0: float) -> float:
    """D(v0) = pi sum_{k in K} |k| phi_k^2 M(v0), K = {+-1, +-2}."""
    return math.pi * sum(2.0 * k * p * p for k, p in PHI.items()) * maxwellian(v0)


def first_iterate_variance(t: float, n_gas: int, v0: float) -> float:
    """Exact Var(Y^(1)_t) = (1/N) sum_k k^2 phi_k^2 E|I_t(k(v - v0))|^2,
    I_t(w) = int_0^t (t - s) exp(-i w s) ds, by quadrature in v."""
    v = np.linspace(-9.0, 9.0, 720001)
    dv = v[1] - v[0]
    dens = np.exp(-0.5 * v * v) / math.sqrt(2.0 * math.pi)
    total = 0.0
    for k, p in PHI.items():
        w = k * (v - v0)
        small = np.abs(w * t) < 1e-4
        ws = np.where(small, 1.0, w)
        # |I_t(w)|^2 = [ (t w - sin(t w))^2 + (1 - cos(t w))^2 ] / w^4
        val = ((t * ws - np.sin(t * ws)) ** 2 + (1 - np.cos(t * ws)) ** 2) / ws**4
        val = np.where(small, t**4 / 4.0, val)
        total += 2.0 * k * k * p * p * float(np.sum(dens * val) * dv)
    return total / n_gas


def force(x: np.ndarray, a1: np.ndarray, a2: np.ndarray, n_gas: int) -> np.ndarray:
    """-(1/N) sum_j phi'(x - x_j(tau)) given a_k = sum_j exp(-i k x_j(tau)).

    x has shape (gases, tagged); a_k has shape (gases,)."""
    e1 = np.exp(1j * x)
    acc = PHI[1] * (a1[:, None] * e1).imag + 2.0 * PHI[2] * (a2[:, None] * e1 * e1).imag
    return (2.0 / n_gas) * acc


def simulate(n_gas: int, n_rep: int, dt_target: float, rng: np.random.Generator):
    """Returns dict of arrays indexed [record, gas, tagged]."""
    t_max = max(S_VALUES) * n_gas ** (1.0 / 3.0)
    n_rec = len(S_VALUES)
    base = S_VALUES[0]
    mult = [int(round(s / base)) for s in S_VALUES]
    assert all(abs(m * base - s) < 1e-12 for m, s in zip(mult, S_VALUES))
    steps_unit = int(math.ceil(base * n_gas ** (1.0 / 3.0) / dt_target))
    dt = base * n_gas ** (1.0 / 3.0) / steps_unit
    rec_steps = [m * steps_unit for m in mult]
    n_steps = rec_steps[-1]
    assert abs(n_steps * dt - t_max) < 1e-9

    x_init = np.array(list(OFFSETS) + [0.0])
    v_init = np.array([V0] * len(OFFSETS) + [V0 + DV])
    n_tag = len(x_init)
    out_Y = np.empty((n_rec, n_rep, n_tag))
    out_Y1 = np.empty((n_rec, n_rep, n_tag))
    out_w = np.empty((n_rec, n_rep, n_tag))

    chunk = max(1, CHUNK_ELEMS // n_gas)
    done = 0
    while done < n_rep:
        g = min(chunk, n_rep - done)
        xj = rng.uniform(0.0, 2.0 * math.pi, size=(g, n_gas))
        vj = rng.standard_normal(size=(g, n_gas))
        phase = np.exp(-1j * xj).astype(np.complex128)
        rot = np.exp(-1j * vj * dt).astype(np.complex128)
        del xj, vj
        x = np.tile(x_init, (g, 1))
        v = np.tile(v_init, (g, 1))
        # first iterate: force evaluated on the ballistic orbit
        y1 = np.zeros((g, n_tag))
        w1 = np.zeros((g, n_tag))
        a1 = phase.sum(axis=1)
        a2 = (phase * phase).sum(axis=1)
        f = force(x, a1, a2, n_gas)
        f1 = force(np.tile(x_init, (g, 1)), a1, a2, n_gas)
        rec = 0
        for n in range(1, n_steps + 1):
            v += 0.5 * dt * f
            x += dt * v
            w1 += 0.5 * dt * f1
            y1 += dt * w1
            phase *= rot
            a1 = phase.sum(axis=1)
            a2 = (phase * phase).sum(axis=1)
            tau = n * dt
            f = force(x, a1, a2, n_gas)
            f1 = force(x_init[None, :] + v_init[None, :] * tau, a1, a2, n_gas)
            v += 0.5 * dt * f
            w1 += 0.5 * dt * f1
            if n == rec_steps[rec]:
                out_Y[rec, done:done + g] = x - x_init[None, :] - v_init[None, :] * tau
                out_Y1[rec, done:done + g] = y1
                out_w[rec, done:done + g] = v - v_init[None, :]
                rec += 1
        done += g
    return {"Y": out_Y, "Y1": out_Y1, "w": out_w, "dt": dt, "n_steps": n_steps}


def mean_se(per_gas: np.ndarray):
    return float(per_gas.mean()), float(per_gas.std(ddof=1) / math.sqrt(len(per_gas)))


def corr_se(a: np.ndarray, b: np.ndarray, n_batch: int = 20):
    """Correlation coefficient with a batch (jackknife-free) standard error."""
    c = float(np.corrcoef(a, b)[0, 1])
    idx = np.array_split(np.arange(len(a)), n_batch)
    cs = np.array([np.corrcoef(a[i], b[i])[0, 1] for i in idx])
    return c, float(cs.std(ddof=1) / math.sqrt(n_batch))


def limit_pair_correlation(s: float, rng: np.random.Generator,
                           n_paths: int = 200_000, n_steps: int = 200):
    """Euler--Maruyama for the limiting two-point motion (Theorem 9), resonant
    pair at separation SEP:  dY^p = lam W^p dsig,
    dW^p = sum_{k>0} 2 Re( f_k exp(i k (x_p + Y^p)) dB_k ),
    f_k = -i k phi_k, E|dB_k|^2 = 2 pi M(v0)/k dsig, lam = s^{3/2}."""
    lam = s ** 1.5
    h = 1.0 / n_steps
    xp = np.array([0.0, SEP])
    Y = np.zeros((n_paths, 2))
    W = np.zeros((n_paths, 2))
    ks = sorted(PHI)
    for _ in range(n_steps):
        dW = np.zeros((n_paths, 2))
        for k in ks:
            sd = math.sqrt(2.0 * math.pi * maxwellian(V0) / k * h / 2.0)
            dB = sd * (rng.standard_normal(n_paths) + 1j * rng.standard_normal(n_paths))
            fk = -1j * k * PHI[k]
            dW += 2.0 * (fk * np.exp(1j * k * (xp[None, :] + Y)) * dB[:, None]).real
        Y += lam * W * h          # Y uses W before the kick (Ito; Y is C^1)
        W += dW
    c, se = corr_se(Y[:, 0], Y[:, 1])
    return c, se, float(Y[:, 0].var())


def main() -> int:
    here = Path(__file__).resolve().parent
    out_dir = here.parent / "results" / "orbit_shot_noise"
    out_path = out_dir / "orbit_shot_noise_check.json"
    if out_path.exists():
        print(f"refusing to overwrite {out_path}", file=sys.stderr)
        return 1
    out_dir.mkdir(parents=True, exist_ok=True)

    t_start = time.time()
    D = landau_D(V0)
    n_res = len(OFFSETS)
    results = {
        "description": "tagged particle in a free gas, d=1; see docs/orbit_shot_noise_theorem.tex",
        "seed": SEED,
        "phi": {str(k): p for k, p in PHI.items()},
        "v0": V0,
        "landau_D": D,
        "s_values": list(S_VALUES),
        "q_values": list(QS),
        "rows": [],
        "pair_rows": [],
        "dt_check": [],
        "limit_pair": [],
    }

    sims = {}
    for i, (n_gas, n_rep, dt_target) in enumerate(RUNS):
        rng = np.random.default_rng([SEED, n_gas])
        t0 = time.time()
        sim = simulate(n_gas, n_rep, dt_target, rng)
        sims[n_gas] = sim
        print(f"N={n_gas}: {n_rep} gases, dt={sim['dt']:.4f}, "
              f"{sim['n_steps']} steps, {time.time() - t0:.1f}s", flush=True)
        for r, s in enumerate(S_VALUES):
            t = s * n_gas ** (1.0 / 3.0)
            Y = sim["Y"][r][:, :n_res]
            Y1 = sim["Y1"][r][:, :n_res]
            w = sim["w"][r][:, :n_res]
            V_exact = first_iterate_variance(t, n_gas, V0)
            var_Y = mean_se((Y ** 2).mean(axis=1))
            var_Y1 = mean_se((Y1 ** 2).mean(axis=1))
            var_w = mean_se((w ** 2).mean(axis=1))
            diff = mean_se(np.abs(Y - Y1).mean(axis=1))
            for q in QS:
                re = mean_se(np.cos(q * Y).mean(axis=1))
                im = mean_se(np.sin(q * Y).mean(axis=1))
                re1 = mean_se(np.cos(q * Y1).mean(axis=1))
                results["rows"].append({
                    "N": n_gas, "s": s, "t": t, "q": q, "gases": n_rep,
                    "dt": sim["dt"],
                    "cf_re": re[0], "cf_re_se": re[1],
                    "cf_im": im[0], "cf_im_se": im[1],
                    "landau_prediction": math.exp(-s ** 3 * q * q * D / 3.0),
                    "first_iterate_cf_re": re1[0], "first_iterate_cf_re_se": re1[1],
                    "first_iterate_gaussian": math.exp(-0.5 * q * q * V_exact),
                    "var_Y": var_Y[0], "var_Y_se": var_Y[1],
                    "var_Y_landau": 2.0 * s ** 3 * D / 3.0,
                    "var_Y1": var_Y1[0], "var_Y1_se": var_Y1[1],
                    "var_Y1_exact": V_exact,
                    "var_w_times_N_over_t": var_w[0] * n_gas / t,
                    "var_w_times_N_over_t_se": var_w[1] * n_gas / t,
                    "two_D": 2.0 * D,
                    "mean_abs_Y_minus_Y1": diff[0], "mean_abs_Y_minus_Y1_se": diff[1],
                })
            # two tagged particles
            YA, YB, YC = sim["Y"][r][:, 0], sim["Y"][r][:, 1], sim["Y"][r][:, n_res]
            c_res = corr_se(YA, YB)
            c_non = corr_se(YA, YC)
            results["pair_rows"].append({
                "N": n_gas, "s": s, "gases": n_rep,
                "corr_resonant_sep_pi_over_2": c_res[0], "corr_resonant_se": c_res[1],
                "corr_nonresonant_dv_1": c_non[0], "corr_nonresonant_se": c_non[1],
            })

    # time-step error: same gases (same seed), dt halved
    for n_gas, n_rep in DT_CHECK:
        rng = np.random.default_rng([SEED, n_gas])
        t0 = time.time()
        fine = simulate(n_gas, n_rep, 0.05, rng)
        coarse = sims[n_gas]
        print(f"dt check N={n_gas}: {n_rep} gases, dt={fine['dt']:.4f}, "
              f"{time.time() - t0:.1f}s", flush=True)
        for r, s in enumerate(S_VALUES):
            Yc = coarse["Y"][r][:n_rep, :n_res]
            Yf = fine["Y"][r][:, :n_res]
            for q in QS:
                d = mean_se((np.cos(q * Yc) - np.cos(q * Yf)).mean(axis=1))
                results["dt_check"].append({
                    "N": n_gas, "s": s, "q": q, "gases": n_rep,
                    "dt_coarse": coarse["dt"], "dt_fine": fine["dt"],
                    "cf_re_coarse_minus_fine": d[0], "se": d[1],
                    "rms_Y_coarse_minus_fine": float(np.sqrt(((Yc - Yf) ** 2).mean())),
                })

    rng = np.random.default_rng([SEED, 7])
    for s in S_VALUES:
        c, se, vy = limit_pair_correlation(s, rng)
        results["limit_pair"].append({
            "s": s, "corr_resonant_sep_pi_over_2": c, "se": se,
            "var_Y": vy, "var_Y_landau": 2.0 * s ** 3 * D / 3.0,
            "small_s_prediction": (math.cos(SEP) * PHI[1] ** 2 + 2 * math.cos(2 * SEP) * PHI[2] ** 2)
            / (PHI[1] ** 2 + 2 * PHI[2] ** 2),
        })

    results["runtime_seconds"] = time.time() - t_start
    with open(out_path, "x") as fh:
        json.dump(results, fh, indent=1)

    print(f"\nLandau D(v0) = {D:.5f}")
    print(" N      s    q   cf_re    (se)    Landau   | 1st-iter (se)   exp(-V q^2/2)"
          " | E|Y-Y1|")
    for row in results["rows"]:
        print(f"{row['N']:6d} {row['s']:4.1f} {row['q']:4.1f} "
              f"{row['cf_re']:8.4f} ({row['cf_re_se']:.4f}) {row['landau_prediction']:8.4f} | "
              f"{row['first_iterate_cf_re']:8.4f} ({row['first_iterate_cf_re_se']:.4f}) "
              f"{row['first_iterate_gaussian']:8.4f} | {row['mean_abs_Y_minus_Y1']:.4f}")
    print("\npairs:")
    for row in results["pair_rows"]:
        print(row)
    print("limit two-point motion:")
    for row in results["limit_pair"]:
        print(row)
    print("dt check:")
    for row in results["dt_check"]:
        print(row)
    print(f"runtime {results['runtime_seconds']:.1f}s; wrote {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
