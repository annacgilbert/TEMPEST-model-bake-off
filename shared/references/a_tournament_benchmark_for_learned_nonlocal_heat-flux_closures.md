# A Tournament Benchmark for Learned Nonlocal Heat-Flux Closures

**Ground truth: Vlasov–Lenard–Bernstein. Target application: non-local electron transport in ICF/IFE.**

*Draft note for discussion — v0.1*

---

## 1. The problem, stated as a closure problem

In inertial confinement and inertial fusion energy targets, the electron mean free path in the
corona becomes comparable to the temperature scale length. Fourier's law with the Spitzer–Härm
conductivity then fails badly: it overpredicts the peak flux by factors of several and, worse,
predicts no flux at all in regions where kinetic simulation shows substantial preheat. The
production workaround — a flux limiter $q = \min(q_{SH}, f\, q_{FS})$ with $f$ tuned per
experiment — is a fitting parameter, not a model.

The mathematical content of the failure is that the exact heat flux is a *functional* of the
temperature profile over a region many mean free paths wide,

$$
q(x) \;=\; \mathcal{Q}\big[n, u, T\big](x),
$$

and not a function of the local state and its first derivative. Any closure of the form
$q = -\kappa(n,T)\,\partial_x T$ is structurally incapable of representing it. So the object to be
learned is an *operator*, and the natural hypothesis classes are kernel/convolution models, neural
operators (FNO, DeepONet), attention over the profile, or auxiliary-PDE closures in the spirit of
SNB. This is what makes the problem interesting rather than a curve fit.

What I would like to propose is: (i) a ground-truth model clean enough that a mathematician can
actually prove things about the closure being approximated, and (ii) a *tournament* structure in
which many groups submit closures, an automated harness evaluates all of them on identical
problems including adversarially generated ones, and everything is scored against both each other
and the published closures.

---

## 2. Why Vlasov–Lenard–Bernstein as the ground truth

We take as the truth model the Vlasov equation with the conservative Lenard–Bernstein (Dougherty)
collision operator. For a single electron species on a fixed neutralizing ion background,

$$
\partial_t f + v\cdot\nabla_x f - \frac{e}{m_e}E\cdot\nabla_v f \;=\; \mathcal{C}_{LB}[f],
$$

$$
\mathcal{C}_{LB}[f] \;=\; \nu(n,T)\,\nabla_v\cdot\!\Big[(v-u)f + \frac{T}{m_e}\nabla_v f\Big],
$$

with $n, u, T$ the moments of $f$ itself, and $E$ from Poisson (or from the zero-current condition
under quasineutrality). We have access to the Haack code, developed with Murillo and Hauck, which
gives us a deterministic solver for exactly this family, including the multispecies BGK-type
extensions.

The reasons to start here rather than with a full Vlasov–Fokker–Planck code:

**It has the structure a mathematician needs.** $\mathcal{C}_{LB}$ conserves mass, momentum, and
energy exactly; it satisfies an H-theorem with Maxwellian equilibria; the linearized operator is
self-adjoint and negative semidefinite in the $L^2(M^{-1})$ inner product. Well-posedness theory
exists. This means statements about the closure can be *theorems*, not observations.

**The local limit is available in closed form.** Because $\nu$ does not depend on $v$, the
linearized LB operator is diagonal in the tensor Hermite basis, with

$$
\mathcal{L}\,H_{\boldsymbol{\alpha}} \;=\; -\nu\,|\boldsymbol{\alpha}|\,H_{\boldsymbol{\alpha}},
\qquad |\boldsymbol{\alpha}| = \alpha_1+\alpha_2+\alpha_3 .
$$

Chapman–Enskog is therefore exact and elementary: viscosity comes from the degree-2 eigenvalue,
heat flux from degree-3, giving $\mu = nT/2\nu$, $\kappa = \tfrac{5}{6}\,nT/(m\nu)$, hence a fixed
Prandtl number (I get $3/2$; worth re-deriving independently before it goes in a paper). Every
submitted closure has an exactly known $\varepsilon\to 0$ limit it must reproduce. There is no
ambiguity about what "the local answer" is, which is not true when you benchmark against a real VFP
code where the Spitzer–Härm coefficient itself depends on the Coulomb logarithm convention.

**The exact linear closure kernel is computable analytically.** Linearize about a uniform
Maxwellian, Fourier transform in $x$, and solve the resulting Hermite recursion. The exact
relationship $\hat{q}(k) = -\hat{\kappa}(k\lambda)\,ik\,\hat{T}(k)$ defines a *gold-standard
symbol* against which any submitted closure can be compared with no simulation error at all. This
is the analogue of the Epperlein–Short curve, but exact rather than semi-analytic. It gives us a
free, cheap, decisive unit test, and it gives the math side something concrete: characterize the
regularity, decay, and analyticity of $\hat\kappa$, and ask which approximation classes achieve
what rates against it.

**The Hermite connection makes "closure" precise.** VLB in a Hermite basis is a moment hierarchy in
which the collision operator is diagonal and the streaming term is tridiagonal. Closing at the
heat-flux moment is *literally* truncating that hierarchy, and Hammett–Perkins-style Landau-fluid
closures are the classical hand-designed answer. So a learned closure sits in a well-understood
family and can be compared against a lineage of analytic ones.

### The caveat, which must be stated loudly

In LB the collision frequency is velocity-independent. In a real plasma $\nu(v)\propto v^{-3}$, so
the electrons that carry most of the heat ($v\approx 3.7\,v_{th}$) have mean free paths of order
$200\,\lambda_{ei}$. *That* is the physical origin of nonlocality in ICF. VLB at a given Knudsen
number is therefore substantially less nonlocal than a real plasma at the same Knudsen number, and
the shape of $\hat\kappa(k\lambda)$ will differ from Epperlein–Short.

The consequence is that **VLB is a testbed for the closure-learning methodology, not a physics
surrogate**. We should be explicit about this in anything we publish. The claim we can support is:
"here is a controlled problem with known exact answers, on which we can determine which operator
architectures, constraints, and training protocols actually work" — and then port the winners up
the ladder. A second consequence, discussed in §6, is that the published closures cannot be
transplanted to VLB without rederivation, since most of them are built around $\nu\propto v^{-3}$.

---

## 3. The closure to be learned

Fix the fluid system to be closed:

$$
\partial_t n + \partial_x(nu) = 0,\qquad
\partial_t(mnu) + \partial_x(mnu^2 + p + \pi) = -enE,
$$
$$
\partial_t\big(\tfrac{3}{2}p\big) + \partial_x\big(\tfrac{3}{2}pu + q\big) + (p+\pi)\,\partial_x u = 0 .
$$

**Primary track:** $\pi$ is supplied by the exact local CE expression (which is exact at
$O(\varepsilon)$ for LB), and only $q$ is learned. This isolates the heat-flux closure and keeps
the tournament interpretable.

**Secondary track:** both $\pi$ and $q$ learned. Worth having, because in the steep-front cases the
viscous closure fails at the same Knudsen numbers and there is real risk that a heat-flux-only
tournament produces closures that silently absorb viscous error.

The electric field must be retained. In the zero-current configuration the return-current field is
a first-order contributor to the flux, and a closure trained on profiles where $E$ was suppressed
will not transfer. Submissions receive $E$ (or the current constraint) as an input.

Dimensionless inputs only: submissions see $(\hat n, \hat u, \hat T, \hat E)$ on the grid plus
$\varepsilon = \lambda_0/L$ and $\hat\nu$. A closure that has learned the density regime of the
training set instead of the Knudsen number is a failure mode we should design out from the start.

### Structural requirements on submissions

These are gates, not scoring criteria. A submission that fails them is disqualified from the main
leaderboard (though it may be interesting enough to report separately).

1. **Correct local limit.** As $\varepsilon\to 0$, must converge to CE-LB at the known rate.
2. **Free-streaming bound.** $|q| \le n T v_{th}$ up to a fixed constant, enforced structurally.
3. **Entropy consistency.** $q\,\partial_x T \le 0$ pointwise. The cleanest way to guarantee this is
   to parameterize the closure as $q = -\mathcal{K}\mathcal{K}^*\partial_x T$ with $\mathcal{K}$
   learned, which makes the closure entropy-dissipative by construction. Whether that
   parameterization is expressive enough to capture the exact kernel is itself a good question.
4. **Conservative form.** Flux evaluated at cell faces, divergence taken discretely, so energy
   conservation is exact regardless of closure error.
5. **Galilean invariance** and invariance under the scalings the nondimensionalization implies.
6. **Determinism and a compute budget.** Fixed cost per call, reported, with no access to the VLB
   solver at evaluation time.

---

## 4. Test hierarchy

Ordered by increasing difficulty; each rung has a clearly defined failure mode.

**T0 — Linear response (analytic gate).** Small sinusoidal $\delta T$ on a uniform background.
Compare the closure's effective conductivity to the exact symbol $\hat\kappa(k\lambda)$ over
$k\lambda \in [10^{-2}, 10^{2}]$. No simulation required; runs in seconds; pass/fail. Any closure
that cannot reproduce this curve should not proceed.

**T1 — Nonlinear relaxation.** Gaussian and top-hat hot spots at amplitudes $\delta T/T \in
\{0.1, 0.5, 2\}$. Tests whether the closure survives outside the linear regime it was probably
trained in. Report both flux error and the decay rate of the peak temperature.

**T2 — Steep front / preheat.** Hot low-density region adjacent to a cold dense slab: the
ICF-relevant configuration and the one flux limiters were invented for. Two distinct error metrics
that must be reported separately — peak flux magnitude, and penetration depth of the preheat tail
(defined by a fixed threshold on $\Delta T$ in the cold material). A closure can get the first right
and the second badly wrong, which is exactly what a flux limiter does.

**T3 — Out-of-distribution profiles.** Random Fourier temperature fields with prescribed spectra,
including multi-scale profiles with no single well-defined $L_T$. This is the generalization test.
The training set should be announced as covering a stated range, and T3 should include cases
outside it, disclosed as such.

**T4 — A posteriori coupling.** Closure embedded in the fluid solver, evolved, compared to VLB
moments over long times. This is the metric that actually matters and the one that most cleanly
separates methods: closures that fit frozen-profile fluxes beautifully routinely destabilize when
the hydrodynamics is allowed to respond, because the error correlates with the mode the solver is
most sensitive to. Report time-to-blowup where relevant.

**T5 — Extensions (stretch).** In rough order of value:
velocity-dependent $\nu(v)$ (this breaks the Hermite diagonalization and is where the problem starts
to resemble real plasma); two-species with the Haack–Hauck–Murillo multispecies operator, where the
ion channel and temperature equilibration enter; magnetized transport with Nernst and Righi-Leduc,
where the published closures are weakest and the payoff is largest.

---

## 5. Tournament mechanics

The point of the tournament framing is that closure papers in this field are almost never compared
on identical problems. Each proposes a method, evaluates it on its own test cases, and compares to
a flux limiter. A common harness would be a genuine contribution independent of who wins.

**Submission interface.** A container exposing a single callable:
`q_faces = closure(n, u, T, E, eps, nu, grid, state)`, with `state` optional and persistent for
closures carrying auxiliary fields (multigroup, SNB-like, memory kernels). Reference
implementations of two baselines shipped as templates.

**Data.** Public training set spanning a declared parameter range, released with the harness.
Hidden test set, same generator, plus adversarial cases (below). Fixed seeds, versioned, archived
with a DOI.

**Automated evaluation.** This is where an AI harness earns its keep, and it is more than
convenience:

- Runs every submission on every case, both tracks, and tabulates — removing the "each paper uses
  its own test" problem.
- **Adversarial profile search.** Optimizes over profile parameters (CMA-ES or gradient-based
  through the coupled solver where differentiable) to *maximize* each closure's error or drive it
  unstable. Every submission gets its own worst case found for it. This is the single most
  informative output of the whole exercise and is not something anyone does by hand.
- Stability and constraint auditing: monitors $q\,\partial_x T$ sign violations, conservation
  drift, CFL-limit degradation, and blowup across the full sweep.
- Regression testing as submissions are revised.
- Cost accounting: wall time and memory per call, relative to VLB.

**Scoring.** Multiple leaderboards, not one composite number. At minimum: T0 symbol error; a priori
$L^2$ flux error; a posteriori trajectory error; worst-case (adversarial) error; constraint
violation rate; cost. Report medians *and* worst cases — a closure with excellent mean error and
one catastrophic failure mode is not a usable closure, and mean-only scoring hides exactly that.

**Anti-gaming.** Hidden test set; no truth-solver access at evaluation; submission-time compute
limits; adversarial cases generated after submission freeze.

---

## 6. Comparison to the published closures

The baseline set: local CE-LB; flux limiters across $f \in [0.03, 0.15]$; the Luciani–Mora–Virmont
nonlocal kernel; Schurtz–Nicolaï–Busquet in its several implementations; Ji–Held; Hammett–Perkins
Landau-fluid closures; higher-order Chapman–Enskog and hyperbolic moment closures (Grad-13,
Levermore, the hyperbolic moment hierarchies of Cai–Fan–Li).

An important subtlety: **most of these cannot be transplanted to VLB unmodified.** SNB's multigroup
structure is built on $\nu \propto v^{-3}$ — the whole point of the energy groups is that different
velocity groups have wildly different mean free paths. With velocity-independent $\nu$, the
multigroup structure collapses and SNB degenerates to a single-group nonlocal diffusion, essentially
a single-Lorentzian LMV kernel. This is not a defect of the exercise; it is informative. On VLB we
can say *exactly* how wrong the degenerate SNB is, because we have the exact symbol. And it sharpens
the argument for T5's velocity-dependent rung: that is precisely where the published closures'
central design assumption switches back on.

Brodrick et al. (2017, *Phys. Plasmas*) is the reference point for benchmarking practice here, both
for their test set and for their documentation of the mean-free-path convention discrepancies that
have made SNB implementations mutually incomparable. We should match their definitional conventions
wherever the problems overlap, so that our numbers can be placed alongside theirs.

---

## 7. Open mathematical questions

The ones I think are worth your attention, roughly in order of tractability:

1. **Characterize the exact linear kernel.** From the Hermite recursion, obtain $\hat\kappa(k\lambda)$
   in closed or semi-closed form. What is its analyticity domain, its decay as $k\lambda\to\infty$,
   its behavior at small $k\lambda$? Is the corresponding operator pseudodifferential in a standard
   class? This is the object every learned closure is trying to approximate in the linear regime, and
   knowing it precisely converts a benchmark into a theorem-supported gold standard.

2. **Admissible closure cone.** Which nonlocal operators $\mathcal{Q}$ yield a well-posed closed
   fluid system? What conditions on the symbol give parabolicity, and which give finite propagation
   speed? LMV-type kernels are known to permit acausal instantaneous action; a clean statement of the
   constraint would be directly useful to practitioners and would give the tournament a principled
   disqualification criterion rather than an empirical one.

3. **Structure-preserving parameterization.** Is $q = -\mathcal{K}\mathcal{K}^*\partial_x T$ (which
   guarantees entropy dissipation) expressive enough to represent the exact kernel, exactly or to
   what accuracy? A positive answer would be a genuinely useful result: entropy-dissipative learned
   closures by construction, with an approximation guarantee.

4. **Memory.** Is an instantaneous-in-time closure adequate at moderate $\varepsilon$, or is a
   time-nonlocal kernel required? Mori–Zwanzig gives the framing; the LB structure may let us
   estimate the memory kernel's decay explicitly and thereby predict when Markovian closures must
   fail. This has a direct experimental counterpart in the tournament: submissions with and without
   persistent state.

5. **Variable coefficients.** The exact kernel is a convolution only about a uniform background. In
   a real profile the local Knudsen number varies, and the operator becomes a genuine
   variable-coefficient pseudodifferential operator. This is where simple kernel closures break down,
   and where neural operators might plausibly earn their complexity. Approximation rates for such
   operators are, as far as I know, open in the relevant class.

6. **Relation to Chapman–Enskog divergence.** The Burnett and super-Burnett equations are unstable
   (Bobylev). Learned closures at moderate $\varepsilon$ are, implicitly, trying to do what the
   divergent CE series cannot. Is there a resummation interpretation? Does the exact kernel's symbol
   have the branch structure that would explain the divergence?

---

## 8. Proposed division and next steps

Suggested first four steps, none of which requires committing to the full program:

1. **Derive $\hat\kappa(k\lambda)$ analytically** and verify it against the Haack code's linear
   response. This alone is a short, self-contained result, and it is the foundation for everything
   downstream. (Math side leads.)
2. **Build the T0–T2 harness** with two baselines (local CE-LB, flux limiter) and confirm the
   numbers against the analytic symbol. (Simulation side leads.)
3. **Fix and publish the nondimensionalization and the submission interface** before recruiting
   anyone. Interface churn kills these efforts.
4. **Pilot with two or three internally built closures** — a learned convolution kernel, an FNO, and
   an SNB-analogue — to shake out the harness before opening submissions.

Open questions I would like your view on: whether the primary track should be 1D1V or 1D3V (1D3V is
more faithful and the Hermite structure survives, but the data volume for training sets grows);
whether the a posteriori track should use a differentiable solver from the start, since that decides
whether adversarial search and end-to-end training are available to entrants; and whether the
Prandtl number and $\kappa$ coefficients above match your own derivation.