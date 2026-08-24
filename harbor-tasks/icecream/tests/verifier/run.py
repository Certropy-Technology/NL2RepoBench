"""Run the fixed icecream slice and emit a bounded custom-json-v1 report."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

EXPECTED_TOTAL = 20
CASE_NAMES = (
    "test_metadata_and_reexports_are_nonempty",
    "test_argument_to_string_uses_stable_pretty_values",
    "test_argument_to_string_preserves_string_newlines",
    "test_literal_recognition_is_deterministic",
    "test_format_uses_mocked_output_free_of_context",
    "test_call_returns_single_argument_and_uses_callback",
    "test_call_returns_tuple_for_multiple_arguments",
    "test_disabled_debugger_is_a_passthrough_without_output",
    "test_enable_restores_callback_output",
    "test_configure_output_changes_prefix_and_formatter",
    "test_configure_output_requires_a_change",
    "test_callable_prefix_is_evaluated_for_each_format",
    "test_singledispatch_registration_and_unregistration",
    "test_prefix_lines_helpers_indent_only_requested_lines",
    "test_format_pair_aligns_a_string_value",
    "test_colorize_is_a_pure_string_operation",
    "test_install_and_uninstall_support_custom_builtin_name",
    "test_uninstall_missing_name_raises_attribute_error",
    "test_debugger_format_handles_simple_values_without_terminal_io",
    "test_debugger_format_multiple_simple_values_is_stable",
)


def _load_slice():
    path = Path(__file__).with_name("tests") / "test_deterministic_slice.py"
    spec = importlib.util.spec_from_file_location("icecream_private_slice", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("private slice module could not be loaded")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def main() -> int:
    # Candidate code is isolated from the verifier package and is only imported
    # by the private slice process.
    preferred = ["/tmp/candidate-site", "/workspace", "/opt/candidate-dependencies/site"]
    remaining = [path for path in sys.path if path not in preferred]
    sys.path[:] = preferred + remaining

    leaves = []
    try:
        module = _load_slice()
        if len(CASE_NAMES) != EXPECTED_TOTAL:
            raise RuntimeError("private slice case list has the wrong denominator")
        for name in CASE_NAMES:
            case = getattr(module, name, None)
            if not callable(case):
                raise RuntimeError(f"private slice case is missing: {name}")
            try:
                case()
            except Exception as exc:  # Candidate failures are individual leaves.
                leaves.append({"id": name, "status": "failed", "message": type(exc).__name__})
            else:
                leaves.append({"id": name, "status": "passed"})
    except Exception as exc:
        leaves = [
            {"id": name, "status": "failed", "message": type(exc).__name__}
            for name in CASE_NAMES
        ]

    print(json.dumps({"schema_version": "1.0", "leaves": leaves}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
