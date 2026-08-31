# TEMPEST Model Bake-Off

A reproducible mathematical and computational benchmark for understanding how
closure emerges—and fails—across microscopic, kinetic, fluid, and turbulent
scales. The project combines theorem-faithful canonical systems with TEMPEST
application profiles, then compares classical limits, cumulant and memory
closures, PINNs, neural operators, PINOs, learned closures, structured neural
dynamics, and world models.

The program architecture now has two layers: canonical mathematical validation
and application-specific physics. The TEMPEST profiles are a dusty-plasma
many-body closure ladder and a core-collapse-supernova turbulence closure that
transfers volume- or angle-averaged information from 3D simulations into a
reduced 1D carrier. Specific solvers, estimators, parameter ranges, profile
activation decisions, and acceptance thresholds remain open.

## Experimental pipeline

The bake-off is a linked closure pipeline, not a flat architecture leaderboard.
For each reduction it declares the retained state, eliminated information,
classical operator, exact or estimated closure defect, and available
information. Verified ensembles then support four connected experiments:

1. effective interaction discovery;
2. particle-to-kinetic reduction;
3. kinetic-to-moment closure; and
4. transfer of validated diagnostics and design principles to a 3D-to-1D
   core-collapse-supernova turbulence closure.

Candidates are tested on held-out targets and after solver embedding, then
reported through separate accuracy/identifiability, dynamics, physical
validity, limit/transfer, and cost scorecards. The proposed dusty-plasma sweep
uses wake relaxation, density, and forcing history to locate when pairwise,
many-particle contextual, and finite-memory models become necessary. The
canonical end-to-end description is
[`docs/experimental_pipeline.md`](docs/experimental_pipeline.md).

## Evaluation harness

We built an evaluation harness for computational closure methods: a fixed suite
of test problems and forcing regimes, a common interface through which any
closure model—analytic, learned, or hybrid—is invoked, and a standardized
battery of accuracy, stability, and cost metrics computed uniformly across
candidates. The harness separates the science (the closures) from the
scaffolding (data handling, integration, scoring), so that adding a new method
requires implementing one interface, and every reported comparison is
reproducible and fair by construction.

Direct rankings are restricted to candidates that approximate the same
mathematical object under a declared information budget.

## Repository map

- `references/`: proposal and background sources supplied by the researchers.
- `docs/`: mathematical program, deliverable sketches, benchmark
  specifications, decisions, meeting memo, presentations, and report.
- `configs/`: version-controlled physics, data, model, and experiment settings.
- `src/tempest_bakeoff/`: reusable simulation, modeling, and evaluation code.
- `scripts/`: thin command-line entry points.
- `tests/`: numerical, physical, interface, and reproducibility checks.
- `data/`: local generated data and committed manifests.
- `results/`: metrics, manifests, figures, and local checkpoints.
- `notebooks/`: exploratory analysis; production logic belongs in `src/`.
- `papers/hani_math_to_algorithms/`: standalone proof-guided program translating
  Hani's cumulants, time layers, molecules, and gardens into computational
  diagnostics and a prospective paper.

## Initial workflow

1. Review `docs/mathematical_closure_program.md` and
   `docs/experimental_pipeline.md`, then
   `docs/first_concrete_deliverables.md` and
   `docs/supernova_application_profile.md`.
2. Complete the mathematical-to-computational translation and the supernova
   3D-to-1D closure mapping before selecting model architectures.
3. Complete `docs/benchmark_specification.md`,
   `docs/information_budgets.md`, and `docs/evaluation_protocol.md`.
4. Record binding scientific choices in `docs/DECISIONS.md`.
5. Only then implement canonical reference generators and model families.

## Development setup

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
pytest
```

The package and command-line scripts are placeholders at this scaffold stage.
