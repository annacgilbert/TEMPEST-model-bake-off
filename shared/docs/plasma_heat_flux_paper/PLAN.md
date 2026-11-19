# Manuscript plan

17 November 2026. Scope: a self-contained mathematical research manuscript
on the potential-driven, linear, quasi-static kinetic-to-fluid heat-flux
closure, synthesized from the plasma closure notes in `shared/docs/`.
Preserve the source notes and the independent project packages.

1. Audit the notes, reconcile their chronology, and verify primary references.
2. Use the physical energy-flux convention in every velocity dimension;
   explicitly translate the doubled one-dimensional third-moment convention.
3. Develop a single resolvent formulation, a one-dimensional variational
   theorem, exact BGK/Dougherty examples, and three-dimensional stress bounds.
4. Give complete proofs of the central results and state the weighted
   analytical inputs for Landau. Present the Airy-layer collisionless
   argument conditionally where its uniform estimates remain unverified.
5. Reproduce the reported constants and closure curves with saved metrics,
   degree-refinement diagnostics, and fresh matrix checks. Add an inexpensive
   embedded linear moment/kinetic experiment to distinguish static response
   accuracy from transient closure accuracy. No learned-model results claimed.
6. Generate tables and scientific figures from those saved data, write an
   editable LaTeX manuscript and bibliography, compile, and visually inspect
   every page of the PDF. Record commands, environment, runtime and failures.

## Evidence boundaries

- No priority claim based on an incomplete literature search.
- No particle-to-Landau, nonlinear, multispecies, magnetic, or boundary theorem.
- Galerkin refinement differences are numerical diagnostics, not certified
  continuum error bars. In particular the numerical positivity threshold is
  not a rigorously certified threshold.
- A single-drive response ratio does not define an arbitrary-initial-data
  constitutive law. Embedded tests must expose this distinction.
- Deterministic calculations have no ensemble-estimation error; discretization,
  asymptotic truncation, and closure model error are reported separately.

## Deliverables

`manuscript.tex`, `references.bib`, final PDF under `output/pdf/`, standalone
reproduction scripts/configuration, small saved metrics, generated figures
and table fragments, a source/proof audit and a validation record.

Completed 17 November 2026: all six steps, including fresh matrix assembly,
embedded checks, the source audit, and visual review of all 22 final PDF pages.

## Merge of the thermal-drive and electron-ion extension (17 November 2026)

Scope: fold `../electron_heat_flux_extension/note.tex` into `manuscript.tex`
as new sections. No new computation; no change to either run directory.

1. New Section "The thermally driven response" after the Landau section:
   setting, dual certificates, bounds and leading coefficient, the 2x2
   parallel/perpendicular matrix, exact thermal Dougherty response.
2. New Section "Electron-electron and electron-ion collisions".
3. New numerical section after the existing one: Braginskii, Spitzer-Harm
   and Lorentz-limit validation, deficit coefficient versus ion charge,
   response curves, and the quasi-neutral embedded decay test.
4. Notation: thermal quantities carry a subscript (`T_th`, `K_th`, `C_th`,
   `b_th`, `chi_th`); `kappa` is the zero-current conductivity and equals
   `kappa_F` when momentum is conserved. Note labels are prefixed `th-`.
5. Rewrite abstract, introduction, discussion, conclusions, claims table
   and README for the merged scope. Statements that the potential-driven
   Landau positivity and Fourier bound are open stay as they are.
6. Figures and table fragments for the new sections are read from
   `../electron_heat_flux_extension/figures/` (generated there from
   `results/2026-11-17/metrics.json`), not copied, so there is one source.
   Their hashes are added to `source_manifest.json`.
7. Rebuild, check for undefined references and overfull boxes, and view the
   new pages. The extension directory keeps its code, tests, metrics and the
   standalone note.

Evidence boundaries of the extension carry over unchanged: conditional on
form-domain solvability, no weighted existence theorem for the electron
operator, Galerkin differences are diagnostics, slow polynomial convergence
at large `Z`. Reference values and the three added bibliography entries were
checked against secondary sources on 18 November 2026; see `VALIDATION.md`
for what was and was not confirmed.

## Promotion of the Landau collisionless limit to a theorem (18 November 2026)

Decision by the author after the reconciliation recorded in `SOURCE_AUDIT.md`.
Source: `shared/docs/landau_collisionless_limit.tex`. No new computation
except a quadrature check of the boundary-layer profile identities.

1. Replace the conditional proposition of Section 6.2 by a theorem
   (`k N_k(sigma) -> pi M_1(0) <sigma^2>_perp` for every even polynomial
   `sigma(v_perp)`) and a corollary: `|k| chi -> 3 sqrt(2/pi)` and positivity
   for all sufficiently large `|k|`, potential drive, like-particle Landau.
2. New appendix with the full proof: density of test functions in the form
   domain, the profile identities, two-sided variational bounds, the sharp
   dual-seminorm bound, and both trial evaluations with every lower-order
   term written out and a stated dominating function.
3. Add the two cited inputs to Appendix C as numbered estimates: the
   local-form comparison with a compactly supported remainder, and the
   bounds on the diffusion matrix. Check both against the published lemmas.
4. New consequence, not in the source note: for admissible trials the
   thermal source pairs as its restriction to `v_x = 0`, so the same theorem
   gives `|k| M(k) -> sqrt(pi/2) I` and `|k| chi_th -> (9/5) sqrt(2/pi)` for
   Landau, under the form-solvability assumption of the thermal section.
5. Update abstract, introduction, discussion, conclusions and claims table.

Evidence boundaries: no convergence rate and no explicit threshold (the
compactness step is not constructive); intermediate wavenumbers stay
numerical; the proof rests on cited operator estimates that are not
reproved; it has not had an independent human referee.

## Solvability, electron collisionless limit, and the response matrix (18 November 2026)

Requested by the author: items 1-3 of the next-steps list.

1. Thermal solvability. Extend Appendix C to (a) the thermal source and any
   even polynomial source with zero mean, and (b) the electron operator
   `Lambda_Z`. Key facts for (b): the Lorentz form is exactly local, it
   commutes with radial weights because `U(v) v = 0`, and coercivity on the
   complement of `span{1, |v|^2}` follows from the like-particle estimate
   plus a shell argument for the `v_x` direction. Result: the assumptions of
   the thermal section become a proposition for like-particle Landau and for
   `Lambda_Z`; positivity, the all-wavenumber bounds and the leading
   coefficient become unconditional (given the cited operator estimates).
2. Material from `landau_positivity.tex` not yet in the manuscript: the
   bound `chi <= 3 kappa_F` under `T_par <= T_perp <= 0`; the sufficient
   condition `N_theta < 9 n_1` with its collisionless value 8/9, now a
   proved limit; a table of the Landau response matrix up to `k lambda = 5`.
   Checked first whether the thermal bounds give a sharper proved positivity
   range: they do not (the candidate criterion `k^2 kappa_F C_perp < 3` gives
   `k lambda < 0.31`, worse than 0.887). This negative result is recorded.
3. Collisionless limit for `Lambda_Z`. Extend Appendix D: sources
   `sigma(v_perp) + v_x^2 p(v)`, no trial constraint, diffusion coefficient
   singular at `v_perp = 0` handled by a regularized layer width and a limit,
   flux lemma reproved without density of smooth functions.
4. Computation: `response_matrix.py` with `config_matrix.json`; new run
   directory `results/2026-11-18-matrix/`; table generated from its metrics.
   Sanity checks run inside the script before the table is written:
   symmetry, positive definiteness, `M_par,par = n_1` and the potential
   response against the shared `closure3d.theta`.

Evidence boundaries: the solvability argument is at the level of detail of
Appendix C and rests on the same cited estimates; the Galerkin table is a
diagnostic at degrees 12 and 16 and does not reach the layer; no proof here
has had an independent referee.

## Stieltjes structure of the thermal closure (18 November 2026)

Requested by the author: item 1 of the next-results list.

1. Theorem (new subsection at the end of the thermal section): for a real
   even source `s` whose pairing is bounded on the admissible even trials,
   `N_s(k) = sup <s phi>^2 / Q_k[phi]` is a Stieltjes function of `t = k^2`,
   and so is `1/(t N_s)`. Proof by complexifying the two quadratic forms
   (collision form `a`, streaming form `b`), Lax-Milgram off the negative
   axis, the identity `conj(N) = a[phi_z] + z b[phi_z]`, and the classical
   characterization of Stieltjes functions by the sign of the imaginary
   part. No operator estimate beyond those already used.
2. Consequences: `chi_th(k) = beta + int d rho(lambda)/(lambda + k^2)` with
   `rho >= 0`; `beta = 0` whenever `chi_th -> 0` (Dougherty, Landau,
   `Lambda_Z`); monotonicity of `chi_th` and of `k^2 chi_th`; the moments
   `int d rho/lambda = kappa`, `int d rho/lambda^2 = kappa K_th`; a positive
   real-space kernel that is a mixture of exponentials; the existing lower
   bound as the first Pade bound and an upper bound from the `k^4`
   coefficient. Same statements for the one-dimensional potential drive and
   for every diagonal form `c.M(k)c`; the potential drive in three
   dimensions is a difference of two such functions.
3. Check before writing (`stieltjes_check.py`, `config_stieltjes.json`, new
   run directory): sign of `Im chi` at complex `k^2` for the closed-form
   BGK and Dougherty responses, for Galerkin Landau and electron operators,
   and for a seeded random finite-dimensional model; monotonicity on the
   real axis; the Pade upper bound for Dougherty with its exact `k^4`
   coefficient. The potential-driven response in three dimensions is tested
   too and whatever it shows is reported.
4. Update abstract, introduction, Section 3 remark on the real-space
   kernel, discussion, conclusions, claims table, README, audit and
   validation records.

Evidence boundaries: the Galerkin and random-model checks test the algebra
and the code, not the continuum hypotheses; the characterization theorem
for Stieltjes functions is cited, not reproved; the measure `rho` is not
computed or bounded beyond its first two moments; no independent referee.

## Large ion charge (18 November 2026)

Requested by the author: item 2 of the next-results list. Units `tau_ee = 1`.

1. Structure used: `Lambda_ee` and the Lorentz operator commute with
   rotations, so `Lambda_Z` is block diagonal in the spherical-harmonic
   degree `l`, and on sector `l` it is `Lambda_ee + Z nu(v) l(l+1)/2` with
   `nu = 3 sqrt(pi)/|v|^3`. Radial functions do not see the ions at all.
2. Theorem (constants): `Z kappa` increases to the Lorentz value
   `kappa_L = 64 sqrt(2)/(3 pi)` with `O(1/Z)` error; `C_th -> C_inf`, the
   inverse form of the like-particle operator on the explicit radial source
   `b_inf^0 = (|v|^2-3)/3 - sqrt(pi/2) |v|^5 (|v|^2-8)/384`, with `O(1/Z)`
   error; hence `K_th/kappa^2 = (C_inf/kappa_L) Z + O(1)`.
3. Theorem (diffusive scaling limit): with `s = k^2/Z` fixed,
   `Z chi_th -> X(s) = 1/(s T_red(s))`, where `T_red` is the response of the
   radial problem `(Lambda_ee + s |v|^5/(9 sqrt(pi))) phi = zeta`. Two-sided:
   `T_red(s) <= T_th <= T_red(s) + E(s)/Z` for every `Z` and `k`, from the
   dual certificates with the radial trial and the `l = 1` dual trial
   `-k v_x phi_s/(Z nu)`. `X` is a Stieltjes function of `s` by Theorem 7.9.
4. Computation (`large_z.py`, `config_large_z.json`, new run directory):
   an independent radial Galerkin solver built from the angular reduction
   of the Landau form (polynomials in `|v|`, not `|v|^2`); cross-check of
   its spectrum against the radial block of the cached Landau matrices;
   `C_inf`, `X(s)`; comparison with the existing three-dimensional electron
   Galerkin constants and curves at increasing `Z`. Table and figure from
   the saved metrics.
5. Manuscript: new subsection in the electron section, proofs in a new
   appendix, numerical subsection, and the "not a theorem" paragraph on the
   `Z` scaling replaced. Update abstract, introduction, discussion,
   conclusions, claims table and the records.

Evidence boundaries: weighted-test and multiplier steps are at the level of
detail of Appendix C and rest on the same cited estimates; the large-`s`
behavior of `X` is not proved; the three-dimensional Galerkin values at
large `Z` converge slowly and are a consistency check, not a confirmation
to many digits; no independent referee.

## Remaining items: potential-drive sharpness, frequency response, rate (18 November 2026)

Requested by the author: the remaining items of the next-results list, with
the proof work delegated to three independent subagents. Each writes a
LaTeX fragment and a report outside the repository and its own script,
configuration and result directory here; none edits the manuscript or the
records. Integration, checking and the records are done afterwards in the
main session.

A. Sharpness of the potential-drive obstruction (item 4).
   - Candidate counterexample to the Fourier upper bound: BGK with a
     separate stress relaxation rate `nu_s` (the linearized ellipsoidal
     model). Sketch: `K = 16/(5 nu^2) - 4/(5 nu nu_s)`, negative for
     `nu_s < nu/4`. To be proved, checked against Dougherty (`2/15`) and
     numerically, and extended to the sign of `chi_pot`, condition (a) of
     Proposition 6.4 and the Stieltjes property at finite `k`.
   - `chi_pot >= chi_th` is equivalent to
     `2 M_perp,perp >= M_par,par + M_par,perp`; prove what can be proved
     (BGK, Dougherty, small and large `k`) and test the family above.
B. Frequency response and transfer bound (item 3).
   - Exact memory form of the closure for forcing and initial data in the
     retained subspace; positive-real kernel `chi(k, s)`; consistency with
     the quasi-static responses and the exact BGK formula (4.6).
   - A bound on the error of the quasi-static closure in the two embedded
     tests in terms of the kernel's frequency dependence; compare the bound
     with the measured errors of Tables 4 and 10.
C. Rate for the collisionless limit and the intermediate range (item 5).
   Exploratory: make the flux lemma quantitative if possible; otherwise
   document precisely where it fails. No result is promised.

Evidence boundaries: subagent proofs are checked in the main session before
anything enters the manuscript; what cannot be checked or proved is
recorded as open, not stated.
