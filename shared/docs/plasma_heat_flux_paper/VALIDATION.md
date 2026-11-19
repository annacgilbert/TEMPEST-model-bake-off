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

## Merge of the extension note (17 November 2026)

The thermal-drive and electron-ion note was merged into `manuscript.tex` as
Sections 7, 8 and 10, with the abstract, introduction, discussion,
conclusions and claims table rewritten for the merged scope. No computation
was rerun and no run directory was touched; the new tables and figures are
read from `../electron_heat_flux_extension/figures/`. The transformation
renamed thermal quantities (`T_th`, `K_th`, `C_th`, `b_th`) and prefixed the
note's labels; it was scripted so that the mathematics was not retyped.
The merged PDF has 33 pages, builds with no undefined references and no
overfull boxes, and the pages containing new material (13-17 and 21-27) were
reviewed at reduced resolution for layout, not re-read line by line in the
PDF. The text of pages 13-17 (Sections 7 and 8) was subsequently proofread in
full from the PDF and every cross-reference there resolves to the intended
equation or theorem.

Reference check, 18 November 2026 (web search of secondary sources; the
printed originals were not consulted):

- Braginskii, Reviews of Plasma Physics vol. 1, pp. 205-311, ed. Leontovich,
  Consultants Bureau 1965: confirmed by the NASA ADS record
  1965RvPP....1..205B.
- Epperlein and Short, Phys. Fluids B 3, 3092-3098 (1991): confirmed by OSTI.
- Helander and Sigmar, Cambridge University Press 2002: confirmed.
- Braginskii's Z = 1 coefficients 0.5129, 0.7110 and 3.1616: confirmed by
  Hunana et al., arXiv:2201.11561, which also lists the heat-conductivity row
  3.1616, 4.890, 6.064, 6.920 (the snippet seen had no column heads, so the
  assignment to Z = 1, 2, 3, 4 is by order).
- Spitzer-Harm heat conductivity at Z = 1: 3.203 in the same source,
  consistent with "about 3.20" in the text and above the degree-16 value
  3.1967, as a lower bound requires.
- Not confirmed: the Spitzer-Harm electrical conductivity "about 1.98".

## Landau collisionless limit promoted to a theorem (18 November 2026)

Section 6.2 now states Theorem 6.2 and Corollary 6.3; Appendix D is the
proof; Corollary 7.8 is the thermal-drive consequence. See `PLAN.md` and
the last section of `SOURCE_AUDIT.md` for scope and for what was and was
not checked. No Galerkin computation was rerun and no result directory was
touched. The Galerkin method does not reach the collisionless layer, so the
limit itself has no numerical confirmation for Landau; at `k lambda = 5` the
source note reports `-T_1/n_1 = 0.396` against the limiting `1/3`.

Profile identities of Lemma D.2, by quadrature:

```
python3 extra_airy_check.py        # about 9 minutes, single core
ODE residual (max over [0.0, 0.3, 1.0, 2.5, 6.0]): 2.22e-16
int F = 3.14159265   (pi = 3.14159265)
int F'^2 + W'^2 = 3.14159265
int_u^inf tF + W'(u) at u=1.3: -1.67e-12
u^4 F at u=40: -2.00000   u W at u=40: -1.00000
```

The output is printed, not saved; the two integrals over `u` use a
trapezoid rule on `[0, 400]` with spacing `0.005` plus the analytic tails.

Build: `latexmk` as above, 39 pages, no undefined references and no
overfull boxes. Pages 12 and 33-37 were read from the PDF.

## Solvability, electron limit and response matrix (18 November 2026)

Manuscript: Proposition 6.4 and Section 6.3, Proposition 8.1, Corollary 8.2,
Theorem 8.3, Table 8, Appendices C.4 and D.6. See `PLAN.md` and
`SOURCE_AUDIT.md`.

Computation (deterministic, cached Landau matrices, under one second):

```
python3 response_matrix.py run results/2026-11-18-matrix
python3 response_matrix.py constants results/2026-11-18-matrix
python3 response_matrix.py table results/2026-11-18-matrix/metrics.json figures
```

- `metrics.json`: status complete, 0 failures over 14 solves (degrees 12
  and 16, seven wavenumbers). In-script checks at every solve: symmetry and
  vanishing imaginary part below 1e-9, positive definiteness,
  `M_par,par = n_1` and the potential-driven conductivity against the shared
  `closure3d.theta`.
- `constants.json`: `C_perp = 8.0084` (degree 12), `8.0097` (degree 16);
  criterion `k^2 kappa_F C_perp < 3` gives `k < 0.308`, against `0.887` from
  `k^2 kappa_F eta < 3`. A negative result, reported in Section 6.3.
- `figures/landau_matrix.tex` is generated from `metrics.json`
  (`figures/provenance_matrix.json`). Degree 12 to 16 changes reach 3.8e-2
  of `M_par,par` at `k tau = 5`; a diagnostic, not a certified bound.
- The `constants` subcommand was added to the script after `run` wrote
  `metrics.json`, so the script hash stored in `metrics.json` is that of the
  earlier version; the `run` code path was not changed.
- The table agrees with the one in `landau_positivity.tex`.

Not validated numerically: Theorem 8.3 and Corollary 7.8 (the basis does
not reach the layer). At `k tau = 5` the like-particle values are
`|k| M = (1.188, 0.112, 1.343)` against the limit `(1.253, 0, 1.253)`.

Build: 45 pages, no undefined references, no overfull boxes. Pages 13,
18-19, 27, 34-35 and 40-42 were read from the PDF.

## Stieltjes structure (18 November 2026)

Manuscript: Section 7.6 (Theorem 7.9, Corollary 7.10, Proposition 7.11,
Corollary 7.12) and Section 10.5. See `PLAN.md` and `SOURCE_AUDIT.md`.

Computation (deterministic except a seeded random model, seed 0; cached
Landau matrices; 0.56 s):

```
python3 stieltjes_check.py results/2026-11-18-stieltjes
```

- `metrics.json`: status complete, 0 failures. 31 cases covered by the
  theorem: closed-form 1D BGK, 1D Dougherty and 3D thermal Dougherty;
  thermal Galerkin responses for Dougherty, Landau and electrons (`Z = 1`,
  `8`) at degrees 12 and 16; 20 random finite-dimensional models. In every
  case `Im chi <= 0` at all sampled points of the upper half `k^2`-plane
  (largest `Im chi/|chi|` over all cases: -1.0e-3), `chi` decreases and
  `k^2 chi` increases on the real axis.
- Sampling: 56 complex points, radii 0.01 to 30, angles 0.1 pi to 0.9 pi;
  11 real points. The closed-form Dougherty integrals converge only for
  `Re k^2 > -1`, so 11 points with `Re k^2 <= -1/2` were skipped for those
  three closed forms (45 sampled). The Galerkin Dougherty runs cover the
  skipped region.
- Thermal Dougherty: `K = 16/45` and `K_2 = 499/2025` in exact rational
  arithmetic; quadrature agrees to 1e-14. The Pade bounds hold at all seven
  tested wavenumbers; the upper bound is 0.06% above the exact response at
  `k^2 = 0.3` and 1.0% above at `k^2 = 1`.
- Not covered by the theorem, reported as observed: the potential-driven
  response in three dimensions. Dougherty (closed form and Galerkin)
  satisfies all sign conditions at every sampled point. Landau Galerkin
  violates `Im chi <= 0` at two points each degree, all at angle 0.9 pi:
  radii 1 and 10 at degree 12, radii 3 and 30 at degree 16. The violating
  points are not stable under refinement; nothing is claimed for the
  continuum.
- A first trial run (scratch directory, not kept) sampled the Dougherty
  closed forms where the integrals diverge and reported spurious
  violations. The sampling restriction above was added because of it.

Not validated: the continuum hypotheses of Theorem 7.9 (the Galerkin and
random-model cases satisfy the theorem exactly, so they test the code and
the algebra only). The measure `rho` was not computed.

Citations: the SNB reference was confirmed against secondary listings
(Phys. Plasmas 7, 4238-4249, 2000). The Schilling-Song-Vondracek book was
confirmed as to edition, year, series and chapter titles; the analytic
characterization of Stieltjes functions is cited by chapter, and the
corollary number was not checked against the book.

Build: 48 pages, no undefined references, no overfull boxes. Pages 18-21
were read from the PDF.

## Large ion charge (18 November 2026)

Manuscript: Section 8.1 (Theorems 8.4 and 8.5), Section 10.6, Table 9,
Figure 5, Appendix E. See `PLAN.md` and `SOURCE_AUDIT.md`.

Computation (deterministic; cached Landau matrices for the comparison
only; 0.27 s):

```
python3 large_z.py run results/2026-11-18-largez
python3 large_z.py figures results/2026-11-18-largez/metrics.json figures
```

- `metrics.json`: status complete, 0 failures.
- Radial solver sanity, six refinement levels (degrees 16 to 64 at 320
  panels, degree 64 at 160): kernel residual at most 2.7e-12, symmetry
  defect of the nonlocal term at most 2.0e-12, smallest eigenvalue above
  -5e-14, source orthogonal to the invariants to 2e-16, and the quadrature
  of `<w phi_0^2>` equal to `64 sqrt(2)/(3 pi)` to rounding.
- Independent cross-check: eigenvalues of the radial form on even
  polynomials of degree at most 12 and 16 against the radial block of the
  cached three-dimensional Landau matrices (radial subspace = null space of
  the Lorentz matrix): largest difference 1.1e-14 and 1.6e-14.
- `C_inf = 13.7378205766`, `C_inf/kappa_L = 1.4305202`,
  `kappa_L C_inf = 131.92943`. Degrees 32, 48, 64 agree to 12 digits; 160
  against 320 panels to 12 digits. Observed convergence, not a certified
  bound.
- Small `s`: `(1 - X/kappa_L)/s` = 131.85 at `s = 1e-6`, 131.17 at 1e-5,
  125.0 at 1e-4, 91.8 at 1e-3, against the predicted limit 131.93. The
  value at `s = 1e-7` (132.07) is rounding-limited.
- Three-dimensional Galerkin against the limit (Table 9): at `Z = 4096`,
  `Z kappa/kappa_L = 0.9989`, `C_th = 13.736`, `K/(kappa^2 Z) = 1.432` at
  degree 16; degree 12 gives 13.790 and 1.438. `Z kappa` increases with `Z`
  at both degrees, and the thermoelectric ratio tends to 3/2 (1.4993).
- Curves (Figure 5): `Z chi_th <= X(s)` at all sampled points with
  `s <= 10` for `Z = 4, 16, 64, 256` and both degrees; largest ratio 0.988.
  For `s` above about 1 the degree-12 and degree-16 curves separate (ratio
  to the limit 0.62 against 0.83 at `s = 10`, `Z = 256`).
- Large `s`: local exponent of `X` is -0.398, -0.399, -0.385, -0.364,
  -0.343, -0.325 on successive decades from 1 to 1e6; `X` changes by up to
  5.7e-4 between degrees 48 and 64 there.

Failures and reruns, kept on the record:

- First trial (scratch directory, not kept): the nonlocal term was
  integrated with a tensor quadrature across the kink of
  `min(a,b)/max(a,b)^2`. The script's own sanity checks failed (kernel
  residual 6e-6, spectrum mismatch 5e-5). The inner integral is now split
  at the kink and done with running integrals; the same checks pass at
  1e-12 or better. `C_inf` moved from 13.73785 to 13.73782.
- First recorded-run attempt stopped on a variable-ordering error before
  the result directory was created; nothing was written.
- The figure legend position was changed after `run`, so the script hash
  inside `metrics.json` is that of the earlier version; the `run` code path
  did not change. `figures/provenance_large_z.json` has the current hash.

Not validated numerically: the error term `E(s)` of Theorem 8.5 (it needs
the like-particle form on an `l = 1` function, which the radial solver does
not have), and the `O(1)` term of the linear law.

Build: 54 pages, no undefined references, no overfull boxes. Pages 22-23,
32-33 and 48-51 were read from the PDF.
