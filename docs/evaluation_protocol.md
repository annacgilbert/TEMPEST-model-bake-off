# Evaluation Protocol

Status: **Draft**

The evaluation has three nested obligations: verify the numerical references,
test the scale-transition mechanism, and only then compare learned models.
The operational sequence is predeclaration, reference verification, ensemble
generation, projection and closure-defect estimation, matched fitting,
a-priori target tests, a-posteriori embedded rollouts, breakdown and transfer
tests, and a final claim audit. See
[`experimental_pipeline.md`](experimental_pipeline.md) for the canonical
end-to-end description.

We built an evaluation harness for computational closure methods: a fixed suite
of test problems and forcing regimes, a common interface through which any
closure model—analytic, learned, or hybrid—is invoked, and a standardized
battery of accuracy, stability, and cost metrics computed uniformly across
candidates. The harness separates the science (the closures) from the
scaffolding (data handling, integration, scoring), so that adding a new method
requires implementing one interface, and every reported comparison is
reproducible and fair by construction.

## 1. Numerical reference verification

- Resolution, time-step, domain-size, and particle/ensemble convergence.
- Conservation, positivity, entropy, symmetry, and boundary checks as relevant.
- Cross-solver or manufactured-solution checks where feasible.
- Numerical uncertainty attached to every derived target.

## 2. Asymptotic and hierarchy validation

- Recovery of the declared classical limit in its expected scaling regime.
- Measured convergence rate versus the relevant small parameter.
- One-point marginal or moment agreement.
- Projected cumulant magnitude and hierarchy-residual norms.
- Factorization-defect and memory-diagnostic curves over time.
- Controlled counterexamples outside the validity assumptions.

Failure to recover the expected limit is a solver, estimator, or specification
problem until ruled out; it is not evidence for a learned correction.

## 3. Statistical estimator validation

- Bias and variance studies versus ensemble size.
- Confidence intervals for marginals, cumulants, residuals, and memory kernels.
- Sensitivity to projection basis, truncation order, and time window.
- Ergodic/homogeneity tests when spatial or temporal averages replace ensembles.
- Signal-to-uncertainty ratio for every claimed closure effect.

## 4. Closure diagnostics

Evaluate closures in both modes:

### A priori

Compare predicted and reference closure terms on held-out high-fidelity states.
Report pointwise, integral, spectral, and regime-conditioned errors.

### A posteriori

Embed the closure in the reduced solver and report stability, accumulated
state error, observable error, and computational cost. A low a-priori error
does not establish a useful closure if solver feedback is unstable.

### Linked-stage evaluation for the B1 dusty-plasma profile

If the dusty-plasma ladder is activated, evaluate three distinct retained
states rather than calling all trajectory models closures of the same kind:

1. **effective interaction:** held-out force/acceleration error,
   identifiability on the empirical occupancy measure, decomposition into
   internal/external/drag terms, independent physical quantities, and stable
   particle rollouts;
2. **particle to kinetic:** distributional error, factorization defect,
   projected cumulants, hierarchy residual, modes/transport, classical-limit
   recovery, and kinetic rollout; and
3. **kinetic to moment:** stress and heat-flux error, realizability,
   hyperbolicity, conservation/entropy, constitutive-limit recovery, and
   moment-solver rollout.

The cross-cutting regime sweep varies wake or field relaxation, density, and
forcing history while nesting an analytic pair law, learned pair kernel,
instantaneous graph model, and finite-memory graph or auxiliary-state model.
Report the boundary at which each additional information class becomes
necessary and whether cumulant/history diagnostics predict that boundary.

## 5. Physical and mathematical validity

- Conservation-law residuals and cumulative drift.
- Positivity, realizability, entropy production, or hyperbolicity as applicable.
- Causality and decay for memory models.
- Boundary and initial-condition errors.
- Symmetry or equivariance tests when claimed.
- Correct equilibrium, near-equilibrium, and asymptotic behavior.

## 6. Predictive accuracy

- State-space norms with units and normalization stated.
- Derived observable and application-facing errors.
- Spectral, scale-dependent, and tail errors where applicable.
- Calibration and uncertainty metrics for probabilistic methods.
- Error decomposed into discretization, sampling, estimator, closure, learning,
  and rollout components when identifiable.

## 7. Dynamics and robustness

- Short- and long-horizon rollout error.
- Stability under perturbed initial conditions, parameters, and history length.
- Attractor, invariant-measure, event-time, or transition statistics.
- Explicit out-of-distribution and failure-boundary tests.
- Reliability: the fraction of seeds and regimes completing without instability.

## 8. Cross-profile transfer

Test whether the following transfer from a canonical benchmark to an
application profile:

- closure-failure diagnostics;
- cumulant/memory state-selection rules;
- structure-preserving parameterizations;
- uncertainty and stopping criteria;
- architectures only after the above are separated.

Transfer claims must state what was frozen, tuned, or retrained and which
test-profile information was available.

For transfer from canonical or dusty-plasma settings to the supernova profile,
only diagnostic logic, state-selection rules, structural parameterizations,
uncertainty procedures, and stopping criteria are presumed portable.
Coefficients, weights, state variables, projection conventions, and theorem
assumptions are supernova-specific unless an explicit experiment establishes
otherwise.

### Supernova 3D-to-1D evaluation

The B2 profile must separate projection error from closure error. Report the
3D reference resolution/filter study, angular or volume averaging convention,
Favre/Reynolds decomposition, shock-alignment procedure, radial/time sampling,
and uncertainty of each projected turbulent term. Compare candidates first on
held-out Reynolds stress, turbulent pressure, flux, production, dissipation,
mixing, or memory targets and then after embedding in the same 1D carrier.

The application scorecard must include mean shock-radius history, shock
revival or runaway classification and timing, turbulent kinetic energy and
support, conservation and Reynolds-stress realizability, explosion energy,
nucleosynthesis-sensitive thermodynamic histories, stable-run fraction, and
end-to-end cost. Improvements that disappear under carrier feedback or rely on
nonconservative source terms do not pass the embedded-closure gate.

## 9. Efficiency

- Data-generation cost, including discarded ensemble members.
- Training wall time, device hours, peak memory, and energy if available.
- Inference latency and throughput at controlled batch sizes.
- Reference-solver calls required at training and inference time.
- Cost of estimating cumulants, histories, or latent state online.
- End-to-end cost to achieve a fixed application error.

## 10. Reproducibility and statistical reporting

- Committed configuration and code revision.
- Data and result manifest identifiers.
- Random seeds and deterministic settings.
- Hardware and software environment.
- Predeclared seed counts, aggregation, uncertainty intervals, and paired tests.
- Failure state, traceback or diagnostic, and retained partial metrics.

Failed runs remain part of reliability metrics; "no runs" is not an exclusion
category.

## 11. Minimum claim ladder

| Claim level | Minimum evidence |
|---|---|
| Numerical observation | Converged reference and estimator uncertainty |
| Closure correlation | Held-out association with a measured closure defect |
| Predictive closure | A-priori improvement over matched classical baselines |
| Useful embedded closure | Stable a-posteriori improvement at reported cost |
| Regime-adaptive closure | Predeclared success and failure detection across asymptotic and breakdown regimes |
| Transferable principle | Repeated evidence on a canonical track and at least one TEMPEST application profile |

No result should be described as a general closure principle below the final
claim level.

## 12. Scorecard policy

There is no single overall leaderboard. Every experiment reports the following
separate scorecards where applicable:

1. target accuracy and identifiability;
2. dynamics and reliability;
3. closure diagnosis and failure-boundary detection;
4. physical and mathematical validity;
5. classical-limit recovery, robustness, and transfer; and
6. information and computational cost.

Models are directly ranked only when they approximate the same mathematical
object. A cross-stage synthesis may state the smallest sufficient information
set, whether the extra state or memory survives solver feedback, and whether a
design principle transfers, but it may not average force, solution, operator,
closure, and world-model scores into one scalar winner.
