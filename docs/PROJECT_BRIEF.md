# Project Brief

## Objective

Design and execute a scientifically defensible mathematical and computational
program for closure across microscopic, kinetic, fluid, and turbulent scales.
The program must reveal what information is discarded in each scale
transition, when the reduced limit is valid, what each numerical or learned
model approximates, and where its assumptions succeed or fail.

## Two-layer architecture

### Canonical mathematical validation

Use systems close to the hypotheses of rigorous scale-limit results to make
cumulants, interaction histories, asymptotic parameters, and hierarchy errors
measurable:

1. hard-sphere or hard-disk dynamics to the Boltzmann equation;
2. nonlinear Schrödinger dynamics to the wave kinetic equation; and
3. Boltzmann dynamics to Euler or Navier-Stokes-Fourier limits.

### TEMPEST application profiles

Adapt the mathematical organization—not unmodified theorem assumptions—to
noncanonical physics. The first proposed profile is nonlocal magnetized heat
transport beyond Braginskii in a 1D2V slab. A dusty-plasma profile is a
candidate transfer test.

## Evaluation harness

We built an evaluation harness for computational closure methods: a fixed suite
of test problems and forcing regimes, a common interface through which any
closure model—analytic, learned, or hybrid—is invoked, and a standardized
battery of accuracy, stability, and cost metrics computed uniformly across
candidates. The harness separates the science (the closures) from the
scaffolding (data handling, integration, scoring), so that adding a new method
requires implementing one interface, and every reported comparison is
reproducible and fair by construction.

## Model families in scope

1. Conventional high-fidelity or reduced numerical solver.
2. Classical Markov kinetic or fluid closure.
3. Explicit finite-cumulant or finite-moment closure.
4. Finite-memory closure or Mori-Zwanzig-type reduced model.
5. Classical PINN approximating one solution.
6. Supervised neural operator trained on solution pairs.
7. Physics-informed neural operator.
8. Learned constitutive, cumulant, or memory closure embedded in a solver.
9. Structured neural ODE or reduced dynamical model.
10. Action-conditioned latent world model.

## Required benchmark capabilities

The physical setting should support:

- a controllable transition from canonical to noncanonical behavior;
- an explicit microscopic-to-kinetic-to-fluid hierarchy where feasible;
- at least one unresolved closure quantity;
- estimable connected cumulants or higher-order statistics;
- interaction-history or memory diagnostics;
- parameterized initial conditions or coefficients;
- data generation at multiple fidelities;
- an optional intervention or control variable;
- meaningful long-time or rollout diagnostics;
- conservation, stability, realizability, or structural tests; and
- in-distribution and out-of-distribution regimes.

Canonical tracks must additionally expose the relevant scaling parameters and
allow numerical tests of convergence toward the claimed kinetic or fluid limit.

## Central comparison question

For every model, identify exactly:

> What mathematical object is the neural network approximating?

Then specify the equations, data, imposed structure, training requirements,
inference requirements, fair comparison conditions, and expected failure modes.

For every scale transition, also ask:

> What connected correlation, interaction history, or asymptotic remainder is
> being discarded, and how will its effect be measured?

## Deliverables

- A versioned benchmark specification and information-budget matrix.
- A mathematical-to-computational translation of the hierarchy, cumulants,
  memory variables, and closure residuals.
- Canonical particle/Boltzmann and NLS/wave-kinetic ensemble benchmarks.
- A common cumulant and interaction-history data schema.
- A factorization and closure-failure diagnostic workflow.
- An MTF translation specification connecting canonical objects to the
  Braginskii and nonlocal heat-flux hierarchy.
- Predeclared success, pivot, and stop criteria.
- Reproducible reference data generation.
- A reusable evaluation harness with common model interfaces, controlled test
  problems and forcing regimes, and uniform accuracy, stability, and cost
  scoring.
- Machine-readable metrics, figures, and comparison tables.
- A detailed LaTeX report including negative and nonconverged results.

## Current phase

Mathematical-program and benchmark design. The two-layer architecture is a
binding project direction; canonical solvers, MTF reference physics, parameter
ranges, and model architectures remain open decisions.
