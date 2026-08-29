#!/usr/bin/env python3
"""Private PyYAML contract verifier using the isolated candidate JSON client."""

from __future__ import annotations

import json

from nl2repobench.verification.candidate_client import execute_script


def _script(body: str) -> str:
    return "import yaml\n" + body + "\nresult = True\n"


SCENARIOS: list[tuple[str, str]] = [
    ("yaml-version", "assert isinstance(yaml.__version__, str) and yaml.__version__"),
    ("yaml-safe-load-mapping", "assert yaml.safe_load('a: 1\\nb: two\\n') == {'a': 1, 'b': 'two'}"),
    ("yaml-safe-load-sequence", "assert yaml.safe_load('- one\\n- 2\\n- true\\n') == ['one', 2, True]"),
    ("yaml-safe-load-scalars", "assert yaml.safe_load('null') is None and yaml.safe_load('3.5') == 3.5"),
    ("yaml-safe-load-unicode", "assert yaml.safe_load('name: cafe\\u0301\\n')['name'] == 'cafe\\u0301'"),
    ("yaml-safe-load-empty", "assert yaml.safe_load('') is None"),
    ("yaml-safe-load-alias", "value = yaml.safe_load('base: &b {x: 1}\\ncopy: *b\\n'); assert value['base'] is value['copy']"),
    ("yaml-safe-load-merge", "assert yaml.safe_load('base: &b {x: 1, y: 2}\\ntarget: {<<: *b, y: 3}\\n')['target'] == {'x': 1, 'y': 3}"),
    ("yaml-load-requires-loader", "try: yaml.load('a: 1')\nexcept TypeError: pass\nelse: raise AssertionError('loader not required')"),
    ("yaml-safe-load-all", "assert list(yaml.safe_load_all('---\\na: 1\\n---\\nb: 2\\n')) == [{'a': 1}, {'b': 2}]"),
    ("yaml-full-load", "assert yaml.full_load('a: 1\\n') == {'a': 1}"),
    ("yaml-full-load-all", "assert list(yaml.full_load_all('--- 1\\n--- 2\\n')) == [1, 2]"),
    ("yaml-safe-tag-rejected", "try: yaml.safe_load('!!python/object/apply:os.system [echo x]')\nexcept yaml.YAMLError: pass\nelse: raise AssertionError('unsafe tag accepted')"),
    ("yaml-parser-error", "try: list(yaml.parse('[unterminated'))\nexcept yaml.YAMLError: pass\nelse: raise AssertionError('parser error missing')"),
    ("yaml-scanner-error", "try: list(yaml.scan('\\tbad'))\nexcept yaml.YAMLError: pass\nelse: raise AssertionError('scanner error missing')"),
    ("yaml-composer-error", "try: yaml.compose('a: [')\nexcept yaml.YAMLError: pass\nelse: raise AssertionError('composer error missing')"),
    ("yaml-dump-sorted", "assert yaml.dump({'b': 2, 'a': 1}) == 'a: 1\\nb: 2\\n'"),
    ("yaml-dump-insertion", "assert yaml.dump({'b': 2, 'a': 1}, sort_keys=False) == 'b: 2\\na: 1\\n'"),
    ("yaml-safe-dump", "assert yaml.safe_dump({'a': [1, True]}) == 'a:\\n- 1\\n- true\\n'"),
    ("yaml-safe-dump-rejects-object", "class C: pass\ntry: yaml.safe_dump(C())\nexcept yaml.representer.RepresenterError: pass\nelse: raise AssertionError('object serialized')"),
    ("yaml-dump-unicode", "text = yaml.safe_dump({'name': 'café'}, allow_unicode=True); assert 'café' in text"),
    ("yaml-dump-flow", "assert yaml.safe_dump({'a': 1}, default_flow_style=True) == '{a: 1}\\n'"),
    ("yaml-dump-all", "assert yaml.safe_dump_all([{'a': 1}, {'b': 2}]) == 'a: 1\\n---\\nb: 2\\n'"),
    ("yaml-safe-dump-all", "assert list(yaml.safe_load_all(yaml.safe_dump_all([1, 2]))) == [1, 2]"),
    ("yaml-parse-events", "events = list(yaml.parse('a: 1\\n')); assert isinstance(events[0], yaml.StreamStartEvent) and isinstance(events[-1], yaml.StreamEndEvent)"),
    ("yaml-scan-tokens", "tokens = list(yaml.scan('a: 1\\n')); assert any(isinstance(t, yaml.ScalarToken) and t.value == 'a' for t in tokens)"),
    ("yaml-compose-scalar", "node = yaml.compose('42\\n'); assert isinstance(node, yaml.ScalarNode) and node.value == '42' and node.tag == 'tag:yaml.org,2002:int'"),
    ("yaml-compose-sequence", "node = yaml.compose('- a\\n- b\\n'); assert isinstance(node, yaml.SequenceNode) and [x.value for x in node.value] == ['a', 'b']"),
    ("yaml-compose-mapping", "node = yaml.compose('a: 1\\nb: 2\\n'); assert isinstance(node, yaml.MappingNode) and [k.value for k, _ in node.value] == ['a', 'b']"),
    ("yaml-emit-events", "events = list(yaml.parse('a: 1\\n')); assert yaml.emit(events) == 'a: 1\\n'"),
    ("yaml-serialize-node", "node = yaml.compose('a: 1\\n'); assert yaml.serialize(node) == 'a: 1\\n'"),
    ("yaml-serialize-all", "nodes = list(yaml.compose_all('--- a\\n--- b\\n')); assert yaml.serialize_all(nodes) == 'a\\n--- b\\n...\\n'"),
    ("yaml-custom-constructor", "class L(yaml.SafeLoader): pass\ndef construct(loader, node): return 'custom:' + loader.construct_scalar(node)\nL.add_constructor('!x', construct); assert yaml.load('!x hi', Loader=L) == 'custom:hi'"),
    ("yaml-multi-constructor", "class L(yaml.SafeLoader): pass\ndef construct(loader, suffix, node): return suffix + ':' + loader.construct_scalar(node)\nL.add_multi_constructor('!prefix/', construct); assert yaml.load('!prefix/name hi', Loader=L) == 'name:hi'"),
    ("yaml-custom-representer", "class D(yaml.SafeDumper): pass\nclass C: pass\nD.add_representer(C, lambda dumper, value: dumper.represent_scalar('tag:yaml.org,2002:str', 'custom'))\nassert yaml.dump(C(), Dumper=D) == 'custom\\n...\\n'"),
    ("yaml-multi-representer", "class D(yaml.SafeDumper): pass\nclass C: pass\nD.add_multi_representer(C, lambda dumper, value: dumper.represent_scalar('tag:yaml.org,2002:str', 'multi'))\nassert yaml.dump(C(), Dumper=D) == 'multi\\n...\\n'"),
    ("yaml-implicit-resolver", "class L(yaml.SafeLoader): pass\nimport re\nL.add_implicit_resolver('!word', re.compile(r'^word$'), ['w'])\nL.add_constructor('!word', lambda loader, node: 'resolved')\nassert yaml.load('word', Loader=L) == 'resolved'"),
    ("yaml-path-resolver", "class L(yaml.SafeLoader): pass\nL.add_path_resolver('!special', ['root', 'value'], str)\nL.add_constructor('!special', lambda loader, node: 'path')\nassert yaml.load('root:\\n  value: x\\n', Loader=L) == {'root': {'value': 'path'}}"),
    ("yaml-yamlobject", "class Obj(yaml.YAMLObject):\n    yaml_tag = '!Obj'\n    yaml_loader = yaml.SafeLoader\n    @classmethod\n    def from_yaml(cls, loader, node): return cls()\nassert isinstance(yaml.load('!Obj {}', Loader=yaml.SafeLoader), Obj)"),
    ("yaml-class-registration", "class L(yaml.SafeLoader): pass\nL.add_constructor('!v', lambda loader, node: loader.construct_scalar(node).upper())\nassert yaml.load('!v hello', Loader=L) == 'HELLO'"),
    ("yaml-token-attributes", "token = next(t for t in yaml.scan('key: value') if isinstance(t, yaml.ScalarToken)); assert token.value == 'key' and hasattr(token, 'start_mark')"),
    ("yaml-event-attributes", "event = next(e for e in yaml.parse('key: value') if isinstance(e, yaml.ScalarEvent)); assert event.value == 'key' and event.implicit"),
    ("yaml-node-tags", "node = yaml.compose('true'); assert node.tag == 'tag:yaml.org,2002:bool'"),
    ("yaml-node-order", "node = yaml.compose('z: 0\\na: 1\\n'); assert [k.value for k, _ in node.value] == ['z', 'a']"),
    ("yaml-loader-classes", "assert all(isinstance(c, type) for c in (yaml.BaseLoader, yaml.SafeLoader, yaml.FullLoader, yaml.Loader, yaml.UnsafeLoader))"),
    ("yaml-dumper-classes", "assert all(isinstance(c, type) for c in (yaml.BaseDumper, yaml.SafeDumper, yaml.Dumper))"),
    ("yaml-error-classes", "assert issubclass(yaml.YAMLError, Exception) and issubclass(yaml.MarkedYAMLError, yaml.YAMLError)"),
    ("yaml-libyaml-flag", "assert isinstance(yaml.__with_libyaml__, bool)"),
    ("yaml-merge-direct", "assert yaml.safe_load('a: &a {x: 1}\\nb: {<<: *a}\\n')['b'] == {'x': 1}"),
    ("yaml-merge-sequence", "assert yaml.safe_load('a: &a {x: 1}\\nb: &b {y: 2}\\nc: {<<: [*a, *b]}\\n')['c'] == {'x': 1, 'y': 2}"),
    ("yaml-merge-nested", "assert yaml.safe_load('a0: &a0 {k0: 0}\\na1: &a1 {<<: [*a0, *a0], k1: 1}\\ntarget: {<<: [*a1, *a1], k2: 2}\\n')['target'] == {'k0': 0, 'k1': 1, 'k2': 2}"),
    ("yaml-merge-fanout", "source = 'base: &b {x: 1}\\na: &a {<<: [*b, *b]}\\nroot: {<<: [*a, *a]}\\n'; assert yaml.safe_load(source)['root'] == {'x': 1}"),
    ("yaml-roundtrip", "value = {'items': [1, 'two', False]}; assert yaml.safe_load(yaml.safe_dump(value)) == value"),
    ("yaml-binary-roundtrip", "value = b'hello\\x00world'; assert yaml.safe_load(yaml.safe_dump(value)) == value"),
    ("yaml-multiple-documents", "assert list(yaml.safe_load_all('---\\n1\\n---\\n2\\n---\\n3\\n')) == [1, 2, 3]"),
    ("yaml-explicit-boundaries", "assert yaml.safe_load('---\\na: 1\\n...\\n') == {'a': 1}"),
    ("yaml-set-roundtrip", "value = {1, 2, 3}; assert yaml.safe_load(yaml.safe_dump(value)) == value"),
    ("yaml-tuple-roundtrip", "value = (1, 2); assert yaml.load(yaml.dump(value), Loader=yaml.Loader) == value"),
    ("yaml-timestamp", "value = yaml.safe_load('date: 2020-01-02\\n')['date']; assert value.year == 2020 and value.month == 1 and value.day == 2"),
    ("yaml-unsafe-python-tag", "value = yaml.load('!!python/tuple [1, 2]', Loader=yaml.UnsafeLoader); assert value == (1, 2)"),
    ("yaml-dump-bytes", "assert isinstance(yaml.dump(b'abc', encoding='utf-8'), bytes)"),
    ("yaml-stream-write", "import io\nstream = io.StringIO(); assert yaml.safe_dump({'a': 1}, stream) is None and stream.getvalue() == 'a: 1\\n'"),
    ("yaml-encoding", "data = yaml.safe_dump({'a': 'é'}, encoding='utf-8'); assert isinstance(data, bytes) and yaml.safe_load(data) == {'a': 'é'}"),
    ("yaml-sort-option", "assert yaml.safe_dump({'b': 2, 'a': 1}, sort_keys=False) == 'b: 2\\na: 1\\n'"),
]


def main() -> int:
    if len(SCENARIOS) != 64 or len({item[0] for item in SCENARIOS}) != 64:
        raise SystemExit("scenario denominator is not exactly 64 unique leaves")
    leaves: list[dict[str, object]] = []
    for leaf_id, body in SCENARIOS:
        observed = execute_script(_script(body), timeout_sec=3.0)
        if observed.ok and observed.value is True:
            leaves.append({"id": leaf_id, "status": "passed"})
        else:
            detail = observed.exception_message or observed.exception_type or "scenario failed"
            leaves.append({"id": leaf_id, "status": "failed", "message": detail[-2000:]})
    print(json.dumps({"schema_version": "1.0", "leaves": leaves}, sort_keys=True))
    # The wrapper owns validity and reward; a scenario failure is data in the
    # bounded report, not a verifier-process failure.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
