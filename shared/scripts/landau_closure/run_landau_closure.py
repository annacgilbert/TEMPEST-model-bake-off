"""Reproduce the numbers in shared/docs/landau_3d_closure.tex.

Usage:  python run_landau_closure.py [MAX_DEGREE]      (default 16; 12 runs in under a minute)

Builds the linearized like-particle Landau matrix for each truncation degree (cached as
.npy files in ./cache, which is not tracked by git), validates it, and prints
  1. the Dougherty check of the same machinery (expected kF = 5/6, eta = 1/2, Kexact = 2/15);
  2. the Landau Chapman-Enskog constants per degree (Braginskii: kappa = 3.906, eta0 = 0.96);
  3. the quasi-static closure chi/kappa_F versus k*lambda with the proved bounds;
  4. the two-sided estimates of the leading-coefficient theorem;
  5. the positivity range k^2 kF eta < 3 and the perpendicular-temperature ratio.
Units: n = m = v_t = 1 with v_t = sqrt(T/m); Braginskii like-particle collision time tau = 1.
Deterministic: no random numbers are used."""
import os, sys, time
import numpy as np
from scipy.integrate import quad
from landau3d import landau_matrix
from closure3d import constants, theta, dougherty, second_order, temperatures

HERE = os.path.dirname(os.path.abspath(__file__)); CACHE = os.path.join(HERE, "cache")

def landau(d):
    os.makedirs(CACHE, exist_ok=True); f = os.path.join(CACHE, f"landau_d{d}.npy")
    if os.path.exists(f): return np.load(f)
    t0 = time.time(); B, L, chk = landau_matrix(d)
    assert abs(chk - np.sqrt(2 / np.pi)) < 1e-9, "quadrature self-check failed"
    np.save(f, L); print(f"  built Landau matrix d={d} ({len(B)} functions) in {time.time()-t0:.0f}s")
    return L

def theta3_dougherty(y):
    """Closed form of dougherty_closure_theorem.tex, three velocity dimensions."""
    a = 1 / y**2; E = lambda s: np.exp(a * (s + np.log1p(-s)))
    I = lambda f: quad(f, 0, 1, limit=400, epsabs=0, epsrel=1e-12)[0]
    return I(lambda s: s * (3 - 2 * s) * E(s)) / I(E) / y

def main(dmax):
    degs = [d for d in (6, 8, 10, 12, 16) if d <= dmax]
    print("1. Dougherty (nu = 1) through the same code; expect kF = 0.833333, eta = 0.5, Kexact = 0.133333")
    for d in degs[-2:]:
        c = constants(dougherty(d), d)
        print(f"   d={d:2d}: kF={c['kF']:.6f} eta={c['eta']:.6f} Kexact={c['Kexact']:.6f}")
    d = degs[-1]
    print("   Galerkin closure versus closed form:   k    chi/kF Galerkin    closed form")
    for k in (0.05, 0.2, 0.5, 1.0, 2.0):
        print(f"      {k:5.2f}   {theta(dougherty(d), d, k)[0]/k/(5/6):.6f}         {theta3_dougherty(1/k)/k/(5/6):.6f}")

    print("\n2. Landau, like-particle (tau = 1); Braginskii values kappa = 3.906, eta0 = 0.96")
    print("    d   kappa_F     eta       C*    <theta,L+chi*>   Kexact   Kbound   max|L h|, h in kernel")
    Ls = {}
    for d in degs:
        Ls[d] = landau(d); c = constants(Ls[d], d)
        print(f"   {d:2d}   {c['kF']:.5f}   {c['eta']:.5f}   {c['Cs']:.3f}     {c['X0']:.3f}        {c['Kexact']:.2f}    {c['Kbound']:.2f}      {c['kern']:.0e}")

    c = constants(Ls[degs[-1]], degs[-1]); kF, Cs, eta, Kex = c["kF"], c["Cs"], c["eta"], c["Kexact"]
    Xm = np.sqrt(12 * eta * Cs)
    print(f"\n3. Landau closure. X_max = {Xm:.3f}; upper bound valid for k*lambda < {np.sqrt(3/(kF*Xm)):.3f}; Kexact/kF^2 = {Kex/kF**2:.3f}")
    print("   k*lam   chi/kF by degree " + str(degs[-3:]) + "      1-Kex k^2   lower     upper    bounds hold")
    for k in (0.005, 0.01, 0.02, 0.05, 0.1, 0.2, 0.3, 0.5, 1.0):
        r = [theta(Ls[d], d, k) for d in degs[-3:]]; x = r[-1][0] / k / kF
        lo = 1 / (1 + kF * (Cs + Xm / 3) * k * k); up = 1 / (1 - kF * Xm * k * k / 3) if kF * Xm * k * k / 3 < 1 else np.inf
        n1ok = 1 / (k * k * kF) - 1e-9 <= r[-1][1] <= 1 / (k * k * kF) + Cs + 1e-9
        print(f"   {k:5.3f}   " + "  ".join(f"{t[0]/k/kF:.5f}" for t in r) + f"      {1-Kex*k*k:8.5f}   {lo:.5f}   {up:.5f}   {lo <= x <= up and n1ok and abs(r[-1][4]) <= Xm}")

    print("\n4. Leading-coefficient theorem: C* - B k^2 <= n1 - 1/(k^2 kF) <= C*  and  |X - t eps X0| <= sqrt(12 eta B) k")
    for name, dd, L in (("Dougherty", min(14, degs[-1]), None), ("Landau", degs[-1], Ls[degs[-1]])):
        L = dougherty(dd) if L is None else L; o = second_order(L, dd)
        print(f"   {name} d={dd}: C*={o['Cs']:.4f} X0={o['X0']:.4f} B={o['B']:.4f} Kexact={o['kF']*(o['Cs']-o['X0']/3):.5f}")
        for k in (0.003, 0.01, 0.03, 0.1):
            t = theta(L, dd, k); eps = k * k * o["kF"]; dn = t[1] - 1 / eps
            te = 1 / (1 - eps * o["Cs"] + eps * k * k * o["B"])
            ok1 = o["Cs"] - o["B"] * k * k - 1e-4 <= dn <= o["Cs"] + 1e-4      # 1e-4: rounding in n1 - 1/eps
            ok2 = abs(t[4] - te * o["X0"]) <= np.sqrt(12 * o["eta"] * o["B"]) * k
            print(f"      k={k:5.3f}  n1-1/eps={dn:9.5f}  {ok1}   |X-t eps X0|={abs(t[4]-te*o['X0']):.5f}  {ok2}")

    print("\n5. Positivity (landau_positivity.tex): proved for k < sqrt(3/(kF eta)); T_perp1/n1 should lie in [-1, 0]")
    for name, dd, L in (("Dougherty", 80, dougherty(80)), ("Landau", degs[-1], Ls[degs[-1]])):
        cc = constants(L, dd); kc = np.sqrt(3 / (cc["kF"] * cc["eta"]))
        print(f"   {name} d={dd}: kF*eta = {cc['kF']*cc['eta']:.4f}, proved range k < {kc:.3f}")
        print("       k    T_perp1/n1   -T1/n1   N(theta)/(9 n1)   -T1 >= 1/(k^2 kF) - eta/3")
        for k in (0.1, 0.3, 0.5, 0.8, 1.0, 1.5, 2.0, 3.0, 5.0):
            t = temperatures(L, dd, k); lb = 1 / (k * k * cc["kF"]) - cc["eta"] / 3
            print(f"     {k:4.1f}   {t['Tperp']/t['n1']:8.4f}   {-t['T1']/t['n1']:7.4f}     {t['Ntheta']/(9*t['n1']):7.4f}          {-t['T1'] >= lb - 1e-9}")

if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 16)
