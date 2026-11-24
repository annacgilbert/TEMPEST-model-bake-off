# References

Place authoritative project sources here.

## Imported background chapter

Imported on 2026-08-08 from the user-supplied
`closure_world_models_latex_bundle.zip`:

- `closure_pinns_operators_world_models.tex`
- `closure_pinns_operators_world_models.pdf`
- `closure_pinns_operators_world_models.bib`
- `README.txt` (the bundle's original instructions)
- `closure_world_models_latex_bundle.zip` (the preserved source archive)

### Project augmentation: Hani canonical benchmarks

On 2026-08-11, the working LaTeX source, bibliography, and compiled PDF were
expanded with a dedicated section on Zaher Hani and collaborators. The new
section summarizes the hard-particle-to-Boltzmann, Boltzmann-to-fluid, and
nonlinear-wave-to-wave-kinetic results; explains why these controlled regimes
form the canonical validation layer of the computational evaluation harness;
and states explicitly which diagnostic logic transfers to TEMPEST and which
physical equations and theorem assumptions do not. The application comparison
now identifies dusty plasma and core-collapse-supernova turbulence as the two
TEMPEST profiles. The preserved source archive listed above was not modified.

## Still expected

No expected initial references are currently missing.

## TEMPEST proposal

`TEMPEST_proposal.pdf` was imported on 2026-08-08 from the user-supplied
Overleaf project export at `TEMPEST_Full_Proposal/main.pdf`. PDF metadata
identifies it as *TEMPEST: NSF STC Full Proposal* by Michael Murillo. The
verified file contains 31 letter-size pages, ending with the bibliography.

## External mathematical foundations

- Deng, Hani, and Ma, [Long time derivation of the Boltzmann equation from hard
  sphere dynamics](https://arxiv.org/abs/2408.07818), v3.
- Deng, Hani, and Ma, [Hilbert's sixth problem: derivation of fluid equations
  via Boltzmann's kinetic theory](https://arxiv.org/abs/2503.01800), v1.
- Deng and Hani, [Long time justification of wave turbulence
  theory](https://arxiv.org/abs/2311.10082), v2.

Versions were checked on 2026-08-08. If local PDFs are later added, record
their retrieval dates and checksums here.

## Supernova closure foundations

- Couch, Warren, and O'Connor,
  [Simulating Turbulence-aided Neutrino-driven Core-collapse Supernova
  Explosions in One Dimension](https://arxiv.org/abs/1902.01340), STIR and
  3D-calibrated turbulence in a 1D carrier.
- Müller,
  [A Critical Assessment of Turbulence Models for 1D Core-Collapse Supernova
  Simulations](https://arxiv.org/abs/1902.04270), emphasizing conservative
  coupling and thermodynamic consistency.
- Abdikamalov et al.,
  [Shock-Turbulence Interaction in Core-Collapse
  Supernovae](https://arxiv.org/abs/1605.09015), a controlled analysis of
  upstream perturbations and post-shock turbulence amplification.

The TEMPEST proposal remains the primary source for the project's proposed 3D
DNS/implicit-LES/LES supernova work and the self-consistent augmentation of a
1D supernova model with volume-averaged 3D turbulence transport effects.

## Downloaded papers

Moved here on 2026-11-09 from the sibling Drive folder `Research/TEMPEST refs/`
(files downloaded April--May 2025). Filenames are unchanged. Publisher PDFs
are local copies and are not committed to the public repository.

| File | Paper | SHA-256 (first 12) |
|---|---|---|
| `2503.01800v1.pdf` | Deng, Hani, and Ma, *Hilbert's sixth problem: derivation of fluid equations via Boltzmann's kinetic theory*, arXiv:2503.01800v1 | `43eb2ba85d1c` |
| `21m1401759.pdf` | Lin, Tian, Livescu, and Anghel, *Data-Driven Learning for the Mori--Zwanzig Formalism: A Generalization of the Koopman Learning Framework*, SIAM J. Appl. Dyn. Syst. 20(4), 2558--2601 (2021) | `62709e5c911b` |
| `22m1506146.pdf` | Lin, Tian, Perez, and Livescu, *Regression-Based Projection for Learning Mori--Zwanzig Operators*, SIAM J. Appl. Dyn. Syst. 22(4), 2890--2926 (2023) | `0f8770b5681e` |
| `attention_for_turbulence.pdf` | Peng, Yuan, et al., *Attention-enhanced neural network models for turbulence simulation*, Phys. Fluids 34, 025111 (2022), doi:10.1063/5.0079302 | `73fe49d9c80b` |
| `generalizability_transformer.pdf` | Drikakis, Kokkinakis, Fung, and Spottswood, *Generalizability of transformer-based deep learning for multidimensional turbulent flow data*, Phys. Fluids 36, 026102 (2024), doi:10.1063/5.0189366 | `aa73f44b747c` |
| `Transformers0512.pdf` | Geshkovski, Letrouit, Polyanskiy, and Rigollet, *A Mathematical Perspective on Transformers* (preprint) | `8669c72f7112` |

## Draft note: tournament benchmark for heat-flux closures

Added to the repository on 2026-11-16. *A Tournament Benchmark for Learned
Nonlocal Heat-Flux Closures* is a six-page draft note for discussion (v0.1).
It proposes Vlasov--Lenard--Bernstein as the ground truth for learned
nonlocal electron heat-flux closures, with non-local electron transport in
ICF/IFE as the target application, and a tournament in which submitted
closures are scored by a shared automated harness. The files carry no author
line; the author is not recorded here.

| File | Modified | SHA-256 (first 12) |
|---|---|---|
| `a_tournament_benchmark_for_learned_nonlocal_heat-flux_closures.md` | 2026-09-02 | `879368d491cb` |
| `a_tournament_benchmark_for_learned_nonlocal_heat-flux_closures.tex` | 2026-11-12 | `6641909bbdb3` |
| `a_tournament_benchmark_for_learned_nonlocal_heat-flux_closures.pdf` | 2026-11-12 | `981dc8624506` |

## Cautionary examples

- Higginbottom, Ercan, Antony, Sanchez Gonzalez, Grazzini Placucci,
  Kassaï Koupaï, and Toshev,
  [ModeCast: One-Shot Prediction of Linear MHD Eigenmodes and Growth Rates in
  Tokamaks](https://arxiv.org/abs/2610.23844), v2 (23 Oct 2026), NeurIPS 2026
  Sim2Science workshop. BibTeX key `higginbottom2026modecast`.

  A supervised surrogate (a roughly 145M-parameter U-Net) trained on about
  46,000 linear JOREK runs. It maps a tokamak equilibrium and toroidal mode
  number to the fastest-growing resistive-MHD eigenmode and its growth rate.
  In the bake-off taxonomy it is family 6 (supervised neural operator on
  solution pairs) used as a black-box control: it replaces the solver and
  supplies no identified correction to an explicit classical operator.

  Why it is cautionary: the surrogate does not avoid a closure, it inherits
  one. Three errors are stacked, and only the last is measured.

  1. Model-form error: whether resistive MHD with collisional closures is the
     right physics in the regime of interest. Not tested; there is no
     higher-fidelity kinetic reference anywhere in the pipeline.
  2. Discretization error: whether JOREK resolved those equations. The paper
     is reported to flag that its 128x128 grid may under-resolve the
     resistive layers, and its reference resistivity-scan slopes (+0.67 kink,
     +0.51 tearing) differ from the scalings it cites (1/3 and 3/5).
  3. Surrogate error: agreement with JOREK. This is what the headline numbers
     report (growth-rate R^2 near 0.97, no missed unstable cases among 1,258
     held-out tests).

  All reported metrics are measured against the same code at the same
  resolution, so a high score on item 3 says nothing about items 1 and 2.
  Use it as the worked example for scientific principle 9 (separate
  discretization, asymptotic-limit, and learned model-form error) and
  engineering principle 10 (keep the classical reduced operator explicit).

  Worth borrowing all the same: geometry-disjoint train/validation/test
  splits, a calibrated classifier that abstains on borderline cases, checks
  against known resistive scalings, and a frozen-trunk, refit-head protocol
  for out-of-distribution transfer.

  Provenance: abstract page and HTML full text (v2) read on 2026-11-24. Only
  the first part of the HTML was read verbatim; the grid-resolution
  limitation and the scan slopes in item 2 come from an extracted summary of
  the remainder and have not been checked against the PDF. No local PDF is
  stored.

## Related work: fusion transport surrogates

- Higginbottom, Antony (Zenithon AI), Z. Li (MIT), and L. Lu (Yale),
  *Physics Informed Function-Space Diffusion for Rapid Gyrokinetic Turbulence
  Modelling*, talk at the IAEA Workshop on Digital Engineering, 10 December
  2025. BibTeX key `higginbottom2025fundiffgk`. Local slides:
  `IAEA_Zenithon_AI.pdf` (20 pages: an 8-slide company introduction followed
  by the 12-slide talk).
- Antony and Higginbottom (Zenithon AI),
  [Development of a Neural Operator-Based Surrogate Model for Accelerated
  Gyrokinetic Transport
  Calculations](https://conferences.iaea.org/event/412/contributions/38155/),
  the abstract submitted to the same workshop. BibTeX key
  `antony2025gksurrogate`.

  Same group as the ModeCast entry above.

  What the slides propose ("TurboTGLF"): TGLF, a quasilinear gyrofluid
  reduced model, maps an equilibrium to a state r (growth rates,
  frequencies, and flux predictions). A function autoencoder maps Fourier
  fields U(k_x, k_y) to a latent code, enforcing Hermitian symmetry and
  spectral constraints. A conditional latent diffusion transformer learns
  p(z | r), so that decoding yields fields and a flux Q "consistent with the
  TGLF state". An ensemble of samples at fixed r is offered as credible
  intervals for transport. Distillation to millisecond inference is listed
  as future work.

  What the slides actually show: no gyrokinetic result. No gyrokinetic code,
  dataset, parameter range, or accuracy figure appears. The only benchmark is
  2D Kolmogorov flow (incompressible Navier-Stokes on a periodic box), where
  the task is to reconstruct the flow from sparse, noisy, downsampled
  observations, described as "simulating ROM conditioning". There the method
  is reported to beat a set of neural-operator baselines in relative L2
  error, and a stream-function decoder gives divergence-free output by
  construction. On the noise-robustness slide the caption's colours appear
  to be swapped relative to the plot legend. Next steps listed: larger
  heterogeneous datasets, ablations over physics constraints, flow matching,
  integration with full-core transport solvers, and distillation.

  How to read it against the bake-off:

  1. In design it is a learned closure with a higher-fidelity reference:
     nonlinear gyrokinetics above TGLF, with the turbulent flux as the
     closure quantity. That is closer to family 8 than ModeCast is.
  2. "Physics informed" here means constraints built into the decoder
     (Hermitian symmetry, divergence-free). No gyrokinetic residual,
     conservation law, or classical-limit recovery is imposed or tested.
  3. Conditioning only on the TGLF state is an identifiability assumption:
     two equilibria with the same TGLF output but different nonlinear
     saturation cannot be told apart. The slides do not test it.
  4. The ensemble spread is a property of the learned conditional density.
     It is not shown to be calibrated against gyrokinetic variability, and
     it does not include model-form or discretization error.
  5. The submitted abstract describes physics-informed neural operators
     trained on delta-f flux-tube gyrokinetic runs; the talk as given
     describes latent diffusion validated on Kolmogorov flow. Treat the
     gyrokinetic claims as a proposal, not a result.

  Provenance: slides saved by the user from
  <https://conferences.iaea.org/event/412/contributions/39509/attachments/21971/37781/IAEA_Zenithon_AI.pdf>
  on 2026-11-24 and read in full (all 20 pages); SHA-256 (first 12)
  `ecd9e4eaa38a`. The PDF is a local copy and is not committed. The abstract
  page returned HTTP 403 and was not read; its description above comes from
  search-index excerpts only.

Do not silently replace or edit source documents. Record provenance, version,
and retrieval date when a reference is added.
