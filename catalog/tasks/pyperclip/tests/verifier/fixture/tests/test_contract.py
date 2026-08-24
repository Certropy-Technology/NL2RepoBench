from __future__ import annotations
import json
import os
from pathlib import Path
import subprocess
import sys

RUNNER = Path(__file__).with_name("runner.py")

def request(operation, **payload):
    body = json.dumps({"operation": operation, **payload}) + "\n"
    env = os.environ.copy()
    env.update({"DISPLAY": "", "WAYLAND_DISPLAY": "", "PYTHONDONTWRITEBYTECODE": "1"})
    completed = subprocess.run([sys.executable, str(RUNNER)], input=body, text=True, capture_output=True, check=False, env=env)
    assert completed.returncode == 0, completed.stderr
    response = json.loads(completed.stdout)
    assert response["ok"], response
    return response["result"]

def test_public_exports_and_version():
    result = request("exports")
    assert result["version"] == "1.11.0"
    assert result["all"] == ["copy", "paste", "set_clipboard", "determine_clipboard"]
    assert result["missing"] == []

def test_import_is_lazy_and_headless_detection_is_explicit():
    result = request("lazy")
    assert result == {"before": False, "after_determine": False, "error": {"type": "PyperclipException", "runtime_error": True}}

def test_fixture_adapter_round_trip_is_json_safe():
    result = request("memory", values=["hé\n", 42, None, [1, 2]])
    assert result == {"available": True, "values": ["hé\n", "42", "None", "[1, 2]"]}

def test_no_clipboard_is_falsey_and_actionable():
    result = request("no_clipboard")
    assert result["available"] is True
    assert result["falsey"] is True
    assert len(result["errors"]) == 2
    assert all(error["runtime_error"] and error["has_guidance"] for error in result["errors"])

def test_invalid_manual_selection_names_choices():
    assert request("invalid_selection") == {"type": "ValueError", "mentions_choices": True}

def test_xclip_uses_utf8_selection_and_closes_descriptors():
    result = request("xclip_mock")
    assert result["result"] == "fixture"
    assert result["calls"][0]["args"] == ["xclip", "-selection", "p"]
    assert result["calls"][0]["input"] == "hé"
    assert result["calls"][0]["kwargs"]["close_fds"] == "True"
    assert result["calls"][1]["args"] == ["xclip", "-selection", "p", "-o"]

def test_wayland_empty_copy_uses_clear_and_primary_selection():
    assert request("wayland_empty_mock") == {"calls": [{"args": ["wl-copy", "-p", "--clear"], "close_fds": True}]}

def test_module_cli_has_short_usage_for_unknown_invocation():
    assert request("cli_usage") == {"has_usage": True}


def test_module_cli_copies_all_stdin_without_argument():
    assert request("cli_copy_stdin") == {"copied": ["from stdin"]}


def test_module_cli_paste_does_not_add_a_newline():
    assert request("cli_paste") == {"stdout": "without newline"}
