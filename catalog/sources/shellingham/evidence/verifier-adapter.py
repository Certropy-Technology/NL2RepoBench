from __future__ import annotations

import argparse
import errno
import importlib
import io
import json
import os
import sys
from pathlib import Path
from unittest.mock import patch


def type_name(exc: BaseException) -> str:
    return type(exc).__module__ + "." + type(exc).__name__


def exercise(scenario: str):
    import shellingham
    from shellingham import posix
    from shellingham.posix._core import Process
    from shellingham.posix import proc, ps

    if scenario == "metadata":
        return {"version": shellingham.__version__, "failure_base": type(shellingham.ShellDetectionFailure()).__module__ + "." + type(shellingham.ShellDetectionFailure()).__bases__[0].__name__}
    if scenario == "exports":
        return sorted(name for name in ("ShellDetectionFailure", "detect_shell") if hasattr(shellingham, name))
    if scenario == "exception-identity":
        return shellingham.ShellDetectionFailure is shellingham._core.ShellDetectionFailure
    if scenario == "shell-names":
        return {key: list(posix._get_shell(key)) for key in ("bash", "ZSH", "fish")}
    if scenario == "login-env":
        with patch.dict(os.environ, {"SHELL": "/custom/login-shell"}, clear=False):
            return list(posix._get_shell("-bash"))
    if scenario == "login-fallback":
        with patch.dict(os.environ, {"SHELL": ""}, clear=False):
            return list(posix._get_shell("-/bin/bash"))
    if scenario == "qemu-forwarding":
        return list(posix._get_shell("qemu-x86_64", "/usr/bin/bash"))
    if scenario == "xonsh-script":
        script = Path("/tmp/candidate-site/xonsh")
        script.write_text("#!python\n", encoding="utf-8")
        return list(posix._get_shell("python", str(script)))
    if scenario == "parent-order":
        records = [Process(("worker",), "7", "8"), Process(("/usr/bin/zsh",), "8", "9")]
        with patch.object(posix, "_iter_process_parents", return_value=records):
            return list(posix.get_shell("7", max_depth=10))
    if scenario == "depth-bound":
        records = [Process(("worker",), "7", "8"), Process(("bash",), "8", "9")]
        with patch.object(posix, "_iter_process_parents", side_effect=lambda pid, depth: iter(records[:depth])):
            return {"one": posix.get_shell("7", max_depth=1), "two": list(posix.get_shell("7", max_depth=2) or ())}
    if scenario == "no-shell":
        with patch.object(posix, "_iter_process_parents", return_value=[Process(("worker",), "7", "9")]):
            return posix.get_shell("7")
    if scenario == "dispatch-success":
        with patch.object(shellingham.importlib, "import_module", return_value=posix):
            with patch.object(posix, "get_shell", return_value=("bash", "bash")):
                return list(shellingham.detect_shell("7"))
    if scenario == "proc-stat":
        with patch.object(proc.os.path, "exists", side_effect=lambda path: path.endswith("/stat")):
            return proc.detect_proc()
    if scenario == "proc-status":
        with patch.object(proc.os.path, "exists", side_effect=lambda path: path.endswith("/status")):
            return proc.detect_proc()
    if scenario == "proc-invalid":
        with patch.object(proc.os.path, "exists", return_value=False):
            try:
                proc.detect_proc()
            except Exception as exc:
                return type_name(exc)
    if scenario == "proc-parents":
        values = {"7": "8", "8": "9"}
        with patch.object(proc, "detect_proc", return_value="stat"), patch.object(proc, "_get_ppid", side_effect=lambda pid, name: values[pid]), patch.object(proc, "_get_cmdline", side_effect=lambda pid: [("prog",), ("bash",)][int(pid) - 7]):
            return [list(item.args) for item in proc.iter_process_parents("7", max_depth=2)]
    if scenario == "proc-cmdline":
        with patch.object(proc.io, "open", return_value=io.StringIO("python\0-m\0demo\0")):
            return list(proc._get_cmdline("7"))
    if scenario == "proc-string-pid":
        with patch.object(proc, "detect_proc", return_value="stat"), patch.object(proc, "_get_ppid", return_value="8"), patch.object(proc, "_get_cmdline", return_value=("bash",)):
            item = next(proc.iter_process_parents("7", max_depth=1))
            return [item.pid, item.ppid]
    if scenario == "ps-bytes":
        output = b"7 8 python -m demo\n8 9 bash\n"
        with patch.object(ps.subprocess, "check_output", return_value=output):
            return [list(item.args) for item in ps.iter_process_parents("7", max_depth=2)]
    if scenario == "ps-malformed":
        output = "7 8 python\nbad line\n8 missing\n"
        with patch.object(ps.subprocess, "check_output", return_value=output):
            return [list(item.args) for item in ps.iter_process_parents("7", max_depth=2)]
    if scenario == "ps-depth":
        output = "7 8 python\n8 9 bash\n"
        with patch.object(ps.subprocess, "check_output", return_value=output):
            return [list(item.args) for item in ps.iter_process_parents("7", max_depth=1)]
    if scenario == "ps-empty":
        with patch.object(ps.subprocess, "check_output", side_effect=__import__("subprocess").CalledProcessError(1, "ps", output=b"")):
            return list(ps.iter_process_parents("7", max_depth=2))
    if scenario == "ps-missing":
        error = OSError(errno.ENOENT, "missing")
        with patch.object(ps.subprocess, "check_output", side_effect=error):
            try:
                list(ps.iter_process_parents("7", max_depth=2))
            except Exception as exc:
                return type_name(exc)
    if scenario == "dispatch-fallback":
        records = [Process(("worker",), "7", "8"), Process(("bash",), "8", "9")]
        with patch.object(posix.proc, "iter_process_parents", side_effect=OSError("no proc")), patch.object(posix.ps, "iter_process_parents", return_value=records):
            return list(posix.get_shell("7", max_depth=2))
    raise ValueError(f"unknown scenario: {scenario}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate-site", required=True)
    parser.add_argument("--scenario", required=True)
    args = parser.parse_args()
    if os.path.realpath(args.candidate_site) != "/tmp/candidate-site":
        raise ValueError("candidate site is unavailable")
    sys.path.insert(0, args.candidate_site)
    try:
        value = exercise(args.scenario)
    except BaseException as exc:
        print(json.dumps({"ok": False, "exception_type": type_name(exc), "exception_message": str(exc)}, sort_keys=True))
    else:
        print(json.dumps({"ok": True, "value": value}, sort_keys=True))


if __name__ == "__main__":
    main()
