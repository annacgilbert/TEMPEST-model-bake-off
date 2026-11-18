# Source and mathematical audit

Prepared 17 November 2026. All source notes are preserved in the parent
directory. Their SHA-256 hashes are recorded in `source_manifest.json`.
The manuscript reorganizes and rederives the material rather than concatenating
the notes. It makes no priority claim.

## Source map

| Source note | Role in the manuscript |
| --- | --- |
| `closure_models_tutorial.tex` | Motivation, hierarchy, and the role of information discarded by closure |
| `hammett_perkins_closure_derivation.tex` | Potential-drive transfer function, collisionless reference, flux convention |
| `plasma_closure_gaps_and_bgk_theorem.tex` | Constant-BGK response, strict Fourier bound, intermediate-regime comparison |
| `bgk_velocity_dependent_closure.tex` | Conserving weighted projection, dual bounds, speed-dependent example |
| `dougherty_closure_theorem.tex` | Conserving diffusion model, positive integral formulas, exact asymptotes |
| `landau_3d_closure.tex` | Stress cross term, Landau form, Galerkin constants |
| `landau_solvability.tex` | Weighted collision inverses and stationary realization |
| `landau_quasistatic_limit.tex` | Regularized resolvent and ordered low-frequency limit |
| `landau_positivity.tex` | Improved finite-wavenumber positivity criterion |
| `landau_collisionless_limit.tex` | Airy-layer candidate and conditional large-wavenumber argument |
| `summary_of_results.tex` | Cross-check of the chronology and reported constants |

The broader `PROJECT_BRIEF`, `mathematical_closure_program`, benchmark
specification, and decisions document informed the error accounting and the
separation of analytic response tests from embedded-solver tests.

## Reconciliations and proof boundaries

1. **Physical heat flux in every dimension.** The one-dimensional notes use the
   third central moment, twice the physical energy flux used by the
   three-dimensional notes. The manuscript uses
   `Q_d = v_x (|v|^2 - d - 2)/2` throughout. In one dimension the conductivity,
   response multiplier, and collisionless coefficient are halved. The relative
   deficit coefficient `K` is unchanged, so `K/kappa_F^2` is multiplied by four.
   A mixed-convention cross-dimensional spread is not repeated. The meaningful
   Landau-to-Dougherty three-dimensional curvature ratio is approximately 7.45.

2. **A specified response, not an arbitrary constitutive law.** The response is
   driven by a potential force from equilibrium, with frequency tending to zero
   first at fixed nonzero wavenumber. At exactly zero frequency the driven
   temperature and heat flux both vanish; the coefficient is their leading
   slow-frequency ratio. Initial conditions or different velocity-space sources
   change the transfer relation. The new embedded test makes this limitation
   quantitative.

3. **Conserving collision models.** Speed-dependent BGK requires the projection
   in the collision-frequency-weighted Gaussian inner product. Ordinary BGK
   projection with a variable rate would generally violate conservation.
   Dougherty restores the momentum and energy invariants; it is not an operator
   with eigenvalue `nu*n` on every Hermite mode. Its three-dimensional stress
   modes still have eigenvalue `2*nu`.

4. **One-dimensional and three-dimensional proofs differ.** In one dimension,
   longitudinal momentum conservation gives `T_1 = -n_1`. In three dimensions a
   stress cross term enters. The latter permits a finite-wavenumber positivity
   criterion but does not supply the same global Fourier upper bound. The
   manuscript keeps the cross term in both the bound and the leading deficit.

5. **Low-frequency proof repaired.** The implication
   `|omega|/sqrt(Im omega) -> 0` does not follow from
   `|omega|^2 <= Gamma Im omega`. The revised proof instead uses the uniform
   weighted estimate to make the weak frequency term vanish. The approach set
   is parabolic, not a linear angular sector. No real-axis limiting-absorption
   statement is inferred. The weighted coercivity and diffusion estimates are
   explicitly attributed to the primary analytical literature.

6. **Landau collisionless claim made conditional.** The Airy profile and its
   normalization alone do not control the nonlocal collision contribution,
   transverse tails, and sharp inverse-form estimates uniformly. The manuscript
   states the precise trial and inverse-form limits needed by the deduction,
   proves the deduction under those hypotheses, and leaves their verification
   open. Neither all-wavenumber Landau positivity nor an unconditional
   collisionless limit is claimed.

7. **A numerical threshold is not a certified threshold.** The exact sufficient
   condition is `k^2*kappa_F*eta < 3`. The approximate cutoff 0.887 is obtained
   from finite-dimensional values. Variational estimates of the two constants
   are lower bounds and cannot certify that cutoff. Refinement differences are
   not promoted to continuum confidence intervals.

8. **Harmonic interpolation has the wrong first correction.** Its conductivity
   deficit begins at order `|k|`, whereas the exact models begin at order `k^2`.
   It therefore underestimates every covered model sufficiently close to zero.
   The speed-dependent BGK overestimate is an intermediate-wavenumber sign
   reversal, not an opposite sign at every wavenumber.

9. **Like-particle Landau normalization is explicit.** The manuscript defines
   the collision form and its time scale. Its scalar coefficients are not
   identified without conversion with electron-ion Spitzer-Harm transport,
   magnetic transport, or a multispecies collision model.

## Added evidence and interpretation

- Fresh Landau matrix assembly through polynomial degree 16, compared with the
  original cached calculations, and machine-readable provenance.
- Positive-integral evaluations, independent rank-three BGK quadrature,
  independent Hermite stationary solves, and numerical limit checks.
- A deterministic embedded kinetic/moment experiment, with degree refinement,
  output-sampling refinement, zero-mode conservation, and energy decay.
- Figures and numerical tables generated from saved metrics. Numerical,
  asymptotic, and model-form errors are discussed separately.
- A benchmark discussion that keeps the classical transport operator explicit
  and treats learning as an identified correction; no training or learned-model
  performance is claimed.

## Literature verification

The bibliography was checked against publisher records, author-hosted papers,
and arXiv primary manuscripts. Particularly relevant are the Hammett-Perkins
and Snyder response conventions, Struchtrup's conserving variable-rate BGK
model, the Kogelbauer-Karlin distinction between response and invariant
hydrodynamic closure, and the Mouhot and Kim-Guo-Hwang weighted Landau
estimates. The latter's numbered estimates refer explicitly to
arXiv:1610.05346v2. Carrapatoso-Mischler is identified as the consulted arXiv
version rather than assigned unverified journal metadata. The Dougherty
publisher record supplies bibliographic metadata; the manuscript's exact
response formula is independently derived in Appendix B.
