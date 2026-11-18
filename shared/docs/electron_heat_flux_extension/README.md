# Thermally driven heat flux with electron-ion collisions

A 12-page companion note that pushes the results of the
[plasma heat-flux paper](../plasma_heat_flux_paper/README.md) toward the
electron heat-flux problem. The paper and its validated bundle are unchanged.

- [Read the note](output/pdf/note.pdf); [LaTeX source](note.tex).
- [Plan and evidence boundaries](PLAN.md).
- [Configuration](config.json) and [saved metrics](results/2026-11-17/metrics.json).

## What is new

1. With an isotropic heating source in place of the potential force, the
   temperature response is a diagonal resolvent entry. The one-dimensional
   variational argument then works in three dimensions and gives
   `kappa/(1 + K k^2) <= chi <= kappa` at every wavenumber, with `K` the sharp
   leading coefficient, for any symmetric nonnegative collision operator whose
   kernel contains `1` and `|v|^2`. Momentum conservation is not required.
2. The potential and thermal responses are two entries of one positive-definite
   2x2 parallel/perpendicular matrix. They share `kappa` and differ at order `k^2`.
3. Exact thermally driven Dougherty response: `K = 16/(45 nu^2)` and
   collisionless coefficient `(9/5) sqrt(2/pi)`.
4. Electron-electron Landau plus Lorentz scattering on ions of charge `Z`:
   zero-current conductivity, deficit coefficient and response curves for
   `Z = 1 ... 64`.
5. Embedded test: decay of a temperature perturbation in the quasi-neutral,
   zero-current kinetic model against the closed temperature equation.

## Validation

- Degree 6 reproduces Braginskii's electron coefficients: heat conductivity
  3.1616, 4.890, 6.064, 6.920 for `Z = 1, 2, 3, 4`; for `Z = 1`, electrical
  conductivity 1.9499 (Braginskii 1.9497) and thermoelectric ratio 0.7110.
  The reference values are quoted from memory of Braginskii's table and should
  be checked against the source before circulation.
- `Z = 4096`, degree 16: within 0.11% and 0.04% of the closed-form Lorentz
  limits `128/(3 pi)` and `32/(3 pi)`.
- The Lorentz matrix satisfies its exact identities to about 1e-14.
- The proved bounds hold at every computed point.
- The Dougherty closed form agrees with the Galerkin solve to 4e-13.

## Reproduce

Run from this directory in a checkout of the full repository. Python 3 with the
packages in `requirements.txt`. The scripts use the modules in
`../../scripts/landau_closure/` and import none of the project packages.

```sh
python3 -m unittest -v test_electron_numerics.py
python3 reproduce.py --output results/my-run            # add --rebuild-landau to ignore the cache
python3 make_figures.py results/my-run/metrics.json
mkdir -p tmp/latex output/pdf
latexmk -pdf -interaction=nonstopmode -halt-on-error -outdir=tmp/latex note.tex
```

`reproduce.py` refuses to overwrite a run directory. With cached Landau
matrices the tests take about 1 s and the run about 1 s; without the cache the
Landau matrices are rebuilt (a few minutes for degree 16). The delivered run
used the existing cache, whose file hashes are recorded in `metrics.json`. No
random numbers are used; seed 0 is recorded.

## Limits

- Linear, homogeneous Maxwellian background, one Fourier direction,
  unmagnetized, immobile ions.
- Theorems assume form-domain solvability; no weighted existence proof is given
  for the electron operator.
- Polynomial Galerkin convergence is slow for the `1/v^3` Lorentz rate. Degree
  differences are diagnostics, not certified error bars; `K` is good to about
  two digits, and curves beyond `k lambda_e` of about 0.1 are not converged at
  large `Z`.
- No learned models, so no ensemble or training error.
