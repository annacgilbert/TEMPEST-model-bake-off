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
