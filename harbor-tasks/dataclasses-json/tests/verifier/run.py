from __future__ import annotations

import json
import os
import signal
import subprocess
import sys


CHILD = r'''
import json, os, sys
sys.path.insert(0, os.environ["CANDIDATE_ROOT"])
sys.path.insert(0, os.environ["NL2REPO_CANDIDATE_DEPENDENCIES"])
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
from dataclasses_json import CatchAll, DataClassJsonMixin, Exclude, LetterCase, Undefined, config, dataclass_json
class Color(Enum): RED = "red"; BLUE = "blue"
@dataclass_json
@dataclass
class Child: value: int
@dataclass_json
@dataclass
class Item: name: str; count: int = 1
@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class Profile: first_name: str; last_name: str
@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class Ignore: value: int
@dataclass_json(undefined=Undefined.RAISE)
@dataclass
class Strict: value: int
@dataclass_json(undefined=Undefined.INCLUDE)
@dataclass
class Flexible: value: int; extras: CatchAll = field(default_factory=dict)
@dataclass_json
@dataclass
class Configured:
    wire_value: int = field(metadata=config(field_name="wireValue"))
    hidden: str = field(default="x", metadata=config(exclude=Exclude.ALWAYS))
@dataclass_json
@dataclass
class OptionalItem: name: str; maybe: Optional[str] = None
def operation(op):
    if op == "exports":
        import dataclasses_json as m
        return all(hasattr(m, x) for x in ["DataClassJsonMixin", "config", "global_config", "Exclude", "CatchAll", "Undefined", "LetterCase", "__version__"])
    if op == "primitive": return Item("tea", 3).to_dict()
    if op == "json_roundtrip": return Item.from_json(Item("tea", 3).to_json()).to_dict()
    if op == "nested": return Item.from_dict({"name": "box", "count": 2}).to_dict()
    if op == "child": return Child.from_dict({"value": 7}).to_dict()
    if op == "containers": return [Child.from_dict(x).to_dict() for x in [{"value": 1}, {"value": 2}]]
    if op == "camel": return Profile("Ada", "Lovelace").to_dict()
    if op == "camel_load": return Profile.from_dict({"firstName": "Ada", "lastName": "Lovelace"}).to_dict()
    if op == "enum": return Color.RED.value
    if op == "optional": return OptionalItem.from_dict({"name": "x"}).to_dict()
    if op == "unicode": return Item("café", 1).to_json(ensure_ascii=False)
    if op == "ascii": return Item("café", 1).to_json()
    if op == "sort": return Configured(2).to_json(sort_keys=True)
    if op == "indent": return "\n" in Item("x").to_json(indent=2)
    if op == "default": return Item.from_dict({"name": "x"}).to_dict()
    if op == "field_config": return Configured(9).to_dict()
    if op == "exclude": return "hidden" not in Configured(9).to_dict()
    if op == "ignore": return Ignore.from_dict({"value": 2, "unknown": 3}).to_dict()
    if op == "strict": return Strict.from_dict({"value": 2, "unknown": 3})
    if op == "include": return Flexible.from_dict({"value": 2, "unknown": 3}).to_dict()
    if op == "schema": return Item.schema().dump(Item("x", 4))
    if op == "schema_many": return Item.schema(many=True).dump([Item("x"), Item("y", 2)])
    if op == "mixin":
        @dataclass
        class M(DataClassJsonMixin): value: int
        return M(5).to_dict()
    if op == "invalid": return Item.from_json("[]")
    raise ValueError("unknown operation")
try:
    request = json.load(sys.stdin)
    value = operation(request["op"])
    print(json.dumps({"ok": True, "value": value}, ensure_ascii=False, allow_nan=False, sort_keys=True))
except Exception as exc:
    print(json.dumps({"ok": False, "error": {"type": type(exc).__name__, "message": str(exc)}} , sort_keys=True))
'''


CASES = [
    ("exports", True, None),
    ("primitive", {"name": "tea", "count": 3}, None),
    ("json_roundtrip", {"name": "tea", "count": 3}, None),
    ("nested", {"name": "box", "count": 2}, None),
    ("child", {"value": 7}, None),
    ("containers", [{"value": 1}, {"value": 2}], None),
    ("camel", {"firstName": "Ada", "lastName": "Lovelace"}, None),
    ("camel_load", {"firstName": "Ada", "lastName": "Lovelace"}, None),
    ("enum", "red", None),
    ("optional", {"name": "x", "maybe": None}, None),
    ("unicode", '{"name": "café", "count": 1}', None),
    ("ascii", '{"name": "caf\\u00e9", "count": 1}', None),
    ("sort", '{"wireValue": 2}', None),
    ("indent", True, None),
    ("default", {"name": "x", "count": 1}, None),
    ("field_config", {"wireValue": 9}, None),
    ("exclude", True, None),
    ("ignore", {"value": 2}, None),
    ("strict", None, "UndefinedParameterError"),
    ("include", {"value": 2, "unknown": 3}, None),
    ("schema", {"name": "x", "count": 4}, None),
    ("schema_many", [{"name": "x", "count": 1}, {"name": "y", "count": 2}], None),
    ("mixin", {"value": 5}, None),
    ("invalid", None, "AttributeError"),
]


def main() -> None:
    leaves = []
    for name, expected, error_type in CASES:
        try:
            completed = subprocess.run(
                ["runuser", "-u", "candidate", "--", "env", "CANDIDATE_ROOT=/tmp/candidate-site", "NL2REPO_CANDIDATE_DEPENDENCIES=/opt/candidate-dependencies/site", "/usr/local/bin/python", "-I", "-c", CHILD],
                input=json.dumps({"op": name}),
                text=True,
                capture_output=True,
                timeout=15,
                check=False,
            )
            response = json.loads(completed.stdout)
            if error_type:
                passed = response.get("ok") is False and response.get("error", {}).get("type") == error_type
            else:
                passed = response.get("ok") is True and response.get("value") == expected
        except Exception:
            passed = False
        leaves.append({"id": name, "status": "passed" if passed else "failed"})
    print(json.dumps({"schema_version": "1.0", "leaves": leaves}, sort_keys=True))


if __name__ == "__main__":
    main()
