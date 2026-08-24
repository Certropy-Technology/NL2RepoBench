"""Child-side adapter for allowlisted attrs behavior scenarios."""

from __future__ import annotations

import argparse
import importlib.metadata
import json
import os
import sys
from typing import Any


def _type_name(exc: BaseException) -> str:
    return f"{type(exc).__module__}.{type(exc).__qualname__}"


def _modern_basics() -> dict[str, Any]:
    import attrs

    @attrs.define
    class User:
        name: str
        age: int = 0

    first = User("Ada")
    second = User("Ada")
    fields = attrs.fields(User)
    return {
        "repr": repr(first),
        "equal": first == second,
        "other_type_equal": first == ("Ada", 0),
        "field_names": [field.name for field in fields],
        "fields_from_instance": attrs.fields(first) is fields,
        "has_dict": hasattr(first, "__dict__"),
        "has_weakref": hasattr(first, "__weakref__"),
        "match_args": list(User.__match_args__),
    }


def _conversion_validation_order() -> dict[str, Any]:
    import attrs

    events: list[str] = []

    def convert(value: Any) -> int:
        events.append(f"convert:{value}")
        return int(str(value).strip())

    def validate(_instance: Any, _attribute: Any, value: int) -> None:
        events.append(f"validate:{value}")
        if value <= 0:
            raise ValueError("must be positive")

    @attrs.define
    class Counter:
        count: int = attrs.field(converter=convert, validator=validate)

    counter = Counter(" 4 ")
    counter.count = "5"
    before_failure = counter.count
    try:
        counter.count = "-1"
    except Exception as exc:
        failure = _type_name(exc)
    else:
        failure = None
    return {
        "value": counter.count,
        "before_failure": before_failure,
        "failure": failure,
        "events": events,
    }


def _factories() -> dict[str, Any]:
    import attrs

    @attrs.define
    class Inventory:
        prefix: str
        values: list[int] = attrs.field(factory=list)
        code: str = attrs.field(
            default=attrs.Factory(lambda self: f"{self.prefix}-1", takes_self=True)
        )

    first = Inventory("a")
    second = Inventory("b")
    first.values.append(3)
    return {
        "first": attrs.asdict(first),
        "second": attrs.asdict(second),
        "fresh": first.values is not second.values,
    }


def _keyword_alias() -> dict[str, Any]:
    import attrs

    @attrs.define
    class Secret:
        _name: str = attrs.field(alias="label")
        count: int = attrs.field(default=1, kw_only=True)

    value = Secret(label="Ada", count=2)
    try:
        Secret("Ada", 2)
    except Exception as exc:
        positional_error = _type_name(exc)
    else:
        positional_error = None
    fields = attrs.fields(Secret)
    return {
        "stored": [value._name, value.count],
        "aliases": [field.alias for field in fields],
        "kw_only": [field.kw_only for field in fields],
        "positional_error": positional_error,
    }


def _classic_compatibility() -> dict[str, Any]:
    import attr
    import attrs

    @attr.s
    class Classic:
        number = attr.ib(converter=int)
        enabled = attr.ib(default=True)

    value = Classic("7")
    return {
        "repr": repr(value),
        "number": value.number,
        "has_dict": hasattr(value, "__dict__"),
        "s_alias": attr.s is attr.attrs and attr.s is attr.attributes,
        "ib_alias": attr.ib is attr.attrib and attr.ib is attr.attr,
        "modern_alias": attr.define is attrs.define and attr.field is attrs.field,
        "dataclass_callable": callable(attr.dataclass),
    }


def _frozen_errors() -> dict[str, Any]:
    import attrs

    @attrs.frozen
    class FrozenValue:
        number: int

    value = FrozenValue(2)
    failures = []
    for operation in ("set", "delete"):
        try:
            if operation == "set":
                value.number = 3
            else:
                del value.number
        except Exception as exc:
            failures.append([_type_name(exc), str(exc), list(exc.args)])
    return {
        "failures": failures,
        "equal_hash": hash(value) == hash(FrozenValue(2)),
    }


def _assignment_hooks() -> dict[str, Any]:
    import attrs

    @attrs.define
    class Config:
        count: int = attrs.field(
            converter=int,
            validator=attrs.validators.ge(0),
        )
        raw: object = attrs.field(on_setattr=attrs.setters.NO_OP)

    config = Config("2", "initial")
    config.count = "7"
    config.raw = {"unconverted": True}
    try:
        config.count = "-1"
    except Exception as exc:
        failure = _type_name(exc)
    else:
        failure = None
    return {"count": config.count, "raw": config.raw, "failure": failure}


def _validator_composition() -> dict[str, Any]:
    import attrs

    values_validator = attrs.validators.deep_iterable(
        attrs.validators.instance_of(int),
        attrs.validators.instance_of(list),
    )

    @attrs.define
    class Payload:
        values: list[int] = attrs.field(validator=values_validator)
        name: str = attrs.field(
            validator=attrs.validators.and_(
                attrs.validators.instance_of(str),
                attrs.validators.matches_re(r"[a-z]+"),
            )
        )

    valid = Payload([1, 2], "alpha")
    failures = []
    for args in (([1, "bad"], "alpha"), ([1], "Alpha1")):
        try:
            Payload(*args)
        except Exception as exc:
            failures.append(_type_name(exc))
    either = attrs.validators.or_(
        attrs.validators.instance_of(int), attrs.validators.instance_of(str)
    )
    attribute = attrs.fields(Payload).name
    either(valid, attribute, "ok")
    try:
        either(valid, attribute, [])
    except Exception as exc:
        or_failure = _type_name(exc)
    else:
        or_failure = None
    return {"values": valid.values, "failures": failures, "or_failure": or_failure}


def _validator_state() -> dict[str, Any]:
    import attr
    import attrs

    @attrs.define
    class Checked:
        number: int = attrs.field(validator=attrs.validators.instance_of(int))

    states = [attrs.validators.get_disabled()]
    with attrs.validators.disabled():
        states.append(attrs.validators.get_disabled())
        with attrs.validators.disabled():
            states.append(attrs.validators.get_disabled())
            accepted = Checked("not-an-int").number
        states.append(attrs.validators.get_disabled())
    states.append(attrs.validators.get_disabled())
    try:
        Checked("not-an-int")
    except Exception as exc:
        restored_failure = _type_name(exc)
    else:
        restored_failure = None
    return {
        "states": states,
        "accepted": accepted,
        "restored_failure": restored_failure,
        "legacy_enabled": attr.get_run_validators(),
    }


def _converter_helpers() -> dict[str, Any]:
    import attrs

    pipe = attrs.converters.pipe(str.strip, int)
    optional = attrs.converters.optional(pipe)
    defaulted = attrs.converters.default_if_none(factory=lambda: ["new"])
    bool_values = [
        attrs.converters.to_bool(value)
        for value in (True, "yes", "1", 1, False, "off", "0", 0)
    ]
    try:
        attrs.converters.to_bool("maybe")
    except Exception as exc:
        failure = _type_name(exc)
    else:
        failure = None
    first = defaulted(None)
    second = defaulted(None)
    return {
        "pipe": pipe(" 12 "),
        "optional_none": optional(None),
        "optional_value": optional(" 4 "),
        "bools": bool_values,
        "invalid": failure,
        "factory_fresh": first == second and first is not second,
    }


def _collection_conversion() -> dict[str, Any]:
    import attr
    import attrs

    @attrs.define
    class Item:
        value: int

    @attrs.define
    class Bag:
        items: tuple[Item, ...]
        mapping: dict[str, Item]

    bag = Bag((Item(1), Item(2)), {"last": Item(3)})
    modern = attrs.asdict(bag)
    classic = attr.asdict(bag)
    retained = attr.asdict(bag, retain_collection_types=True)
    return {
        "modern": modern,
        "modern_items_type": type(modern["items"]).__name__,
        "classic": classic,
        "classic_items_type": type(classic["items"]).__name__,
        "retained_items_type": type(retained["items"]).__name__,
        "tuple": attrs.astuple(bag),
    }


def _field_introspection() -> dict[str, Any]:
    import attrs

    @attrs.define
    class Record:
        value: int = attrs.field(metadata={"role": "id"})

    fields = attrs.fields(Record)
    field = fields.value
    try:
        field.metadata["role"] = "changed"
    except Exception as exc:
        metadata_error = _type_name(exc)
    else:
        metadata_error = None
    renamed = field.evolve(name="_identifier")
    explicit = field.evolve(alias="external").evolve(name="other")
    return {
        "indexed_identity": fields[0] is field,
        "dict_identity": attrs.fields_dict(Record)["value"] is field,
        "metadata": dict(field.metadata),
        "metadata_error": metadata_error,
        "renamed": [renamed.name, renamed.alias, renamed.alias_is_default],
        "explicit": [explicit.name, explicit.alias, explicit.alias_is_default],
    }


def _evolve_behavior() -> dict[str, Any]:
    import attrs

    @attrs.define
    class Account:
        _name: str = attrs.field(converter=str.strip)
        token: str = attrs.field(default="fixed", init=False)

    original = Account(" Ada ")
    changed = attrs.evolve(original, name=" Grace ")
    failures = []
    for changes in ({"token": "new"}, {"unknown": 1}):
        try:
            attrs.evolve(original, **changes)
        except Exception as exc:
            failures.append(_type_name(exc))
    return {
        "original": [original._name, original.token],
        "changed": [changed._name, changed.token],
        "distinct": original is not changed,
        "failures": failures,
    }


def _inheritance_order() -> dict[str, Any]:
    import attrs

    @attrs.define
    class Base:
        base: int

    @attrs.define
    class Child(Base):
        child: int = 2

    fields = attrs.fields(Child)
    value = Child(1)
    return {
        "repr": repr(value),
        "names": [field.name for field in fields],
        "inherited": [field.inherited for field in fields],
        "has": [attrs.has(Base), attrs.has(Child), attrs.has(object)],
    }


def _make_class_behavior() -> dict[str, Any]:
    import attrs

    Point = attrs.make_class(
        "Point",
        {
            "x": attrs.field(converter=int),
            "y": attrs.field(default=0),
        },
        slots=True,
    )
    point = Point("3")
    return {
        "repr": repr(point),
        "values": [point.x, point.y],
        "fields": [field.name for field in attrs.fields(Point)],
        "slotted": not hasattr(point, "__dict__"),
    }


def _ordering_hashing() -> dict[str, Any]:
    import attrs

    @attrs.frozen(order=True)
    class Score:
        value: int

    @attrs.define
    class Mutable:
        value: int

    first = Score(1)
    second = Score(2)
    try:
        hash(Mutable(1))
    except Exception as exc:
        mutable_hash_error = _type_name(exc)
    else:
        mutable_hash_error = None
    return {
        "ordered": [first < second, second > first, first <= Score(1)],
        "equal_hash": hash(first) == hash(Score(1)),
        "mutable_hash_error": mutable_hash_error,
    }


def _resolve_types() -> dict[str, Any]:
    import attrs

    @attrs.define
    class Node:
        child: "Node | None" = None

    before = attrs.fields(Node).child.type
    returned = attrs.resolve_types(Node, localns={"Node": Node})
    after = attrs.fields(Node).child.type
    return {
        "before_is_string": isinstance(before, str),
        "same_class": returned is Node,
        "resolved": after == Node | None,
    }


def _value_serializer() -> dict[str, Any]:
    import attrs

    @attrs.define
    class Record:
        number: int
        label: str

    calls: list[list[Any]] = []

    def serialize(_instance: Any, attribute: Any, value: Any) -> Any:
        calls.append([attribute.name, value])
        if isinstance(value, int):
            return value * 2
        return value.upper()

    converted = attrs.asdict(Record(3, "alpha"), value_serializer=serialize)
    return {"converted": converted, "calls": calls}


def _init_hooks() -> dict[str, Any]:
    import attrs

    events: list[str] = []

    def convert(value: Any) -> int:
        events.append("convert")
        return int(value)

    def validate(_instance: Any, _attribute: Any, _value: Any) -> None:
        events.append("validate")

    @attrs.define
    class Derived:
        source: int = attrs.field(converter=convert, validator=validate)
        doubled: int = attrs.field(default=0, init=False)

        def __attrs_pre_init__(self) -> None:
            events.append("pre")

        def __attrs_post_init__(self) -> None:
            events.append("post")
            self.doubled = self.source * 2

    value = Derived("4")
    return {"events": events, "values": [value.source, value.doubled]}


def _version_aliases() -> dict[str, Any]:
    import attr
    import attrs

    info = attrs.__version_info__
    return {
        "distribution": importlib.metadata.version("attrs"),
        "versions": [attr.__version__, attrs.__version__],
        "version_info": [info.year, info.minor, info.micro, info.releaselevel],
        "version_comparison": info == (26, 1, 0, "final") and info > (26, 0),
        "exception_identity": (
            attr.exceptions.FrozenInstanceError
            is attrs.exceptions.FrozenInstanceError
        ),
        "converter_identity": attr.converters.pipe is attrs.converters.pipe,
        "validator_identity": attr.validators.instance_of is attrs.validators.instance_of,
        "required_exports": all(
            hasattr(attrs, name)
            for name in ("define", "field", "fields", "asdict", "validators", "inspect")
        ),
    }


SCENARIOS = {
    "modern-basics": _modern_basics,
    "conversion-validation-order": _conversion_validation_order,
    "factories": _factories,
    "keyword-alias": _keyword_alias,
    "classic-compatibility": _classic_compatibility,
    "frozen-errors": _frozen_errors,
    "assignment-hooks": _assignment_hooks,
    "validator-composition": _validator_composition,
    "validator-state": _validator_state,
    "converter-helpers": _converter_helpers,
    "collection-conversion": _collection_conversion,
    "field-introspection": _field_introspection,
    "evolve-behavior": _evolve_behavior,
    "inheritance-order": _inheritance_order,
    "make-class": _make_class_behavior,
    "ordering-hashing": _ordering_hashing,
    "resolve-types": _resolve_types,
    "value-serializer": _value_serializer,
    "init-hooks": _init_hooks,
    "version-aliases": _version_aliases,
}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate-site", required=True)
    parser.add_argument("--request", required=True)
    args = parser.parse_args()
    site = os.path.realpath(args.candidate_site)
    if site != "/tmp/candidate-site" or not os.path.isdir(site):
        raise ValueError("candidate site is unavailable")
    sys.path.insert(0, site)
    request = json.loads(args.request)
    if set(request) != {"schema_version", "scenario"}:
        raise ValueError("invalid scenario request fields")
    if request["schema_version"] != "1.0":
        raise ValueError("unsupported scenario schema")
    scenario = request["scenario"]
    if scenario not in SCENARIOS:
        raise ValueError("scenario is not allowlisted")
    value = SCENARIOS[scenario]()
    print(json.dumps({"ok": True, "value": value}, sort_keys=True, separators=(",", ":")))


try:
    main()
except BaseException as exc:
    print(
        json.dumps(
            {
                "ok": False,
                "exception_type": _type_name(exc),
                "exception_message": str(exc),
            },
            sort_keys=True,
            separators=(",", ":"),
        )
    )
