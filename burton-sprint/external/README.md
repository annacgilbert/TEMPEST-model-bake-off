# External: Burton lab software

## Known public code

`https://github.com/wyu54/many-body-force-infer` (Zenodo DOI
10.5281/zenodo.15866619), checked 2026-11-09. Contents:

- `ForceInfer.py` and `demonstration.ipynb`: the force-inference model from
  the paper (TensorFlow 2.4, numpy 1.21, pandas 1.2, sympy 1.10).
- Five tracked trajectory files (`9p`, `10p`, `13p`, `18p`, and
  `0.75Pa15p`, each `_cleared.csv`) with columns frame, particle, x, y, z,
  and brightness.

The repository has no license file, and it does not contain the lab's image
tracking or 3D reconstruction code, or any raw images.

## Lab-provided code (2026-11-11)

Justin Burton will provide an updated, cleaned-up version of the lab's code
directly. It is not public and will not be until a further paper is out.

- Put it in this folder. Everything here except this README is git-ignored.
- Never commit it, push it, or redistribute it.
- Use it, not the public `ForceInfer.py`, for any baseline.
- Not yet known: whether it includes the tracking and 3D-reconstruction
  code, its language, and its license.

When code is added, record here: source, commit or date, authors, license,
language and dependencies, and any local modifications.
