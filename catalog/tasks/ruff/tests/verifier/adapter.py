from __future__ import annotations

import importlib.metadata
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile


SITE = Path(os.environ.get("NL2REPO_RUFF_CANDIDATE_SITE", "/tmp/candidate-site"))
MAX_OUTPUT = 1024 * 1024
ENTRY_CODE = r'''
import importlib.metadata
import json
import sys

site = sys.argv[1]
arguments = json.loads(sys.argv[2])
sys.path.append(site)
matches = [
    entry
    for distribution in importlib.metadata.distributions(path=[site])
    for entry in distribution.entry_points
    if entry.group == "console_scripts" and entry.name == "ruff"
]
if len(matches) != 1:
    raise RuntimeError(f"expected one ruff console script, found {len(matches)}")
sys.argv = ["ruff", *arguments]
result = matches[0].load()()
raise SystemExit(result if isinstance(result, int) else 0)
'''


def run_console(arguments: list[str], directory: Path, stdin: str = "") -> tuple[int, str, str]:
    try:
        completed = subprocess.run(
            [sys.executable, "-I", "-c", ENTRY_CODE, str(SITE), json.dumps(arguments)],
            cwd=directory,
            input=stdin,
            text=True,
            capture_output=True,
            timeout=5,
            check=False,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        return 70, "", f"{type(exc).__name__}: {exc}"
    stdout = completed.stdout[:MAX_OUTPUT]
    stderr = completed.stderr[:MAX_OUTPUT]
    if len(completed.stdout) > MAX_OUTPUT or len(completed.stderr) > MAX_OUTPUT:
        return 70, stdout, "candidate output exceeded limit"
    return completed.returncode, stdout, stderr


def distribution_contract() -> bool:
    try:
        distributions = list(importlib.metadata.distributions(path=[str(SITE)]))
        selected = [
            distribution
            for distribution in distributions
            if distribution.metadata["Name"].casefold().replace("_", "-") == "ruff"
        ]
        if len(selected) != 1 or selected[0].version != "0.16.4":
            return False
        entries = [
            entry
            for entry in selected[0].entry_points
            if entry.group == "console_scripts" and entry.name == "ruff"
        ]
        return len(entries) == 1
    except Exception:
        return False


def case(case_id: str) -> bool:
    if case_id == "package-metadata":
        return distribution_contract()

    with tempfile.TemporaryDirectory(prefix="ruff-contract-") as temporary:
        root = Path(temporary)
        # The candidate runs under a dedicated unprivileged UID. It needs to
        # traverse this disposable fixture directory but cannot write trusted
        # verifier files or the candidate installation target.
        root.chmod(0o755)
        source = root / "sample.py"
        source.write_text("import os\n", encoding="utf-8")

        if case_id == "version":
            code, stdout, _ = run_console(["--version"], root)
            return code == 0 and stdout == "ruff 0.16.4\n"
        if case_id == "help-check":
            code, stdout, _ = run_console(["help", "check"], root)
            return code == 0 and "Run Ruff" in stdout and "--fix" in stdout
        if case_id == "check-clean":
            source.write_text("answer = 42\nprint(answer)\n", encoding="utf-8")
            code, stdout, _ = run_console(["check", "--isolated", "--no-cache", "sample.py"], root)
            return code == 0 and "F401" not in stdout
        if case_id == "check-f401":
            code, stdout, _ = run_console(["check", "--isolated", "--no-cache", "sample.py"], root)
            return code == 1 and "F401" in stdout and "sample.py" in stdout
        if case_id == "check-json":
            code, stdout, _ = run_console(
                ["check", "--isolated", "--no-cache", "--output-format", "json", "sample.py"], root
            )
            try:
                diagnostics = json.loads(stdout)
            except json.JSONDecodeError:
                return False
            return (
                code == 1
                and isinstance(diagnostics, list)
                and len(diagnostics) == 1
                and diagnostics[0].get("code") == "F401"
                and diagnostics[0].get("filename", "").endswith("sample.py")
                and diagnostics[0].get("location", {}).get("row") == 1
                and diagnostics[0].get("location", {}).get("column") == 8
            )
        if case_id == "check-stdin":
            code, stdout, _ = run_console(
                ["check", "--isolated", "--no-cache", "--stdin-filename", "stdin_name.py", "-"],
                root,
                "import os\n",
            )
            return code == 1 and "F401" in stdout and "stdin_name.py" in stdout
        if case_id == "check-noqa":
            source.write_text("import os  # noqa: F401\n", encoding="utf-8")
            code, stdout, _ = run_console(["check", "--isolated", "--no-cache", "sample.py"], root)
            return code == 0 and "F401" not in stdout
        if case_id == "check-ignore-config":
            (root / "pyproject.toml").write_text(
                "[tool.ruff.lint]\nignore = [\"F401\"]\n", encoding="utf-8"
            )
            code, stdout, _ = run_console(["check", "--no-cache", "sample.py"], root)
            return code == 0 and "F401" not in stdout
        if case_id == "check-isolated-config":
            (root / "pyproject.toml").write_text(
                "[tool.ruff.lint]\nignore = [\"F401\"]\n", encoding="utf-8"
            )
            code, stdout, _ = run_console(["check", "--isolated", "--no-cache", "sample.py"], root)
            return code == 1 and "F401" in stdout
        if case_id == "check-e501-config":
            source.write_text("value = 'abcdefghijklmnopqrstuvwxyz'\n", encoding="utf-8")
            (root / "pyproject.toml").write_text(
                "[tool.ruff]\nline-length = 20\n\n[tool.ruff.lint]\nselect = [\"E501\"]\n",
                encoding="utf-8",
            )
            code, stdout, _ = run_console(["check", "--no-cache", "sample.py"], root)
            return code == 1 and "E501" in stdout
        if case_id == "check-missing-config":
            code, _, stderr = run_console(["check", "--config", "missing.toml", "sample.py"], root)
            return code == 2 and "missing.toml" in stderr
        if case_id == "fix-f401":
            code, _, _ = run_console(["check", "--isolated", "--no-cache", "--fix", "sample.py"], root)
            return code == 0 and source.read_text(encoding="utf-8") == ""
        if case_id == "no-fix":
            code, stdout, _ = run_console(
                ["check", "--isolated", "--no-cache", "--fix", "--no-fix", "sample.py"], root
            )
            return code == 1 and "F401" in stdout and source.read_text(encoding="utf-8") == "import os\n"
        if case_id == "format-stdin":
            code, stdout, _ = run_console(
                ["format", "--isolated", "--stdin-filename", "stdin.py", "-"], root, "x=1\n"
            )
            return code == 0 and stdout == "x = 1\n"
        if case_id == "format-check":
            source.write_text("x=1\n", encoding="utf-8")
            code, stdout, _ = run_console(["format", "--isolated", "--check", "sample.py"], root)
            return code == 1 and "sample.py" in stdout and source.read_text(encoding="utf-8") == "x=1\n"
        if case_id == "format-write":
            source.write_text("x=1\n", encoding="utf-8")
            code, _, _ = run_console(["format", "--isolated", "sample.py"], root)
            return code == 0 and source.read_text(encoding="utf-8") == "x = 1\n"
        if case_id == "format-diff":
            source.write_text("x=1\n", encoding="utf-8")
            code, stdout, _ = run_console(["format", "--isolated", "--diff", "sample.py"], root)
            return code == 1 and "-x=1" in stdout and "+x = 1" in stdout
        if case_id == "format-function":
            source.write_text("def f(a, b,):\n    return 'ok'\n", encoding="utf-8")
            code, _, _ = run_console(["format", "--isolated", "sample.py"], root)
            formatted = source.read_text(encoding="utf-8")
            return code == 0 and "def f(\n" in formatted and 'return "ok"' in formatted
        if case_id == "rule-f401":
            code, stdout, _ = run_console(["rule", "F401"], root)
            return code == 0 and "F401" in stdout and "unused" in stdout.casefold()
    return False


def main() -> None:
    request = json.loads(sys.stdin.read())
    case_id = request.get("id")
    result = isinstance(case_id, str) and case(case_id)
    print(json.dumps({"id": case_id, "ok": result}, sort_keys=True))


if __name__ == "__main__":
    main()
