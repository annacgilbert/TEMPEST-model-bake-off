# Experimental program and decision gates

## Central question

Does a compact, time-oriented representation of connected interaction history
predict the error of a classical kinetic closure better than the retained state
and scalar cumulant magnitudes alone?

## Hypotheses

- **H1, scaling:** classical closure defects decay under the theorem's kinetic
  scaling on fixed reduced-time intervals.
- **H2, detectability:** projected low-order cumulants and history features
  detect finite-scale closure error before macroscopic observables drift.
- **H3, orientation:** time-oriented features outperform unordered norms on
  forward/reverse paired data.
- **H4, compression:** a bounded history sketch performs comparably to exact
  small-graph features on held-out layers.
- **H5, correction:** a conservative defect correction improves long-time
  rollout without degrading invariant preservation or stability.
- **H6, abstention:** calibrated uncertainty identifies out-of-distribution
  regimes where the correction should be disabled.

## Phase 0: mathematical and estimator audit

Deliverables:

1. notation crosswalk for the three papers;
2. exact tests for moment-to-cumulant conversion;
3. exact tests for temporal multigraph components and circuit rank;
4. synthetic two-layer molecules for checking the simplified cutting logic;
5. a provenance table stating which quantities are exact theorem objects,
   finite-scale estimators, or heuristic proxies.

Gate: do not run expensive ensembles until the estimators pass synthetic cases
with known independence, correlation, cycle rank, and time reversal.

## Phase 1: wave pilot (recommended first scientific experiment)

### Regime

Use a computationally affordable periodic cubic NLS test before attempting the
full theorem limit. Sweep box size `L`, nonlinearity exponent `gamma`, ensemble
size, spectral resolution, and layer width in kinetic time.

### Compared models

1. WKE baseline;
2. WKE plus Markovian residual based on the current spectrum;
3. WKE plus spectrum and fourth/sixth cumulants;
4. WKE plus cumulants and oriented resonant-history features;
5. oracle one-layer correction, used only to quantify headroom.

### Primary targets

- one-layer spectral increment error;
- weak WKE residual;
- flux error;
- long-time spectrum and invariant drift;
- calibration of predicted defect magnitude.

### Negative controls

- shuffle history features across ensemble members;
- reverse layer order;
- destroy hyperedge time orientation while retaining motif counts;
- condition on a future layer to quantify leakage;
- replace connected cumulants with raw moments of the same dimension.

Gate: continue only if history improves held-out defect prediction beyond the
spectrum-plus-cumulant model at matched parameter count and data budget.

## Phase 2: hard-sphere pilot

### Regime

Begin with two-dimensional hard disks for throughput and debugging, then
confirm selected cases in three dimensions. Use periodic boxes and low packing
fractions. Sweep `epsilon` and `N` along approximate Boltzmann--Grad curves.

### Measurements

- weak one-particle density coefficients;
- connected pair and triplet coefficients;
- tagged-particle ancestry graphs;
- circuit rank and repeated-pair recollisions;
- weak Boltzmann residuals;
- EDMD versus Boltzmann/DSMC observables.

### Bias and variance audit

Report ensemble size, effective distinct tuples, finite-`N` corrections,
bootstrap or replicate uncertainty, and sensitivity to basis dimension. Never
interpret a noisy high-order cumulant as physical without a null-ensemble
calibration.

Gate: the observed residual and cumulant estimates must converge under ensemble
and resolution refinement before fitting corrections.

## Phase 3: exact small-molecule computation

On small tagged collision histories, enumerate the physical molecule and a
restricted family of valid cuts. Compare:

- empirical history frequency;
- numerical quadrature or importance sampling of the associated restricted
  integral;
- proof upper-bound score; and
- learned defect score.

This phase tests whether the cutting logic can support a numerical certificate
or variance-reduction method. It is not on the critical path for the Phase 1
paper.

## Phase 4: kinetic to fluid

Use an asymptotic-preserving Boltzmann solver and matched Euler/NSF solvers.
Measure the non-Maxwellian micro state, stress, heat flux, and solver
disagreement across Knudsen and Mach sweeps. Test an adaptive selector among
fluid, kinetic, and corrected-fluid evolution.

Gate: selection must reduce total cost at a fixed accuracy and stability target
without using unavailable microscopic information at deployment.

## Data schema

Each layer record should contain:

```text
run_id, ensemble_id, regime_parameters, seed
t_start, t_end, layer_index
retained_state, projected_cumulants
history_features, history_schema_version
baseline_increment, observed_increment, closure_defect
invariants, numerical_error_estimates, statistical_uncertainty
solver_versions, code_commit, config_hash
```

Raw trajectories and Fourier fields remain separate from derived layer tables.
Every derived feature records the exact raw-data and code version used to
produce it.

## Paper-level acceptance criteria

The first paper should not be submitted as an algorithm paper unless it shows:

1. a reproducible microscopic/reduced paired dataset;
2. statistically resolved connected-cumulant estimates;
3. a forward/reverse or history-shuffle experiment;
4. improvement on held-out regimes, not only interpolation;
5. stable corrected rollout or a reliable abstaining validity indicator; and
6. a clear statement of which theorem-inspired quantities are proxies.

