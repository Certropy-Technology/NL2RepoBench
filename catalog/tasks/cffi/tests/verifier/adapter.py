from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Any

RESULT_PREFIX = "NL2REPO_CFFI_RESULT="


def _error(action: Any) -> dict[str, str]:
    try:
        action()
    except BaseException as exc:
        return {"type": f"{type(exc).__module__}.{type(exc).__qualname__}", "message": str(exc)}
    return {"type": "", "message": ""}


def exercise(name: str) -> Any:
    import cffi
    from cffi import FFI

    if name == "exports-version":
        return {"all": list(cffi.__all__), "version": cffi.__version__, "ffi": FFI.__name__}
    if name == "ffi-construction":
        ffi = FFI()
        return {"type": type(ffi).__name__, "null": bool(ffi.NULL), "has_new": callable(ffi.new)}
    if name == "primitive-type":
        ffi = FFI()
        primitive = ffi.typeof("int")
        pointer = ffi.typeof("int *")
        return {"kind": primitive.kind, "cname": primitive.cname, "size": ffi.sizeof("int"), "align": ffi.alignof("int"), "pointer_item": pointer.item.cname}
    if name == "pointer-new":
        ffi = FFI()
        p = ffi.new("int *", 42)
        p[0] = -7
        return {"value": p[0], "kind": ffi.typeof(p).kind, "cname": ffi.typeof(p).cname}
    if name == "array-new":
        ffi = FFI()
        p = ffi.new("int[]", [1, 2, 3])
        return {"length": len(p), "items": list(p), "item": ffi.typeof(p).item.cname}
    if name == "struct-new":
        ffi = FFI()
        ffi.cdef("struct point { int x; int y; };")
        p = ffi.new("struct point *", {"x": 2, "y": 3})
        return {"x": p.x, "y": p.y, "kind": ffi.typeof(p).kind, "cname": ffi.typeof(p).cname}
    if name == "cast-and-size":
        ffi = FFI()
        unsigned = int(ffi.cast("unsigned int", -1))
        return {"unsigned": unsigned, "int_size": ffi.sizeof("int"), "char_size": ffi.sizeof("char"), "double_size": ffi.sizeof("double")}
    if name == "string-read":
        ffi = FFI()
        p = ffi.new("char[]", b"hello\x00hidden")
        return {"full": ffi.string(p).decode(), "max3": ffi.string(p, 3).decode(), "bytes": len(p)}
    if name == "buffer-read":
        ffi = FFI()
        p = ffi.new("char[]", b"abc123")
        return {"all": bytes(ffi.buffer(p)).decode(), "prefix": bytes(ffi.buffer(p, 3)).decode()}
    if name == "getctype-normalization":
        ffi = FFI()
        return {"plain": ffi.getctype("int"), "pointer": ffi.getctype("int *"), "array": ffi.getctype("int[3]", "value")}
    if name == "callback-success":
        ffi = FFI()
        cb = ffi.callback("int(int)", lambda value: value + 1)
        return {"result": cb(41), "kind": ffi.typeof(cb).kind}
    if name == "callback-error":
        ffi = FFI()
        def broken(_: int) -> int:
            raise ValueError("broken")
        cb = ffi.callback("int(int)", broken, error=-7)
        return {"result": cb(1)}
    if name == "callback-onerror":
        ffi = FFI()
        seen: list[str] = []
        def onerror(exc: type[BaseException], value: BaseException, tb: Any) -> None:
            seen.extend([exc.__name__, type(value).__name__])
        def broken(_: int) -> int:
            raise ValueError("broken")
        cb = ffi.callback("int(int)", broken, error=-9, onerror=onerror)
        result = cb(1)
        return {"result": result, "seen": seen}
    if name == "handle-roundtrip":
        ffi = FFI()
        obj = {"x": [1, 2]}
        handle = ffi.new_handle(obj)
        return {"same": ffi.from_handle(handle) is obj, "kind": ffi.typeof(handle).kind}
    if name == "handle-identity":
        ffi = FFI()
        a, b = ffi.new_handle(None), ffi.new_handle(None)
        return {"distinct": a != b, "same_type": ffi.typeof(a).cname == ffi.typeof(b).cname}
    if name == "addressof-array":
        ffi = FFI()
        array = ffi.new("int[3]", [1, 2, 3])
        middle = ffi.addressof(array, 1)
        middle[0] = 8
        return {"items": list(array), "kind": ffi.typeof(middle).kind}
    if name == "struct-field":
        ffi = FFI()
        ffi.cdef("struct pair { int left; int right; };")
        pair = ffi.new("struct pair *", {"left": 4, "right": 5})
        field = ffi.addressof(pair[0], "right")
        field[0] = 9
        return {"left": pair.left, "right": pair.right, "field": ffi.typeof(field).cname}
    if name == "pointer-arithmetic":
        ffi = FFI()
        array = ffi.new("int[3]", [10, 20, 30])
        pointer = ffi.cast("int *", array)
        return {"first": pointer[0], "second": pointer[1], "third": pointer[2]}
    if name == "cdef-types":
        ffi = FFI()
        ffi.cdef("typedef unsigned long word_t; enum mode { MODE_A, MODE_B }; struct item { word_t value; };")
        return {"typedef": ffi.typeof("word_t").kind, "enum": ffi.typeof("enum mode").kind, "struct": ffi.typeof("struct item").kind}
    if name == "cdef-invalid":
        ffi = FFI()
        error = _error(lambda: ffi.cdef("struct broken {"))
        return {"type": error["type"].split(".")[-1], "has_message": bool(error["message"])}
    if name == "list-types":
        ffi = FFI()
        ffi.cdef("typedef int counter_t; struct record { int value; };")
        types = ffi.list_types()
        return {"typedefs": list(types[0]), "structs": list(types[1]), "unions": list(types[2])}
    if name == "dlopen-abs":
        ffi = FFI()
        ffi.cdef("int abs(int);")
        return {"result": ffi.dlopen(None).abs(-12)}
    if name == "dlopen-strlen":
        ffi = FFI()
        ffi.cdef("size_t strlen(const char *);")
        return {"result": ffi.dlopen(None).strlen(b"hello")}
    if name == "emit-c-code":
        ffi = FFI()
        ffi.set_source("generated_cffi_contract", "int add(int x, int y) { return x + y; }")
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "generated.c"
            result = ffi.emit_c_code(str(path))
            text = path.read_text(encoding="utf-8")
        return {"result": result, "exists": True, "has_include": "#include" in text, "has_function": "add" in text}
    if name == "set-source":
        ffi = FFI()
        result = ffi.set_source("local_contract", None)
        return {"result": result, "type": type(ffi).__name__}
    if name == "error-hierarchy":
        from cffi.error import CDefError, FFIError, VerificationError, VerificationMissing
        return {"cdef_is_ffi": issubclass(CDefError, FFIError), "verification_is_ffi": issubclass(VerificationError, FFIError), "missing_is_verification": issubclass(VerificationMissing, VerificationError)}
    if name == "null-and-bool":
        ffi = FFI()
        null = ffi.cast("void *", 0)
        return {"false": not bool(null), "equal": null == ffi.NULL, "cname": ffi.typeof(null).cname}
    if name == "deterministic-repeat":
        def sample() -> dict[str, Any]:
            ffi = FFI()
            ffi.cdef("struct sample { int value; };")
            p = ffi.new("struct sample *", {"value": 17})
            return {"value": p.value, "kind": ffi.typeof(p).kind, "size": ffi.sizeof(p)}
        return {"same": sample() == sample(), "sample": sample()}
    raise ValueError(f"unknown scenario: {name}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate-site", required=True)
    parser.add_argument("--dependency-site", required=True)
    parser.add_argument("--scenario", required=True)
    args = parser.parse_args()
    if Path(args.candidate_site).resolve() != Path("/tmp/candidate-site"):
        raise ValueError("candidate site is unavailable")
    sys.path.insert(0, args.candidate_site)
    sys.path.insert(1, args.dependency_site)
    try:
        payload = {"ok": True, "value": exercise(args.scenario)}
    except BaseException as exc:
        payload = {"ok": False, "type": f"{type(exc).__module__}.{type(exc).__qualname__}", "message": str(exc)}
    os.write(1, (RESULT_PREFIX + json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n").encode())


if __name__ == "__main__":
    main()
