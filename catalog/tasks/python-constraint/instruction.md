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

# Supports

- Python 3.11 or newer; the Harbor image uses CPython 3.12.14.
- Distribution name `python-constraint2`, version `2.7.3`.
- Top-level imports through `constraint` and direct imports from `constraint.domain`, `constraint.problem`, `constraint.constraints`, `constraint.solvers`, and `constraint.parser`.
- No third-party runtime dependencies. Cython compilation is performed during installation when the build tools are available; pure-Python behavior must remain available.
- A standards-compliant `pyproject.toml` and BSD-2-Clause license metadata.

# API Usage Guide

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
