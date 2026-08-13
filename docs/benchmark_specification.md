# Benchmark Specification

Status: **Draft - program architecture selected; solvers and parameter ranges remain open**

## 1. Scientific questions

The benchmark tests two linked claims:

1. When does a microscopic or higher-order description reduce reliably to a
   kinetic, fluid, spectral, or turbulent model, and which correlations and
   history variables predict the failure of that reduction?
2. When a classical TEMPEST closure fails, can a compact, structure-preserving
   correction improve the resolved model after it is embedded in a solver?

The benchmark is therefore not only a contest among predictors. It is a test
of what information a valid closure must retain.

## 2. Program architecture

### Track A: theorem-faithful canonical systems

- **A1. Hard particles to Boltzmann:** particle ensembles, one-particle
  marginals, connected correlations, collision histories, and the Boltzmann
  approximation.
- **A2. Nonlinear Schrodinger dynamics to wave kinetics:** ensembles of random
  waves, spectra, spectral cumulants, resonant interaction histories, and the
  wave kinetic equation.
- **A3. Boltzmann to fluid:** kinetic solutions, hydrodynamic moments,
  non-equilibrium corrections, and Euler/Navier-Stokes-Fourier limits.

These systems test whether the numerical workflow can reproduce the
factorization, scaling, and asymptotic mechanisms used in rigorous analysis.

### Track B: TEMPEST application profiles

- **B1. Magnetic-target-fusion nonlocal heat transport:** the proposed first
  application profile.
- **B2. Dusty-plasma transport and self-organization:** a candidate second
  application profile, pending scientific-owner agreement.

Track B uses the diagnostics validated in Track A but does not assume that a
canonical theorem transfers unchanged to application physics.

### Common evaluation harness

We built an evaluation harness for computational closure methods: a fixed suite
of test problems and forcing regimes, a common interface through which any
closure model—analytic, learned, or hybrid—is invoked, and a standardized
battery of accuracy, stability, and cost metrics computed uniformly across
candidates. The harness separates the science (the closures) from the
scaffolding (data handling, integration, scoring), so that adding a new method
requires implementing one interface, and every reported comparison is
reproducible and fair by construction.

## 3. Common scale-transition specification

Every profile must identify the following objects before code or data
generation begins.

| Object | Required definition |
|---|---|
| Microscopic/high-fidelity state | Particle, kinetic, field, or fine-grid state and its probability law |
| Reduced state | Marginal, moments, spectrum, filtered field, or coarse variables |
| Connected information | Cumulants, correlations, non-equilibrium moments, or unresolved stresses/fluxes |
| Reduced operator | Boltzmann, WKE, Euler/NSF, Braginskii, LES, or another declared operator |
| Exact closure defect | Difference between the projected high-fidelity evolution and the declared reduced operator |
| Scaling coordinates | Knudsen number, wave nonlinearity, scale separation, collisionality, magnetization, or other profile coordinates |
| Validity assumptions | Factorization, randomness, smoothness, locality, Markovianity, or near-equilibrium assumptions |
| Mandatory structure | Conservation, positivity, entropy, realizability, symmetry, causality, and stability constraints |

A generic notation is

\[
f_2=f_1 f_1+g_2, \qquad
\partial_t f_1=\mathcal L f_1+\mathcal C[f_1]+\mathcal R[g_2,g_3,\ldots],
\]

where the closure task is to approximate the residual \(\mathcal R\) from a
declared information set. Higher-order terms may be compressed through
projected cumulants \(\Pi_r g_k\), low-rank bases, or time-layered interaction
summaries, but the approximation error must be measured.

## 4. Canonical benchmark requirements

### A1. Particle-Boltzmann benchmark

Compare a converged particle ensemble with a kinetic solver over:

- one-particle observables and collision statistics;
- projected two- and three-particle cumulants;
- hierarchy residuals and a factorization-defect score;
- increasing time horizons and asymptotic scaling coordinates;
- deliberately invalid regimes in which recollisions or correlations persist.

### A2. NLS-WKE benchmark

Compare ensembles of nonlinear-wave simulations with a wave-kinetic solver
over:

- energy or wave-action spectra;
- spectral cumulants and resonant transfer rates;
- interaction-history summaries across time layers;
- weak-nonlinearity and scale-separation sweeps;
- coherent or strongly correlated regimes outside kinetic assumptions.

### A3. Boltzmann-fluid benchmark

Compare a kinetic solver with Euler and Navier-Stokes-Fourier reductions over:

- hydrodynamic moments and constitutive fluxes;
- non-equilibrium moment/cumulant coordinates;
- asymptotic convergence rates as Knudsen number decreases;
- shocks, steep gradients, and boundary layers that expose breakdown;
- closure corrections embedded in the fluid solver.

## 5. Proposed application profile B1: nonlocal heat transport in MTF

The first profile should use a one-dimensional magnetized slab or flux-tube
geometry whose complexity can be increased only after the diagnostic workflow
is verified. The retained state should include density, temperature, flow, and
the minimum magnetic variables required by the selected kinetic model. The
high-fidelity reference may be kinetic, gyrokinetic, or a scientifically
accepted reduced kinetic solver selected by the TEMPEST team.

The leading closure target is

\[
q = q_{\mathrm{classical}} + \Delta q_{\mathrm{nonlocal}},
\]

with the possibility of adding stress or transport corrections after the heat
flux problem is stable. Regime coordinates should include collisionality,
temperature-gradient scale length, magnetization, boundary forcing, and a
compression or implosion-history parameter if the reference solver supports
it.

Required observables include heat flux, temperature evolution, energy balance,
peak-temperature timing, and at least one application-facing quantity agreed
with the MTF science team.

## 6. Data and estimator specification

The data product is an ensemble with provenance, not merely a collection of
trajectories. Each profile must declare:

- ensemble definition, sample count, randomization, and independence;
- discretization, convergence evidence, and reference-solver uncertainty;
- marginal, moment, cumulant, residual, and history estimators;
- estimator bias, sampling variance, basis truncation, and time-window error;
- raw-to-reduced transformations and units;
- whether an ergodic or homogeneity assumption substitutes for ensembles.

A single trajectory must not be reported as an ensemble cumulant without a
stated ergodic estimator and uncertainty analysis.

## 7. Parameter domains and splits

Predeclare four distinct regimes:

1. **Asymptotic verification:** conditions in which the classical limit should
   become accurate.
2. **Controlled breakdown:** conditions in which correlations, memory, or
   nonlocality should invalidate it.
3. **Interpolation/extrapolation:** held-out parameter values, initial
   conditions, and time horizons.
4. **Cross-profile transfer:** diagnostics or architectures transferred from a
   canonical track to an application profile without shared test data.

No split may leak trajectories, ensemble members, initial-condition families,
or parameter-neighbor information across train and test sets.

## 8. Model targets and closure ladder

Each run must identify whether it approximates a solution, solution operator,
vector field, flow map, constitutive closure, memory kernel, cumulant evolution,
or action-conditioned world model.

The closure ladder is:

1. classical reduced operator;
2. explicit Markov correction;
3. explicit cumulant or moment augmentation;
4. finite-memory or Mori-Zwanzig model;
5. learned closure with hard or soft structure;
6. end-to-end solution/operator surrogate;
7. structured dynamics or world model when sequential intervention is real.

Every learned method must be compared with the simplest lower rung that uses
the same privileged information.

## 9. Experimental controls

Specify seeds, optimization budgets, stopping rules, hyperparameter-selection
rules, numerical precision, hardware accounting, failure handling, and
reference-solver calls. Separate error from discretization, ensemble sampling,
statistical estimation, closure approximation, learning, and rollout.

## 10. Acceptance criteria

A result enters the comparative report only if:

- the high-fidelity and reduced solvers pass convergence and conservation
  checks appropriate to the profile;
- estimator uncertainty is smaller than the closure effect being claimed;
- the classical asymptotic limit is recovered where it should hold;
- claimed structural properties are tested rather than inferred from the
  architecture name;
- closures are evaluated both a priori and after solver embedding;
- failed, unstable, or non-convergent runs remain in the reliability record;
- all information access, configurations, and manifests are reproducible.
