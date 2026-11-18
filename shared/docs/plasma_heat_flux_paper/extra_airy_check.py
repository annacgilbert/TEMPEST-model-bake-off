"""Quadrature check of the boundary-layer profile identities (Lemma D.2).

gamma(u) = int_0^inf exp(-i u t - t^3/3) dt = F + i W.
Prints the residuals of the identities used in Appendix D. No output file.
Run: python extra_airy_check.py
"""
import numpy as np
from scipy.integrate import quad


def moment(u, p, trig):
    """int_0^inf t^p trig(u t) exp(-t^3/3) dt (integrand < 1e-70 at t = 8)."""
    return quad(lambda t: t**p*trig(u*t)*np.exp(-t**3/3), 0, 8,
                epsabs=1e-13, epsrel=1e-13, limit=2000)[0]


F = lambda u: moment(u, 0, np.cos)
W = lambda u: -moment(u, 0, np.sin)
dF = lambda u: -moment(u, 1, np.sin)
dW = lambda u: -moment(u, 1, np.cos)
d2F = lambda u: -moment(u, 2, np.cos)
d2W = lambda u: moment(u, 2, np.sin)

us = [0.0, 0.3, 1.0, 2.5, 6.0]
ode = max(max(abs(-u*W(u)-d2F(u)-1), abs(u*F(u)-d2W(u))) for u in us)
U = 400.0
grid = np.linspace(0, U, 80001)
Fv = np.array([F(u) for u in grid])
dFv = np.array([dF(u) for u in grid])
dWv = np.array([dW(u) for u in grid])
# tails beyond U from the expansions F ~ -2/u^4, W' ~ 1/u^2, F' ~ 8/u^5
intF = 2*(np.trapezoid(Fv, grid)-2/(3*U**3))
energy = 2*(np.trapezoid(dFv**2+dWv**2, grid)+1/(3*U**3))
u0 = 1.3
flux = quad(lambda t: t*F(t), u0, 60, limit=400)[0]-2/(2*60**2)
print(f"ODE residual (max over {us}): {ode:.2e}")
print(f"int F = {intF:.8f}   (pi = {np.pi:.8f})")
print(f"int F'^2 + W'^2 = {energy:.8f}")
print(f"int_u^inf tF + W'(u) at u={u0}: {flux+dW(u0):.2e}")
print(f"u^4 F at u=40: {40**4*F(40.0):.5f}   u W at u=40: {40*W(40.0):.5f}")
