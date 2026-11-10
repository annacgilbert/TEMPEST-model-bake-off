# Burton Sprint

A short, focused project built on three inputs from Justin Burton's lab:

1. his paper (`paper/`);
2. his stack of TIFF images (reached through an MCP server, see `mcp/`); and
3. whatever analysis software the lab already has (`external/`).

The sprint design is in [`docs/SPRINT_PLAN.md`](docs/SPRINT_PLAN.md): three weeks,
six people, covering automated data access, a tracking-method benchmark, and
a test for forces beyond the paper's pairwise model.

## Directory map

- `paper/`: the paper PDF and reading notes.
- `mcp/SPEC.md`: specification for the MCP server that will serve the image
  data. The server itself is to be written by others.
- `data/samples/`: a few local TIFFs for getting started before the MCP server
  exists. Git-ignored.
- `data/manifests/`: committed manifests (filenames, checksums, acquisition
  metadata) for any data used.
- `external/`: slot for the Burton lab's software; how it is brought in is
  undecided.
- `src/burton_sprint/`: this project's own Python package.
- `tests/`, `notebooks/`, `docs/`: tests, exploratory analysis, and project
  notes.

## Setup

```bash
cd burton-sprint
python -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
```

## Open items

See "Questions for Justin Burton" in the sprint plan: what the TIFF stack
contains, whether the lab's tracking code can be shared, and licensing of the
public force-inference code.
