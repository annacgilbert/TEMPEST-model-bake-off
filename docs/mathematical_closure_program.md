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

The first proposed application profile is nonlocal magnetized heat transport
beyond Braginskii in a 1D2V plasma slab. Dusty plasma is a candidate second
profile for testing transfer to strongly correlated, particle-resolved data.

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
4. **Transfer:** the representation and diagnostics learned in canonical
   systems remain useful, after physics-specific adaptation, in at least two
   TEMPEST application profiles.

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

#### B1. MTF nonlocal heat transport

- Hierarchy: particle/MD or PIC to Vlasov-Fokker-Planck/Landau to Grad or
  two-fluid MHD to radiation-MHD.
- Trusted limit: Braginskii transport in the collisional, near-Maxwellian,
  small-Knudsen regime.
- Initial target:
  \[
  q=q_{\mathrm{Braginskii}}+\Delta q_{\mathrm{NL}}.
  \]
- Candidate augmented state: non-Maxwellian moments, projected species
  correlations, pressure anisotropy, and a heat-front memory state.
- Required constraints: conservation, admissibility, positivity,
  hyperbolicity, entropy behavior, symmetry, and recovery of the Braginskii
  limit.

#### B2. Dusty-plasma transfer profile

- Hierarchy: particle tracking or DRIAD to kinetic statistics to moment or
  coarse collective dynamics.
- Purpose: test transfer to strong correlations, anomalous transport, and
  experimentally observable particle cumulants.
- Status: candidate; not part of the first implementation milestone.

## Closure models to compare

1. Classical Markov kinetic or fluid closure.
2. Explicit finite-cumulant or finite-moment closure.
3. Finite-memory closure using kernels or auxiliary variables.
4. Structure-preserving learned cumulant/memory correction.
5. Direct black-box surrogate as a diagnostic control, not the default model.

PINNs, neural operators, PINOs, structured neural dynamics, and world models
remain in the broader bake-off, but they approximate different mathematical
objects. The closure and structured-dynamics tracks are the center of this
mathematical program.

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

