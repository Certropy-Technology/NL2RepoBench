from __future__ import annotations

import json
import textwrap

from nl2repobench.verification.candidate_client import execute_script


LEAVES: list[dict[str, str]] = []


def record(leaf_id: str, passed: bool, detail: str = "") -> None:
    item = {"id": leaf_id, "status": "passed" if passed else "failed"}
    if detail and not passed:
        item["message"] = detail[:500]
    LEAVES.append(item)


def scenario(leaf_id: str, source: str, expected: object) -> None:
    source = (
        "import contextlib, io, sys\n"
        "sys.path.insert(0, '/tmp/candidate-site')\n"
        "with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):\n"
        + textwrap.indent(source, "    ")
    )
    result = execute_script(source, timeout_sec=8.0)
    actual = result.value if result.ok else {
        "exception_type": result.exception_type,
        "exception_message": result.exception_message,
    }
    record(leaf_id, actual == expected, json.dumps({"actual": actual, "expected": expected}, sort_keys=True))


def main() -> int:
    scenario("metadata/version", "import pytest\nresult = pytest.__version__", "9.2.0.dev277")
    scenario("metadata/exports", "import pytest\nresult = {\"count\": len(pytest.__all__), \"approx\": 'approx' in pytest.__all__, \"fixture\": 'fixture' in pytest.__all__}", {"count": 89, "approx": True, "fixture": True})
    scenario("metadata/distribution", "import importlib.metadata as metadata\nvalue = metadata.metadata('pytest')\nresult = {\"name\": value['Name'], \"requires_python\": value['Requires-Python']}", {"name": "pytest", "requires_python": ">=3.10"})

    scenario("approx/scalar", "import pytest\nresult = {\"equal\": pytest.approx(1.0) == 1.001, \"not_equal\": pytest.approx(1.0) == 1.1, \"repr\": repr(pytest.approx(1.0, abs=0.01))}", {"equal": False, "not_equal": False, "repr": "1.0 ± 0.01"})
    scenario("approx/sequence", "import pytest\nvalue = pytest.approx([1.0, 2.0], abs=0.01)\nresult = {\"equal\": value == [1.001, 1.999], \"len\": len(value.expected), \"expected\": value.expected}", {"equal": True, "len": 2, "expected": [1.0, 2.0]})
    scenario("approx/mapping", "import pytest\nvalue = pytest.approx({\"a\": 1.0, \"b\": 2.0})\nresult = {\"equal\": value == {\"a\": 1.001, \"b\": 1.999}, \"keys\": sorted(value.expected)}", {"equal": False, "keys": ["a", "b"]})
    scenario("approx/nan", "import math, pytest\nvalue = pytest.approx(float(\"nan\"), nan_ok=True)\nresult = value == float(\"nan\") and math.isnan(value.expected)", True)
    scenario("raises/context", "import pytest\nwith pytest.raises(ValueError, match=\"bad\") as info:\n    raise ValueError(\"bad input\")\nresult = {\"type\": type(info.value).__name__, \"args\": info.value.args, \"match\": str(info.value)}", {"type": "ValueError", "args": ["bad input"], "match": "bad input"})
    scenario("raises/callable", "import pytest\ndef fail():\n    raise KeyError(\"key\")\ninfo = pytest.raises(KeyError, fail)\nresult = {\"type\": type(info.value).__name__, \"message\": str(info.value)}", {"type": "KeyError", "message": "'key'"})
    scenario("warns/context", "import warnings, pytest\nwith pytest.warns(UserWarning, match=\"hello\") as caught:\n    warnings.warn(\"hello world\", UserWarning)\nresult = {\"count\": len(caught), \"category\": caught[0].category.__name__, \"message\": str(caught[0].message)}", {"count": 1, "category": "UserWarning", "message": "hello world"})
    scenario("marks/decorator", "import pytest\nmark = pytest.mark.slow\nresult = {\"name\": mark.mark.name, \"args\": mark.mark.args, \"repr\": str(mark)}", {"name": "slow", "args": [], "repr": "MarkDecorator(mark=Mark(name='slow', args=(), kwargs={}))"})
    scenario("marks/parametrize", "import pytest\nmark = pytest.mark.parametrize(\"x\", [1, 2], ids=[\"one\", \"two\"])\nresult = {\"name\": mark.mark.name, \"args\": [mark.mark.args[0], list(mark.mark.args[1])], \"ids\": mark.mark.kwargs[\"ids\"]}", {"name": "parametrize", "args": ["x", [1, 2]], "ids": ["one", "two"]})
    scenario("param/fields", "import pytest\np = pytest.param(3, 4, id=\"sum\", marks=pytest.mark.slow)\nresult = {\"values\": list(p.values), \"id\": p.id, \"mark\": p.marks[0].mark.name}", {"values": [3, 4], "id": "sum", "mark": "slow"})
    scenario("fixture/decorator", "import pytest\n@pytest.fixture(scope=\"module\", autouse=True, params=[1, 2], ids=[\"a\", \"b\"])\ndef value():\n    return 7\ninfo = value._fixture_function_marker\nresult = {\"scope\": info.scope, \"autouse\": info.autouse, \"params\": list(info.params), \"ids\": list(info.ids)}", {"scope": "module", "autouse": True, "params": [1, 2], "ids": ["a", "b"]})
    scenario("fixture/usefixtures", "import pytest\nmark = pytest.mark.usefixtures(\"db\", \"tmp\")\nresult = {\"name\": mark.mark.name, \"args\": list(mark.mark.args)}", {"name": "usefixtures", "args": ["db", "tmp"]})
    scenario("outcomes/skip", "import pytest\ntry:\n    pytest.skip(\"later\")\nexcept pytest.skip.Exception as exc:\n    result = {\"type\": type(exc).__name__, \"message\": str(exc)}", {"type": "Skipped", "message": "later"})
    scenario("outcomes/xfail", "import pytest\ntry:\n    pytest.xfail(\"known\")\nexcept pytest.xfail.Exception as exc:\n    result = {\"type\": type(exc).__name__, \"message\": str(exc)}", {"type": "XFailed", "message": "known"})
    scenario("outcomes/fail", "import pytest\ntry:\n    pytest.fail(\"broken\")\nexcept pytest.fail.Exception as exc:\n    result = {\"type\": type(exc).__name__, \"message\": str(exc)}", {"type": "Failed", "message": "broken"})
    scenario("main/pass", "import pathlib, tempfile, pytest\nwith tempfile.TemporaryDirectory() as d:\n    p = pathlib.Path(d) / \"test_ok.py\"\n    p.write_text(\"def test_ok(): assert 2 + 2 == 4\\n\")\n    result = int(pytest.main([\"-q\", \"--disable-warnings\", str(p)]))", 0)
    scenario("main/fail", "import pathlib, tempfile, pytest\nwith tempfile.TemporaryDirectory() as d:\n    p = pathlib.Path(d) / \"test_bad.py\"\n    p.write_text(\"def test_bad(): assert False\\n\")\n    result = int(pytest.main([\"-q\", \"--disable-warnings\", str(p)]))", 1)
    scenario("main/no-tests", "import pathlib, tempfile, pytest\nwith tempfile.TemporaryDirectory() as d:\n    p = pathlib.Path(d) / \"empty.py\"\n    p.write_text(\"x = 1\\n\")\n    result = int(pytest.main([\"-q\", \"--disable-warnings\", str(p)]))", 5)
    scenario("main/fixture-param", "import pathlib, tempfile, pytest\nwith tempfile.TemporaryDirectory() as d:\n    p = pathlib.Path(d) / \"test_param.py\"\n    p.write_text(\"import pytest\\n@pytest.fixture\\ndef base(): return 2\\n@pytest.mark.parametrize('x', [3, 4])\\ndef test_sum(base, x): assert base + x > 4\\n\")\n    result = int(pytest.main([\"-q\", \"--disable-warnings\", str(p)]))", 0)
    scenario("monkeypatch/env", "import os, pytest\nmonkey = pytest.MonkeyPatch()\nmonkey.setenv(\"NL2REPO_TEST\", \"yes\")\na = os.environ.get(\"NL2REPO_TEST\")\nmonkey.delenv(\"NL2REPO_TEST\")\nb = os.environ.get(\"NL2REPO_TEST\")\nmonkey.undo()\nresult = [a, b, os.environ.get(\"NL2REPO_TEST\")]", ["yes", None, None])
    scenario("importorskip/missing", "import pytest\ntry:\n    pytest.importorskip(\"module_that_does_not_exist_nl2repo\")\nexcept pytest.skip.Exception as exc:\n    result = type(exc).__name__.startswith(\"Skipped\")", True)
    scenario("deprecated-call", "import pytest, warnings\nwith pytest.deprecated_call():\n    warnings.warn(\"old\", DeprecationWarning)\nresult = True", True)
    scenario("stash/key", "import pytest\nkey = pytest.StashKey[int]()\nresult = {\"module\": key.__class__.__module__, \"name\": key.__class__.__name__, \"distinct\": key != pytest.StashKey[int]()} ", {"module": "_pytest.stash", "name": "StashKey", "distinct": True})
    scenario("exit-codes", "import pytest\nresult = {name: int(value) for name, value in ((item.name, item) for item in pytest.ExitCode)}", {"OK": 0, "TESTS_FAILED": 1, "INTERRUPTED": 2, "INTERNAL_ERROR": 3, "USAGE_ERROR": 4, "NO_TESTS_COLLECTED": 5, "MAX_WARNINGS_ERROR": 6})

    scenario("console/version", "import importlib.metadata as metadata, sys\nentry = next(item for item in metadata.entry_points(group='console_scripts') if item.name == 'pytest')\nsys.argv = ['pytest', '--version']\nresult = entry.load()()", 0)
    print(json.dumps({"schema_version": "1.0", "leaves": LEAVES}, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
