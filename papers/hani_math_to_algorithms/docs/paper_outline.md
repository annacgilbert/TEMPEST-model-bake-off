# Prospective paper outline

## Working title

**From Collision Histories to Computable Closure: Proof-Guided Cumulants and
Temporal Interaction Graphs**

## One-sentence claim

Time-oriented, proof-guided summaries of connected interaction history provide
computable finite-scale diagnostics of kinetic closure error that cannot be
replaced by the retained state or scalar cumulant norms alone.

This is a hypothesis until the experiments satisfy the gates in
`experimental_program.md`.

## Suggested scope

The first paper should make the cubic-NLS to WKE experiment the principal
demonstration and use hard-sphere collision histories as a smaller transfer or
validation study. Attempting all three of particle, wave, and fluid limits at
full scale would obscure the central methodological claim.

## Sections

1. **Introduction.** Closure, irreversibility, and why finite-scale diagnostics
   need interaction history.
2. **Mathematical blueprint.** Factorization, connected cumulants, time
   layering, molecules/gardens, and the norm-only obstruction.
3. **Computational state.** Projected cumulants, temporal graphs/hypergraphs,
   closure defects, uncertainty, and conservative correction.
4. **Wave experiment.** NLS ensemble, WKE solver, scaling sweep, and
   resonant-history instrumentation.
5. **Arrow-of-time and negative controls.** Forward/reverse pairs, shuffling,
   raw moments, and ablations.
6. **Particle transfer study.** EDMD collision histories, weak cumulants, and
   Boltzmann residuals.
7. **Results.** Detectability, calibration, long-time stability, computational
   cost, and failure cases.
8. **Relation to the proofs.** What was transferred, what was approximated, and
   what was deliberately not implemented.
9. **Discussion.** Applicability to TEMPEST closure problems and limits of the
   canonical regimes.

## Figures that would make the paper

1. theorem object to computational object pipeline;
2. a layered garden and a temporal hypergraph sketch of the same information;
3. forward/reverse pair with matched scalar cumulants but different defects;
4. defect prediction versus scaling parameter and model information level;
5. corrected versus baseline long-time rollout;
6. hard-sphere ancestry graph with recollision/circuit-rank annotations.

## Authorship discussion to initiate early

This project depends strongly on interpreting proof structures correctly.
Before the computational claim hardens, discuss scope and potential
collaboration with Zaher Hani and, as appropriate, Yu Deng and Xiao Ma. The
numerical WKE and wave-verification authors are also natural technical contacts.

