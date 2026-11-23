# Burton Sprint

A three-week sprint, 2026-11-30 to 2026-12-18, on tracking dust particles
in image data from Justin Burton's lab. It is built on three inputs:

1. the lab's paper (`paper/`);
2. raw `.cine` camera video for three of the paper's five runs, shared by
   the lab; and
3. the lab's own analysis software, where it can be shared (`external/`).

The sprint design is in [`docs/SPRINT_PLAN.md`](docs/SPRINT_PLAN.md): six
people in five workstreams covering data access, synthetic ground truth,
detection, linking, and a scorecard that every tracker is held to.

The sprint is run as an exercise for its participants. This folder is
scaffolding: the plan, the MCP specification, the paper, and an empty
package. The participants write the code, starting with the code that
fetches the data. Nothing here downloads the data for you yet.

## Directory map

- `paper/`: the paper PDF and reading notes.
- `mcp/SPEC.md`: specification for the MCP server that will serve the image
  data. Writing the server is part of workstream A.
- `data/samples/`: local cache for fetched data. Git-ignored.
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

## Getting the data

The lab's data are unpublished. They are not in this repository, the link to
them is not in this repository, and nobody passes copies around. Workstream
A's first assignment is a fetch command that pulls the runs from the lab's
shared folder into a local git-ignored cache and checks them against a
committed manifest. When it exists, its usage goes here.

Before the sprint starts, make sure you can push to this repository and
that you are in the TEMPEST Slack. Then copy `.env.example` to `.env` and set
`BURTON_DATA_URL` to the folder link from the TEMPEST Slack. `.env` is
git-ignored. Check that you can open the folder in a browser.

## Open items

See "Open items from the kickoff" and "Still owed by the lab" in the sprint
plan.
