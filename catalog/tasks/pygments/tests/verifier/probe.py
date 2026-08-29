from __future__ import annotations

import io
import json
import subprocess
import sys

sys.path.insert(0, "/tmp/candidate-site")


def encode(value):
    if isinstance(value, tuple):
        return [encode(item) for item in value]
    if isinstance(value, list):
        return [encode(item) for item in value]
    if isinstance(value, dict):
        return {str(key): encode(item) for key, item in value.items()}
    if isinstance(value, type):
        return value.__name__
    return value


def token_list(tokens):
    return [[repr(kind), text] for kind, text in tokens]


def main(request):
    import pygments

    if not str(getattr(pygments, "__file__", "")).startswith("/tmp/candidate-site/"):
        raise RuntimeError("candidate pygments package was not imported from candidate site")
    op = request["operation"]
    if op == "metadata":
        return {"version": pygments.__version__, "all": list(pygments.__all__)}
    if op == "tokens":
        from pygments.token import Token, string_to_tokentype

        target = Token.Name.Function
        return {
            "repr": repr(target),
            "split": [repr(item) for item in target.split()],
            "contains": target in Token.Name,
            "roundtrip": repr(string_to_tokentype("Name.Function")),
        }
    if op == "lex":
        from pygments.lexers import get_lexer_by_name

        lexer = get_lexer_by_name(request["lexer"], **request.get("options", {}))
        return token_list(list(pygments.lex(request["code"], lexer)))
    if op == "lookup":
        from pygments import lexers

        action = request["action"]
        if action == "name":
            return type(lexers.get_lexer_by_name(request["value"])).__name__
        if action == "filename":
            return type(lexers.get_lexer_for_filename(request["value"])).__name__
        if action == "mime":
            return type(lexers.get_lexer_for_mimetype(request["value"])).__name__
        if action == "guess":
            return type(lexers.guess_lexer(request["value"])).__name__
        if action == "all-count":
            return len(list(lexers.get_all_lexers(plugins=False)))
    if op == "format":
        from pygments.formatters import get_formatter_by_name
        from pygments.lexers import get_lexer_by_name

        formatter = get_formatter_by_name(request["formatter"], **request.get("options", {}))
        lexer = get_lexer_by_name(request["lexer"])
        value = pygments.highlight(request["code"], lexer, formatter)
        return value.decode("utf-8") if isinstance(value, bytes) else value
    if op == "format-outfile":
        from pygments.formatters import get_formatter_by_name
        from pygments.lexers import get_lexer_by_name

        out = io.StringIO()
        pygments.highlight(
            request["code"], get_lexer_by_name("python"), get_formatter_by_name("terminal"), out
        )
        return {"return": None, "out": out.getvalue()}
    if op == "style":
        from pygments.styles import get_style_by_name

        style = get_style_by_name(request["name"])
        return {
            "name": style.__name__,
            "background": style.background_color,
            "styles": len(style.styles),
        }
    if op == "util":
        from pygments import util

        action = request["action"]
        if action == "escape":
            return util.html_escape(request["value"])
        if action == "bool":
            return util.get_bool_opt(request["options"], "value", False)
        if action == "int":
            return util.get_int_opt(request["options"], "value", 7)
        if action == "duplicates":
            return list(util.duplicates_removed(request["values"]))
        if action == "shebang":
            return util.shebang_matches(request["text"], request["regex"])
    if op == "regexopt":
        from pygments.regexopt import regex_opt

        return regex_opt(
            request["values"], prefix=request.get("prefix", ""), suffix=request.get("suffix", "")
        )
    if op == "custom-regex":
        from pygments.lexer import RegexLexer
        from pygments.token import Name, Number, Text

        class DemoLexer(RegexLexer):
            tokens = {"root": [(r"[a-zA-Z_]\w*", Name), (r"\d+", Number), (r"\s+", Text)]}

        return token_list(list(DemoLexer().get_tokens(request["code"])))
    if op == "cli":
        code = (
            "import sys;sys.path.insert(0,'/tmp/candidate-site');"
            "from pygments.cmdline import main;raise SystemExit(main(['pygmentize',*sys.argv[1:]]))"
        )
        completed = subprocess.run(
            [sys.executable, "-I", "-B", "-c", code, *request["args"]],
            input=request.get("input"),
            text=True,
            capture_output=True,
            timeout=5,
        )
        return {
            "code": completed.returncode,
            "stdout": completed.stdout,
            "stderr": completed.stderr,
        }
    raise KeyError(op)


request = json.loads(sys.stdin.read())
try:
    print(
        json.dumps({"ok": True, "value": encode(main(request))}, ensure_ascii=False, sort_keys=True)
    )
except BaseException as error:
    print(
        json.dumps(
            {
                "ok": False,
                "type": f"{type(error).__module__}.{type(error).__qualname__}",
                "message": str(error),
            },
            ensure_ascii=False,
            sort_keys=True,
        )
    )
