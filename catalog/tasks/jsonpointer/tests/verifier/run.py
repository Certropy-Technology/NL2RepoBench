from __future__ import annotations

from collections.abc import Callable

from nl2repobench.verification.candidate_client import (
    CandidateCallResult,
    call,
    call_method,
    get,
)


def passed(result: CandidateCallResult, predicate: Callable[[object], bool]) -> None:
    if not result.ok or not predicate(result.value):
        raise AssertionError(
            f"unexpected candidate result: ok={result.ok} value={result.value!r} "
            f"type={result.exception_type!r} message={result.exception_message!r}"
        )


def raises(result: CandidateCallResult, exception_type: str) -> None:
    if result.ok or result.exception_type != exception_type:
        raise AssertionError(
            f"expected {exception_type}, got ok={result.ok} "
            f"type={result.exception_type!r} message={result.exception_message!r}"
        )


def starts(value: object, prefix: str) -> bool:
    return isinstance(value, str) and value.startswith(prefix)


def constructed_pointer(path: str) -> dict[str, object]:
    return {
        "__nl2repo_construct__": {
            "args": [path],
            "attribute": "JsonPointer",
            "kwargs": {},
            "module": "jsonpointer",
        }
    }


def check_pointer_representation() -> None:
    passed(call("jsonpointer", "JsonPointer", "/a~1b"), lambda x: x == "JsonPointer('/a~1b')")
    passed(
        call_method("jsonpointer", "JsonPointer", ["/a~1b"], "path", invoke=False),
        lambda x: x == "/a~1b",
    )
    passed(
        call_method("jsonpointer", "JsonPointer", ["/a~1b"], "get_parts"),
        lambda x: x == ["a/b"],
    )


def check_pointer_composition() -> None:
    passed(
        call("jsonpointer", "JsonPointer.from_parts", ["a", "~", "/", 0]),
        lambda x: x == "JsonPointer('/a/~0/~1/0')",
    )
    passed(
        call_method("jsonpointer", "JsonPointer", ["/a/b"], "join", "/c~1d"),
        lambda x: x == "JsonPointer('/a/b/c~1d')",
    )
    passed(
        call_method(
            "jsonpointer",
            "JsonPointer",
            ["/a/b/c"],
            "contains",
            constructed_pointer("/a/b"),
        ),
        lambda x: x is True,
    )
    passed(
        call_method(
            "jsonpointer",
            "JsonPointer",
            ["/a/0/b"],
            "to_last",
            {"a": [{"b": 1}]},
        ),
        lambda x: x == [{"b": 1}, "b"],
    )


def leaf_checks() -> list[tuple[str, Callable[[], None]]]:
    document = {
        "foo": ["bar", "baz"],
        "": 0,
        "a/b": 1,
        "m~n": 8,
        "c%d": 2,
    }
    return [
        ("metadata.version", lambda: passed(get("jsonpointer", "__version__"), lambda x: x == "3.1.1")),
        ("module.escape", lambda: passed(call("jsonpointer", "escape", "a~/b"), lambda x: x == "a~0~1b")),
        ("module.unescape", lambda: passed(call("jsonpointer", "unescape", "a~0~1b"), lambda x: x == "a~/b")),
        ("module.pairwise", lambda: passed(call("jsonpointer", "pairwise", [1, 2, 3]), lambda x: x == [[1, 2], [2, 3]])),
        ("resolve.root", lambda: passed(call("jsonpointer", "resolve_pointer", document, ""), lambda x: x == document)),
        ("resolve.mapping", lambda: passed(call("jsonpointer", "resolve_pointer", document, "/foo"), lambda x: x == ["bar", "baz"])),
        ("resolve.sequence", lambda: passed(call("jsonpointer", "resolve_pointer", document, "/foo/0"), lambda x: x == "bar")),
        ("resolve.rfc6901_escapes", lambda: passed(call("jsonpointer", "resolve_pointer", document, "/a~1b"), lambda x: x == 1)),
        ("resolve.literal_percent", lambda: passed(call("jsonpointer", "resolve_pointer", document, "/c%d"), lambda x: x == 2)),
        ("resolve.default", lambda: passed(call("jsonpointer", "resolve_pointer", document, "/missing", None), lambda x: x is None)),
        ("resolve.missing_error", lambda: raises(call("jsonpointer", "resolve_pointer", document, "/missing"), "jsonpointer.JsonPointerException")),
        ("constructor.no_start_slash", lambda: raises(call("jsonpointer", "JsonPointer", "foo"), "jsonpointer.JsonPointerException")),
        ("constructor.invalid_escape", lambda: raises(call("jsonpointer", "JsonPointer", "/foo~2"), "jsonpointer.JsonPointerException")),
        ("constructor.trailing_escape", lambda: raises(call("jsonpointer", "JsonPointer", "/foo~"), "jsonpointer.JsonPointerException")),
        ("sequence.invalid_index", lambda: raises(call("jsonpointer", "resolve_pointer", [0, 1], "/a"), "jsonpointer.JsonPointerException")),
        ("sequence.leading_zero", lambda: raises(call("jsonpointer", "resolve_pointer", [0, 1], "/01"), "jsonpointer.JsonPointerException")),
        ("sequence.out_of_bounds", lambda: raises(call("jsonpointer", "resolve_pointer", [0, 1], "/10"), "jsonpointer.JsonPointerException")),
        ("sequence.end_marker", lambda: passed(call("jsonpointer", "resolve_pointer", {"foo": [1]}, "/foo/-"), lambda x: starts(x, "EndOfList("))),
        ("sequence.end_marker_walk", lambda: raises(call("jsonpointer", "resolve_pointer", {"foo": [1]}, "/foo/-/1"), "jsonpointer.JsonPointerException")),
        ("get_part.mapping", lambda: passed(call("jsonpointer", "JsonPointer.get_part", {"a": 1}, "a"), lambda x: x == "a")),
        ("get_part.sequence", lambda: passed(call("jsonpointer", "JsonPointer.get_part", [1, 2], "1"), lambda x: x == 1)),
        ("get_part.invalid", lambda: raises(call("jsonpointer", "JsonPointer.get_part", [1, 2], "a"), "jsonpointer.JsonPointerException")),
        ("set.copy_nested", lambda: passed(call("jsonpointer", "set_pointer", document, "/foo/1", "cod", inplace=False), lambda x: x["foo"] == ["bar", "cod"])),
        ("set.copy_append", lambda: passed(call("jsonpointer", "set_pointer", document, "/foo/-", "xyz", inplace=False), lambda x: x["foo"] == ["bar", "baz", "xyz"])),
        ("set.copy_root", lambda: passed(call("jsonpointer", "set_pointer", document, "", 9, inplace=False), lambda x: x == 9)),
        ("set.copy_new_member", lambda: passed(call("jsonpointer", "set_pointer", document, "/new", "value", inplace=False), lambda x: x["new"] == "value")),
        ("pointer.representation", check_pointer_representation),
        ("pointer.composition", check_pointer_composition),
    ]


def main() -> None:
    leaves = []
    for leaf_id, check in leaf_checks():
        try:
            check()
        except Exception as exc:
            leaves.append({"id": leaf_id, "status": "failed", "message": str(exc)[:4000]})
        else:
            leaves.append({"id": leaf_id, "status": "passed"})
    import json

    print(json.dumps({"schema_version": "1.0", "leaves": leaves}, sort_keys=True))


if __name__ == "__main__":
    main()
