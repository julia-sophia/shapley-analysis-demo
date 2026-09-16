"""Exact Shapley values for small, precedence-constrained cooperative games.

This module is deliberately independent of the work application from which the
idea arose. A caller supplies a value function for each coalition of players;
the module attributes the change from the empty coalition to the full coalition.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping, Sequence
from dataclasses import dataclass
from itertools import combinations
import math


Coalition = frozenset[str]
ValueFunction = Callable[[Coalition], float]
Constraint = tuple[str, str]


class ShapleyError(ValueError):
    """Raised when the players or precedence constraints are invalid."""


@dataclass(frozen=True)
class ShapleyResult:
    """The calculated attribution, plus intermediate values useful for audit."""

    values: Mapping[str, float]
    coalition_values: Mapping[Coalition, float]
    feasible_coalitions: int
    valid_orderings: int

    @property
    def baseline(self) -> float:
        return self.coalition_values[frozenset()]

    @property
    def full_case(self) -> float:
        return self.coalition_values[max(self.coalition_values, key=len)]

    @property
    def total_change(self) -> float:
        return self.full_case - self.baseline

    @property
    def reconciliation_error(self) -> float:
        """Zero (up to floating-point rounding) when the attribution reconciles."""

        return sum(self.values.values()) - self.total_change


def _validate_players(players: Sequence[str]) -> tuple[str, ...]:
    players = tuple(players)
    if not players:
        raise ShapleyError("At least one player is required.")
    if any(not isinstance(player, str) or not player.strip() for player in players):
        raise ShapleyError("Each player must be a non-empty string.")
    if len(set(players)) != len(players):
        raise ShapleyError("Player names must be unique.")
    return players


def predecessor_map(
    players: Sequence[str], constraints: Iterable[Constraint] = ()
) -> dict[str, frozenset[str]]:
    """Return each player's direct prerequisites and reject cyclic graphs.

    A constraint ``(before, after)`` says that ``before`` must occur earlier in
    a valid ordering. The result is an adjacency representation of incoming
    edges in a directed acyclic graph.
    """

    player_names = _validate_players(players)
    known = set(player_names)
    predecessors: dict[str, set[str]] = {player: set() for player in player_names}
    for before, after in constraints:
        if before not in known or after not in known:
            raise ShapleyError("Every constraint must name two known players.")
        if before == after:
            raise ShapleyError("A player cannot be its own prerequisite.")
        predecessors[after].add(before)

    # Depth-first search detects a back edge, so cycles fail early and clearly.
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(player: str) -> None:
        if player in visiting:
            raise ShapleyError("Precedence constraints contain a cycle.")
        if player in visited:
            return
        visiting.add(player)
        for prerequisite in predecessors[player]:
            visit(prerequisite)
        visiting.remove(player)
        visited.add(player)

    for player in player_names:
        visit(player)
    return {player: frozenset(items) for player, items in predecessors.items()}


def feasible_coalitions(
    players: Sequence[str], predecessors: Mapping[str, frozenset[str]]
) -> tuple[Coalition, ...]:
    """Enumerate subsets closed under their prerequisite relation.

    Without constraints every subset is feasible, giving ``2**n`` states. With
    constraints, a coalition is feasible only when it includes the prerequisites
    of each of its members.
    """

    result: list[Coalition] = []
    for size in range(len(players) + 1):
        for combination in combinations(players, size):
            coalition = frozenset(combination)
            if all(predecessors[player] <= coalition for player in coalition):
                result.append(coalition)
    return tuple(result)


def _available_additions(
    coalition: Coalition,
    players: Sequence[str],
    predecessors: Mapping[str, frozenset[str]],
) -> tuple[str, ...]:
    """Players that can legally be added to this coalition next."""

    return tuple(
        player
        for player in players
        if player not in coalition and predecessors[player] <= coalition
    )


def _ordering_counts(
    coalitions: Sequence[Coalition],
    players: Sequence[str],
    predecessors: Mapping[str, frozenset[str]],
) -> tuple[dict[Coalition, int], dict[Coalition, int]]:
    """Count valid paths to and from every feasible coalition using dynamic programming."""

    empty = frozenset()
    full = frozenset(players)
    ways_to: dict[Coalition, int] = {empty: 1}
    for coalition in coalitions:
        count = ways_to.get(coalition, 0)
        for player in _available_additions(coalition, players, predecessors):
            successor = coalition | {player}
            ways_to[successor] = ways_to.get(successor, 0) + count

    ways_from: dict[Coalition, int] = {full: 1}
    for coalition in reversed(coalitions):
        if coalition == full:
            continue
        ways_from[coalition] = sum(
            ways_from[coalition | {player}]
            for player in _available_additions(coalition, players, predecessors)
        )
    return ways_to, ways_from


def exact_shapley(
    players: Sequence[str],
    value: ValueFunction,
    constraints: Iterable[Constraint] = (),
) -> ShapleyResult:
    """Calculate exact Shapley values by averaging marginal contributions.

    Each valid player ordering gives one path from the empty coalition to the
    full coalition. For a transition ``S -> S union {i}``, the number of valid
    orderings that use it is ``ways_to[S] * ways_from[S union {i}]``. Dividing
    by the total ordering count gives its exact probability, avoiding explicit
    enumeration of all permutations.
    """

    player_names = _validate_players(players)
    predecessors = predecessor_map(player_names, constraints)
    coalitions = feasible_coalitions(player_names, predecessors)
    values_by_coalition: dict[Coalition, float] = {}
    for coalition in coalitions:
        result = value(coalition)
        if isinstance(result, bool) or not isinstance(result, (int, float)):
            raise ShapleyError("The value function must return a real number.")
        if not math.isfinite(float(result)):
            raise ShapleyError("The value function returned a non-finite number.")
        values_by_coalition[coalition] = float(result)

    ways_to, ways_from = _ordering_counts(coalitions, player_names, predecessors)
    ordering_total = ways_to[frozenset(player_names)]
    contributions = {player: 0.0 for player in player_names}
    for coalition in coalitions:
        for player in _available_additions(coalition, player_names, predecessors):
            successor = coalition | {player}
            probability = ways_to[coalition] * ways_from[successor] / ordering_total
            marginal_value = values_by_coalition[successor] - values_by_coalition[coalition]
            contributions[player] += probability * marginal_value

    return ShapleyResult(
        values=contributions,
        coalition_values=values_by_coalition,
        feasible_coalitions=len(coalitions),
        valid_orderings=ordering_total,
    )
