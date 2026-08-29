from __future__ import annotations

import json
import textwrap

from nl2repobench.verification.candidate_client import execute_script, run_module


def check(label: str, source: str, expected: object) -> dict[str, object]:
    observed = execute_script(source, timeout_sec=20.0)
    if not observed.ok:
        return {"id": label, "status": "failed", "message": observed.exception_message or "candidate error"}
    if observed.value != expected:
        return {"id": label, "status": "failed", "message": f"expected {expected!r}, got {observed.value!r}"}
    return {"id": label, "status": "passed"}


def check_exception(label: str, source: str, expected_type: str, expected_code: str | None, expected_position: int | None = 1) -> dict[str, object]:
    wrapped = "try:\n" + textwrap.indent(source, "    ") + (
        "\n    result = ('no-exception',)\n"
        "except BaseException as exc:\n"
        "    result = (type(exc).__name__, getattr(exc, 'code', None), "
        "getattr(exc, 'position', None))\n"
    )
    observed = execute_script(wrapped, timeout_sec=20.0)
    expected = [expected_type, expected_code, expected_position]
    if not observed.ok or observed.value != expected:
        return {"id": label, "status": "failed", "message": f"expected {expected!r}, got {observed!r}"}
    return {"id": label, "status": "passed"}


def check_module(label: str, args: list[str], expected_stdout: str, input_text: str | None = None, expected_returncode: int = 0) -> dict[str, object]:
    observed = run_module("idna", args, input_text=input_text)
    if observed.returncode != expected_returncode or observed.stdout != expected_stdout:
        return {"id": label, "status": "failed", "message": f"module result {observed!r}"}
    return {"id": label, "status": "passed"}


def main() -> None:
    leaves: list[dict[str, object]] = []
    leaves.append(check("exports-and-version", "import idna; result = [idna.__version__, idna.unicode_version, sorted(idna.__all__)]", ["3.19", "17.0.0", sorted([
        "__version__", "unicode_version", "IDNABidiError", "IDNAError", "InvalidCodepoint", "InvalidCodepointContext",
        "alabel", "check_bidi", "check_hyphen_ok", "check_initial_combiner", "check_label", "check_nfc", "decode", "encode",
        "intranges_contain", "ulabel", "uts46_remap", "valid_contextj", "valid_contexto", "valid_label_length", "valid_string_length",
    ])]))
    leaves.append(check("encode-ascii", "import idna; result = idna.encode('www.example.com')", "b'www.example.com'"))
    leaves.append(check("encode-unicode", "import idna; result = idna.encode('bücher.example')", "b'xn--bcher-kva.example'"))
    leaves.append(check("decode-unicode", "import idna; result = idna.decode(b'xn--bcher-kva.example')", "bücher.example"))
    leaves.append(check("trailing-dot-and-bytes", "import idna; result = [idna.encode('bücher.example.'), idna.decode(b'xn--bcher-kva.example.') ]", ["b'xn--bcher-kva.example.'", "bücher.example."]))
    leaves.append(check("uts46-remap", "import idna; result = [idna.uts46_remap('Ａ.Example.'), idna.encode('Ａ.Example.', uts46=True)]", ["a.example.", "b'a.example.'"]))
    leaves.append(check("uts46-transitional", "import idna; result = idna.uts46_remap('faß.de', transitional=True)", "faß.de"))
    leaves.append(check("label-round-trip", "import idna; result = [idna.alabel('bücher'), idna.ulabel('xn--bcher-kva')]", ["b'xn--bcher-kva'", "bücher"]))
    leaves.append(check("length-helpers", "import idna; result = [idna.valid_label_length('a'*63), idna.valid_label_length('a'*64), idna.valid_string_length('a'*253, False), idna.valid_string_length('a'*254, True), idna.valid_string_length('a'*254, False)]", [True, False, True, True, False]))
    leaves.append(check_exception("empty-label", "import idna; idna.check_label('')", "IDNAError", "empty_label", None))
    leaves.append(check_exception("hyphen-rule", "import idna; idna.check_label('-bad')", "IDNAError", "hyphen_start_end", None))
    leaves.append(check_exception("invalid-utf8", "import idna; idna.check_label(b'\\xff')", "IDNAError", "invalid_utf8", None))
    leaves.append(check_exception("disallowed-codepoint", "import idna; idna.check_label('a/b')", "InvalidCodepoint", "disallowed_codepoint", 2))
    leaves.append(check_exception("bidi-error", "import idna; idna.check_bidi('a\\u05d0')", "IDNABidiError", "bidi_rule_5", 2))
    leaves.append(check("context-rules", "import idna; result = (idna.valid_contexto('l·l', 1), idna.valid_contexto('l·x', 1), idna.valid_contextj('a\\u200cب', 1), idna.valid_contextj('a\\u200d', 1))", [True, False, False, False]))
    leaves.append(check_exception("compat-shim", "from idna.compat import ToASCII, ToUnicode, nameprep; assert ToASCII('bücher') == b'xn--bcher-kva'; assert ToUnicode(b'xn--bcher-kva') == 'bücher'; nameprep('x')", "NotImplementedError", None, None))
    leaves.append(check("intranges", "from idna.intranges import intranges_from_list, intranges_contain; r = intranges_from_list([1,2,3,7]); result = [intranges_contain(2, r), intranges_contain(4, r), intranges_contain(7, r)]", [True, False, True]))
    leaves.append(check("codec-stateless", "import codecs, idna.codec; result = (codecs.encode('bücher.example', 'idna2008'), codecs.decode(b'xn--bcher-kva.example', 'idna2008'))", ["b'xn--bcher-kva.example'", "bücher.example"]))
    leaves.append(check("codec-incremental", "import codecs, idna.codec; e=codecs.getincrementalencoder('idna2008')(); d=codecs.getincrementaldecoder('idna2008')(); result=(e.encode('bücher.', False)+e.encode('example', True), d.decode(b'xn--bcher-kva.', False)+d.decode(b'example', True))", ["b'xn--bcher-kva.example'", "bücher.example"]))
    leaves.append(check_exception("codec-errors", "import codecs, idna.codec; codecs.encode('x', 'idna2008', 'ignore')", "IDNAError", "unsupported_errors", None))
    leaves.append(check_module("cli-explicit", ["--encode", "bücher.example"], "xn--bcher-kva.example\n"))
    leaves.append(check_module("cli-autodetect", ["xn--bcher-kva.example", "xn--bcher-kva.de"], "bücher.example\nbücher.de\n"))
    leaves.append(check_module("cli-stdin", [], "xn--bcher-kva.example\n", "bücher.example\n\n"))
    leaves.append(check_module("cli-error-continue", ["--encode", "bücher.example", "a..b"], "xn--bcher-kva.example\n", expected_returncode=1))
    leaves.append(check("distribution-metadata", "import importlib.metadata; result = importlib.metadata.version('idna')", "3.19"))
    print(json.dumps({"schema_version": "1.0", "leaves": leaves}, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
