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
3. Boltzmann dynamics to Euler or Navier-Stokes limits.

Note that Yu Deng and Zaher Hani have recent work proving rigorously these
scale-limit results but these results are incredibly complicated and
mathematical rather than computational. Part of this program is to turn the
canonical mathematical validation into a computational one.

### TEMPEST application profiles

Adapt the mathematical organization—not unmodified theorem assumptions—to
noncanonical physics. The first profile is a dusty-plasma closure ladder
organized as linked effective-interaction, particle-to-kinetic, and
kinetic-to-moment experiments. The second profile is core-collapse-supernova
turbulence: extract unresolved turbulent stresses, fluxes, and memory from 3D
DNS/implicit-LES/LES references and close a reduced 1D supernova carrier.

## Experimental pipeline

The bake-off is a sequence of closure experiments rather than a flat contest
among architectures. For every transition it declares the high-fidelity state,
projection, retained state, discarded information, classical reduced operator,
and measurable closure defect. Verified ensembles are projected into
marginals, moments, cumulants, interaction histories, and residual targets;
matched analytic, learned, and hybrid candidates are then tested first on those
targets and then after solver embedding. Separate scorecards report target
accuracy, identifiability, long-rollout behavior, physical validity,
classical-limit recovery, failure detection, out-of-distribution transfer, and
total cost.

The linked stages are:

1. effective interaction discovery at the retained-particle level;
2. particle-to-kinetic reduction and correlation closure;
3. kinetic-to-moment reduction and constitutive closure; and
4. transfer of validated diagnostics and design principles to a TEMPEST
   application, initially the supernova 3D-to-1D turbulence closure.

Track A supplies theorem-faithful tests of the scale-limit logic. The
dusty-plasma B1 profile supplies a controlled many-body setting in which
pairwise, contextual, and finite-memory descriptions can be separated. B2
tests whether the resulting principles remain useful when unresolved 3D
shock-turbulence physics is represented in a reduced 1D supernova model.
Coefficients, trained weights, and theorem assumptions do not transfer without
a new validation. The full execution sequence and stage gates are specified in
[`experimental_pipeline.md`](experimental_pipeline.md).

## Evaluation harness

We built an evaluation harness for computational closure methods: a fixed suite
of test problems and forcing regimes, a common interface through which any
closure model—analytic, learned, or hybrid—is invoked, and a standardized
battery of accuracy, stability, and cost metrics computed uniformly across
candidates. The harness separates the science (the closures) from the
scaffolding (data handling, integration, scoring), so that adding a new method
requires implementing one interface, and every reported comparison is
reproducible and fair by construction.

Because different families approximate different mathematical objects, the
harness does not produce one universal leaderboard. Direct rankings are made
within a declared target and information budget; cross-family conclusions use
the stage scorecards and claim ladder.

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
- A canonical end-to-end experimental-pipeline specification with activation
  gates and target-specific scorecards.
- A mathematical-to-computational translation of the hierarchy, cumulants,
  memory variables, and closure residuals.
- Canonical particle/Boltzmann and NLS/wave-kinetic ensemble benchmarks.
- A common cumulant and interaction-history data schema.
- A factorization and closure-failure diagnostic workflow.
- A supernova translation specification connecting filtered or angle-averaged
  3D dynamics to 1D turbulent stress, flux, production, and dissipation terms.
- A versioned supernova application contract covering projection, target
  estimators, physical constraints, rollout observables, and activation gates.
- Predeclared success, pivot, and stop criteria.
- Reproducible reference data generation.
- A reusable evaluation harness with common model interfaces, controlled test
  problems and forcing regimes, and uniform accuracy, stability, and cost
  scoring.
- Machine-readable metrics, figures, and comparison tables.
- A detailed LaTeX report including negative and nonconverged results.

## Current phase

Mathematical-program and benchmark design. The two-layer architecture is a
binding project direction, as are the linked scale-transition pipeline and
target-specific scorecards. Canonical solvers, dusty-plasma reference physics,
supernova reference simulations and reduced carrier, parameter ranges, and
model architectures remain open decisions.
