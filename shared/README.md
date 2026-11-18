# Shared TEMPEST material

Background used by all three projects. Nothing here is project-specific code.

- `references/`: the TEMPEST proposal, the closure / PINN / operator /
  world-model literature chapter, and the classical many-body ML survey.
  Provenance is recorded in `references/README.md`.
- `docs/`: `PROJECT_BRIEF` and `mathematical_closure_program` (Markdown and
  PDF).
  Also `dusty_plasma_data_sources.md`, a running list of datasets offered
  to the collaboration.
  The [plasma heat-flux paper](docs/plasma_heat_flux_paper/README.md) synthesizes
  the closure notes into a research manuscript with proofs, a source audit,
  and reproducible computations; the original notes remain intact.
  The [electron heat-flux extension](docs/electron_heat_flux_extension/README.md)
  carries those results to a thermal drive and to electron-ion collisions.
- `presentations/`: the full TEMPEST closure-models talk.
- `assets/`: figures reused across documents and the talk.

Do not silently replace or edit source documents; record provenance, version,
and retrieval date when adding one.
