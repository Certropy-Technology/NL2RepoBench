#!/usr/bin/env python3
"""Untrusted child-side adapter for fixed sortedcontainers scenarios."""

from __future__ import annotations

import argparse
import json
import sys
import traceback


def check(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def expect_error(error_type, callback, message: str) -> None:
    try:
        callback()
    except error_type:
        return
    raise AssertionError(message)


def api_surface() -> None:
    import sortedcontainers as package
    from sortedcontainers import SortedKeyList, SortedListWithKey

    expected = {
        "SortedList",
        "SortedKeyList",
        "SortedListWithKey",
        "SortedDict",
        "SortedKeysView",
        "SortedItemsView",
        "SortedValuesView",
        "SortedSet",
    }
    check(set(package.__all__) == expected, "root export set mismatch")
    check(SortedListWithKey is SortedKeyList, "SortedListWithKey alias mismatch")
    check(package.__title__ == "sortedcontainers", "title mismatch")
    check(package.__version__ == "2.4.0", "version mismatch")
    check(package.__license__ == "Apache 2.0", "license metadata mismatch")


def sorted_list_init_order() -> None:
    from sortedcontainers import SortedList

    values = SortedList([4, 1, 3, 1, 2])
    check(list(values) == [1, 1, 2, 3, 4], "initial sort or duplicates changed")
    check(values.key is None and len(values) == 5, "basic metadata mismatch")
    check(list(reversed(values)) == [4, 3, 2, 1, 1], "reverse order mismatch")


def sorted_list_mutations() -> None:
    from sortedcontainers import SortedList

    values = SortedList([3, 1, 2, 2])
    values.add(0)
    values.update([5, 4, 2])
    values.discard(9)
    values.discard(2)
    values.remove(3)
    check(list(values) == [0, 1, 2, 2, 4, 5], "mutation order mismatch")
    values.clear()
    check(list(values) == [], "clear did not empty the list")


def sorted_list_sequence() -> None:
    from sortedcontainers import SortedList

    values = SortedList([9, 3, 7, 1, 5, 2])
    check(values[0] == 1 and values[-1] == 9, "integer indexing mismatch")
    check(values[1:5:2] == [2, 5], "positive slice mismatch")
    check(values[::-2] == [9, 5, 2], "negative slice mismatch")
    check(values == [1, 2, 3, 5, 7, 9], "sequence equality mismatch")
    check(values < [1, 2, 4], "lexicographic comparison mismatch")


def sorted_list_delete_pop() -> None:
    from sortedcontainers import SortedList

    values = SortedList(range(10))
    del values[2]
    del values[4:8:2]
    popped = [values.pop(), values.pop(0), values.pop(-2)]
    check(popped == [9, 0, 6], "positional pop mismatch")
    check(list(values) == [1, 3, 4, 8], "delete result mismatch")


def sorted_list_bisect_count_index() -> None:
    from sortedcontainers import SortedList

    values = SortedList([1, 2, 2, 2, 4, 7])
    check(values.bisect_left(2) == 1, "bisect_left mismatch")
    check(values.bisect_right(2) == 4 and values.bisect(2) == 4, "right bisect mismatch")
    check(values.count(2) == 3 and values.count(3) == 0, "count mismatch")
    check(values.index(2) == 1 and values.index(2, 2, 5) == 2, "index bounds mismatch")


def sorted_list_islice() -> None:
    from sortedcontainers import SortedList

    values = SortedList(range(12))
    check(list(values.islice(2, 9)) == list(range(2, 9)), "islice mismatch")
    check(list(values.islice(2, 9, reverse=True)) == list(range(2, 9))[::-1], "reverse islice mismatch")
    check(list(values.islice(start=9)) == [9, 10, 11], "open islice mismatch")


def sorted_list_irange() -> None:
    from sortedcontainers import SortedList

    values = SortedList(range(10))
    check(list(values.irange(2, 6)) == [2, 3, 4, 5, 6], "inclusive irange mismatch")
    check(list(values.irange(2, 6, (False, False))) == [3, 4, 5], "exclusive irange mismatch")
    check(list(values.irange(2, 6, reverse=True)) == [6, 5, 4, 3, 2], "reverse irange mismatch")
    check(list(values.irange(None, 3, (True, False))) == [0, 1, 2], "open irange mismatch")


def sorted_list_operators_copy() -> None:
    from sortedcontainers import SortedList

    values = SortedList([3, 1, 2])
    combined = values + [0, 3]
    repeated = values * 2
    duplicate = values.copy()
    duplicate += [4, -1]
    check(list(combined) == [0, 1, 2, 3, 3], "addition mismatch")
    check(list(repeated) == [1, 1, 2, 2, 3, 3], "multiplication mismatch")
    check(list(values) == [1, 2, 3] and list(duplicate) == [-1, 1, 2, 3, 4], "copy or in-place addition mismatch")


def sorted_key_list_init_stability() -> None:
    from sortedcontainers import SortedKeyList, SortedList

    key = lambda value: value % 3
    values = SortedList([21, 10, 12, 11, 20], key=key)
    check(type(values) is SortedKeyList, "keyed constructor type mismatch")
    check(values.key is key, "key property mismatch")
    check(list(values) == [21, 12, 10, 11, 20], "stable equal-key order mismatch")


def sorted_key_list_mutations() -> None:
    from sortedcontainers import SortedKeyList

    values = SortedKeyList([10, 20, 30], key=lambda value: value % 10)
    for value in [40, 50, 60]:
        values.add(value)
    values.update([1, 11, 21])
    values.remove(11)
    values.discard(999)
    check(list(values) == [10, 20, 30, 40, 50, 60, 1, 21], "keyed mutation stability mismatch")


def sorted_key_list_key_range() -> None:
    from sortedcontainers import SortedKeyList

    values = SortedKeyList(range(20), key=lambda value: value % 5)
    check(values.bisect_key_left(2) == 8, "key left bisect mismatch")
    check(values.bisect_key_right(2) == 12 and values.bisect_key(2) == 12, "key right bisect mismatch")
    check(list(values.irange_key(1, 3, (True, False))) == [1, 6, 11, 16, 2, 7, 12, 17], "key range mismatch")


def sorted_key_list_value_queries() -> None:
    from sortedcontainers import SortedKeyList

    values = SortedKeyList([1, 11, 21, 2, 12, 22], key=lambda value: value % 10)
    check(11 in values and 31 not in values, "exact membership mismatch")
    check(values.count(11) == 1 and values.index(21) == 2, "exact count/index mismatch")
    check(values.bisect_left(12) == 3 and values.bisect_right(12) == 6, "value bisect within key group mismatch")


def sorted_set_init_sequence() -> None:
    from sortedcontainers import SortedSet

    values = SortedSet([4, 1, 3, 1, 2])
    check(list(values) == [1, 2, 3, 4], "set initialization mismatch")
    check(values[0] == 1 and values[-1] == 4, "set indexing mismatch")
    check(values[1:3] == [2, 3] and list(reversed(values)) == [4, 3, 2, 1], "set sequence mismatch")


def sorted_set_mutations() -> None:
    from sortedcontainers import SortedSet

    values = SortedSet([1, 2, 3])
    values.add(4)
    values.add(4)
    values.update([0, 5], [6])
    values.discard(99)
    values.discard(2)
    values.remove(5)
    check(list(values) == [0, 1, 3, 4, 6], "set mutation mismatch")
    check(values.count(4) == 1 and values.count(2) == 0, "set count mismatch")


def sorted_set_delete_pop() -> None:
    from sortedcontainers import SortedSet

    values = SortedSet(range(10))
    del values[2]
    del values[3:7:2]
    popped = [values.pop(), values.pop(0), values.pop(-2)]
    check(popped == [9, 0, 7], "set positional pop mismatch")
    check(list(values) == [1, 3, 5, 8], "set deletion mismatch")


def sorted_set_range_bisect() -> None:
    from sortedcontainers import SortedSet

    values = SortedSet(range(10))
    check(values.bisect_left(4) == 4 and values.bisect_right(4) == 5, "set bisect mismatch")
    check(list(values.islice(2, 6, reverse=True)) == [5, 4, 3, 2], "set islice mismatch")
    check(list(values.irange(3, 7, (False, True))) == [4, 5, 6, 7], "set irange mismatch")


def sorted_set_algebra() -> None:
    from sortedcontainers import SortedSet

    left = SortedSet(range(6))
    right = SortedSet(range(3, 9))
    check(list(left & right) == [3, 4, 5], "set intersection mismatch")
    check(list(left | right) == list(range(9)), "set union mismatch")
    check(list(left - right) == [0, 1, 2], "set difference mismatch")
    check(list(left ^ right) == [0, 1, 2, 6, 7, 8], "set symmetric difference mismatch")
    check(left.isdisjoint([10]) and left.issubset(range(9)) and left.issuperset([1, 2]), "set relation mismatch")


def sorted_set_inplace_operations() -> None:
    from sortedcontainers import SortedSet

    values = SortedSet(range(6))
    values |= [6, 7]
    values &= range(2, 8)
    values -= [3, 7]
    values ^= [1, 2, 8]
    check(list(values) == [1, 4, 5, 6, 8], "in-place set operations mismatch")


def sorted_set_key_order() -> None:
    from sortedcontainers import SortedSet

    values = SortedSet(range(20), key=lambda value: value % 5)
    expected = sorted(range(20), key=lambda value: value % 5)
    check(list(values) == expected, "keyed set order mismatch")
    check(values.bisect_key_left(2) == 8 and values.bisect_key_right(2) == 12, "keyed set bisect mismatch")
    check(list(values.irange_key(1, 2)) == expected[4:12], "keyed set range mismatch")


def sorted_dict_init_order() -> None:
    from sortedcontainers import SortedDict

    values = SortedDict({"c": 3, "a": 1, "b": 2})
    check(list(values) == ["a", "b", "c"], "dictionary key order mismatch")
    check(list(reversed(values)) == ["c", "b", "a"], "dictionary reverse mismatch")
    check(list(values.items()) == [("a", 1), ("b", 2), ("c", 3)], "dictionary item order mismatch")


def sorted_dict_mutations() -> None:
    from sortedcontainers import SortedDict

    values = SortedDict({"b": 2})
    values["a"] = 1
    values.update({"d": 4}, c=3)
    check(values.get("a") == 1 and values.get("z", 9) == 9, "dictionary get mismatch")
    check(values.setdefault("b", 20) == 2 and values.setdefault("e", 5) == 5, "setdefault mismatch")
    del values["c"]
    check(list(values.items()) == [("a", 1), ("b", 2), ("d", 4), ("e", 5)], "dictionary mutation mismatch")


def sorted_dict_pop_peek() -> None:
    from sortedcontainers import SortedDict

    values = SortedDict({"c": 3, "a": 1, "b": 2, "d": 4})
    check(values.peekitem() == ("d", 4) and values.peekitem(1) == ("b", 2), "peekitem mismatch")
    check(values.popitem(0) == ("a", 1), "indexed popitem mismatch")
    check(values.pop("c") == 3 and values.pop("missing", 9) == 9, "mapping pop mismatch")
    check(values.popitem() == ("d", 4) and list(values.items()) == [("b", 2)], "final popitem mismatch")


def sorted_dict_range_bisect() -> None:
    from sortedcontainers import SortedDict

    values = SortedDict(zip("abcdefgh", range(8)))
    check(values.index("f", 2, -1) == 5, "dictionary index mismatch")
    check(values.bisect_left("d") == 3 and values.bisect_right("d") == 4, "dictionary bisect mismatch")
    check(list(values.islice(2, 6, reverse=True)) == list("fedc"), "dictionary islice mismatch")
    check(list(values.irange("c", "f", (False, True))) == list("def"), "dictionary irange mismatch")


def sorted_dict_key_order() -> None:
    from sortedcontainers import SortedDict

    values = SortedDict(lambda value: value % 4, zip(range(12), range(12)))
    expected = sorted(range(12), key=lambda value: value % 4)
    check(list(values) == expected, "keyed dictionary order mismatch")
    check(values.bisect_key_left(2) == 6 and values.bisect_key_right(2) == 9, "keyed dictionary bisect mismatch")
    check(list(values.irange_key(1, 2)) == expected[3:9], "keyed dictionary range mismatch")


def sorted_dict_live_views() -> None:
    from sortedcontainers import SortedDict, SortedItemsView, SortedKeysView, SortedValuesView

    values = SortedDict({"b": 2, "a": 1})
    keys, items, vals = values.keys(), values.items(), values.values()
    check(isinstance(keys, SortedKeysView) and isinstance(items, SortedItemsView) and isinstance(vals, SortedValuesView), "view types mismatch")
    check(keys[0] == "a" and items[-1] == ("b", 2) and vals[:] == [1, 2], "view indexing mismatch")
    values.update({"d": 4, "c": 3})
    check(list(keys) == list("abcd"), "keys view is not live")
    check(items[1:3] == [("b", 2), ("c", 3)], "items view slice mismatch")
    check(list(reversed(vals)) == [4, 3, 2, 1], "values view reverse mismatch")


def sorted_dict_view_set_operations() -> None:
    from sortedcontainers import SortedDict

    values = SortedDict({"a": 1, "b": 2, "c": 3})
    keys = values.keys()
    items = values.items()
    check(keys == {"a", "b", "c"}, "keys view equality mismatch")
    check(keys & {"b", "d"} == {"b"}, "keys view intersection mismatch")
    check(keys - {"a", "c"} == {"b"}, "keys view difference mismatch")
    check(items & {("a", 1), ("z", 9)} == {("a", 1)}, "items view intersection mismatch")
    check(items.isdisjoint([("a", 9)]), "items view disjoint mismatch")


def sorted_dict_union() -> None:
    from sortedcontainers import SortedDict

    left = SortedDict({"b": 2, "a": 1})
    combined = left | {"b": 20, "c": 3}
    reflected = {"z": 0, "a": 9} | left
    left |= {"d": 4, "a": 10}
    check(isinstance(combined, SortedDict) and list(combined.items()) == [("a", 1), ("b", 20), ("c", 3)], "dictionary union mismatch")
    check(isinstance(reflected, SortedDict) and list(reflected.items()) == [("a", 1), ("b", 2), ("z", 0)], "reflected union mismatch")
    check(list(left.items()) == [("a", 10), ("b", 2), ("d", 4)], "in-place union mismatch")


def copy_independence() -> None:
    from sortedcontainers import SortedDict, SortedList, SortedSet

    original_list = SortedList([3, 1, 2])
    copied_list = original_list.copy()
    copied_list.add(4)
    original_set = SortedSet([3, 1, 2])
    copied_set = original_set.copy()
    copied_set.remove(2)
    original_dict = SortedDict({"b": 2, "a": 1})
    copied_dict = original_dict.copy()
    copied_dict["c"] = 3
    check(list(original_list) == [1, 2, 3] and list(copied_list) == [1, 2, 3, 4], "list copy shared state")
    check(list(original_set) == [1, 2, 3] and list(copied_set) == [1, 3], "set copy shared state")
    check(list(original_dict) == ["a", "b"] and list(copied_dict) == ["a", "b", "c"], "dictionary copy shared state")


def error_contracts() -> None:
    from sortedcontainers import SortedDict, SortedList, SortedSet

    expect_error(ValueError, lambda: SortedList([1]).remove(2), "list remove accepted absent value")
    expect_error(ValueError, lambda: SortedList([1]).index(2), "list index accepted absent value")
    expect_error(IndexError, lambda: SortedList().pop(), "empty list pop did not fail")
    expect_error(ValueError, lambda: SortedList([1])[::0], "zero slice step did not fail")
    expect_error(KeyError, lambda: SortedSet([1]).remove(2), "set remove accepted absent value")
    expect_error(IndexError, lambda: SortedSet().pop(), "empty set pop did not fail")
    expect_error(KeyError, lambda: SortedDict().popitem(), "empty dict popitem did not fail")
    expect_error(IndexError, lambda: SortedDict({"a": 1}).peekitem(2), "invalid peekitem did not fail")


SCENARIOS = {
    "api-surface": api_surface,
    "sorted-list-init-order": sorted_list_init_order,
    "sorted-list-mutations": sorted_list_mutations,
    "sorted-list-sequence": sorted_list_sequence,
    "sorted-list-delete-pop": sorted_list_delete_pop,
    "sorted-list-bisect-count-index": sorted_list_bisect_count_index,
    "sorted-list-islice": sorted_list_islice,
    "sorted-list-irange": sorted_list_irange,
    "sorted-list-operators-copy": sorted_list_operators_copy,
    "sorted-key-list-init-stability": sorted_key_list_init_stability,
    "sorted-key-list-mutations": sorted_key_list_mutations,
    "sorted-key-list-key-range": sorted_key_list_key_range,
    "sorted-key-list-value-queries": sorted_key_list_value_queries,
    "sorted-set-init-sequence": sorted_set_init_sequence,
    "sorted-set-mutations": sorted_set_mutations,
    "sorted-set-delete-pop": sorted_set_delete_pop,
    "sorted-set-range-bisect": sorted_set_range_bisect,
    "sorted-set-algebra": sorted_set_algebra,
    "sorted-set-inplace-operations": sorted_set_inplace_operations,
    "sorted-set-key-order": sorted_set_key_order,
    "sorted-dict-init-order": sorted_dict_init_order,
    "sorted-dict-mutations": sorted_dict_mutations,
    "sorted-dict-pop-peek": sorted_dict_pop_peek,
    "sorted-dict-range-bisect": sorted_dict_range_bisect,
    "sorted-dict-key-order": sorted_dict_key_order,
    "sorted-dict-live-views": sorted_dict_live_views,
    "sorted-dict-view-set-operations": sorted_dict_view_set_operations,
    "sorted-dict-union": sorted_dict_union,
    "copy-independence": copy_independence,
    "error-contracts": error_contracts,
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate-site", required=True)
    parser.add_argument("--scenario", choices=sorted(SCENARIOS), required=True)
    args = parser.parse_args()
    sys.path.insert(0, args.candidate_site)
    verdict = {"scenario": args.scenario, "status": "failed"}
    try:
        SCENARIOS[args.scenario]()
        verdict["status"] = "passed"
    except BaseException:
        verdict["message"] = traceback.format_exc(limit=8)[-1600:]
    print(json.dumps(verdict, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
