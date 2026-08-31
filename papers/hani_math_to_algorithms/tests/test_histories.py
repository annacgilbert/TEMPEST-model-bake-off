import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from hani_closure.histories import CollisionEvent, InteractionHistory


class InteractionHistoryTests(unittest.TestCase):
    def test_triangle_history_has_one_cycle(self) -> None:
        history = InteractionHistory(
            [
                CollisionEvent(0, 0.0, 0, 1, 0),
                CollisionEvent(1, 0.5, 1, 2, 0),
                CollisionEvent(2, 1.0, 2, 0, 1),
            ]
        )
        self.assertEqual(history.component_count(), 1)
        self.assertEqual(history.circuit_rank(), 1)
        self.assertEqual(history.long_bond_count(0.75), 1)

    def test_repeated_pair_is_counted_as_recollision_proxy(self) -> None:
        history = InteractionHistory(
            [
                CollisionEvent(0, 0.0, 0, 1, 0),
                CollisionEvent(1, 1.0, 0, 1, 1),
            ]
        )
        self.assertEqual(history.repeated_pair_recollisions(), 1)

    def test_duplicate_event_id_is_rejected(self) -> None:
        history = InteractionHistory([CollisionEvent(0, 0.0, 0, 1, 0)])
        with self.assertRaises(ValueError):
            history.add(CollisionEvent(0, 1.0, 1, 2, 1))


if __name__ == "__main__":
    unittest.main()

