"""Deterministic, platform-neutral behavior slice for the icecream task."""

from __future__ import annotations

import builtins

import icecream
import pytest
from icecream import (
    IceCreamDebugger,
    argumentToString,
    colorize,
    formatPair,
    install,
    isLiteral,
    prefixFirstLineIndentRemaining,
    prefixLines,
    uninstall,
)


def make_debugger(prefix="DBG: "):
    output = []
    debugger = IceCreamDebugger(prefix=prefix, outputFunction=output.append)
    return debugger, output


def test_metadata_and_reexports_are_nonempty():
    for name in ("__title__", "__version__", "__license__", "__author__", "__url__"):
        value = getattr(icecream, name)
        assert isinstance(value, str) and value
    assert callable(icecream.ic)
    assert callable(icecream.stderrPrint)


def test_argument_to_string_uses_stable_pretty_values():
    assert argumentToString({"a": [1, 2]}) == "{'a': [1, 2]}"


def test_argument_to_string_preserves_string_newlines():
    assert argumentToString("line1\nline2") == "'line1\nline2'"


def test_literal_recognition_is_deterministic():
    assert isLiteral("1")
    assert isLiteral("{'a': 2}")
    assert not isLiteral("name")


def test_format_uses_mocked_output_free_of_context():
    debugger, output = make_debugger()
    assert debugger.format(1, "x") == "DBG: 1, 'x'"
    assert output == []


def test_call_returns_single_argument_and_uses_callback():
    debugger, output = make_debugger()
    assert debugger(42) == 42
    assert output == ["DBG: 42"]


def test_call_returns_tuple_for_multiple_arguments():
    debugger, output = make_debugger()
    assert debugger("a", 2) == ("a", 2)
    assert output == ["DBG: 'a', 2"]


def test_disabled_debugger_is_a_passthrough_without_output():
    debugger, output = make_debugger()
    debugger.disable()
    assert debugger(7) == 7
    assert output == []
    assert not debugger.enabled


def test_enable_restores_callback_output():
    debugger, output = make_debugger()
    debugger.disable()
    debugger.enable()
    assert debugger(8) == 8
    assert output == ["DBG: 8"]
    assert debugger.enabled


def test_configure_output_changes_prefix_and_formatter():
    debugger, output = make_debugger()
    debugger.configureOutput(
        prefix="VALUE: ",
        argToStringFunction=lambda value: "constant",
    )
    assert debugger.format(123) == "VALUE: constant"
    assert output == []


def test_configure_output_requires_a_change():
    debugger, _ = make_debugger()
    with pytest.raises(TypeError):
        debugger.configureOutput()


def test_callable_prefix_is_evaluated_for_each_format():
    debugger, _ = make_debugger(prefix=lambda: "CALL: ")
    assert debugger.format(5) == "CALL: 5"


def test_singledispatch_registration_and_unregistration():
    debugger, _ = make_debugger()
    default = debugger.format((1, 2))

    def render_tuple(value):
        return "tuple-value"

    argumentToString.register(tuple, render_tuple)
    try:
        assert tuple in argumentToString.registry
        assert debugger.format((1, 2)) == "DBG: tuple-value"
    finally:
        argumentToString.unregister(tuple)
    assert tuple not in argumentToString.registry
    assert debugger.format((1, 2)) == default


def test_prefix_lines_helpers_indent_only_requested_lines():
    assert prefixLines("> ", "a\nb", startAtLine=1) == ["a", "> b"]
    assert prefixFirstLineIndentRemaining("X: ", "a\nb") == ["X: a", "   b"]


def test_format_pair_aligns_a_string_value():
    assert formatPair("", "name", "'line1\nline2'") == "name: 'line1\n       line2'"


def test_colorize_is_a_pure_string_operation():
    rendered = colorize("x = 1")
    assert isinstance(rendered, str)
    assert "x" in rendered and "1" in rendered
    assert "\x1b[" in rendered


def test_install_and_uninstall_support_custom_builtin_name():
    name = "icecream_slice_ic"
    if hasattr(builtins, name):
        delattr(builtins, name)
    install(name)
    try:
        assert getattr(builtins, name) is icecream.ic
    finally:
        uninstall(name)
    assert not hasattr(builtins, name)


def test_uninstall_missing_name_raises_attribute_error():
    name = "icecream_slice_missing_ic"
    if hasattr(builtins, name):
        delattr(builtins, name)
    with pytest.raises(AttributeError):
        uninstall(name)


def test_debugger_format_handles_simple_values_without_terminal_io():
    debugger, _ = make_debugger()
    assert debugger.format(9) == "DBG: 9"


def test_debugger_format_multiple_simple_values_is_stable():
    debugger, _ = make_debugger()
    assert debugger.format(1, 2) == "DBG: 1, 2"
