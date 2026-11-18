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
