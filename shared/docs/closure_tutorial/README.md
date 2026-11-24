# Closure methods: a comprehensive tutorial

A 48-page tutorial on closure methods, written 2026-11-24. It expands the two
earlier notes in the parent directory:

- `../closure_models_tutorial.tex`, the high-level overview; and
- `../hammett_perkins_closure_derivation.tex`, the Hammett-Perkins derivation.

Both earlier notes are unchanged. They are source notes of the heat-flux
manuscript, and `../plasma_heat_flux_paper/source_manifest.json` records their
SHA-256 hashes, so the expansion lives here as a new document. Everything in
the two notes is included in it.

- [Read the tutorial](tutorial.pdf).
- [LaTeX source](tutorial.tex), with one file per section in `sections/`.
- [Numerical checks](checks.py) and their
  [recorded output](results/2026-11-24/checks.json).

## Contents

| Sections | Subject |
| --- | --- |
| 1-2 | The closure problem; a priori and embedded error; the five hierarchies (BBGKY, kinetic moments, Reynolds/LES, statistical moments, waves) |
| 3-6 | The classical methods: Chapman-Enskog, moment closures by ansatz (Grad, maximum entropy), turbulence closures, Mori-Zwanzig memory closures |
| 7-10 | Plasmas: collisional (Spitzer-Harm, Braginskii, nonlocal models), collisionless (Hammett-Perkins, derived in full and extended to general order), the range between the two limits, magnetized closures |
| 11-13 | Strongly coupled and dusty plasmas; radiation, neutrinos and the supernova profile; wave kinetics and quasilinear theory |
| 14-16 | Learned closures; how a closure is judged; what this repository proves and how the benchmark tracks use it |
| 17, A-C | Summary tables, exercises with answers, symbols, conventions, and the record of numerical checks |

## What is checked and what is not

The first page of the tutorial states this in full. In short:

- The worked examples and every number in them are produced by `checks.py`
  and compared with an independent calculation (Appendix C lists each one).
- Results of the closure notes and the heat-flux manuscript are quoted with
  their conditions and are not re-proved.
- The standard theory, historical attributions, and constants of named models
  were written from general knowledge. The note at the head of the reference
  list says which bibliography entries were checked against sources.

## Reproduce

Python 3 with NumPy and SciPy. From this directory:

```sh
python3 checks.py --output results/my-run
latexmk -pdf tutorial.tex
```

Choose a new run directory each time; the script refuses to overwrite one.
The two figures read `response.dat` and `intermediate.dat` from the run
directory named by `\rundir` in `tutorial.tex`. No random numbers are used.
The run takes a few seconds.
