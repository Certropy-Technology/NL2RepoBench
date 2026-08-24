"""Run the frozen parsy suite in an unprivileged candidate subprocess."""

from __future__ import annotations

import json
from pathlib import Path
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET

ROOT = Path("/tests/verifier")
FIXTURE = Path("/tmp/parsy-tests")
JUNIT = Path("/tmp/parsy-junit.xml")
CANDIDATE_UID = 10001

FROZEN_NODE_IDS = (
    "examples/json.py::test",
    "examples/simple_eval.py::test_item",
    "examples/simple_logo_parser.py::test_item",
    "examples/sql_select.py::test_select",
    "examples/sql_select.py::test_optional_where",
    "tests/test_parsy.py::TestParser::test_add",
    "tests/test_parsy.py::TestParser::test_alt",
    "tests/test_parsy.py::TestParser::test_any_char",
    "tests/test_parsy.py::TestParser::test_at_most",
    "tests/test_parsy.py::TestParser::test_bind",
    "tests/test_parsy.py::TestParser::test_char_from_bytes",
    "tests/test_parsy.py::TestParser::test_char_from_str",
    "tests/test_parsy.py::TestParser::test_combine",
    "tests/test_parsy.py::TestParser::test_combine_dict",
    "tests/test_parsy.py::TestParser::test_combine_dict_list",
    "tests/test_parsy.py::TestParser::test_combine_dict_skip_None",
    "tests/test_parsy.py::TestParser::test_combine_dict_skip_underscores",
    "tests/test_parsy.py::TestParser::test_concat",
    "tests/test_parsy.py::TestParser::test_concat_from_byte_stream",
    "tests/test_parsy.py::TestParser::test_decimal_digit",
    "tests/test_parsy.py::TestParser::test_digit",
    "tests/test_parsy.py::TestParser::test_from_enum_int",
    "tests/test_parsy.py::TestParser::test_from_enum_string",
    "tests/test_parsy.py::TestParser::test_from_enum_transform",
    "tests/test_parsy.py::TestParser::test_generate",
    "tests/test_parsy.py::TestParser::test_generate_backtracking",
    "tests/test_parsy.py::TestParser::test_generate_default_desc",
    "tests/test_parsy.py::TestParser::test_generate_desc",
    "tests/test_parsy.py::TestParser::test_generate_return_parser",
    "tests/test_parsy.py::TestParser::test_letter",
    "tests/test_parsy.py::TestParser::test_line_info",
    "tests/test_parsy.py::TestParser::test_many",
    "tests/test_parsy.py::TestParser::test_many_with_then",
    "tests/test_parsy.py::TestParser::test_map",
    "tests/test_parsy.py::TestParser::test_mark",
    "tests/test_parsy.py::TestParser::test_multiple_failures",
    "tests/test_parsy.py::TestParser::test_multiply",
    "tests/test_parsy.py::TestParser::test_multiply_range",
    "tests/test_parsy.py::TestParser::test_optional",
    "tests/test_parsy.py::TestParser::test_or",
    "tests/test_parsy.py::TestParser::test_or_with_then",
    "tests/test_parsy.py::TestParser::test_peek",
    "tests/test_parsy.py::TestParser::test_regex_bytes",
    "tests/test_parsy.py::TestParser::test_regex_compiled",
    "tests/test_parsy.py::TestParser::test_regex_group_name",
    "tests/test_parsy.py::TestParser::test_regex_group_number",
    "tests/test_parsy.py::TestParser::test_regex_group_tuple",
    "tests/test_parsy.py::TestParser::test_regex_str",
    "tests/test_parsy.py::TestParser::test_sep_by",
    "tests/test_parsy.py::TestParser::test_sep_by_with_min_and_max",
    "tests/test_parsy.py::TestParser::test_seq",
    "tests/test_parsy.py::TestParser::test_seq_kwargs",
    "tests/test_parsy.py::TestParser::test_seq_kwargs_error",
    "tests/test_parsy.py::TestParser::test_seq_kwargs_fail",
    "tests/test_parsy.py::TestParser::test_should_fail",
    "tests/test_parsy.py::TestParser::test_string",
    "tests/test_parsy.py::TestParser::test_string_from",
    "tests/test_parsy.py::TestParser::test_string_from_transform",
    "tests/test_parsy.py::TestParser::test_string_transform",
    "tests/test_parsy.py::TestParser::test_string_transform_2",
    "tests/test_parsy.py::TestParser::test_tag",
    "tests/test_parsy.py::TestParser::test_tag_map_dict",
    "tests/test_parsy.py::TestParser::test_test_char",
    "tests/test_parsy.py::TestParser::test_then",
    "tests/test_parsy.py::TestParser::test_times",
    "tests/test_parsy.py::TestParser::test_times_with_min_and_max",
    "tests/test_parsy.py::TestParser::test_times_with_min_and_max_and_then",
    "tests/test_parsy.py::TestParser::test_times_with_then",
    "tests/test_parsy.py::TestParser::test_times_zero",
    "tests/test_parsy.py::TestParser::test_until",
    "tests/test_parsy.py::TestParser::test_until_with_consume_other",
    "tests/test_parsy.py::TestParser::test_until_with_max",
    "tests/test_parsy.py::TestParser::test_until_with_min",
    "tests/test_parsy.py::TestParser::test_until_with_min_max",
    "tests/test_parsy.py::TestParser::test_whitespace",
    "tests/test_parsy.py::TestParserTokens::test_index",
    "tests/test_parsy.py::TestParserTokens::test_match_item",
    "tests/test_parsy.py::TestParserTokens::test_parse_tokens",
    "tests/test_parsy.py::TestParserTokens::test_test_item",
    "tests/test_parsy.py::TestUtils::test_line_info_at",
    "tests/test_parsy.py::TestForwardDeclaration::test_forward_declaration_1",
    "tests/test_parsy.py::TestForwardDeclaration::test_forward_declaration_2",
    "tests/test_parsy.py::TestForwardDeclaration::test_forward_declaration_cant_become_twice",
    "tests/test_sexpr.py::TestSexpr::test_boolean",
    "tests/test_sexpr.py::TestSexpr::test_comments",
    "tests/test_sexpr.py::TestSexpr::test_double_quote",
    "tests/test_sexpr.py::TestSexpr::test_form",
    "tests/test_sexpr.py::TestSexpr::test_quote",
)


def _stage_fixture() -> None:
    if FIXTURE.exists():
        shutil.rmtree(FIXTURE)
    shutil.copytree(ROOT / "fixture", FIXTURE)
    shutil.copy2(ROOT / "adapter.py", FIXTURE / "adapter.py")
    for path in FIXTURE.rglob("*"):
        path.chmod(0o555 if path.is_dir() else 0o444)
    FIXTURE.chmod(0o555)


def _run_tests() -> subprocess.CompletedProcess[str]:
    JUNIT.write_text("", encoding="utf-8")
    JUNIT.chmod(0o666)
    subprocess.run(["chown", f"{CANDIDATE_UID}:{CANDIDATE_UID}", str(JUNIT)], check=True)
    return subprocess.run(
        [
            "runuser", "-u", "candidate", "--", "env", "HOME=/tmp",
            "PYTHONNOUSERSITE=1", "PYTHONDONTWRITEBYTECODE=1",
            "PYTEST_DISABLE_PLUGIN_AUTOLOAD=1", "/usr/local/bin/python", "-I", "-B",
            str(FIXTURE / "adapter.py"), "-p", "no:cacheprovider",
            "--continue-on-collection-errors", "--junitxml=/tmp/parsy-junit.xml", "-q", ".",
        ], cwd=FIXTURE, capture_output=True, text=True, timeout=240, check=False
    )


def _junit_statuses() -> dict[tuple[str, str], str]:
    if not JUNIT.is_file() or JUNIT.stat().st_size == 0:
        return {}
    try:
        cases = list(ET.parse(JUNIT).getroot().iter("testcase"))
    except (ET.ParseError, OSError):
        return {}
    statuses: dict[tuple[str, str], str] = {}
    for case in cases:
        status = "failed"
        if case.find("skipped") is not None:
            status = "skipped"
        elif case.find("failure") is None and case.find("error") is None:
            status = "passed"
        statuses[(case.get("classname", ""), case.get("name", ""))] = status
    return statuses


def _junit_key(node_id: str) -> tuple[str, str]:
    parts = node_id.split("::")
    module = parts[0].replace("/", ".").removesuffix(".py")
    if len(parts) == 2:
        return module, parts[1]
    return f"{module}.{parts[1]}", parts[2]


def main() -> None:
    _stage_fixture()
    completed = _run_tests()
    statuses = _junit_statuses()
    if not statuses:
        print(f"frozen suite produced no JUnit cases: rc={completed.returncode}", file=sys.stderr)
    leaves = [
        {"id": node_id, "status": statuses.get(_junit_key(node_id), "failed")}
        for node_id in FROZEN_NODE_IDS
    ]
    print(json.dumps({"schema_version": "1.0", "leaves": leaves}, sort_keys=True))


if __name__ == "__main__":
    main()
