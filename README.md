# TEMPEST Model Bake-Off

A reproducible mathematical and computational benchmark for understanding how
closure emerges—and fails—across microscopic, kinetic, fluid, and turbulent
scales. The project combines theorem-faithful canonical systems with TEMPEST
application profiles, then compares classical limits, cumulant and memory
closures, PINNs, neural operators, PINOs, learned closures, structured neural
dynamics, and world models.

The program architecture now has two layers: canonical mathematical validation
and application-specific physics. The first proposed application profile is
nonlocal magnetized heat transport beyond Braginskii in a 1D2V plasma slab.
Specific solvers, estimators, parameter ranges, and acceptance thresholds remain
open decisions.

## Evaluation harness

We built an evaluation harness for computational closure methods: a fixed suite
of test problems and forcing regimes, a common interface through which any
closure model—analytic, learned, or hybrid—is invoked, and a standardized
battery of accuracy, stability, and cost metrics computed uniformly across
candidates. The harness separates the science (the closures) from the
scaffolding (data handling, integration, scoring), so that adding a new method
requires implementing one interface, and every reported comparison is
reproducible and fair by construction.

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

## Initial workflow

1. Review `docs/mathematical_closure_program.md` and
   `docs/first_concrete_deliverables.md`.
2. Complete the mathematical-to-computational translation and the MTF mapping
   before selecting model architectures.
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
