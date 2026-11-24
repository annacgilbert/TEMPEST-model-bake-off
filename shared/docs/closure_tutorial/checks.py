"""Numerical checks for the worked examples in tutorial.tex.

Every number quoted in the tutorial as "checked" is produced here and saved
to a JSON file; the two figures are drawn from the .dat files written next
to it. No random numbers are used.

Usage:
    python3 checks.py --output results/<new-run-directory>

The script refuses to write into an existing directory.
"""

from __future__ import annotations

import argparse
import json
import math
import platform
import sys
from fractions import Fraction
from pathlib import Path

import numpy as np
import scipy
from scipy.integrate import quad
from scipy.special import gamma, wofz

SQRT2 = math.sqrt(2.0)
SQRTPI = math.sqrt(math.pi)


# ---------------------------------------------------------------------------
# Section 1: fast-slow toy model
# ---------------------------------------------------------------------------
def fast_slow(a=0.0, b=1.0, c=-1.0):
    """x' = a x + b y,  eps y' = c x - y.  Slow eigenvalue against closures."""
    rows = []
    for eps in (0.2, 0.1, 0.05, 0.025):
        mat = np.array([[a, b], [c / eps, -1.0 / eps]])
        eig = np.linalg.eigvals(mat)
        slow = float(eig[np.argmin(np.abs(eig))].real)
        markov = a + b * c
        first = (a + b * c) * (1.0 - eps * b * c)
        pade = (a + b * c) / (1.0 + eps * b * c)
        rows.append(
            dict(
                eps=eps,
                exact_slow_eigenvalue=slow,
                markov=markov,
                first_order=first,
                rational=pade,
                err_markov=abs(markov - slow),
                err_first_order=abs(first - slow),
                err_rational=abs(pade - slow),
            )
        )
    return rows


# ---------------------------------------------------------------------------
# Section 2: cumulant-discard closure for dx = -x^3 dt + sigma dW
# ---------------------------------------------------------------------------
def cubic_langevin():
    exact_m2 = SQRT2 * gamma(0.75) / gamma(0.25)  # in units of sigma
    num = quad(lambda x: x**2 * math.exp(-(x**4) / 2.0), -np.inf, np.inf)[0]
    den = quad(lambda x: math.exp(-(x**4) / 2.0), -np.inf, np.inf)[0]
    m4_num = quad(lambda x: x**4 * math.exp(-(x**4) / 2.0), -np.inf, np.inf)[0]
    gaussian = 1.0 / math.sqrt(6.0)
    sixth = 1.0 / math.sqrt(5.0)
    return dict(
        exact_m2_over_sigma=exact_m2,
        exact_m2_by_quadrature=num / den,
        exact_m4_over_sigma2=m4_num / den,
        gaussian_closure_m2=gaussian,
        gaussian_relative_error=gaussian / exact_m2 - 1.0,
        sixth_cumulant_closure_m2=sixth,
        sixth_cumulant_relative_error=sixth / exact_m2 - 1.0,
    )


# ---------------------------------------------------------------------------
# Section 3: Chapman-Enskog coefficients for BGK from Gaussian moments
# ---------------------------------------------------------------------------
def gaussian_even_moment(n):
    """E[c^n] for a standard normal, n even."""
    out = Fraction(1)
    for j in range(1, n, 2):
        out *= j
    return out


def bgk_chapman_enskog():
    # 3D, units n = T = m = 1.  <c_x^2 c^4> = <c^6>/3, <c_x^2 c^2> = <c^4>/3,
    # with <c^4> = 15 and <c^6> = 105 for a 3D unit Gaussian.
    c4, c6 = Fraction(15), Fraction(105)
    kappa_times_nu = c6 / 3 / 4 - Fraction(5, 4) * c4 / 3
    # shear: mu*nu = <c_x^2 c_y^2> = 1
    mu_times_nu = Fraction(1)
    prandtl = Fraction(5, 2) * mu_times_nu / kappa_times_nu
    # 1D, q = <He_3 h>: kappa*nu = <He_3^2>/2 = 3
    he3sq = gaussian_even_moment(6) - 6 * gaussian_even_moment(4) + 9 * gaussian_even_moment(2)
    return dict(
        kappa_times_nu_3d=str(kappa_times_nu),
        mu_times_nu_3d=str(mu_times_nu),
        prandtl_bgk=str(prandtl),
        kappa_times_nu_1d_third_central_moment=str(he3sq / 2),
    )


# ---------------------------------------------------------------------------
# Section 4: moment-closure facts
# ---------------------------------------------------------------------------
def hermite_truncation_nodes(order=8):
    """Truncating the Hermite hierarchy after a_N is a discrete-velocity model
    on the roots of He_{N+1}."""
    n = order + 1
    jac = np.zeros((n, n))
    for j in range(n - 1):
        jac[j, j + 1] = jac[j + 1, j] = math.sqrt(j + 1)
    eig = np.sort(np.linalg.eigvalsh(jac))
    nodes, _ = np.polynomial.hermite_e.hermegauss(n)
    return dict(
        retained_order=order,
        max_difference_eigenvalues_vs_gauss_hermite_nodes=float(np.max(np.abs(eig - np.sort(nodes)))),
        largest_node=float(eig[-1]),
    )


def eddington_factors():
    def m1(f):
        return (3.0 + 4.0 * f * f) / (5.0 + 2.0 * math.sqrt(4.0 - 3.0 * f * f))

    rows = []
    for beta in (0.1, 0.4, 0.7, 0.9):
        w = lambda mu: (1.0 - beta * mu) ** -4
        e = quad(w, -1, 1)[0]
        f = quad(lambda mu: mu * w(mu), -1, 1)[0] / e
        chi = quad(lambda mu: mu * mu * w(mu), -1, 1)[0] / e
        rows.append(dict(beta=beta, f=f, chi_quadrature=chi, chi_formula=m1(f)))
    minerbo = []
    for bb in (0.5, 2.0, 8.0):
        w = lambda mu: math.exp(bb * mu)
        e = quad(w, -1, 1)[0]
        f = quad(lambda mu: mu * w(mu), -1, 1)[0] / e
        chi = quad(lambda mu: mu * mu * w(mu), -1, 1)[0] / e
        minerbo.append(
            dict(b=bb, f=f, f_formula=1.0 / math.tanh(bb) - 1.0 / bb, chi_quadrature=chi, chi_formula=1.0 - 2.0 * f / bb)
        )
    lp = lambda r: (1.0 / math.tanh(r) - 1.0 / r) / r
    return dict(
        m1_limits=dict(f0=m1(0.0), f1=m1(1.0)),
        m1_boosted_isotropic=rows,
        minerbo_exponential=minerbo,
        levermore_pomraning_limiter=dict(R_small=lp(1e-3), R_large_times_R=lp(1e3) * 1e3),
    )


# ---------------------------------------------------------------------------
# Section 5: Hammett-Perkins
# ---------------------------------------------------------------------------
def zfun(zeta):
    return 1j * SQRTPI * wofz(zeta)


def r_exact(zeta):
    return 1.0 + zeta * zfun(zeta)


CHI1 = 2.0 / SQRTPI
B4 = 8.0 / (3.0 * math.pi - 8.0)
D1 = 2.0 * SQRTPI / (3.0 * math.pi - 8.0)
BETA1 = (32.0 - 9.0 * math.pi) / (3.0 * math.pi - 8.0)


def r3(zeta, chi1=CHI1):
    return (chi1 - 1j * zeta) / (chi1 - 3j * zeta - 2 * chi1 * zeta**2 + 2j * zeta**3)


def r4(zeta, b=B4, d1=D1):
    num = b - 2j * d1 * zeta - 2 * zeta**2
    den = b - 6j * d1 * zeta - (2 * b + 6) * zeta**2 + 4j * d1 * zeta**3 + 4 * zeta**4
    return num / den


def static_ratio_formula(n):
    """c_n with a_{n+1} = -i sgn(k) c_n a_n in the quasi-static collisionless
    response; a_n are coefficients in the orthonormal Hermite basis."""

    ratio = 1.0  # n!!/(n-1)!! accumulated as a product of bounded factors
    for m in range(n, 0, -2):
        ratio *= m / (m - 1.0) if m > 1 else 1.0
    pref = math.sqrt(2.0 / math.pi) if n % 2 == 0 else math.sqrt(math.pi / 2.0)
    return pref * ratio / math.sqrt(n + 1.0)


def static_ratio_quadrature(n, eps=1e-4):
    """Independent evaluation: W_n(z) = <He_n/(v-z)> at z = i*eps by quadrature."""

    def w(m):
        he = np.polynomial.hermite_e.HermiteE.basis(m)

        def integrand(v, part):
            val = he(v) * math.exp(-v * v / 2.0) / math.sqrt(2.0 * math.pi) / (v - 1j * eps)
            return val.real if part == 0 else val.imag

        re = quad(integrand, -12, 12, args=(0,), points=[0.0], limit=800)[0]
        im = quad(integrand, -12, 12, args=(1,), points=[-eps, 0.0, eps], limit=800)[0]
        return re + 1j * im

    ratio = w(n + 1) / (w(n) * math.sqrt(n + 1.0))
    return complex(ratio)


def hammett_perkins(figdir: Path):
    out = dict(chi1=CHI1, D1=D1, beta1=BETA1, b=B4)

    # small-zeta expansion R = 1 + i sqrt(pi) zeta - 2 zeta^2 + ...
    z = 1e-3
    out["small_zeta_residual_exact"] = abs(r_exact(z) - (1 + 1j * SQRTPI * z - 2 * z * z))
    out["small_zeta_R3_minus_R"] = abs(r3(z) - r_exact(z))
    out["small_zeta_R4_minus_R"] = abs(r4(z) - r_exact(z))
    # orders of agreement at small zeta: error ~ zeta^p
    e3 = [abs(r3(t) - r_exact(t)) for t in (1e-2, 2e-2)]
    e4 = [abs(r4(t) - r_exact(t)) for t in (1e-2, 2e-2)]
    out["small_zeta_error_order_R3"] = math.log2(e3[1] / e3[0])
    out["small_zeta_error_order_R4"] = math.log2(e4[1] / e4[0])
    # large-zeta: 1/R = -2 zeta^2 + 3 + c/zeta^2
    zl = 40.0
    out["large_zeta_coefficient_exact"] = float(((1 / r_exact(zl + 0j)) + 2 * zl * zl - 3).real * zl * zl)
    out["large_zeta_coefficient_R4"] = float(((1 / r4(zl)) + 2 * zl * zl - 3).real * zl * zl)
    el3 = [abs(r3(t) - r_exact(t + 0j)) for t in (20.0, 40.0)]
    el4 = [abs(r4(t) - r_exact(t + 0j)) for t in (20.0, 40.0)]
    out["large_zeta_error_decay_order_R3"] = -math.log2(el3[1] / el3[0])
    out["large_zeta_error_decay_order_R4"] = -math.log2(el4[1] / el4[0])

    grid = np.linspace(0.0, 12.0, 24001)
    rex = r_exact(grid + 0j)
    d3 = np.abs(r3(grid) - rex)
    d4 = np.abs(r4(grid) - rex)
    out["sup_error_R3_real_axis"] = float(d3.max())
    out["argmax_R3"] = float(grid[d3.argmax()])
    out["sup_error_R4_real_axis"] = float(d4.max())
    out["argmax_R4"] = float(grid[d4.argmax()])
    out["sup_abs_R_real_axis"] = float(np.abs(rex).max())

    plot = np.linspace(0.0, 4.0, 161)
    rp = r_exact(plot + 0j)
    table = np.column_stack(
        [plot, rp.real, rp.imag, r3(plot).real, r3(plot).imag, r4(plot).real, r4(plot).imag]
    )
    np.savetxt(
        figdir / "response.dat",
        table,
        header="zeta ReR ImR ReR3 ImR3 ReR4 ImR4",
        comments="",
        fmt="%.8f",
    )

    ratios = []
    for n in range(2, 9):
        num = static_ratio_quadrature(n)
        ratios.append(
            dict(
                n=n,
                c_formula=static_ratio_formula(n),
                c_quadrature=float((1j * num).real),
                quadrature_residual=abs(num + 1j * static_ratio_formula(n)),
            )
        )
    out["static_ratios"] = ratios
    out["static_ratio_n200"] = static_ratio_formula(200)
    out["static_ratio_n201"] = static_ratio_formula(201)
    # translate c_2 into the heat-flux coefficient: q = sqrt(6) a_3, T = sqrt(2) a_2
    out["three_moment_coefficient_from_c2"] = static_ratio_formula(2) * math.sqrt(6.0) / math.sqrt(2.0)
    out["sqrt_8_over_pi"] = math.sqrt(8.0 / math.pi)
    return out


# ---------------------------------------------------------------------------
# Section 6: exact quasi-static closures between the two limits (1D)
# ---------------------------------------------------------------------------
def gauss(v):
    return math.exp(-v * v / 2.0) / math.sqrt(2.0 * math.pi)


def theta_bgk(y):
    num = quad(lambda v: (v**3 - 3 * v) ** 2 * gauss(v) / (v * v + y * y), -np.inf, np.inf, limit=400)[0]
    den = quad(lambda v: (v * v - 1) ** 2 * gauss(v) / (v * v + y * y), -np.inf, np.inf, limit=400)[0]
    return (1 + y * y) / (y * (3 + y * y)) * num / den


def theta_dougherty(y):
    a = 1.0 / (y * y)
    logE = lambda s: a * (math.log1p(-s) + s)
    num = quad(lambda s: s * math.exp(logE(s)), 0, 1, limit=400)[0]
    den = quad(lambda s: math.exp(logE(s)), 0, 1, limit=400)[0]
    return 2.0 / y * num / den


def theta_galerkin(y, kind, nmodes=1200):
    """Independent check: solve (ik v + Lambda) g = 1 in a Hermite basis,
    k = 1, nu = y.  theta = -2/(|k| <He_2 g>)."""
    a = np.zeros((nmodes, nmodes), dtype=complex)
    for j in range(nmodes - 1):
        a[j, j + 1] = a[j + 1, j] = 1j * math.sqrt(j + 1)
    for j in range(3, nmodes):
        a[j, j] += y * (1.0 if kind == "bgk" else float(j))
    rhs = np.zeros(nmodes, dtype=complex)
    rhs[0] = 1.0
    g = np.linalg.solve(a, rhs)
    t1 = math.sqrt(2.0) * g[2]
    return complex(-2.0 / t1)


def intermediate(figdir: Path):
    out = {}
    hp = math.sqrt(8.0 / math.pi)
    out["bgk_table"] = [dict(y=y, theta=theta_bgk(y)) for y in (0.01, 0.1, 1.0, 3.0, 10.0, 100.0)]
    out["galerkin_checks"] = []
    for y in (1.0, 3.0):
        for kind, fn in (("bgk", theta_bgk), ("dougherty", theta_dougherty)):
            gal = theta_galerkin(y, kind)
            out["galerkin_checks"].append(
                dict(y=y, operator=kind, formula=fn(y), galerkin_real=gal.real, galerkin_imag=gal.imag)
            )
    out["collisionless_limits"] = dict(
        hammett_perkins=hp, bgk_y_0p002=theta_bgk(0.002), dougherty_y_0p02=theta_dougherty(0.02)
    )
    y = 50.0
    out["leading_deficit"] = dict(
        bgk_coefficient=(1 - theta_bgk(y) * y / 3.0) * y * y,
        dougherty_coefficient=(1 - theta_dougherty(y) * y) * y * y,
    )

    svals = np.logspace(-2, 2, 81)
    rows = []
    ratio_b, ratio_d = [], []
    for s in svals:
        cb = theta_bgk(3.0 / s) / s  # kappa_F = 3/nu, s = 3/y
        cd = theta_dougherty(1.0 / s) / s  # kappa_F = 1/nu, s = 1/y
        ch = 1.0 / (1.0 + s * math.sqrt(math.pi / 8.0))
        rows.append([s, cb, cd, ch, min(1.0, hp / s)])
        ratio_b.append(cb / ch)
        ratio_d.append(cd / ch)
    np.savetxt(
        figdir / "intermediate.dat",
        np.array(rows),
        header="s bgk dougherty harmonic limits",
        comments="",
        fmt="%.8e",
    )
    out["exact_over_harmonic_interpolant"] = dict(
        bgk_min=min(ratio_b), bgk_max=max(ratio_b), dougherty_min=min(ratio_d), dougherty_max=max(ratio_d)
    )
    for target in (0.1, 0.3, 1.0, 3.0, 10.0):
        j = int(np.argmin(np.abs(svals - target)))
        out.setdefault("matched_conductivity_table", []).append(
            dict(s=float(svals[j]), bgk=rows[j][1], dougherty=rows[j][2], harmonic=rows[j][3])
        )
    return out


# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    outdir: Path = args.output
    if outdir.exists():
        sys.exit(f"refusing to overwrite existing directory {outdir}")
    outdir.mkdir(parents=True)

    results = dict(
        environment=dict(
            python=platform.python_version(), numpy=np.__version__, scipy=scipy.__version__, seed="none used"
        ),
        fast_slow=fast_slow(),
        cubic_langevin=cubic_langevin(),
        bgk_chapman_enskog=bgk_chapman_enskog(),
        hermite_truncation=hermite_truncation_nodes(),
        eddington=eddington_factors(),
        hammett_perkins=hammett_perkins(outdir),
        intermediate=intermediate(outdir),
    )
    (outdir / "checks.json").write_text(json.dumps(results, indent=2) + "\n")
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
