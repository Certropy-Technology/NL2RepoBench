from __future__ import annotations

import contextlib
import importlib.metadata
import inspect
import io
import json
import os
import pickle
import sys
import warnings


CANDIDATE_SITE = os.environ.get(
    "NL2REPO_TYPING_EXTENSIONS_CANDIDATE_SITE", "/tmp/candidate-site"
)
if CANDIDATE_SITE not in sys.path:
    sys.path.insert(0, CANDIDATE_SITE)

import typing
import typing_extensions as te


def rendered(value):
    if isinstance(value, dict):
        return {str(key): rendered(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [rendered(item) for item in value]
    if isinstance(value, (set, frozenset)):
        return sorted(rendered(item) for item in value)
    if isinstance(value, bytes):
        return {"bytes_hex": value.hex()}
    if isinstance(value, type):
        return f"{value.__module__}.{value.__qualname__}"
    if value is Ellipsis:
        return "..."
    if value is te.NoDefault:
        return "typing_extensions.NoDefault"
    return value


def type_form(value):
    return {
        "repr": repr(value),
        "origin": repr(te.get_origin(value)),
        "args": [repr(item) for item in te.get_args(value)],
    }


def error(callable_, *args, **kwargs):
    try:
        callable_(*args, **kwargs)
    except Exception as exc:
        return {"type": type(exc).__name__}
    return None


def error_with_message(callable_, *args, **kwargs):
    try:
        callable_(*args, **kwargs)
    except Exception as exc:
        return {"type": type(exc).__name__, "message": str(exc)}
    return None


def package_identity():
    return {
        "distribution_version": importlib.metadata.version("typing_extensions"),
        "module": te.__name__,
        "file_name": os.path.basename(te.__file__),
    }


def export_surface():
    required = [
        "Annotated", "Concatenate", "Doc", "Literal", "LiteralString",
        "Never", "NoDefault", "NotRequired", "ParamSpec", "Protocol",
        "ReadOnly", "Required", "Self", "Sentinel", "TypeAliasType",
        "TypeGuard", "TypeIs", "TypeVarTuple", "TypedDict", "Unpack",
        "assert_never", "assert_type", "clear_overloads", "dataclass_transform",
        "deprecated", "evaluate_forward_ref", "final", "get_annotations",
        "get_args", "get_origin", "get_original_bases", "get_overloads",
        "get_protocol_members", "get_type_hints", "is_protocol", "is_typeddict",
        "overload", "override", "reveal_type", "runtime_checkable",
    ]
    return {
        "required": {name: name in te.__all__ and hasattr(te, name) for name in required},
        "all_unique": len(te.__all__) == len(set(te.__all__)),
    }


def standard_reexports():
    names = (
        "Any", "Callable", "ClassVar", "Final", "Generic", "NamedTuple",
        "NewType", "Optional", "TypeVar", "Union", "get_args", "get_origin",
        "get_type_hints", "no_type_check",
    )
    return {name: getattr(te, name) is getattr(typing, name) for name in names}


def literal_and_qualifiers():
    return {
        "literal": type_form(te.Literal[1, "x", None]),
        "final": type_form(te.Final[int]),
        "classvar": type_form(te.ClassVar[str]),
        "required": type_form(te.Required[int]),
        "not_required": type_form(te.NotRequired[str]),
        "read_only": type_form(te.ReadOnly[bytes]),
    }


def annotated_runtime():
    inner = te.Annotated[int, "first"]
    nested = te.Annotated[inner, {"level": 2}, 3]
    return {
        "form": type_form(nested),
        "metadata": rendered(nested.__metadata__),
        "origin_attribute": repr(nested.__origin__),
        "hashable_error": error(hash, nested),
    }


def guard_forms():
    return {
        "type_guard": type_form(te.TypeGuard[list[str]]),
        "type_is": type_form(te.TypeIs[tuple[int, ...]]),
        "literal_string": repr(te.LiteralString),
        "never": repr(te.Never),
        "self": repr(te.Self),
    }


def unpack_and_concatenate():
    parameters = te.ParamSpec("Parameters")
    unpacked = te.Unpack[tuple[int, str]]
    concatenated = te.Concatenate[bytes, parameters]
    return {
        "unpack": type_form(unpacked),
        "concatenate": type_form(concatenated),
        "paramspec_args_origin": repr(te.get_origin(parameters.args)),
        "paramspec_kwargs_origin": repr(te.get_origin(parameters.kwargs)),
    }


def type_alias_runtime():
    item = te.TypeVar("Item")
    pair = te.TypeAliasType("Pair", tuple[item, item], type_params=(item,))
    specialized = pair[int]
    return {
        "repr": repr(pair),
        "name": pair.__name__,
        "module": pair.__module__,
        "value": repr(pair.__value__),
        "type_params": [repr(value) for value in pair.__type_params__],
        "specialized": type_form(specialized),
        "cannot_instantiate": error(pair),
    }


def type_parameter_defaults():
    type_var = te.TypeVar("Value", default=str)
    no_default = te.TypeVar("Plain")
    params = te.ParamSpec("Params", default=[int, str])
    variadic = te.TypeVarTuple("Items", default=te.Unpack[tuple[int, ...]])
    return {
        "type_var": [repr(type_var.__default__), type_var.has_default()],
        "no_default": [repr(no_default.__default__), no_default.has_default()],
        "paramspec": [repr(params.__default__), params.has_default()],
        "typevartuple": [repr(variadic.__default__), variadic.has_default()],
        "sentinel_repr": repr(te.NoDefault),
    }


def typed_dict_metadata():
    Payload = te.TypedDict(
        "Payload",
        {
            "identifier": int,
            "nickname": te.NotRequired[str],
            "checksum": te.ReadOnly[bytes],
        },
    )

    return {
        "is_typeddict": te.is_typeddict(Payload),
        "required": Payload.__required_keys__,
        "optional": Payload.__optional_keys__,
        "readonly": Payload.__readonly_keys__,
        "mutable": Payload.__mutable_keys__,
        "total": Payload.__total__,
        "annotations": {key: repr(value) for key, value in Payload.__annotations__.items()},
        "runtime_value": Payload(identifier=7, checksum=b"x"),
        "instance_error": error(isinstance, {}, Payload),
    }


def typed_dict_inheritance():
    Base = te.TypedDict(
        "Base", {"optional": int, "forced": te.Required[str]}, total=False
    )

    class Child(Base):
        current: bool

    return {
        "required": Child.__required_keys__,
        "optional": Child.__optional_keys__,
        "orig_bases": [repr(value) for value in te.get_original_bases(Child)],
        "dict_subclass": issubclass(Child, dict),
        "factory": Child(optional=1, forced="yes", current=True),
    }


def protocol_introspection():
    @te.runtime_checkable
    class Closable(te.Protocol):
        label: str

        def close(self) -> None: ...

    class Resource:
        label = "ready"

        def close(self):
            return None

    return {
        "is_protocol": te.is_protocol(Closable),
        "members": te.get_protocol_members(Closable),
        "runtime": Closable._is_runtime_protocol,
        "instance": isinstance(Resource(), Closable),
        "subclass_error": error(issubclass, Resource, Closable),
        "non_protocol_members_error": error(te.get_protocol_members, Resource),
    }


def callable_protocol_runtime():
    @te.runtime_checkable
    class Runner(te.Protocol):
        def run(self, value: int) -> str: ...

    class Good:
        def run(self, value):
            return str(value)

    class Missing:
        pass

    return {
        "members": te.get_protocol_members(Runner),
        "good_instance": isinstance(Good(), Runner),
        "good_subclass": issubclass(Good, Runner),
        "missing_instance": isinstance(Missing(), Runner),
        "missing_subclass": issubclass(Missing, Runner),
    }


def protocol_errors():
    class Plain(te.Protocol):
        def method(self): ...

    class Nominal:
        pass

    return {
        "instance": error(isinstance, Nominal(), Plain),
        "runtime_checkable": error(te.runtime_checkable, Nominal),
        "members": error(te.get_protocol_members, Nominal),
    }


def overload_registry():
    @te.overload
    def transform(value: int) -> str: ...

    @te.overload
    def transform(value: str) -> int: ...

    def transform(value):
        return str(value) if isinstance(value, int) else len(value)

    overloads = te.get_overloads(transform)
    before = [str(inspect.signature(item)) for item in overloads]
    annotations = [
        {key: repr(value) for key, value in item.__annotations__.items()}
        for item in overloads
    ]
    te.clear_overloads()
    return {
        "before": before,
        "annotations": annotations,
        "after": te.get_overloads(transform),
        "implementation": [transform(5), transform("abcd")],
    }


def decorator_markers():
    @te.final
    class Closed:
        @te.final
        def stop(self):
            return "stopped"

    class Parent:
        def method(self):
            return "parent"

    class Child(Parent):
        @te.override
        def method(self):
            return "child"

    return {
        "class_final": Closed.__final__,
        "method_final": Closed.stop.__final__,
        "override": Child.method.__override__,
        "calls": [Closed().stop(), Child().method()],
    }


def deprecated_function():
    @te.deprecated("use replacement()", category=FutureWarning)
    def old(value: int) -> int:
        return value + 1

    with warnings.catch_warnings(record=True) as captured:
        warnings.simplefilter("always")
        result = old(4)
    return {
        "result": result,
        "marker": old.__deprecated__,
        "warnings": [
            [type(item.message).__name__, str(item.message)] for item in captured
        ],
    }


def deprecated_class():
    @te.deprecated("Legacy is obsolete")
    class Legacy:
        def __init__(self, value):
            self.value = value

    with warnings.catch_warnings(record=True) as captured:
        warnings.simplefilter("always")
        instance = Legacy(9)
    return {
        "value": instance.value,
        "marker": Legacy.__deprecated__,
        "warning": [type(captured[0].message).__name__, str(captured[0].message)],
    }


def dataclass_transform_marker():
    @te.dataclass_transform(
        eq_default=False,
        order_default=True,
        kw_only_default=True,
        frozen_default=True,
        field_specifiers=(str, int),
        custom="value",
    )
    def model(cls):
        return cls

    marker = model.__dataclass_transform__
    return {
        "eq_default": marker["eq_default"],
        "order_default": marker["order_default"],
        "kw_only_default": marker["kw_only_default"],
        "frozen_default": marker["frozen_default"],
        "field_specifiers": [value.__name__ for value in marker["field_specifiers"]],
        "kwargs": marker["kwargs"],
    }


def type_hints_extras():
    class Record(te.TypedDict):
        name: te.Required[str]
        note: te.NotRequired[te.Annotated[str, te.Doc("display note")]]

    plain = te.get_type_hints(Record)
    extras = te.get_type_hints(Record, include_extras=True)
    return {
        "plain": {key: repr(value) for key, value in plain.items()},
        "extras": {key: repr(value) for key, value in extras.items()},
    }


def original_bases():
    item = te.TypeVar("Item")

    class Box(te.Generic[item]):
        pass

    class IntBox(Box[int]):
        pass

    class Plain(list[int]):
        pass

    return {
        "generic": [repr(value) for value in te.get_original_bases(IntBox)],
        "builtin": [repr(value) for value in te.get_original_bases(Plain)],
        "fallback": [repr(value) for value in te.get_original_bases(object)],
    }


def assertion_helpers():
    value = {"answer": 42}
    stderr = io.StringIO()
    with contextlib.redirect_stderr(stderr):
        revealed = te.reveal_type(value)
    return {
        "assert_identity": te.assert_type(value, dict) is value,
        "reveal_identity": revealed is value,
        "reveal_stderr": stderr.getvalue().strip(),
        "assert_never_short": error_with_message(te.assert_never, "unexpected"),
        "assert_never_long": error_with_message(te.assert_never, "x" * 200),
    }


def new_type_runtime():
    UserId = te.NewType("UserId", int)
    value = UserId(12)
    return {
        "name": UserId.__name__,
        "qualname": UserId.__qualname__,
        "supertype": repr(UserId.__supertype__),
        "call": value,
        "same_object": value is UserId(value),
        "repr": repr(UserId),
        "instance_error": error(isinstance, value, UserId),
    }


def named_tuple_runtime():
    class Point(te.NamedTuple):
        x: int
        y: int = 5

    point = Point(2)
    return {
        "value": point,
        "fields": Point._fields,
        "defaults": Point._field_defaults,
        "annotations": {key: repr(value) for key, value in Point.__annotations__.items()},
        "asdict": point._asdict(),
        "replace": point._replace(y=8),
        "tuple_instance": isinstance(point, tuple),
    }


def doc_metadata():
    form = te.Annotated[int, te.Doc("positive count")]
    document = te.get_args(form)[1]
    return {
        "form": repr(form),
        "doc": document.documentation,
        "doc_repr": repr(document),
        "origin": repr(te.get_origin(form)),
    }


def get_annotations_runtime():
    namespace = {"te": te}
    exec(
        "from __future__ import annotations\n"
        "def convert(value: list[int]) -> te.Annotated[str, 'result']: ...\n",
        namespace,
    )
    function = namespace["convert"]
    raw = te.get_annotations(function, eval_str=False)
    evaluated = te.get_annotations(function, globals=namespace, eval_str=True)
    return {
        "raw": raw,
        "evaluated": {key: repr(value) for key, value in evaluated.items()},
    }


def evaluate_forward_reference():
    reference = typing.ForwardRef("list[Item]")
    globals_ = {"Item": int}
    evaluated = te.evaluate_forward_ref(reference, globals=globals_)
    unresolved = error(te.evaluate_forward_ref, typing.ForwardRef("Missing"), globals={})
    return {
        "evaluated": repr(evaluated),
        "origin": repr(te.get_origin(evaluated)),
        "args": [repr(value) for value in te.get_args(evaluated)],
        "unresolved": unresolved,
    }


def no_type_check_runtime():
    @te.no_type_check
    def function(value: "Missing") -> "Unknown":
        return value

    class Parent:
        def method(self, value: int) -> str:
            return str(value)

    decorated = te.no_type_check(Parent)
    return {
        "function_marker": function.__no_type_check__,
        "function_hints": te.get_type_hints(function),
        "class_marker": decorated.__no_type_check__,
        "method_marker": decorated.method.__no_type_check__,
    }


def sentinel_runtime():
    missing = te.Sentinel("MISSING")
    same_name = te.Sentinel("MISSING")
    custom = te.Sentinel("CUSTOM", repr="not-set")
    return {
        "name": missing._name,
        "repr": repr(missing),
        "custom_repr": repr(custom),
        "bool": bool(missing),
        "identity": missing is same_name,
        "equality": missing == same_name,
        "class_repr": repr(te.Sentinel),
        "pickle_error": error(pickle.dumps, missing),
        "call_error": error(missing),
        "left_union": repr(int | missing),
        "right_union": repr(missing | str),
    }


def buffer_runtime():
    values = [b"abc", bytearray(b"abc"), memoryview(b"abc"), "abc"]
    return {
        "repr": repr(te.Buffer),
        "instances": [isinstance(value, te.Buffer) for value in values],
        "subclasses": [issubclass(value, te.Buffer) for value in (bytes, bytearray, memoryview, str)],
    }


def special_form_errors():
    return {
        "literal_instance": error(isinstance, 1, te.Literal[1]),
        "annotated_instance": error(isinstance, 1, te.Annotated[int, "x"]),
        "type_guard_parameters": error(te.TypeGuard.__getitem__, (int, str)),
        "required_parameters": error(te.Required.__getitem__, (int, str)),
        "unpack_parameters": error(te.Unpack.__getitem__, (int, str)),
    }


def typed_dict_errors():
    return {
        "duplicate_closed_extra": error(
            te.TypedDict, "Bad", {"x": int}, closed=True, extra_items=str
        ),
        "bad_field_map": error(te.TypedDict, "Bad", 42),
        "instance": error(isinstance, {}, te.TypedDict("Empty", {})),
    }


OPERATIONS = {
    name: value
    for name, value in globals().copy().items()
    if callable(value)
    and name
    in {
        "package_identity", "export_surface", "standard_reexports",
        "literal_and_qualifiers", "annotated_runtime", "guard_forms",
        "unpack_and_concatenate", "type_alias_runtime", "type_parameter_defaults",
        "typed_dict_metadata", "typed_dict_inheritance", "protocol_introspection",
        "callable_protocol_runtime", "protocol_errors", "overload_registry",
        "decorator_markers", "deprecated_function", "deprecated_class",
        "dataclass_transform_marker", "type_hints_extras", "original_bases",
        "assertion_helpers", "new_type_runtime", "named_tuple_runtime",
        "doc_metadata", "get_annotations_runtime", "evaluate_forward_reference",
        "no_type_check_runtime", "sentinel_runtime",
        "buffer_runtime", "special_form_errors", "typed_dict_errors",
    }
}


def main():
    for line in sys.stdin:
        try:
            request = json.loads(line)
            request_id = request["id"]
            operation = request["operation"]
            result = rendered(OPERATIONS[operation]())
            response = {"id": request_id, "ok": True, "result": result}
        except Exception as exc:
            response = {
                "id": request.get("id") if isinstance(request, dict) else None,
                "ok": False,
                "error": {"type": type(exc).__name__, "message": str(exc)},
            }
        print(json.dumps(response, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
