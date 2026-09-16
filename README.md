# Shapley Analysis: Demo Version

This is a compact, standalone "demo" version of a Python tool I developed at work (not publically available) to mathematically disaggregate the relative contributions of several independent variables to a combined result (whether commercial or technical).
To keep the codebase clean and avoid IP issues, I used a trivial/toy project portfolio and dropped support for Excel input in this demo version.

The main implementation is [`src/shapley.py`](src/shapley.py), however this should be read alongside the example (program and output) as well as the tests.

## What the algorithm does

The [Shapley value](https://en.wikipedia.org/wiki/Shapley_value) is a fair way to divide a total gain among a group of contributors. A contributor's value is its average *marginal* effect across all valid orderings in which contributors can be introduced. This matters when, for example, the combined effect of two projects (contributors) is larger than the sum of their separate effects (in non-zero-sum games, i.e. most real-world economic situations!)

The implementation supports precedence constraints such as `Research before
Prototype`. It represents a coalition as an immutable `frozenset` and the
constraints as a directed graph of prerequisites. It then:

1. Enumerates feasible coalitions (subsets that contain each member's
   prerequisites).
2. Evaluates the supplied value function once for every feasible coalition.
3. Uses dynamic programming to count valid paths to and from each coalition.
4. Weights each transition by the proportion of valid orderings that use it,
   and sums its marginal contribution for each player.

As it does not sample or approximate any ordering, the number of
states can grow exponentially, so this calculation is best suited to modest numbers of
players. The "dynamic-programming" count avoids separately generating every valid
permutation (by calculating the relative frequency of permutations given a specific combination.) 

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
