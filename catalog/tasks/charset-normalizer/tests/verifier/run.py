from __future__ import annotations

import json

from nl2repobench.verification.candidate_client import execute_script, metadata_requires


def observe(source: str) -> dict[str, object]:
    result = execute_script(source, timeout_sec=20.0)
    value: dict[str, object] = {"ok": result.ok, "value": result.value}
    if not result.ok:
        value["exception_type"] = result.exception_type
        value["exception_message"] = result.exception_message
    return value


def ok(value: object) -> dict[str, object]:
    return {"ok": True, "value": value}


CASES: list[tuple[str, str, dict[str, object]]] = [
    (
        "public-surface",
        "import charset_normalizer as c\nresult=[c.__version__,c.VERSION,sorted(c.__all__)]",
        ok(["3.5.1", ["3", "5", "1"], ["CharsetMatch", "CharsetMatches", "VERSION", "__version__", "detect", "from_bytes", "from_fp", "from_path", "is_binary", "set_logging_handler"]]),
    ),
    (
        "signatures",
        "import inspect,charset_normalizer as c\nresult=[str(inspect.signature(x)) for x in (c.from_bytes,c.from_fp,c.from_path,c.is_binary,c.detect)]",
        ok(["(sequences: 'bytes | bytearray', steps: 'int' = 5, chunk_size: 'int' = 512, threshold: 'float' = 0.2, cp_isolation: 'list[str] | None' = None, cp_exclusion: 'list[str] | None' = None, preemptive_behaviour: 'bool' = True, explain: 'bool' = False, language_threshold: 'float' = 0.1, enable_fallback: 'bool' = True) -> 'CharsetMatches'", "(fp: 'BinaryIO', steps: 'int' = 5, chunk_size: 'int' = 512, threshold: 'float' = 0.2, cp_isolation: 'list[str] | None' = None, cp_exclusion: 'list[str] | None' = None, preemptive_behaviour: 'bool' = True, explain: 'bool' = False, language_threshold: 'float' = 0.1, enable_fallback: 'bool' = True) -> 'CharsetMatches'", "(path: 'str | bytes | PathLike', steps: 'int' = 5, chunk_size: 'int' = 512, threshold: 'float' = 0.2, cp_isolation: 'list[str] | None' = None, cp_exclusion: 'list[str] | None' = None, preemptive_behaviour: 'bool' = True, explain: 'bool' = False, language_threshold: 'float' = 0.1, enable_fallback: 'bool' = True) -> 'CharsetMatches'", "(fp_or_path_or_payload: 'PathLike | str | BinaryIO | bytes', steps: 'int' = 5, chunk_size: 'int' = 512, threshold: 'float' = 0.2, cp_isolation: 'list[str] | None' = None, cp_exclusion: 'list[str] | None' = None, preemptive_behaviour: 'bool' = True, explain: 'bool' = False, language_threshold: 'float' = 0.1, enable_fallback: 'bool' = False) -> 'bool'", "(byte_str: 'bytes', should_rename_legacy: 'bool' = False, **kwargs: 'Any') -> 'ResultDict'"]),
    ),
    (
        "empty-detection",
        "from charset_normalizer import from_bytes\nm=from_bytes(b'').best(); result=[m.encoding,str(m),m.byte_order_mark,m.language,m.multi_byte_usage,m.alphabets]",
        ok(["utf_8", "", False, "Unknown", 0.0, []]),
    ),
    (
        "ascii-detection",
        "from charset_normalizer import from_bytes\nm=from_bytes(b'plain ascii').best(); result=[m.encoding,str(m),m.language,m.percent_chaos,m.percent_coherence,m.alphabets,m.output().decode()]",
        ok(["ascii", "plain ascii", "English", 0.0, 0.0, ["Basic Latin"], "plain ascii"]),
    ),
    (
        "utf8-detection",
        "from charset_normalizer import from_bytes\ns='Bсеки човек има право на образование.'; m=from_bytes(s.encode()).best(); result=[m.encoding,str(m),m.byte_order_mark]",
        ok(["utf_8", "Bсеки човек има право на образование.", False]),
    ),
    (
        "utf8-sig",
        "from charset_normalizer import from_bytes\nm=from_bytes('Hello'.encode('utf-8-sig')).best(); result=[m.encoding,str(m),m.bom,m.raw.hex()]",
        ok(["utf_8", "Hello", True, "efbbbf48656c6c6f"]),
    ),
    (
        "utf16-bom",
        "from charset_normalizer import from_bytes\nm=from_bytes('hello'.encode('utf-16')).best(); result=[m.encoding,str(m),m.bom,m.output().decode()]",
        ok(["utf_16", "hello", True, "hello"]),
    ),
    (
        "utf32-bom",
        "from charset_normalizer import from_bytes\nm=from_bytes('hello'.encode('utf-32')).best(); result=[m.encoding,str(m),m.bom]",
        ok(["utf_32", "hello", True]),
    ),
    (
        "cp-isolation",
        "from charset_normalizer import from_bytes\np=('Привет мир ' * 8).encode('cp1251'); r=from_bytes(p,cp_isolation=['cp1251']); result=[len(r),r.best().encoding,str(r.best())]",
        ok([1, "cp1251", "Привет мир " * 8]),
    ),
    (
        "cp-exclusion",
        "from charset_normalizer import from_bytes\nr=from_bytes(b'plain ascii',cp_exclusion=['ascii']); result=['ascii' not in [m.encoding for m in r],bool(r)]",
        ok([True, True]),
    ),
    (
        "invalid-input",
        "from charset_normalizer import from_bytes\nfrom_bytes('text')",
        {"ok": False, "value": None, "exception_type": "builtins.TypeError", "exception_message": "Expected object of type bytes or bytearray, got: <class 'str'>"},
    ),
    (
        "from-fp",
        "import io\nfrom charset_normalizer import from_fp\nm=from_fp(io.BytesIO('hello'.encode('utf-16'))).best(); result=[m.encoding,str(m)]",
        ok(["utf_16", "hello"]),
    ),
    (
        "from-path",
        "import tempfile,pathlib\nfrom charset_normalizer import from_path\np=pathlib.Path(tempfile.gettempdir())/'cn-path.txt'; p.write_bytes('Hello'.encode('utf-8-sig')); m=from_path(p).best(); p.unlink(); result=[m.encoding,str(m),m.bom]",
        ok(["utf_8", "Hello", True]),
    ),
    (
        "is-binary-bytes",
        "from charset_normalizer import is_binary\nresult=[is_binary(b'plain text'),is_binary(bytes(range(256))*8)]",
        ok([False, True]),
    ),
    (
        "is-binary-file",
        "import io\nfrom charset_normalizer import is_binary\nresult=[is_binary(io.BytesIO(b'plain text')),is_binary(io.BytesIO(bytes(range(256))*8))]",
        ok([False, True]),
    ),
    (
        "legacy-detect",
        "from charset_normalizer import detect\nresult=[detect('Hello'.encode('utf-8-sig')),detect('hello'.encode('utf-16'))]",
        ok([{"encoding": "UTF-8-SIG", "language": "", "confidence": 1.0}, {"encoding": "UTF-16", "language": "", "confidence": 1.0}]),
    ),
    (
        "legacy-invalid",
        "from charset_normalizer import detect\ndetect('text')",
        {"ok": False, "value": None, "exception_type": "builtins.TypeError", "exception_message": "Expected object of type bytes or bytearray, got: <class 'str'>"},
    ),
    (
        "matches-empty",
        "from charset_normalizer.models import CharsetMatches\nr=CharsetMatches(); result=[len(r),bool(r),r.best(),r.first()]",
        ok([0, False, None, None]),
    ),
    (
        "matches-order",
        "from charset_normalizer.models import CharsetMatch,CharsetMatches\nr=CharsetMatches(); r.append(CharsetMatch(b'abc','ascii',.1,False,[])); r.append(CharsetMatch(b'abc','utf_8',0,False,[])); result=[[x.encoding for x in r],r.best().encoding,r.first().encoding]",
        ok([["utf_8", "ascii"], "utf_8", "utf_8"]),
    ),
    (
        "matches-index-alias",
        "from charset_normalizer.models import CharsetMatch,CharsetMatches\nr=CharsetMatches([CharsetMatch(b'abc','utf_8',0,False,[])]); result=[r[0].encoding,r['utf-8'].encoding]",
        ok(["utf_8", "utf_8"]),
    ),
    (
        "matches-invalid-append",
        "from charset_normalizer.models import CharsetMatches\nCharsetMatches().append('bad')",
        {"ok": False, "value": None, "exception_type": "builtins.ValueError", "exception_message": "Cannot append instance '<class 'str'>' to CharsetMatches"},
    ),
    (
        "match-properties",
        "from charset_normalizer.models import CharsetMatch\nm=CharsetMatch('café'.encode(),'utf_8',.125,False,[('French',.75)]); result=[m.encoding,m.language,m.languages,m.chaos,m.coherence,m.percent_chaos,m.percent_coherence,m.raw.hex(),m.could_be_from_charset,m.has_submatch]",
        ok(["utf_8", "French", ["French"], 0.125, 0.75, 12.5, 75.0, "636166c3a9", ["utf_8"], False]),
    ),
    (
        "match-output",
        "from charset_normalizer.models import CharsetMatch\nm=CharsetMatch('café'.encode(),'utf_8',0,False,[]); result=[str(m),m.output('utf_16_le').hex(),m.alphabets]",
        ok(["café", "630061006600e900", ["Basic Latin", "Latin-1 Supplement"]]),
    ),
    (
        "iana-name",
        "from charset_normalizer.utils import iana_name\nresult=[iana_name('utf-8'),iana_name('latin1'),iana_name('windows-1252'),iana_name('not-real',False)]",
        ok(["utf_8", "latin_1", "cp1252", "not_real"]),
    ),
    (
        "iana-name-strict",
        "from charset_normalizer.utils import iana_name\niana_name('not-real')",
        {"ok": False, "value": None, "exception_type": "builtins.ValueError", "exception_message": "Unable to retrieve IANA for 'not_real'"},
    ),
    (
        "declared-encoding",
        "from charset_normalizer.utils import any_specified_encoding\nresult=[any_specified_encoding(b'<meta charset=\"windows-1252\">'),any_specified_encoding(b'# coding: utf-8'),any_specified_encoding(b'plain')]",
        ok(["cp1252", "utf_8", None]),
    ),
    (
        "identify-bom",
        "from charset_normalizer.utils import identify_sig_or_bom\nresult=[[a,b.hex()] for a,b in (identify_sig_or_bom(b'\\xef\\xbb\\xbfhi'),identify_sig_or_bom(b'\\xff\\xfeh\\x00'),identify_sig_or_bom(b'plain'))]",
        ok([["utf_8", "efbbbf"], ["utf_16", "fffe"], [None, ""]]),
    ),
    (
        "unicode-ranges",
        "from charset_normalizer.utils import unicode_range\nresult=[unicode_range(x) for x in ['a','é','中','あ','ア','한','ก','ع','😀','\\x00']]",
        ok(["Basic Latin", "Latin-1 Supplement", "CJK Unified Ideographs", "Hiragana", "Katakana", "Hangul Syllables", "Thai", "Arabic", "Emoticons", "Control character"]),
    ),
    (
        "character-classification",
        "from charset_normalizer import utils as u\nresult=[[u.is_accentuated('é'),u.is_latin('é')],[u.is_cjk('中'),u.is_hiragana('あ'),u.is_katakana('ア'),u.is_hangul('한')],[u.is_thai('ก'),u.is_arabic('ع'),u.is_emoticon('😀')],[u.is_punctuation('!'),u.is_separator(' '),u.is_symbol('😀'),u.is_unprintable('\\x00')]]",
        ok([[True, True], [True, True, True, True], [True, True, True], [True, True, True, True]]),
    ),
    (
        "remove-accent",
        "from charset_normalizer.utils import remove_accent\nresult=[remove_accent(x) for x in ['é','À','a']]",
        ok(["e", "A", "a"]),
    ),
    (
        "cli-version",
        "import io,contextlib\nfrom charset_normalizer.cli import cli_detect\nout=io.StringIO()\ntry:\n with contextlib.redirect_stdout(out): cli_detect(['--version'])\nexcept SystemExit as exc:\n result=[exc.code,out.getvalue().strip()]",
        ok([0, "Charset-Normalizer 3.5.1 - Python 3.12.14 - Unicode 15.0.0 - SpeedUp OFF"]),
    ),
    (
        "cli-minimal",
        "import io,contextlib,tempfile,pathlib\nfrom charset_normalizer.cli import cli_detect\np=pathlib.Path(tempfile.gettempdir())/'cn-cli.txt'; p.write_bytes(b'plain ascii'); out=io.StringIO()\nwith contextlib.redirect_stdout(out): code=cli_detect(['-m',str(p)])\np.unlink(); result=[code,out.getvalue().strip()]",
        ok([0, "ascii"]),
    ),
]


def main() -> None:
    leaves: list[dict[str, object]] = []
    for identifier, source, expected in CASES:
        actual = observe(source)
        leaf: dict[str, object] = {
            "id": identifier,
            "status": "passed" if actual == expected else "failed",
        }
        if actual != expected:
            leaf["message"] = json.dumps({"actual": actual, "expected": expected}, ensure_ascii=False, sort_keys=True)
        leaves.append(leaf)
    requirement = metadata_requires("charset-normalizer")
    leaves.append(
        {
            "id": "metadata-no-runtime-dependencies",
            "status": "passed" if requirement.ok and requirement.value in (None, []) else "failed",
            "message": "" if requirement.ok and requirement.value in (None, []) else repr(requirement),
        }
    )
    print(json.dumps({"schema_version": "1.0", "leaves": leaves}, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
