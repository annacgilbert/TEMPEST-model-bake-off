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

- Use dusty plasma as Application Profile 1, organized as a linked
  effective-interaction, particle-to-kinetic, and kinetic-to-moment ladder.
- Use core-collapse supernovae as Application Profile 2, centered on
  shock-turbulence interaction and the self-consistent transfer of 3D
  turbulence effects into a reduced 1D model.
- Reference simulators, exact closure targets, rollout observables, action
  protocols, and success thresholds remain subject to design-meeting approval.

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

## 2026-08-31 — Linked experimental pipeline and scorecards

- Organize the bake-off as linked retained-state transitions rather than a flat
  architecture contest: effective interaction discovery,
  particle-to-kinetic reduction, kinetic-to-moment closure, and TEMPEST
  application transfer.
- Preserve Track A as theorem-faithful validation and B1 as a dusty-plasma
  many-body ladder that uses one verified particle ensemble for
  effective-force, kinetic, and moment closure questions.
- Specify B2 as a core-collapse-supernova 3D-to-1D closure profile. Its
  high-fidelity reference, reduced carrier, projection, and application-facing
  metrics require scientific-owner approval before production runs.
- Use wake or field relaxation, density/coupling, and forcing history to test
  when pairwise, many-particle contextual, finite-memory, and collective
  descriptions become necessary.
- Produce target-specific scorecards. Do not collapse force inference,
  solution approximation, operator learning, embedded closure, structured
  dynamics, and world-model rollout into one universal leaderboard.
- Treat diagnostic logic, state-selection rules, structural
  parameterizations, and evaluation procedures as candidates for transfer;
  coefficients, learned weights, states, and theorem assumptions require
  profile-specific validation.

## Open decisions

- Canonical solver choices for hard-sphere/Boltzmann and NLS/wave-kinetic
  tracks.
- Dusty-plasma scientific owner, reference particle/wake/field physics,
  independent validation quantities, and first small parameter sweep.
- Version-0 supernova 3D reference ensemble, angle/volume projection, reduced
  1D carrier, turbulent closure target, and rollout observables.
- Projected cumulant basis, estimator, maximum order, and uncertainty method.
- Interaction-history representation and time-layer definition.
- Nondimensionalization and parameter ranges.
- Fidelity hierarchy and reference solver.
- In-distribution and out-of-distribution splits.
- Compute and data budgets.
- Exact version-0 model-interface and metric schemas within the approved common
  harness architecture.
- Project license.
