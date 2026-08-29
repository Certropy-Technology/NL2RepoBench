from __future__ import annotations

import json
import os
import subprocess
import sys

PROBE = open(os.path.join(os.path.dirname(__file__), "probe.py"), encoding="utf-8").read()


def case(identifier, request, expected=None, *, type_name=None, message=None):
    result = {"id": identifier, "request": request}
    if type_name is not None:
        result["expect_error"] = {"type": type_name, "message": message}
    else:
        result["expected"] = expected
    return result


CASES = [
    case(
        "metadata",
        {"operation": "metadata"},
        {"version": "2.21.0", "all": ["lex", "format", "highlight"]},
    ),
    case(
        "tokens",
        {"operation": "tokens"},
        {
            "repr": "Token.Name.Function",
            "split": ["Token", "Token.Name", "Token.Name.Function"],
            "contains": True,
            "roundtrip": "Token.Name.Function",
        },
    ),
    case(
        "python-lex",
        {"operation": "lex", "lexer": "python", "code": "x = 1\n"},
        [
            ["Token.Name", "x"],
            ["Token.Text", " "],
            ["Token.Operator", "="],
            ["Token.Text", " "],
            ["Token.Literal.Number.Integer", "1"],
            ["Token.Text.Whitespace", "\n"],
        ],
    ),
    case(
        "json-lex",
        {"operation": "lex", "lexer": "json", "code": '{"ok": true}'},
        [
            ["Token.Punctuation", "{"],
            ["Token.Name.Tag", '"ok"'],
            ["Token.Punctuation", ":"],
            ["Token.Text.Whitespace", " "],
            ["Token.Keyword.Constant", "true"],
            ["Token.Punctuation", "}"],
            ["Token.Text.Whitespace", "\n"],
        ],
    ),
    case(
        "javascript-lex",
        {"operation": "lex", "lexer": "javascript", "code": "const n = 2;"},
        [
            ["Token.Keyword.Declaration", "const"],
            ["Token.Text.Whitespace", " "],
            ["Token.Name.Other", "n"],
            ["Token.Text.Whitespace", " "],
            ["Token.Operator", "="],
            ["Token.Text.Whitespace", " "],
            ["Token.Literal.Number.Float", "2"],
            ["Token.Punctuation", ";"],
            ["Token.Text.Whitespace", "\n"],
        ],
    ),
    case(
        "strip-options",
        {
            "operation": "lex",
            "lexer": "python",
            "code": "\n  x\n\n",
            "options": {"stripall": True, "ensurenl": False},
        },
        [["Token.Name", "x"]],
    ),
    case(
        "lookup-name", {"operation": "lookup", "action": "name", "value": "python"}, "PythonLexer"
    ),
    case(
        "lookup-filename",
        {"operation": "lookup", "action": "filename", "value": "example.py"},
        "PythonLexer",
    ),
    case(
        "lookup-mime",
        {"operation": "lookup", "action": "mime", "value": "text/x-python"},
        "PythonLexer",
    ),
    case(
        "lookup-guess",
        {"operation": "lookup", "action": "guess", "value": "def hello():\n    return 1\n"},
        None,
    ),
    case("lookup-count", {"operation": "lookup", "action": "all-count"}, 600),
    case(
        "html-format",
        {
            "operation": "format",
            "formatter": "html",
            "lexer": "python",
            "code": "x < 2\n",
            "options": {"nowrap": True},
        },
        '<span class="n">x</span> <span class="o">&lt;</span> <span class="mi">2</span>\n',
    ),
    case(
        "html-full",
        {
            "operation": "format",
            "formatter": "html",
            "lexer": "python",
            "code": "x = 1\n",
            "options": {"full": True},
        },
        None,
    ),
    case(
        "terminal-format",
        {"operation": "format", "formatter": "terminal", "lexer": "python", "code": "x = 1\n"},
        "x = \x1b[34m1\x1b[39;49;00m\x1b[37m\x1b[39;49;00m\n",
    ),
    case(
        "latex-format",
        {"operation": "format", "formatter": "latex", "lexer": "python", "code": "x = 1\n"},
        None,
    ),
    case(
        "rtf-format",
        {"operation": "format", "formatter": "rtf", "lexer": "python", "code": "x = 1\n"},
        None,
    ),
    case(
        "svg-format",
        {"operation": "format", "formatter": "svg", "lexer": "python", "code": "x = 1\n"},
        None,
    ),
    case("outfile", {"operation": "format-outfile", "code": "x = 1\n"}, None),
    case(
        "style",
        {"operation": "style", "name": "default"},
        {"name": "DefaultStyle", "background": "#f8f8f8", "styles": 80},
    ),
    case(
        "escape",
        {"operation": "util", "action": "escape", "value": '<a href="x">&'},
        "&lt;a href=&quot;x&quot;&gt;&amp;",
    ),
    case("bool", {"operation": "util", "action": "bool", "options": {"value": "yes"}}, True),
    case("int", {"operation": "util", "action": "int", "options": {"value": "12"}}, 12),
    case(
        "duplicates",
        {"operation": "util", "action": "duplicates", "values": ["a", "b", "a", "c", "b"]},
        ["a", "b", "c"],
    ),
    case(
        "shebang",
        {
            "operation": "util",
            "action": "shebang",
            "text": "#!/usr/bin/python3\n",
            "regex": r"python(3)?",
        },
        True,
    ),
    case(
        "regexopt", {"operation": "regexopt", "values": ["cat", "car", "dog"]}, "(ca(?:[rt])|dog)"
    ),
    case(
        "custom-regex",
        {"operation": "custom-regex", "code": "abc 42"},
        [
            ["Token.Name", "abc"],
            ["Token.Text", " "],
            ["Token.Literal.Number", "42"],
            ["Token.Text", "\n"],
        ],
    ),
    case(
        "bytes-lex",
        {"operation": "lex", "lexer": "python", "code": "x = 1\n"},
        [
            ["Token.Name", "x"],
            ["Token.Text", " "],
            ["Token.Operator", "="],
            ["Token.Text", " "],
            ["Token.Literal.Number.Integer", "1"],
            ["Token.Text.Whitespace", "\n"],
        ],
    ),
    case(
        "invalid-lexer",
        {"operation": "lex", "lexer": "does-not-exist", "code": "x"},
        type_name="pygments.util.ClassNotFound",
        message="no lexer",
    ),
    case(
        "invalid-formatter",
        {"operation": "format", "formatter": "does-not-exist", "lexer": "python", "code": "x"},
        type_name="pygments.util.ClassNotFound",
        message="no formatter",
    ),
    case("cli-help", {"operation": "cli", "args": ["-h"]}, None),
    case(
        "cli-highlight",
        {"operation": "cli", "args": ["-l", "python", "-f", "html"], "input": "x = 1\n"},
        None,
    ),
    case(
        "highlight",
        {
            "operation": "format",
            "formatter": "html",
            "lexer": "python",
            "code": "print('hi')\n",
            "options": {"nowrap": True},
        },
        None,
    ),
]


def run_probe(request):
    process = subprocess.run(
        [
            "runuser",
            "-u",
            "candidate",
            "--",
            "env",
            "PYTHONDONTWRITEBYTECODE=1",
            "prlimit",
            "--as=536870912",
            "--cpu=8",
            "--fsize=1048576",
            "--nofile=64",
            "--nproc=32",
            sys.executable,
            "-I",
            "-B",
            "-c",
            PROBE,
        ],
        input=json.dumps(request, ensure_ascii=False, separators=(",", ":")),
        capture_output=True,
        text=True,
        timeout=5,
        check=False,
    )
    if process.returncode != 0:
        return {
            "ok": False,
            "type": "candidate.process",
            "message": (process.stderr or process.stdout)[-2000:],
        }
    return json.loads(process.stdout.splitlines()[-1])


def matches(actual, item):
    if "expect_error" in item:
        expected = item["expect_error"]
        return (
            not actual.get("ok")
            and actual.get("type") == expected["type"]
            and expected["message"] in actual.get("message", "")
        )
    expected = item.get("expected")
    if expected is None:
        return actual.get("ok") is True
    return actual.get("ok") is True and actual.get("value") == expected


leaves = []
for item in CASES:
    try:
        actual = run_probe(item["request"])
        passed = matches(actual, item)
        if item["id"] == "lookup-count":
            passed = (
                actual.get("ok") is True
                and isinstance(actual.get("value"), int)
                and actual["value"] >= 600
            )
        if item["id"] in {
            "lookup-guess",
            "html-full",
            "latex-format",
            "rtf-format",
            "svg-format",
            "outfile",
            "cli-help",
            "cli-highlight",
            "highlight",
        }:
            value = actual.get("value", {})
            if item["id"] == "lookup-guess":
                passed = (
                    actual.get("ok") is True and isinstance(value, str) and value.endswith("Lexer")
                )
            elif item["id"] == "html-full":
                passed = actual.get("ok") is True and "<html" in value and "x" in value
            elif item["id"] == "latex-format":
                passed = actual.get("ok") is True and "\\begin{Verbatim}" in value
            elif item["id"] == "rtf-format":
                passed = actual.get("ok") is True and value.startswith("{\\rtf")
            elif item["id"] == "svg-format":
                passed = actual.get("ok") is True and "<svg" in value
            elif item["id"] == "outfile":
                passed = (
                    actual.get("ok") is True
                    and value.get("return") is None
                    and "x" in value.get("out", "")
                )
            elif item["id"] == "cli-help":
                passed = (
                    actual.get("ok") is True
                    and actual["value"]["code"] == 0
                    and "usage" in actual["value"]["stdout"]
                )
            elif item["id"] == "cli-highlight":
                passed = (
                    actual.get("ok") is True
                    and actual["value"]["code"] == 0
                    and "<span" in actual["value"]["stdout"]
                )
            elif item["id"] == "highlight":
                passed = actual.get("ok") is True and "print" in value and "Token" not in value
        leaves.append(
            {
                "id": item["id"],
                "status": "passed" if passed else "failed",
                "message": "" if passed else json.dumps(actual, sort_keys=True)[:1800],
            }
        )
    except BaseException as error:
        leaves.append(
            {"id": item["id"], "status": "failed", "message": f"{type(error).__name__}: {error}"}
        )
print(json.dumps({"schema_version": "1.0", "leaves": leaves}, sort_keys=True))
