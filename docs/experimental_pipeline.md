# Experimental Pipeline

Status: **Canonical summary of the proposed bake-off; numerical choices remain open**

## One-paragraph summary

The TEMPEST bake-off is a linked sequence of closure experiments, not a single
race among neural-network architectures. We first verify high-fidelity and
reduced reference solvers, define the retained state and the information
discarded at each reduction, and measure the resulting closure defect with
uncertainty. We then compare analytic, learned, and hybrid models at four
connected levels: effective interaction discovery, particle-to-kinetic
reduction, kinetic-to-moment closure, and transfer to the core-collapse-
supernova 3D-to-1D turbulence application. Every candidate declares the
mathematical object it approximates and the equations, data, histories, and
structural assumptions it receives. The common computational and evaluative
harness trains or calibrates the candidate, embeds closures in the appropriate
solver, runs identical held-out regimes, and produces separate scorecards for
target accuracy, long-rollout behavior, physical validity, failure detection,
out-of-distribution transfer, and end-to-end cost. Canonical scale-limit tests
and a dusty-plasma many-body ladder expose when pairwise, contextual, or
memory-dependent descriptions are sufficient; the supernova profile tests
whether the resulting diagnostics and design principles remain useful when
unresolved 3D shock-turbulence effects are closed inside a reduced 1D model,
without pretending that coefficients or theorem assumptions transfer
unchanged.

## The experimental logic

The same scientific contract is used at every scale transition:

1. Declare the high-fidelity state $X$, projection $\Pi$, retained state
   $u=\Pi X$, and classical reduced operator $F_0$.
2. Define the exact or estimable closure defect

   \[
   C^\star[X] = \Pi F(X) - F_0(\Pi X).
   \]
3. Name the discarded particles, fields, correlations, moments, or histories
   whose effect appears in $C^\star$.
4. Specify the information available to a candidate at training and inference
   time, then construct matched-information and matched-compute comparisons.
5. Test the candidate first against the held-out closure target and then after
   embedding it in the reduced solver.
6. Require recovery of the trusted classical limit, mandatory physical
   structure, and honest failure reporting before making a transfer claim.

The pipeline therefore follows

> verified references -> projected data and closure defects -> diagnostic
> state selection -> matched model fitting -> a-priori tests -> embedded
> rollouts -> breakdown and transfer tests -> scorecards and claim audit.

## Program layers

### Layer A: theorem-faithful validation

Three canonical tracks validate the numerical logic against explicit scale
limits:

- **A1, hard particles to Boltzmann:** factorization, particle cumulants,
  recollisions, collision histories, and the particle-to-kinetic residual;
- **A2, nonlinear waves to wave kinetics:** spectra, spectral cumulants,
  resonant histories, and the wave-kinetic residual; and
- **A3, Boltzmann to fluid:** non-Maxwellian moments, constitutive fluxes,
  hydrodynamic remainders, and Euler or Navier-Stokes-Fourier recovery.

These tracks determine whether cumulants and histories genuinely diagnose
closure failure in settings close to the relevant mathematics. They are not
surrogates for plasma physics.

### Layer B: TEMPEST application profiles

- **B1, dusty-plasma many-body ladder:** the particle-resolved profile that
  connects effective interaction learning to kinetic statistics and moment
  closures.
- **B2, core-collapse-supernova turbulence closure:** the second science
  application, in which angle- or volume-averaged 3D reference dynamics supply
  turbulent closure targets for a reduced 1D carrier.

Both profiles require approved scientific owners, reference physics,
estimators, and application observables before production runs.

Only diagnostic logic, state-selection rules, structural parameterizations,
and evaluation procedures are candidates for transfer between profiles.
Physical coefficients, trained weights, state variables, and theorem
assumptions transfer only when a separate test justifies them.

## The four linked bake-offs

### Stage 1: effective interaction discovery

**Question.** Given particle trajectories and declared external conditions,
what instantaneous or history-dependent effective law reproduces the force on
each retained particle?

**Retained state.** Particle positions, velocities, species or charge labels,
and observable external conditions.

**Discarded information.** Electrons, ions, wakes, unresolved fields,
collisions, and sub-observation-time dynamics.

**Candidate learned objects.** Radial or anisotropic pair kernels, directed
nonreciprocal interactions, environment forces, drag, graph interactions,
field-conditioned forces, and finite-memory auxiliary states.

**Candidate methods.** Analytic screened-interaction baselines, statistically
identifiable kernel regression, weak-form force inference, physics-tailored
networks, equivariant graph models, recurrent or auxiliary-state graph models,
and a deliberately unrestricted black-box control.

**Primary evidence.** Held-out force error, identifiability under the empirical
occupancy measure, recovery of mass/charge/screening relations, decomposition
of internal and external forces, symmetry or nonreciprocity tests, and
particle-rollout stability.

This is a closure experiment when the learned force represents the effect of
eliminated plasma or field degrees of freedom. It is not automatically a
kinetic or fluid closure merely because many particles are present.

### Stage 2: particle-to-kinetic reduction

**Question.** When can the particle ensemble be replaced by a one-particle
distribution, and what correction is needed when correlations persist?

**Retained state.** A one-particle distribution or compressed kinetic state.

**Discarded information.** Particle identities, connected correlations,
interaction graphs, rare events, and histories.

**Candidate learned objects.** Correlation or collision corrections,
projected-cumulant dynamics, kinetic residuals, memory kernels, or a kinetic
solution operator.

**Candidate methods.** Classical mean-field or kinetic operators, analytic
correlation corrections, weak-form equation discovery, explicit cumulant
closures, learned residual operators, finite-memory models, and kinetic neural
operators or PINOs when paired families of solutions are available.

**Primary evidence.** Distributional error, two- and higher-particle
cumulants, hierarchy residual, collective-mode and transport statistics,
classical-limit recovery, and long-time kinetic rollouts.

### Stage 3: kinetic-to-moment closure

**Question.** Which moments or memory variables close a fluid-scale model over
both near-equilibrium and breakdown regimes?

**Retained state.** Density, momentum, energy, and a predeclared set of
additional moments or latent closure coordinates.

**Discarded information.** Velocity-space structure, non-Maxwellian tails,
higher moments, correlations, and relaxation history.

**Candidate learned objects.** Stress, heat flux, production/relaxation terms,
hyperbolic moment closures, memory states, or a moment-solution operator.

**Candidate methods.** Classical constitutive laws, Grad or maximum-entropy
closures, explicit cumulant closures, Christlieb-style hyperbolic learned
closures, finite-memory corrections, structure-preserving learned residuals,
and neural operators or PINOs for parameterized reduced solution maps.

**Primary evidence.** Stress and heat-flux accuracy, realizability,
hyperbolicity, conservation, entropy behavior, recovery of equilibrium and
classical transport limits, embedded-solver stability, and application
observable error.

### Stage 4: TEMPEST application transfer

**Question.** Do failure diagnostics and closure-design principles validated
in canonical and particle-resolved settings help construct a reliable closure
for a distinct TEMPEST application?

The proposed test is core-collapse-supernova turbulence. Candidate models
predict a declared decomposition of

\[
C_{\mathrm{SN}}^\star[X]
=\langle F_{3\mathrm D}(X)\rangle_\Omega
-F_{1\mathrm D}(\langle X\rangle_\Omega),
\]

such as Reynolds stress or turbulent pressure, turbulent energy/enthalpy
flux, production, dissipation, mixing, or a bounded memory state. PINNs are
evaluated as equation-informed solvers for particular inverse or forward
instances; neural operators and PINOs are evaluated on families of progenitor,
forcing, and closure inputs; learned closures are embedded in the 1D carrier;
and a world model is admitted only if the benchmark defines a genuine
sequential intervention rather than a fixed parameter sweep.

Transfer success means that a predeclared diagnostic, representation rule, or
constraint improves supernova closure selection or rollout after
supernova-specific fitting. It does not mean that a dusty-plasma force law or
a canonical theorem is used unchanged in the supernova model.

## Proposed dusty-plasma reference family

A useful controlled family contains heterogeneous dust particles with
confinement, drag, screened repulsion, nonreciprocal wake effects, external
forcing, and an optional dynamical wake variable. A schematic reference is

\[
m_i \dot v_i = F_i^{\mathrm{conf}} + F_i^{\mathrm{ext}}
- \gamma_i v_i + \sum_{j\ne i}F_{ij}(r_i,r_j,\zeta_j;\mu)+\eta_i,
\qquad
\tau_w \dot\zeta_j = \zeta_{\mathrm{eq}}(\mathcal E_j)-\zeta_j,
\]

where $\mathcal E_j$ summarizes the local plasma environment. The family
should vary particle count, density/coupling, screening, charge and mass
heterogeneity, wake relaxation $\tau_w$, forcing amplitude and frequency,
and forcing history. The exact force and wake model must be selected with the
dusty-plasma scientific owner; this equation is a benchmark design, not an
assertion that one model is universally correct.

The controlled regimes are:

1. **Instantaneous pair regime:** small $\tau_w$, weak collective effects;
2. **Contextual many-particle regime:** local geometry changes the effective
   interaction even when explicit memory is weak;
3. **Finite-memory regime:** wake or field relaxation is comparable to the
   resolved dynamics; and
4. **Collective/nonlocal regime:** a pairwise representation is structurally
   insufficient.

## Proposed supernova reference family

The high-fidelity family should contain 3D core-collapse-supernova
radiation-hydrodynamic or (M)HD simulations at multiple resolutions or filter
widths, including shock-turbulence interaction and the upstream/downstream
fluctuations that drive it. The retained state is an angle- or volume-averaged
1D radial model. Discarded information includes nonradial velocity, entropy,
and composition fluctuations; anisotropic Reynolds stresses; shock
corrugation; intermittent transfer; subgrid cascade; and unresolved history.

The first nested comparison is:

1. unaugmented 1D carrier;
2. declared local RANS, mixing-length, or STIR-like baseline;
3. explicit turbulent-energy/Reynolds-stress augmentation;
4. structure-preserving learned residual with the same retained state;
5. finite-memory augmentation; and
6. an end-to-end operator surrogate as a labeled control.

The decisive test is not closure-target error alone. Each candidate must be
embedded in the same 1D carrier and scored on shock-radius history, shock
revival or runaway timing/classification, turbulent support, conservation and
realizability, explosion energy, nucleosynthesis-sensitive histories, failure
rate, and total cost. A model that improves a projected 3D stress but destabilizes
the shock trajectory fails the application gate.

## Cross-cutting decisive experiment

Across wake relaxation, density, and forcing history, compare the same nested
model family:

1. analytic instantaneous pair law;
2. learned instantaneous pair kernel;
3. instantaneous equivariant many-particle graph model;
4. finite-memory graph or auxiliary-state model; and
5. unrestricted black-box dynamics control.

This experiment locates where pairwise information stops being sufficient,
where many-particle context becomes necessary, and where explicit memory earns
its cost. Projected cumulants, interaction-history complexity, and closure
residuals are evaluated as pre-error indicators of those boundaries. The
resulting particle ensembles then feed Stages 2 and 3, allowing the benchmark
to ask whether the same diagnostics predict failure at kinetic and moment
levels.

## Method roles and fairness

There is no scientifically meaningful single leaderboard because the methods
approximate different objects.

| Method family | Fair role in the pipeline |
|---|---|
| Analytic or numerical baseline | Trusted reduced operator, asymptotic anchor, or reference solver |
| Interaction kernel method | Interpretable effective force under an explicit particle representation |
| Graph particle model | Contextual or memory-dependent particle dynamics |
| PINN | One equation-constrained solution or inverse instance |
| Neural operator | A family of input-to-solution maps learned from paired simulations |
| PINO | The same operator target with paired data and equation residuals |
| Learned closure | An identified residual embedded in a retained solver |
| Structured dynamics | A vector field or flow map with stated stability, geometric, or thermodynamic structure |
| World model | Action-conditioned latent rollout for real sequential interventions |

Methods are compared directly only when they target the same object and use
matched information. Cross-family comparisons report the different task,
information, and deployment cost rather than hiding them in a scalar score.

## Scorecards and claim gates

Each stage produces its own scorecard:

- **target and identifiability:** force, residual, flux, operator, or flow-map
  error with estimator uncertainty;
- **dynamics:** short and long rollouts, invariant statistics, event timing,
  and fraction of stable runs;
- **closure diagnosis:** cumulant, memory, and history features versus measured
  closure failure;
- **physical validity:** conservation, positivity, realizability,
  hyperbolicity, entropy, symmetry/equivariance, and causality as applicable;
- **limits and robustness:** classical-limit recovery, interpolation,
  extrapolation, failure-boundary detection, and transfer;
- **resources:** high-fidelity calls, observations, ensemble members, training
  compute, inference latency, online diagnostic cost, and total cost at a fixed
  application error.

A cross-stage synthesis records which retained information first becomes
necessary, whether that information remains useful after further reduction,
and whether its benefit survives solver feedback. It does not average unlike
tasks into a universal winner.

## Reproducible execution sequence

1. **Predeclare.** Freeze states, equations, scaling coordinates, forcing
   regimes, splits, observables, uncertainty estimators, budgets, and gates.
2. **Verify references.** Demonstrate numerical convergence and required
   physical checks before generating learning targets.
3. **Generate ensembles.** Save versioned manifests, units,
   nondimensionalization, randomization, and solver provenance.
4. **Project and diagnose.** Compute marginals, moments, cumulants, histories,
   closure defects, estimator uncertainty, and classical-limit errors.
5. **Fit matched candidates.** Use one model interface and record every source
   of equation, data, history, structural, and action information.
6. **Evaluate a priori.** Test the learned object on held-out verified targets.
7. **Evaluate a posteriori.** Embed closures in the carrier solver and measure
   stability, feedback, observables, and cost.
8. **Stress and transfer.** Run predeclared asymptotic, controlled-breakdown,
   out-of-distribution, and cross-profile tests with no retuning on test data.
9. **Audit claims.** Apply the claim ladder, retain failures, and separate
   discretization, sampling, estimation, asymptotic, model, and rollout error.
10. **Report.** Generate versioned scorecards, figures, tables, manifests, and
    narrative conclusions from machine-readable results.

## Activation gates

No stage advances to large learned-model sweeps until its reference solutions,
estimators, and classical limits pass review. B1 requires an approved dusty-
plasma physical reference, owner, accessible data or simulator, and independent
validation quantities. B2 requires an approved 3D supernova ensemble, reduced
1D carrier, projection convention, closure-defect estimator, and application
observables. Failure of
cumulant compressibility, finite-memory saturation, pairwise identifiability,
or transfer is a valid result and may narrow or stop the next stage.
