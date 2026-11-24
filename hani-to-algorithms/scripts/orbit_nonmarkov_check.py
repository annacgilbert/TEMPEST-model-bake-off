#!/usr/bin/env python3
"""Monte Carlo check of docs/orbit_nonmarkov_theorem.tex (numpy only).

Particle  dY/dtau = w,  dw/dtau = eps * G(Y, tau),  Y(0) = w(0) = 0, in the
frame of the ballistic orbit, with
    G(y, tau) = sum_k Re( f_k b_k(tau) exp(i k.y) ),
where the b_k are independent stationary circular complex Gaussian processes
with covariance rho_k(u) = E[b_k(u) conj b_k(0)].  The note predicts
    E exp(i q.Y_t) = exp(-eps^2 t^3 q.Dq / 3) + error,
    q.Dq = (1/2) sum_k |q.f_k|^2 int_0^inf Re rho_k(u) du
         = (pi/2) sum_k |q.f_k|^2 S_k(0),
S_k being the spectral density of b_k (frequency measured from resonance).

Experiments
  A  undamped continuum, Gaussian spectral density (inside the theorem);
  A' undamped continuum, compactly supported spectral density with
     |rho(u)| ~ u^-2 (outside the theorem: tests the conjecture);
  R  recurrence: the same continuum sampled on coarser frequency grids, so
     that the recurrence time 2 pi / dOmega falls below t;
  B  failure example: one undamped mode (pure point spectrum), resonant and
     non-resonant;
  C  one resonant Ornstein-Uhlenbeck mode, damping gamma swept through
     eps^(1/2) (trapping threshold).

The continuum is sampled on a uniform frequency grid dOmega = 2 pi / T_rec
and synthesised by FFT, so the sampled field is exactly periodic in time with
period T_rec (the recurrence time).  Reported separately: Monte Carlo
standard errors, time-step error (common random numbers), and the spectral
discretisation error (covariance error and recurrence time).

Usage:  python orbit_nonmarkov_check.py [output_dir]
        python orbit_nonmarkov_check.py --second-order [output_dir]
The second form writes the deterministic second-order coefficients kappa1,
kappa2 of the note (quadrature, no sampling) to a separate JSON file.
Refuses to overwrite an existing results file.
"""
import json
import math
import os
import sys
import time

import numpy as np

SEED = 20261124
Q = np.array([1.0, 0.5])
KVEC = np.array([[1.0, 0.0], [0.0, 1.0], [1.0, 1.0], [1.0, -1.0], [2.0, 1.0]])
PHI0 = np.array([1.0, 0.8, 0.6, 0.6, 0.4])       # potential amplitudes (rescaled)
OMEGA0 = np.array([0.0, 0.4, -0.5, 0.8, 1.2])    # centre of S_k minus k.v0
WIDTH = np.array([1.0, 0.8, 1.2, 1.0, 1.5])      # spectral width of mode k
TARGET_D = 0.9                                   # q.Dq after rescaling


# ---------------------------------------------------------------- spectra
def spec_gauss(om, k):
    s = WIDTH[k]
    return np.exp(-(om - OMEGA0[k]) ** 2 / (2 * s * s)) / (math.sqrt(2 * math.pi) * s)


def rho_gauss(u, k):
    return np.exp(-1j * OMEGA0[k] * u - 0.5 * (WIDTH[k] * u) ** 2)


def spec_epan(om, k):
    # S = 3/(4W) (1 - x^2)_+,  x = (om - Omega0)/W,  W = 2*width
    W = 2.0 * WIDTH[k]
    x = (om - OMEGA0[k]) / W
    return 0.75 / W * np.clip(1.0 - x * x, 0.0, None)


def rho_epan(u, k):
    W = 2.0 * WIDTH[k]
    z = np.asarray(W * u, dtype=float)
    out = np.ones_like(z)
    nz = np.abs(z) > 1e-6
    zz = z[nz]
    out[nz] = 3.0 * (np.sin(zz) - zz * np.cos(zz)) / zz ** 3
    return np.exp(-1j * OMEGA0[k] * u) * out


SPECTRA = {"gauss": (spec_gauss, rho_gauss, 9.0), "epan": (spec_epan, rho_epan, 5.0)}


def amplitudes(spec):
    """f_k = -i phi_k k with phi rescaled so that q.Dq = TARGET_D."""
    s0 = np.array([spec(0.0, k) for k in range(len(KVEC))])
    qk = KVEC @ Q
    d_raw = 0.5 * math.pi * np.sum((PHI0 * qk) ** 2 * s0)
    phi = PHI0 * math.sqrt(TARGET_D / d_raw)
    return phi, 0.5 * math.pi * np.sum((phi * qk) ** 2 * s0)


# ------------------------------------------------------- continuum sampler
class Continuum:
    """Frequency grid Omega_m = m * dOm, m = -mh..mh, dOm = 2 pi / t_rec."""

    def __init__(self, name, t_rec):
        self.spec, self.rho, band = SPECTRA[name]
        self.t_rec = t_rec
        self.dom = 2 * math.pi / t_rec
        self.mh = int(math.ceil(band / self.dom))
        self.m = np.arange(-self.mh, self.mh + 1)
        nk = len(KVEC)
        self.wgt = np.empty((nk, self.m.size))
        for k in range(nk):
            w = self.spec(self.m * self.dom, k) * self.dom
            self.wgt[k] = w / w.sum()          # enforce E|b_k|^2 = 1 exactly
        self.phi, self.d = amplitudes(self.spec)

    def n_modes(self):
        return int((self.wgt > 1e-14).sum())

    def rho_sampled(self, u, k):
        return (self.wgt[k][None, :] * np.exp(-1j * np.outer(u, self.m * self.dom))).sum(1)

    def cov_error(self, t_max):
        u = np.linspace(0.0, t_max, 2001)
        return max(float(np.abs(self.rho_sampled(u, k) - self.rho(u, k)).max())
                   for k in range(len(KVEC)))

    def d_sampled(self, t_max):
        """q.D_M q with the time integral of the sampled covariance cut at t_max."""
        u = np.linspace(0.0, t_max, 20001)
        qk = KVEC @ Q
        tot = 0.0
        for k in range(len(KVEC)):
            r = self.rho_sampled(u, k).real
            tot += 0.5 * (self.phi[k] * qk[k]) ** 2 * float(((r[1:] + r[:-1]) * 0.5 * np.diff(u)).sum())
        return tot

    def draw(self, rng, n):
        z = rng.standard_normal((n, len(KVEC), self.m.size)) \
            + 1j * rng.standard_normal((n, len(KVEC), self.m.size))
        return z * np.sqrt(0.5 * self.wgt)[None]

    def synth(self, coef, dt, nsteps):
        nfft = int(round(self.t_rec / dt))
        assert abs(nfft * dt - self.t_rec) < 1e-9 and nfft > 2 * self.mh + 1
        arr = np.zeros(coef.shape[:2] + (nfft,), dtype=complex)
        arr[:, :, self.m % nfft] = coef
        b = np.fft.fft(arr, axis=2)            # b[n] = sum_m c_m exp(-i Om_m n dt)
        idx = np.arange(nsteps + 1) % nfft     # periodic continuation (recurrence)
        return b[:, :, idx]


def integrate(b, phi, eps, dt, record):
    """Velocity Verlet for Y'' = eps G(Y, tau); b has shape (n, K, nsteps+1)."""
    n = b.shape[0]
    Y = np.zeros((n, 2))
    w = np.zeros((n, 2))
    fk = -1j * phi[:, None] * KVEC             # f_k = -i phi_k k

    def acc(Y, i):
        amp = b[:, :, i] * np.exp(1j * (Y @ KVEC.T))
        return eps * (amp[:, :, None] * fk[None]).real.sum(1)

    a = acc(Y, 0)
    out = {}
    for i in range(b.shape[2] - 1):
        Y = Y + dt * w + 0.5 * dt * dt * a
        a2 = acc(Y, i + 1)
        w = w + 0.5 * dt * (a + a2)
        a = a2
        if i + 1 in record:
            out[i + 1] = np.exp(1j * (Y @ Q))
    return out


def mean_se(x):
    n = x.size
    return (float(x.real.mean()), float(x.real.std(ddof=1) / math.sqrt(n)),
            float(x.imag.mean()), float(x.imag.std(ddof=1) / math.sqrt(n)))


def run_continuum(name, t_rec, n_part, s_list, n_samp, dt, rng, batch=2000, dt_coarse=None):
    cont = Continuum(name, t_rec)
    eps = n_part ** -0.5
    times = [s * n_part ** (1.0 / 3.0) for s in s_list]
    ratio = 1 if dt_coarse is None else int(round(dt_coarse / dt))
    rec = [ratio * int(round(t / (dt * ratio))) for t in times]   # common time grid
    vals = {r: [] for r in rec}
    diffs = {r: [] for r in rec}
    for _ in range(n_samp // batch):
        coef = cont.draw(rng, batch)
        out = integrate(cont.synth(coef, dt, max(rec)), cont.phi, eps, dt, set(rec))
        for r in rec:
            vals[r].append(out[r])
        if dt_coarse is not None:
            rc = [r // ratio for r in rec]
            outc = integrate(cont.synth(coef, dt_coarse, max(rc)), cont.phi, eps,
                             dt_coarse, set(rc))
            for r, r2 in zip(rec, rc):
                diffs[r].append(outc[r2] - out[r])
    rows = []
    for s, t, r in zip(s_list, times, rec):
        x = np.concatenate(vals[r])
        re, re_se, im, im_se = mean_se(x)
        pred = math.exp(-eps ** 2 * (r * dt) ** 3 * cont.d / 3.0)
        row = dict(N=n_part, eps=eps, s=s, t=r * dt, measured_re=re, mc_se_re=re_se,
                   measured_im=im, mc_se_im=im_se, predicted=pred,
                   deviation=re - pred, deviation_over_se=(re - pred) / re_se)
        if dt_coarse is not None:
            dx = np.concatenate(diffs[r])
            row["timestep_diff_coarse_minus_fine"] = float(dx.real.mean())
            row["timestep_diff_se"] = float(dx.real.std(ddof=1) / math.sqrt(dx.size))
        rows.append(row)
    t_max = max(times)
    info = dict(spectrum=name, t_rec=t_rec, d_omega=cont.dom, n_frequencies_per_mode=2 * cont.mh + 1,
                n_modes_with_weight=cont.n_modes(), qDq=cont.d, phi=cont.phi.tolist(),
                dt=dt, n_samples=(n_samp // batch) * batch,
                cov_error_sup_up_to_tmax=cont.cov_error(t_max),
                qDq_sampled_time_integral_to_tmax=cont.d_sampled(t_max))
    return info, rows


# ------------------------------------------------- B: single undamped mode
def run_single_undamped(rng, n_samp=20000, dt=0.02):
    """d = 1, k = f = 1.  Y'' = eps |zeta| cos(Y - Omega tau + phase)."""
    res = []
    q = 1.0 / 12.0
    for n_part in (1e3, 1e4, 1e5):
        eps = n_part ** -0.5
        for omega in (0.0, 1.0):
            t = 1.5 * n_part ** (1.0 / 3.0)
            nst = int(round(t / dt))
            zeta = (rng.standard_normal(n_samp) + 1j * rng.standard_normal(n_samp)) / math.sqrt(2)
            Y = np.zeros(n_samp)
            w = np.zeros(n_samp)
            maxabs = np.zeros(n_samp)
            a = eps * (zeta * np.exp(1j * Y)).real
            for i in range(nst):
                Y = Y + dt * w + 0.5 * dt * dt * a
                a2 = eps * (zeta * np.exp(1j * (Y - omega * (i + 1) * dt))).real
                w = w + 0.5 * dt * (a + a2)
                a = a2
                np.maximum(maxabs, np.abs(Y), out=maxabs)
            re, re_se, im, im_se = mean_se(np.exp(1j * q * Y))
            row = dict(N=n_part, eps=eps, Omega=omega, q=q, t=nst * dt, measured_re=re,
                       mc_se_re=re_se, measured_im=im, mc_se_im=im_se,
                       var_Y=float(Y.var()), max_abs_Y_over_2pi=float(maxabs.max() / (2 * math.pi)))
            if omega == 0.0:
                row["lower_bound_proved"] = math.cos(2 * math.pi * q)
                row["first_iterate_var"] = eps ** 2 * t ** 4 / 8.0
                row["first_iterate_gaussian_value"] = math.exp(-q * q * eps ** 2 * t ** 4 / 16.0)
            else:
                A = np.abs(zeta)
                good = 4 * eps * A < omega ** 2
                row["event_fraction"] = float(good.mean())
                row["max_ratio_Y_to_bound"] = float(
                    (maxabs[good] / (4 * eps * A[good] * nst * dt / abs(omega))).max())
            res.append(row)
    return res


# --------------------------------------------- C: resonant OU mode, gamma sweep
def run_gamma_sweep(rng, eps=1e-3, n_samp=20000, s=1.5, q=1.0):
    """d = 1, k = f = 1, lambda = gamma (resonant).  D = 1/(2 gamma);
    t = s (gamma/eps^2)^(1/3); prediction exp(-s^3 q^2 / 6) for every gamma."""
    res = []
    for ratio in (0.03, 0.1, 0.3, 1.0, 3.0, 10.0, 30.0):
        gamma = ratio * math.sqrt(eps)
        t = s * (gamma / eps ** 2) ** (1.0 / 3.0)
        dt = min(0.05, 0.02 / gamma, t / 400.0)
        nst = int(math.ceil(t / dt))
        dt = t / nst
        dec = math.exp(-gamma * dt)
        sd = math.sqrt((1 - dec * dec) / 2)
        b = (rng.standard_normal(n_samp) + 1j * rng.standard_normal(n_samp)) / math.sqrt(2)
        Y = np.zeros(n_samp)
        w = np.zeros(n_samp)
        maxabs = np.zeros(n_samp)
        a = eps * (b * np.exp(1j * Y)).real
        for _ in range(nst):
            Y = Y + dt * w + 0.5 * dt * dt * a
            b = dec * b + sd * (rng.standard_normal(n_samp) + 1j * rng.standard_normal(n_samp))
            a2 = eps * (b * np.exp(1j * Y)).real
            w = w + 0.5 * dt * (a + a2)
            a = a2
            np.maximum(maxabs, np.abs(Y), out=maxabs)
        re, re_se, im, im_se = mean_se(np.exp(1j * q * Y))
        pred = math.exp(-s ** 3 * q * q / 6.0)
        res.append(dict(eps=eps, gamma=gamma, gamma_over_sqrt_eps=ratio, t=t, gamma_t=gamma * t,
                        dt=dt, s=s, q=q, measured_re=re, mc_se_re=re_se, measured_im=im,
                        mc_se_im=im_se, predicted=pred, deviation=re - pred,
                        fraction_within_2pi=float((maxabs <= 2 * math.pi).mean())))
    return res


def second_order(out_dir):
    """Deterministic second-order coefficients of the note (experiment A):
        E exp(iq.Y_t) ~ exp(-eps^2 t^3 d/3) (1 + eps^2 t^2 (kappa1 - i kappa2)/2),
    kappa1 = int_0^inf u c(u) du,
    kappa2 = (1/2) sum_k int_0^inf u Im(rho_k(u) B_k (k.conj f_k)) du,
    and the exact first-iterate value exp(-Var(q.Y1_t)/2).  Quadrature only."""
    out_path = os.path.join(out_dir, "orbit_nonmarkov_second_order.json")
    if os.path.exists(out_path):
        sys.exit("refusing to overwrite " + out_path)
    os.makedirs(out_dir, exist_ok=True)
    phi, d = amplitudes(spec_gauss)
    qk = KVEC @ Q
    k2 = (KVEC ** 2).sum(1)
    u = np.linspace(0.0, 40.0, 400001)
    du = u[1] - u[0]

    def quad(y):
        return float((y[1:] + y[:-1]).sum() * 0.5 * du)

    c = sum(0.5 * (phi[k] * qk[k]) ** 2 * rho_gauss(u, k).real for k in range(len(KVEC)))
    kappa1 = quad(u * c)
    # f_k = -i phi_k k:  B_k (k.conj f_k) = phi_k^2 (q.k) |k|^2  (real)
    kappa2 = 0.5 * sum(phi[k] ** 2 * qk[k] * k2[k] * quad(u * rho_gauss(u, k).imag)
                       for k in range(len(KVEC)))
    rows = []
    for n_part in (1e3, 1e4, 1e5):
        eps = n_part ** -0.5
        for s in (1.0, 1.5):
            t = 0.1 * round(s * n_part ** (1.0 / 3.0) / 0.1) if n_part == 1e4 else \
                0.05 * round(s * n_part ** (1.0 / 3.0) / 0.05)
            lead = math.exp(-eps ** 2 * t ** 3 * d / 3.0)
            uu = u[u <= t]
            cc = c[: uu.size]
            wgt = (t - uu) ** 3 / 3.0 + uu * (t - uu) ** 2 / 2.0
            y = cc * wgt
            var1 = 2 * eps ** 2 * float((y[1:] + y[:-1]).sum() * 0.5 * du)
            rows.append(dict(N=n_part, s=s, t=t, leading=lead,
                             second_order_re=lead * eps ** 2 * t ** 2 * kappa1 / 2.0,
                             second_order_im=-lead * eps ** 2 * t ** 2 * kappa2 / 2.0,
                             first_iterate_value=math.exp(-var1 / 2.0)))
    with open(out_path, "x") as fh:
        json.dump(dict(qDq=d, kappa1=kappa1, kappa2=kappa2, rows=rows), fh, indent=1)
    print("kappa1", kappa1, "kappa2", kappa2)
    for r in rows:
        print(r)


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    default_dir = os.path.join(here, "..", "results", "orbit_nonmarkov")
    if len(sys.argv) > 1 and sys.argv[1] == "--second-order":
        second_order(sys.argv[2] if len(sys.argv) > 2 else default_dir)
        return
    out_dir = sys.argv[1] if len(sys.argv) > 1 else default_dir
    out_path = os.path.join(out_dir, "orbit_nonmarkov_check.json")
    if os.path.exists(out_path):
        sys.exit("refusing to overwrite " + out_path)
    os.makedirs(out_dir, exist_ok=True)
    t0 = time.time()
    rng = np.random.default_rng(SEED)
    result = dict(script="orbit_nonmarkov_check.py", seed=SEED, numpy=np.__version__,
                  q=Q.tolist(), kvec=KVEC.tolist(), omega0=OMEGA0.tolist(),
                  width=WIDTH.tolist(), target_qDq=TARGET_D)

    # A: Gaussian spectral density, T_rec = 204.8, dt = 0.05; dt = 0.1 control
    rows, info = [], None
    for n_part in (1e3, 1e4, 1e5):
        info, r = run_continuum("gauss", 204.8, n_part, (1.0, 1.5), 40000, 0.05, rng,
                                dt_coarse=0.1 if n_part == 1e4 else None)
        rows += r
        print("A", n_part, [(round(x["measured_re"], 4), round(x["predicted"], 4),
                             round(x["mc_se_re"], 4)) for x in r], flush=True)
    result["A_gaussian_spectrum"] = dict(info=info, rows=rows)

    # A': compactly supported spectral density (outside the hypotheses)
    rows = []
    for n_part in (1e3, 1e4, 1e5):
        info, r = run_continuum("epan", 409.6, n_part, (1.0, 1.5), 20000, 0.05, rng)
        rows += r
        print("A'", n_part, [(round(x["measured_re"], 4), round(x["predicted"], 4),
                              round(x["mc_se_re"], 4)) for x in r], flush=True)
    result["A2_compact_spectrum_outside_hypotheses"] = dict(info=info, rows=rows)

    # R: recurrence.  N = 1e4, t = 32.3; frequency grids with T_rec below and above t
    rows = []
    for t_rec in (6.4, 12.8, 25.6, 51.2, 102.4):
        info, r = run_continuum("gauss", t_rec, 1e4, (1.5,), 20000, 0.05, rng)
        r[0].update(t_rec=t_rec, n_frequencies_per_mode=info["n_frequencies_per_mode"],
                    cov_error_sup_up_to_t=info["cov_error_sup_up_to_tmax"],
                    qDq_sampled_time_integral_to_t=info["qDq_sampled_time_integral_to_tmax"])
        rows += r
        print("R", t_rec, round(r[0]["measured_re"], 4), round(r[0]["predicted"], 4),
              round(r[0]["mc_se_re"], 4), flush=True)
    result["R_recurrence"] = rows

    result["B_single_undamped_mode"] = run_single_undamped(rng)
    for x in result["B_single_undamped_mode"]:
        print("B", x["N"], x["Omega"], round(x["measured_re"], 4), round(x["max_abs_Y_over_2pi"], 4),
              flush=True)
    result["C_gamma_sweep"] = run_gamma_sweep(rng)
    for x in result["C_gamma_sweep"]:
        print("C", x["gamma_over_sqrt_eps"], round(x["measured_re"], 4), round(x["predicted"], 4),
              round(x["mc_se_re"], 4), flush=True)

    result["runtime_seconds"] = time.time() - t0
    with open(out_path, "x") as fh:
        json.dump(result, fh, indent=1)
    print("wrote", out_path, "in", round(result["runtime_seconds"], 1), "s")


if __name__ == "__main__":
    main()
