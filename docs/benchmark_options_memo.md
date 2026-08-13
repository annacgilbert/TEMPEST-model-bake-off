# Design-Meeting Memo: A Mathematical Closure Program with an MTF Flagship

**To:** TEMPEST benchmark design group  
**From:** TEMPEST Model Bake-Off planning team  
**Date:** August 8, 2026  
**Subject:** Joining rigorous scale-limit diagnostics, an AI/ML closure bake-off, and the magnetic-target-fusion line of sight

## Decision requested

Approve a two-layer program:

1. a **canonical mathematical closure track** that turns ideas from rigorous
   particle-to-kinetic, wave-to-kinetic, and kinetic-to-fluid limits into
   numerical experiments; and
2. a **TEMPEST application track**, with nonlocal magnetized heat transport in
   magnetic target fusion (MTF) as proposed Application Profile 1.

Authorize a 90-day specification and pilot phase. Do not yet authorize a
full-model bake-off. The immediate decisions are which reference solvers and
scientific owners support the canonical pilots and MTF profile, which
correlation/history quantities are estimable, and what evidence will justify
moving from diagnostics to learned closures.

## Bottom line

Andrew Christlieb's slides give TEMPEST a concrete line of sight: retain
radiation-MHD as the engineering carrier, identify where local Braginskii
transport fails, learn a constrained nonlocal correction from kinetic data,
validate it in a controlled slab, and test whether it improves an MTF design
quantity. That is an excellent flagship application.

It is not, by itself, the general foundational experiment originally intended
for the bake-off. The new mathematical idea supplies that missing foundation.
The three motivating papers study when complicated microscopic or field
dynamics genuinely reduce to kinetic or fluid equations. Their useful
computational lesson is not simply "use a neural network." It is that closure
quality is controlled by connected correlations, interaction histories,
scaling regimes, and carefully accumulated remainder terms. Those objects can
become diagnostics, state variables, and correction targets in a numerical
program.

The combined program asks a sharper question:

> Can we measure when a reduced model is valid, identify the smallest
> correlation or memory state that predicts its failure, and learn a
> structure-preserving correction that remains useful after solver embedding?

That question is general enough to support TEMPEST's foundational AI/ML goals
and concrete enough to be tested in MTF.

## What Andrew's slides are actually proposing

The slides organize TEMPEST activity around an MTF application rather than an
abstract model comparison. An axial current produces an azimuthal magnetic
field and inward \(\mathbf J\!\times\!\mathbf B\) compression. During an
implosion, temperature, density, ionization, collisionality, and magnetization
cross regimes in which local, near-Maxwellian transport assumptions may fail.

The trusted carrier is integrated radiation-MHD with equation-of-state,
opacity, radiation, and reduced transport models. The initial missing physics
is nonlocal electron heat transport beyond the Braginskii regime. The proposed
learned object is approximately

\[
q=q_{\mathrm{Braginskii}}+\Delta q_{\mathrm{nonlocal}},
\]

possibly mediated by an evolved Grad-moment state. A regime indicator should
recover or fall back to Braginskii when local collisional assumptions hold.
The closure must respect conservation, positivity/admissibility,
hyperbolicity, stability, and appropriate entropy behavior.

The proposed pilot is a 1D-in-space, 2D-in-velocity plasma slab with a density
or composition gradient and a boundary heat pulse or localized deposition.
It sweeps from local collisional transport through the nonlocal transition
toward free streaming. Candidate coordinates include Knudsen number,
magnetization \(\omega_c\tau\), plasma beta, gradient scale, Mach number,
composition, and ionization state. The intended progression is from a slab and
kinetic reference, to a learned closure inside two-fluid/MHD, to higher
dimensions, experimental validation, and a partner-relevant design study.

In plain terms, Andrew is proposing **an engineered kinetic-to-MHD closure
program for fusion**, not a general contest among PINNs, neural operators, and
world models. Our experiment should provide the general closure science and
fair comparison machinery underneath that application program.

## What the three mathematical papers add

The papers motivate three canonical scale transitions:

- [Hard-particle dynamics to Boltzmann](https://arxiv.org/abs/2408.07818):
  long-time kinetic behavior is controlled through cumulant/cluster structure,
  interaction histories, exceptional events, and time-layered estimates.
- [Hard particles through kinetic to hydrodynamic limits](https://arxiv.org/abs/2503.01800):
  a chain from microscopic dynamics to Boltzmann and onward to Euler or
  Navier-Stokes-Fourier exposes where errors enter at each reduction.
- [Nonlinear Schrodinger dynamics to the wave kinetic equation](https://arxiv.org/abs/2311.10082):
  spectral cumulants and organized resonant interaction histories play a role
  analogous to particle correlations in a wave system.

These are not plug-and-play MTF closures. The proposal is to translate their
analysis into falsifiable computational hypotheses:

1. **Detectability:** projected connected correlations rise before the
   classical reduced model develops large error.
2. **Compressibility:** a low-order, low-rank cumulant state explains a useful
   portion of the exact closure defect.
3. **Finite memory:** time-layered interaction summaries outperform a purely
   Markovian correction at comparable state dimension.
4. **Transfer:** diagnostics validated on canonical systems can help select
   closure state and identify failure regimes in MTF, even if coefficients and
   architectures must be retrained.

The proof machinery should guide the numerics without being copied literally.
The first implementation should estimate projected cumulants, hierarchy
residuals, and finite interaction-history summaries—not attempt to reproduce
every combinatorial cutting or diagrammatic construction in the proofs.

## Proposed benchmark architecture

### Track A: canonical mathematical validation

**A1. Hard particles to Boltzmann.** Compare particle ensembles and a
Boltzmann solver using one-particle observables, collision statistics,
projected two- and three-particle cumulants, hierarchy residuals, and
factorization-defect curves. Sweep both an expected kinetic regime and a
correlated/recollision breakdown regime.

**A2. Nonlinear waves to wave kinetics.** Compare nonlinear-wave ensembles
and a wave-kinetic solver using spectra, spectral cumulants, resonant-transfer
rates, and layered interaction-history summaries. Sweep weak-nonlinearity and
scale-separation coordinates and include coherent counterexamples.

**A3. Boltzmann to fluid.** Compare kinetic, Euler, and
Navier-Stokes-Fourier descriptions. Measure hydrodynamic moments,
non-equilibrium cumulant/moment coordinates, constitutive residuals, and
convergence as Knudsen number decreases. Include shocks, steep gradients, and
boundary layers as controlled failure cases.

### Track B: TEMPEST application profiles

**B1. MTF nonlocal heat transport.** Use the slab proposed in Andrew's deck.
The first embedded closure target should be the heat-flux correction unless
the scientific owners make a strong case for an evolved moment state first.

**B2. Dusty plasma, candidate.** Retain the earlier dusty-plasma setting as a
second profile for strongly correlated, non-Maxwellian, particle-resolved
dynamics. It is valuable principally as a transfer test; it should not delay
the first canonical and MTF pilots.

## Common evaluation harness

We built an evaluation harness for computational closure methods: a fixed suite
of test problems and forcing regimes, a common interface through which any
closure model—analytic, learned, or hybrid—is invoked, and a standardized
battery of accuracy, stability, and cost metrics computed uniformly across
candidates. The harness separates the science (the closures) from the
scaffolding (data handling, integration, scoring), so that adding a new method
requires implementing one interface, and every reported comparison is
reproducible and fair by construction.

## How the AI/ML bake-off fits

The methods approximate different mathematical objects and must not be ranked
by one undifferentiated score.

| Model family | Natural role in the combined program |
|---|---|
| Numerical reduced model | Classical asymptotic baseline and solver carrier |
| Markov closure | Instantaneous correction from the resolved state |
| Cumulant/moment closure | Evolve selected connected or non-equilibrium coordinates |
| Memory/Mori-Zwanzig model | Represent unresolved history through a kernel or augmented state |
| PINN | Approximate one solution using equations plus declared observations |
| Neural operator | Learn a family of solution maps from paired simulations |
| PINO | Learn that operator with both data and equation residuals |
| Learned closure | Predict the hierarchy, constitutive, heat-flux, or stress residual inside a solver |
| Structured neural dynamics | Evolve a compact state with conservation, entropy, stability, or geometric constraints |
| World model | Predict coarse dynamics conditioned on a real time-dependent intervention |

For the MTF profile, a world model is justified only if heat deposition,
current waveform, magnetic field, or another realizable control varies in
time. A fixed pulse supplied as a parameter defines a conditional surrogate,
not an action-conditioned world model.

Every learned model should be compared with the simplest classical or explicit
cumulant/memory model using the same information. Equation-generated data,
direct closure labels, ensemble cumulants, histories, and inference-time solver
calls must be counted separately.

## First concrete deliverables

The 90-day phase should produce seven reviewable artifacts:

1. **Mathematical-to-computational translation specification:** common notation
   for the high-fidelity state, reduced state, cumulants, history summaries,
   closure defect, scaling variables, and error decomposition in all tracks.
2. **Hard-particle/Boltzmann pilot:** a small converged ensemble data set and
   matching kinetic runs, including a validity and a breakdown regime.
3. **NLS/WKE pilot:** a matched wave ensemble with spectral-cumulant and
   resonant-transfer estimators.
4. **Common cumulant/history schema:** versioned data objects and uncertainty
   metadata that both canonical pilots can write and the model code can read.
5. **Closure-failure diagnostic notebook:** plots testing whether correlations
   and memory predict reduced-model error, with negative results retained.
6. **Canonical-to-MTF translation table:** defensible analogies and explicit
   non-analogies between particle/wave diagnostics and MTF transport physics.
7. **Predeclared gates:** numerical, estimator, scientific-signal, embedded
   closure, and resource thresholds for continuing, revising, or stopping.

Weeks 1-4 should freeze definitions and run very small convergence studies;
weeks 5-8 should generate the two canonical pilot ensembles and estimators;
weeks 9-12 should test the closure hypotheses and complete the MTF translation;
week 13 should hold a gate review. Full PINN/operator/world-model sweeps should
begin only after the reference and estimator gates pass.

## Questions the design meeting must resolve

1. Who owns the hard-particle, NLS/WKE, kinetic-fluid, and MTF reference solvers?
2. What is the smallest feasible canonical configuration for a 90-day pilot?
3. Which cumulant order, projection basis, rank, ensemble size, and history
   horizon are scientifically estimable within available compute?
4. Which MTF kinetic or gyrokinetic solver is authoritative, and what
   numerical/experimental data can be shared?
5. Is the first MTF learned object \(\Delta q_{\mathrm{nonlocal}}\), an evolved
   Grad state, or a staged combination?
6. Which application-facing MTF observable and uncertainty define improvement?
7. What time-dependent intervention, if any, makes the world-model comparison
   physically meaningful?
8. What compute, storage, wall-time, and personnel caps define the pilot?
9. What evidence triggers continue, revise, merge, or stop decisions?

## Recommended meeting outcome

Approve the program title and scope:

> **TEMPEST Mathematical Closure and AI/ML Benchmark Framework**  
> **Flagship Application Profile 1: Nonlocal Magnetized Heat Transport Beyond
> Braginskii**

Assign scientific owners for each reference model, the common statistical data
schema, MTF validation, and benchmark evaluation. Approve the seven pilot
deliverables and the week-13 gate review. Defer broad model implementation and
ranking until the classical limits, cumulant/history estimators, information
budgets, and application metric are fixed.

*Basis: the TEMPEST Full Proposal; Andrew Christlieb's August 2026 “TEMPEST
Line of Sight to Magnetic Target Fusion” preview deck; and the three
mathematical scale-limit papers linked above.*
