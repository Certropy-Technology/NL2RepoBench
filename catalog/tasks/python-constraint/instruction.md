# Project Description

Build an installable Python distribution named `python-constraint2` that exposes
the import package `constraint`. The library solves finite-domain constraint
satisfaction problems: callers define variables and candidate values, attach
callable, string, or predefined constraints, choose a solver, and request one
or all satisfying assignments.

The implementation must support mutable domain state for forward checking,
deterministic backtracking solvers, a stochastic minimum-conflicts solver, an
experimental parallel solver, numeric and set-membership constraints, and the
public string-constraint parser. This is a library API; no command-line program
is required.

# Supports

- Python 3.11 or newer.
- Distribution name `python-constraint2`, version `2.7.3`.
- Top-level imports through `constraint` and direct imports from
  `constraint.domain`, `constraint.problem`, `constraint.constraints`,
  `constraint.solvers`, and `constraint.parser`.
- No third-party runtime dependencies. Build-time acceleration with Cython is
  optional, but pure-Python and compiled forms expose the same behavior.
- A standards-compliant `pyproject.toml`, BSD-2-Clause license metadata, and a
  package installable with `pip`.

# API Usage Guide

## Variables and domains

```python
Variable(name)
Domain(values)
domain.resetState()
domain.pushState()
domain.popState()
domain.hideValue(value)
check_if_compiled() -> bool
```

`Variable` wraps a name; string names are returned by `repr`. Plain hashable
objects may also serve as problem variables. The module exports an `Unassigned`
sentinel for partial constraint evaluation.

`Domain` is list-like. `pushState()` records the visible state, `hideValue()`
temporarily removes a visible value, `popState()` restores values hidden since
the matching push, and `resetState()` restores all hidden values and clears the
state stack. Normal list errors apply to a missing value or missing saved state.
`check_if_compiled()` reports whether Cython-compiled modules are active.

## Problems

```python
Problem(solver=None)
problem.reset()
problem.setSolver(solver)
problem.getSolver()
problem.addVariable(variable, domain)
problem.addVariables(variables, domain)
problem.addConstraint(constraint, variables=None)
problem.getSolution()
problem.getSolutions()
problem.getSolutionIter()
problem.getSolutionsOrderedList(order=None)
problem.getSolutionsAsListDict(order=None, validate=True)
```

The default solver is `OptimizedBacktrackingSolver`. Domain inputs are copied,
so search pruning does not alter the caller's domain. Duplicate variables and
empty domains raise `ValueError`; unsupported domains raise `TypeError`.

`addConstraint()` accepts a `Constraint`, a callable wrapped as
`FunctionConstraint`, one string expression, or a list of string expressions.
String expressions infer referenced variables. An omitted `variables` argument
applies an object or callable constraint to all variables; explicit variable
order determines positional callable arguments.

`getSolution()` returns one assignment dictionary or `None`; `getSolutions()`
returns all assignment dictionaries; empty or unsatisfiable problems yield no
solutions. `getSolutionIter()` is lazy when supported by the solver.
`getSolutionsOrderedList()` converts assignments to tuples in a requested key
order. `getSolutionsAsListDict()` returns `(solution_tuples, index_map, size)`
and, by default, rejects duplicate tuples.

For deterministic domains and constraints, backtracking traversal is stable:

```python
from constraint import AllDifferentConstraint, Problem

problem = Problem()
problem.addVariables(["a", "b"], [1, 2, 3])
problem.addConstraint(AllDifferentConstraint())
assert problem.getSolutions() == [
    {"a": 3, "b": 2}, {"a": 3, "b": 1},
    {"a": 2, "b": 3}, {"a": 2, "b": 1},
    {"a": 1, "b": 2}, {"a": 1, "b": 3},
]
```

## Solvers

```python
BacktrackingSolver(forwardcheck=True)
OptimizedBacktrackingSolver(forwardcheck=True)
RecursiveBacktrackingSolver(forwardcheck=True)
MinConflictsSolver(steps=1000, rand=None)
ParallelSolver(process_mode=False)
```

All derive from `Solver`; unimplemented base operations raise
`NotImplementedError`. The three backtracking solvers return equivalent
solution sets and honor forward checking. `BacktrackingSolver` also supports
lazy iteration. `OptimizedBacktrackingSolver` is the default.

`MinConflictsSolver` returns at most one solution, performs at most `steps`
repair attempts, and accepts a random-compatible object through `rand`; asking
it for all solutions is unsupported. `ParallelSolver` computes all solutions
with threads or, with `process_mode=True`, worker processes. It does not support
single-solution or iterator calls. Process mode accepts picklable,
string-derived constraints and rejects callable `FunctionConstraint` objects.

## Constraint protocol

```python
constraint(variables, domains, assignments, forwardcheck=False) -> bool
constraint.preProcess(variables, domains, constraints, vconstraints)
constraint.forwardCheck(variables, domains, assignments) -> bool
FunctionConstraint(func, assigned=True)
CompilableFunctionConstraint(func: str, assigned=True)
```

A `Constraint` reports whether a complete or partial assignment can still
succeed. Forward checking may hide impossible values and fails when a domain is
emptied. `preProcess()` may prune domains before search. Subclasses may override
this protocol. `FunctionConstraint` invokes its callable in variable order;
when `assigned=False`, missing values use `Unassigned`.
`CompilableFunctionConstraint` carries equivalent expression text for process
workers.

The predefined numeric constraints are:

```python
AllDifferentConstraint()
AllEqualConstraint()
ExactSumConstraint(exactsum, multipliers=None)
MinSumConstraint(minsum, multipliers=None)
MaxSumConstraint(maxsum, multipliers=None)
VariableExactSumConstraint(target_var, sum_vars, multipliers=None)
VariableMinSumConstraint(target_var, sum_vars, multipliers=None)
VariableMaxSumConstraint(target_var, sum_vars, multipliers=None)
ExactProdConstraint(exactprod)
MinProdConstraint(minprod)
MaxProdConstraint(maxprod)
VariableExactProdConstraint(target_var, product_vars)
VariableMinProdConstraint(target_var, product_vars)
VariableMaxProdConstraint(target_var, product_vars)
```

Constant variants compare a fixed exact/minimum/maximum bound. Variable
variants compare a named target with the sum or product of named source
variables. Sum multipliers scale values positionally. Partial assignments prune
only when remaining values cannot satisfy the bound. Negative values and mixed
integer/float values are supported.

Set constraints are:

```python
InSetConstraint(values)
NotInSetConstraint(values)
SomeInSetConstraint(values, n=1, exact=False)
SomeNotInSetConstraint(values, n=1, exact=False)
```

The first pair requires every value to be inside or outside the set. The latter
pair requires at least `n` matching values, or exactly `n` when `exact=True`,
and applies the same rule during forward checking.

## String constraints and parser helpers

```python
parse_restrictions(restrictions: list[str], tune_params: dict)
compile_to_constraints(constraints: list[str], domains: dict, picklable=False)
is_or_evals_to_number(text: str) -> int | float | None
extract_operators(expression: str) -> list[str]
```

String constraints use Python-style names, comparisons, Boolean operators,
arithmetic, and chained comparisons. `parse_restrictions()` returns ordered
`(restriction, variables)` pairs, specializing recognized sum/product bounds
and retaining unsupported forms as expressions. `compile_to_constraints()`
returns `(constraint, variables, source)` triples; `source` is retained for
callable-style constraints and is `None` for specialized objects. With
`picklable=True`, fallback expressions become process-safe compilable
constraints.

Strict inequalities retain strict boundaries. A chain such as
`50 <= x * y < 100` becomes two constraints in source order.
`is_or_evals_to_number()` evaluates real constant arithmetic and returns `None`
for names, strings, complex values, or invalid expressions.
`extract_operators()` returns binary arithmetic operators left-to-right while
ignoring unary signs.

# Implementation Notes

- Re-export the public classes, functions, and sentinel from `constraint`.
- Preserve and fully restore nested domain states during backtracking.
- Do not mutate caller-provided domains or variable sequences.
- Repeated solves must not duplicate deferred string constraints or solutions.
- Parallel process workers must use picklable state and preserve the sequential
  solver's solution set.
- Keep all behavior available when optional compiled extensions are absent.
