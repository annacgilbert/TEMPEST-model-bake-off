# Decision Log

Record only binding project decisions here. Proposed ideas belong in the
relevant design document until accepted.

## 2026-08-08 — Repository organization

- Use one Git repository for all model families during benchmark development.
- Use a shared data pipeline, split definitions, metric schema, and plotting
  code to reduce accidental unfairness.
- Keep large generated data and checkpoints out of Git; commit their manifests.
- Treat notebooks as exploratory clients of reusable package code.

## 2026-08-08 — Comparison principles

- Report both matched-information and matched-compute comparisons.
- Keep equation information, observation data, operator data, closure targets,
  structural constraints, and action labels explicit rather than collapsing
  them into a single notion of “training data.”
- Include physical validity, stability, and rollout diagnostics alongside
  pointwise errors.
- Preserve failed and nonconverged runs in the experiment record.

## 2026-08-08 — Mathematical program architecture

- Organize the bake-off in two linked layers: theorem-faithful canonical
  mathematical validation and TEMPEST application profiles.
- Treat connected cumulants, factorization error, interaction histories,
  hierarchy residuals, memory, and asymptotic-limit recovery as first-class
  benchmark objects.
- Begin with specifications and small canonical ensemble benchmarks before
  implementing application-scale ML models.
- Keep classical kinetic and fluid operators as explicit asymptotic anchors;
  learned models should correct identified unresolved terms.
- Require both a priori closure diagnostics and a posteriori embedded-solver
  tests.
- Treat failure of cumulant compressibility, finite-memory sufficiency, or
  cross-application transfer as valid scientific outcomes.

## 2026-08-08 — Proposed application profile

- Use nonlocal magnetized heat transport beyond Braginskii as the leading
  candidate for Application Profile 1.
- The 1D2V MTF slab, exact kinetic reference, learned target, action protocol,
  and success thresholds remain subject to design-meeting approval.
- Retain dusty plasma as a candidate Application Profile 2 for testing transfer
  to strongly correlated particle-resolved physics.

## 2026-08-09 — Common evaluation harness

- Use a fixed, versioned suite of test problems and forcing regimes for all
  computational closure methods.
- Invoke analytic, learned, and hybrid closures through one common interface.
- Compute accuracy, stability, reliability, and cost metrics through shared
  evaluation code rather than method-specific scoring paths.
- Keep closure science separate from data handling, time integration, scoring,
  and report generation so that a new method implements only the declared
  interface.
- Treat reproducibility and comparison fairness as properties enforced by the
  harness, configurations, manifests, and information budgets.

## Open decisions

- Canonical solver choices for hard-sphere/Boltzmann and NLS/wave-kinetic
  tracks.
- Version-0 MTF profile and reference kinetic equation.
- Projected cumulant basis, estimator, maximum order, and uncertainty method.
- Interaction-history representation and time-layer definition.
- Nondimensionalization and parameter ranges.
- Fidelity hierarchy and reference solver.
- In-distribution and out-of-distribution splits.
- Compute and data budgets.
- Exact version-0 model-interface and metric schemas within the approved common
  harness architecture.
- Project license.
