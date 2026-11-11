# Dusty-plasma data sources available to the collaboration

Status: notes, started 2026-11-11. Nothing here has been inspected first-hand
unless it says so. Each entry records who reported it and when.

## Summary

| Source | Kind | Dimensions | Held by | Status |
|---|---|---|---|---|
| Burton lab image stacks | Raw TIFF camera frames | 3D via laser-sheet scan | Emory (Burton) | Raw version of the published data offered 2026-11-11; new data also on offer |
| Burton lab published trajectories | Tracked particle positions, five runs | 3D | Public repository | Verified 2026-11-09 |
| PK-4 experiment tracks | Tracked particle positions | 2D, and lower-resolution 3D | Auburn and Baylor | Offered to the collaboration |
| DRIAD simulation | Simulated dust and ion dynamics | 3D | Baylor (Lorin's group) | Offered to the collaboration |
| Dust velocimetry | Velocity fields | Not stated | Saikat | Mentioned; access exists |
| Other Auburn and Baylor experiments | Tracked particle positions | Not stated | Auburn and Baylor | Offered to the collaboration |

## Burton lab (Emory)

See `burton-sprint/README.md` and `burton-sprint/docs/SPRINT_PLAN.md`.

- Published trajectories: five runs with 9 to 18 particles, as CSV files in
  `github.com/wyu54/many-body-force-infer`. Ground-based experiment with
  particles levitated in the sheath; forces are non-reciprocal at short
  range. The published analysis assumes pairwise forces and does not test
  for many-body effects. The repository contains no simulator and no
  simulated trajectories.
- Raw image stacks: Justin offered the raw version of the published data
  first, and new data with complete metadata later (2026-11-11). To be
  served through the MCP server specified in `burton-sprint/mcp/SPEC.md`.
- Metadata: pressure, power, and particle sizes are known. The laser-sheet
  phase was not recorded per frame and is derived from a calibration.
- Updated lab code will be provided directly and is not public.

## PK-4 experiments (Auburn and Baylor)

Reported by Eva on 2026-11-11.

- Plasmakristall-4 (PK-4) is a dusty-plasma facility on board the
  International Space Station.
- The dust-dust interaction potential deviates from Yukawa because of a
  unidirectional external electric field.
- Particle tracking data are available in 2D and in 3D. The 3D data are much
  lower resolution; the reconstruction method was offered verbally and is not
  yet documented here.
- The two groups are working with NASA to release PK-4 datasets, metadata,
  and analysis codes through the Physical Sciences Informatics (PSI)
  repository:
  <https://psi.nasa.gov/physci/repo/search?q=pk-4&data_source=psi&data_type=investigation>

Not yet known: number of runs, particle counts, frame rates, spatial
resolution, file formats, uncertainty estimates, and terms of use.

## DRIAD simulation (Baylor)

Reported by Eva on 2026-11-11.

- DRIAD models both dust and ions under PK-4 conditions.
- Because ions are simulated, the interaction potential among dust particles
  shielded by anisotropic ion clouds can be reconstructed explicitly.
- 3D data can be provided.
- Relevance to closure work: with ions resolved, the dust-only description
  is a reduced model whose eliminated variables are available. The defect of
  a pairwise force closure (many-body terms from overlapping ion clouds,
  memory from wake relaxation) can therefore be computed directly, which
  makes DRIAD a candidate reference case for the effective-interaction stage
  of the dusty-plasma ladder in `model-bakeoff/` and for workstream D of the
  Burton sprint.

Not yet known: output format, parameter ranges available, whether ion-level
data or only dust trajectories and reconstructed potentials are shared, and
the code's availability.

## Dust velocimetry

Reported by Eva on 2026-11-11.

- Velocimetry data exist from PK-4 and from many laboratory experiments.

Not yet known: technique, resolution, formats, and which experiments.

## Related method work elsewhere in the collaboration

Students in the Auburn and Baylor groups are using sparse regression (SINDy)
to learn the functional form of the dust interaction potential, first from
DRIAD simulations and eventually from PK-4 experiments. This overlaps with
the force-inference work in `burton-sprint/` and with the
effective-interaction stage of the dusty-plasma ladder in `model-bakeoff/`,
so the efforts should be coordinated.

## Open items for the collaboration

- A meeting on data formats and standards was proposed so that all groups
  provide consistent datasets.
- How to release data so that colleagues outside dusty plasma can use it.

A common trajectory schema would need at least: run identifier, frame index
and timestamp, particle identifier, positions with units, per-coordinate
uncertainty, a brightness or size proxy, and per-run metadata (pressure,
power, gas, particle size and material, field configuration, gravity
condition, and how 3D positions were reconstructed). The Burton CSV layout
(frame, particle, x, y, z, brightness) is a subset of this.
