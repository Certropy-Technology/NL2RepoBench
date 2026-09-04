from __future__ import annotations

import dataclasses
import json
import math
import sys
from collections.abc import Iterator
from typing import Annotated, Literal, get_args, get_origin

sys.path.insert(0, "/tmp/candidate-site")

try:
    import annotated_types as at
except Exception:  # noqa: BLE001 - a broken candidate still gets every fixed leaf
    at = None  # type: ignore[assignment]


def _field_names(cls: type[object]) -> tuple[str, ...]:
    return tuple(field.name for field in dataclasses.fields(cls))


def _run() -> list[dict[str, object]]:
    tests: list[tuple[str, object]] = []

    def add(name: str, fn: object) -> None:
        tests.append((name, fn))

    add("exports-exact", lambda: at.__all__ == (
        "BaseMetadata", "GroupedMetadata", "Gt", "Ge", "Lt", "Le",
        "Interval", "MultipleOf", "MinLen", "MaxLen", "Len", "Timezone",
        "Predicate", "LowerCase", "UpperCase", "IsDigits", "IsFinite",
        "IsNotFinite", "IsNan", "IsNotNan", "IsInfinite", "IsNotInfinite",
        "doc", "DocInfo", "__version__",
    ))
    add("version", lambda: at.__version__ == "0.8.0")
    add("base-metadata-slots", lambda: not hasattr(at.BaseMetadata(), "__dict__"))
    add("root-compatibility-attributes", lambda: all(
        hasattr(at, name) for name in ("Unit", "IsDigit", "IsAscii", "Not", "Doc")
    ))

    add("Gt-value", lambda: (at.Gt(4).gt == 4 and repr(at.Gt(4)) == "Gt(gt=4)"))
    add("Ge-value", lambda: at.Ge(4) == at.Ge(4) and at.Ge(4) != at.Ge(5))
    add("Lt-value", lambda: at.Lt("z").lt == "z")
    add("Le-value", lambda: at.Le(4).le == 4)
    add("bound-classes-frozen-slotted", lambda: all(
        not hasattr(cls(1), "__dict__") for cls in (at.Gt, at.Ge, at.Lt, at.Le)
    ))
    add("multiple-of", lambda: at.MultipleOf(3).multiple_of == 3)
    add("min-max-len", lambda: (
        at.MinLen(2).min_length == 2 and at.MaxLen(5).max_length == 5
    ))
    add("timezone", lambda: at.Timezone(None).tz is None and at.Timezone(...).tz is Ellipsis)
    add("unit", lambda: at.Unit("m/s").unit == "m/s")
    add("metadata-dataclass-fields", lambda: (
        _field_names(at.Gt) == ("gt",)
        and _field_names(at.MultipleOf) == ("multiple_of",)
        and _field_names(at.Timezone) == ("tz",)
        and _field_names(at.Unit) == ("unit",)
    ))
    add("metadata-frozen", lambda: _frozen_assignment(at.Gt(1), "gt"))

    add("interval-order", lambda: tuple(type(x) for x in at.Interval(gt=1, ge=2, lt=3, le=4)) == (
        at.Gt, at.Ge, at.Lt, at.Le
    ))
    add("interval-values", lambda: tuple(x.__dict__ if hasattr(x, "__dict__") else dataclasses.asdict(x)
        for x in at.Interval(gt=1, ge=2, lt=3, le=4)) == (
            {"gt": 1}, {"ge": 2}, {"lt": 3}, {"le": 4}
        ))
    add("interval-none-empty", lambda: tuple(at.Interval()) == ())
    add("interval-keyword-only", lambda: _raises_type_error(lambda: at.Interval(1)))
    add("len-lower-only", lambda: tuple(at.Len(3)) == (at.MinLen(3),))
    add("len-upper-only", lambda: tuple(at.Len(0, 4)) == (at.MaxLen(4),))
    add("len-both-and-empty", lambda: (
        tuple(at.Len(3, 5)) == (at.MinLen(3), at.MaxLen(5))
        and tuple(at.Len()) == ()
    ))
    add("len-frozen", lambda: _frozen_assignment(at.Len(1), "min_length"))

    add("grouped-marker", lambda: at.Interval().__is_annotated_types_grouped_metadata__ is True)
    add("grouped-runtime-check", lambda: isinstance(at.Interval(), at.GroupedMetadata))
    add("grouped-iterator-yields", lambda: tuple(_StructuralGrouped()) == (at.Gt(0),))
    add("grouped-missing-iterator-rejected", lambda: _bad_grouped_subclass())
    add("grouped-base-iterator-error", lambda: _raises_not_implemented(_bare_grouped_iterator))
    add("grouped-structural-implementer", lambda: isinstance(_StructuralGrouped(), at.GroupedMetadata))

    add("predicate-stores-callable", lambda: at.Predicate(bool).func is bool)
    add("predicate-not-callable", lambda: not callable(at.Predicate(bool)))
    add("predicate-builtin-repr", lambda: repr(at.Predicate(str.isascii)) == "Predicate(str.isascii)")
    add("predicate-function-repr", lambda: repr(at.Predicate(math.isfinite)) in {
        "Predicate(math.isfinite)", "Predicate(isfinite)"
    })
    add("predicate-method-descriptor-repr", lambda: repr(at.Predicate(str.islower)) == "Predicate(str.islower)")
    add("predicate-lambda-repr", lambda: _predicate_lambda_repr())
    add("predicate-frozen", lambda: _frozen_assignment(at.Predicate(bool), "func"))

    add("not-call-true", lambda: at.Not(lambda x: x > 0)(-1) is True)
    add("not-call-false", lambda: at.Not(lambda x: x > 0)(1) is False)
    add("not-exposes-function", lambda: callable(at.Not(bool).func))

    add("lowercase-alias", lambda: _alias_has(at.LowerCase[str], str.islower))
    add("uppercase-alias", lambda: _alias_has(at.UpperCase[str], str.isupper))
    add("digit-alias", lambda: _alias_has(at.IsDigit[str], str.isdigit) and at.IsDigits is at.IsDigit)
    add("ascii-alias", lambda: _alias_has(at.IsAscii[str], str.isascii))
    add("finite-alias", lambda: _alias_has(at.IsFinite[float], math.isfinite))
    add("negative-finite-alias", lambda: _alias_has_not(at.IsNotFinite[float], math.isfinite))
    add("nan-alias", lambda: _alias_has(at.IsNan[float], math.isnan))
    add("negative-nan-alias", lambda: _alias_has_not(at.IsNotNan[float], math.isnan))
    add("infinite-alias", lambda: _alias_has(at.IsInfinite[float], math.isinf))
    add("negative-infinite-alias", lambda: _alias_has_not(at.IsNotInfinite[float], math.isinf))
    add("alias-origin", lambda: get_origin(at.LowerCase[str]) is Annotated)
    add("alias-predicate-behavior", lambda: (
        get_args(at.LowerCase[str])[1].func("abc") is True
        and get_args(at.LowerCase[str])[1].func("ABC") is False
    ))

    add("doc-aliases", lambda: at.doc is at.Doc and at.DocInfo is at.Doc)
    add("doc-value", lambda: at.doc("A number").documentation == "A number")
    add("doc-slotted-or-compatible", lambda: hasattr(at.doc("x"), "documentation"))
    add("annotated-stacking", lambda: get_args(Annotated[at.LowerCase[str], "extra"])[1:] == (
        get_args(at.LowerCase[str])[1], "extra"
    ))

    add("comparison-equality", lambda: hash(at.Gt(1)) == hash(at.Gt(1)))
    add("interval-repr", lambda: repr(at.Interval(gt=1, le=4)) == "Interval(gt=1, ge=None, lt=None, le=4)")
    add("len-repr", lambda: repr(at.Len(3, 5)) == "Len(min_length=3, max_length=5)")
    add("unit-repr", lambda: repr(at.Unit("kg")) == "Unit(unit='kg')")
    add("unknown-metadata-ignored-by-python", lambda: get_args(Annotated[int, object()])[0] is int)

    leaves: list[dict[str, object]] = []
    for name, fn in tests:
        try:
            result = fn()  # type: ignore[operator]
            if result is not True:
                raise AssertionError(f"check returned {result!r}")
        except Exception as exc:  # noqa: BLE001 - convert each leaf into a bounded result
            leaves.append({"id": name, "status": "failed", "message": f"{type(exc).__name__}: {exc}"})
        else:
            leaves.append({"id": name, "status": "passed"})
    if len(leaves) != 60:
        raise RuntimeError(f"verifier definition has {len(leaves)} leaves, expected 60")
    return leaves


def _frozen_assignment(value: object, name: str) -> bool:
    try:
        setattr(value, name, None)
    except (AttributeError, dataclasses.FrozenInstanceError):
        return True
    return False


def _raises_type_error(fn: object) -> bool:
    try:
        fn()  # type: ignore[operator]
    except TypeError:
        return True
    return False


def _raises_not_implemented(fn: object) -> bool:
    try:
        fn()  # type: ignore[operator]
    except NotImplementedError:
        return True
    return False


def _bad_grouped_subclass() -> bool:
    try:
        class _Bad(at.GroupedMetadata):
            pass
    except TypeError:
        return True
    return False


def _bare_grouped_iterator() -> Iterator[object]:
    class _BareGrouped(at.GroupedMetadata):  # type: ignore[union-attr]
        def __iter__(self) -> Iterator[object]:
            return super().__iter__()

    return iter(_BareGrouped())


class _StructuralGrouped:
    __is_annotated_types_grouped_metadata__: Literal[True] = True

    def __iter__(self) -> Iterator[object]:
        yield at.Gt(0)


def _alias_has(alias: object, func: object) -> bool:
    args = get_args(alias)
    return get_origin(alias) is Annotated and len(args) == 2 and isinstance(args[1], at.Predicate) and args[1].func is func


def _alias_has_not(alias: object, func: object) -> bool:
    args = get_args(alias)
    return (
        get_origin(alias) is Annotated
        and len(args) == 2
        and isinstance(args[1], at.Predicate)
        and isinstance(args[1].func, at.Not)
        and args[1].func.func is func
    )


def _predicate_lambda_repr() -> bool:
    fn = lambda value: bool(value)  # noqa: E731
    return repr(at.Predicate(fn)).startswith("Predicate(<function ")


if __name__ == "__main__":
    print(json.dumps({"schema_version": "1.0", "leaves": _run()}, sort_keys=True))
