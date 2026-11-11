# Burton Sprint Plan

Status: draft for review, 2026-11-09. Nothing here is binding until recorded
in `model-bakeoff/docs/DECISIONS.md`.

## Summary

A three-week sprint, six people (the lead plus five) working with AI agents,
built on Yu, Abdelaleem, Nemenman, and Burton, *Physics-tailored machine
learning reveals unexpected physics in dusty plasmas* (PNAS 122(31),
e2505725122, 2025; arXiv:2310.05273).

The sprint goes beyond the paper in three ways:

1. **Automated data access.** An MCP server gives code and agents read-only
   access to Justin Burton's TIFF image stacks.
2. **Tracking benchmark.** Alternative image-processing and tracking methods
   are scored against the lab's TrackPy-based pipeline.
3. **Beyond-pairwise test.** The paper's model assumes pairwise forces. The
   sprint asks whether the data show many-body or history-dependent forces
   that a pairwise model cannot represent. In TEMPEST's terms this is a
   closure test: the pairwise force law is the lowest-order closure of the
   dust dynamics, and the sprint measures its defect.

Deliverable: a working pipeline from TIFFs to trajectories to a
beyond-pairwise verdict, a tracking scorecard, and a short report that
includes failures and inconclusive results.

## What the paper provides

Facts taken from the paper and the lab's public repository.

- **Experiments.** Five runs with 9, 10, 13, 15, and 18 melamine-formaldehyde
  particles (8.0 to 12.8 μm) in argon at 0.75 to 1.20 Pa, levitated about
  4.2 mm above the electrode.
- **Imaging.** A laser sheet scans about 4 mm vertically at 200 Hz,
  synchronized to an 8000 fps camera, giving about 40 images per sweep and a
  3D volume rate of 200 Hz. Stated resolution is 50 μm in x, y and 100 μm in
  z. Camera model, sensor size, image format, and bit depth are not stated.
- **Tracking.** TrackPy v0.6.4, with "special care" for closely spaced
  particles. The 3D reconstruction method is deferred to earlier lab papers
  (Yu and Burton, Phys. Plasmas 2023; Yu, Cho, and Burton, PRE 2022).
- **Model.** Three small TensorFlow networks trained together: a pairwise
  interaction force, an environment force, and a damping coefficient. The
  loss is a weak-form residual, so accelerations are never differentiated
  from noisy positions. Ten-fold cross-validation over contiguous time
  blocks gives test R² of 0.991 to 0.996.
- **Public code and data.** `github.com/wyu54/many-body-force-infer` (Zenodo
  DOI 10.5281/zenodo.15866619) holds `ForceInfer.py`, a demonstration
  notebook, and the five tracked trajectories as CSV files (frame, particle,
  x, y, z, brightness). It has no license file, no tracking code, no raw
  images, and no simulator or simulated trajectories (checked 2026-11-11).

Limits the paper states about itself, which the sprint builds on:

- Forces are restricted to be pairwise, and only horizontal components are
  inferred.
- "Mis-identification or mis-tracking of particles can have a detrimental
  effect."
- Error bars cover model variance only; bias is excluded. A high total R²
  "does not necessarily indicate that each component is fit correctly."
- Non-reciprocity appears at separations below about 0.6 mm, which is the
  regime where tracking closely spaced particles is hardest.

What the paper does not do, from a reading of the article and supporting
information on 2026-11-11:

- It does not test the pairwise assumption. The introduction states that
  forces "are expected to be pairwise to leading order," and the model sums
  pair forces linearly, so a third particle's position never enters and no
  many-body term can be learned.
- Its validation simulation is also pairwise ("a pairwise, non-reciprocal
  repulsive force"), so the method was never checked on a system with
  many-body effects.
- It reports no residual analysis against a third particle or local
  density, and no bound on the size of a many-body contribution. The high
  total R² limits the unexplained force overall, but a many-body effect
  could be absorbed into the environment or pair force.

## Questions for Justin Burton

Sent to Justin by Slack on 2026-11-09, with a link to this plan. He replied
by 2026-11-11; answers are paraphrased below. A follow-up discussion with his
students was proposed for a Wednesday meeting.

1. **The TIFF stack.** Is it the raw camera data behind the five published
   runs, or new experiments? Which runs does it cover, how many frames, what
   bit depth and pixel scale, how large is it in total, and where is it
   hosted?
   - Answer (2026-11-11): the lab can provide either the original data or
     new data it is currently working on. Start with the raw version of the
     published data. New data is also on offer and could come with complete
     metadata.
   - Still open: frame counts, bit depth, pixel scale, total size, hosting,
     and how the data will be transferred.
2. **Tracking code.** Can the lab share its image-tracking and
   3D-reconstruction code? In what language is it, and under what license?
   The public repository does not include it.
   - Answer (2026-11-11): the lab's code has been cleaned up substantially
     since the PNAS submission and Justin will provide an updated version
     directly. A new public release waits on a further paper.
   - Still open: whether the version provided includes the tracking and
     3D-reconstruction code or only force inference; language and license.
   - To ask (added 2026-11-11): can the lab share the molecular-dynamics
     simulation it used to validate the method in the paper, or its output?
     The public repository contains no simulator and no simulated
     trajectories (checked 2026-11-11). Their simulator would make the
     sprint's controls directly comparable to the paper's validation. It
     would not provide image-level ground truth for the tracking benchmark,
     which still needs a forward image model.
3. **Force-inference code.** Is it OK to use and redistribute `ForceInfer.py`
   from `wyu54/many-body-force-infer`? That repository has no license file.
   - Answer (2026-11-11): use the updated version the lab will provide, not
     the public one. It is not yet public, so it must not be redistributed.
     Justin also noted that not all authors of the force-inference work are
     part of TEMPEST, and asked that the sprint pursue questions orthogonal
     to that work.
   - Still open: which questions count as orthogonal. See "Consequences of
     Justin's answers" below.
   - To ask (added 2026-11-11): what does he mean by orthogonal? Possible
     readings to put to him: (a) do not use or extend the lab's
     force-inference code; (b) do not do force inference on this data at
     all; (c) do not duplicate what the lab's next paper covers. Under (a),
     a model-free beyond-pairwise test is fine; under (b) or (c) it may not
     be. Point to raise: the paper assumes pairwise forces in the model and
     in its validation simulation, and does not test for or bound many-body
     effects, so the beyond-pairwise question examines an assumption of the
     published work and does not repeat it.
4. **Metadata.** What acquisition metadata exists for each run: pressure,
   power, particle sizes, laser-sheet phase per frame, and spatial
   calibration?
   - Answer (2026-11-11): pressure, power, and particle sizes are known. The
     laser sheet was calibrated, but its phase was not recorded per frame; it
     is derived from the calibration. The student who took the published data
     has since left, so new data is the route to complete metadata.

### Consequences of Justin's answers

- **Lab code stays out of this public repository.** Anything the lab
  provides goes in `external/`, which is git-ignored apart from its README.
- **Workstream C waits for the lab's version.** The pairwise baseline should
  use the code Justin provides, not the public `ForceInfer.py`.
- **Workstream D needs to be re-scoped with Justin.** As drafted, it extends
  the lab's force-inference model with density, three-body, and memory
  terms. That may be too close to the published force-inference work. To
  settle at the Wednesday meeting: whether beyond-pairwise tests count as
  orthogonal, whether they should avoid the lab's architecture and rely on
  model-free diagnostics (residual structure, three-particle correlations),
  or whether a different question should replace them.
- **Workstreams A and B are unaffected and are clearly orthogonal.** Data
  access and a tracking benchmark do not overlap with force inference.
- **The laser-sheet phase is inferred, not recorded.** The forward image
  model and any 3D reconstruction in workstream B must take the sheet
  position from the calibration, and should treat its uncertainty as a
  source of z error. Ask for the calibration procedure and data.
- **New data is an option for the tracking benchmark**, since it could carry
  full metadata and current lab members can answer questions about it.

If the TIFFs are not available by day 3, workstreams B and C proceed on
synthetic images and the published trajectories, and the report says so.

## Workstreams

### A. Data access (week 1)

Build the MCP server specified in `../mcp/SPEC.md`.

- Day 1 to 2: characterize the stack, fill in the data-description section
  of the spec, and write a manifest with checksums in `../data/manifests/`.
- Day 2 to 5: implement read-only tools for listing runs, reading metadata,
  and fetching frames or sweep volumes by range.
- A plain Python loader with the same interface ships on day 2 so the other
  workstreams are never blocked on the server.

Acceptance: a fresh agent session can list runs, pull one full laser-sheet
sweep, and reproduce its checksum; frames are returned unmodified; missing
frames produce explicit errors.

### B. Image processing and tracking benchmark (weeks 1 to 3)

Compare tracking methods against the lab's TrackPy pipeline.

**Ground truth.** Real images have no known true positions, so the benchmark
needs two references:

- *Synthetic stacks.* Simulated 3D trajectories rendered into image sweeps
  with a forward model of the scanning sheet, particle point-spread function,
  and camera noise, calibrated to the real TIFFs. True positions are known
  exactly.
- *Published trajectories.* If the TIFFs are the raw data for the five
  published runs, each method's output is compared with the lab's CSVs. This
  measures agreement with the lab, not correctness.

**Candidate methods.** The lab's TrackPy configuration as baseline; a
classical alternative (blob detection with sub-pixel Gaussian fitting and a
3D fit across the sweep); a learned detector trained only on synthetic
stacks; and at least one alternative linker (for example, assignment-based
or Kalman-filter linking) to isolate detection errors from identity errors.

**Scorecard.**

| Metric | Why it matters |
|---|---|
| Detection recall and precision | Missed or phantom particles |
| Position error in x, y, z | Compared with the stated 50 and 100 μm resolution |
| Close-pair resolution vs separation | Non-reciprocity lives below 0.6 mm |
| Identity swaps and track fragmentation | The model's particle identifier depends on stable identity |
| Runtime per sweep | Cost |
| Downstream force error | Each tracker's output is fed through the force-inference model on synthetic data with known forces |

The last row is the one that connects tracking quality to the physics claim.

Acceptance: every method is run on the same frozen synthetic test set and,
if available, the same real runs; failures and non-converged runs are
reported in the table.

### C. Pairwise baseline (week 1)

Run the lab's released model on the five released trajectories and confirm
the pipeline works end to end. This is not a full reproduction study; it
establishes the pairwise baseline that workstream D tests against, and
records any numbers that differ from the paper.

Also build the simulator used by B and D: a small molecular-dynamics code for
10 to 20 particles with confinement, Epstein damping, and screened-Coulomb
interactions, with switchable additions:

- a point-charge ion wake (pairwise, non-reciprocal), which is the negative
  control;
- a planted non-pairwise effect, such as particle charge that depends on
  local density or a wake that takes finite time to relax, which is the
  positive control.

### D. Beyond pairwise (weeks 2 to 3)

**Question.** After the best pairwise-plus-environment model is fit, is there
structure left that depends on more than two particles, or on history?

**Closure framing (added 2026-11-11).** This is a closure test in the sense
used across TEMPEST, and can be stated in the bake-off's terms:

- *Retained state:* dust particle positions and velocities.
- *Eliminated information:* ions, electrons, and neutrals.
- *Classical reduced operator:* pairwise effective force plus environment
  force and linear damping, which is the paper's model.
- *Closure defect:* whatever the true force on a dust particle contains
  beyond that, such as many-body terms from overlapping ion clouds and
  memory from finite wake relaxation.

The pairwise assumption is the lowest-order closure, and workstream D
measures its defect. This corresponds to the effective-interaction stage of
the dusty-plasma ladder in `model-bakeoff/`. Two cautions:

- The force-level closure above is distinct from closing the correlation
  hierarchy (pair versus three-particle statistics). Test 3 below addresses
  the second; tests 1 and 2 address the first. Report them separately.
- Any augmented model must recover the pairwise model where it is trusted,
  at low density and large separation.

DRIAD is the natural reference: it resolves the ions, so the closure defect
can be computed directly and not only inferred.

**Tests, in order of cost.**

1. *Residual structure.* Fit the pairwise model, then test whether held-out
   residuals on particle i depend on features the model cannot see: the
   position of a third particle near a pair, local density, or the recent
   relative velocity of a neighbor.
2. *Nested models.* Add one capacity at a time to the lab's architecture:
   a pair force conditioned on local density; an explicit three-body term;
   a short-memory term using lagged neighbor positions. Compare each with
   the pairwise model on held-out time blocks at matched data and matched
   parameter count.
3. *Correlation diagnostics.* Estimate low-order connected correlations of
   the particle configurations, as defined in `hani-to-algorithms/`, to
   check whether three-particle structure exceeds what pair structure
   predicts. This is a diagnostic, not a force measurement.

**Controls.** Every test runs first on simulated data pushed through the
same tracking noise:

- On the strictly pairwise simulation, the tests must report no
  beyond-pairwise effect. This sets the false-positive rate.
- On the planted simulation, the tests must detect the effect at a strength
  comparable to what is plausible physically. This sets the detection
  threshold.

Only then are the tests applied to the experimental trajectories.

**Possible outcomes, all reportable.**

- A beyond-pairwise effect above the detection threshold, with its size and
  the regime where it appears.
- No effect, with an upper bound set by the planted-simulation threshold.
- Inconclusive, because 9 to 18 particles and the available run lengths
  cannot separate many-body effects from the environment force or from
  tracking error. This is a likely outcome and determines what data a
  follow-on experiment would need.

**Known confounders.** The environment force and a density-dependent pair
force can trade off; charge and mass are coupled in the fit; only horizontal
forces are available; particle identity is encoded through mean height.

## Schedule

| Week | A. Data | B. Tracking | C/D. Model and science |
|---|---|---|---|
| 1 | Characterize stack; loader on day 2; MCP server by day 5 | Forward image model; baseline TrackPy run | Run lab code on released data; build simulator with controls |
| 2 | Harden server; manifests; support | Implement alternatives; freeze synthetic test set; first scorecard | Residual tests and nested models on simulation; set thresholds |
| 3 | Documentation | Real-data runs; downstream force error; final scorecard | Apply tests to experimental data; write report |

Checkpoints: end of week 1 (data reachable, baseline runs, simulator
exists); end of week 2 (controls behave as designed, or the science scope is
cut back); day 13 (results frozen; remaining time is writing).

## Staffing

The team is strong in ML, scientific computing, and plasma and statistical
physics, and has no dedicated image-processing or infrastructure specialist.

| Role | People | Notes |
|---|---|---|
| Data access and MCP | 1 | ML or scientific-computing person, leaning heavily on agents |
| Tracking benchmark | 2 | One on the forward image model and ground truth, one on methods |
| Simulator and controls | 1 | Physics background |
| Beyond-pairwise models | 1 | ML background |
| Lead | 1 | Scope, contact with the Burton lab, physics judgment, report |

The two physics people should own the simulator and the interpretation of
any claimed effect. Tracking is the area with the least in-house expertise,
so its scope is held to a small number of methods done carefully.

## Rules carried over from AGENTS.md

- Test time blocks and test synthetic stacks never influence normalization,
  hyperparameters, or training.
- Methods are compared at matched data and matched compute.
- Failures and non-converged runs are reported, not dropped.
- Tracking error, estimator uncertainty, and model-form error are reported
  separately.
- Physical units are preserved from TIFF metadata through to force plots.
- Every experiment has a committed configuration and recorded seeds.

## Risks

| Risk | Response |
|---|---|
| TIFFs arrive late or are not the published runs | Synthetic stacks and published trajectories carry B and D |
| Lab tracking code is not shareable | Baseline is a TrackPy configuration reconstructed from the papers, labeled as such |
| Synthetic images are unrealistic | Calibrate the forward model to real frames; report the gap |
| Too little data to detect many-body effects | Report an upper bound and the data a follow-on would need |
| Lab code is unpublished | Use the version Justin provides; keep it in git-ignored `external/`; never commit or redistribute it |
| Beyond-pairwise work overlaps the lab's force-inference line | Re-scope workstream D with Justin before week 1; fall back to model-free diagnostics |
| Laser-sheet phase was not recorded per frame | Use the calibration; carry its uncertainty into z error |
| MCP work overruns | The plain loader keeps everything else moving |

## Additional datasets offered on 2026-11-11

Eva reported that Auburn and Baylor can provide PK-4 particle
tracks (2D, and lower-resolution 3D), DRIAD simulations of dust and ions
under PK-4 conditions, and velocimetry data. Details are in
`shared/docs/dusty_plasma_data_sources.md`. Proposed handling, not yet
agreed:

- **Core scope is unchanged.** The three weeks stay centered on the Burton
  data. PK-4 is a different regime (microgravity, external field, lower 3D
  resolution) and its formats are not yet known.
- **DRIAD as an external control (stretch, workstream D).** DRIAD resolves
  the ions, so the true dust interaction is known and comes from physics the
  sprint did not write. In closure terms, it lets the defect of the pairwise
  closure be computed directly. If data arrive by the end of week 1, run the
  beyond-pairwise tests on it alongside the in-house simulator. Overlapping
  anisotropic ion clouds are a physically motivated source of the
  non-pairwise effects the tests look for.
- **Design data access for more than one source (workstream A).** The MCP
  server and manifests should use a trajectory schema that PK-4 and DRIAD
  data could also fit, so they can be added later without redesign.
- **Coordinate on methods.** Auburn and Baylor students are applying sparse
  regression (SINDy) to learn the interaction potential. Share the controls
  and scoring from workstream D so results are comparable, and avoid
  duplicating their work.
- **Join the proposed data-standards meeting** with the draft schema and the
  MCP spec as input.

## Out of scope

- Vertical forces.
- The origin of the pressure-dependent charge-mass exponent.
- A full reproduction study of every number in the paper.
- Comparison with the other model families in `model-bakeoff/`.

These are natural follow-ons, and the tracking ground truth and data access
built here are meant to be reusable for them.
