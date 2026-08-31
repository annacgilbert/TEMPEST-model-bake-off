# Mathematical Closure Program

Status: **Draft program architecture**

## Purpose

Turn rigorous scale-limit analysis into a computational program for detecting,
representing, and correcting closure failure. The program connects two kinds of
evidence:

1. theorem-faithful canonical systems in which microscopic-to-kinetic and
   kinetic-to-fluid limits can be tested numerically; and
2. TEMPEST application profiles in which the assumptions behind those limits
   fail and an augmented closure is needed.

The application layer contains two complementary profiles. Dusty plasma makes
eliminated fields, strong correlations, context, and memory observable in
particle-resolved data. Core-collapse supernovae test a different reduction:
whether unresolved 3D shock-turbulence dynamics can be represented
self-consistently in a reduced 1D carrier.

## Mathematical foundations

Three papers motivate one connected program:

- Deng, Hani, and Ma, [*Long time derivation of the Boltzmann equation from
  hard sphere dynamics*](https://arxiv.org/abs/2408.07818), organize departure
  from particle independence through cumulants, time layers, partial time
  expansions, and collision-history diagrams called molecules.
- Deng, Hani, and Ma, [*Hilbert's sixth problem: derivation of fluid equations
  via Boltzmann's kinetic theory*](https://arxiv.org/abs/2503.01800), connect the
  particle-to-Boltzmann limit to compressible Euler and incompressible
  Navier-Stokes-Fourier limits under stated scalings and preparation
  assumptions.
- Deng and Hani, [*Long time justification of wave turbulence
  theory*](https://arxiv.org/abs/2311.10082), use time-layered spectral
  cumulants and canonical layered gardens to justify the wave kinetic equation
  over its full lifespan.

These are not ready-made plasma or turbulence closures. They provide a
mathematical organization of what a reduced description discards and a way to
state when that discarded information remains negligible.

## Hierarchy and closure defect

Let \(F_N(Z_N,t)\) denote an ensemble density for a microscopic \(N\)-body
system and \(f_s(z_1,\ldots,z_s,t)\) its \(s\)-particle marginals. At second
order, write

\[
f_2(z_1,z_2,t)
=
f_1(z_1,t)f_1(z_2,t)+g_2(z_1,z_2,t),
\]

where \(g_2\) is the connected two-particle correlation. Higher connected
cumulants \(g_3,g_4,\ldots\) measure departures from lower-order
factorization.

A generic first-level reduced equation can be organized as

\[
\partial_t f_1
=
\mathcal L f_1
+
\mathcal C[f_1]
+
\mathcal R[g_2,g_3,\ldots].
\]

The classical closure either neglects \(\mathcal R\) or absorbs its asymptotic
effect into \(\mathcal C\). The computational target is not the full
high-dimensional cumulant hierarchy. It is the smallest representation of
\(\mathcal R\) needed to predict selected resolved observables over the desired
time horizon.

For basis or test functions \(\psi_i\), projected statistics include

\[
a_i=\mathbb E[\psi_i(Z)],
\qquad
\kappa_{ij}
=
\mathbb E[\psi_i(Z)\psi_j(Z)]-a_i a_j,
\]

with analogous higher connected cumulants. Candidate compression mechanisms
include spectral bases, low-rank tensors, random sketches, collision-graph
features, and learned encoders.

## Time-layered computational state

The long-time proofs avoid expanding the leading solution from the current
time all the way back to \(t=0\). They restart short-time expansions at later
base times while propagating structured information about connected
correlations.

A computational analogue is

\[
S_\ell
=
\left(f_1^\ell,\Pi_r g_2^\ell,\Pi_r g_3^\ell,h_\ell\right),
\qquad
S_{\ell+1}=\Phi_\theta(S_\ell;\mu),
\]

where \(\Pi_r\) is a controlled projection, \(h_\ell\) is a finite history
state, and \(\mu\) contains scaling and physical parameters. The baseline
kinetic or fluid evolution remains explicit; \(\Phi_\theta\) supplies only the
unresolved cumulant or memory contribution.

## Central hypotheses

The program tests four falsifiable hypotheses:

1. **Detectability:** projected cumulants or interaction-history features
   identify the onset of closure failure before large resolved-state error.
2. **Compressibility:** the dynamically important closure defect occupies a
   low-dimensional or otherwise tractable representation.
3. **Finite memory:** a bounded history state materially improves long-time
   prediction over a Markov closure without growing indefinitely.
4. **Transfer:** the representation and diagnostics learned in canonical and
   dusty-plasma systems remain useful, after physics-specific adaptation, for
   a core-collapse-supernova turbulence closure.

Failure of any hypothesis is a reportable scientific outcome and triggers a
stop, pivot, or restriction of scope.

## Benchmark architecture

### Track A: canonical mathematical validation

#### A1. Particle-to-Boltzmann

- Microscopic reference: event-driven hard-disk or hard-sphere ensembles.
- Reduced reference: a Boltzmann solver under matching scaling and initial
  data.
- Measured losses: factorization error, projected cumulants, collision-history
  connectivity, recollision counts, and reduced-equation residual.
- Primary question: when and how does propagation of chaos fail at finite
  parameters and finite time?

#### A2. NLS-to-wave-kinetic equation

- Microscopic reference: ensemble pseudospectral cubic NLS.
- Reduced reference: a wave kinetic equation solver.
- Measured losses: spectral covariance error, fourth- and sixth-order connected
  cumulants, resonant-interaction history, and kinetic-equation residual.
- Primary question: what history state is needed beyond a random-phase or
  Gaussian closure?

#### A3. Boltzmann-to-fluid

- Kinetic reference: Boltzmann solutions approaching the appropriate
  hydrodynamic scaling.
- Reduced references: compressible Euler and incompressible
  Navier-Stokes-Fourier.
- Measured losses: departure from local Maxwellians, Hilbert-expansion
  remainder, constitutive flux error, and macroscopic limit error.
- Primary question: can a regime indicator detect the boundary of validity of
  the fluid closure?

### Track B: TEMPEST application profiles

#### B1. Dusty-plasma many-body closure ladder

- Hierarchy: particle tracking or DRIAD to kinetic statistics to moment or
  coarse collective dynamics.
- Purpose: test transfer to strong correlations, anomalous transport, and
  experimentally observable particle cumulants.
- Proposed internal ladder:
  1. infer effective pair, environment, graph, or memory-dependent forces after
     eliminating plasma and wake degrees of freedom;
  2. test the particle-to-kinetic factorization and correlation closure;
  3. test kinetic-to-moment stress, flux, production, and memory closures; and
  4. compare which diagnostics persist across the two reductions.
- Decisive coordinates: coupling and density, screening, charge/mass
  heterogeneity, forcing history, and the ratio of wake or field relaxation
  time to resolved particle time.
- Status: retained TEMPEST application profile; production runs remain gated
  on a scientific owner, reference model, independent validation quantities,
  and approved parameter sweep.

#### B2. Core-collapse-supernova turbulence closure

- High-fidelity reference: 3D radiation-hydrodynamic or (M)HD
  DNS/implicit-LES/LES simulations that resolve or quantify shock-turbulence
  interaction over a declared filter and resolution hierarchy.
- Reduced carrier: a 1D spherically symmetric supernova model with the
  minimum thermodynamic, composition, gravity, and neutrino-transport state
  required by the selected science case.
- Projection: angle or volume averaging of the 3D state onto radial profiles,
  with Favre/Reynolds conventions and shock tracking declared before data
  generation.
- Initial target:
  \[
  C_{\mathrm{SN}}^\star[X]
  =\langle F_{3\mathrm D}(X)\rangle_\Omega
   -F_{1\mathrm D}(\langle X\rangle_\Omega),
  \]
  decomposed into Reynolds stress/turbulent pressure, turbulent energy or
  enthalpy flux, production, dissipation, mixing, and optional finite-memory
  terms.
- Candidate augmented state: turbulent kinetic energy, anisotropy or
  Reynolds-stress coordinates, shock-relative features, filtered cumulants,
  and a bounded history state.
- Required constraints: total-energy and lepton-number accounting as provided
  by the carrier, positivity and realizability, stable shock-capturing rollout,
  causal memory, and recovery of the declared zero-turbulence or calibrated
  local baseline.
- Application observables: mean shock-radius history, shock revival or runaway
  classification and timing, turbulent support behind the shock, explosion
  energy, and nucleosynthesis-sensitive thermodynamic histories, with the
  version-0 subset fixed by the supernova science owners.
- Status: selected second TEMPEST science application; exact reference
  simulations, carrier, projections, and acceptance thresholds remain open.

Within B1, the proposed decisive experiment nests an analytic instantaneous pair law, a
learned pair kernel, an instantaneous many-particle graph model, and a
finite-memory graph or auxiliary-state model. Sweeping wake relaxation,
density, and forcing history reveals where pairwise closure fails, where
many-particle context is required, and where memory earns its inference cost.
Projected cumulants and interaction-history complexity are tested as early
warnings of these boundaries. The same ensembles then define kinetic and
moment closure defects, converting interaction learning into an input to the
next two scale transitions rather than an isolated trajectory-prediction task.

The complete cross-track execution sequence is maintained in
[`experimental_pipeline.md`](experimental_pipeline.md).

## Closure models to compare

1. Analytic and statistically identifiable effective interaction laws.
2. Contextual or finite-memory graph particle models.
3. Classical Markov kinetic or fluid closure.
4. Explicit finite-cumulant or finite-moment closure.
5. Finite-memory closure using kernels or auxiliary variables.
6. Structure-preserving learned cumulant/memory correction.
7. Direct black-box surrogate as a diagnostic control, not the default model.

PINNs, neural operators, PINOs, structured neural dynamics, and world models
remain in the broader bake-off, but they approximate different mathematical
objects. The closure and structured-dynamics tracks are the center of this
mathematical program. No single scalar ranking should combine force inference,
solution approximation, operator learning, closure prediction, and controlled
rollout; each is scored against its own declared object and information budget.

## Required numerical evidence

- Convergence across the theorem's or model's scaling parameters.
- Ensemble uncertainty and sample-complexity analysis for cumulant estimates.
- A priori closure-defect accuracy and a posteriori embedded-solver stability.
- Long-time factorization, memory, and resolved-observable errors.
- Conservation, positivity, realizability, entropy, and hyperbolicity tests.
- Ablations over cumulant order, projection rank, memory length, and graph
  features.
- Explicit failure boundaries and comparison with the classical asymptotic
  limit.

## Scope discipline

Do not begin by implementing the proof's full diagrammatic cutting algorithms.
Those algorithms establish mathematical bounds and are not automatically
efficient numerical closures. First instrument canonical simulators so that
cumulants and interaction histories are measurable. Only then test which proof
structures are computationally predictive and compressible.
