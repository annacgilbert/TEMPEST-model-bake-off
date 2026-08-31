# Bake-Off Pipeline Update Plan

Status: **Approved for documentation update; numerical choices remain open**

## Goal

Turn the bake-off from a flat comparison of model families into a linked
experimental pipeline that tests closure at successive reductions. Preserve
the theorem-faithful canonical validation layer and the dusty-plasma
many-body ladder, then add core-collapse-supernova turbulence as the second
TEMPEST application and the flagship 3D-to-1D transfer test.

## Architecture to preserve

- Track A remains the canonical validation layer: hard particles to Boltzmann,
  nonlinear waves to wave kinetics, and Boltzmann to fluid.
- Track B1 is the dusty-plasma many-body closure ladder.
- Track B2 is core-collapse-supernova turbulence, with 3D
  DNS/implicit-LES/LES references projected into a reduced 1D carrier.
- Production runs for both profiles remain gated on scientific owners,
  reference physics, estimators, and application-facing observables.
- Analytic, learned, and hybrid models continue to use one computational and
  evaluative harness with explicit information and compute budgets.

## Documentation changes

1. Add one canonical end-to-end description of the experimental pipeline.
2. Define four linked stages: interaction discovery, particle-to-kinetic
   reduction, kinetic-to-moment closure, and application transfer.
3. Preserve the dusty-plasma reference family and wake-relaxation experiment
   that separates pairwise, contextual, and memory-dependent closure.
4. Replace any implied single leaderboard with target-specific scorecards plus
   a cross-stage synthesis.
5. Map each AI/ML family to the mathematical object and pipeline stage for which
   it is a fair candidate.
6. Extend information ledgers, splits, failure gates, deliverables, and the
   design-meeting memo to cover the linked pipeline.
7. Specify the supernova projection, turbulent closure defect, reference
   hierarchy, physical constraints, rollout metrics, and failure gates.
8. Update the report scaffold, presentation, and repository entry points to
   point to the canonical pipeline description.

## Validation

- Check internal links and terminology across all edited Markdown files.
- Confirm that binding and open decisions are not conflated.
- Compile the LaTeX report scaffold after its pipeline summary is updated.
- Review the generated report pages for obvious layout failures.
- Inspect the final Git diff and run the inexpensive repository test suite.

## Non-goals for this update

This documentation update does not select reference solvers, fix parameter
ranges, generate data, implement models, authorize full dusty-plasma runs, or
claim that one architecture is uniformly best.
