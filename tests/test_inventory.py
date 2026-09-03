from __future__ import annotations

import json
from pathlib import Path

import pytest

from nl2repobench.authoring.inventory import (
    InventoryError,
    scan_java_source,
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
        test.name == "test_empty" and "exception" in test.assertion_kinds for test in first.tests
    )


def test_inventory_writer_emits_canonical_json(tmp_path: Path) -> None:
    inventory = scan_python_source(FIXTURE)
    output = tmp_path / "authoring" / "inventory.json"
    write_inventory(inventory, output)
    assert json.loads(output.read_text(encoding="utf-8")) == inventory.to_dict()


def test_inventory_rejects_empty_or_non_directory(tmp_path: Path) -> None:
    with pytest.raises(InventoryError, match="no Python files"):
        scan_python_source(tmp_path)


def test_java_inventory_is_static_and_deterministic(tmp_path: Path) -> None:
    source = tmp_path / "src/main/java/example"
    source.mkdir(parents=True)
    (source / "Parser.java").write_text(
        """package example;
import java.util.List;
public final class Parser {
    public static String parse(String value) { return value; }
}
""",
        encoding="utf-8",
    )
    tests = tmp_path / "src/test/java/example"
    tests.mkdir(parents=True)
    (tests / "ParserTest.java").write_text(
        """package example;
import org.junit.jupiter.api.Test;
class ParserTest {
    @Test void parses() {}
}
""",
        encoding="utf-8",
    )
    (tmp_path / "pom.xml").write_text("<project />", encoding="utf-8")

    first = scan_java_source(tmp_path)
    second = scan_java_source(tmp_path)

    assert first == second
    assert first.language == "java"
    assert first.scanner_identity == "java-regex-stdlib-v1"
    assert first.metrics.test_count == 1
    assert first.metrics.public_symbol_count == 2
    assert first.risk_flags == ()
