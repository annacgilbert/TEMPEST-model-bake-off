# TEMPEST closure projects

Three independent projects on closure across microscopic, kinetic, fluid, and
turbulent scales, plus the background material they share.

| Folder | Project |
|---|---|
| [`model-bakeoff/`](model-bakeoff/) | Reproducible benchmark comparing classical limits, cumulant and memory closures, PINNs, neural operators, PINOs, learned closures, structured neural dynamics, and world models under a common evaluation harness. |
| [`hani-to-algorithms/`](hani-to-algorithms/) | Proof-guided program and prospective paper turning the Deng--Hani--Ma cumulant and interaction-history structures into measurable diagnostics and numerical corrections. |
| [`burton-sprint/`](burton-sprint/) | Sprint project built on Justin Burton's dusty-plasma paper, his stack of TIFF images, and his lab's software. |
| [`shared/`](shared/) | TEMPEST proposal, literature surveys, project brief, mathematical closure program, talk deck, and common figures. |

Each project has its own README, Python package, tests, and `pyproject.toml`.
Projects do not import one another's code; anything all three need to read
lives in `shared/`.

Working rules for contributors and coding agents are in
[`AGENTS.md`](AGENTS.md). Binding decisions are logged in
[`model-bakeoff/docs/DECISIONS.md`](model-bakeoff/docs/DECISIONS.md).
