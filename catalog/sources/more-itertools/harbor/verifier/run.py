#!/usr/bin/env python3
"""Private deterministic scenarios for the more-itertools public contract.

Each scenario runs as the unprivileged candidate in an isolated subprocess and
must be derivable from the public instruction (https://github.com/more-itertools/more-itertools,
v11.1.0, immutable revision 64be96ceb2a6e836f76f069f4a96d2394d59fd0c). The
candidate runner executes the script and reads the ``result`` binding.
"""

from __future__ import annotations

import json

from nl2repobench.verification.candidate_client import execute_script


def _run(source: str, expected: object) -> tuple[str, object]:
    observed = execute_script(source, timeout_sec=20.0)
    actual: dict[str, object] = {"ok": observed.ok, "value": observed.value}
    if not observed.ok:
        actual["exception_type"] = observed.exception_type
        actual["exception_message"] = observed.exception_message
    return "passed" if actual == expected else "failed", actual


CASES: list[tuple[str, str, object]] = [
    # === Grouping Functions ===
    (
        "chunked-basic",
        "from more_itertools import chunked\nresult = list(chunked([1, 2, 3, 4, 5, 6], 3))",
        {"ok": True, "value": [[1, 2, 3], [4, 5, 6]]},
    ),
    (
        "chunked-partial",
        "from more_itertools import chunked\nresult = list(chunked([1, 2, 3, 4, 5], 2))",
        {"ok": True, "value": [[1, 2], [3, 4], [5]]},
    ),
    (
        "chunked-empty",
        "from more_itertools import chunked\nresult = list(chunked([], 3))",
        {"ok": True, "value": []},
    ),
    (
        "batched-basic",
        "from more_itertools import batched\nresult = list(batched('ABCDEFG', 3))",
        {"ok": True, "value": [('A', 'B', 'C'), ('D', 'E', 'F'), ('G',)]},
    ),
    (
        "sliced-basic",
        "from more_itertools import sliced\nresult = [list(s) for s in sliced(range(10), 3)]",
        {"ok": True, "value": [[0, 1, 2], [3, 4, 5], [6, 7, 8], [9]]},
    ),
    (
        "distribute-basic",
        "from more_itertools import distribute\ni1, i2 = distribute(2, [1,2,3,4])\nresult = [list(i1), list(i2)]",
        {"ok": True, "value": [[1, 3], [2, 4]]},
    ),
    (
        "divide-basic",
        "from more_itertools import divide\nresult = [list(x) for x in divide(3, range(10))]",
        {"ok": True, "value": [[0, 1, 2, 3], [4, 5, 6], [7, 8, 9]]},
    ),
    (
        "split_at-basic",
        "from more_itertools import split_at\nresult = [list(x) for x in split_at([1,2,0,3,4,0,5], lambda x: x==0)]",
        {"ok": True, "value": [[1, 2], [3, 4], [5]]},
    ),
    (
        "split_before-basic",
        "from more_itertools import split_before\nresult = [list(x) for x in split_before('OneTwoThree', str.isupper)]",
        {"ok": True, "value": [['O', 'n', 'e'], ['T', 'w', 'o'], ['T', 'h', 'r', 'e', 'e']]},
    ),
    (
        "split_after-basic",
        "from more_itertools import split_after\nresult = [list(x) for x in split_after([1,2,3,4,5], lambda x: x%2==0)]",
        {"ok": True, "value": [[1, 2], [3, 4], [5]]},
    ),
    (
        "split_into-basic",
        "from more_itertools import split_into\nresult = [list(x) for x in split_into([1,2,3,4,5], [2,3])]",
        {"ok": True, "value": [[1, 2], [3, 4, 5]]},
    ),
    (
        "partition-basic",
        "from more_itertools import partition\nfalses, trues = partition(lambda x: x%2, range(5))\nresult = [list(falses), list(trues)]",
        {"ok": True, "value": [[0, 2, 4], [1, 3]]},
    ),
    (
        "unzip-basic",
        "from more_itertools import unzip\na, b = unzip([(1,'a'), (2,'b'), (3,'c')])\nresult = [list(a), list(b)]",
        {"ok": True, "value": [[1, 2, 3], ['a', 'b', 'c']]},
    ),
    (
        "grouper-basic",
        "from more_itertools import grouper\nresult = list(grouper('ABCDEFG', 3, fillvalue='x'))",
        {"ok": True, "value": [('A', 'B', 'C'), ('D', 'E', 'F'), ('G', 'x', 'x')]},
    ),
    
    # === Lookahead and Lookback ===
    (
        "spy-basic",
        "from more_itertools import spy\nhead, iterable = spy(range(5), 2)\nresult = [head, list(iterable)]",
        {"ok": True, "value": [[0, 1], [0, 1, 2, 3, 4]]},
    ),
    (
        "peekable-basic",
        "from more_itertools import peekable\np = peekable([1,2,3])\nfirst_peek = p.peek()\nfirst_next = next(p)\nsecond_peek = p.peek()\nresult = [first_peek, first_next, second_peek]",
        {"ok": True, "value": [1, 1, 2]},
    ),
    (
        "peekable-empty-default",
        "from more_itertools import peekable\np = peekable([])\nresult = p.peek('default')",
        {"ok": True, "value": "default"},
    ),
    (
        "seekable-basic",
        "from more_itertools import seekable\ns = seekable(range(5))\nnext(s)\nnext(s)\ns.seek(0)\nresult = list(s)",
        {"ok": True, "value": [0, 1, 2, 3, 4]},
    ),
    
    # === Windowing Functions ===
    (
        "windowed-basic",
        "from more_itertools import windowed\nresult = list(windowed([1,2,3,4], 2))",
        {"ok": True, "value": [(1, 2), (2, 3), (3, 4)]},
    ),
    (
        "windowed-fillvalue",
        "from more_itertools import windowed\nresult = list(windowed([1,2,3], 3, fillvalue='x'))",
        {"ok": True, "value": [(1, 2, 3)]},
    ),
    (
        "pairwise-basic",
        "from more_itertools import pairwise\nresult = list(pairwise([1,2,3,4]))",
        {"ok": True, "value": [(1, 2), (2, 3), (3, 4)]},
    ),
    (
        "triplewise-basic",
        "from more_itertools import triplewise\nresult = list(triplewise(range(5)))",
        {"ok": True, "value": [(0, 1, 2), (1, 2, 3), (2, 3, 4)]},
    ),
    (
        "sliding_window-basic",
        "from more_itertools import sliding_window\nresult = list(sliding_window([1,2,3,4,5], 3))",
        {"ok": True, "value": [(1, 2, 3), (2, 3, 4), (3, 4, 5)]},
    ),
    (
        "stagger-basic",
        "from more_itertools import stagger\nresult = list(stagger([0,1,2,3], offsets=(0,1), fillvalue=None))",
        {"ok": True, "value": [(0, 1), (1, 2), (2, 3)]},
    ),
    
    # === Selecting Functions ===
    (
        "first-basic",
        "from more_itertools import first\nresult = first([0, 1, 2, 3])",
        {"ok": True, "value": 0},
    ),
    (
        "first-default",
        "from more_itertools import first\nresult = first([], 'default')",
        {"ok": True, "value": "default"},
    ),
    (
        "first-empty-error",
        "from more_itertools import first\ntry:\n    first([])\n    result = 'no_error'\nexcept ValueError:\n    result = 'error'",
        {"ok": True, "value": "error"},
    ),
    (
        "last-basic",
        "from more_itertools import last\nresult = last([0, 1, 2, 3])",
        {"ok": True, "value": 3},
    ),
    (
        "last-default",
        "from more_itertools import last\nresult = last([], 'default')",
        {"ok": True, "value": "default"},
    ),
    (
        "one-basic",
        "from more_itertools import one\nresult = one([5])",
        {"ok": True, "value": 5},
    ),
    (
        "one-error",
        "from more_itertools import one\ntry:\n    one([1, 2])\n    result = 'no_error'\nexcept ValueError:\n    result = 'error'",
        {"ok": True, "value": "error"},
    ),
    (
        "only-basic",
        "from more_itertools import only\nresult = only([5])",
        {"ok": True, "value": 5},
    ),
    (
        "only-empty",
        "from more_itertools import only\nresult = only([], default='default')",
        {"ok": True, "value": "default"},
    ),
    (
        "nth-basic",
        "from more_itertools import nth\nresult = nth(range(10), 3)",
        {"ok": True, "value": 3},
    ),
    (
        "nth-default",
        "from more_itertools import nth\nresult = nth(range(5), 10, default='x')",
        {"ok": True, "value": "x"},
    ),
    (
        "take-basic",
        "from more_itertools import take\nresult = take(3, range(10))",
        {"ok": True, "value": [0, 1, 2]},
    ),
    (
        "tail-basic",
        "from more_itertools import tail\nresult = tail(3, range(5))",
        {"ok": True, "value": [2, 3, 4]},
    ),
    (
        "strictly_n-basic",
        "from more_itertools import strictly_n\nresult = list(strictly_n([1,2,3], 3))",
        {"ok": True, "value": [1, 2, 3]},
    ),
    (
        "strictly_n-error",
        "from more_itertools import strictly_n\ntry:\n    list(strictly_n([1,2], 3))\n    result = 'no_error'\nexcept ValueError:\n    result = 'error'",
        {"ok": True, "value": "error"},
    ),
    (
        "strip-basic",
        "from more_itertools import strip\nresult = list(strip([0,1,2,3,0], lambda x: x==0))",
        {"ok": True, "value": [1, 2, 3]},
    ),
    (
        "lstrip-basic",
        "from more_itertools import lstrip\nresult = list(lstrip([0,0,1,2,3], lambda x: x==0))",
        {"ok": True, "value": [1, 2, 3]},
    ),
    (
        "rstrip-basic",
        "from more_itertools import rstrip\nresult = list(rstrip([1,2,3,0,0], lambda x: x==0))",
        {"ok": True, "value": [1, 2, 3]},
    ),
    (
        "filter_map-basic",
        "from more_itertools import filter_map\nresult = list(filter_map(lambda x: x if x>2 else None, [1,2,3,4]))",
        {"ok": True, "value": [3, 4]},
    ),
    (
        "unique_everseen-basic",
        "from more_itertools import unique_everseen\nresult = list(unique_everseen('AAAABBBCCDAABBB'))",
        {"ok": True, "value": ['A', 'B', 'C', 'D']},
    ),
    (
        "unique_justseen-basic",
        "from more_itertools import unique_justseen\nresult = list(unique_justseen('AAAABBBCCDAABBB'))",
        {"ok": True, "value": ['A', 'B', 'C', 'D', 'A', 'B']},
    ),
    (
        "unique-basic",
        "from more_itertools import unique\nresult = list(unique([3,1,4,1,5,9,2,6,5,3]))",
        {"ok": True, "value": [1, 2, 3, 4, 5, 6, 9]},
    ),
    
    # === Summarizing Functions ===
    (
        "ilen-basic",
        "from more_itertools import ilen\nresult = ilen(x for x in range(100) if x%2)",
        {"ok": True, "value": 50},
    ),
    (
        "all_equal-true",
        "from more_itertools import all_equal\nresult = all_equal([1,1,1])",
        {"ok": True, "value": True},
    ),
    (
        "all_equal-false",
        "from more_itertools import all_equal\nresult = all_equal([1,1,2])",
        {"ok": True, "value": False},
    ),
    (
        "all_equal-empty",
        "from more_itertools import all_equal\nresult = all_equal([])",
        {"ok": True, "value": True},
    ),
    (
        "all_unique-true",
        "from more_itertools import all_unique\nresult = all_unique([1,2,3])",
        {"ok": True, "value": True},
    ),
    (
        "all_unique-false",
        "from more_itertools import all_unique\nresult = all_unique([1,2,1])",
        {"ok": True, "value": False},
    ),
    (
        "is_sorted-true",
        "from more_itertools import is_sorted\nresult = is_sorted([1,2,3,4])",
        {"ok": True, "value": True},
    ),
    (
        "is_sorted-false",
        "from more_itertools import is_sorted\nresult = is_sorted([1,3,2,4])",
        {"ok": True, "value": False},
    ),
    (
        "exactly_n-true",
        "from more_itertools import exactly_n\nresult = exactly_n([1,2,3,4], 2, lambda x: x%2)",
        {"ok": True, "value": True},
    ),
    (
        "exactly_n-false",
        "from more_itertools import exactly_n\nresult = exactly_n([1,2,3,4], 3, lambda x: x%2)",
        {"ok": True, "value": False},
    ),
    (
        "quantify-basic",
        "from more_itertools import quantify\nresult = quantify([1,0,1,1,0,1])",
        {"ok": True, "value": 4},
    ),
    (
        "first_true-basic",
        "from more_itertools import first_true\nresult = first_true([0, False, 3, 4], pred=bool)",
        {"ok": True, "value": 3},
    ),
    (
        "argmin-basic",
        "from more_itertools import argmin\nresult = argmin([3,1,4,1,5])",
        {"ok": True, "value": 1},
    ),
    (
        "argmax-basic",
        "from more_itertools import argmax\nresult = argmax([3,1,4,1,5])",
        {"ok": True, "value": 5},
    ),
    (
        "minmax-basic",
        "from more_itertools import minmax\nresult = minmax([3,1,4,1,5])",
        {"ok": True, "value": (1, 5)},
    ),
    (
        "consecutive_groups-basic",
        "from more_itertools import consecutive_groups\nresult = [list(g) for g in consecutive_groups([1,2,3,5,6,8])]",
        {"ok": True, "value": [[1, 2, 3], [5, 6], [8]]},
    ),
    (
        "run_length-basic",
        "from more_itertools import run_length\nresult = [[k, v] for k, v in run_length('aaabbbc')]",
        {"ok": True, "value": [['a', 3], ['b', 3], ['c', 1]]},
    ),
    
    # === Combining Functions ===
    (
        "flatten-basic",
        "from more_itertools import flatten\nresult = list(flatten([[1,2], [3,4], [5]]))",
        {"ok": True, "value": [1, 2, 3, 4, 5]},
    ),
    (
        "collapse-basic",
        "from more_itertools import collapse\nresult = list(collapse([[1], 2, [[3], 4]]))",
        {"ok": True, "value": [1, 2, 3, 4]},
    ),
    (
        "interleave-basic",
        "from more_itertools import interleave\nresult = list(interleave([1,2,3], ['a','b','c']))",
        {"ok": True, "value": [1, 'a', 2, 'b', 3, 'c']},
    ),
    (
        "interleave_longest-basic",
        "from more_itertools import interleave_longest\nresult = list(interleave_longest([1,2], ['a','b','c'], fillvalue='x'))",
        {"ok": True, "value": [1, 'a', 2, 'b', 'x', 'c']},
    ),
    (
        "roundrobin-basic",
        "from more_itertools import roundrobin\nresult = list(roundrobin('ABC', 'D', 'EF'))",
        {"ok": True, "value": ['A', 'D', 'E', 'B', 'F', 'C']},
    ),
    (
        "prepend-basic",
        "from more_itertools import prepend\nresult = list(prepend(1, [2,3,4]))",
        {"ok": True, "value": [1, 2, 3, 4]},
    ),
    (
        "value_chain-basic",
        "from more_itertools import value_chain\nresult = list(value_chain(1, [2,3], 4, [5,6]))",
        {"ok": True, "value": [1, 2, 3, 4, 5, 6]},
    ),
    
    # === Mathematical Functions ===
    (
        "dotproduct-basic",
        "from more_itertools import dotproduct\nresult = dotproduct([1,2,3], [4,5,6])",
        {"ok": True, "value": 32},
    ),
    (
        "sum_of_squares-basic",
        "from more_itertools import sum_of_squares\nresult = sum_of_squares([1,2,3])",
        {"ok": True, "value": 14},
    ),
    (
        "transpose-basic",
        "from more_itertools import transpose\nresult = [list(t) for t in transpose([[1,2,3], [4,5,6]])]",
        {"ok": True, "value": [[1, 4], [2, 5], [3, 6]]},
    ),
    (
        "polynomial_eval-basic",
        "from more_itertools import polynomial_eval\nresult = polynomial_eval([1,0,3], 2)",
        {"ok": True, "value": 7},
    ),
    (
        "convolve-basic",
        "from more_itertools import convolve\nresult = list(convolve([1,2,3], [1,1]))",
        {"ok": True, "value": [1, 3, 5, 3]},
    ),
    (
        "matmul-basic",
        "from more_itertools import matmul\nresult = [list(row) for row in matmul([[1,2]], [[3],[4]])]",
        {"ok": True, "value": [[11]]},
    ),
    
    # === Combinatorial Functions ===
    (
        "powerset-basic",
        "from more_itertools import powerset\nresult = [list(p) for p in powerset([1,2])]",
        {"ok": True, "value": [[], [1], [2], [1, 2]]},
    ),
    (
        "circular_shifts-basic",
        "from more_itertools import circular_shifts\nresult = [list(x) for x in circular_shifts([1,2,3])]",
        {"ok": True, "value": [[1, 2, 3], [2, 3, 1], [3, 1, 2]]},
    ),
    (
        "partitions-basic",
        "from more_itertools import partitions\nresult = list(partitions(5))",
        {"ok": True, "value": [[5], [4, 1], [3, 2], [3, 1, 1], [2, 2, 1], [2, 1, 1, 1], [1, 1, 1, 1, 1]]},
    ),
    (
        "set_partitions-basic",
        "from more_itertools import set_partitions\nresult = len(list(set_partitions([1,2], 2)))",
        {"ok": True, "value": 1},
    ),
    
    # === Utility Functions ===
    (
        "consume-basic",
        "from more_itertools import consume\nit = iter([1,2,3,4,5])\nconsume(it, 3)\nresult = list(it)",
        {"ok": True, "value": [4, 5]},
    ),
    (
        "iter_except-basic",
        "from more_itertools import iter_except\nd = {1: 'a', 2: 'b'}\nresult = sorted(iter_except(d.popitem, KeyError))",
        {"ok": True, "value": [[1, 'a'], [2, 'b']]},
    ),
    (
        "repeatfunc-basic",
        "from more_itertools import repeatfunc\nresult = list(repeatfunc(lambda: 5, times=3))",
        {"ok": True, "value": [5, 5, 5]},
    ),
    (
        "side_effect-basic",
        "from more_itertools import side_effect\nresults = []\ndef record(x):\n    results.append(x*2)\nitems = list(side_effect(record, [1,2,3]))\nresult = [items, results]",
        {"ok": True, "value": [[1, 2, 3], [2, 4, 6]]},
    ),
    (
        "always_iterable-scalar",
        "from more_itertools import always_iterable\nresult = list(always_iterable(5))",
        {"ok": True, "value": [5]},
    ),
    (
        "always_iterable-list",
        "from more_itertools import always_iterable\nresult = list(always_iterable([1,2,3]))",
        {"ok": True, "value": [1, 2, 3]},
    ),
    (
        "countable-basic",
        "from more_itertools import countable\nc = countable(range(5))\nlist(c)\nresult = c.items_seen",
        {"ok": True, "value": 5},
    ),
]

assert len(CASES) == 87, f"Expected 87 test cases but got {len(CASES)}"


def main() -> None:
    leaves: list[dict[str, object]] = []
    for case_id, source, expected in CASES:
        status, actual = _run(source, expected)
        leaf: dict[str, object] = {"id": case_id, "status": status}
        if status == "failed":
            leaf["message"] = json.dumps(actual, ensure_ascii=False, sort_keys=True)
        leaves.append(leaf)
    print(json.dumps({"schema_version": "1.0", "leaves": leaves}, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
