from __future__ import annotations

import importlib.metadata
import json
import subprocess
import sys

import pytest

import ministats
from ministats import normalize, summarize, tokenize


def test_public_exports_and_version() -> None:
    assert ministats.__version__ == "1.0.0"
    assert ministats.__all__ == ["__version__", "normalize", "summarize", "tokenize"]


def test_distribution_has_no_runtime_dependencies() -> None:
    assert importlib.metadata.requires("ministats-bench") in (None, [])


def test_normalize_case_and_whitespace() -> None:
    assert normalize("  Hello\tWORLD\n") == "hello world"


def test_normalize_nfkc() -> None:
    assert normalize("ＣＡＴ ①") == "cat 1"


def test_normalize_unicode_whitespace() -> None:
    assert normalize("alpha\u2003\u00a0beta") == "alpha beta"


def test_normalize_rejects_non_string() -> None:
    with pytest.raises(TypeError):
        normalize(123)  # type: ignore[arg-type]


def test_tokenize_punctuation_and_underscore() -> None:
    assert tokenize("One, TWO_one 2026!") == ["one", "two", "one", "2026"]


def test_tokenize_unicode_alphanumeric() -> None:
    assert tokenize("Café 中文-１２") == ["café", "中文", "12"]


def test_tokenize_empty_input() -> None:
    assert tokenize("") == []


def test_summarize_counts_original_characters() -> None:
    result = summarize("Red blue red")
    assert result["characters"] == 12
    assert result["words"] == 3
    assert result["unique_words"] == 2


def test_summarize_orders_by_count_then_token() -> None:
    assert summarize("pear apple pear apple plum", top=3)["top_words"] == [
        ("apple", 2),
        ("pear", 2),
        ("plum", 1),
    ]


def test_summarize_top_zero() -> None:
    assert summarize("one two", top=0)["top_words"] == []


def test_summarize_rejects_non_integer_top() -> None:
    with pytest.raises(TypeError):
        summarize("text", top=1.5)  # type: ignore[arg-type]


def test_summarize_rejects_negative_top() -> None:
    with pytest.raises(ValueError):
        summarize("text", top=-1)


def test_module_cli_with_positional_text() -> None:
    completed = subprocess.run(
        [sys.executable, "-m", "ministats", "Red blue red", "--top", "1"],
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(completed.stdout)
    assert payload["top_words"] == [["red", 2]]
    assert completed.stdout.count("\n") == 1


def test_module_cli_reads_stdin() -> None:
    completed = subprocess.run(
        [sys.executable, "-m", "ministats", "--top", "2"],
        input="zeta alpha zeta",
        check=True,
        capture_output=True,
        text=True,
    )
    assert json.loads(completed.stdout)["top_words"] == [["zeta", 2], ["alpha", 1]]


def test_console_script_and_pretty_output() -> None:
    completed = subprocess.run(
        ["ministats", "One one", "--pretty"],
        check=True,
        capture_output=True,
        text=True,
    )
    assert json.loads(completed.stdout)["words"] == 2
    assert completed.stdout.startswith("{\n  ")


def test_cli_rejects_negative_top() -> None:
    completed = subprocess.run(
        [sys.executable, "-m", "ministats", "text", "--top", "-1"],
        capture_output=True,
        text=True,
    )
    assert completed.returncode != 0
    assert "non-negative" in completed.stderr
