"""Sanity tests. Run before the full computation: python -m unittest -v test_electron_numerics.py"""
import unittest
import numpy as np
import electron_numerics as en

D = 6


class Shared(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        _, cls.Lee, cls.landau_check = en.landau_matrix(D)
        cls.M, cls.lorentz_check = en.lorentz_matrix(D)
        cls.vecs = en.vecs(D)


class LorentzMatrix(Shared):
    def test_normalization_symmetry_kernel(self):
        B, ix, one, vx, E2, th, Q, Vx = self.vecs
        self.assertAlmostEqual(self.lorentz_check, np.sqrt(2/np.pi), places=12)
        self.assertLess(np.abs(self.M-self.M.T).max(), 1e-12)
        self.assertLess(np.abs(self.M@one).max(), 1e-12)
        self.assertLess(np.abs(self.M@E2).max(), 1e-11)
        self.assertGreater(np.linalg.eigvalsh(self.M).min(), -1e-12)

    def test_exact_momentum_loss_rate(self):
        B, ix, one, vx, E2, th, Q, Vx = self.vecs
        self.assertAlmostEqual(vx@self.M@vx, 2/3*np.sqrt(2/np.pi), places=12)
        for Z in (1, 7):
            L = en.electron_operator(0*self.Lee, self.M, Z)
            self.assertAlmostEqual(vx@L@vx, 1/en.tau_e(Z), places=11)

    def test_braginskii_degree_six(self):
        # Degree 6 spans the Sonine polynomials used by Braginskii for Z = 1.
        c = en.transport(en.electron_operator(self.Lee, self.M, 1), D, False)
        self.assertAlmostEqual(c['kappa']/en.tau_e(1), 3.1616, places=3)
        self.assertAlmostEqual(c['L11']/en.tau_e(1), 1/0.5129, places=3)


class ThermalResponse(Shared):
    def operators(self):
        yield 'landau', self.Lee, True
        yield 'dougherty', en.dougherty(D), True
        for Z in (1, 16):
            yield f'electron Z={Z}', en.electron_operator(self.Lee, self.M, Z), False

    def test_bounds_and_moment_identities(self):
        for name, L, conserving in self.operators():
            c = en.transport(L, D, conserving)
            self.assertLess(c['source_residual'], 1e-9, name)
            self.assertLess(c['current_residual'], 1e-9, name)
            for k in (0.01, 0.1, 1.0, 5.0):
                r = en.thermal_response(L, D, k)
                self.assertLess(r['flux_residual'], 1e-8/k, name)
                self.assertLess(r['current_residual'], 1e-9, name)
                self.assertLessEqual(r['chi'], c['kappa']*(1+1e-10), name)
                self.assertGreaterEqual(r['chi'], c['kappa']/(1+c['K']*k*k)*(1-1e-10), name)

    def test_leading_coefficient(self):
        for name, L, conserving in self.operators():
            c = en.transport(L, D, conserving)
            # K k^2 = 1e-4: small enough for the O(k^4) remainder, large enough
            # that the subtraction 1 - chi/kappa is not dominated by round-off.
            k = 1e-2/np.sqrt(c['K'])
            deficit = 1-en.thermal_response(L, D, k)['chi']/c['kappa']
            self.assertAlmostEqual(deficit/(c['K']*k*k), 1, places=2, msg=name)

    def test_matrix_reproduces_both_drives(self):
        for k in (0.05, 0.7):
            Mk = en.anisotropic_matrix(self.Lee, D, k)
            self.assertAlmostEqual(Mk[0, 1], Mk[1, 0], places=10)
            self.assertGreater(np.linalg.eigvalsh((Mk+Mk.T)/2).min(), 0)
            pot, thermal = en.responses_from_matrix(Mk, k)
            self.assertAlmostEqual(pot, en.theta(self.Lee, D, k)[0]/k, places=9)
            self.assertAlmostEqual(thermal, en.thermal_response(self.Lee, D, k)['chi'], places=9)


class DoughertyClosedForm(unittest.TestCase):
    def test_constants(self):
        c = en.transport(en.dougherty(8), 8, True)
        self.assertAlmostEqual(c['kappa'], 5/6, places=12)
        self.assertAlmostEqual(c['K'], 16/45, places=12)

    def test_formula_against_galerkin_and_limits(self):
        d = 16
        L = en.dougherty(d)
        for k in (0.1, 0.5):
            self.assertAlmostEqual(en.dougherty_thermal_theta(k)/k,
                                   en.thermal_response(L, d, k)['chi'], places=6)
        k = 1e-2
        self.assertAlmostEqual((1-en.dougherty_thermal_theta(k)/k/(5/6))/k**2, 16/45, places=3)
        self.assertAlmostEqual(en.dougherty_thermal_theta(300.0), 1.8*np.sqrt(2/np.pi), places=2)


class EmbeddedModel(Shared):
    def test_zero_current_invariants(self):
        L = en.electron_operator(self.Lee, self.M, 1)
        times = np.linspace(0, 40, 81)
        r = en.zero_current_rollout(L, D, 0.3, times)
        self.assertAlmostEqual(r['T'][0].real, 1)
        self.assertLess(np.abs(r['n']).max(), 1e-10)
        self.assertLess(np.abs(r['u']).max(), 1e-10)
        self.assertLess(np.diff(r['energy']).max(), 1e-12)

    def test_closed_model_matches_kinetics_at_small_k(self):
        L = en.electron_operator(self.Lee, self.M, 1)
        k = 0.01
        chi = en.thermal_response(L, D, k)['chi']
        times = np.linspace(0, 4/(2/3*k*k*chi), 201)
        ref = en.zero_current_rollout(L, D, k, times)['T']
        self.assertLess(en.relative_history_error(en.temperature_decay(k, chi, times), ref, times), 2e-2)
        slow, _ = en.slowest_mode_chi(L, D, k)
        self.assertAlmostEqual(slow/chi, 1, places=2)


if __name__ == '__main__':
    unittest.main()
