# Primary-source literature map

Search checked: 2026-08-31. This map distinguishes work that directly supplies
the mathematical objects from work that supplies a reusable numerical
component. It does not treat a generic Boltzmann or NLS solver as an
implementation of the history-bearing cumulant program.

## 1. Direct mathematical foundation

- Deng, Hani, and Ma, [Long time derivation of the Boltzmann equation from hard
  sphere dynamics](https://arxiv.org/abs/2408.07818). The long-time particle to
  kinetic result; cumulant ansatz, partial time expansion, collision-history
  molecules, and cutting algorithm.
- Deng, Hani, and Ma, [Hilbert's sixth problem: derivation of fluid equations
  via Boltzmann's kinetic theory](https://arxiv.org/abs/2503.01800). Connects
  hard-sphere dynamics through Boltzmann to compressible Euler and
  incompressible Navier--Stokes--Fourier on the torus.
- Deng and Hani, [Long time justification of wave turbulence
  theory](https://arxiv.org/abs/2311.10082). Long-time NLS to WKE result using
  cumulants, partial expansions, and canonical layered gardens.
- Deng and Hani, [Propagation of chaos and higher order statistics in wave
  kinetic theory](https://arxiv.org/abs/2110.04565). Supplies the higher-moment,
  hierarchy, and non-Gaussian statistical context needed for computational
  estimators.
- Hani's publication page links two especially useful expository documents:
  [notes on the strategy and proof](https://sites.lsa.umich.edu/zhani/wp-content/uploads/sites/1199/2025/04/Notes_Boltzmann.pdf)
  and [notes on the cutting
  algorithm](https://sites.lsa.umich.edu/zhani/wp-content/uploads/sites/1199/2025/04/Toy_model_algorithm.pdf).

## 2. Closest particle-side ingredients

### Collision histories and correlations

Simonella, [Evolution of correlation functions in hard-sphere
dynamics](https://arxiv.org/abs/1205.2789), derives correlation-function series
and a graphical collision-history language. It is a conceptual predecessor,
not a numerical implementation.

Bodineau, Gallagher, Saint-Raymond, and Simonella develop hard-sphere
fluctuation and cluster-expansion theory, including [statistical dynamics and
large deviations](https://doi.org/10.4007/annals.2023.198.3.3) and [long-time
derivation of the fluctuating Boltzmann
equation](https://doi.org/10.1214/23-AOP1656). These works motivate fluctuation
targets and uncertainty estimates, but do not supply the proposed finite-scale
history-aware closure code.

### Microscopic simulator

Smallenburg, [Efficient event-driven simulations of hard
spheres](https://arxiv.org/abs/2201.01100), supplies a lightweight, benchmarked
event-driven method. The accompanying [public EDMD
repository](https://github.com/FSmallenburg/EDMD) is a plausible adapter target.
It logs physical hard-sphere evolution, not Hani's abstract cut molecules.

Visco, van Wijland, and Trizac, [Collisional statistics of the hard-sphere
gas](https://arxiv.org/abs/0803.1291), show that collision-count statistics are
not naively Poisson even in the dilute regime and compare theory with molecular
dynamics and DSMC. This is strong evidence that collision histories contain
testable structure beyond one-particle marginals.

### Kinetic and fluid baselines

Direct Simulation Monte Carlo and deterministic spectral methods solve the
already-closed Boltzmann equation. They are essential baselines but cannot by
themselves test propagation of chaos or recollision corrections.

Filbet and Jin, [A class of asymptotic-preserving schemes for kinetic equations
and related problems with stiff sources](https://arxiv.org/abs/0905.1378), give
a practical route across Boltzmann and fluid scales. Their BGK penalization
captures the Euler limit without resolving the collision scale and can recover
Navier--Stokes behavior when the relevant transport scales are resolved.

## 3. Closest wave-side ingredients

Hrabski and Pan, [Verification of wave turbulence theory in the kinetic
limit](https://arxiv.org/abs/2311.10846), directly compare microscopic wave
simulations and a WKE as nonlinearity weakens and the domain grows. Their
one-dimensional Majda--McLaughlin--Tabak model is not the `d>=3` cubic NLS in
Hani's theorem, but their scaling-sweep logic is exactly the kind of numerical
validation the proposed project needs.

Qi, Shen, and Wang, [A fast Fourier spectral method for the wave kinetic
equation](https://arxiv.org/abs/2503.12805), reformulate the four-wave collision
operator as a spherical integral and expose an FFT-accelerated double
convolution. This is the strongest current candidate for the reduced WKE side
of the experiment.

Chibbaro, Dematteis, and Rondoni, [4-wave dynamics in kinetic wave
turbulence](https://arxiv.org/abs/1611.08030), derive multimode PDF and
hierarchy descriptions designed to retain higher statistics and intermittency.
This is adjacent to, and potentially compatible with, the proposed cumulant
diagnostics.

The newer formal work of Escobedo and Velazquez, [On the onset of correlations
in wave turbulence close to
singularities](https://arxiv.org/abs/2605.02540), argues that a cumulant
hierarchy becomes necessary near WKE blow-up. It identifies a scientifically
important closure-failure regime for later testing; it is not yet a validated
numerical algorithm.

## 4. What appears not to exist yet

The search found no primary-source software or numerical paper that does all of
the following:

1. simulates the microscopic hard-sphere or cubic-NLS ensemble;
2. estimates the connected cumulants used in the long-time induction;
3. stores a time-oriented compressed collision-history molecule or layered
   garden state;
4. predicts the finite-scale kinetic closure defect; and
5. embeds that prediction conservatively in a long-time reduced rollout.

That absence should be described as a search finding, not a proof of
nonexistence. Before submission, repeat the search in MathSciNet, Web of
Science, zbMATH, Google Scholar citation graphs, and by contacting Hani, Deng,
Ma, Pan, and the WKE numerical authors.

## 5. Reuse versus novelty

| Component | Reuse | Proposed novelty |
|---|---|---|
| hard-sphere evolution | public EDMD or another verified event-driven solver | ancestry/molecule logging adapter and scaling protocol |
| Boltzmann evolution | DSMC or conservative spectral solver | weak microscopic-to-Boltzmann defect estimator |
| NLS evolution | dealiased pseudospectral ensemble solver | layer-aware cumulant and resonant-history instrumentation |
| WKE evolution | fast Fourier spectral solver | synchronized NLS/WKE defect data and history-conditioned correction |
| kinetic-to-fluid | asymptotic-preserving micro--macro solver | theorem-aligned remainder/validity score |
| statistics | standard connected-cumulant estimators | finite-`N` weak estimators tied to graph histories and closure error |

## 6. Recommended reading order for implementation

1. Hani's strategy notes: KF1--KF5 and the physical/abstract molecule warning.
2. Hani's toy-model algorithm notes: implement only the simplified graph
   mechanics as a verification exercise.
3. The introductions and setup of the three main papers.
4. Deng--Hani higher-order wave statistics.
5. Hrabski--Pan for experimental scaling design.
6. Qi--Shen--Wang for the WKE baseline.
7. Smallenburg EDMD plus Simonella's collision histories.
8. Filbet--Jin for the kinetic-to-fluid solver architecture.

