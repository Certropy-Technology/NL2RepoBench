from __future__ import annotations

import json
from typing import Any

from nl2repobench.verification.candidate_client import execute_script


LEAF_IDS = [
    "exports", "version", "struct-basics", "struct-options", "field-metadata", "defstruct", "raw", "meta", "to-builtins", "convert-valid", "convert-invalid", "struct-helpers",
    "json-encode", "json-decode", "json-typed-struct", "json-deterministic", "json-encoder", "json-decoder-lines", "json-format", "json-schema", "json-components", "json-hook", "json-invalid",
    "msgpack-roundtrip", "msgpack-typed-struct", "msgpack-ext", "msgpack-deterministic", "msgpack-hook", "msgpack-invalid",
    "toml-roundtrip", "yaml-roundtrip", "unknown-field", "missing-field", "frozen-mutation", "strict-type", "buffer-input", "repr-determinism",
]


SCENARIO = r'''
import msgspec

checks = []
def check(fn):
    try:
        checks.append(bool(fn()))
    except BaseException:
        checks.append(False)

check(lambda: all(hasattr(msgspec, name) for name in (
    'Struct', 'StructMeta', 'field', 'defstruct', 'Raw', 'Meta', 'convert',
    'to_builtins', 'json', 'msgpack', 'structs', 'inspect', 'toml', 'yaml')))
check(lambda: isinstance(msgspec.__version__, str) and bool(msgspec.__version__))

def struct_basics():
    class User(msgspec.Struct):
        user_id: int
        name: str
    u = User(7, 'Ada')
    return (u.user_id, u.name, repr(u), User.__match_args__) == (7, 'Ada', "User(user_id=7, name='Ada')", ('user_id', 'name'))
check(struct_basics)

def struct_options():
    class User(msgspec.Struct, rename='camel', omit_defaults=True, frozen=True, order=True):
        user_id: int
        active: bool = True
    a, b = User(1), User(2, False)
    return (msgspec.json.encode(a), a < b, a.__struct_config__.frozen, a.__struct_config__.omit_defaults) == (b'{"userId":1}', True, True, True)
check(struct_options)

def field_metadata():
    class Item(msgspec.Struct):
        item_id: int = msgspec.field(name='itemId')
        tags: list[str] = msgspec.field(default_factory=list)
    fs = msgspec.structs.fields(Item)
    return (fs[0].name, fs[0].encode_name, fs[0].required, fs[1].required, Item(1).tags is not Item(2).tags) == ('item_id', 'itemId', True, False, True)
check(field_metadata)

def defstruct_case():
    Point = msgspec.defstruct('Point', [('x', int), ('y', str, 'origin')])
    p = Point(3)
    return (p.x, p.y, msgspec.json.decode(msgspec.json.encode(p), type=Point).y, msgspec.structs.astuple(p)) == (3, 'origin', 'origin', (3, 'origin'))
check(defstruct_case)
check(lambda: bytes(msgspec.Raw('abc')) == b'abc' and isinstance(msgspec.Raw('abc').copy(), msgspec.Raw))
check(lambda: (lambda m: (m.ge, m.title, m.examples) == (1, 'Name', ['ada']))(msgspec.Meta(ge=1, title='Name', examples=['ada'])))

def to_builtins_case():
    class User(msgspec.Struct, rename='camel'):
        user_id: int
        name: str
    return msgspec.to_builtins({'user': User(1, 'Ada')}) == {'user': {'userId': 1, 'name': 'Ada'}}
check(to_builtins_case)
def convert_valid():
    class User(msgspec.Struct):
        user_id: int
        name: str
    u = msgspec.convert({'user_id': 2, 'name': 'Lin'}, User)
    return isinstance(u, User) and (u.user_id, u.name) == (2, 'Lin')
check(convert_valid)
def convert_invalid():
    class User(msgspec.Struct):
        user_id: int
    try:
        msgspec.convert({'user_id': 'bad'}, User)
    except msgspec.ValidationError:
        return True
    return False
check(convert_invalid)
def struct_helpers():
    class User(msgspec.Struct):
        user_id: int
        name: str
    u = User(1, 'Ada')
    v = msgspec.structs.replace(u, name='Lin')
    return msgspec.structs.asdict(u) == {'user_id': 1, 'name': 'Ada'} and msgspec.structs.astuple(v) == (1, 'Lin') and u.name == 'Ada'
check(struct_helpers)

check(lambda: msgspec.json.encode({'text': 'café', 'values': [1, True, None]}) == b'{"text":"caf\xc3\xa9","values":[1,true,null]}')
check(lambda: msgspec.json.decode(bytearray(b'{"x": 1, "ok": true}')) == {'x': 1, 'ok': True})
def json_typed():
    class User(msgspec.Struct, rename='camel'):
        user_id: int
        active: bool = True
    u = msgspec.json.decode('{"userId": 3}', type=User)
    return isinstance(u, User) and (u.user_id, u.active) == (3, True)
check(json_typed)
check(lambda: msgspec.json.encode({'b': 1, 'a': 2}, order='sorted') == b'{"a":2,"b":1}')
def json_encoder():
    enc = msgspec.json.Encoder(order='sorted')
    expected = enc.encode({'b': 1, 'a': 2})
    buf = bytearray(32)
    enc.encode_into({'b': 1, 'a': 2}, buf, 2)
    return bytes(buf[2:2 + len(expected)]) == expected
check(json_encoder)
check(lambda: msgspec.json.Decoder().decode_lines(b'{"x":1}\n[2,3]\n') == [{'x': 1}, [2, 3]] and msgspec.json.Encoder().encode_lines([1, 2]) == b'1\n2\n')
check(lambda: msgspec.json.format('{"b":2,"a":[1]}') == '{\n  "b": 2,\n  "a": [\n    1\n  ]\n}')
def json_schema():
    class Point(msgspec.Struct):
        x: int
    schema = msgspec.json.schema(Point)
    return schema['$ref'] == '#/$defs/Point' and schema['$defs']['Point']['properties']['x']['type'] == 'integer'
check(json_schema)
def json_components():
    class Point(msgspec.Struct):
        x: int
    components, refs = msgspec.json.schema_components([Point])
    return components == ({'$ref': '#/$defs/Point'},) and 'Point' in refs
check(json_components)
check(lambda: msgspec.json.encode(object(), enc_hook=lambda obj: 'object') == b'"object"')
def json_invalid():
    try:
        msgspec.json.decode(b'{')
    except msgspec.DecodeError:
        return True
    return False
check(json_invalid)

value = {'a': [1, 'x'], 'ok': True}
check(lambda: msgspec.msgpack.decode(msgspec.msgpack.encode(value)) == value)
def msgpack_typed():
    class Point(msgspec.Struct):
        x: int
        y: int
    p = msgspec.msgpack.decode(msgspec.msgpack.encode(Point(1, 2)), type=Point)
    return isinstance(p, Point) and (p.x, p.y) == (1, 2)
check(msgpack_typed)
check(lambda: msgspec.msgpack.decode(msgspec.msgpack.encode(msgspec.msgpack.Ext(3, b'abc')), ext_hook=lambda code, data: (code, bytes(data))) == (3, b'abc'))
check(lambda: msgspec.msgpack.encode({'b': 1, 'a': 2}, order='sorted') == msgspec.msgpack.encode({'a': 2, 'b': 1}, order='sorted'))
check(lambda: msgspec.msgpack.encode(object(), enc_hook=lambda obj: 'object') == msgspec.msgpack.encode('object'))
def msgpack_invalid():
    try:
        msgspec.msgpack.decode(b'\xc1')
    except msgspec.DecodeError:
        return True
    return False
check(msgpack_invalid)

def toml_case():
    data = msgspec.toml.encode({'name': 'Ada', 'count': 2})
    return msgspec.toml.decode(data) == {'name': 'Ada', 'count': 2}
check(toml_case)
def yaml_case():
    data = msgspec.yaml.encode({'name': 'Ada', 'items': [1, 2]})
    return msgspec.yaml.decode(data) == {'name': 'Ada', 'items': [1, 2]}
check(yaml_case)
def unknown_field():
    class Point(msgspec.Struct, forbid_unknown_fields=True):
        x: int
    try:
        msgspec.json.decode(b'{"x":1,"y":2}', type=Point)
    except msgspec.ValidationError:
        return True
    return False
check(unknown_field)
def missing_field():
    class Point(msgspec.Struct):
        x: int
    try:
        Point()
    except TypeError:
        return True
    return False
check(missing_field)
def frozen_mutation():
    class Point(msgspec.Struct, frozen=True):
        x: int
    p = Point(1)
    try:
        p.x = 2
    except AttributeError:
        return p.x == 1
    return False
check(frozen_mutation)
def strict_type():
    class Point(msgspec.Struct):
        x: int
    try:
        msgspec.json.decode(b'{"x": 1.5}', type=Point)
    except msgspec.ValidationError:
        return True
    return False
check(strict_type)
raw = b'{"x": 4}'
check(lambda: all(msgspec.json.decode(buf) == {'x': 4} for buf in (raw, bytearray(raw), memoryview(raw))))
def repr_determinism():
    class Point(msgspec.Struct):
        x: int
    return repr(Point(1)) == 'Point(x=1)' and repr(Point(1)) == repr(Point(1))
check(repr_determinism)
result = checks
'''


def main() -> None:
    outcome = execute_script(SCENARIO, timeout_sec=30.0)
    values: list[Any] = outcome.value if outcome.ok and isinstance(outcome.value, list) else []
    leaves = []
    for index, identifier in enumerate(LEAF_IDS):
        passed = index < len(values) and values[index] is True
        leaves.append({"id": identifier, "status": "passed" if passed else "failed", "message": ""})
    print(json.dumps({"schema_version": "1.0", "leaves": leaves}, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
