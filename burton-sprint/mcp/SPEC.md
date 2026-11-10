# MCP server for the Burton image data: specification

Status: draft skeleton. The server will be written by others; this document
is the contract they implement and the sprint code relies on. Sections marked
_open_ need input from the Burton lab or the sprint lead.

## Purpose

Give analysis code and AI agents read-only, structured access to Justin
Burton's TIFF image stacks without copying the full dataset into this
repository.

## Data description (_open_)

- Experiments / runs covered:
- Number of stacks and frames per stack:
- Frame rate, exposure, pixel scale (with physical units):
- Image dimensions, bit depth, channels:
- Total size and where it is hosted:
- Associated metadata (pressure, power, particle size, camera settings):

## Proposed tools

| Tool | Input | Returns |
|---|---|---|
| `list_runs` | optional filters | run ids with summary metadata |
| `get_run_metadata` | run id | acquisition parameters with units |
| `list_frames` | run id, optional range | frame indices and timestamps |
| `get_frame` | run id, frame index, optional crop / downsample | image data plus dtype, shape, pixel scale |
| `get_frames` | run id, index range, stride | a batch of frames |
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
- Whether derived products (particle positions, tracks) are also served.
- Where the server code lives (`burton-sprint/mcp/` or its own repository).
