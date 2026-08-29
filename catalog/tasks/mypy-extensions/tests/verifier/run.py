from __future__ import annotations

import json
import textwrap
from dataclasses import dataclass
from typing import Any

from nl2repobench.verification.candidate_client import execute_script, metadata_requires


@dataclass(frozen=True)
class Case:
    leaf_id: str
    source: str
    expected: Any
    timeout_sec: float = 1.0


CASES: list[Case] = []


def case(leaf_id: str, source: str, expected: Any, timeout_sec: float = 1.0) -> None:
    CASES.append(Case(leaf_id, textwrap.dedent(source), expected, timeout_sec))


case(
    "packaging.version",
    """
    import importlib.metadata
    result = importlib.metadata.version("mypy_extensions")
    """,
    "1.2.0.dev0",
)
case(
    "packaging.public-symbols",
    """
    import mypy_extensions as m
    names = [
        "TypedDict", "Arg", "DefaultArg", "NamedArg", "DefaultNamedArg",
        "VarArg", "KwArg", "trait", "mypyc_attr", "FlexibleAlias",
        "i64", "i32", "i16", "u8",
    ]
    result = all(hasattr(m, name) for name in names)
    """,
    True,
)

for name in ("Arg", "DefaultArg", "NamedArg", "DefaultNamedArg"):
    case(
        f"markers.{name}.provided-type",
        f"""
        import mypy_extensions as m
        result = m.{name}(int) is int
        """,
        True,
    )
    case(
        f"markers.{name}.default-any",
        f"""
        import typing
        import mypy_extensions as m
        result = m.{name}() is typing.Any
        """,
        True,
    )
    case(
        f"markers.{name}.name-is-runtime-noop",
        f"""
        import mypy_extensions as m
        token = object()
        result = m.{name}(token, "argument_name") is token
        """,
        True,
    )

for name in ("VarArg", "KwArg"):
    case(
        f"markers.{name}.provided-type",
        f"""
        import mypy_extensions as m
        result = m.{name}(str) is str
        """,
        True,
    )
    case(
        f"markers.{name}.default-any",
        f"""
        import typing
        import mypy_extensions as m
        result = m.{name}() is typing.Any
        """,
        True,
    )

case(
    "trait.class-identity",
    """
    import mypy_extensions as m
    class C: pass
    result = m.trait(C) is C
    """,
    True,
)
case(
    "trait.class-state-preserved",
    """
    import mypy_extensions as m
    class C:
        value = 7
    decorated = m.trait(C)
    result = [decorated.__name__, decorated().value]
    """,
    ["C", 7],
)

case(
    "mypyc-attr.function-identity",
    """
    import mypy_extensions as m
    def f(): return 3
    decorated = m.mypyc_attr("allow_interpreted_subclasses")(f)
    result = [decorated is f, decorated()]
    """,
    [True, 3],
)
case(
    "mypyc-attr.keyword-metadata-noop",
    """
    import mypy_extensions as m
    def f(): return 5
    decorated = m.mypyc_attr(serializable=True, always_allow_keywords=False)(f)
    result = [decorated is f, vars(decorated)]
    """,
    [True, {}],
)
case(
    "mypyc-attr.class-identity",
    """
    import mypy_extensions as m
    class C: pass
    result = m.mypyc_attr("native")(C) is C
    """,
    True,
)

case(
    "flexible-alias.single-first-argument",
    """
    import mypy_extensions as m
    result = repr(m.FlexibleAlias[dict][str])
    """,
    "dict[-1]",
)
case(
    "flexible-alias.last-first-stage-argument",
    """
    import mypy_extensions as m
    result = m.FlexibleAlias[str, int][float] is int
    """,
    True,
)
case(
    "flexible-alias.applied-reuse",
    """
    import mypy_extensions as m
    applied = m.FlexibleAlias[dict]
    result = [repr(applied[int]), repr(applied[str])]
    """,
    ["dict[-1]", "dict[-1]"],
)

for name in ("i64", "i32", "i16", "u8"):
    case(
        f"native-int.{name}.integer-construction",
        f"""
        import mypy_extensions as m
        cls = m.{name}
        result = [cls(), cls(1), cls(-3), cls(2**64), cls(-(2**64))]
        """,
        [0, 1, -3, 2**64, -(2**64)],
    )
    case(
        f"native-int.{name}.float-truncation",
        f"""
        import mypy_extensions as m
        cls = m.{name}
        result = [cls(1.234), cls(2.634), cls(-1.234), cls(-2.634)]
        """,
        [1, 2, -1, -2],
    )
    case(
        f"native-int.{name}.string-and-base",
        f"""
        import mypy_extensions as m
        cls = m.{name}
        result = [cls("0"), cls("123"), cls("abc", 16), cls("-101", base=2)]
        """,
        [0, 123, 2748, -5],
    )
    case(
        f"native-int.{name}.instance-check",
        f"""
        import mypy_extensions as m
        cls = m.{name}
        result = [isinstance(0, cls), isinstance(1234, cls), isinstance(True, cls), isinstance(1.0, cls)]
        """,
        [True, True, True, False],
    )
    case(
        f"native-int.{name}.plain-int-result",
        f"""
        import mypy_extensions as m
        cls = m.{name}
        value = cls(8)
        result = [type(value) is int, cls is not int]
        """,
        [True, True],
    )
    case(
        f"native-int.{name}.docstring",
        f"""
        import mypy_extensions as m
        doc = m.{name}.__doc__ or ""
        result = [{name!r} in doc, "int" in doc]
        """,
        [True, True],
    )

case(
    "typeddict.functional-mapping",
    """
    import warnings
    import mypy_extensions as m
    with warnings.catch_warnings(record=True) as seen:
        warnings.simplefilter("always")
        Emp = m.TypedDict("Emp", {"name": str, "id": int})
    value = Emp(name="Jim", id=1)
    result = [
        Emp.__name__, Emp.__module__, Emp.__bases__ == (dict,),
        Emp.__annotations__ == {"name": str, "id": int}, Emp.__total__,
        type(value) is dict, value, len(seen), seen[0].category is DeprecationWarning,
    ]
    """,
    ["Emp", "__main__", True, True, True, True, {"id": 1, "name": "Jim"}, 1, True],
)
case(
    "typeddict.functional-keywords",
    """
    import warnings
    import mypy_extensions as m
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        Emp = m.TypedDict("Emp", name=str, id=int)
    result = [Emp.__annotations__ == {"name": str, "id": int}, Emp(name="A", id=2)]
    """,
    [True, {"id": 2, "name": "A"}],
)
case(
    "typeddict.mixed-fields-rejected",
    """
    import warnings
    import mypy_extensions as m
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            m.TypedDict("Bad", {"x": int}, y=str)
    except Exception as exc:
        result = [type(exc).__name__, "either a dict or keyword arguments" in str(exc)]
    else:
        result = [None, False]
    """,
    ["TypeError", True],
)
case(
    "typeddict.invalid-field-type-rejected",
    """
    import warnings
    import mypy_extensions as m
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            m.TypedDict("Bad", {"x": ()})
    except Exception as exc:
        result = type(exc).__name__
    else:
        result = None
    """,
    "TypeError",
)
case(
    "typeddict.class-syntax",
    """
    import warnings
    import mypy_extensions as m
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        namespace = {"m": m, "__name__": "__main__"}
        source = "class Point(m.TypedDict):\\n    x: int\\n    y: int\\n"
        exec(compile(source, "<typed-dict-class>", "exec", dont_inherit=True), namespace)
        Point = namespace["Point"]
    result = [Point.__name__, Point.__module__, Point.__bases__ == (dict,), Point.__annotations__, Point.__total__, Point(x=1, y=2)]
    """,
    ["Point", "__main__", True, {"x": "<class 'int'>", "y": "<class 'int'>"}, True, {"x": 1, "y": 2}],
)
case(
    "typeddict.multiple-inheritance",
    """
    import warnings
    import mypy_extensions as m
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        class Point(m.TypedDict):
            x: int
            y: int
        Label = m.TypedDict("Label", {"label": str})
        class LabeledPoint(Point, Label):
            active: bool
    result = [LabeledPoint.__bases__ == (dict,), list(LabeledPoint.__annotations__), LabeledPoint.__total__]
    """,
    [True, ["active", "x", "y", "label"], True],
)
case(
    "typeddict.functional-total-false",
    """
    import warnings
    import mypy_extensions as m
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        D = m.TypedDict("D", {"x": int}, total=False)
    result = [D.__total__, D(), D(x=1)]
    """,
    [False, {}, {"x": 1}],
)
case(
    "typeddict.class-total-false",
    """
    import warnings
    import mypy_extensions as m
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        class Options(m.TypedDict, total=False):
            log_level: int
            log_path: str
    result = [Options.__total__, Options(), Options(log_level=2)]
    """,
    [False, {}, {"log_level": 2}],
)
case(
    "typeddict.runtime-does-not-validate",
    """
    import warnings
    import mypy_extensions as m
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        D = m.TypedDict("D", {"x": int})
    result = D(x="not-an-int", extra=2)
    """,
    {"extra": 2, "x": "not-an-int"},
)
case(
    "typeddict.instance-check-rejected",
    """
    import warnings
    import mypy_extensions as m
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        D = m.TypedDict("D", {"x": int})
    try:
        isinstance({"x": 1}, D)
    except Exception as exc:
        result = [type(exc).__name__, "does not support instance and class checks" in str(exc)]
    else:
        result = [None, False]
    """,
    ["TypeError", True],
)
case(
    "typeddict.subclass-check-rejected",
    """
    import warnings
    import mypy_extensions as m
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        D = m.TypedDict("D", {"x": int})
    try:
        issubclass(dict, D)
    except Exception as exc:
        result = [type(exc).__name__, "does not support instance and class checks" in str(exc)]
    else:
        result = [None, False]
    """,
    ["TypeError", True],
)
case(
    "typeddict.functional-deprecation",
    """
    import warnings
    import mypy_extensions as m
    with warnings.catch_warnings(record=True) as seen:
        warnings.simplefilter("always")
        m.TypedDict("D", {"x": int})
    result = [len(seen), seen[0].category is DeprecationWarning, "mypy_extensions.TypedDict is deprecated" in str(seen[0].message)]
    """,
    [1, True, True],
)
case(
    "typeddict.class-deprecation",
    """
    import warnings
    import mypy_extensions as m
    with warnings.catch_warnings(record=True) as seen:
        warnings.simplefilter("always")
        class D(m.TypedDict):
            x: int
    result = [len(seen), seen[0].category is DeprecationWarning, "mypy_extensions.TypedDict is deprecated" in str(seen[0].message)]
    """,
    [1, True, True],
)
case(
    "typeddict.pickle-instance-and-class",
    """
    import pickle
    import sys
    import warnings
    import mypy_extensions as m
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        PickledTD = m.TypedDict("PickledTD", {"name": str, "id": int})
    setattr(sys.modules["__main__"], "PickledTD", PickledTD)
    value = PickledTD(name="Jane", id=37)
    value2 = pickle.loads(pickle.dumps(value, pickle.HIGHEST_PROTOCOL))
    cls2 = pickle.loads(pickle.dumps(PickledTD, pickle.HIGHEST_PROTOCOL))
    result = [value2 == value, type(value2) is dict, cls2(name="Jane", id=37) == value]
    """,
    [True, True, True],
)
case(
    "typeddict.typing-integration",
    """
    import typing
    import warnings
    import mypy_extensions as m
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        D = m.TypedDict("D", {"x": int})
    result = [typing.Optional[D] == typing.Union[None, D], typing.List[D] != typing.Tuple[D]]
    """,
    [True, True],
)

case(
    "no-return.first-access-warning",
    """
    import warnings
    import mypy_extensions as m
    m.__dict__.pop("NoReturn", None)
    with warnings.catch_warnings(record=True) as seen:
        warnings.simplefilter("always")
        value = m.NoReturn
    result = [value.__name__, len(seen), seen[0].category is DeprecationWarning, "typing.NoReturn" in str(seen[0].message)]
    """,
    ["_DEPRECATED_NoReturn", 1, True, True],
)
case(
    "no-return.cached-after-first-access",
    """
    import warnings
    import mypy_extensions as m
    m.__dict__.pop("NoReturn", None)
    with warnings.catch_warnings(record=True) as seen:
        warnings.simplefilter("always")
        first = m.NoReturn
        second = m.NoReturn
    result = [first is second, len(seen), m.__dict__["NoReturn"] is first]
    """,
    [True, 1, True],
)
case(
    "no-return.unknown-attribute",
    """
    import mypy_extensions as m
    try:
        m.DefinitelyMissing
    except Exception as exc:
        result = [type(exc).__name__, str(exc)]
    else:
        result = [None, None]
    """,
    ["AttributeError", "module 'mypy_extensions' has no attribute 'DefinitelyMissing'"],
)


def main() -> None:
    leaves: list[dict[str, str]] = []

    requires = metadata_requires("mypy_extensions")
    if requires.ok and requires.value is None:
        leaves.append({"id": "packaging.no-runtime-dependencies", "status": "passed"})
    else:
        leaves.append(
            {
                "id": "packaging.no-runtime-dependencies",
                "status": "failed",
                "message": f"unexpected dependency metadata: {requires!r}"[:1000],
            }
        )

    for item in CASES:
        observed = execute_script(item.source, timeout_sec=item.timeout_sec)
        if observed.ok and observed.value == item.expected:
            leaves.append({"id": item.leaf_id, "status": "passed"})
            continue
        leaves.append(
            {
                "id": item.leaf_id,
                "status": "failed",
                "message": (
                    f"expected {item.expected!r}; observed ok={observed.ok!r} "
                    f"value={observed.value!r} exception={observed.exception_type!r}: "
                    f"{observed.exception_message!r}"
                )[:1000],
            }
        )

    assert len(leaves) == 69, len(leaves)
    print(json.dumps({"schema_version": "1.0", "leaves": leaves}, sort_keys=True))


if __name__ == "__main__":
    main()
