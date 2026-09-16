from __future__ import annotations

from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from shapley import ShapleyError, exact_shapley  # noqa: E402


class ExactShapleyTests(unittest.TestCase):
    def test_additive_game_returns_each_direct_effect(self):
        effects = {"A": 1.5, "B": -2.0, "C": 4.25}
        result = exact_shapley(
            tuple(effects), lambda coalition: 10 + sum(effects[p] for p in coalition)
        )
        for player, expected in effects.items():
            self.assertAlmostEqual(result.values[player], expected)
        self.assertEqual(result.valid_orderings, 6)
        self.assertAlmostEqual(result.reconciliation_error, 0.0)

    def test_interaction_is_shared_equally_without_constraints(self):
        result = exact_shapley(
            ("Prototype", "Launch"),
            lambda coalition: 10.0 if len(coalition) == 2 else 0.0,
        )
        self.assertEqual(result.values, {"Prototype": 5.0, "Launch": 5.0})

    def test_precedence_counts_only_valid_orderings(self):
        result = exact_shapley(
            ("Research", "Prototype", "Launch"),
            lambda coalition: float(len(coalition)),
            (("Research", "Prototype"), ("Research", "Launch")),
        )
        self.assertEqual(result.feasible_coalitions, 5)
        self.assertEqual(result.valid_orderings, 2)
        self.assertEqual(result.values, {"Research": 1.0, "Prototype": 1.0, "Launch": 1.0})

    def test_cycle_is_rejected(self):
        with self.assertRaisesRegex(ShapleyError, "cycle"):
            exact_shapley(("A", "B"), lambda _: 0.0, (("A", "B"), ("B", "A")))


if __name__ == "__main__":
    unittest.main()
