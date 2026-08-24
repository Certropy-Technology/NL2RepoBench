"""Trusted schedule verifier: runs the frozen upstream suite over a boundary.

This module is trusted and runs as root inside the verifier image. It never
imports candidate code. All candidate interaction happens in a child process
launched as the unprivileged ``candidate`` user with ``python -I``, so the
candidate cannot influence this interpreter.

The graded denominator is the frozen collection of the pinned upstream test
module (81 node ids, recorded below). Leaves are emitted for exactly those
frozen node ids, so a candidate can neither add nor remove graded leaves.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

CANDIDATE_UID = 10001
ADAPTER = Path(__file__).with_name("adapter.py")
FROZEN_TEST = Path(__file__).with_name("test_schedule.py")
SCRATCH = Path("/tmp/schedule-verifier-scratch")
TEST_FILENAME = "test_schedule.py"
TIMEOUT_SEC = 240.0

# Frozen collection of the pinned revision; see provenance.md.
FROZEN_NODE_IDS = (
    "test_schedule.py::SchedulerTests::test_align_utc_offset_after_fold_fixate",
    "test_schedule.py::SchedulerTests::test_align_utc_offset_no_change",
    "test_schedule.py::SchedulerTests::test_align_utc_offset_no_timezone",
    "test_schedule.py::SchedulerTests::test_align_utc_offset_with_dst_fold",
    "test_schedule.py::SchedulerTests::test_align_utc_offset_with_dst_fold_fixate_1",
    "test_schedule.py::SchedulerTests::test_align_utc_offset_with_dst_fold_fixate_2",
    "test_schedule.py::SchedulerTests::test_align_utc_offset_with_dst_gap",
    "test_schedule.py::SchedulerTests::test_at_time",
    "test_schedule.py::SchedulerTests::test_at_time_hour",
    "test_schedule.py::SchedulerTests::test_at_time_minute",
    "test_schedule.py::SchedulerTests::test_cancel_job",
    "test_schedule.py::SchedulerTests::test_cancel_jobs",
    "test_schedule.py::SchedulerTests::test_clear_by_tag",
    "test_schedule.py::SchedulerTests::test_daylight_saving_time",
    "test_schedule.py::SchedulerTests::test_get_by_tag",
    "test_schedule.py::SchedulerTests::test_idle_seconds",
    "test_schedule.py::SchedulerTests::test_job_func_args_are_passed_on",
    "test_schedule.py::SchedulerTests::test_misconfigured_job_wont_break_scheduler",
    "test_schedule.py::SchedulerTests::test_move_to_next_weekday_nextweek",
    "test_schedule.py::SchedulerTests::test_move_to_next_weekday_today",
    "test_schedule.py::SchedulerTests::test_move_to_next_weekday_tommorrow",
    "test_schedule.py::SchedulerTests::test_next_run_property",
    "test_schedule.py::SchedulerTests::test_next_run_time",
    "test_schedule.py::SchedulerTests::test_next_run_time_day_end",
    "test_schedule.py::SchedulerTests::test_next_run_time_hour_end",
    "test_schedule.py::SchedulerTests::test_next_run_time_hour_end_katmandu",
    "test_schedule.py::SchedulerTests::test_next_run_time_hour_end_london",
    "test_schedule.py::SchedulerTests::test_next_run_time_minute_end",
    "test_schedule.py::SchedulerTests::test_next_run_time_minute_end_katmhandu",
    "test_schedule.py::SchedulerTests::test_next_run_time_minute_end_london",
    "test_schedule.py::SchedulerTests::test_next_run_with_tag",
    "test_schedule.py::SchedulerTests::test_repr_functools_partial_job_func",
    "test_schedule.py::SchedulerTests::test_run_all",
    "test_schedule.py::SchedulerTests::test_run_all_with_decorator",
    "test_schedule.py::SchedulerTests::test_run_all_with_decorator_args",
    "test_schedule.py::SchedulerTests::test_run_all_with_decorator_defaultargs",
    "test_schedule.py::SchedulerTests::test_run_every_n_days_at_specific_time",
    "test_schedule.py::SchedulerTests::test_run_every_weekday_at_specific_time_past_today",
    "test_schedule.py::SchedulerTests::test_run_every_weekday_at_specific_time_today",
    "test_schedule.py::SchedulerTests::test_run_pending",
    "test_schedule.py::SchedulerTests::test_singular_time_units_match_plural_units",
    "test_schedule.py::SchedulerTests::test_tag_type_enforcement",
    "test_schedule.py::SchedulerTests::test_time_range",
    "test_schedule.py::SchedulerTests::test_time_range_repr",
    "test_schedule.py::SchedulerTests::test_time_units",
    "test_schedule.py::SchedulerTests::test_to_repr",
    "test_schedule.py::SchedulerTests::test_to_string",
    "test_schedule.py::SchedulerTests::test_to_string_functools_partial_job_func",
    "test_schedule.py::SchedulerTests::test_to_string_lambda_job_func",
    "test_schedule.py::SchedulerTests::test_tz",
    "test_schedule.py::SchedulerTests::test_tz_daily_different_simultaneous_dst_change",
    "test_schedule.py::SchedulerTests::test_tz_daily_dst",
    "test_schedule.py::SchedulerTests::test_tz_daily_dst_ending_point",
    "test_schedule.py::SchedulerTests::test_tz_daily_dst_overlap_hour",
    "test_schedule.py::SchedulerTests::test_tz_daily_dst_skip_hour",
    "test_schedule.py::SchedulerTests::test_tz_daily_dst_starting_point",
    "test_schedule.py::SchedulerTests::test_tz_daily_end_month_offset",
    "test_schedule.py::SchedulerTests::test_tz_daily_end_year_cross_continent",
    "test_schedule.py::SchedulerTests::test_tz_daily_exact_future_scheduling",
    "test_schedule.py::SchedulerTests::test_tz_daily_exact_seconds_precision",
    "test_schedule.py::SchedulerTests::test_tz_daily_half_hour_offset",
    "test_schedule.py::SchedulerTests::test_tz_daily_issue_592",
    "test_schedule.py::SchedulerTests::test_tz_daily_issue_605",
    "test_schedule.py::SchedulerTests::test_tz_daily_issue_608_before_dst_end",
    "test_schedule.py::SchedulerTests::test_tz_daily_issue_608_mid_dst",
    "test_schedule.py::SchedulerTests::test_tz_daily_issue_608_post_dst",
    "test_schedule.py::SchedulerTests::test_tz_daily_issue_608_pre_dst",
    "test_schedule.py::SchedulerTests::test_tz_daily_leap_year",
    "test_schedule.py::SchedulerTests::test_tz_daily_midnight",
    "test_schedule.py::SchedulerTests::test_tz_daily_new_year_offset",
    "test_schedule.py::SchedulerTests::test_tz_daily_opposite_dst_change",
    "test_schedule.py::SchedulerTests::test_tz_daily_skip_dst_change",
    "test_schedule.py::SchedulerTests::test_tz_daily_utc",
    "test_schedule.py::SchedulerTests::test_tz_hourly_intermediate_conversion",
    "test_schedule.py::SchedulerTests::test_tz_invalid_timezone_exceptions",
    "test_schedule.py::SchedulerTests::test_tz_minutes_year_round",
    "test_schedule.py::SchedulerTests::test_tz_weekly_large_interval_backward",
    "test_schedule.py::SchedulerTests::test_tz_weekly_large_interval_forward",
    "test_schedule.py::SchedulerTests::test_tz_weekly_sunday_conversion",
    "test_schedule.py::SchedulerTests::test_until_time",
    "test_schedule.py::SchedulerTests::test_weekday_at_todady",
)


def _prepare_scratch() -> Path:
    """Give the candidate user a private, writable copy of the frozen suite."""

    shutil.rmtree(SCRATCH, ignore_errors=True)
    SCRATCH.mkdir(parents=True, exist_ok=True)
    target = SCRATCH / TEST_FILENAME
    shutil.copyfile(FROZEN_TEST, target)
    os.chmod(target, 0o444)
    os.chown(target, CANDIDATE_UID, CANDIDATE_UID)
    os.chown(SCRATCH, CANDIDATE_UID, CANDIDATE_UID)
    os.chmod(SCRATCH, 0o700)
    return target


def _run_adapter(report: Path) -> dict[str, object]:
    """Execute the adapter as the candidate user and read its JSON report."""

    dependency_site = os.environ.get(
        "NL2REPO_CANDIDATE_DEPENDENCIES", "/opt/candidate-dependencies/site"
    )
    candidate_site = os.environ.get("NL2REPO_CANDIDATE_SITE", "/tmp/candidate-site")
    command = [
        sys.executable,
        "-I",
        "-B",
        "-",
        "--candidate-site",
        candidate_site,
        "--dependency-site",
        dependency_site,
        "--scratch",
        str(SCRATCH),
        "--test-file",
        TEST_FILENAME,
        "--report",
        str(report),
    ]
    if os.environ.get("NL2REPO_DIRECT_ADAPTER") != "1":
        command = [
            "runuser",
            "-u",
            "candidate",
            "--",
            "env",
            "HOME=/tmp/schedule-verifier-scratch",
            "TMPDIR=/tmp/schedule-verifier-scratch",
            "TZ=UTC",
            "LANG=C.UTF-8",
            "LC_ALL=C.UTF-8",
            "PYTHONDONTWRITEBYTECODE=1",
            "PYTHONHASHSEED=0",
            "PYTEST_DISABLE_PLUGIN_AUTOLOAD=1",
            *command,
        ]
    try:
        completed = subprocess.run(
            command,
            input=ADAPTER.read_bytes(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=TIMEOUT_SEC,
            check=False,
        )
    except (OSError, subprocess.SubprocessError) as error:
        return {"error": "VerifierProcessError", "message": str(error)[:2000]}
    if not report.is_file():
        detail = completed.stderr.decode("utf-8", "replace")[-2000:]
        return {
            "error": "CandidateProcessError",
            "message": f"exit={completed.returncode} {detail}",
        }
    try:
        return json.loads(report.read_text(encoding="utf-8"))
    except (OSError, ValueError) as error:
        return {"error": "CandidateProtocolError", "message": str(error)[:2000]}


def main() -> None:
    report_path = SCRATCH / "report.json"
    try:
        _prepare_scratch()
        result = _run_adapter(report_path)
    except OSError as error:
        result = {"error": "VerifierSetupError", "message": str(error)[:2000]}

    outcomes = result.get("outcomes") if isinstance(result, dict) else None
    if not isinstance(outcomes, dict):
        outcomes = {}
    failure_note = None
    if isinstance(result, dict) and result.get("error"):
        failure_note = f"{result['error']}: {str(result.get('message', ''))[:400]}"

    leaves = []
    for nodeid in FROZEN_NODE_IDS:
        status = outcomes.get(nodeid)
        if status not in {"passed", "failed", "skipped"}:
            leaf = {"id": nodeid, "status": "failed"}
            leaf["message"] = failure_note or "node id absent from candidate run"
            leaves.append(leaf)
            continue
        leaf = {"id": nodeid, "status": status}
        if status == "failed":
            leaf["message"] = "frozen upstream assertion failed"
        leaves.append(leaf)

    print(json.dumps({"schema_version": "1.0", "leaves": leaves}, sort_keys=True))


if __name__ == "__main__":
    main()
