from __future__ import annotations

import json
from typing import Any

from nl2repobench.verification.candidate_client import (
    CandidateCallResult,
    call,
    get,
    metadata_requires,
    run_console,
    run_module,
)


def candidate_value(attribute: str, *args: Any, **kwargs: Any) -> Any:
    result = call("ministats", attribute, *args, **kwargs)
    assert result.ok, result
    return result.value


def candidate_exception(attribute: str, *args: Any, **kwargs: Any) -> CandidateCallResult:
    result = call("ministats", attribute, *args, **kwargs)
    assert result.ok is False, result
    return result


def test_public_exports_and_version() -> None:
    version = get("ministats", "__version__")
    exports = get("ministats", "__all__")
    assert version.ok and version.value == "1.0.0", version
    assert exports.ok and exports.value == [
        "__version__",
        "normalize",
        "summarize",
        "tokenize",
    ], exports


def test_distribution_has_no_runtime_dependencies() -> None:
    result = metadata_requires("ministats-bench")
    assert result.ok and result.value in (None, []), result


def test_normalize_case_and_whitespace() -> None:
    assert candidate_value("normalize", "  Hello\tWORLD\n") == "hello world"


def test_normalize_nfkc() -> None:
    assert candidate_value("normalize", "ＣＡＴ ①") == "cat 1"


def test_normalize_unicode_whitespace() -> None:
    assert candidate_value("normalize", "alpha\u2003\u00a0beta") == "alpha beta"


def test_normalize_rejects_non_string() -> None:
    result = candidate_exception("normalize", 123)
    assert result.exception_type == "builtins.TypeError"


def test_tokenize_punctuation_and_underscore() -> None:
    assert candidate_value("tokenize", "One, TWO_one 2026!") == ["one", "two", "one", "2026"]


def test_tokenize_unicode_alphanumeric() -> None:
    assert candidate_value("tokenize", "Café 中文-１２") == ["café", "中文", "12"]


def test_tokenize_empty_input() -> None:
    assert candidate_value("tokenize", "") == []


def test_summarize_counts_original_characters() -> None:
    result = candidate_value("summarize", "Red blue red")
    assert result["characters"] == 12
    assert result["words"] == 3
    assert result["unique_words"] == 2


def test_summarize_orders_by_count_then_token() -> None:
    assert candidate_value("summarize", "pear apple pear apple plum", top=3)[
        "top_words"
    ] == [
        ["apple", 2],
        ["pear", 2],
        ["plum", 1],
    ]


def test_summarize_top_zero() -> None:
    assert candidate_value("summarize", "one two", top=0)["top_words"] == []


def test_summarize_rejects_non_integer_top() -> None:
    result = candidate_exception("summarize", "text", top=1.5)
    assert result.exception_type == "builtins.TypeError"


def test_summarize_rejects_negative_top() -> None:
    result = candidate_exception("summarize", "text", top=-1)
    assert result.exception_type == "builtins.ValueError"


def test_module_cli_with_positional_text() -> None:
    completed = run_module("ministats", ["Red blue red", "--top", "1"])
    assert completed.returncode == 0, completed
    payload = json.loads(completed.stdout)
    assert payload["top_words"] == [["red", 2]]
    assert completed.stdout.count("\n") == 1


def test_module_cli_reads_stdin() -> None:
    completed = run_module("ministats", ["--top", "2"], input_text="zeta alpha zeta")
    assert completed.returncode == 0, completed
    assert json.loads(completed.stdout)["top_words"] == [["zeta", 2], ["alpha", 1]]


def test_console_script_and_pretty_output() -> None:
    completed = run_console("ministats", ["One one", "--pretty"])
    assert completed.returncode == 0, completed
    assert json.loads(completed.stdout)["words"] == 2
    assert completed.stdout.startswith("{\n  ")


def test_cli_rejects_negative_top() -> None:
    completed = run_module("ministats", ["text", "--top", "-1"])
    assert completed.returncode != 0
    assert "non-negative" in completed.stderr
