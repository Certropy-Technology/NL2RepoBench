"""Trusted JSON report writer for the prompt_toolkit headless slice.

Candidate code is only evaluated by the private adapter in a fresh,
unprivileged child process. This root-owned report writer compares its bounded
JSON result against values frozen from prompt_toolkit 3.0.53.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys


ADAPTER = Path(__file__).with_name("adapter.py")
SCHEMA_VERSION = "prompt-toolkit-headless-v1"
CHILD_TIMEOUT_SEC = 20.0

CASES = [
    {
        "id": "api-surface-and-packaging",
        "operation": "api_surface",
        "expected": {
            "all": [
                "Application",
                "prompt",
                "choice",
                "PromptSession",
                "print_formatted_text",
                "HTML",
                "ANSI",
                "__version__",
                "VERSION",
            ],
            "root_exports": {
                "ANSI": True,
                "Application": True,
                "HTML": True,
                "PromptSession": True,
                "VERSION": True,
                "__version__": True,
                "choice": True,
                "print_formatted_text": True,
                "prompt": True,
            },
            "types": {
                "Completion": "Completion",
                "Document": "Document",
                "InMemoryHistory": "InMemoryHistory",
                "KeyBindings": "KeyBindings",
                "Keys": "Keys",
                "NestedCompleter": "NestedCompleter",
                "WordCompleter": "WordCompleter",
            },
            "version": "3.0.53",
            "version_tuple": [3, 0, 53],
        },
    },
    {
        "id": "document-cursor-lines-and-search",
        "operation": "document",
        "expected": {
            "char_before_cursor": "e",
            "current_char": "t",
            "current_line": "beta gamma",
            "current_line_after_cursor": "ta gamma",
            "current_line_before_cursor": "be",
            "cursor_position": 8,
            "cursor_position_col": 2,
            "cursor_position_row": 1,
            "find_a": 1,
            "find_backwards_a": -4,
            "line_count": 3,
            "lines": ["alpha", "beta gamma", ""],
            "text_after_cursor": "ta gamma\n",
            "text_before_cursor": "alpha\nbe",
            "translate_index": [1, 5],
            "translate_row_col": 16,
            "word_before_cursor": "be",
        },
    },
    {
        "id": "buffer-editing-undo-readonly-and-apply-completion",
        "operation": "buffer_editing",
        "expected": {
            "after_delete": {"cursor": 6, "text": "some_txt"},
            "after_redo": {"cursor": 4, "text": "abXYcd"},
            "after_undo": {"cursor": 4, "text": "abcd"},
            "applied_completion": {"cursor": 11, "text": "hello world"},
            "before_undo": {"cursor": 4, "text": "abXYcd"},
            "deleted": "eA",
            "inserted": {"cursor": 8, "text": "some_teAxt"},
            "readonly_error": "EditReadOnlyBuffer",
        },
    },
    {
        "id": "completion-data-model",
        "operation": "completion_data",
        "expected": {
            "completion": {
                "display_meta_text": "cached",
                "display_text": "Archive",
                "selected_style": "class:selected",
                "start_position": -2,
                "style": "class:item",
                "text": "archive",
            },
            "position_minus_one": {
                "display_meta_text": "cached",
                "display_text": "Archive",
                "selected_style": "",
                "start_position": 0,
                "style": "",
                "text": "rchive",
            },
        },
    },
    {
        "id": "word-completion-case-and-sentence-rules",
        "operation": "word_completion",
        "expected": {
            "case_insensitive_A": ["alpha", "Alpine", "alphabet"],
            "case_sensitive_A": ["Alpine"],
            "case_sensitive_a": ["alpha", "alphabet"],
            "sentence": ["show version", "show value"],
        },
    },
    {
        "id": "nested-and-deduplicated-completion-order",
        "operation": "nested_completion",
        "expected": {
            "deduplicated": ["alpha", "beta", "gamma"],
            "nested_child": ["version", "value"],
            "nested_root": ["show", "exit"],
        },
    },
    {
        "id": "in-memory-history-clipboard-and-selection-data",
        "operation": "history_clipboard",
        "expected": {
            "clipboard_current": {"text": "plain", "type": "CHARACTERS"},
            "clipboard_rotated": {"text": "line", "type": "LINES"},
            "history_loaded": ["third", "second", "first"],
            "history_strings": ["first", "second", "third"],
            "selection": {
                "original_cursor_position": 7,
                "shift_mode": True,
                "type": "BLOCK",
            },
        },
    },
    {
        "id": "validator-data-and-buffer-cursor-placement",
        "operation": "validation",
        "expected": {
            "invalid": {
                "cursor": 2,
                "error_cursor": 2,
                "error_message": "expected accepted",
                "result": False,
            },
            "valid": {"error": True, "result": True},
        },
    },
    {
        "id": "key-binding-prefix-longest-match-and-any",
        "operation": "key_bindings",
        "expected": {
            "calls": ["control-x", "control-d", "control-x-control-c", "any:z"],
            "pending_after_prefix": ["c-x"],
            "prefix_match_count": 1,
            "specific_match_count": 1,
        },
    },
]


def invoke(operation: str) -> dict[str, object]:
    request = json.dumps(
        {"operation": operation, "schema_version": SCHEMA_VERSION},
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    )
    command = [
        sys.executable,
        "-I",
        "-B",
        "-",
        "--candidate-site",
        os.environ.get("NL2REPO_CANDIDATE_SITE", "/tmp/candidate-site"),
        "--request",
        request,
    ]
    if os.environ.get("NL2REPO_DIRECT_ADAPTER") != "1":
        command = [
            "runuser",
            "-u",
            "candidate",
            "--",
            "env",
            "HOME=/home/candidate",
            "PYTHONDONTWRITEBYTECODE=1",
            "PYTHONHASHSEED=0",
            "PYTEST_DISABLE_PLUGIN_AUTOLOAD=1",
            "LC_ALL=C.UTF-8",
            "TZ=UTC",
            "TERM=dumb",
            "NO_COLOR=1",
            *command,
        ]
    try:
        completed = subprocess.run(
            command,
            input=ADAPTER.read_bytes(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=CHILD_TIMEOUT_SEC,
            check=False,
        )
    except (OSError, subprocess.SubprocessError) as error:
        return {
            "exception_message": str(error),
            "exception_type": "VerifierProcessError",
            "ok": False,
        }
    lines = [
        line for line in completed.stdout.decode("utf-8", "replace").splitlines() if line
    ]
    if completed.returncode != 0 or len(lines) != 1:
        detail = completed.stderr.decode("utf-8", "replace") or completed.stdout.decode(
            "utf-8", "replace"
        )
        return {
            "exception_message": detail[-2000:],
            "exception_type": "CandidateProcessError",
            "ok": False,
        }
    try:
        result = json.loads(lines[0])
    except json.JSONDecodeError as error:
        return {
            "exception_message": str(error),
            "exception_type": "CandidateProtocolError",
            "ok": False,
        }
    if not isinstance(result, dict):
        return {
            "exception_message": "adapter response is not an object",
            "exception_type": "CandidateProtocolError",
            "ok": False,
        }
    return result


def main() -> None:
    leaves = []
    for case in CASES:
        result = invoke(case["operation"])
        passed = result.get("ok") is True and result.get("value") == case["expected"]
        leaf = {
            "id": "prompt-toolkit/" + case["id"],
            "status": "passed" if passed else "failed",
        }
        if not passed:
            leaf["message"] = json.dumps(
                {"actual": result, "expected": case["expected"]},
                ensure_ascii=False,
                sort_keys=True,
            )[:1000]
        leaves.append(leaf)
    print(
        json.dumps(
            {"schema_version": "1.0", "leaves": leaves},
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
