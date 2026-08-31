# Design-Meeting Memo: Mathematical Closure with Dusty-Plasma and Supernova Applications

**To:** TEMPEST benchmark design group  
**From:** TEMPEST Model Bake-Off planning team  
**Date:** August 31, 2026

**Subject:** A common closure program for dusty-plasma many-body physics and
core-collapse-supernova turbulence

## Decision requested

Approve the following program architecture:

1. **Track A - canonical mathematical validation:** hard particles to
   Boltzmann, nonlinear waves to wave kinetics, and Boltzmann to fluid.
2. **Track B1 - dusty-plasma many-body closure:** effective interactions,
   particle-to-kinetic reduction, and kinetic-to-moment closure using one
   verified ensemble family.
3. **Track B2 - core-collapse-supernova turbulence:** project 3D
   radiation-hydrodynamic or (M)HD reference simulations into a reduced 1D
   carrier and close the missing turbulent stresses, fluxes, sources, and
   memory.

Authorize a 90-day specification and pilot phase, not a full model sweep. The
immediate decisions are the scientific and numerical owners, the version-0
reference hierarchy for each profile, estimable correlation/history or
turbulence targets, application observables, and the gates that justify moving
from diagnostics to learned closures.

## Bottom line

The foundational question remains:

> What is the smallest observable state - pairwise, contextual, cumulant,
> moment, or memory-bearing - that closes the retained dynamics over the
> required horizon?

Dusty plasma and supernovae test this question in complementary ways.
Dusty-plasma data expose eliminated fields and wake dynamics at the particle
level, making pairwise failure, many-body context, strong correlation, and
finite memory measurable. Core-collapse supernovae expose a different closure
failure: a 1D model discards nonradial 3D turbulence, shock corrugation,
anisotropic Reynolds stress, turbulent transport, intermittent mixing, and
their history.

The common computational/evaluative harness is the foundational layer. It
declares the retained state and closure defect, versions the reference and
projection, invokes every analytic, learned, or hybrid candidate through the
same interface, embeds closures in the same carrier, and reports matched
accuracy, physical validity, reliability, transfer, and cost scorecards.

## Why supernovae fit the TEMPEST program

The TEMPEST proposal identifies under-resolved turbulence in multidimensional
core-collapse-supernova simulations and proposes DNS, implicit LES, and LES of
supernova shock-turbulence interactions. It also explicitly proposes
augmenting a 1D supernova model with volume-averaged 3D turbulence transport
effects through a self-consistent ML closure.

That gives the bake-off a concrete reduction:

\[
C_{\mathrm{SN}}^\star[X]
=\langle F_{3\mathrm D}(X)\rangle_\Omega
-F_{1\mathrm D}(\langle X\rangle_\Omega).
\]

The target is not a generic supernova surrogate. It is a declared
decomposition of this defect into Reynolds stress or turbulent pressure,
turbulent energy/enthalpy flux, production, dissipation, mixing, and optional
memory terms that can be embedded in a 1D carrier.

The profile is scientifically demanding in exactly the right way. Published
1D turbulence models such as STIR demonstrate the value of importing
multidimensional turbulence into spherical models, while critical analyses
show that apparent gains can be invalid if buoyant production and potential
energy are not coupled conservatively. Energy accounting is therefore a
benchmark requirement, not an optional metric.

## Proposed supernova profile

### High-fidelity and reduced models

- **High fidelity:** 3D core-collapse-supernova radiation hydrodynamics or
  (M)HD at multiple resolutions or filter widths, including declared neutrino,
  gravity, equation-of-state, and progenitor assumptions.
- **Projection:** angle or volume average with explicit Favre/Reynolds
  convention, radial bins, shock alignment, filters, and time windows.
- **Reduced carrier:** a scientifically accepted 1D supernova model with the
  minimum thermodynamic, composition, gravity, and neutrino state needed by
  the selected science question.

### Nested closure candidates

1. unaugmented 1D carrier;
2. declared local RANS, mixing-length, or STIR-like baseline;
3. explicit turbulent-energy or Reynolds-stress augmentation;
4. structure-preserving learned residual at matched retained state;
5. finite-memory augmentation; and
6. an end-to-end operator surrogate as a labeled control.

PINNs remain one-instance equation-informed solvers. Neural operators and
PINOs target families of progenitor, forcing, and closure inputs. Learned
closures must be embedded in the 1D carrier. A world model enters only if the
benchmark supplies a genuine sequential intervention; a fixed progenitor or
heating parameter does not by itself create an action-conditioned task.

### Required observables and structure

- mean shock-radius history;
- shock revival or runaway classification and timing;
- turbulent kinetic energy, Reynolds stress, and turbulent support;
- total-energy and lepton-number accounting as represented by the carrier;
- Reynolds-stress realizability, positivity, and stable shock capturing;
- explosion energy and at least one nucleosynthesis-sensitive thermodynamic
  history statistic;
- recovery of the declared zero-turbulence or local-baseline limit; and
- stable-run fraction and total cost.

The version-0 subset of these observables must be chosen with the supernova
science owners before data generation.

## Dusty plasma remains a full closure application

The dusty-plasma profile is retained intact. A controlled reference family
varies density/coupling, particle number, screening, charge and mass
heterogeneity, external forcing and forcing history, and a wake or field
relaxation time. It nests an analytic pair law, learned pair kernel,
instantaneous equivariant graph model, finite-memory graph or auxiliary-state
model, and black-box control.

The first experiment locates where pairwise closure fails, where many-particle
context becomes necessary, and where memory earns its cost. Projected
cumulants and interaction-history complexity are tested as early warnings.
The same verified ensembles then support particle-to-kinetic and
kinetic-to-moment closures, so interaction learning feeds the next reductions
rather than remaining an isolated trajectory exercise.

## What the Hani papers add

The three motivating papers provide canonical scale transitions in which the
hierarchy, small parameters, discarded correlations, and expected reduced
limits are unusually explicit:

- hard-particle dynamics to Boltzmann;
- hard particles through kinetic to hydrodynamic limits; and
- nonlinear Schrodinger dynamics to the wave kinetic equation.

They do not provide dusty-plasma or supernova equations. They motivate four
falsifiable computational hypotheses:

1. projected connected correlations or fluctuation statistics detect closure
   failure before large resolved-state error;
2. the important closure defect is compressible;
3. finite history improves long rollout when a Markov state is insufficient;
4. diagnostic and state-selection principles survive physics-specific
   refitting across the application profiles.

## Common evaluation harness

The harness separates science from scaffolding. Each method implements one
interface; the shared system handles reference manifests, data projection,
integration, scoring, uncertainty, failure retention, and report generation.
Direct rankings are restricted to candidates approximating the same object
with matched information and compute. Cross-family conclusions use separate
scorecards rather than a universal leaderboard.

Every application claim must pass both tests:

1. **A priori:** predict a held-out closure target with uncertainty smaller
   than the claimed effect.
2. **A posteriori:** improve the retained solver without instability,
   conservation failure, or unavailable inference-time information.

For supernovae, projection and filter uncertainty are reported separately from
closure-model error. For dusty plasma, ensemble/cumulant and effective-force
identifiability uncertainty are reported separately from rollout error.

## First 90-day deliverables

1. mathematical-to-computational object and estimator specification;
2. minimal hard-particle/Boltzmann and NLS/WKE canonical pilots;
3. common cumulant/history and closure-residual data schema;
4. factorization and closure-failure diagnostic notebook;
5. dusty-plasma activation packet and small pair/context/memory sweep;
6. supernova 3D-to-1D translation specification;
7. a small verified 3D projection data slice plus matching 1D carrier case;
8. predeclared numerical, estimator, physical, embedded-rollout, and resource
   gates.

Weeks 1-3 freeze the objects, projections, owners, and observables. Weeks 4-10
verify minimal reference generators and estimators. Weeks 11-13 run the first
diagnostic and embedded-closure smoke tests, then hold a continue/narrow/stop
gate review. Broad PINN/operator/world-model sweeps begin only after the
reference and estimator gates pass.

## Questions the design meeting must resolve

1. Who owns the canonical, dusty-plasma, 3D supernova, and 1D supernova
   reference solvers?
2. Which 3D simulations can be shared, and what resolution/filter hierarchy is
   adequate for a first projection study?
3. What angle/volume and Favre/Reynolds convention defines the 1D closure
   defect across the moving shock?
4. Which turbulent term is the first learned target: Reynolds stress,
   turbulent energy/enthalpy flux, production/dissipation, mixing, or a staged
   combination?
5. Which shock, explosion, and nucleosynthesis-sensitive observables define
   improvement, with what uncertainty?
6. Which dusty-plasma reference and independent quantities distinguish a
   plausible force fit from a correct eliminated-environment closure?
7. Which cumulants, histories, or fluctuation coordinates are estimable within
   the compute budget?
8. What evidence triggers continue, revise, merge, or stop decisions?

## Recommended meeting outcome

Approve the program title and scope:

> **TEMPEST Mathematical Closure and AI/ML Benchmark Framework**
>
> **Application 1: Dusty-Plasma Many-Body Closure**
>
> **Application 2: Core-Collapse-Supernova Turbulence Closure**

Assign owners for the canonical references, dusty-plasma physics, the 3D
supernova ensemble, the 1D carrier, the common statistical schema, and the
evaluation harness. Approve the 90-day deliverables and week-13 gate review.
Defer broad model ranking until the reference hierarchy, projections,
information budgets, and application observables are fixed.

*Basis: the TEMPEST Full Proposal; Couch, Warren, and O'Connor,
[STIR](https://arxiv.org/abs/1902.01340); Müller,
[critical assessment of 1D supernova turbulence models](https://arxiv.org/abs/1902.04270);
Abdikamalov et al.,
[shock-turbulence interaction](https://arxiv.org/abs/1605.09015); and the three
mathematical scale-limit papers listed in the project references.*
