# Validation record

17 November 2026. Run from this manuscript directory. The Python executable was
`/Users/ag245/.pyenv/versions/3.13.0/bin/python3`; the saved metrics record the
complete platform, NumPy and SciPy versions and source hashes. The configuration
is `config.json`, with seed 0 and no stochastic sampling.

## Executed computations

| Command (Python executable abbreviated as `python`) | Outcome |
| --- | --- |
| `python -m unittest -v test_numerics.py` | Four tests passed in approximately 0.12 seconds |
| `python reproduce.py --output results/2026-11-17` | Complete; approximately 5.74 seconds; existing matrices used where available |
| `python reproduce.py --output results/2026-11-17-fresh --rebuild-landau` | Complete; approximately 261.84 seconds; every Landau degree rebuilt |
| `python extra_checks.py results/2026-11-17-fresh/metrics.json --output results/2026-11-17-fresh/verification.json --compare-metrics results/2026-11-17/metrics.json` | Complete; approximately 5.69 seconds |
| `python make_figures.py results/2026-11-17-fresh/metrics.json` | Generated three vector figures and four numerical table fragments |

The fresh run is the numerical source for the delivered paper. The archived
`extra_checks.json` was produced by an earlier version of the auxiliary check
script; the configurable current version reproduced its numerical checks in
`verification.json`. No result file was overwritten.

## Numerical checks and limits

- Independent BGK evaluations agree to `6.7e-16`; the one-dimensional Dougherty
  integral and Hermite stationary solves agree to `1.2e-16` at the tested points.
- The three-dimensional Dougherty integral and degree-32 stationary solve agree
  to `1.8e-14` at the five tested wavenumbers.
- Fresh and cached Landau transport constants agree at every stored digit for
  degrees 6, 8, 10, 12 and 16. This verifies the archived assembly, not continuum
  convergence.
- The radial normalization check differs from `sqrt(2/pi)` by `6.7e-16`.
  Matrix asymmetry is at most `4.4e-15` in the checked caches.
- The maximum stationary mass residual is `1.1e-12`. The maximum absolute flux
  residual is `2.4e-8`, across wavenumbers including 0.005 where the target flux
  magnitude is 200. Degree refinement remains the significant response error.
- Landau degree 12 versus 16 gives a conductivity-ratio difference about
  `1.5e-3` at `k*tau=0.3`; six continuum digits are not claimed there. The
  curvature constant converges less quickly than the conductivity.
- Embedded Hermite degree 64 versus 128 history differences are below `1e-13`.
  Matrix-exponential actions avoid a time-step approximation. Doubling output
  intervals changes the history error by at most `1.38e-6`.
- Kinetic and closed systems preserve the tested zero mode exactly and decrease
  their respective quadratic energies. These are linear checks, not nonlinear
  positivity/realizability tests.
- The quasi-static closure's history errors are approximately 2.03%, 23.68%,
  and 33.80% at `k/nu=0.1,1,3`. They are retained and interpreted as model error,
  not hidden as numerical nonconvergence.
- No ensemble or learning uncertainty applies. No certified continuum error
  bars, unconditional Landau collisionless limit, or global Landau positivity
  theorem is inferred from these runs.

## Build and visual checks

The paper was built with:

```sh
latexmk -pdf -interaction=nonstopmode -halt-on-error -outdir=tmp/latex manuscript.tex
pdftoppm -r 110 -png tmp/latex/manuscript.pdf tmp/pdfs/final
pdftotext -layout tmp/latex/manuscript.pdf tmp/pdfs/manuscript.txt
```

The final PDF has 22 pages. Final checks include all rendered pages, readable figure axes and legends,
unbroken table rows, bibliography and theorem cross-references, and the absence
of overfull boxes, unresolved references, or LaTeX warnings. Intermediate
renderings and build logs remain in the ignored `tmp/` directory. The final
PDF is copied to `output/pdf/manuscript.pdf`.

## Failures and repairs during preparation

- The shell initially selected a different Python without SciPy. Numerical
  commands were rerun with the explicit Python 3.13 executable above. This was
  an environment-selection failure; no scientific run was discarded.
- An initial TeX build had a package-order conflict between theorem and math
  fonts; loading the theorem package before the font package resolved it.
- Another initial TeX build exposed a doubled subscript in the dimensional
  conductivity notation; the notation was corrected.
- Layout review enlarged figure labels, separated the rollout legend from the
  curves, kept the scope table before the bibliography, and removed an
  unnecessary float barrier that left a large blank area.

Both primary numerical runs completed with empty failure lists. The Landau
proof boundaries and corrected normalization are documented separately in
`SOURCE_AUDIT.md` and in the manuscript itself.
