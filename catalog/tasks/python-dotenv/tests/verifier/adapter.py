from __future__ import annotations

import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile


SITE = os.environ.get("NL2REPO_DOTENV_CANDIDATE_SITE", "/tmp/candidate-site")
DEPS = os.environ.get("NL2REPO_CANDIDATE_DEPENDENCIES", "/opt/candidate-dependencies/site")
sys.path[:0] = [SITE, DEPS]

import dotenv


def clean_env(names: list[str]) -> None:
    for name in names:
        os.environ.pop(name, None)


def cli(args: list[str], cwd: Path, extra_env: dict[str, str] | None = None) -> dict[str, object]:
    code = "import sys; sys.path[:0]=sys.argv[1:3]; sys.argv=sys.argv[:1]+sys.argv[3:]; sys.argv[0]='python -m dotenv'; from dotenv.__main__ import cli; cli()"
    env = os.environ.copy()
    env.update(extra_env or {})
    completed = subprocess.run(
        [sys.executable, "-I", "-c", code, SITE, DEPS, *args], cwd=cwd,
        text=True, capture_output=True, timeout=15, check=False, env=env,
    )
    marker = str(cwd)
    return {
        "code": completed.returncode,
        "stdout": completed.stdout.replace(marker, "<tmp>"),
        "stderr": completed.stderr.replace(marker, "<tmp>"),
    }


def package_surface() -> object:
    from dotenv.version import __version__

    return {
        "version": __version__,
        "exports": sorted(name for name in dotenv.__all__ if name != "load_ipython_extension"),
        "cli_string": dotenv.get_cli_string("config.env", "set", "GREETING", "hello world", "auto"),
    }


def parse_basics() -> object:
    text = "# note\n export PLAIN = value \nEMPTY=\nNOVALUE\nSPACED=hello world   # note\nHASH=a#b\n"
    return dict(dotenv.dotenv_values(stream=io.StringIO(text)))


def parse_quotes() -> object:
    text = "SINGLE='it\\'s ok'\nDOUBLE=\"line\\n\\tquoted\\\"\"\nMULTI='a\nb'\nUNICODE=雪\n"
    return dict(dotenv.dotenv_values(stream=io.StringIO(text)))


def parse_invalid() -> object:
    return dict(dotenv.dotenv_values(stream=io.StringIO("A=one\nbad: value\nB=two\n")))


def parse_no_interpolate() -> object:
    return dict(dotenv.dotenv_values(stream=io.StringIO("A=one\nB=${A}\nC=$A"), interpolate=False))


def interpolate_environment() -> object:
    clean_env(["EXT", "MISSING"]); os.environ["EXT"] = "outside"
    return dict(dotenv.dotenv_values(stream=io.StringIO("A=${EXT}\nB=${MISSING}\nC=${MISSING:-fallback}\n")))


def interpolate_file_order() -> object:
    clean_env(["A"]); os.environ["A"] = "outside"
    return dict(dotenv.dotenv_values(stream=io.StringIO("A=first\nB=${A}\nA=last\nC=${A}\n")))


def interpolation_bare_and_default() -> object:
    clean_env(["X"])
    return dict(dotenv.dotenv_values(stream=io.StringIO("A=$X\nB=x${X:-d}y\nC=${X}${X}\n")))


def get_key_values() -> object:
    with tempfile.TemporaryDirectory() as raw:
        path = Path(raw) / ".env"; path.write_text("café=thé\nNOVALUE\n", encoding="utf-8")
        return [dotenv.get_key(path, "café"), dotenv.get_key(path, "NOVALUE"), dotenv.get_key(path, "missing")]


def find_parent() -> object:
    with tempfile.TemporaryDirectory() as raw:
        root = Path(raw); leaf = root / "a" / "b" / "c"; leaf.mkdir(parents=True); (root / ".env").write_text("A=1")
        previous = Path.cwd(); os.chdir(leaf)
        try: result = dotenv.find_dotenv(usecwd=True)
        finally: os.chdir(previous)
        return Path(result).relative_to(root).as_posix()


def find_missing() -> object:
    with tempfile.TemporaryDirectory() as raw:
        previous = Path.cwd(); os.chdir(raw)
        try: return dotenv.find_dotenv(filename="absent.env", usecwd=True)
        finally: os.chdir(previous)


def find_raise() -> object:
    with tempfile.TemporaryDirectory() as raw:
        previous = Path.cwd(); os.chdir(raw)
        try:
            try: dotenv.find_dotenv(filename="absent.env", usecwd=True, raise_error_if_not_found=True)
            except Exception as exc: return type(exc).__name__
            return None
        finally: os.chdir(previous)


def load_no_override() -> object:
    clean_env(["A", "B"]); os.environ["A"] = "outside"
    result = dotenv.load_dotenv(stream=io.StringIO("A=file\nB=${A}\n"), override=False)
    return [result, os.environ.get("A"), os.environ.get("B")]


def load_override() -> object:
    clean_env(["A", "B"]); os.environ["A"] = "outside"
    result = dotenv.load_dotenv(stream=io.StringIO("A=file\nB=${A}\n"), override=True)
    return [result, os.environ.get("A"), os.environ.get("B")]


def load_stream_none_value() -> object:
    clean_env(["UNICODE", "NOVALUE"])
    result = dotenv.load_dotenv(stream=io.StringIO("UNICODE=雪\nNOVALUE\n"), override=True)
    return [result, os.environ.get("UNICODE"), "NOVALUE" in os.environ]


def load_empty_missing() -> object:
    return [dotenv.load_dotenv(stream=io.StringIO("")), dotenv.load_dotenv("/tmp/definitely-missing-dotenv")]


def load_no_interpolate() -> object:
    clean_env(["A", "B"])
    result = dotenv.load_dotenv(stream=io.StringIO("A=one\nB=${A}\n"), override=True, interpolate=False)
    return [result, os.environ.get("B")]


def set_create_always() -> object:
    with tempfile.TemporaryDirectory() as raw:
        path = Path(raw) / ".env"; result = dotenv.set_key(path, "A", "hello world")
        return [list(result), path.read_text()]


def set_replace_preserve() -> object:
    with tempfile.TemporaryDirectory() as raw:
        path = Path(raw) / ".env"; path.write_text("# head\nA=old\nB=keep")
        result = dotenv.set_key(path, "A", "new")
        return [list(result), path.read_text()]


def set_quote_modes() -> object:
    outputs = []
    with tempfile.TemporaryDirectory() as raw:
        for mode, value in [("never", "a b"), ("auto", "abc123"), ("auto", "a b")]:
            path = Path(raw) / mode.replace("auto", f"auto{len(outputs)}")
            dotenv.set_key(path, "K", value, quote_mode=mode); outputs.append(path.read_text())
    return outputs


def set_export_escape() -> object:
    with tempfile.TemporaryDirectory() as raw:
        path = Path(raw) / ".env"; result = dotenv.set_key(path, "K", "it's", export=True)
        return [list(result), path.read_text()]


def set_invalid_mode() -> object:
    with tempfile.TemporaryDirectory() as raw:
        try: dotenv.set_key(Path(raw) / ".env", "K", "V", quote_mode="sometimes")
        except Exception as exc: return [type(exc).__name__, str(exc)]
        return None


def set_encoding() -> object:
    with tempfile.TemporaryDirectory() as raw:
        path = Path(raw) / ".env"; result = dotenv.set_key(path, "é", "è", encoding="latin-1")
        return [list(result), path.read_bytes().hex()]


def unset_existing() -> object:
    with tempfile.TemporaryDirectory() as raw:
        path = Path(raw) / ".env"; path.write_text("A=one\nB=two\nA=three\n")
        result = dotenv.unset_key(path, "A"); return [list(result), path.read_text()]


def unset_missing_key() -> object:
    with tempfile.TemporaryDirectory() as raw:
        path = Path(raw) / ".env"; path.write_text("A=one\n")
        result = dotenv.unset_key(path, "B"); return [list(result), path.read_text()]


def unset_missing_file() -> object:
    with tempfile.TemporaryDirectory() as raw: return list(dotenv.unset_key(Path(raw) / ".env", "A"))


def cli_version() -> object:
    with tempfile.TemporaryDirectory() as raw: return cli(["--version"], Path(raw))


def cli_list_formats() -> object:
    with tempfile.TemporaryDirectory() as raw:
        root = Path(raw); path = root / ".env"; path.write_text("B='a b'\nA=one\nNOVALUE\n")
        return [cli(["--file", str(path), "list", "--format", mode], root) for mode in ["simple", "json", "shell", "export"]]


def cli_get() -> object:
    with tempfile.TemporaryDirectory() as raw:
        root = Path(raw); path = root / ".env"; path.write_text("A=one\nEMPTY=\n")
        return [cli(["-f", str(path), "get", key], root) for key in ["A", "EMPTY", "MISSING"]]


def cli_set() -> object:
    with tempfile.TemporaryDirectory() as raw:
        root = Path(raw); path = root / ".env"
        first = cli(["-f", str(path), "-q", "auto", "set", "A", "a b"], root)
        second = cli(["-f", str(path), "-e", "true", "set", "B", "two"], root)
        return [first, second, path.read_text()]


def cli_unset() -> object:
    with tempfile.TemporaryDirectory() as raw:
        root = Path(raw); path = root / ".env"; path.write_text("A=one\nB=two\n")
        first = cli(["-f", str(path), "unset", "A"], root); second = cli(["-f", str(path), "unset", "A"], root)
        return [first, second, path.read_text()]


def cli_run_override() -> object:
    with tempfile.TemporaryDirectory() as raw:
        root = Path(raw); path = root / ".env"; path.write_text("A=file\nNOVALUE\n")
        command = [sys.executable, "-c", "import os; print(os.environ.get('A')); print('NOVALUE' in os.environ)"]
        return [cli(["-f", str(path), "run", *command], root, {"A": "outside"}), cli(["-f", str(path), "run", "--no-override", *command], root, {"A": "outside"})]


def cli_errors() -> object:
    with tempfile.TemporaryDirectory() as raw:
        root = Path(raw); path = root / ".env"; path.write_text("A=one\n")
        return [cli(["-f", str(root / "missing"), "list"], root), cli(["-f", str(path), "run"], root)]


OPERATIONS = {name: value for name, value in globals().copy().items() if callable(value) and name in {
    "package_surface", "parse_basics", "parse_quotes", "parse_invalid", "parse_no_interpolate",
    "interpolate_environment", "interpolate_file_order", "interpolation_bare_and_default", "get_key_values",
    "find_parent", "find_missing", "find_raise", "load_no_override", "load_override", "load_stream_none_value",
    "load_empty_missing", "load_no_interpolate", "set_create_always", "set_replace_preserve", "set_quote_modes",
    "set_export_escape", "set_invalid_mode", "set_encoding", "unset_existing", "unset_missing_key",
    "unset_missing_file", "cli_version", "cli_list_formats", "cli_get", "cli_set", "cli_unset",
    "cli_run_override", "cli_errors",
}}


for line in sys.stdin:
    request = json.loads(line); name = request.get("operation")
    try:
        result = OPERATIONS[name]()
        response = {"id": request.get("id"), "ok": True, "result": result}
    except BaseException as exc:
        response = {"id": request.get("id"), "ok": False, "error": {"type": type(exc).__name__, "message": str(exc)}}
    print(json.dumps(response, ensure_ascii=False, sort_keys=True), flush=True)
