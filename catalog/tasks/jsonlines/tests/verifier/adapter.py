from __future__ import annotations

import codecs
import importlib.metadata
import io
import json
import os
from pathlib import Path
import sys
import tempfile
from typing import Any, Callable


CANDIDATE_SITE = os.environ.get(
    "NL2REPO_JSONLINES_CANDIDATE_SITE", "/tmp/candidate-site"
)
if CANDIDATE_SITE not in sys.path:
    sys.path.insert(0, CANDIDATE_SITE)
DEPENDENCY_SITE = os.environ.get("NL2REPO_CANDIDATE_DEPENDENCIES")
if DEPENDENCY_SITE and DEPENDENCY_SITE not in sys.path:
    sys.path.insert(1, DEPENDENCY_SITE)

import jsonlines


def error_name(call: Callable[..., Any], *args: Any, **kwargs: Any) -> str | None:
    try:
        call(*args, **kwargs)
    except Exception as exc:
        return type(exc).__name__
    return None


def invalid_details(exc: BaseException) -> dict[str, Any]:
    line = getattr(exc, "line", None)
    return {
        "type": type(exc).__name__,
        "line": line.hex() if isinstance(line, bytes) else line,
        "line_is_bytes": isinstance(line, bytes),
        "lineno": getattr(exc, "lineno", None),
        "cause": type(exc.__cause__).__name__ if exc.__cause__ else None,
        "mentions_line": f"(line {getattr(exc, 'lineno', None)})" in str(exc),
    }


def package_surface() -> dict[str, Any]:
    return {
        "version": importlib.metadata.version("jsonlines"),
        "all": list(jsonlines.__all__),
        "classes": [
            jsonlines.Reader.__name__,
            jsonlines.Writer.__name__,
            jsonlines.Error.__name__,
            jsonlines.InvalidLineError.__name__,
        ],
        "callable_open": callable(jsonlines.open),
    }


def read_json_values() -> list[Any]:
    lines = [
        '{"a": [1, true, null, "caf\\u00e9"]}\n',
        "[1, 2]\n",
        '"hello"\n',
        "3.5\n",
        "7\n",
        "false\n",
    ]
    return list(jsonlines.Reader(lines))


def read_bytes_unicode() -> dict[str, Any]:
    reader = jsonlines.Reader(['"snowman: \u2603"'.replace("\x01", "\u2603").encode()])
    return {"value": reader.read(), "eof": error_name(reader.read)}


def read_eof() -> dict[str, Any]:
    reader = jsonlines.Reader(["1"])
    first = reader.read()
    try:
        reader.read()
    except Exception as exc:
        return {"first": first, "type": type(exc).__name__, "message": str(exc)}
    return {"first": first, "type": None, "message": None}


def read_prefixes() -> dict[str, Any]:
    reader = jsonlines.Reader(["\x1e1", "\ufeff2", "\x1e\ufeff3"])
    values = [reader.read(), reader.read()]
    try:
        reader.read()
    except Exception as exc:
        return {"values": values, "third": invalid_details(exc)}
    return {"values": values, "third": None}


def read_empty_policy() -> dict[str, Any]:
    reader = jsonlines.Reader([" \t\r\n", "2\n"])
    try:
        reader.read()
    except Exception as exc:
        details = invalid_details(exc)
    else:
        details = {}
    return {"error": details, "next": reader.read()}


def read_skip_empty() -> list[Any]:
    return list(jsonlines.Reader(["\n", "  \t", "1\n", "", "2"]).iter(skip_empty=True))


def read_invalid_json() -> dict[str, Any]:
    reader = jsonlines.Reader(['{"x":\n'])
    try:
        reader.read()
    except Exception as exc:
        result = invalid_details(exc)
        result["message_prefix"] = str(exc).startswith("line contains invalid json:")
        return result
    return {}


def read_invalid_utf8() -> dict[str, Any]:
    reader = jsonlines.Reader([b"\xff\xfe\n"])
    try:
        reader.read()
    except Exception as exc:
        result = invalid_details(exc)
        result["message_prefix"] = str(exc).startswith("line is not valid utf-8:")
        return result
    return {}


def read_null() -> dict[str, Any]:
    reader = jsonlines.Reader(["null\n", "null\n"])
    try:
        reader.read()
    except Exception as exc:
        first = invalid_details(exc)
        first["message"] = str(exc)
    else:
        first = {}
    return {"strict": first, "allowed": reader.read(allow_none=True)}


def read_typed_values() -> list[Any]:
    reader = jsonlines.Reader(["1", "1.5", "true", '"x"', "{}", "[]"])
    return [
        reader.read(type=int),
        reader.read(type=float),
        reader.read(type=bool),
        reader.read(type=str),
        reader.read(type=dict),
        reader.read(type=list),
    ]


def read_typed_mismatch() -> dict[str, Any]:
    reader = jsonlines.Reader(["true", "1"])
    errors = []
    for requested in (int, bool):
        try:
            reader.read(type=requested)
        except Exception as exc:
            details = invalid_details(exc)
            details["message"] = str(exc)
            errors.append(details)
    return {"errors": errors}


def read_invalid_type() -> dict[str, Any]:
    reader = jsonlines.Reader([])
    try:
        reader.read(type=tuple)
    except Exception as exc:
        return {"type": type(exc).__name__, "message": str(exc)}
    return {}


def iter_skip_invalid() -> list[Any]:
    reader = jsonlines.Reader(["1", "bad", "null", '{"ok": true}', "3"])
    return list(reader.iter(skip_invalid=True))


def iter_direct() -> dict[str, Any]:
    reader = jsonlines.Reader(["1", "2"])
    iterator = iter(reader)
    return {
        "iterator_is_self": iterator is reader,
        "values": list(iterator),
        "after": list(reader),
    }


def custom_loads() -> dict[str, Any]:
    seen = []

    def loads(value: str) -> dict[str, str]:
        seen.append(type(value).__name__)
        return {"raw": value.rstrip()}

    value = jsonlines.Reader([b"payload\n"], loads=loads).read()
    return {"value": value, "argument_types": seen}


def reader_lifecycle() -> dict[str, Any]:
    stream = io.StringIO("1\n")
    with jsonlines.Reader(stream) as reader:
        inside = reader.read()
        repr_ok = repr(reader).startswith("<jsonlines.Reader at 0x")
    reader.close()
    return {
        "inside": inside,
        "reader_error": error_name(reader.read),
        "stream_closed": stream.closed,
        "repr_ok": repr_ok,
    }


def error_hierarchy() -> dict[str, Any]:
    exc = jsonlines.InvalidLineError("broken", "value  \n", 7)
    return {
        "is_error": isinstance(exc, jsonlines.Error),
        "is_value_error": isinstance(exc, ValueError),
        "line": exc.line,
        "lineno": exc.lineno,
        "message": str(exc),
        "base_error": str(jsonlines.Error("base")),
    }


def writer_text() -> dict[str, Any]:
    stream = io.StringIO()
    writer = jsonlines.Writer(stream)
    counts = [writer.write({"text": "caf\u00e9".replace("\x00", "\u00e9")}), writer.write(None)]
    return {"counts": counts, "text": stream.getvalue()}


def writer_binary_all() -> dict[str, Any]:
    stream = io.BytesIO()
    count = jsonlines.Writer(stream).write_all([{"a": 1}, [2, 3], True])
    return {"count": count, "bytes": stream.getvalue().decode("utf-8")}


def writer_flags() -> dict[str, Any]:
    stream = io.StringIO()
    count = jsonlines.Writer(stream, compact=True, sort_keys=True).write({"b": 2, "a": 1})
    return {"count": count, "text": stream.getvalue()}


def writer_custom_str() -> dict[str, Any]:
    stream = io.BytesIO()
    calls = []

    def dumps(obj: Any) -> str:
        calls.append(obj)
        return f"value={obj}"

    count = jsonlines.Writer(stream, dumps=dumps).write(3)
    return {"count": count, "bytes": stream.getvalue().decode(), "calls": calls}


def writer_custom_bytes() -> dict[str, Any]:
    stream = io.StringIO()

    def dumps(obj: Any) -> bytes:
        return json.dumps(obj, sort_keys=True).encode()

    count = jsonlines.Writer(stream, dumps=dumps).write({"b": 2, "a": 1})
    return {"count": count, "text": stream.getvalue()}


def writer_flush() -> dict[str, Any]:
    class FlushStream(io.StringIO):
        flushes = 0

        def flush(self) -> None:
            self.flushes += 1
            super().flush()

    stream = FlushStream()
    writer = jsonlines.Writer(stream, flush=True)
    writer.write(1)
    writer.write(2)
    return {"flushes": stream.flushes, "text": stream.getvalue()}


def writer_lifecycle() -> dict[str, Any]:
    stream = io.BytesIO()
    with jsonlines.Writer(stream) as writer:
        count = writer.write("x")
        repr_ok = repr(writer).startswith("<jsonlines.Writer at 0x")
    writer.close()
    return {
        "count": count,
        "writer_error": error_name(writer.write, 2),
        "stream_closed": stream.closed,
        "repr_ok": repr_ok,
    }


def open_roundtrip() -> dict[str, Any]:
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "values.jsonl"
        with jsonlines.open(path, "w") as writer:
            writer_type = type(writer).__name__
            writer.write_all([{"a": 1}, "caf\u00e9".replace("\x00", "\u00e9")])
        writer_closed = error_name(writer.write, 3)
        raw = path.read_bytes().decode("utf-8")
        with jsonlines.open(path) as reader:
            reader_type = type(reader).__name__
            values = list(reader)
        reader_closed = error_name(reader.read)
    return {
        "types": [writer_type, reader_type],
        "raw": raw,
        "values": values,
        "closed_errors": [writer_closed, reader_closed],
    }


def open_bom() -> list[Any]:
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "bom.jsonl"
        path.write_bytes(codecs.BOM_UTF8 + b"1\n" + codecs.BOM_UTF8 + b"2\n")
        with jsonlines.open(path) as reader:
            return list(reader)


def open_append() -> dict[str, Any]:
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "append.jsonl"
        with jsonlines.open(path, "w") as writer:
            writer.write(1)
        with jsonlines.open(path, "a") as writer:
            writer.write(2)
        return {"raw": path.read_text(), "values": list(jsonlines.open(path))}


def open_exclusive_invalid() -> dict[str, Any]:
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "exclusive.jsonl"
        with jsonlines.open(path, "x") as writer:
            writer.write(1)
        exists_error = error_name(jsonlines.open, path, "x")
        mode_error = None
        mode_message = None
        try:
            jsonlines.open(path, "rb")
        except Exception as exc:
            mode_error = type(exc).__name__
            mode_message = str(exc)
        return {
            "exists_error": exists_error,
            "mode_error": mode_error,
            "mode_message": mode_message,
        }


def open_custom() -> dict[str, Any]:
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "custom.jsonl"
        with jsonlines.open(path, "w", dumps=lambda obj: f"<{obj}>") as writer:
            writer.write(4)
        seen = []

        def loads(value: str) -> str:
            seen.append(type(value).__name__)
            return value.strip("<>\n")

        with jsonlines.open(path, loads=loads) as reader:
            value = reader.read()
        return {"raw": path.read_text(), "value": value, "argument_types": seen}


OPERATIONS: dict[str, Callable[[], Any]] = {
    name: value
    for name, value in globals().copy().items()
    if callable(value)
    and name
    in {
        "package_surface",
        "read_json_values",
        "read_bytes_unicode",
        "read_eof",
        "read_prefixes",
        "read_empty_policy",
        "read_skip_empty",
        "read_invalid_json",
        "read_invalid_utf8",
        "read_null",
        "read_typed_values",
        "read_typed_mismatch",
        "read_invalid_type",
        "iter_skip_invalid",
        "iter_direct",
        "custom_loads",
        "reader_lifecycle",
        "error_hierarchy",
        "writer_text",
        "writer_binary_all",
        "writer_flags",
        "writer_custom_str",
        "writer_custom_bytes",
        "writer_flush",
        "writer_lifecycle",
        "open_roundtrip",
        "open_bom",
        "open_append",
        "open_exclusive_invalid",
        "open_custom",
    }
}


def main() -> None:
    for line in sys.stdin:
        try:
            request = json.loads(line)
            request_id = request["id"]
            operation = request["operation"]
            result = OPERATIONS[operation]()
            response = {"id": request_id, "ok": True, "result": result}
        except Exception as exc:
            response = {
                "id": request.get("id") if isinstance(request, dict) else None,
                "ok": False,
                "error": {"type": type(exc).__name__, "message": str(exc)},
            }
        print(json.dumps(response, ensure_ascii=True, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
