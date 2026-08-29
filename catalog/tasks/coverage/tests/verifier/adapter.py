"""Child-side JSON adapter for the deterministic coverage.py contract."""

from __future__ import annotations

import argparse
import json
import io
import os
import pathlib
import runpy
import subprocess
import sys
import tempfile
from typing import Any


def _type_name(exc: BaseException) -> str:
    return f"{type(exc).__module__}.{type(exc).__qualname__}"


def _write_module(root: pathlib.Path, name: str, source: str) -> pathlib.Path:
    path = root / name
    path.write_text(source, encoding="utf-8")
    return path


def _basic_measurement() -> dict[str, Any]:
    from coverage import Coverage

    with tempfile.TemporaryDirectory() as raw:
        root = pathlib.Path(raw)
        module = _write_module(root, "sample.py", "VALUE = 2\n\nif VALUE:\n    RESULT = VALUE + 3\n")
        data_file = root / ".coverage"
        cov = Coverage(data_file=str(data_file), source=[str(root)], config_file=False)
        cov.start()
        runpy.run_path(str(module), run_name="sample")
        cov.stop()
        cov.save()
        data = cov.get_data()
        return {
            "measured": [pathlib.Path(name).name for name in data.measured_files()],
            "lines": data.lines(str(module)),
            "has_arcs": data.has_arcs(),
            "data_exists": data_file.exists(),
            "report": cov.report(file=io.StringIO(), ignore_errors=False),
        }


def _branch_measurement() -> dict[str, Any]:
    from coverage import Coverage

    with tempfile.TemporaryDirectory() as raw:
        root = pathlib.Path(raw)
        module = _write_module(
            root,
            "branchy.py",
            "def choose(value):\n    if value:\n        return 'yes'\n    return 'no'\n\nchoose(True)\n",
        )
        cov = Coverage(data_file=str(root / ".coverage"), source=[str(root)], branch=True, config_file=False)
        cov.start()
        runpy.run_path(str(module), run_name="branchy")
        cov.stop()
        cov.save()
        arcs = cov.get_data().arcs(str(module))
        return {"has_arcs": cov.get_data().has_arcs(), "arc_count": len(arcs or []), "missing": cov.analysis(str(module))[3]}


def _data_roundtrip() -> dict[str, Any]:
    from coverage import CoverageData

    with tempfile.TemporaryDirectory() as raw:
        path = pathlib.Path(raw) / ".coverage"
        data = CoverageData(str(path))
        data.add_lines({"pkg/mod.py": {1, 3, 5}})
        data.set_context("unit")
        data.add_lines({"pkg/mod.py": {7}})
        data.write()
        loaded = CoverageData(str(path))
        loaded.read()
        return {
            "files": sorted(pathlib.PurePath(name).as_posix() for name in loaded.measured_files()),
            "lines": sorted(loaded.lines("pkg/mod.py") or []),
            "contexts": sorted(loaded.measured_contexts()),
            "has_arcs": loaded.has_arcs(),
        }


def _data_arcs() -> dict[str, Any]:
    from coverage import CoverageData

    data = CoverageData(no_disk=True)
    data.set_context("branch")
    data.add_arcs({"pkg/mod.py": [(1, 2), (2, -1)]})
    data.set_query_context("branch")
    return {
        "has_arcs": data.has_arcs(),
        "arcs": [list(arc) for arc in (data.arcs("pkg/mod.py") or [])],
        "contexts": sorted(data.measured_contexts()),
        "files": sorted(data.measured_files()),
    }


def _contexts() -> dict[str, Any]:
    from coverage import Coverage

    with tempfile.TemporaryDirectory() as raw:
        root = pathlib.Path(raw)
        module = _write_module(root, "contexts.py", "VALUE = 1\n")
        cov = Coverage(data_file=str(root / ".coverage"), source=[str(root)], config_file=False)
        cov.start()
        cov.switch_context("alpha")
        runpy.run_path(str(module), run_name="contexts")
        cov.switch_context("beta")
        cov.stop()
        cov.save()
        return {
            "contexts": sorted(cov.get_data().measured_contexts()),
            "lines_alpha": sorted(cov.get_data().lines(str(module)) or []),
            "context_by_line": {
                str(line): sorted(contexts)
                for line, contexts in cov.get_data().contexts_by_lineno(str(module)).items()
            },
        }


def _reports() -> dict[str, Any]:
    from coverage import Coverage

    with tempfile.TemporaryDirectory() as raw:
        root = pathlib.Path(raw)
        module = _write_module(root, "reportme.py", "def f():\n    return 4\n\nf()\n")
        cov = Coverage(data_file=str(root / ".coverage"), source=[str(root)], config_file=False)
        cov.start()
        runpy.run_path(str(module), run_name="reportme")
        cov.stop()
        cov.save()
        json_path = root / "coverage.json"
        xml_path = root / "coverage.xml"
        lcov_path = root / "coverage.lcov"
        html_dir = root / "html"
        annotated = root / "reportme.py,cover"
        json_status = cov.json_report(outfile=str(json_path))
        xml_status = cov.xml_report(outfile=str(xml_path))
        lcov_status = cov.lcov_report(outfile=str(lcov_path))
        cov.html_report(directory=str(html_dir))
        cov.annotate(directory=str(root))
        document = json.loads(json_path.read_text(encoding="utf-8"))
        return {
            "json_status": json_status,
            "xml_status": xml_status,
            "lcov_status": lcov_status,
            "json_version": document["meta"]["version"],
            "json_files": sorted(pathlib.PurePath(name).name for name in document["files"]),
            "xml_prefix": xml_path.read_text(encoding="utf-8")[:5],
            "lcov_prefix": lcov_path.read_text(encoding="utf-8").splitlines()[0][:3],
            "html_index": (html_dir / "index.html").exists(),
            "annotated": any(root.glob("**/*.py,cover")),
        }


def _lifecycle() -> dict[str, Any]:
    from coverage import Coverage

    cov = Coverage(data_file=None, config_file=False)
    before = Coverage.current()
    with cov.collect():
        during = Coverage.current() is cov
    after = Coverage.current()
    return {"before": before is None, "during": during, "after": after is None, "running": cov._started}


def _configuration() -> dict[str, Any]:
    from coverage import Coverage

    cov = Coverage(data_file=None, branch=True, timid=True, config_file=False)
    return {"branch": cov.config.branch, "timid": cov.config.timid, "data_file": cov.config.data_file}


def _combine_data() -> dict[str, Any]:
    from coverage import Coverage, CoverageData

    with tempfile.TemporaryDirectory() as raw:
        root = pathlib.Path(raw)
        base = root / ".coverage"
        first = CoverageData(str(base) + ".one")
        first.add_lines({"a.py": {1, 2}})
        first.write()
        second = CoverageData(str(base) + ".two")
        second.add_lines({"a.py": {3}})
        second.write()
        cov = Coverage(data_file=str(base), config_file=False)
        cov.combine(data_paths=[str(root)])
        return {"lines": sorted(cov.get_data().lines("a.py") or []), "parallel_left": sorted(p.name for p in root.glob(".coverage.*"))}


def _cli() -> dict[str, Any]:
    with tempfile.TemporaryDirectory() as raw:
        root = pathlib.Path(raw)
        script = _write_module(root, "cli_target.py", "print('hello-cli')\n")
        env = dict(os.environ)
        env["PYTHONPATH"] = "/tmp/candidate-site"
        result = subprocess.run(
            [sys.executable, "-m", "coverage", "run", "--data-file", str(root / ".coverage"), str(script)],
            cwd=root,
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )
        report = subprocess.run(
            [sys.executable, "-m", "coverage", "report", "--data-file", str(root / ".coverage")],
            cwd=root,
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )
        return {
            "run_exit": result.returncode,
            "run_stdout": result.stdout.strip(),
            "report_exit": report.returncode,
            "report_has_file": "cli_target.py" in report.stdout,
        }


def _errors() -> dict[str, Any]:
    import coverage

    failures: list[list[str]] = []
    for call in (
        lambda: coverage.Coverage(source_dirs=["missing-directory"], config_file=False).start(),
        lambda: coverage.Coverage(data_file=None, config_file=False).report(file=io.StringIO()),
    ):
        try:
            call()
        except Exception as exc:
            failures.append([_type_name(exc), str(exc)])
        else:
            failures.append(["none", ""])
    return {"failures": failures, "exception_is_root": coverage.CoverageException is coverage.exceptions.CoverageException}


def _plugin_protocol() -> dict[str, Any]:
    from coverage import CoveragePlugin, FileReporter, FileTracer

    class Reporter(FileReporter):
        def source(self) -> str:
            return "x = 1\n"

        def relative_filename(self) -> str:
            return "virtual.py"

    class Tracer(FileTracer):
        def file_tracer(self, filename: str) -> str | None:
            return "plugin" if filename.endswith(".tmpl") else None

        def source_filename(self) -> str:
            return "virtual.py"

        def line_number_range(self, frame: Any) -> tuple[int, int]:
            return (1, 1)

    class Plugin(CoveragePlugin):
        def file_tracer(self, filename: str) -> FileTracer | None:
            return Tracer() if filename.endswith(".tmpl") else None

        def file_reporter(self, filename: str) -> FileReporter:
            return Reporter(filename)

    return {"reporter": Reporter("x").relative_filename(), "tracer": Tracer().source_filename(), "plugin": Plugin().file_tracer("a.tmpl") is not None}


SCENARIOS = {
    "basic-measurement": _basic_measurement,
    "branch-measurement": _branch_measurement,
    "data-roundtrip": _data_roundtrip,
    "data-arcs": _data_arcs,
    "contexts": _contexts,
    "reports": _reports,
    "lifecycle": _lifecycle,
    "configuration": _configuration,
    "combine-data": _combine_data,
    "cli": _cli,
    "errors": _errors,
    "plugin-protocol": _plugin_protocol,
}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate-site", required=True)
    parser.add_argument("--request", required=True)
    args = parser.parse_args()
    site = os.path.realpath(args.candidate_site)
    if site != "/tmp/candidate-site" or not os.path.isdir(site):
        raise ValueError("candidate site is unavailable")
    sys.path.insert(0, site)
    request = json.loads(args.request)
    if set(request) != {"schema_version", "scenario"} or request["schema_version"] != "1.0":
        raise ValueError("invalid scenario request")
    scenario = request["scenario"]
    if scenario not in SCENARIOS:
        raise ValueError("scenario is not allowlisted")
    print(json.dumps({"ok": True, "value": SCENARIOS[scenario]()}, sort_keys=True, separators=(",", ":")))


try:
    main()
except BaseException as exc:
    print(json.dumps({"ok": False, "exception_type": _type_name(exc), "exception_message": str(exc)}, sort_keys=True, separators=(",", ":")))
