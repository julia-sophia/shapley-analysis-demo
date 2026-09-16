# Exact Shapley Value Algorithm: a self-contained Python example

This is a compact, standalone version of a Python tool I developed to explain
how a collection of independent business drivers contributes to a combined
result. It contains no confidential data, spreadsheet automation, graphical
interface, or third-party dependency. The example uses a fictional project
portfolio instead.

The code is intended as evidence of Python and algorithmic programming
experience. The main implementation is [`src/shapley.py`](src/shapley.py); it
uses standard-library data structures and is designed to be read alongside the
example and tests.

## What the algorithm does

The Shapley value is a fair way to divide a total change among interacting
contributors. A contributor's value is its average *marginal* effect across all
valid orders in which contributors can be introduced. This matters when, for
example, the combined effect of two projects is larger than the sum of their
separate effects.

The implementation supports precedence constraints such as `Research before
Prototype`. It represents a coalition as an immutable `frozenset` and the
constraints as a directed graph of prerequisites. It then:

1. Enumerates feasible coalitions (subsets that contain each member's
   prerequisites).
2. Evaluates the supplied value function once for every feasible coalition.
3. Uses dynamic programming to count valid paths to and from each coalition.
4. Weights each transition by the proportion of valid orderings that use it,
   and sums its marginal contribution for each player.

This is exact: it does not sample or approximate any ordering. The number of
states can grow exponentially, so this form is best suited to modest numbers of
players. The dynamic-programming count avoids separately generating every valid
permutation.

## Run the example

Requires Python 3.10 or later. There are no packages to install.

```powershell
python examples/project_selection.py
```

The expected console output is saved in
[`examples/project_selection_output.txt`](examples/project_selection_output.txt).
The fictional example has three players. `Research` must come before both
`Prototype` and `Launch`, leaving two valid orders. The interaction bonus between
`Prototype` and `Launch` is shared through the Shapley calculation.

## Run the tests

```powershell
python -m unittest discover -s tests -v
```

The tests cover additive effects, sharing of an interaction, constrained
ordering counts, and detection of a cyclic dependency.

## Files to review

- [`src/shapley.py`](src/shapley.py) — the exact algorithm and validation.
- [`examples/project_selection.py`](examples/project_selection.py) — a small,
  fictional input model.
- [`examples/project_selection_output.txt`](examples/project_selection_output.txt)
  — reproducible output from the example.
- [`tests/test_shapley.py`](tests/test_shapley.py) — automated checks of the
  principal behaviours.
