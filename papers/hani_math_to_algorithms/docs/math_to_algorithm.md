# From Hani's analysis to a computational framework

## 1. What the theorems actually close

The papers do not introduce an empirical constitutive formula. They prove that
an enormous reversible system has an effectively closed, irreversible reduced
description in a scaling limit.

For hard spheres, the retained object is a one-particle density. If
`f_s(t,z_1,...,z_s)` is an `s`-particle correlation function, the basic closure
is factorization:

\[
f_s \approx f_1^{\otimes s}.
\]

The connected remainder is represented by cumulants. In the authors'
expository notation,

\[
f_s(\ell\tau)
= \sum_{H\subseteq[s]} (f^A)^{\otimes([s]\setminus H)}E_H
  + \mathrm{Err}.
\]

Here `f^A` is close to the Boltzmann solution and `E_H` records the departure
from independence. For weakly nonlinear waves, the retained object is the
spectrum

\[
n_k(t)=\mathbb E|\widehat u_k(t)|^2,
\]

and connected Fourier-mode cumulants of order four and higher record departure
from independent Gaussian modes.

The hydrodynamic step closes still further: the Boltzmann density is projected
onto mass, momentum, and energy, while the non-Maxwellian remainder carries
stress, heat flux, and other kinetic information.

## 2. The five proof mechanisms and their computational translations

The hard-sphere expository notes organize the proof around five key formulas.
They give a clean blueprint for the computation, but not a ready-made solver.

| Proof mechanism | Mathematical role | Computational translation |
|---|---|---|
| KF1: factorized part plus cumulants | separates retained density from connected correlations | estimate a retained state and projected connected cumulants from ensembles |
| KF2: cumulant bounded by a sum over molecules | represents connected correlations by collision histories | log finite-window interaction histories and attach them to cumulant samples |
| KF3: count molecules by circuit rank | controls combinatorial proliferation | compute graph size, component count, cycle rank, recollision, depth, and layer statistics |
| KF4: cut a molecule and factor its integral bound | chooses an integration/factorization order | use graph partitions for diagnostics, variance reduction, and feature compression; do not modify the physical trajectory |
| KF5: enough good `{33}` pieces relative to bad `{4}` pieces | gains a positive power of the small parameter | test whether proof-inspired motif scores predict empirical closure defect and uncertainty |

Three warnings are essential.

1. A logged physical collision graph corresponds to a molecule only before
   abstract cutting. After a cut, the proof object need not represent a
   physically realizable trajectory.
2. The proof's molecule integral is a bound on a family of histories, not an
   empirical frequency by itself.
3. The theorem shows asymptotic smallness. It does not say that its constants,
   truncations, or elementary-molecule estimates are numerically sharp at an
   affordable finite scale.

## 3. The proposed layered closure state

At layer time `t_l = l Delta`, define

\[
S_l = (y_l, c_l, h_l, d_l, \sigma_l).
\]

- `y_l`: retained density, spectrum, or fluid moments;
- `c_l`: low-order projected connected cumulants;
- `h_l`: time-oriented interaction-history sketch;
- `d_l`: measured one-layer closure defect; and
- `sigma_l`: estimator uncertainty and effective sample size.

The baseline solver advances the known reduced equation,

\[
y_{l+1}^{(0)}=\Phi_{\rm base}^{\Delta}(y_l).
\]

A correction model then predicts either a defect or a validity score:

\[
(\widehat d_{l+1},\widehat q_{l+1})
=G_\theta(y_l,c_l,h_l;\mu),
\qquad
y_{l+1}=y_{l+1}^{(0)}+\mathcal P\widehat d_{l+1}.
\]

`P` projects the correction so that collision invariants are preserved. The
architecture can be analytic, regression based, graph based, or neural; the
scientific object being tested is the augmented state, not a particular model
brand.

## 4. Algorithm A: hard spheres to Boltzmann

### 4.1 Data generator

Use event-driven molecular dynamics in a periodic two- or three-dimensional
box. Sweep particle diameter `epsilon` and number `N` with

\[
N\epsilon^{d-1}=\alpha
\]

approximately fixed. Sample a grand-canonical-like or carefully controlled
finite-`N` ensemble from a prescribed one-particle density. Log every collision
as

```text
(event_id, time, particle_i, particle_j, x, v_i^-, v_j^-, v_i^+, v_j^+)
```

and assign it to a fixed time layer.

### 4.2 Retained density and weak cumulants

Direct density estimation in `2d*s` dimensions is wasteful. Select test
functions `phi_a(z)` and estimate weak marginals. For example,

\[
\widehat m_a
=\frac1N\sum_i\phi_a(z_i),
\]

\[
\widehat C_{ab}^{(2)}
=\frac{1}{N(N-1)}\sum_{i\ne j}\phi_a(z_i)\phi_b(z_j)
-\widehat m_a\widehat m_b,
\]

with ensemble averaging and finite-`N` bias correction. Third and higher
connected terms are formed by the usual partition/Mobius formula. Basis
families should include collision invariants, low Hermite modes in velocity,
and local spatial windows.

### 4.3 History graph

For each observation window, create an event multigraph:

- vertices are collision events;
- two vertices are joined when the same particle participates in consecutive
  events;
- edges retain particle identity and elapsed time;
- vertices retain time layer and collision geometry.

For tagged particles, take the backward ancestral subgraph. Compute exact
features for small graphs and sketches for large ones:

- number of events and particles;
- connected components and maximum component size;
- circuit rank `|E|-|V|+components`;
- repeated-pair recollisions;
- maximum ancestry depth and temporal span;
- cross-layer edges and long-bond counts;
- event-graph degree and adjacent-degree motif counts.

These are computable proxies. They must not be labeled as exact proof
`{3}`, `{4}`, or `{33}` counts unless the abstract cutting construction has
actually been implemented and verified.

### 4.4 Closure defect

For weak test function `psi(x,v)`, estimate

\[
R_\psi
= \langle f_1,\partial_t\psi+v\cdot\nabla_x\psi\rangle
-\alpha\langle Q(f_1,f_1),\psi\rangle.
\]

This is the scalar target for the first experiments. It avoids differentiating
a noisy density and asks exactly whether the one-particle state obeys the
Boltzmann closure.

### 4.5 Layer update

```text
for each ensemble member:
    evolve exact hard-sphere dynamics for one layer
    log collisions and update the history graph
at the layer boundary:
    estimate f1 in a weak basis
    estimate connected cumulants with confidence intervals
    compute history features
    estimate weak Boltzmann residuals
fit or evaluate residual/validity model using only past information
advance the Boltzmann baseline one layer and add a conservative correction
```

## 5. Algorithm B: nonlinear waves to wave kinetics

The microscopic model is cubic NLS on a large torus with weak nonlinearity
`alpha=L^{-gamma}` and kinetic time `T_kin=1/(2 alpha^2)`. Random Fourier
coefficients are drawn with variance `phi_in(k)`. The reduced state is the wave
action spectrum and the baseline is the four-wave kinetic equation.

### 5.1 Generator and estimators

- Solve cubic NLS with a dealiased split-step or exponential integrator for a
  large ensemble.
- Record `n_k=E|u_hat(k)|^2`.
- Estimate connected fourth- and sixth-order mode cumulants only on momentum-
  compatible tuples and on stratified samples near the resonant manifold.
- Record near-resonant quartets during each time layer as a temporal
  hypergraph. Weight a quartet by its oscillatory phase mismatch and nonlinear
  contribution.
- Compare the observed spectral increment with the four-wave kinetic solver to
  define a layer defect.

### 5.2 Garden-inspired compression

Full canonical layered gardens are too large to enumerate in production.
Start with features that preserve their decisive structure:

- layer labels and time orientation;
- tree depth and branching histogram;
- pairings of terminal modes;
- resonance mismatch distribution;
- irreducible connected-component counts;
- cancellations between signed contributions; and
- fourth/sixth cumulant norms in localized mode blocks.

Only if these features predict defect should we invest in exact low-order
garden enumeration.

### 5.3 Why this is the recommended first track

The spectrum and its cumulants are natural ensemble statistics, NLS is easy to
solve spectrally, and an efficient four-wave kinetic solver now exists. The
wave track therefore tests the central history hypothesis without first solving
the difficult high-dimensional particle density-estimation problem.

## 6. Algorithm C: Boltzmann to fluid

Write a micro--macro decomposition

\[
f=M[\rho,u,T]+g,\qquad
\int (1,v,|v|^2)g\,dv=0.
\]

Use an asymptotic-preserving Boltzmann solver. At each layer record:

- norm and spectral content of `g`;
- stress and heat flux carried by `g`;
- local Knudsen and Mach numbers;
- entropy production and distance to the local Maxwellian;
- Euler or Navier--Stokes--Fourier residuals; and
- disagreement between kinetic and fluid advances.

Here the computational analogue of the theorem is primarily a certified model
switch or correction, not a collision-history graph. This track connects the
paper to multiscale simulation but should follow the wave and particle pilots.

## 7. The decisive arrow-of-time experiment

The papers show why a norm bound on cumulants alone cannot propagate the
irreversible closure: the microscopic flow is reversible, while Boltzmann and
WKE are not. The missing information is forward interaction structure.

At a layer boundary, create paired continuations:

1. continue the ensemble forward;
2. reverse velocities for hard spheres, or complex-conjugate/reverse the NLS
   flow as appropriate, and evolve the paired system;
3. match the retained state and scalar cumulant norms as closely as possible;
4. compare future closure defects.

Test three predictors:

- retained state only;
- retained state plus unordered cumulant magnitudes; and
- retained state plus signed, time-oriented history features.

The third must improve defect prediction and calibration on held-out paired
data for the central computational thesis to survive.

## 8. What would count as a genuine algorithmic contribution

The paper should claim success only if it supplies at least one of the
following:

1. a convergent and variance-controlled estimator for proof-relevant projected
   cumulants;
2. a scalable temporal graph/hypergraph representation whose features predict
   closure error across the scaling sweep;
3. a stable, conservative, history-aware correction that improves long-time
   rollout over the uncorrected kinetic equation; or
4. a certified validity indicator that reliably detects when the classical
   closure is already sufficient and when it is not.

Merely drawing molecules, fitting spectra in distribution, or replacing the
entire kinetic solver with a black-box surrogate would not realize the
mathematical program.

