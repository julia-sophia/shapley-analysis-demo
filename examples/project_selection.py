"""A small, fictional example of exact precedence-constrained attribution."""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from shapley import Coalition, exact_shapley  # noqa: E402


PLAYERS = ("Research", "Prototype", "Launch")
CONSTRAINTS = (("Research", "Prototype"), ("Research", "Launch"))


def portfolio_score(coalition: Coalition) -> float:
    """Return a fictional score for the projects currently in the coalition."""

    score = 100.0
    score += 7.0 if "Research" in coalition else 0.0
    score += 12.0 if "Prototype" in coalition else 0.0
    score += 25.0 if "Launch" in coalition else 0.0
    # This interaction has no natural single owner, so Shapley values share it.
    score += 10.0 if {"Prototype", "Launch"} <= coalition else 0.0
    return score


def display(coalition: Coalition) -> str:
    return ", ".join(player for player in PLAYERS if player in coalition) or "(empty)"


if __name__ == "__main__":
    result = exact_shapley(PLAYERS, portfolio_score, CONSTRAINTS)
    print("Exact precedence-constrained Shapley values")
    print(f"Feasible coalitions: {result.feasible_coalitions}")
    print(f"Valid orderings:     {result.valid_orderings}")
    print("\nCoalition values:")
    for coalition, score in result.coalition_values.items():
        print(f"  {display(coalition):<28} {score:7.2f}")
    print("\nAttribution of the total change:")
    for player, value in result.values.items():
        print(f"  {player:<12} {value:+7.2f}")
    print(f"  {'Total change':<12} {result.total_change:+7.2f}")
    print("\nChecks:")
    print(f"  Baseline score: {result.baseline:.2f}")
    print(f"  Full score:     {result.full_case:.2f}")
    print(f"  Reconciliation error: {result.reconciliation_error:.2e}")
