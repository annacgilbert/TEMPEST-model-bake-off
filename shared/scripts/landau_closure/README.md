# Landau closure scripts

Code behind the numbers in `shared/docs/landau_3d_closure.tex`. It is a
standalone numerical check, not part of any project package.

| File | Purpose |
|---|---|
| `landau3d.py` | Linearized like-particle Landau collision matrix in the polynomial basis `psi_n(v_x) L_m(v_perp^2/2)`, `n + 2m <= d`, by Gauss quadrature that is exact for the integrand. |
| `closure3d.py` | Chapman-Enskog constants, the proved bounds, and the quasi-static closure from the Galerkin solve; also the Dougherty operator in the same basis. |
| `run_landau_closure.py` | Reproduces the tables in the note. |

## Run

```bash
cd shared/scripts/landau_closure
python run_landau_closure.py        # degrees up to 16, about 5 minutes on first run
python run_landau_closure.py 12     # under a minute
```

Requires `numpy` and `scipy`. No random numbers are used. Matrices are cached
in `cache/`, which is ignored by git; delete it to rebuild.

## What it checks

- The quadrature reproduces `E[1/|u|] = sqrt(2/pi)`.
- The Landau matrix annihilates `1`, `v_x`, `|v|^2`.
- Conductivity and viscosity against Braginskii's `3.906` and `0.96`.
- With the Dougherty operator, `kappa_F = 5/6`, `eta = 1/2`, and the
  leading coefficient `2/15`; the Galerkin closure against the closed form.
- The two-sided estimates used in the proof of the leading-coefficient
  theorem, for both operators.

## Limits

- Like-particle collisions only; no electron-ion scattering.
- A polynomial basis converges only for `k*lambda` up to about 1.
- The Landau values are converged in the truncation degree but carry no
  error bound.
