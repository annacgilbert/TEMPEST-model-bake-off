# AGENTS.md

## Mission

Build a reproducible mathematical and computational benchmark for closure
across microscopic, kinetic, fluid, and turbulent scales. Compare classical
limits, explicit cumulant and memory closures, PINNs, neural operators,
physics-informed neural operators, learned closures, structured neural
dynamical systems, and world models on canonical systems and shared TEMPEST
application profiles.

## Scientific principles

1. Identify the exact hierarchy, limiting process, retained state, discarded
   information, and closure defect for every scale transition.
2. Distinguish equation information, paired solution data, trajectory data,
   ensemble statistics, cumulants, interaction histories, closure targets,
   structural assumptions, and control or action labels.
3. Never allow test or out-of-distribution cases to influence normalization,
   hyperparameter selection, or training.
4. Report failures and nonconverged runs; never silently discard them.
5. Compare methods at matched data budgets and matched compute budgets.
6. Preserve physical units and document every nondimensionalization.
7. Test conservation, stability, realizability, and long-rollout behavior, not
   only pointwise prediction error.
8. Include theorem-faithful canonical benchmarks before adapting a mathematical
   closure construction to noncanonical application physics.
9. Quantify discretization error, ensemble-estimation error, asymptotic-limit
   error, and learned model-form error separately.
10. Require augmented closures to recover their trusted kinetic or fluid limit
    in the appropriate asymptotic regime.

## Engineering principles

1. Every model implements a common train, evaluate, and checkpoint interface.
2. Every experiment is specified by a committed configuration file.
3. Set and record all random seeds.
4. Write numerical and physics sanity tests before large training runs.
5. Store large generated data and checkpoints outside Git; commit manifests.
6. Never overwrite an existing result directory.
7. Generate report tables and figures from saved machine-readable metrics.
8. Prefer reusable Python modules over logic embedded only in notebooks.
9. Treat ensemble definitions, projected cumulants, interaction histories, and
   estimator uncertainty as versioned data products.
10. Keep the classical reduced operator explicit; learned models should supply
    only an identified unresolved correction unless an experiment is explicitly
    designated as a black-box control.

## Workflow

For substantial changes:

1. Read `docs/PROJECT_BRIEF.md`, `docs/mathematical_closure_program.md`,
   `docs/benchmark_specification.md`, and `docs/DECISIONS.md`.
2. Produce or update a written plan before implementation.
3. Make the smallest coherent implementation.
4. Run unit tests and at least one inexpensive end-to-end smoke test.
5. Record commands, configuration, runtime, and results.
6. Update documentation when an interface or scientific assumption changes.

## Definition of done

A model implementation is not done until:

- its unit tests pass;
- a small deterministic smoke experiment runs;
- metrics are saved in the standard schema;
- ensemble uncertainty and numerical error are separated from model error;
- claimed scale limits and classical-limit recovery have been tested;
- an embedded-solver test accompanies any a priori closure-target test;
- failures are handled and reported;
- the relevant documentation is updated; and
- the result can be reproduced from a clean environment.
