from __future__ import annotations

import json
from pathlib import Path

import pytest

from nl2repobench.authoring.inventory import (
    InventoryError,
    scan_python_source,
    write_inventory,
)

FIXTURE = Path(__file__).parent / "fixtures" / "inventory-python"


def test_python_inventory_is_static_complete_and_deterministic() -> None:
    first = scan_python_source(FIXTURE)
    second = scan_python_source(FIXTURE)
    assert first.to_json() == second.to_json()
    assert first.language == "python"
    assert first.metrics.public_symbol_count >= 4
    assert first.metrics.test_count == 2
    assert "dynamic-execution" in first.risk_flags
    assert "external-service" in first.risk_flags
    assert "cli" in first.cli_entries
    assert any(symbol.qualified_name == "sample.Parser.parse" for symbol in first.symbols)
    assert any(
        test.name == "test_empty" and "exception" in test.assertion_kinds
        for test in first.tests
    )


def test_inventory_writer_emits_canonical_json(tmp_path: Path) -> None:
    inventory = scan_python_source(FIXTURE)
    output = tmp_path / "authoring" / "inventory.json"
    write_inventory(inventory, output)
    assert json.loads(output.read_text(encoding="utf-8")) == inventory.to_dict()


def test_inventory_rejects_empty_or_non_directory(tmp_path: Path) -> None:
    with pytest.raises(InventoryError, match="no Python files"):
        scan_python_source(tmp_path)
