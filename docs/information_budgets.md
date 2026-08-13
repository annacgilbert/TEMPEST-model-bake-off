# Information Budgets

Status: **Draft**

Calling everything "training data" hides the central scientific question.
Each comparison must expose which equations, ensembles, correlations,
histories, targets, and solver calls a method receives.

## Scale-transition ledger

Complete this ledger for every benchmark profile.

| Information object | Particle/Boltzmann | NLS/WKE | Boltzmann/fluid | MTF profile |
|---|---|---|---|---|
| High-fidelity equations | Particle flow and collision law | Nonlinear wave equation | Kinetic equation | Selected kinetic/gyrokinetic model |
| Reduced equations | Boltzmann equation | Wave kinetic equation | Euler or NSF | Fluid/transport model |
| Ensemble definition | Initial particle law and samples | Random-field law and samples | Kinetic initial/boundary family | Drive, boundary, and uncertainty ensemble |
| One-point state | One-particle marginal | Spectrum/mode occupations | Hydrodynamic moments | Density, temperature, flow, magnetic state |
| Higher connected statistics | Particle cumulants | Spectral cumulants | Non-equilibrium moments/cumulants | Nonlocal flux, stress, or learned latent statistics |
| History information | Collision/recollision summaries | Resonant interaction summaries | Relaxation history | Compression, drive, and transport history |
| Classical limit | Boltzmann collision operator | WKE collision integral | Euler/NSF constitutive law | Braginskii/local transport |
| Correction target | Hierarchy residual | Spectral-transfer residual | Constitutive residual | Nonlocal heat-flux correction |
| Asymptotic coordinates | Diluteness and kinetic time | Weak nonlinearity and scale separation | Knudsen number | Collisionality, magnetization, gradient scale |

## Model-family ledger

Use "full," "partial," "derived," or "none" in experiment manifests rather
than leaving cells implicit.

| Model | Mathematical target | Equations | Paired fields | Ensembles/cumulants | Histories | Direct closure target | Structural prior | Actions | Train-time solver | Inference-time solver |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Numerical baseline | Discrete solution | Full | No | No | No | Analytic/classical | Discretization | Optional | Yes | Yes |
| Classical Markov closure | Constitutive operator | Reduced | No | Optional diagnostics | No | Yes | Analytic physics | Optional | Calibration only | Yes |
| Explicit cumulant closure | Augmented hierarchy | Reduced/hierarchy | Often | Required | Optional | Yes | Truncation/realizability | Optional | Usually | Yes |
| Finite-memory closure | Memory kernel/augmented state | Reduced/projected | Often | Often | Required | Direct/indirect | Causality/stability | Optional | Usually | Yes |
| PINN | One solution field | Full/partial | Optional sparse | Optional | Optional | Usually no | Trial function/loss | Optional | Residual evaluation | No |
| Neural operator | Solution operator | Optional | Required | Optional | Optional | No | Architecture-dependent | Optional | Data generator | No |
| PINO | Solution operator | Full/partial | Usually | Optional | Optional | No | Operator plus residual | Optional | Data/residuals | No |
| Learned closure | Closure functional | Resolved | Optional | Optional to required | Optional | Direct/indirect | Constraints | Optional | Usually | Yes |
| Structured dynamics | Vector field/flow map | Optional | No | Optional | Required trajectories | Optional | Geometric/stability | Optional | No | No/decoder |
| World model | Action-conditioned latent dynamics | Optional | No | Optional | Required trajectories | No | Latent dynamics | Required | No | No/decoder |

## Privileged-information rules

- A model may not receive test-time cumulants, high-fidelity states, or future
  history unless the deployment scenario makes them observable.
- Diagnostics used only to label a regime must be separated from variables
  supplied to the predictor.
- A learned closure and a classical baseline must be compared at matched state
  dimension whenever possible.
- If extra cumulants or memory coordinates are supplied, report their storage,
  estimation, and inference cost.
- Equation-generated data still count as simulator information even when the
  model does not receive the equation explicitly.
- A residual loss counts as equation access and its derivative/evaluation cost
  must be recorded.

## Matched comparisons

Report at least the following comparisons:

- matched high-fidelity simulator calls and ensemble members;
- matched observed scalar values and time windows;
- matched cumulant order, projection rank, and history length;
- matched training wall time or accelerator hours;
- matched state dimension and parameter count where scientifically relevant;
- matched uncertainty in the closure targets;
- matched inference accuracy target and resulting total cost;
- an unrestricted best-effort comparison, labeled separately.

## Required manifest fields

Each experiment manifest must record:

- benchmark/profile and scale-transition coordinates;
- train, validation, test, breakdown, and transfer split identifiers;
- equations and operators available at train and inference time;
- ensemble membership and estimator definitions;
- cumulant order, basis/projection rank, and history horizon;
- direct labels and derived labels;
- structural constraints and how they are verified;
- reference-solver calls, compute, precision, and hardware;
- uncertainty contributions from numerical, sampling, estimation, model, and
  rollout error.
