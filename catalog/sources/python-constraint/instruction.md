# Project Description

Build an installable Python distribution named `python-constraint2` (version
`2.7.3`) that exposes the import package `constraint`. It solves finite-domain
constraint-satisfaction problems with deterministic backtracking, numeric and
set constraints, string constraints, and the public solver/parser APIs.

This task measures the versioned **scenario-adapter v1** contract below. The
adapter runs in an untrusted child process and constructs all callable,
stateful, generator, and solver objects locally from fixed scenario names. Do
not send Python source, callbacks, pickles, object handles, or executable code
through JSON.

## Natural Language Instruction

Create an installable `python-constraint2` project from an empty workspace,
exposing the import package `constraint`. Implement finite-domain variables,
stateful domains, problems, solver families, numeric/set constraints, string
constraints, and parser helpers with the deterministic behavior specified below.
Preserve public imports and caller-owned state without network or external
services.

# Supports

- Python 3.11 or newer; the Harbor image uses CPython 3.12.14.
- Distribution name `python-constraint2`, version `2.7.3`.
- Top-level imports through `constraint` and direct imports from `constraint.domain`, `constraint.problem`, `constraint.constraints`, `constraint.solvers`, and `constraint.parser`.
- No third-party runtime dependencies. Cython compilation is performed during installation when the build tools are available; pure-Python behavior must remain available.
- A standards-compliant `pyproject.toml` and BSD-2-Clause license metadata.

## Project Directory Structure

```text
workspace/
├── pyproject.toml
├── LICENSE
└── constraint/
    ├── __init__.py
    ├── domain.py
    ├── problem.py
    ├── constraints.py
    ├── solvers.py
    └── parser.py
```

The package root is `constraint`; the modules above correspond to the direct
imports in the API guide. Install from `workspace/` without an upstream
checkout or evaluator-only file.

## API Usage Guide

Implement the public `Variable`, `Domain`, `Problem`, `Constraint`,
`FunctionConstraint`, `CompilableFunctionConstraint`, the backtracking solver
classes, `MinConflictsSolver`, `ParallelSolver`, all documented numeric and set
constraints, and parser helpers listed in this section.

## Stateful domains and problems

`Domain(values)` is list-like. `pushState()` saves the visible domain,
`hideValue(value)` temporarily removes a value, `popState()` restores values
hidden since the matching push, and `resetState()` restores all values and
clears the stack. `Problem.addVariable` copies domains, preserves a supplied
`Domain` subclass, and rejects duplicate variables and empty domains.

`Problem.addConstraint` accepts a `Constraint`, a callable wrapped as a
`FunctionConstraint`, one string expression, or a list of string expressions.
`getSolution()` returns one assignment or `None`; `getSolutions()` returns all
assignments; `getSolutionIter()` is lazy; ordered-list helpers preserve the
requested key order and duplicate validation behavior.

## Solvers and constraints

`BacktrackingSolver`, `OptimizedBacktrackingSolver`, and
`RecursiveBacktrackingSolver` must honor forward checking and return equivalent
solution sets. `MinConflictsSolver(steps=..., rand=...)` returns at most one
solution and is deterministic when supplied a seeded random-compatible object.
`ParallelSolver(process_mode=False)` computes all solutions with threads. With
`process_mode=True`, it accepts picklable string-derived constraints and rejects
callable `FunctionConstraint` objects; single-solution and iterator calls are
unsupported.

Provide `AllDifferentConstraint`, `AllEqualConstraint`, exact/min/max sum and
product constraints, variable-target sum/product constraints, and
`InSetConstraint`, `NotInSetConstraint`, `SomeInSetConstraint`, and
`SomeNotInSetConstraint`. Partial assignments and forward checking must reject
impossible domains without mutating caller-owned domain objects.

`parse_restrictions`, `compile_to_constraints`, `is_or_evals_to_number`, and
`extract_operators` parse Python-style arithmetic/comparison expressions,
recognize supported specialized numeric constraints, preserve strict bounds,
and support `picklable=True` fallback constraints.

Import the public surface from the installed package:

```python
from constraint import Problem, Domain, AllDifferentConstraint
from constraint.parser import parse_restrictions
```

## Implementation Notes

Keep solver results deterministic for equivalent inputs and preserve requested
variable order in ordered helper methods. Domain state stacks must be balanced
when a constraint rejects a partial assignment. Construct callable and solver
objects inside the local package process rather than serializing them.

## Examples

```python
problem = Problem()
problem.addVariable("x", [1, 2])
problem.addVariable("y", [1, 2])
problem.addConstraint(AllDifferentConstraint(), ("x", "y"))
print(problem.getSolutions())
```

```python
domain = Domain(["red", "blue"])
domain.pushState()
domain.hideValue("red")
domain.popState()
assert list(domain) == ["red", "blue"]
```

## Error Handling and Boundary Conditions

Reject duplicate variables, empty domains, malformed expressions, and
unsupported process-mode callable constraints with the documented exception
types. Unsatisfiable and empty problems return their specified empty forms;
repeated solves do not leak domain mutations.

# Frozen scenario leaves

The private verifier collects exactly 16 leaves, all named by this allowlist:

- `domain-nested-state`
- `problem-domain-copy`
- `callable-order-and-generator`
- `custom-constraint-forward-check`
- `backtracking-family-equivalence`
- `string-constraint-solve`
- `numeric-and-set-constraints`
- `parser-specialization`
- `parser-operator-helpers`
- `lazy-solution-iterator`
- `min-conflicts-seeded`
- `parallel-thread-solutions`
- `parallel-process-string-solutions`
- `parallel-process-callable-rejection`
- `unsatisfiable-and-empty-problems`
- `repeated-solves-stable`

Each scenario is constructed and asserted wholly inside the child adapter.
The trusted verifier compares only the child verdict to its expected outcome;
no candidate object is imported by the trusted verifier. The adapter bounds each
scenario to finite domains, at most 256 solutions, and a 20-second child
budget. The 16-leaf denominator is a deliberate v0.2.0 rescope from the old
52-node upstream collection: upstream packaging metadata, examples, README
 doctests, compiled-extension benchmark timing, and direct multiprocessing
fixtures are not included because those repository fixtures are not exposed by
this install-only public contract. Their exclusion is recorded in the source
lifecycle and does not delete an assertion from the retained scenario leaves.
