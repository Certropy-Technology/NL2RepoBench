"""Unprivileged child adapter for the bounded glom contract."""

from __future__ import annotations

import argparse
import hashlib
from importlib import metadata
import json
import os
from pathlib import Path
import sys


def _observe(value):
    if isinstance(value, dict):
        return {
            "kind": "dict",
            "items": [[_observe(key), _observe(item)] for key, item in value.items()],
        }
    if isinstance(value, tuple):
        return {"kind": "tuple", "items": [_observe(item) for item in value]}
    if isinstance(value, list):
        return [_observe(item) for item in value]
    if isinstance(value, (set, frozenset)):
        items = [_observe(item) for item in value]
        return {"kind": type(value).__name__, "items": sorted(items, key=repr)}
    if isinstance(value, type):
        return {"type": f"{value.__module__}.{value.__qualname__}"}
    return value


def _double(value):
    return value * 2


def _positive(value):
    return value > 0


def _even(value):
    return value % 2 == 0


def _total(mapping):
    return mapping["price"] * mapping["quantity"]


def _api_surface(candidate_site: Path):
    import glom

    required = (
        "A", "And", "Assign", "Auto", "BadSpec", "Call", "Check",
        "CheckError", "Coalesce", "CoalesceError", "Delete", "Fill",
        "Flatten", "Fold", "FoldError", "GlomError", "Glommer", "Inspect",
        "Invoke", "Iter", "M", "Match", "MatchError", "Merge", "Not",
        "Optional", "Or", "Path", "PathAccessError", "PathAssignError",
        "PathDeleteError", "Pipe", "ROOT", "Ref", "Regex", "Required", "S",
        "SKIP", "STOP", "Spec", "Sum", "Switch", "T", "TypeMatchError",
        "UP", "UnregisteredTarget", "Val", "Vars", "assign", "delete",
        "flatten", "glom", "merge", "register", "register_op",
    )
    origin = Path(glom.__file__).resolve()
    return {
        "candidate_origin": origin.is_relative_to(candidate_site.resolve()),
        "distribution_version": metadata.version("glom"),
        "exports": {name: hasattr(glom, name) for name in required},
        "runtime_version": glom.__version__,
    }


def _basic_access():
    from glom import Coalesce, glom

    target = {
        "user": {"profile": {"name": "Ada"}},
        "rows": [{"value": 7}, {"value": 9}],
    }
    return glom(
        target,
        {
            "name": "user.profile.name",
            "first": "rows.0.value",
            "fallback": Coalesce("missing.path", default="none"),
        },
    )


def _explicit_path():
    from glom import Path, glom

    target = {"a.b": [{("x", 1): {"value": 11}}]}
    return {
        "explicit": glom(target, Path("a.b", 0, ("x", 1), "value")),
        "parts": Path("a.b", 0, "value").values(),
        "text": Path.from_text("root.2.name").values(),
    }


def _construction_and_t():
    from glom import T, glom

    target = {
        "orders": [
            {"name": "pen", "price": 3, "quantity": 2},
            {"name": "book", "price": 8, "quantity": 1},
        ]
    }
    spec = {
        "names": ("orders", [("name", str.upper)]),
        "totals": ("orders", [(T["price"] * T["quantity"])]),
        "count": ("orders", len),
    }
    return glom(target, spec)


def _call_and_invoke():
    from glom import Call, Invoke, T, Val, glom

    target = {"left": 4, "right": 5, "values": [4, 5]}
    called = glom(target, Call(pow, args=(T["left"], Val(2))))
    invoked = glom(target, Invoke(sum).specs(T["values"]))
    constants = glom(target, Invoke(dict).constants(kind="sum").specs(value=Val(called)))
    return {"call": called, "constants": constants, "invoke": invoked}


def _coalesce_contract():
    from glom import Coalesce, glom

    target = {"empty": None, "good": {"value": 12}}
    return {
        "default": glom(target, Coalesce("missing", default="fallback")),
        "skip": glom(target, Coalesce("empty", "good.value", skip=None)),
        "skip_exc": glom(target, Coalesce(lambda _t: 1 / 0, "good.value", skip_exc=ZeroDivisionError)),
    }


def _val_fill_pipe():
    from glom import Fill, Pipe, T, Val, glom

    target = {"name": "Ada", "scores": [2, 3]}
    return {
        "fill": glom(target, Fill((T["name"], [T["scores"], Val("fixed")]))),
        "pipe": glom(target, Pipe("scores", sum, _double)),
        "val": glom(target, {"literal": Val({"x": [1, 2]})}),
    }


def _ref_recursive():
    from glom import Ref, glom

    target = {
        "name": "root",
        "children": [
            {"name": "left", "children": []},
            {"name": "right", "children": [{"name": "leaf", "children": []}]},
        ],
    }
    tree = Ref("tree", {"label": "name", "children": ("children", [Ref("tree")])})
    return glom(target, tree)


def _spec_scope():
    from glom import Spec, glom

    target = {"items": [2, 4, 6]}
    spec = Spec({"scaled": ("items", [lambda value: value * 3])})
    return {"repr_has_spec": repr(spec).startswith("Spec("), "result": glom(target, spec)}


def _match_mapping():
    from glom import Match, Optional, Required, glom

    spec = Match({"name": str, Optional("age"): int})
    return {
        "complete": glom({"name": "Ada", "age": 37}, spec),
        "defaulted": glom({"name": "Grace"}, spec),
    }


def _match_logic():
    from glom import And, Match, Not, Or, Regex, glom

    values = ["ABC-12", "bad", 8, -1]
    pattern = Or(Regex(r"^[A-Z]{3}-\d{2}$"), And(int, _positive, Not(0)))
    return [glom(value, Match(pattern, default="no-match")) for value in values]


def _check_and_switch():
    from glom import Check, Switch, glom

    check = Check(type=int, validate=_positive, default=0)
    switch = Switch([("c", lambda _target: 3), ("a", "a")], default=4)
    return {
        "check_bad": glom(-2, check),
        "check_good": glom(5, check),
        "first": glom({"a": 1, "c": None}, switch),
        "second": glom({"c": None}, switch),
        "default": glom(None, switch),
    }


def _match_error():
    from glom import Match, glom

    try:
        glom({"count": "wrong"}, Match({"count": int}))
    except Exception as error:
        return {
            "class": type(error).__name__,
            "is_glom_error": any(base.__name__ == "GlomError" for base in type(error).__mro__),
            "message_has_path": "count" in str(error),
        }
    raise AssertionError("expected match failure")


def _path_error():
    from glom import PathAccessError, glom

    try:
        glom({"a": {}}, "a.missing.value")
    except PathAccessError as error:
        return {
            "class": type(error).__name__,
            "part_idx": error.part_idx,
            "path_values": error.path.values(),
            "message_has_missing": "missing" in str(error),
        }
    raise AssertionError("expected path failure")


def _assign_existing():
    from glom import assign

    target = {"users": [{"name": "Ada", "active": False}]}
    returned = assign(target, "users.0.active", True)
    return {"identity": returned is target, "target": target}


def _assign_missing():
    from glom import assign

    target = {}
    returned = assign(target, "profile.contact.email", "ada@example.test", missing=dict)
    return {"identity": returned is target, "target": target}


def _assign_spec():
    from glom import Assign, T, glom

    target = {"price": 5, "quantity": 4}
    result = glom(target, Assign("total", T["price"] * T["quantity"], missing=dict))
    return {"identity": result is target, "target": target}


def _delete_contract():
    from glom import delete

    target = {"rows": [{"value": 1}, {"value": 2}, {"value": 3}], "meta": {"drop": True}}
    first = delete(target, "rows.1")
    second = delete(target, "meta.drop")
    ignored = delete(target, "meta.missing", ignore_missing=True)
    return {
        "identities": [first is target, second is target, ignored is target],
        "target": target,
    }


def _iter_map_filter():
    from glom import Iter, glom

    target = {"items": [{"value": 1}, {"value": 2}, {"value": 3}, {"value": 4}]}
    spec = ("items", Iter().filter(lambda item: item["value"] % 2 == 0).map(lambda item: item["value"] * 10), list)
    return glom(target, spec)


def _iter_chunk_window():
    from glom import Iter, glom

    values = [1, 2, 3, 4, 5]
    return {
        "chunked": glom(values, (Iter().chunked(2), list)),
        "windowed": glom(values, (Iter().windowed(3), list)),
    }


def _iter_unique_slice():
    from glom import Iter, glom

    values = ["a", "b", "a", "c", "b", "d"]
    return {
        "slice": glom(range(10), (Iter().slice(2, 8, 2), list)),
        "unique": glom(values, (Iter().unique(), list)),
    }


def _iter_flatten_split():
    from glom import Iter, glom

    return {
        "flatten": glom([[1, 2], [], [3], [4, 5]], (Iter().flatten(), list)),
        "split": glom([1, 2, 0, 3, 0, 4], (Iter().split(0), list)),
    }


def _iter_terminal():
    from glom import Iter, glom

    return {
        "all": glom([2, 4, 6], Iter().filter(_even).all()),
        "first_default": glom([], Iter().first(default="empty")),
        "first_match": glom([1, 3, 4, 6], Iter().filter(_even).first()),
    }


def _reductions():
    from glom import Flatten, Merge, Sum, glom

    return {
        "flatten": glom([[1, 2], [], [3]], Flatten()),
        "merge": glom([{"a": 1}, {"b": 2}, {"a": 9}], Merge()),
        "sum": glom([1, 2, 3, 4], Sum(init=lambda: 10)),
    }


def _fold_custom():
    from glom import Fold, glom

    return glom([1, 2, 3, 4], Fold(lambda item: item, init=lambda: [], op=lambda left, right: left + [right]))


def _grouping():
    from glom import T, glom
    from glom.grouping import First, Group, Limit

    target = [
        {"team": "red", "score": 5},
        {"team": "blue", "score": 9},
        {"team": "red", "score": 7},
    ]
    return {
        "buckets": glom(target, Group({T["team"]: [T["score"]]})),
        "first": glom([5, 6, 7], Group(First())),
        "limited": glom(range(5), Group({T % 2: Limit(1)})),
    }


def _glommer_registry():
    from glom import Glommer

    class Record:
        def __init__(self, values):
            self.values = values

    glommer = Glommer(register_default_types=True)
    glommer.register(Record, get=lambda target, key: target.values[key])
    target = Record({"name": "Ada", "nested": Record({"value": 17})})
    return glommer.glom(target, {"name": "name", "nested": "nested.value"})


def _cli_json():
    from contextlib import redirect_stderr, redirect_stdout
    from glom.cli import main
    import io

    stdout = io.StringIO()
    stderr = io.StringIO()
    with redirect_stdout(stdout), redirect_stderr(stderr):
        result = main(["glom", "--indent", "0", "items.1.v", '{"items":[{"v":1},{"v":2}]}'])
    return {"exit": result, "stderr": stderr.getvalue(), "stdout": stdout.getvalue()}


CASES = {
    "api-surface": _api_surface,
    "basic-access": _basic_access,
    "explicit-path": _explicit_path,
    "construction-and-t": _construction_and_t,
    "call-and-invoke": _call_and_invoke,
    "coalesce-contract": _coalesce_contract,
    "val-fill-pipe": _val_fill_pipe,
    "ref-recursive": _ref_recursive,
    "spec-scope": _spec_scope,
    "match-mapping": _match_mapping,
    "match-logic": _match_logic,
    "check-and-switch": _check_and_switch,
    "match-error": _match_error,
    "path-error": _path_error,
    "assign-existing": _assign_existing,
    "assign-missing": _assign_missing,
    "assign-spec": _assign_spec,
    "delete-contract": _delete_contract,
    "iter-map-filter": _iter_map_filter,
    "iter-chunk-window": _iter_chunk_window,
    "iter-unique-slice": _iter_unique_slice,
    "iter-flatten-split": _iter_flatten_split,
    "iter-terminal": _iter_terminal,
    "reductions": _reductions,
    "fold-custom": _fold_custom,
    "grouping": _grouping,
    "glommer-registry": _glommer_registry,
    "cli-json": _cli_json,
}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate-site", type=Path, required=True)
    parser.add_argument("--request", required=True)
    arguments = parser.parse_args()
    try:
        request = json.loads(arguments.request)
        if request.get("schema_version") != "glom-scenarios-v1":
            raise ValueError("unsupported request schema")
        case_id = request["case_id"]
        if case_id not in CASES:
            raise ValueError("unsupported case")
        dependency_root = os.environ.get("NL2REPO_CANDIDATE_DEPENDENCIES")
        if dependency_root:
            sys.path.insert(0, dependency_root)
        sys.path.insert(0, str(arguments.candidate_site))
        function = CASES[case_id]
        value = function(arguments.candidate_site) if case_id == "api-surface" else function()
        observed = _observe(value)
        encoded = json.dumps(observed, ensure_ascii=False, separators=(",", ":"), sort_keys=True).encode()
        response = {"ok": True, "value": hashlib.sha256(encoded).hexdigest()}
    except BaseException as error:
        response = {
            "exception_message": str(error),
            "exception_type": type(error).__name__,
            "ok": False,
        }
    print(json.dumps(response, ensure_ascii=False, separators=(",", ":"), sort_keys=True))


if __name__ == "__main__":
    main()
