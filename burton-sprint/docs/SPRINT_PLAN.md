# Burton Sprint Plan

Status: draft for review, revised 2026-11-23. This revision replaces the
2026-11-09 draft and brings the plan in line with the 2026-11-11 meeting
with the Burton lab and the kickoff deck of 2026-11-16
(`shared/presentations/AI_agent_tutorial.pptx`, slides 9 to 19).

Each item below is marked as one of:

- **Fixed**: agreed with the Burton lab or set by the lead.
- **Proposed**: the lead's proposal from the kickoff deck, not yet confirmed
  by the team.
- **Open**: put to the team at the kickoff; the outcome is not yet recorded
  here.

Nothing is binding until recorded in `model-bakeoff/docs/DECISIONS.md`.
The 2026-11-09 draft is in Git history
(`git show 1140243:burton-sprint/docs/SPRINT_PLAN.md`).

## Summary

A three-week sprint, six people (the lead plus five) working with AI agents,
built on Yu, Abdelaleem, Nemenman, and Burton, *Physics-tailored machine
learning reveals unexpected physics in dusty plasmas* (PNAS 122(31),
e2505725122, 2025; arXiv:2310.05273).

- **Lead question (fixed, agreed with the lab 2026-11-11):** how well can we
  find and follow the particles? The sprint's contribution is better
  particle tracking.
- **Dates (fixed):** Monday 2026-11-30 to Friday 2026-12-18, with a
  checkpoint every Friday morning, live or asynchronous.
- **Out of scope (fixed):** force inference. It is the lab's own line of
  work, and not all of its authors are part of TEMPEST.
- **Deliverable (proposed):** a scorecard that every tracker is held to, on
  a frozen synthetic test set and then on the lab's runs, and a short report
  that includes failures and inconclusive results. Whether the sprint also
  builds an easy-to-use tracking tool is open.

## The sprint is an exercise for its participants

Set by the lead on 2026-11-23 (fixed). The sprint is run like a three-week
homework exercise: the participants, working with their own agents, write
the code. That includes the code that gets the data.

- **The repository starts as scaffolding.** It holds this plan, the MCP
  specification, the paper, and an empty package. There is no loader, no
  manifest, and no tracker, on purpose. Nobody, including the lead and the
  lead's agents, builds these ahead of the sprint.
- **Each workstream below is an assignment.** It states what to build, what
  "done" means, and what to hand in at each Friday checkpoint. How to build
  it is for the workstream owner to decide and write down.
- **Data access is the first assignment, not a service.** Nobody downloads
  the lab's data on the team's behalf or passes copies around. Workstream A
  writes code that fetches the runs from where the lab shared them, and
  every participant gets the data by running that code.
- **Handing in.** Work is handed in as commits to this repository: code,
  tests, a committed configuration for each experiment, and a short written
  note of what was run, what failed, and what was not checked.

## What changed since the 2026-11-09 draft

| | Draft of 2026-11-09 | After the 2026-11-11 meeting |
|---|---|---|
| Lead question | Is the pairwise force law an adequate closure? | How well can we find and follow the particles? |
| Inference code | Run the lab's model as a baseline, then extend it | Out of scope; it is the lab's own line of work |
| Data | TIFF stacks promised, transfer unknown | Three of the five published runs shared by the lab as `.cine` video; participants fetch them with their own code; new data later in the year |
| Beyond pairwise | Workstream D, weeks 2 and 3 | Parked unless the team decides otherwise (open) |
| Lab code | An updated version to come from Justin | Use the repaired 2D code, not the paper's repository, which has a plotting error |
| Workstreams | Four: data access, tracking benchmark, pairwise baseline, beyond pairwise | Five, all on tracking (proposed) |

## What the paper provides

Facts taken from the paper and the lab's public repository.

- **Experiments.** Five runs with 9, 10, 13, 15, and 18 melamine-formaldehyde
  particles (8.0 to 12.8 μm) in argon at 0.75 to 1.20 Pa, levitated about
  4.2 mm above the electrode.
- **Imaging.** A laser sheet scans about 4 mm vertically at 200 Hz,
  synchronized to an 8000 fps camera, giving about 40 images per sweep and a
  3D volume rate of 200 Hz. Stated resolution is 50 μm in x, y and 100 μm in
  z.
- **Tracking.** TrackPy v0.6.4, with "special care" for closely spaced
  particles. The 3D reconstruction method is deferred to earlier lab papers
  (Yu and Burton, Phys. Plasmas 2023; Yu, Cho, and Burton, PRE 2022).
- **Public code and data.** `github.com/wyu54/many-body-force-infer` (Zenodo
  DOI 10.5281/zenodo.15866619) holds the force-inference model and the five
  tracked trajectories as CSV files (frame, particle, x, y, z, brightness).
  It has no license file, no tracking code, no raw images, and no simulator
  (checked 2026-11-11).

Limits the paper states about itself that bear on tracking:

- "Mis-identification or mis-tracking of particles can have a detrimental
  effect."
- Non-reciprocity appears at separations below about 0.6 mm, which is the
  regime where tracking closely spaced particles is hardest.

## What the lab told us on 2026-11-11

From the meeting with Justin Burton and his students, recorded from the
lead's handwritten notes.

- **Today's pipeline.** TrackPy running Crocker–Grier–Weeks: blob detection,
  sub-pixel refinement, tunable particle size.
- **Rig.** 10 μm particles in a 100 μm laser sheet, on an arm that tilts.
  Scanning now reaches 500 Hz, up from 200 Hz.
- **Many-body onset.** Justin's view is that pairwise forces hold at 9 to 18
  particles, the range of the published runs. Near 40 particles, three can
  approach closely and n-body terms matter.
- **What the lab would like.** "Even a clickable, very user-friendly
  tracking software would be great."
- **Metadata.** Pressure, power, and particle sizes are known. The
  laser-sheet phase was not recorded per frame; it is derived from a
  calibration. The student who took the published data has left the lab.

### The three tracking problems the sprint takes on

1. **Pixel locking.** Sub-pixel centroid estimates are biased toward
   whole-pixel values, which puts a systematic error into positions and so
   into velocities and forces. Justin flagged this as a big deal. The
   suggested correction is SPIFF, from a UChicago group (group name to be
   confirmed; the handwritten note is unclear).
2. **Track separation.** When particles scatter off each other, identities
   are hard to keep apart. All of the lab's turbulence analysis depends on
   this, and it is the same sub-0.6 mm regime where the paper finds
   non-reciprocity.
3. **Depth.** z resolution is 100 μm against 50 μm in x and y, and the sheet
   position is inferred from a calibration, not recorded.

## Data shared by the lab

Justin shared a Google Drive folder on 2026-11-12 with three of the five
published runs. The link was posted in the TEMPEST Slack; it is not recorded
in this public repository. The table is taken from the lab's metadata sheets
as reported in the kickoff deck. Nobody on the sprint has opened the `.cine`
files yet; doing so is workstream A's first task.

| Run | Conditions | Camera, scan | Frames per volume | xy scale | z scale | Zipped size |
|---|---|---|---|---|---|---|
| 9p | 1.00 Pa, 17.3 V | 2000 fps, 100 Hz | 20 | 0.051 mm/px | not determined | 640 MB |
| 13p | 1.00 Pa, 17.3 V | 2000 fps, 200 Hz | 10 | 0.051 mm/px | 0.125 mm/slice | 689 MB |
| 15p | 0.75 Pa, 17 V | 4000 fps, 200 Hz | 20 | 0.0439 mm/px | 0.1253 mm/slice | 263 MB |

- **Format.** Each run is a zipped `.cine` camera video with a one-row
  metadata sheet. The data are not TIFF stacks, so the loader and
  `../mcp/SPEC.md` must change.
- **Pixel locking is already visible.** The lab's notes say the xy scale was
  confirmed from the pixel-locking period in the published tracks.
- **Handling (fixed).** The data are unpublished raw material. Each
  participant fetches them from the lab's folder with the sprint's own code
  into a local, git-ignored cache. They are never committed, never
  redistributed, and not mirrored to anyone's personal drive for others to
  copy. Only manifests go in `../data/manifests/`, and the folder link stays
  out of the repository.

Still to find out:

- Frame counts and bit depth, which are inside the `.cine` files.
- The z scale for the 9-particle run.
- Whether the 10- and 18-particle runs will follow.
- Why these runs are at 2000 and 4000 fps with 10 or 20 frames per volume,
  where the paper describes 8000 fps and about 40 images per sweep. Ask
  Justin.

## Still owed by the lab

- Justin's paper on 3D imaging, offered at the meeting.
- A pointer to SPIFF.
- The repaired 2D code. Anything the lab provides goes in `../external/`,
  which is git-ignored apart from its README.

Who follows up on each is open.

## Workstreams (proposed)

All five are on tracking. The split of the old tracking benchmark into C and
D follows the two problems the lab named: pixel locking is a detection
problem, and track separation is a linking problem.

| Workstream | Weeks | People | Produces |
|---|---|---|---|
| A. Data access | 1 | 1 | Manifest and loader by day 2; MCP server by day 5 |
| B. Ground truth | 1 to 2 | 1 | Synthetic image sweeps with known particle positions |
| C. Detection | 1 to 3 | 1 | TrackPy baseline, a pixel-locking fix, one alternative detector |
| D. Linking | 1 to 3 | 1 | Alternative linkers; identity through close encounters |
| E. Scorecard and tool | 2 to 3 | 1 | Frozen test set, the scorecard, a tracker people can use |
| Lead | 1 to 3 | 1 | Scope, contact with the Burton lab, the report |

Who takes which workstream is open. The team is strong in ML, scientific
computing, and plasma and statistical physics, and has no image-processing
or infrastructure specialist, so A and B are where agents should help most
and also where a wrong answer is easiest to miss.

### A. Data access (week 1)

Assignment: write the code that gets the lab's data to everyone on the
sprint, and document it so the other four workstreams can use it on day 2.

- Day 1: a fetch command that takes the lab's shared-folder link from local
  configuration (an environment variable or a git-ignored file), downloads
  the three runs and their metadata sheets into a local git-ignored cache,
  and verifies what it downloaded. It must be safe to run twice and must
  fail loudly on a partial or changed file.
- Day 1: read the `.cine` headers and write a manifest in
  `../data/manifests/` with file names, sizes, checksums, frame counts, bit
  depth, and the acquisition metadata with units. Fill in the
  data-description section of `../mcp/SPEC.md`. Report any disagreement
  between the headers and the lab's metadata sheets.
- Day 2: a plain Python loader with the same interface as the server, so no
  other workstream is blocked on the server.
- Day 2 to 5: read-only MCP tools for listing runs, reading metadata, and
  fetching frames or sweep volumes by range.

To settle on day 1 and write down: how the code authenticates to the shared
folder, where the cache lives by default, and which `.cine` reader is used
and how it was checked.

Acceptance: a participant with a fresh clone and access to the lab's folder
can run one documented command and end up with data whose checksums match
the committed manifest. A fresh agent session can then list runs, pull one
full laser-sheet sweep, and reproduce its checksum; frames are returned
unmodified; missing frames produce explicit errors.

Hand in on 4 December: the fetch command, the manifest, the loader with
tests, the updated spec, and a setup note in `../README.md`.

### B. Ground truth (weeks 1 to 2)

Real images have no known true positions. Simulate particle trajectories and
render them into image sweeps through a forward model of the scanning sheet,
the particle point-spread function, and camera noise, calibrated to the
lab's frames.

- The sheet position comes from the calibration; its uncertainty is carried
  into z error.
- The gap between synthetic and real frames is measured and reported.

Acceptance: synthetic sweeps with exact known positions exist by the end of
week 1, and by the end of week 2 a person, not an agent, has judged whether
they look enough like the lab's frames for the scorecard to mean anything.

Hand in: on 4 December, the image model, a seeded configuration, and sample
sweeps; on 11 December, the calibration against real frames and a written
judgment of the gap.

### C. Detection (weeks 1 to 3)

- Baseline: a TrackPy configuration matching the lab's as closely as the
  papers and the lab's code allow, labeled as a reconstruction if the lab's
  configuration is not available.
- A pixel-locking correction (SPIFF if it can be obtained, otherwise an
  alternative documented as such).
- One alternative detector, for example blob detection with sub-pixel
  Gaussian fitting and a 3D fit across the sweep.

A first task that needs no raw data: measure pixel locking in the published
13-particle tracks by histogramming the sub-pixel part of x and y at
0.051 mm per pixel, with a test on uniform random positions that must give a
flat histogram.

Hand in: on 4 December, the pixel-locking measurement and a baseline TrackPy
run; on 11 December, the correction and the alternative detector, scored on
synthetic sweeps; on 18 December, scores on the lab's runs.

### D. Linking (weeks 1 to 3)

- At least one alternative linker, for example assignment-based or
  Kalman-filter linking, so detection errors can be separated from identity
  errors.
- Find and count identity swaps and broken tracks through close encounters.
- A person decides what counts as a correct track in a close encounter.

Hand in: on 4 December, a written definition of a correct track and a swap
counter tested on a made-up crossing; on 11 December, the alternative linker
scored on synthetic sweeps; on 18 December, scores on the lab's runs.

### E. Scorecard and tool (weeks 2 to 3)

- Owns the frozen synthetic test set, so nobody tunes on it.
- Builds the scoring harness and produces the scorecard.
- Packages a tracker the lab can use, if the team decides to build one
  (open).

Hand in: on 11 December, the frozen test set with its manifest and the first
scorecard; on 18 December, the final scorecard, generated from saved
machine-readable metrics.

## Scorecard (proposed)

| Metric | Why it matters |
|---|---|
| Detection recall and precision | Missed particles and phantom particles |
| Position error in x, y, and z | Compared with the stated 50 μm and 100 μm resolution |
| Sub-pixel bias | Pixel locking, measured directly |
| Close-pair resolution against separation | Non-reciprocity shows up below about 0.6 mm |
| Identity swaps and broken tracks | Track separation through close encounters |
| Runtime per sweep | Cost |

- Every method runs on the same frozen synthetic test set, then on the
  lab's runs. Failed and non-converged runs go in the table.
- On real images there is no ground truth. Real-data scores measure
  agreement with the lab's published tracks, not correctness, and the report
  says so.
- The 2026-11-09 draft had a "downstream force error" row that pushed each
  tracker's output through the lab's force-inference model. It is dropped
  because the inference code is out of scope. To ask Justin: would the lab
  run that comparison itself?

## Schedule

Dates and the Friday checkpoints are fixed. The contents of each week are
proposed.

| Week | Dates | Work |
|---|---|---|
| 1. Get set up | 30 Nov to 4 Dec | Fetch code and manifest on day 1; loader on day 2, MCP server by day 5. Image model calibrated to real frames. Baseline TrackPy run. |
| 2. Build and measure | 7 to 11 Dec | Pixel-locking fix and alternative trackers. Synthetic test set frozen. First scorecard. |
| 3. Real data and report | 14 to 18 Dec | Trackers on the lab's runs. Final scorecard; tool packaged. Results frozen on Wednesday 16 December (working day 13), then writing. |

Checkpoints:

- **4 December:** every participant has fetched the data with the sprint's
  own code; baseline runs; synthetic images exist.
- **11 December:** the ground truth is trusted, or scope is cut. This is the
  checkpoint that matters most: if the synthetic images do not look enough
  like the lab's frames, the scorecard means little, and scope is cut then
  and not in week 3.
- **18 December:** the report.

A written update counts as attending a checkpoint.

## How the sprint is run with agents

- **One workstream, one session.** Every agent session starts from
  `AGENTS.md` and this plan. What a session learns goes into a file, or the
  next session does not have it.
- **Plan before code.** A written plan, then the smallest piece that runs.
- **Known answers first.** Synthetic ground truth before real data.
- **Check everything.** Each person re-reads and adjusts what their agent
  produces. Review in a fresh session that has not seen the first one's
  reasoning.

Suggested split of work, to be revised by each workstream owner in week 1:

| Workstream | Hand to an agent | Keep for yourself |
|---|---|---|
| A. Data access | Write the fetch command, read the `.cine` headers, write the loader and manifest, scaffold the MCP server from the spec | Decide what "unmodified" means; look at real frames by eye; check the manifest against the lab's metadata sheets |
| B. Ground truth | Code the image model (laser sheet, particle blur, camera noise) and fit it to real frames | Judge whether synthetic frames look like the lab's |
| C. Detection | Run TrackPy parameter sweeps, implement the pixel-locking fix, plot sub-pixel histograms | Choose which methods are worth comparing |
| D. Linking | Implement alternative linkers; find and count identity swaps | Decide what a correct track is in a close encounter |
| E. Scorecard and tool | Build the scoring harness and the tool's interface | Freeze the test set; sign off on every number |

Week-1 exercise: everyone writes one task brief for their own workstream
(goal, what to read first, what to do, what "done" means with a known
answer, what to report) and brings the result to the first checkpoint.

## Rules carried over from AGENTS.md

- The frozen synthetic test set never influences normalization,
  hyperparameters, or tuning.
- Methods are compared at matched data and matched compute.
- Failures and non-converged runs are reported, not dropped.
- Tracking error, estimator uncertainty, and forward-model error are
  reported separately.
- Physical units are preserved from the `.cine` metadata through to every
  table and plot.
- Every experiment has a committed configuration and recorded seeds.
- The lab's code and unpublished data are never committed or redistributed.

## Open items from the kickoff

Put to the team on 2026-11-16. Record each outcome here and in
`model-bakeoff/docs/DECISIONS.md`.

1. **The beyond-pairwise test.** Park it for the new 40-particle data, or
   keep a small version? The lead's recommendation is to park it.
2. **Who takes which workstream.**
3. **Tools and access before 30 November.** Which agent tools each person
   uses, who still needs the team plan, and whether every participant can
   open the lab's shared data folder.
4. **The deliverable.** A scorecard and a short report; does the sprint also
   build the easy-to-use tracker?
5. **Follow-ups with the lab.** Who chases the 3D imaging paper and SPIFF.
6. **Later, not now.** PK-4 tracks, DRIAD simulations, and velocimetry from
   Auburn and Baylor.

## Risks

| Risk | Response |
|---|---|
| `.cine` files are hard to read or differ from the metadata sheets | Day-1 header read and manifest; report any mismatch to Justin before building on it |
| Fetching from the lab's shared folder is harder than expected (access, authentication, large files) | It is the day-1 assignment, so it surfaces first; workstreams B to D start on synthetic images and the published tracks, which need no raw data |
| A participant lacks access to the lab's folder | Settle access before 30 November, with the tools question in the open items |
| Synthetic images are unrealistic | Calibrate the forward model to real frames; report the gap; cut scope at the week-2 checkpoint |
| SPIFF cannot be obtained | Implement an alternative pixel-locking correction and label it as such |
| Lab tracking configuration or repaired code does not arrive | Baseline is a TrackPy configuration reconstructed from the papers, labeled as such |
| No image-processing specialist | Hold the number of methods small and done carefully; a person judges every image-level result |
| Laser-sheet phase was not recorded per frame | Use the calibration; carry its uncertainty into z error |
| Unpublished lab code or data leaks into the public repository | Git-ignored folders only; manifests, not data, are committed |
| MCP work overruns | The plain loader keeps everything else moving |
| The 10- and 18-particle runs do not arrive | Report on the three runs in hand |

## Parked: pairwise baseline and beyond-pairwise test

Parked unless the team decides otherwise. The full design is in the
2026-11-09 draft; the framing is kept here because it is the sprint's link
to the rest of TEMPEST.

- **Closure framing.** The retained state is the dust positions and
  velocities; ions, electrons, and neutrals are eliminated. The paper's
  pairwise force plus environment force and damping is the classical reduced
  operator, and many-body or memory terms are its closure defect. This is
  the effective-interaction stage of the dusty-plasma ladder in
  `model-bakeoff/`.
- **Why it is parked.** Force inference is the lab's own line of work, and
  the published runs (9 to 18 particles) sit in the range where Justin
  expects pairwise forces to hold. The question belongs with the new
  40-particle data.
- **What would carry over.** Controls first (a strictly pairwise simulation
  to set the false-positive rate, a planted effect to set the detection
  threshold), then experimental data; model-free diagnostics (residual
  structure, three-particle correlations) before any extension of the lab's
  model; and DRIAD, which resolves the ions, as the place where the defect
  can be computed directly.
- **What this sprint contributes to it.** Tracking with quantified error at
  close separations is a precondition for any later claim about forces
  there.

## Additional datasets offered on 2026-11-11

Auburn and Baylor can provide PK-4 particle tracks, DRIAD simulations, and
velocimetry data; details are in `shared/docs/dusty_plasma_data_sources.md`.
These are not part of this sprint. The loader and manifests should use a
schema that other sources could fit later without redesign.

## Out of scope

- Force inference, including vertical forces and the pressure-dependent
  charge-mass exponent.
- A reproduction study of the paper's numbers.
- Comparison with the model families in `model-bakeoff/`.
