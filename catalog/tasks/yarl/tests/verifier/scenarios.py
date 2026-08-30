from __future__ import annotations

COMMON = r'''
import re

def _error(action):
    try:
        action()
    except BaseException as exc:
        return {
            "message": re.sub(r"0x[0-9a-fA-F]+", "0x<address>", str(exc)),
            "type": f"{type(exc).__module__}.{type(exc).__qualname__}",
        }
    return {"message": None, "type": None}
'''


SCENARIOS = {
    "exports-version-metadata": r'''
import importlib.metadata
import yarl
result = {
    "all": list(yarl.__all__),
    "distribution": importlib.metadata.version("yarl"),
    "types_present": all(hasattr(yarl, name) for name in ("SimpleQuery", "QueryVariable", "Query")),
    "url_module": yarl.URL.__module__,
    "version": yarl.__version__,
}
''',
    "constructor-empty-copy-split": r'''
from urllib.parse import urlsplit
from yarl import URL
original = URL("https://example.com/a?b=c#d")
result = {
    "copy_equal": URL(original) == original,
    "copy_identity": URL(original) is original,
    "empty": [str(URL()), bool(URL())],
    "split_default": _error(lambda: URL(urlsplit("https://user:pass@example.com:8443/a?q=1#f"))),
    "split_encoded": str(URL(urlsplit("https://user:pass@example.com:8443/a?q=1#f"), encoded=True)),
}
''',
    "constructor-unicode-canonical": r'''
from yarl import URL
value = URL("https://user:пароль@εμπορικόσήμα.eu/шлях/這裡?ключ=знач#якір")
result = {"raw": str(value), "human": value.human_repr(), "repr": repr(value)}
''',
    "constructor-encoded-preservation": r'''
from yarl import URL
value = URL("http://example.com/%30?a=%31#%32", encoded=True)
result = {
    "fragment": value.fragment,
    "path": value.path,
    "query": value.query_string,
    "raw": str(value),
}
''',
    "absolute-auth-properties": r'''
from yarl import URL
value = URL("https://us%65r:p%40ss@example.com:8443/a")
result = {
    "absolute": value.absolute,
    "authority": value.authority,
    "explicit_port": value.explicit_port,
    "host": value.host,
    "is_absolute": value.is_absolute(),
    "password": value.password,
    "port": value.port,
    "raw_authority": value.raw_authority,
    "raw_password": value.raw_password,
    "raw_user": value.raw_user,
    "scheme": value.scheme,
    "user": value.user,
}
''',
    "ipv6-host-properties": r'''
from yarl import URL
value = URL("http://[2001:db8::1]:8080/p")
result = {
    "host": value.host,
    "host_port_subcomponent": value.host_port_subcomponent,
    "host_subcomponent": value.host_subcomponent,
    "port": value.port,
    "raw_host": value.raw_host,
    "string": str(value),
}
''',
    "relative-properties": r'''
from yarl import URL
value = URL("folder/file.txt?x=1#frag")
result = {
    "absolute": value.absolute,
    "authority": value.authority,
    "host": value.host,
    "is_absolute": value.is_absolute(),
    "path": value.path,
    "port": value.port,
    "scheme": value.scheme,
}
''',
    "build-components": r'''
from yarl import URL
value = URL.build(
    scheme="https", user="u s", password="p@ss", host="пример.рф", port=9443,
    path="/a b", query=[("x", "1"), ("x", "2")], fragment="f g",
)
result = {"string": str(value), "human": value.human_repr(), "query": list(value.query.items())}
''',
    "build-authority": r'''
from yarl import URL
result = {
    "authority": str(URL.build(scheme="http", authority="user:pass@example.com:8080", path="/a")),
    "empty": str(URL.build()),
    "encoded": str(URL.build(scheme="http", host="example.com", path="/%30", encoded=True)),
}
''',
    "build-mutual-exclusion-errors": r'''
from yarl import URL
result = {
    "authority_host": _error(lambda: URL.build(authority="example.com", host="example.org")),
    "query_both": _error(lambda: URL.build(query={"a": "b"}, query_string="a=b")),
    "user_without_host": _error(lambda: URL.build(user="u")),
}
''',
    "string-bytes-data-model": r'''
from yarl import URL
value = URL("https://example.com/a?b=c#d")
result = {
    "bool_empty": bool(URL()),
    "bool_value": bool(value),
    "bytes": bytes(value).decode("ascii"),
    "hash_stable": hash(value) == hash(URL(str(value))),
    "repr": repr(value),
    "str": str(value),
}
''',
    "comparison-ordering": r'''
from yarl import URL
a = URL("http://example.com/a")
b = URL("http://example.com/b")
result = {
    "eq": a == URL(str(a)),
    "ge": b >= a,
    "gt": b > a,
    "le": a <= b,
    "lt": a < b,
    "ne_other": a != "http://example.com/a",
    "other_order": _error(lambda: a < "http://example.com/b"),
}
''',
    "operators-path-division": r'''
from yarl import URL
base = URL("https://example.com/root")
result = {
    "chain": str(base / "a b" / "c"),
    "encoded": str(base.joinpath("%30", encoded=True)),
    "slash_error": _error(lambda: base / "/absolute"),
}
''',
    "operators-query-modulo": r'''
from yarl import URL
base = URL("https://example.com/a")
result = {
    "mapping": str(base % {"x": "1", "unicode": "знач"}),
    "pairs": str(base % [("x", 1), ("x", 2)]),
}
''',
    "origin-and-relative": r'''
from yarl import URL
value = URL("https://user:pass@example.com:8443/a/b?q=1#f")
result = {
    "origin": str(value.origin()),
    "relative": str(value.relative()),
    "relative_origin_error": _error(lambda: URL("/a").origin()),
}
''',
    "default-and-explicit-ports": r'''
from yarl import URL
values = [URL("http://example.com"), URL("http://example.com:80"), URL("http://example.com:81"), URL("custom://example.com")]
result = [[v.port, v.explicit_port, v.is_default_port(), str(v)] for v in values]
''',
    "path-properties": r'''
from yarl import URL
value = URL("https://example.com/a%20b/c%2Fd?q=1")
result = {
    "path": value.path,
    "path_qs": value.path_qs,
    "path_safe": value.path_safe,
    "raw_path": value.raw_path,
    "raw_path_qs": value.raw_path_qs,
}
''',
    "path-parts-name-suffix-parent": r'''
from yarl import URL
value = URL("https://example.com/a/файл.tar.gz?q=1#f")
result = {
    "name": value.name,
    "parent": str(value.parent),
    "parts": list(value.parts),
    "raw_name": value.raw_name,
    "raw_parts": list(value.raw_parts),
    "raw_suffix": value.raw_suffix,
    "raw_suffixes": list(value.raw_suffixes),
    "suffix": value.suffix,
    "suffixes": list(value.suffixes),
}
''',
    "query-properties-duplicates": r'''
from yarl import URL
value = URL("https://example.com/a?x=1&x=2&ключ=знач")
result = {
    "items": list(value.query.items()),
    "query_string": value.query_string,
    "raw_query_string": value.raw_query_string,
    "x_all": value.query.getall("x"),
}
''',
    "fragment-properties": r'''
from yarl import URL
value = URL("https://example.com/a#якір тут")
result = {"fragment": value.fragment, "raw_fragment": value.raw_fragment, "string": str(value)}
''',
    "with-scheme": r'''
from yarl import URL
result = {
    "changed": str(URL("http://example.com:80/a").with_scheme("https")),
    "relative_error": _error(lambda: URL("/a").with_scheme("https")),
}
''',
    "with-user-password": r'''
from yarl import URL
value = URL("http://user:pass@example.com/a")
result = {
    "clear_password": str(value.with_password(None)),
    "clear_user": str(value.with_user(None)),
    "password": str(value.with_password("пароль")),
    "user": str(value.with_user("новый")),
}
''',
    "with-host": r'''
from yarl import URL
value = URL("http://example.com/a")
result = {
    "idna": str(value.with_host("пример.рф")),
    "relative_error": _error(lambda: URL("/a").with_host("example.com")),
    "colon_error": _error(lambda: value.with_host("bad:host")),
}
''',
    "with-port": r'''
from yarl import URL
value = URL("http://example.com:8080/a")
result = {
    "changed": str(value.with_port(9090)),
    "cleared": str(value.with_port(None)),
    "range_error": _error(lambda: value.with_port(70000)),
    "type_error": _error(lambda: value.with_port("80")),
}
''',
    "with-path": r'''
from yarl import URL
value = URL("http://example.com/old?q=1#f")
result = {
    "default": str(value.with_path("/новый путь")),
    "encoded": str(value.with_path("/%30", encoded=True)),
    "keep": str(value.with_path("/new", keep_query=True, keep_fragment=True)),
}
''',
    "with-query-mapping": r'''
from yarl import URL
value = URL("http://example.com/a?old=1")
result = {
    "clear": str(value.with_query(None)),
    "kwargs": str(value.with_query(a="1", b="знач")),
    "mapping": str(value.with_query({"a": [1, 2], "b": 3.5})),
}
''',
    "with-query-pairs-and-string": r'''
from yarl import URL
value = URL("http://example.com/a")
result = {
    "pairs": str(value.with_query([("x", "1"), ("x", "2")])),
    "string": str(value.with_query("x=1&x=2")),
}
''',
    "query-value-errors": r'''
from yarl import URL
value = URL("http://example.com/a")
result = {
    "bool": _error(lambda: value.with_query({"a": True})),
    "nested": _error(lambda: value.with_query({"a": [[1]]})),
    "object": _error(lambda: value.with_query({"a": object()})),
    "too_many_args": _error(lambda: value.with_query("a=1", "b=2")),
}
''',
    "extend-query": r'''
from yarl import URL
value = URL("http://example.com/a?x=0")
result = {
    "none_identity": value.extend_query(None) is value,
    "pairs": str(value.extend_query([("x", 1), ("y", 2)])),
    "string": str(value.extend_query("x=1&y=2")),
}
''',
    "update-query": r'''
from yarl import URL
value = URL("http://example.com/a?x=0&x=old&z=9")
result = {
    "mapping": str(value.update_query({"x": [1, 2], "y": 3})),
    "none_identity": value.update_query(None) is value,
    "pairs": str(value.update_query([("x", "new"), ("x", "again")])),
}
''',
    "without-query-params": r'''
from yarl import URL
value = URL("http://example.com/a?x=1&y=2&x=3")
result = {
    "missing_identity": value.without_query_params("missing") is value,
    "remove": str(value.without_query_params("x")),
}
''',
    "with-fragment": r'''
from yarl import URL
value = URL("http://example.com/a#old")
result = {"changed": str(value.with_fragment("якір")), "cleared": str(value.with_fragment(None))}
''',
    "with-name": r'''
from yarl import URL
value = URL("http://example.com/a/old.txt?q=1#f")
result = {
    "default": str(value.with_name("новый.md")),
    "keep": str(value.with_name("new.md", keep_query=True, keep_fragment=True)),
    "slash_error": _error(lambda: value.with_name("a/b")),
}
''',
    "with-suffix": r'''
from yarl import URL
value = URL("http://example.com/a/file.tar.gz?q=1#f")
result = {
    "changed": str(value.with_suffix(".zip")),
    "cleared": str(value.with_suffix("")),
    "keep": str(value.with_suffix(".txt", keep_query=True, keep_fragment=True)),
    "invalid": _error(lambda: value.with_suffix("txt")),
}
''',
    "join-rfc-cases": r'''
from yarl import URL
base = URL("http://a/b/c/d;p?q")
refs = ["g", "./g", "../g", "/g", "//g", "?y", "#s", "g?y#s", "../../g"]
result = {ref: str(base.join(URL(ref))) for ref in refs}
''',
    "joinpath": r'''
from yarl import URL
base = URL("http://example.com/a/b?x=1#f")
result = {
    "empty": str(base.joinpath()),
    "segments": str(base.joinpath("c", "d e")),
    "absolute_error": _error(lambda: base.joinpath("/root", "child")),
}
''',
    "percent-and-malformed-input": r'''
from yarl import URL
inputs = ["http://example.com/%", "http://example.com/%2", "http://example.com/%2f", "http://example.com/a b"]
result = [[text, str(URL(text)), URL(text).path] for text in inputs]
''',
    "dot-segment-normalization": r'''
from yarl import URL
inputs = ["http://example.com/a/./b", "http://example.com/a/../b", "/a//b/../c", "a/../../b"]
result = [[text, str(URL(text))] for text in inputs]
''',
    "invalid-authority-errors": r'''
from yarl import URL
result = {
    "bad_ipv6": _error(lambda: URL("http://[::1")),
    "bad_port": _error(lambda: URL("http://example.com:bad").port),
    "host_colon": _error(lambda: URL.build(scheme="http", host="a:b")),
    "port_range": _error(lambda: URL("http://example.com:99999").port),
}
''',
    "pickle-copy-roundtrip": r'''
import copy
import pickle
from yarl import URL
value = URL("https://пример.рф/a?q=1#f")
shallow = copy.copy(value)
deep = copy.deepcopy(value)
restored = pickle.loads(pickle.dumps(value))
result = {
    "deep_equal": deep == value,
    "deep_identity": deep is value,
    "pickle_equal": restored == value,
    "pickle_string": str(restored),
    "shallow_equal": shallow == value,
    "shallow_identity": shallow is value,
}
''',
    "cache-control": r'''
import yarl
yarl.cache_configure(idna_encode_size=2, idna_decode_size=3, ip_address_size=4, host_validate_size=5, encode_host_size=6)
yarl.cache_clear()
info = yarl.cache_info()
result = {
    "keys": list(info),
    "sizes": {name: {"currsize": item.currsize, "maxsize": item.maxsize} for name, item in sorted(info.items())},
}
''',
    "pydantic-integration": r'''
from pydantic import BaseModel, TypeAdapter, ValidationError
from yarl import URL
class Model(BaseModel):
    url: URL
model = Model(url="https://пример.рф/a")
adapter = TypeAdapter(URL)
invalid = _error(lambda: adapter.validate_python(123))
result = {
    "dump_json": model.model_dump_json(),
    "model_type": type(model.url).__name__,
    "string": str(model.url),
    "adapter": str(adapter.validate_python("http://example.com/b")),
    "invalid_type": invalid["type"],
}
''',
    "idna-human-roundtrip": r'''
from yarl import URL
value = URL("https://münich.example/путь?q=雪#片")
roundtrip = URL(str(value))
result = {
    "equal": roundtrip == value,
    "host": value.host,
    "human": value.human_repr(),
    "raw_host": value.raw_host,
    "string": str(value),
}
''',
    "deterministic-repetition": r'''
from yarl import URL
def build():
    return URL.build(scheme="https", host="пример.рф", path="/a b").update_query([("x", 1), ("x", 2)]).with_fragment("я")
values = [build() for _ in range(5)]
result = {
    "all_equal": all(item == values[0] for item in values),
    "hashes_equal": len({hash(item) for item in values}) == 1,
    "strings": [str(item) for item in values],
}
''',
}
