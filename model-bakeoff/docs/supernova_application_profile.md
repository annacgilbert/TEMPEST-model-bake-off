# Core-Collapse-Supernova Turbulence Application Profile

Status: **Selected second TEMPEST science application; version-0 numerical
contract remains open**

## Scientific objective

Determine which unresolved three-dimensional turbulence information must be
retained so that a reduced one-dimensional core-collapse-supernova model
predicts selected shock, explosion, and nucleosynthesis-sensitive observables
reliably.

The profile implements the TEMPEST proposal's stated plan to combine 3D DNS,
implicit LES, and LES of supernova shock-turbulence interaction with
self-consistent ML augmentation of a 1D supernova model using volume-averaged
3D turbulence transport effects.

## Closure contract

Let $X(\mathbf{x},t)$ be the selected 3D radiation-hydrodynamic or (M)HD
state, let $\Pi_\Omega$ be the declared angle/volume projection into radial
coordinates, and let $F_{1\mathrm D}$ be the unaugmented 1D carrier operator.
The estimable closure defect is

\[
C_{\mathrm{SN}}^\star[X]
=\Pi_\Omega F_{3\mathrm D}(X)-F_{1\mathrm D}(\Pi_\Omega X).
\]

The version-0 decomposition should select a subset of:

- Reynolds stress and turbulent pressure;
- turbulent kinetic-energy evolution;
- turbulent energy, enthalpy, composition, or lepton flux;
- production, buoyant driving, dissipation, and mixing;
- shock-relative nonlocal features; and
- a bounded causal memory state.

The learned component corrects one declared residual. It does not silently
replace gravity, neutrino transport, the equation of state, shock capturing,
or the complete 1D carrier.

## High-fidelity reference

The reference manifest must record:

- progenitor and initial perturbations;
- radiation/neutrino, gravity, equation-of-state, composition, and magnetic
  assumptions;
- numerical method, grid, resolution, effective filter, and subgrid model;
- shock definition and tracking method;
- ensemble or repeated-realization definition where available; and
- conservation, convergence, and uncertainty evidence.

The first data slice should be small: one or a few matched 3D cases with a
resolution/filter ladder and the corresponding 1D carrier case. Production
data generation waits for the projection and estimator gates.

## Projection and estimator requirements

Before target construction, freeze:

1. angle versus volume averaging;
2. Reynolds versus Favre decomposition;
3. radial binning and interpolation;
4. shock alignment and treatment of moving discontinuities;
5. spatial and temporal filters;
6. derivative/residual discretization;
7. averaging window and ensemble assumptions; and
8. uncertainty from discretization, filter choice, projection, and sampling.

Projection error must be reported separately from closure-model error. A
target is not learnable evidence if its estimator uncertainty is comparable to
or larger than the measured defect.

## Nested candidates

1. unaugmented 1D carrier;
2. declared local RANS, mixing-length, or STIR-like baseline;
3. explicit turbulent-energy or Reynolds-stress closure;
4. structure-preserving learned residual using the same retained state;
5. finite-memory or auxiliary-state augmentation;
6. neural operator or PINO for a declared solution-map family; and
7. end-to-end surrogate as a labeled diagnostic control.

Every candidate declares train-time and inference-time access to the carrier
equations, 3D fields, projected profiles, closure targets, histories, and
solver calls. Direct rankings use matched target, state, data, and compute.

## Regime coordinates and splits

Candidate coordinates include progenitor structure, post-bounce time, shock
strength or Mach number, upstream turbulence intensity and correlation scale,
heating or forcing conditions, resolution/filter width, and magnetic-field
strength where relevant. The science owners must select the version-0 subset.

Hold out complete progenitors, perturbation families, time intervals, and
resolution/filter combinations. Radial zones or frames from the same 3D run
must not be split across training and test sets in a way that leaks the shock
history.

## Scorecard

### Closure target and diagnosis

- stress, pressure, flux, production, dissipation, mixing, and memory errors;
- estimator uncertainty and signal-to-uncertainty ratio;
- state-selection value of cumulants, anisotropy, and history features; and
- closure-failure detection before large shock-trajectory error.

### Embedded dynamics

- mean shock-radius history;
- shock revival or runaway classification and timing;
- turbulent kinetic energy, Reynolds stress, and turbulent support;
- explosion energy;
- nucleosynthesis-sensitive thermodynamic histories;
- long-rollout stability and failed-run fraction.

### Physical and mathematical validity

- conservative coupling and cumulative energy drift;
- lepton-number accounting as represented by the carrier;
- positivity and Reynolds-stress realizability;
- causal, decaying memory;
- shock-capturing stability; and
- recovery of the declared zero-turbulence or calibrated local baseline.

### Resources

- 3D reference cost and discarded runs;
- projection and online-diagnostic cost;
- training and inference cost;
- 1D carrier overhead; and
- total cost at fixed application error.

## Activation gates

Production runs begin only when:

- the 3D reference and 1D carrier have named owners;
- the projection and shock-alignment convention is frozen;
- numerical and projection uncertainty is below the first target signal;
- the first turbulent term and application observable are fixed;
- the unaugmented and local turbulence baselines reproduce their declared
  limits; and
- conservative embedded evaluation is implemented.

Stop or narrow the profile if the target is not identifiable under the
available resolution/filter hierarchy, if projection choices dominate the
signal, if a priori gains vanish after embedding, or if conservation and
realizability cannot be enforced without losing the claimed benefit.

## Scientific basis

- TEMPEST Full Proposal, sections proposing stellar-turbulence DNS/LES,
  supernova shock-turbulence interaction, and augmentation of a 1D supernova
  model with volume-averaged 3D turbulence transport effects.
- Couch, Warren, and O'Connor,
  [STIR](https://arxiv.org/abs/1902.01340).
- Müller,
  [A Critical Assessment of Turbulence Models for 1D Core-Collapse Supernova
  Simulations](https://arxiv.org/abs/1902.04270).
- Abdikamalov et al.,
  [Shock-Turbulence Interaction in Core-Collapse
  Supernovae](https://arxiv.org/abs/1605.09015).
