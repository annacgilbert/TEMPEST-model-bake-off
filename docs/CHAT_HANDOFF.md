# Conversation Handoff

## Origin

This project grew from the ChatGPT conversation “Closure models in fluid
dynamics.” The discussion developed a unified numerical-approximation view of
closure models, PINNs, neural operators, structured learned dynamics, and world
models.

## Conceptual thread

The organizing question is not merely whether a method uses neural networks or
physics, but what mathematical object it approximates:

- a single PDE solution;
- a parameter-to-solution or function-to-function operator;
- a constitutive or unresolved closure term;
- a reduced vector field or flow map;
- an invariant or slow manifold;
- a memory-bearing closure; or
- an action-conditioned latent simulator.

The earlier discussion emphasized that these methods consume different kinds
of information. A PINN may use governing equations and sparse observations for
one instance; a supervised neural operator needs a population of input-output
solution pairs; a PINO mixes operator data with equation residuals; a learned
closure needs closure targets or indirect rollout supervision; and a world
model needs trajectories with actions or interventions.

## Scientific motivation

The TEMPEST proposal motivates a hierarchy spanning particle, kinetic,
hydrodynamic, and turbulent descriptions. Its themes include closure,
structure-preserving learning, surrogate dynamics, slow manifolds,
Mori--Zwanzig memory, and multiscale benchmark data. The bake-off should use
one tractable setting that exposes several of these ideas without pretending
that fundamentally different methods have identical objectives.

## Mathematical-program turn

Three rigorous scale-limit papers motivated a more mathematical version of the
bake-off: hard-particle dynamics to Boltzmann, hard particles through kinetic
to hydrodynamic limits, and nonlinear Schrodinger dynamics to the wave kinetic
equation. The project does not treat the proofs as ready-made engineering
closures. It translates their organizing variables into numerical questions:

- do projected connected correlations detect reduced-model failure early;
- can a low-order or low-rank cumulant state explain the closure defect;
- do time-layered interaction summaries justify a finite-memory model; and
- do those diagnostic principles transfer to a TEMPEST application?

The selected architecture has two layers. Canonical benchmarks verify these
ideas on particle-to-Boltzmann, NLS-to-WKE, and Boltzmann-to-fluid transitions.
TEMPEST application profiles then test whether the diagnostics and closure
design rules remain useful in application physics. Dusty plasma supplies the
particle-resolved many-body closure ladder. Core-collapse supernovae supply
the second science application: unresolved 3D shock-turbulence effects must be
represented self-consistently in a reduced 1D carrier.

## Repository strategy

The local Git repository is the durable source of truth. The raw conversation
is context, while binding assumptions, specifications, configurations, and
results belong in version-controlled files. Large generated data and model
checkpoints stay outside Git, with manifests committed here.

## Inputs still needed

- Scientific owners and reference solvers for the canonical, dusty-plasma,
  and supernova pilots.
- A decision on the first supernova 3D-to-1D closure object, projection, and
  application-facing metric.
- Feasible ensemble size, cumulant basis/order, and history horizon.
- Available compute, wall-time, storage, and experimental-data constraints.

The TEMPEST proposal PDF and the prior LaTeX chapter bundle were added to
`references/` on 2026-08-08.

The active program documents are `mathematical_closure_program.md`,
`first_concrete_deliverables.md`, `benchmark_specification.md`,
`information_budgets.md`, `evaluation_protocol.md`, and the revised
`benchmark_options_memo.md` in this directory.
