"""JSON-line adapter used by the separate verifier.

The verifier talks to the candidate only through JSON values. The in-memory
clipboard is a test double; it is never part of the candidate package.
"""
from __future__ import annotations
import contextlib
import io
import json
import runpy
import os
import sys
from pathlib import Path
from unittest import mock

REQUIRED_EXPORTS = [
    "copy", "paste", "set_clipboard", "determine_clipboard", "is_available",
    "lazy_load_stub_copy", "lazy_load_stub_paste", "init_osx_pbcopy_clipboard",
    "init_osx_pyobjc_clipboard", "init_dev_clipboard_clipboard", "init_qt_clipboard",
    "init_xclip_clipboard", "init_xsel_clipboard", "init_wl_clipboard",
    "init_klipper_clipboard", "init_no_clipboard", "init_windows_clipboard",
    "init_wsl_clipboard", "CheckedCall", "PyperclipException",
    "PyperclipWindowsException", "PyperclipTimeoutException", "_executable_exists",
    "ENCODING",
]

def _fresh_import():
    sys.modules.pop("pyperclip", None)
    import pyperclip
    return pyperclip

def _memory_pair():
    state = {"text": ""}
    def copy_memory(value):
        state["text"] = str(value)
    def paste_memory():
        return state["text"]
    return copy_memory, paste_memory

def _invoke(request):
    operation = request["operation"]
    pyperclip = _fresh_import()
    if operation == "exports":
        return {"version": pyperclip.__version__, "all": list(pyperclip.__all__), "missing": [name for name in REQUIRED_EXPORTS if not hasattr(pyperclip, name)]}
    if operation == "lazy":
        before = pyperclip.is_available()
        copy_fn, paste_fn = pyperclip.determine_clipboard()
        after_determine = pyperclip.is_available()
        try:
            copy_fn("probe")
        except Exception as exc:
            error = {"type": type(exc).__name__, "runtime_error": isinstance(exc, RuntimeError)}
        else:
            error = None
        return {"before": before, "after_determine": after_determine, "error": error}
    if operation == "memory":
        pyperclip.determine_clipboard = _memory_pair
        observed = []
        for value in request.get("values", ["text", 42, None, [1, 2]]):
            pyperclip.copy(value)
            observed.append(pyperclip.paste())
        return {"available": pyperclip.is_available(), "values": observed}
    if operation == "no_clipboard":
        pyperclip.set_clipboard("no")
        errors = []
        for fn, args in ((pyperclip.copy, ("text",)), (pyperclip.paste, ())):
            try:
                fn(*args)
            except Exception as exc:
                errors.append({"type": type(exc).__name__, "runtime_error": isinstance(exc, RuntimeError), "has_guidance": "copy/paste mechanism" in str(exc)})
        return {"available": pyperclip.is_available(), "falsey": not pyperclip.copy, "errors": errors}
    if operation == "invalid_selection":
        try:
            pyperclip.set_clipboard("invalid")
        except Exception as exc:
            return {"type": type(exc).__name__, "mentions_choices": "pbcopy" in str(exc) and "windows" in str(exc)}
        return {"type": None, "mentions_choices": False}
    if operation == "xclip_mock":
        calls = []
        class FakeProcess:
            def __init__(self, args, **kwargs):
                calls.append({"args": args, "kwargs": {key: str(value) for key, value in kwargs.items() if key != "stdin"}})
            def communicate(self, input=None):
                calls[-1]["input"] = input.decode("utf-8") if isinstance(input, bytes) else input
                return b"fixture", b""
        with mock.patch.object(pyperclip.subprocess, "Popen", FakeProcess):
            copy_fn, paste_fn = pyperclip.init_xclip_clipboard()
            copy_fn("hé", primary=True)
            result = paste_fn(primary=True)
        return {"result": result, "calls": calls}
    if operation == "wayland_empty_mock":
        calls = []
        def check_call(args, **kwargs):
            calls.append({"args": args, "kwargs": kwargs})
        with mock.patch.object(pyperclip.subprocess, "check_call", check_call):
            copy_fn, _ = pyperclip.init_wl_clipboard()
            copy_fn("", primary=True)
        return {"calls": [{"args": call["args"], "close_fds": call["kwargs"].get("close_fds")} for call in calls]}
    if operation == "cli_usage":
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout), mock.patch.object(sys, "argv", ["pyperclip", "--bad"]):
            runpy.run_module("pyperclip", run_name="__main__")
        return {"has_usage": stdout.getvalue().startswith("Usage: python -m pyperclip")}
    if operation == "cli_copy_stdin":
        copied = []
        with mock.patch.object(pyperclip, "copy", copied.append), mock.patch.object(sys, "argv", ["pyperclip", "--copy"]), mock.patch.object(sys, "stdin", io.StringIO("from stdin")):
            runpy.run_module("pyperclip", run_name="__main__")
        return {"copied": copied}
    if operation == "cli_paste":
        stdout = io.StringIO()
        with mock.patch.object(pyperclip, "paste", lambda: "without newline"), contextlib.redirect_stdout(stdout), mock.patch.object(sys, "argv", ["pyperclip", "-p"]):
            runpy.run_module("pyperclip", run_name="__main__")
        return {"stdout": stdout.getvalue()}
    raise ValueError(f"unknown operation: {operation}")

def main():
    for line in sys.stdin:
        if not line.strip():
            continue
        try:
            result = {"ok": True, "result": _invoke(json.loads(line))}
        except Exception as exc:
            result = {"ok": False, "error": {"type": type(exc).__name__, "message": str(exc)}}
        print(json.dumps(result, ensure_ascii=True, sort_keys=True), flush=True)

if __name__ == "__main__":
    main()
