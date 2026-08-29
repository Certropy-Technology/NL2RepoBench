from __future__ import annotations

import argparse
import base64
import io
import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Any


def error_value(exc: BaseException) -> dict[str, Any]:
    result: dict[str, Any] = {"error": f"{type(exc).__module__}.{type(exc).__qualname__}"}
    if hasattr(exc, "offset"):
        result["offset"] = exc.offset  # type: ignore[attr-defined]
    return result


def capture(func: Any) -> Any:
    try:
        return func()
    except BaseException as exc:
        return error_value(exc)


def json_value(value: Any) -> Any:
    if isinstance(value, bytes):
        return {"__bytes__": value.hex()}
    if isinstance(value, tuple):
        return [json_value(item) for item in value]
    if isinstance(value, list):
        return [json_value(item) for item in value]
    if isinstance(value, dict):
        return {str(json_value(key)): json_value(item) for key, item in value.items()}
    return value


def field_summary(field: Any) -> list[Any]:
    return [field.field_name, field.value, field.content_type]


def file_summary(file: Any) -> list[Any]:
    position = file.file_object.tell()
    file.file_object.seek(0)
    data = file.file_object.read()
    file.file_object.seek(position)
    return [file.field_name, file.file_name, file.actual_file_name, file.size, file.in_memory, file.content_type, data]


def header_summary(value: Any) -> list[Any]:
    media_type, parameters = value
    return [media_type, [[key, parameters[key]] for key in sorted(parameters)]]


def multipart_body(boundary: bytes = b"AaB03x") -> bytes:
    return (
        b"--" + boundary + b"\r\n"
        b'Content-Disposition: form-data; name="alpha"\r\n\r\n'
        b"one\r\n"
        b"--" + boundary + b"\r\n"
        b'Content-Disposition: form-data; name="upload"; filename="hello.txt"\r\n'
        b"Content-Type: text/plain\r\n\r\n"
        b"file-data\r\n"
        b"--" + boundary + b"--\r\n"
    )


def form_parse(body: bytes, content_type: str, boundary: bytes | None = None, chunks: list[int] | None = None) -> dict[str, Any]:
    from python_multipart.multipart import FormParser

    fields: list[Any] = []
    files: list[Any] = []
    parser = FormParser(content_type, fields.append, files.append, boundary=boundary)
    if chunks is None:
        parser.write(body)
    else:
        start = 0
        for end in chunks:
            parser.write(body[start:end])
            start = end
        parser.write(body[start:])
    parser.finalize()
    return {
        "fields": [field_summary(item) for item in fields],
        "files": [file_summary(item) for item in files],
    }


def run_scenarios() -> dict[str, Any]:
    import python_multipart
    from python_multipart import BaseParser, FormParser, MultipartParser, OctetStreamParser, QuerystringParser
    from python_multipart.decoders import Base64Decoder, QuotedPrintableDecoder
    from python_multipart.exceptions import (
        DecodeError,
        FileError,
        FormParserError,
        MultipartParseError,
        ParseError,
        QuerystringParseError,
    )
    from python_multipart.multipart import Field, File, create_form_parser, parse_form, parse_options_header

    result: dict[str, Any] = {}
    result["imports/root"] = [python_multipart.__version__, list(python_multipart.__all__), sorted(name for name in python_multipart.__all__ if hasattr(python_multipart, name))]
    result["imports/compat"] = capture(lambda: __import__("multipart").__version__)
    result["imports/exceptions"] = [issubclass(ParseError, FormParserError), issubclass(FileError, OSError), issubclass(MultipartParseError, ParseError), issubclass(QuerystringParseError, ParseError), issubclass(DecodeError, ParseError)]
    result["imports/offset"] = capture(lambda: [ParseError("bad", offset=7).offset, str(ParseError("bad", offset=7))])

    result["headers/basic"] = header_summary(parse_options_header(b'Multipart/Form-Data; boundary="abc"; charset=utf-8'))
    result["headers/quoted"] = header_summary(parse_options_header('text/plain; note="a\\"b;c"; token=VaL'))
    result["headers/empty"] = [header_summary(parse_options_header(None)), header_summary(parse_options_header(b"")), header_summary(parse_options_header("  "))]
    result["headers/extended"] = header_summary(parse_options_header(b"text/plain; filename*=utf-8''ignored.txt; filename=plain.txt"))
    result["headers/continuation"] = header_summary(parse_options_header(b"text/plain; filename*0*=utf-8''a; filename*1*=b"))
    result["headers/case"] = header_summary(parse_options_header(b"TEXT/PLAIN; X-TEST=Value"))
    result["headers/bytes-and-text"] = header_summary(parse_options_header("application/json; boundary='x'"))

    field = Field(b"name", content_type="text/plain")
    result["values/field-lifecycle"] = [field.write(b"a"), field.on_data(b"b"), field.field_name, field.value, field.content_type]
    result["values/field-finalize"] = capture(lambda: [field.finalize(), field.value, repr(field)])
    result["values/field-from-value"] = field_summary(Field.from_value(b"x", b"value"))
    none_field = Field.from_value(b"empty", None)
    result["values/field-none"] = [none_field.field_name, none_field.value]
    result["values/field-equality"] = [Field.from_value(b"a", b"b") == Field.from_value(b"a", b"b"), Field.from_value(b"a", b"b") == Field.from_value(b"a", b"c")]
    result["values/file-memory"] = capture(lambda: (lambda f: (f.write(b"abc"), f.finalize(), file_summary(f)))(File(b"hello.txt", b"upload", content_type="text/plain")))
    with tempfile.TemporaryDirectory() as directory:
        f = File(b"../report.txt", b"upload", {"UPLOAD_DIR": os.fsencode(directory), "UPLOAD_KEEP_FILENAME": True, "UPLOAD_KEEP_EXTENSIONS": False})
        f.write(b"payload")
        f.flush_to_disk()
        f.file_object.seek(0)
        result["values/file-disk"] = [os.path.basename(f.actual_file_name), f.in_memory, f.file_object.read()]
        f.close()

    f = File(b"big.bin", config={"MAX_MEMORY_FILE_SIZE": 2})
    f.write(b"abc")
    f.file_object.seek(0)
    result["values/file-threshold"] = [f.in_memory, f.size, f.file_object.read()]
    f.close()

    class Sink:
        def __init__(self) -> None:
            self.data: list[bytes] = []
            self.events: list[str] = []
        def write(self, data: bytes) -> int:
            self.data.append(data)
            return len(data)
        def close(self) -> None:
            self.events.append("close")
        def finalize(self) -> None:
            self.events.append("finalize")

    sink = Sink()
    decoder = Base64Decoder(sink)
    result["decoders/base64"] = [decoder.write(b"Zm"), decoder.write(b"9v"), decoder.finalize(), b"".join(sink.data)]
    sink = Sink()
    decoder = Base64Decoder(sink)
    bad = capture(lambda: [decoder.write(b"Zg"), decoder.finalize()])
    result["decoders/base64-error"] = bad
    sink = Sink()
    decoder = Base64Decoder(sink)
    result["decoders/base64-invalid"] = capture(lambda: decoder.write(b"!!!!"))
    sink = Sink()
    decoder = QuotedPrintableDecoder(sink)
    result["decoders/quoted-printable"] = [decoder.write(b"hello="), decoder.write(b"20world"), decoder.finalize(), b"".join(sink.data)]
    sink = Sink()
    decoder = QuotedPrintableDecoder(sink)
    decoder.write(b"line=3Dvalue")
    decoder.finalize()
    decoder.close()
    result["decoders/forward-lifecycle"] = [b"".join(sink.data), sink.events]
    result["decoders/repr"] = repr(Base64Decoder(Sink())).startswith("Base64Decoder(underlying=")

    events: list[Any] = []
    parser = BaseParser()
    parser.set_callback("start", lambda: events.append("start"))
    parser.set_callback("data", lambda data, start, end: events.append(data[start:end]))
    parser.callback("start")
    parser.callback("data", b"prefix-value", 7, 12)
    parser.set_callback("start", None)
    result["parsers/base-callbacks"] = events

    events = []
    octets = OctetStreamParser({"on_start": lambda: events.append("start"), "on_data": lambda data, start, end: events.append(data[start:end]), "on_end": lambda: events.append("end")}, max_size=5)
    result["parsers/octet"] = [octets.write(b"abc"), octets.write(b"def"), octets.finalize(), events]
    result["parsers/octet-invalid"] = capture(lambda: OctetStreamParser(max_size=0))

    events = []
    query = QuerystringParser({"on_field_start": lambda: events.append("start"), "on_field_name": lambda data, start, end: events.append(["name", data[start:end]]), "on_field_data": lambda data, start, end: events.append(["data", data[start:end]]), "on_field_end": lambda: events.append("field-end"), "on_end": lambda: events.append("end")})
    query.write(b"a=1&b")
    query.finalize()
    result["parsers/query-events"] = events
    result["parsers/query-strict"] = capture(lambda: QuerystringParser(strict_parsing=True).write(b"bare&ok=yes"))
    result["parsers/query-max"] = capture(lambda: [QuerystringParser(max_size=3).write(b"a=123"), QuerystringParser(max_size=3).finalize()])
    result["parsers/query-repr"] = repr(QuerystringParser(strict_parsing=True, max_size=4))
    result["parsers/octet-repr"] = repr(OctetStreamParser(max_size=4))

    body = multipart_body()
    result["multipart/form"] = form_parse(body, "multipart/form-data", b"AaB03x")
    result["multipart/chunks"] = form_parse(body, "multipart/form-data", b"AaB03x", [1, 4, 9, 19, 32, 55, 87, 111])
    encoded = b"--b\r\nContent-Disposition: form-data; name=\"x\"\r\nContent-Transfer-Encoding: base64\r\n\r\n" + base64.b64encode(b"hello") + b"\r\n--b--\r\n"
    result["multipart/base64"] = form_parse(encoded, "multipart/form-data", b"b")
    qp = b"--b\r\nContent-Disposition: form-data; name=\"x\"\r\nContent-Transfer-Encoding: quoted-printable\r\n\r\nhello=20world\r\n--b--\r\n"
    result["multipart/quoted-printable"] = form_parse(qp, "multipart/form-data", b"b")
    preamble = b"\r\nignored preamble\r\n" + body + b"epilogue"
    result["multipart/preamble-epilogue"] = form_parse(preamble, "multipart/form-data", b"AaB03x")
    result["multipart/case-headers"] = form_parse(body.replace(b"Content-Disposition", b"content-disposition").replace(b"Content-Type", b"content-type"), "multipart/form-data", b"AaB03x")
    result["multipart/max-size"] = capture(lambda: MultipartParser(b"b", max_size=4).write(b"12345"))
    result["multipart/header-count"] = capture(lambda: MultipartParser(b"b", max_header_count=1).write(b"--b\r\nA: b\r\nC: d\r\n\r\nbody\r\n--b--\r\n"))
    result["multipart/invalid-content"] = capture(lambda: FormParser("application/not-real", None, None))
    result["multipart/no-boundary"] = capture(lambda: create_form_parser({"Content-Type": b"multipart/form-data"}, None, None))
    result["multipart/urlencoded"] = form_parse(b"first=one+two&empty=&bare", "application/x-www-form-urlencoded")
    octet_data: list[bytes] = []
    fp = FormParser("application/octet-stream", None, None, config={"UPLOAD_DIR": None})
    fp.parser.set_callback("data", lambda data, start, end: octet_data.append(data[start:end]))
    fp.write(b"raw")
    fp.finalize()
    result["multipart/octet-form"] = octet_data
    fields: list[Any] = []
    files: list[Any] = []
    parse_form({"Content-Type": b"multipart/form-data; boundary=AaB03x", "Content-Length": str(len(body)).encode()}, io.BytesIO(body), fields.append, files.append)
    result["multipart/parse-form"] = {"fields": [field_summary(item) for item in fields], "files": [file_summary(item) for item in files]}
    result["multipart/create-parser"] = type(create_form_parser({"Content-Type": b"application/x-www-form-urlencoded"}, None, None)).__name__
    result["multipart/parse-errors"] = capture(lambda: parse_form({"Content-Type": b"text/plain"}, io.BytesIO(b"x"), None, None))
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate-site", required=True)
    args = parser.parse_args()
    if os.path.realpath(args.candidate_site) != "/tmp/candidate-site":
        raise ValueError("candidate site is unavailable")
    sys.path.insert(0, args.candidate_site)
    print(json.dumps({"ok": True, "results": json_value(run_scenarios())}, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(json.dumps({"ok": False, **error_value(exc)}, sort_keys=True))
