import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from hani_closure.cumulants import joint_cumulant


class JointCumulantTests(unittest.TestCase):
    def test_first_cumulant_is_mean(self) -> None:
        self.assertEqual(joint_cumulant([[1.0], [3.0]]), 2.0)

    def test_second_cumulant_is_covariance(self) -> None:
        samples = [[-1.0, -1.0], [-1.0, 1.0], [1.0, -1.0], [1.0, 1.0]]
        self.assertAlmostEqual(joint_cumulant(samples), 0.0)

    def test_duplicate_symmetric_variable_has_unit_variance(self) -> None:
        self.assertAlmostEqual(joint_cumulant([[-1.0, -1.0], [1.0, 1.0]]), 1.0)

    def test_higher_cumulant_with_constant_column_vanishes(self) -> None:
        samples = [[-1.0, -1.0, 2.0], [1.0, 1.0, 2.0]]
        self.assertAlmostEqual(joint_cumulant(samples), 0.0)


if __name__ == "__main__":
    unittest.main()

