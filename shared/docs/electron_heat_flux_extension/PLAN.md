# Extension plan: thermal drive and electron-ion collisions

17 November 2026. Scope: push the results of
`shared/docs/plasma_heat_flux_paper/manuscript.tex` toward the electron
heat-flux problem that plasma transport codes actually close. The manuscript
and its validated bundle are not modified; this directory is a companion note
with its own code, configuration, tests and saved metrics.

## Scale transition

- Full state: linearized electron distribution `h(t, x, v)`, `v` in R^3,
  axisymmetric about `x`.
- Retained state: electron temperature `T` (density and current are pinned
  by quasi-neutrality with immobile ions).
- Discarded: heat flux, stress, friction, all higher moments.
- Classical reduced operator: Spitzer-Harm conduction at zero current.
- Closure defect: `q + i k kappa T`, measured through the multiplier
  `chi(k)` of a specified response.

## Steps

1. Replace the potential drive by an isotropic heating source. Show that the
   temperature response is then a diagonal resolvent entry, so the
   one-dimensional dual variational principle carries over to three
   dimensions for every symmetric nonnegative collision operator whose
   kernel contains `1` and `|v|^2`. Consequences to prove: positivity and
   `kappa/(1 + K k^2) <= chi <= kappa` at all `k`, and the sharp leading
   coefficient `K`.
2. Record the 2x2 parallel/perpendicular response matrix that explains why
   the potential-driven response of the manuscript has an uncontrolled
   cross term and the thermal one does not.
3. Derive the exact thermally driven Dougherty response in three dimensions
   as the theorem-faithful reference.
4. Add electron-ion pitch-angle scattering (immobile ions, charge `Z`) to
   the like-particle Landau operator. Momentum is no longer conserved; the
   local limit becomes the zero-current Spitzer-Harm conductivity.
5. Numerics in the existing polynomial Galerkin basis: exact-quadrature
   Lorentz matrix, transport constants versus `Z`, response curves, degree
   refinement. Validate against Braginskii (degree 6), Spitzer-Harm, and
   the closed-form Lorentz limits.
6. Embedded test: decay of a temperature perturbation in the quasi-neutral,
   zero-current kinetic model versus the closed temperature equation.
7. Tests before the full run; metrics saved in a new run directory; tables
   and figures generated only from saved metrics; companion note in LaTeX.

## Evidence boundaries

- Linear, homogeneous Maxwellian background, one spatial Fourier direction,
  unmagnetized, immobile ions, no ion dynamics or sheath.
- Theorems are conditional on the form-domain solvability hypotheses, as in
  the manuscript. No weighted-space existence proof is added for the
  electron operator.
- Galerkin degree differences are diagnostics, not certified error bars.
  The `1/v^3` Lorentz rate makes polynomial convergence slow at large `Z`;
  this is reported, not hidden.
- No trained models. Deterministic calculations have no ensemble error.
