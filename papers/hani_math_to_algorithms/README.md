# Hani Math-to-Algorithms Program

This directory is a standalone research program and prospective paper inside
the TEMPEST bake-off repository. It asks a narrower and more mathematical
question than the bake-off itself:

> Can the history-bearing cumulant structures used by Deng, Hani, and Ma to
> justify kinetic closure be converted into measurable diagnostics, reduced
> state variables, and stable numerical corrections?

The project begins with three rigorous reduction ladders:

1. hard-sphere dynamics to the Boltzmann equation;
2. cubic nonlinear Schrödinger dynamics to the wave kinetic equation; and
3. Boltzmann dynamics to compressible Euler or incompressible
   Navier--Stokes--Fourier.

The proposed computation does **not** treat the proof's cutting algorithm as a
drop-in physical simulator. Instead it uses the proof to decide what to log,
estimate, compress, and test: connected cumulants, time layers, collision or
resonance histories, circuit rank, recollisions, and non-equilibrium
remainders. The baseline kinetic or fluid equation remains explicit. A
history-aware model predicts only the closure defect or a validity indicator.

## Working thesis

A scalar measure of "small correlation" is not enough for long-time closure.
The orientation and organization of interaction history matter. A practical
closure state should therefore combine:

- the retained one-particle density or wave spectrum;
- low-order projected connected cumulants;
- compressed time-ordered interaction-graph features; and
- a calibrated closure-defect estimate with uncertainty.

This thesis is falsifiable. If history features do not improve held-out defect
prediction or long-time rollout after controlling for the retained state and
low-order cumulants, then the computational value of the proof structure is
limited in that regime.

## Recommended first publishable unit

Start with the wave track because both sides of the reduction are directly
computable: ensemble pseudospectral NLS and a four-wave kinetic solver. Use a
small hard-sphere pilot in parallel to validate the interaction-history data
model. A full particle-to-Boltzmann scaling study follows only after the
estimators and negative controls are stable.

## Directory map

- `docs/math_to_algorithm.md`: proof object to computational object, with
  proposed algorithms.
- `docs/literature_map.md`: primary-source survey and the identified gap.
- `docs/experimental_program.md`: phased experiments and acceptance gates.
- `docs/paper_outline.md`: proposed paper claim and section structure.
- `paper/main.tex`: a compilable paper shell.
- `references/README.md`: canonical papers, expository notes, and numerical
  neighbors.
- `src/hani_closure/`: small, dependency-free prototypes for cumulants and
  interaction histories.
- `tests/`: exact tests for those prototypes.

## Immediate commands

```bash
cd papers/hani_math_to_algorithms
python -m unittest discover -s tests -v
```

The prototype is deliberately small. Production NLS, WKE, event-driven
hard-sphere, Boltzmann, and fluid solvers should be adapters around trusted
implementations, not reimplemented inside this package.

