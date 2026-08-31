# Classical Many-Body Machine Learning Survey Plan

## Objective

Add a substantial, self-contained section to
`references/closure_pinns_operators_world_models.tex` surveying machine
learning for classical many-body systems. The section will begin from the
three supplied papers by Lu, Maggioni, and Tang; Maggioni, Miller, Qiu, and
Zhong; and Yu, Abdelaleem, Nemenman, and Burton. It will connect interaction
law inference and particle-level learning to the report's central closure
question without conflating force recovery, learned simulation, and reduced
closure.

## Scope boundary

Included systems are classical interacting particles or agents: stochastic
particle systems, classical molecular and coarse-grained dynamics, granular
and active matter, collective motion, point particles on manifolds, and dusty
plasmas. Quantum many-body learning, wavefunction or density-matrix models,
quantum Monte Carlo, electronic-structure prediction, and machine-learned
Born-Oppenheimer potentials are outside scope.

## Section architecture

1. Define the scope and a generic heterogeneous classical particle model.
2. Separate the learned objects: interaction kernel, force decomposition,
   interaction graph, vector field or flow map, coarse closure, and ensemble
   density.
3. Review statistically identifiable nonparametric kernel inference, including
   occupancy measures, coercivity, sample complexity, time-discretization
   error, heterogeneity, and manifold geometry.
4. Use the dusty-plasma study as the central experimental case study in
   physics-tailored neural force decomposition, weak-form training, broken
   symmetries, nonreciprocity, and independent physical validation.
5. Survey graph/message-passing simulators, relational inference, and
   Euclidean-equivariant models.
6. Survey sparse and symbolic discovery, weak-form identification, and
   particle-to-mean-field equation learning.
7. Cover Hamiltonian, Lagrangian, conservative, dissipative, and
   geometry-preserving architectures.
8. Connect classical force matching, coarse-grained free energies,
   Mori-Zwanzig memory, and generative ensemble models to closure.
9. State a validation ladder and failure modes for noisy, partial,
   heterogeneous, variable-particle-number observations.
10. Translate the survey into a concrete dusty-plasma/TEMPEST bake-off ladder
    using the common computational evaluation harness.

## Planned report changes

- Insert the new section after the rigorous scale-limit benchmark discussion
  and before the general neural approximation section.
- Add two comparison tables and two boxed distinctions.
- Extend the abstract to name classical many-body learning and the dusty-plasma
  application profile.
- Add verified bibliography entries for the three supplied papers and a
  focused set of primary sources spanning interaction inference, graph
  simulators, equivariance, equation discovery, structure preservation,
  coarse-graining, memory, and generative ensembles.

## Verification

Compile with `latexmk -pdf`, check that all citations resolve, inspect the log
for overfull boxes and undefined references, render representative pages from
the inserted section, and visually inspect the resulting PDF.
