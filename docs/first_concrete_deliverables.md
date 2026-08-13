# First Concrete Deliverables

Status: **Design sketch - implementation not authorized until specifications
and owners are approved**

## D1. Mathematical-to-computational translation

### Purpose

Create the common notation and exact object map required before code or data
generation. This prevents “cumulant,” “closure,” “memory,” and “correlation”
from meaning different things in the analysis, numerical, ML, and application
workstreams.

### Contents

- Microscopic state, ensemble law, marginals, and governing dynamics.
- Kinetic state and collision or interaction operator.
- Connected cumulant definitions through the first practically estimable
  orders.
- Moment map, local-equilibrium manifold, and fluid variables.
- Exact hierarchy residuals and candidate closure defects.
- Time-layer definition and admissible memory state.
- Scaling parameters and the order in which limits are taken.
- Conserved quantities, entropy, positivity, realizability, symmetries, and
  well-posedness requirements.
- Correspondence between theorem quantities and finite-parameter estimators.

### Artifact

`docs/mathematical_translation_specification.md`, containing a notation table,
dependency diagram, estimator definitions, and pseudocode for every diagnostic.

### Acceptance gate

An analyst, numerical scientist, application physicist, and ML researcher can
independently identify the same inputs, outputs, units, and closure residual for
each scale transition.

## D2. Minimal hard-sphere/Boltzmann ensemble benchmark

### Minimum scope

- Homogeneous or simple periodic 2D hard disks first; 3D follows only if needed.
- Event-driven microscopic simulation with independent ensemble members.
- Matching Boltzmann reduced solver or controlled numerical approximation.
- Parameter sweep over particle diameter, expected particle count, density or
  Boltzmann-Grad parameter, initial distribution, and time horizon.
- Collision-event logging sufficient to reconstruct connected histories and
  recollisions for sampled particles.

### Recorded data

- One-particle empirical distributions and selected observables.
- Projected two-, three-, and four-particle connected cumulants.
- Factorization error for specified test functions.
- Collision-graph motif counts, component sizes, circuit rank, and recollision
  counts.
- Boltzmann residual and particle-to-Boltzmann observable error.
- Ensemble standard errors and effective sample sizes.

### Acceptance gate

The benchmark reproduces convergence toward the kinetic description in at
least one controlled regime, identifies a finite-parameter regime with a
measurable closure defect, and demonstrates that the defect is not a sampling
or discretization artifact.

## D3. Minimal NLS/wave-kinetic ensemble benchmark

### Minimum scope

- Cubic NLS on a periodic domain with random Fourier initial data.
- Ensemble pseudospectral solver with convergence checks.
- Wave kinetic solver or controlled resonant-interaction approximation.
- Sweep over box size, nonlinearity strength, spectral initial condition, and
  normalized kinetic time.

### Recorded data

- Spectral density \(\mathbb E|\widehat u_k|^2\).
- Fourth- and sixth-order connected spectral cumulants.
- Wave-kinetic residual and spectrum error.
- Resonant and near-resonant interaction statistics.
- Comparison of global unrolling with time-layered state updates.

### Acceptance gate

The code reproduces the wave-kinetic prediction over a verified regime and
shows whether a projected higher-cumulant or history state improves the first
observed breakdown regime.

## D4. Common cumulant and interaction-history data schema

### Required entities

- `run`: code revision, configuration hash, seed, hardware, and status.
- `ensemble`: population definition, member count, sampling design, and
  uncertainty metadata.
- `state`: microscopic, kinetic, moment, or fluid fields with units and grids.
- `observable`: test function, estimator, normalization, and uncertainty.
- `cumulant`: order, basis, indices, value, estimator bias correction, standard
  error, and sample count.
- `interaction_event`: participants or modes, time, geometry or resonance
  metadata, and layer identifier.
- `history_graph`: sampled roots, nodes, edges, layer structure, recollisions,
  and graph features.
- `closure_residual`: target equation, discretization, residual convention,
  and uncertainty.

### Storage principles

- Store ensemble definitions and sufficient statistics, not only trajectory
  arrays.
- Separate raw histories from derived graph features.
- Preserve units, nondimensionalization, and estimator provenance.
- Support chunked, append-safe storage without committing large arrays to Git.
- Commit schemas, manifests, and small fixtures.

### Acceptance gate

Both canonical benchmarks can write the schema and the same analysis routine
can read cumulants, histories, and closure residuals without system-specific
branching in the core interface.

## D5. Factorization and closure-failure diagnostic notebook

### Required panels

1. One-particle distribution or spectrum versus reduced-model prediction.
2. Projected cumulant magnitude by order and time layer.
3. Factorization error with ensemble uncertainty.
4. Closure residual versus cumulant and graph features.
5. Recollision or interaction-history complexity versus reduced-model error.
6. Singular-value or rank curve for the proposed compressed state.
7. Memory-length ablation.
8. Canonical-to-noncanonical regime map with failure boundaries.

### Required conclusions

The notebook must answer whether closure failure is detectable, compressible,
and history-dependent. It must distinguish numerical error, estimator error,
and genuine model-form error.

### Acceptance gate

The notebook runs from committed small fixtures, regenerates its figures, and
contains an automated check preventing unsupported claims when uncertainty is
larger than the reported effect.

## D6. MTF mathematical translation specification

### Required mapping

| Canonical mathematical object | MTF slab counterpart |
|---|---|
| Microscopic interacting system | Particle/MD or PIC description with species and fields |
| One-particle kinetic state | Species Vlasov-Fokker-Planck or Landau distributions |
| Connected particle cumulants | Species correlations and selected pair/history statistics |
| Local-equilibrium manifold | Magnetized Maxwellian or stated reference manifold |
| Hydrodynamic variables | Grad moments, two-fluid variables, and radiation-MHD state |
| Classical closure | Braginskii heat flux and associated transport tables |
| Closure defect | \(\Delta q_{\mathrm{NL}}\), stress/relaxation corrections, or augmented moments |
| Scaling parameters | Knudsen number, magnetization, coupling, beta, composition, and gradient scales |
| History state | Heat-front, species, collision, or kinetic-tail memory variables |

### Required decisions

- Exact kinetic reference equation and numerical owner.
- First learned target and retained moment set.
- Definition of the Braginskii recovery limit.
- Available particle, kinetic, and experimental data.
- Time-dependent action protocol, if the world-model track remains in scope.
- Integrated observable and uncertainty metric relevant to target design.

### Acceptance gate

Every term in the first reduced MTF closure equation has a dimensional
definition, reference-data estimator, numerical implementation path, and
physical validity test.

## D7. Predeclared success and stop criteria

### Success criteria

- Canonical solvers recover at least one expected scale limit under refinement.
- Cumulant estimates pass ensemble convergence and bias checks.
- A compressed cumulant or memory state improves held-out embedded rollouts
  over the classical Markov closure.
- The correction recovers the classical limit and preserves mandatory
  invariants and admissibility.
- The regime indicator identifies failure boundaries on held-out parameter
  paths.
- Results reproduce from committed configurations and manifests.

### Stop or pivot criteria

- Estimated cumulants remain below sampling or discretization uncertainty.
- Required representation rank or memory grows without practical saturation.
- A priori improvement disappears when the closure is embedded in the solver.
- The learned correction violates conservation, entropy, positivity,
  realizability, or hyperbolicity and cannot be repaired without losing its
  benefit.
- The MTF target cannot be estimated from available reference data.
- Apparent gains rely on information unavailable at inference time.

### Acceptance gate

Threshold values, confidence intervals, resource limits, and decision owners
are approved before large-scale data generation.

## Suggested first 90 days

### Weeks 1-3: mathematical specification

- Complete D1 and the first draft of D6.
- Select projected observables and cumulant estimators.
- Select canonical solver implementations and owners.

### Weeks 4-7: minimal canonical generators

- Produce deterministic smoke cases for the particle and wave tracks.
- Implement ensemble manifests and small schema fixtures.
- Verify conservation and discretization convergence.

### Weeks 8-10: closure diagnostics

- Estimate the first projected cumulants.
- Record collision or interaction histories.
- Produce the first factorization and residual plots.

### Weeks 11-13: feasibility decision

- Run D5 on small verified datasets.
- Approve, narrow, or stop each canonical track.
- Fix the MTF pilot target and reference solver only if the estimator and data
  path are credible.

## Ownership needed

- Mathematical analysis and hierarchy definitions.
- Microscopic and kinetic numerical methods.
- MTF application physics and experimental observables.
- Statistical estimation and uncertainty.
- Structure-preserving ML and reduced dynamics.
- Data engineering, testing, and reproducibility.

