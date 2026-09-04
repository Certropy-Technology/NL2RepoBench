#!/usr/bin/env python3
"""Untrusted child-side scenario adapter for python-constraint.

Only a scenario token crosses the trusted boundary. Every callable, subclass,
iterator, and solver is built in this process from this fixed allowlist.
"""
from __future__ import annotations

import argparse
import json
import random
import sys
import traceback
from pathlib import Path

MAX_SOLUTIONS = 256


def check(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def solution_set(values):
    check(len(values) <= MAX_SOLUTIONS, "scenario solution bound exceeded")
    return {tuple(sorted(item.items(), key=lambda pair: repr(pair[0]))) for item in values}


def domain_nested_state() -> None:
    from constraint import Domain

    domain = Domain(["a", "b", "c"])
    domain.pushState()
    domain.hideValue("b")
    domain.pushState()
    domain.hideValue("c")
    check(domain == ["a"], "nested hide did not update visible state")
    domain.popState()
    check(domain == ["a", "c"], "inner state was not restored")
    domain.popState()
    check(sorted(domain) == ["a", "b", "c"], "outer state was not restored")
    domain.hideValue("a")
    domain.resetState()
    check(sorted(domain) == ["a", "b", "c"] and not domain._states, "resetState incomplete")


def problem_domain_copy() -> None:
    from constraint import Constraint, Domain, Problem

    class CustomDomain(Domain):
        pass

    class ObservingConstraint(Constraint):
        def __call__(self, variables, domains, assignments, forwardcheck=False):
            check(isinstance(domains["y"], CustomDomain), "domain subclass was not copied")
            return True

    original = CustomDomain([0, 1])
    problem = Problem()
    problem.addVariable("x", [0, 1])
    problem.addVariable("y", original)
    problem.addConstraint(ObservingConstraint())
    solutions = problem.getSolutions()
    check(len(solutions) == 4, "unexpected copied-domain solution count")
    check(original == [0, 1] and not original._hidden, "caller domain was mutated")


def callable_order_and_generator() -> None:
    from constraint import Problem

    seen = []
    problem = Problem()
    problem.addVariables(["a", "b"], [1, 2])

    def ordered(a, b):
        seen.append((a, b))
        return b > a

    problem.addConstraint(ordered, ["a", "b"])
    iterator = problem.getSolutionIter()
    check(iter(iterator) is iterator, "solution iterator is not an iterator")
    values = list(iterator)
    check(values == [{"a": 1, "b": 2}], "callable order or generator result changed")
    check(seen and (1, 2) in seen, "callback did not receive the declared variable order")


def custom_constraint_forward_check() -> None:
    from constraint import Constraint, Problem

    class SuccessorConstraint(Constraint):
        def __call__(self, variables, domains, assignments, forwardcheck=False):
            if len(assignments) == 2:
                return assignments[variables[1]] == assignments[variables[0]] + 1
            if forwardcheck:
                return self.forwardCheck(variables, domains, assignments)
            return True

    problem = Problem()
    problem.addVariables(["x", "y"], [1, 2, 3])
    problem.addConstraint(SuccessorConstraint(), ["x", "y"])
    values = solution_set(problem.getSolutions())
    check(values == {(('x', 1), ('y', 2)), (('x', 2), ('y', 3))}, "forward check result mismatch")


def backtracking_family_equivalence() -> None:
    from constraint import (
        BacktrackingSolver,
        MinSumConstraint,
        OptimizedBacktrackingSolver,
        Problem,
        RecursiveBacktrackingSolver,
    )

    expected = None
    for solver in (BacktrackingSolver(), OptimizedBacktrackingSolver(), RecursiveBacktrackingSolver()):
        problem = Problem(solver)
        problem.addVariables(["x", "y"], [0, 1, 2])
        problem.addConstraint(MinSumConstraint(2), ["x", "y"])
        values = solution_set(problem.getSolutions())
        if expected is None:
            expected = values
        check(values == expected, "backtracking solver families disagree")
    check(expected == {(('x', 0), ('y', 2)), (('x', 1), ('y', 1)), (('x', 2), ('y', 0)), (('x', 1), ('y', 2)), (('x', 2), ('y', 1)), (('x', 2), ('y', 2))}, "family baseline mismatch")


def string_constraint_solve() -> None:
    from constraint import Problem

    problem = Problem()
    problem.addVariables(["x", "y"], [0, 1, 2, 3])
    problem.addConstraint(["x != y", "x + y == 3"])
    check(solution_set(problem.getSolutions()) == {(('x', 0), ('y', 3)), (('x', 1), ('y', 2)), (('x', 2), ('y', 1)), (('x', 3), ('y', 0))}, "string constraint solve mismatch")


def numeric_and_set_constraints() -> None:
    from constraint import (
        ExactProdConstraint,
        ExactSumConstraint,
        InSetConstraint,
        Problem,
        SomeInSetConstraint,
    )

    sum_problem = Problem()
    sum_problem.addVariables(["a", "b"], [1, 2, 3])
    sum_problem.addConstraint(ExactSumConstraint(4), ["a", "b"])
    check(solution_set(sum_problem.getSolutions()) == {(('a', 1), ('b', 3)), (('a', 2), ('b', 2)), (('a', 3), ('b', 1))}, "exact sum mismatch")

    product_problem = Problem()
    product_problem.addVariables(["a", "b"], [1, 2, 3])
    product_problem.addConstraint(ExactProdConstraint(6), ["a", "b"])
    check(solution_set(product_problem.getSolutions()) == {(('a', 2), ('b', 3)), (('a', 3), ('b', 2))}, "exact product mismatch")

    set_problem = Problem()
    set_problem.addVariables(["a", "b", "c"], ["red", "blue", "green"])
    set_problem.addConstraint(SomeInSetConstraint({"red"}, n=2), ["a", "b", "c"])
    set_problem.addConstraint(InSetConstraint({"red", "blue", "green"}), ["a", "b", "c"])
    check(len(set_problem.getSolutions()) == 7, "set constraint count mismatch")


def parser_specialization() -> None:
    from constraint import (
        ExactSumConstraint,
        FunctionConstraint,
        VariableExactSumConstraint,
        compile_to_constraints,
    )

    domains = {"x": [1, 2], "y": [1, 2], "z": [2, 3, 4]}
    exact = compile_to_constraints(["x + y == 3"], domains)[0][0]
    variable = compile_to_constraints(["x + y == z"], domains)[0][0]
    fallback = compile_to_constraints(["x != y"], domains)[0][0]
    check(isinstance(exact, ExactSumConstraint), "constant sum was not specialized")
    check(isinstance(variable, VariableExactSumConstraint), "variable sum was not specialized")
    check(isinstance(fallback, FunctionConstraint), "fallback was not callable")


def parser_operator_helpers() -> None:
    from constraint import extract_operators, is_or_evals_to_number

    check(is_or_evals_to_number("2 + 3 * 4") == 14, "constant arithmetic mismatch")
    check(is_or_evals_to_number("x") is None, "name was evaluated unexpectedly")
    check(extract_operators("x * y + z") == ["*", "+"], "operator extraction mismatch")
    check(extract_operators("-x + y") == ["+"], "unary sign was treated as binary")


def lazy_solution_iterator() -> None:
    from constraint import Problem

    problem = Problem()
    problem.addVariables(["x", "y"], [0, 1])
    iterator = problem.getSolutionIter()
    check(not isinstance(iterator, list), "iterator was eagerly materialized")
    values = list(iterator)
    check(len(values) == 4 and solution_set(values) == {(('x', 0), ('y', 0)), (('x', 0), ('y', 1)), (('x', 1), ('y', 0)), (('x', 1), ('y', 1))}, "lazy iterator values mismatch")


def min_conflicts_seeded() -> None:
    from constraint import MinConflictsSolver, Problem

    def build():
        problem = Problem(MinConflictsSolver(steps=100, rand=random.Random(7)))
        problem.addVariables(["x", "y"], [0, 1])
        problem.addConstraint(lambda x, y: x != y, ["x", "y"])
        return problem

    first = build().getSolution()
    second = build().getSolution()
    check(first == second and first in ({"x": 0, "y": 1}, {"x": 1, "y": 0}), "seeded min-conflicts mismatch")


def parallel_thread_solutions() -> None:
    from constraint import ParallelSolver, Problem

    problem = Problem(ParallelSolver(process_mode=False))
    problem.addVariables(["x", "y"], [0, 1, 2])
    problem.addConstraint("x < y")
    check(solution_set(problem.getSolutions()) == {(('x', 0), ('y', 1)), (('x', 0), ('y', 2)), (('x', 1), ('y', 2))}, "thread parallel mismatch")


def parallel_process_string_solutions() -> None:
    from constraint import ParallelSolver, Problem

    problem = Problem(ParallelSolver(process_mode=True))
    problem.addVariables(["x", "y"], [0, 1, 2])
    problem.addConstraint("x < y")
    check(solution_set(problem.getSolutions()) == {(('x', 0), ('y', 1)), (('x', 0), ('y', 2)), (('x', 1), ('y', 2))}, "process parallel mismatch")


def parallel_process_callable_rejection() -> None:
    from constraint import FunctionConstraint, ParallelSolver, Problem

    problem = Problem(ParallelSolver(process_mode=True))
    problem.addVariables(["x", "y"], [0, 1])
    problem.addConstraint(FunctionConstraint(lambda x, y: x != y), ["x", "y"])
    try:
        problem.getSolutions()
    except AssertionError:
        return
    raise AssertionError("process mode accepted a non-picklable callable")


def unsatisfiable_and_empty_problems() -> None:
    from constraint import Problem

    empty = Problem()
    check(empty.getSolution() is None and empty.getSolutions() == [], "empty problem mismatch")
    impossible = Problem()
    impossible.addVariable("x", [1])
    impossible.addConstraint("x != x")
    check(impossible.getSolution() is None and impossible.getSolutions() == [], "unsatisfiable problem mismatch")


def repeated_solves_stable() -> None:
    from constraint import Problem

    problem = Problem()
    problem.addVariables(["x", "y"], [0, 1, 2])
    problem.addConstraint("x != y")
    first = problem.getSolutions()
    second = problem.getSolutions()
    check(solution_set(first) == solution_set(second) and len(first) == len(second) == 6, "repeated solve changed result")


SCENARIOS = {
    "domain-nested-state": domain_nested_state,
    "problem-domain-copy": problem_domain_copy,
    "callable-order-and-generator": callable_order_and_generator,
    "custom-constraint-forward-check": custom_constraint_forward_check,
    "backtracking-family-equivalence": backtracking_family_equivalence,
    "string-constraint-solve": string_constraint_solve,
    "numeric-and-set-constraints": numeric_and_set_constraints,
    "parser-specialization": parser_specialization,
    "parser-operator-helpers": parser_operator_helpers,
    "lazy-solution-iterator": lazy_solution_iterator,
    "min-conflicts-seeded": min_conflicts_seeded,
    "parallel-thread-solutions": parallel_thread_solutions,
    "parallel-process-string-solutions": parallel_process_string_solutions,
    "parallel-process-callable-rejection": parallel_process_callable_rejection,
    "unsatisfiable-and-empty-problems": unsatisfiable_and_empty_problems,
    "repeated-solves-stable": repeated_solves_stable,
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scenario", choices=sorted(SCENARIOS), required=True)
    parser.add_argument("--candidate-site", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    sys.path.insert(0, args.candidate_site)
    verdict = {"status": "failed", "scenario": args.scenario}
    try:
        SCENARIOS[args.scenario]()
        verdict = {"status": "passed", "scenario": args.scenario}
    except BaseException:
        verdict["message"] = traceback.format_exc(limit=8)[-1600:]
    args.output.write_text(json.dumps(verdict, sort_keys=True), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
