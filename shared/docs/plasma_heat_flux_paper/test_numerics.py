"""Physics checks, independent representations, and an embedded smoke test."""
import unittest
import numpy as np
from numerics import (bgk_constants, bgk_theta, variable_bgk_theta,
                      dougherty_theta, hermite_response, constants, dougherty,
                      kinetic_rollout, moment_rollout)

class ClosureChecks(unittest.TestCase):
    def test_bgk_normalization_and_independent_resolvent(self):
        c = bgk_constants()
        self.assertAlmostEqual(c['kappa'], 1.5, places=11)
        self.assertAlmostEqual(c['K'], 4.0, places=10)
        for k in (0.1,1,3):
            self.assertAlmostEqual(bgk_theta(k), variable_bgk_theta(k, False)[0], places=9)

    def test_dougherty_limits_and_independent_hermite(self):
        for k in (0.1,1,3):
            self.assertAlmostEqual(dougherty_theta(k), hermite_response(k,100), places=9)
        for dim,kappa,K,lim in ((1,.5,1/3,np.sqrt(2/np.pi)),
                                (3,5/6,2/15,3*np.sqrt(2/np.pi))):
            k=.01
            self.assertAlmostEqual((1-dougherty_theta(k,dim)/k/kappa)/k**2,K,places=4)
            self.assertLess(abs(dougherty_theta(1e4,dim)-lim)/lim,2e-4)

    def test_3d_transport_invariants(self):
        L=dougherty(10)
        c=constants(L,10)
        self.assertLess(c['kern'],1e-12)
        self.assertGreater(c['mineig'],-1e-12)
        self.assertAlmostEqual(c['kF'],5/6,places=10)
        self.assertAlmostEqual(c['eta'],.5,places=10)
        self.assertAlmostEqual(c['Kexact'],2/15,places=10)

    def test_embedded_entropy_and_unresolved_initial_flux(self):
        times=np.linspace(0,10,101)
        U,E,q=kinetic_rollout(1,64,times)
        V,F=moment_rollout(1,dougherty_theta(1),times)
        self.assertTrue(np.all(np.diff(E)<1e-12))
        self.assertTrue(np.all(np.diff(F)<1e-12))
        self.assertLess(np.max(abs(U[0]-[0,0,1])),1e-12)
        self.assertEqual(q[0],0)
        self.assertGreater(abs(-1j*dougherty_theta(1)*V[0,2]-q[0]),.3)

if __name__=='__main__':
    unittest.main()
