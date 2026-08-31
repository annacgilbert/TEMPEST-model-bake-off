# Benchmark Specification

Status: **Draft - program architecture selected; solvers and parameter ranges remain open**

## 1. Scientific questions

The benchmark tests three linked claims:

1. When does a microscopic or higher-order description reduce reliably to a
   kinetic, fluid, spectral, or turbulent model, and which correlations and
   history variables predict the failure of that reduction?
2. When a classical TEMPEST closure fails, can a compact, structure-preserving
   correction improve the resolved model after it is embedded in a solver?
3. Can the onset of pairwise, Markov, kinetic, and moment closure failure be
   located by controlled changes in correlations, many-body context, and
   memory, and do any of those diagnostics remain useful in a distinct
   application profile?

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

- **B1. Dusty-plasma many-body closure ladder:** the particle-resolved profile
  connecting effective interaction discovery, particle-to-kinetic reduction,
  and kinetic-to-moment closure.
- **B2. Core-collapse-supernova turbulence closure:** the second science
  application, transferring unresolved 3D shock-turbulence effects into a
  reduced 1D carrier.

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

The harness generates target-specific scorecards, not one universal
leaderboard. A force model, one-instance PINN, solution operator, embedded
closure, and action-conditioned world model are directly ranked only against
models approximating the same mathematical object with a declared information
budget. Cross-family synthesis records accuracy, validity, robustness, and cost
without averaging unlike tasks into a fictitious winner.

The full end-to-end sequence is specified in
[`experimental_pipeline.md`](experimental_pipeline.md): predeclaration,
reference verification, ensemble generation, projection and diagnostics,
matched fitting, a-priori tests, embedded rollouts, breakdown and transfer
tests, claim audit, and report generation.

## 3. Common scale-transition specification

Every profile must identify the following objects before code or data
generation begins.

| Object | Required definition |
|---|---|
| Microscopic/high-fidelity state | Particle, kinetic, field, or fine-grid state and its probability law |
| Reduced state | Marginal, moments, spectrum, filtered field, or coarse variables |
| Connected information | Cumulants, correlations, non-equilibrium moments, or unresolved stresses/fluxes |
| Reduced operator | Boltzmann, WKE, Euler/NSF, RANS/LES, a 1D turbulence-augmented carrier, or another declared operator |
| Exact closure defect | Difference between the projected high-fidelity evolution and the declared reduced operator |
| Scaling coordinates | Knudsen number, wave nonlinearity, scale separation, collisionality, magnetization, or other profile coordinates |
| Validity assumptions | Factorization, randomness, smoothness, locality, Markovianity, or near-equilibrium assumptions |
| Mandatory structure | Conservation, positivity, entropy, realizability, symmetry, causality, and stability constraints |

At a retained-particle transition, the same specification applies. The
high-fidelity state may include plasma fields or dynamical wake variables, the
reduced state may retain only observed dust particles, and the closure defect
is the force or acceleration contribution of the eliminated environment.

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

## 5. Proposed application profile B2: core-collapse-supernova turbulence

The second science application closes the effect of unresolved 3D turbulence
in a reduced 1D core-collapse-supernova model. The high-fidelity family should
contain 3D radiation-hydrodynamic or (M)HD DNS, implicit-LES, or LES
simulations with an explicit resolution/filter hierarchy and shock tracking.
The reduced carrier should be a scientifically accepted 1D supernova solver
with the thermodynamic, composition, gravity, and neutrino-transport state
required by the selected case.

The projection from 3D to 1D must declare angle versus volume averaging,
Favre/Reynolds conventions, radial binning, shock alignment, and treatment of
moving discontinuities. The exact closure defect is

\[
C_{\mathrm{SN}}^\star[X]
=\langle F_{3\mathrm D}(X)\rangle_\Omega
-F_{1\mathrm D}(\langle X\rangle_\Omega),
\]

decomposed into Reynolds stress or turbulent pressure, turbulent energy and
enthalpy fluxes, production, dissipation, mixing, and optional finite-memory
terms. Initial baselines should include the unaugmented 1D carrier and at least
one declared local RANS/mixing-length or STIR-like closure; learned candidates
must correct an identified residual rather than silently replace the carrier.

Regime coordinates should include progenitor structure, post-bounce time,
shock strength, upstream turbulence intensity and correlation scale,
heating/forcing conditions, resolution or filter width, and magnetic-field
strength where relevant. The version-0 subset must be fixed with the supernova
science owners.

Required observables include mean shock-radius history, shock revival or
runaway classification and timing, turbulent kinetic energy and Reynolds
stress profiles, energy and lepton-number balance as represented by the
carrier, explosion energy, and at least one nucleosynthesis-sensitive
thermodynamic-history statistic. Required structure includes positivity,
Reynolds-stress realizability, conservative coupling, causal memory, stable
shock-capturing rollout, and recovery of the declared zero-turbulence or
calibrated local baseline.

## 6. Proposed application profile B1: dusty-plasma many-body ladder

B1 is designed to make the transition from many-body learning to closure
mathematically explicit. A controlled reference family should contain
heterogeneous dust particles, confinement, drag, screened repulsion,
nonreciprocal wake interactions, external forcing, and an optional dynamical
wake or field variable. A schematic reference is

\[
m_i \dot v_i = F_i^{\mathrm{conf}}+F_i^{\mathrm{ext}}-\gamma_i v_i
+\sum_{j\ne i}F_{ij}(r_i,r_j,\zeta_j;\mu)+\eta_i,
\qquad
\tau_w\dot\zeta_j=\zeta_{\mathrm{eq}}(\mathcal E_j)-\zeta_j.
\]

The scientific owner must select the actual reference physics; this schematic
exists to define the experimental degrees of freedom. Required sweep
coordinates include particle count, density or coupling, screening, charge and
mass heterogeneity, wake relaxation $\tau_w$, forcing amplitude and
frequency, and forcing history.

### B1.1 Effective interaction discovery

Compare:

1. an analytic instantaneous pair law;
2. a learned pair kernel with an identifiability/coercivity diagnostic;
3. a physics-tailored force decomposition;
4. an instantaneous equivariant many-particle graph model;
5. a finite-memory graph or auxiliary-state model; and
6. an unrestricted black-box control.

Measure held-out force error, effective-law identifiability under the sampled
occupancy measure, internal/external force decomposition, symmetry and
nonreciprocity, independent physical quantities such as inferred mass or
screening where available, and stable particle rollouts.

### B1.2 Particle-to-kinetic closure

Project the same particle ensembles to one-particle distributions and selected
two- and higher-particle cumulants. Compare classical mean-field or kinetic
operators, analytic correlation corrections, weak-form discovered operators,
explicit cumulant closures, learned correlation/collision residuals,
finite-memory models, and kinetic neural operators or PINOs where paired
solution families exist.

Measure distribution and collective-mode error, projected cumulants,
hierarchy and closure residuals, transport coefficients, factorization
failure, classical-limit recovery, and long-time kinetic rollouts.

### B1.3 Kinetic-to-moment closure

Project the kinetic reference to density, momentum, energy, and a predeclared
set of higher moments. Compare classical constitutive laws, Grad or
maximum-entropy closures, explicit cumulant closures, hyperbolic learned
moment closures, finite-memory corrections, structure-preserving learned
residuals, and parameterized moment-solution operators.

Measure stress and heat flux, moment realizability, hyperbolicity,
conservation, entropy behavior, equilibrium and classical-limit recovery,
embedded-solver stability, and collective or transport observables.

### B1.4 Controlled closure regimes

The sweep must contain four predeclared regimes:

1. small wake-relaxation time and weak collective effects, where an
   instantaneous pair law should be adequate;
2. a contextual regime where local many-particle geometry matters;
3. a finite-memory regime where wake or field relaxation is comparable to the
   resolved particle time; and
4. a collective or nonlocal regime in which pairwise structure is
   intentionally insufficient.

The decisive result is the empirical boundary at which each additional type of
information - pairwise state, many-particle context, then history - becomes
necessary, together with whether cumulants or interaction-history summaries
predict that boundary before large rollout error.

## 7. Data and estimator specification

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

## 8. Parameter domains and splits

Predeclare four distinct regimes:

1. **Asymptotic verification:** conditions in which the classical limit should
   become accurate.
2. **Controlled breakdown:** conditions in which correlations, memory, or
   nonlocality should invalidate it.
3. **Interpolation/extrapolation:** held-out parameter values, initial
   conditions, and time horizons.
4. **Cross-profile transfer:** diagnostics or architectures transferred from a
   canonical track to an application profile without shared test data.

For B1, splits must hold out entire combinations of particle number, density,
wake timescale, and forcing history. Random trajectory frames from the same
realization may not be separated across train and test sets.

No split may leak trajectories, ensemble members, initial-condition families,
or parameter-neighbor information across train and test sets.

## 9. Model targets and closure ladder

Each run must identify whether it approximates a solution, solution operator,
vector field, flow map, constitutive closure, memory kernel, cumulant evolution,
or action-conditioned world model.

The linked target and closure ladder is:

1. analytic effective interaction or classical reduced operator;
2. learned pair kernel or explicit Markov correction;
3. contextual many-particle model or explicit cumulant/moment augmentation;
4. finite-memory or Mori-Zwanzig model;
5. learned closure with hard or soft structure embedded in a retained solver;
6. end-to-end solution/operator surrogate;
7. structured dynamics or world model when sequential intervention is real.

Every learned method must be compared with the simplest lower rung that uses
the same privileged information.

## 10. Experimental controls

Specify seeds, optimization budgets, stopping rules, hyperparameter-selection
rules, numerical precision, hardware accounting, failure handling, and
reference-solver calls. Separate error from discretization, ensemble sampling,
statistical estimation, closure approximation, learning, and rollout.

## 11. Stage scorecards

Report six scorecards at every applicable stage:

1. target accuracy and identifiability with estimator uncertainty;
2. short- and long-horizon dynamics and reliability;
3. closure-failure detection and state-selection value;
4. physical and mathematical validity;
5. asymptotic recovery, robustness, and transfer; and
6. data-generation, training, online-diagnostic, inference, and end-to-end cost.

A cross-stage synthesis identifies the smallest sufficient information set in
each regime and whether that information remains useful after the next
reduction. It must not average stage scores into a universal architecture
ranking.

## 12. Acceptance criteria

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

For B1 production activation, the scientific owner, reference force or field model,
independent validation quantities, accessible data/simulator path, and initial
parameter regimes must be approved before production data generation.

For B2 production activation, the 3D reference ensemble, reduced 1D carrier,
projection and shock-alignment convention, closure-defect estimator,
application observables, and numerical/estimator uncertainty budgets must be
approved before production data generation.
