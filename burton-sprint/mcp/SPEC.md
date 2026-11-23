# MCP server for the Burton image data: specification

Status: draft skeleton, revised 2026-11-23. The server is written by the
sprint participants in workstream A (see `../docs/SPRINT_PLAN.md`); this
document is the contract they implement and the other workstreams rely on.
Sections marked _open_ are filled in by workstream A from the data itself.

## Purpose

Give analysis code and AI agents read-only, structured access to the Burton
lab's `.cine` camera video without copying the dataset into this repository.

The server reads from a local cache. Filling that cache is a separate step:
a fetch command, also written by workstream A, that downloads the runs from
the lab's shared folder and verifies them against the committed manifest.
The folder link is read from `BURTON_DATA_URL` in the git-ignored
`burton-sprint/.env` and is never committed.

## Data description (_open_)

Known from the lab's metadata sheets, as reported on 2026-11-16 and not yet
checked against the files:

- Runs covered: three of the paper's five, with 9, 13, and 15 particles.
- Format: one zipped `.cine` video per run, each with a one-row metadata
  sheet; about 1.6 GB zipped in total.
- Camera and scan rates, frames per volume, and pixel scales: see the table
  in `../docs/SPRINT_PLAN.md`.

To be filled in by workstream A from the `.cine` headers:

- Number of frames per run:
- Exposure:
- Image dimensions, bit depth, channels:
- z scale for the 9-particle run:
- Any disagreement between the headers and the metadata sheets:

## Proposed tools

| Tool | Input | Returns |
|---|---|---|
| `list_runs` | optional filters | run ids with summary metadata |
| `get_run_metadata` | run id | acquisition parameters with units |
| `list_frames` | run id, optional range | frame indices and timestamps |
| `get_frame` | run id, frame index, optional crop / downsample | image data plus dtype, shape, pixel scale |
| `get_frames` | run id, index range, stride | a batch of frames |
| `get_volume` | run id, sweep index | all frames of one laser-sheet sweep, in order |
| `get_checksum` | run id, optional frame index | content hash for manifests |

The tool list is a proposal; revise once the data layout is known.

## Requirements

- Read-only. No tool modifies or deletes source data.
- Frames are returned unmodified by default: no rescaling, normalization, or
  lossy compression unless explicitly requested, and any such processing is
  reported in the response.
- Every response carries physical units and enough identifiers (run id, frame
  index, checksum) to write a reproducible manifest in `data/manifests/`.
- Errors and missing frames are reported explicitly, never silently skipped.
- Large requests are paginated or range-limited.

## Open questions

- Transport and hosting (local stdio server vs. remote HTTP), and who runs it.
- Authentication and who may access the data.
- Image encoding for transfer (raw array, TIFF bytes, PNG).
- Which `.cine` reader is used and how it is validated.
- Whether derived products (particle positions, tracks) are also served.
- Where the server code lives (`burton-sprint/mcp/` or its own repository).
