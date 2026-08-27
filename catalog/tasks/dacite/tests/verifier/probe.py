from __future__ import annotations

import dataclasses
import enum
import importlib
import importlib.metadata
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, Generic, List, Literal, NewType, Optional, Set, Tuple, Type, TypeVar, Union


sys.path.insert(0, "/tmp/candidate-site")
dependency_root = os.environ.get("NL2REPO_CANDIDATE_DEPENDENCIES")
if dependency_root:
    sys.path.insert(1, dependency_root)


def _type_name(value: Any) -> str:
    module = getattr(value, "__module__", "")
    name = getattr(value, "__qualname__", getattr(value, "__name__", str(value)))
    return f"{module}.{name}" if module else name


def _encode(value: Any) -> Any:
    if dataclasses.is_dataclass(value) and not isinstance(value, type):
        return {
            "__class__": type(value).__name__,
            "fields": {field.name: _encode(getattr(value, field.name)) for field in dataclasses.fields(value)},
        }
    if isinstance(value, enum.Enum):
        return {
            "__enum__": f"{type(value).__name__}.{value.name}",
            "value": _encode(value.value),
        }
    if isinstance(value, tuple):
        return {"__tuple__": [_encode(item) for item in value]}
    if isinstance(value, (set, frozenset)):
        encoded = [_encode(item) for item in value]
        encoded.sort(key=lambda item: json.dumps(item, sort_keys=True))
        return {"__set__": encoded}
    if isinstance(value, list):
        return [_encode(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _encode(item) for key, item in value.items()}
    if isinstance(value, type):
        return {"__type__": _type_name(value)}
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    return {"__type__": _type_name(type(value))}


def _default_factory(name: str):
    factories = {"list": list, "dict": dict, "set": set, "tuple": tuple}
    return factories[name]


def _build_registry(request: dict[str, Any]) -> dict[str, Any]:
    registry: dict[str, Any] = {}
    for name in request.get("typevars", []):
        registry[name] = TypeVar(name)
    for definition in request.get("enums", []):
        registry[definition["name"]] = enum.Enum(definition["name"], definition["members"])
    for definition in request.get("newtypes", []):
        registry[definition["name"]] = NewType(definition["name"], _parse_type(definition["type"], registry))
    for definition in request.get("classes", []):
        fields = []
        for field_definition in definition["fields"]:
            field_type = _parse_type(field_definition["type"], registry)
            options: dict[str, Any] = {}
            if "default" in field_definition:
                options["default"] = field_definition["default"]
            if "default_factory" in field_definition:
                options["default_factory"] = _default_factory(field_definition["default_factory"])
            if field_definition.get("init") is False:
                options["init"] = False
            fields.append(
                (field_definition["name"], field_type, dataclasses.field(**options))
                if options
                else (field_definition["name"], field_type)
            )
        namespace: dict[str, Any] = {"__module__": "__main__"}
        post_init = definition.get("post_init")
        if post_init == "sum-total":
            def __post_init__(self: Any) -> None:
                object.__setattr__(self, "total", self.left + self.right)

            namespace["__post_init__"] = __post_init__
        elif post_init == "copy-raw":
            def __post_init__(self: Any, raw: Any) -> None:
                object.__setattr__(self, "value", raw)

            namespace["__post_init__"] = __post_init__
        generic_parameters = tuple(registry[name] for name in definition.get("generic", []))
        bases = (Generic[generic_parameters],) if generic_parameters else ()
        registry[definition["name"]] = dataclasses.make_dataclass(
            definition["name"],
            fields,
            bases=bases,
            frozen=definition.get("frozen", False),
            namespace=namespace,
        )
    return registry


def _parse_type(spec: Any, registry: dict[str, Any]) -> Any:
    builtins = {
        "Any": Any,
        "None": type(None),
        "bool": bool,
        "bytes": bytes,
        "complex": complex,
        "dict": dict,
        "enum.Enum": enum.Enum,
        "float": float,
        "int": int,
        "list": list,
        "set": set,
        "str": str,
        "tuple": tuple,
    }
    if isinstance(spec, str):
        if spec in builtins:
            return builtins[spec]
        if spec in registry:
            return registry[spec]
        raise KeyError(f"unknown type spec: {spec}")
    if "ref" in spec:
        return registry[spec["ref"]]
    if "forward" in spec:
        return spec["forward"]
    if "enum" in spec:
        return registry[spec["enum"]]
    if "newtype" in spec:
        return registry[spec["newtype"]]
    if "typevar" in spec:
        return registry[spec["typevar"]]
    if "generic" in spec:
        generic = spec["generic"]
        arguments = tuple(_parse_type(item, registry) for item in generic["args"])
        return registry[generic["ref"]][arguments]
    if "initvar" in spec:
        return dataclasses.InitVar[_parse_type(spec["initvar"], registry)]
    if "optional" in spec:
        return Optional[_parse_type(spec["optional"], registry)]
    if "union" in spec:
        return Union[tuple(_parse_type(item, registry) for item in spec["union"])]
    if "list" in spec:
        return List[_parse_type(spec["list"], registry)]
    if "set" in spec:
        return Set[_parse_type(spec["set"], registry)]
    if "tuple" in spec:
        return Tuple[tuple(_parse_type(item, registry) for item in spec["tuple"])]
    if "tuple_variadic" in spec:
        return Tuple[_parse_type(spec["tuple_variadic"], registry), ...]
    if "dict" in spec:
        key, value = spec["dict"]
        return Dict[_parse_type(key, registry), _parse_type(value, registry)]
    if "literal" in spec:
        return Literal[tuple(spec["literal"])]
    if "type" in spec:
        return Type[_parse_type(spec["type"], registry)]
    raise KeyError(f"unknown type spec: {spec}")


def _hook(name: str):
    if name == "lower":
        return lambda value: value.lower()
    if name == "upper":
        return lambda value: value.upper()
    if name == "int":
        return int
    if name == "plus-one":
        return lambda value: int(value) + 1
    raise KeyError(f"unknown hook: {name}")


def _decode_data(value: Any, registry: dict[str, Any]) -> Any:
    if isinstance(value, list):
        return [_decode_data(item, registry) for item in value]
    if not isinstance(value, dict):
        return value
    if "__tuple__" in value and len(value) == 1:
        return tuple(_decode_data(item, registry) for item in value["__tuple__"])
    if "__set__" in value and len(value) == 1:
        return {_decode_data(item, registry) for item in value["__set__"]}
    if "__type__" in value and len(value) == 1:
        return _parse_type(value["__type__"], registry)
    return {key: _decode_data(item, registry) for key, item in value.items()}


def _convert_key(name: str):
    if name == "identity":
        return lambda value: value
    if name == "camel":
        def camel(value: str) -> str:
            first, *rest = value.split("_")
            return first + "".join(part.title() for part in rest)

        return camel
    raise KeyError(f"unknown key converter: {name}")


def _config(dacite: Any, spec: dict[str, Any], registry: dict[str, Any]) -> Any:
    kwargs: dict[str, Any] = {}
    for name in ("check_types", "strict", "strict_unions_match"):
        if name in spec:
            kwargs[name] = spec[name]
    if "cast" in spec:
        kwargs["cast"] = [_parse_type(item, registry) for item in spec["cast"]]
    if "type_hooks" in spec:
        kwargs["type_hooks"] = {
            _parse_type(item["type"], registry): _hook(item["hook"])
            for item in spec["type_hooks"]
        }
    if "forward_references" in spec:
        kwargs["forward_references"] = {
            name: _parse_type(item, registry)
            for name, item in spec["forward_references"].items()
        }
    if "convert_key" in spec:
        kwargs["convert_key"] = _convert_key(spec["convert_key"])
    return dacite.Config(**kwargs)


def _exception_payload(error: BaseException) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "type": f"{type(error).__module__}.{type(error).__qualname__}",
        "message": str(error),
    }
    for name in ("field_path", "keys", "message"):
        if hasattr(error, name):
            payload[name] = _encode(getattr(error, name))
    if hasattr(error, "union_matches"):
        payload["union_matches"] = sorted(_type_name(item) for item in error.union_matches)
    return payload


def _main(request: dict[str, Any]) -> Any:
    dacite = importlib.import_module("dacite")
    operation = request["operation"]
    if operation == "convert":
        registry = _build_registry(request)
        config = _config(dacite, request.get("config", {}), registry)
        target_spec = request["target"]
        target = registry[target_spec] if isinstance(target_spec, str) else _parse_type(target_spec, registry)
        data = _decode_data(request["data"], registry)
        return _encode(dacite.from_dict(target, data, config=config))
    if operation == "exports":
        return {"all": list(dacite.__all__), "module": dacite.from_dict.__module__}
    if operation == "config-defaults":
        config = dacite.Config()
        return {
            "type_hooks": config.type_hooks,
            "cast": config.cast,
            "forward_references": config.forward_references,
            "check_types": config.check_types,
            "strict": config.strict,
            "strict_unions_match": config.strict_unions_match,
            "convert_key_identity": config.convert_key("some_field"),
        }
    if operation == "cache":
        before = dacite.get_cache_size()
        dacite.set_cache_size(request["size"])
        after = dacite.get_cache_size()
        dacite.clear_cache()
        return {"before": before, "after": after}
    if operation == "metadata":
        requirements = importlib.metadata.requires("dacite") or []
        return {
            "version": importlib.metadata.version("dacite"),
            "requires": [requirement for requirement in requirements if "extra ==" not in requirement],
        }
    if operation == "exception-hierarchy":
        names = [
            "DaciteError",
            "DaciteFieldError",
            "WrongTypeError",
            "MissingValueError",
            "UnionMatchError",
            "StrictUnionMatchError",
            "ForwardReferenceError",
            "UnexpectedDataError",
        ]
        return {
            name: [base.__name__ for base in getattr(dacite, name).__mro__[:4]]
            for name in names
        }
    raise KeyError(f"unknown operation: {operation}")


request = json.loads(sys.stdin.read())
try:
    response = {"ok": True, "value": _main(request)}
except BaseException as error:
    response = {"ok": False, "exception": _exception_payload(error)}
print(json.dumps(response, ensure_ascii=False, separators=(",", ":"), sort_keys=True))
