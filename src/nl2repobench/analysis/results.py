"""Normalize Harbor trial results into Polars-friendly benchmark tables.

The normalizer keeps the raw result files authoritative and extracts only a
bounded, flat analysis record.  It deliberately does not rewrite canonical
manifests or grading artifacts, and it computes macro averages over valid task
scores rather than over raw test-case counts.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import polars as pl


def result_paths(roots: list[Path]) -> list[Path]:
    """Return trial result files, excluding job-level aggregate result files."""

    paths: set[Path] = set()
    for root in roots:
        if root.is_file() and root.name == "result.json":
            paths.add(root)
            continue
        if root.is_dir():
            paths.update(path for path in root.rglob("result.json") if path.is_file())
    return sorted(
        path
        for path in paths
        if _is_trial_result(path)
    )


def normalize_result(path: Path) -> dict[str, Any]:
    """Extract one stable analysis record from a Harbor trial result."""

    payload = json.loads(path.read_text(encoding="utf-8"))
    config = _mapping(payload.get("config"))
    agent = _mapping(config.get("agent"))
    agent_info = _mapping(payload.get("agent_info"))
    model = agent.get("model_name") or agent_info.get("model") or agent_info.get("name")
    verifier = _mapping(payload.get("verifier_result"))
    rewards = _mapping(verifier.get("rewards"))
    grading = _read_grading(path.parent)
    exception = _mapping(payload.get("exception_info"))
    counts = _mapping(grading.get("counts"))
    failure_class = grading.get("failure_class")
    failure_reason = (
        grading.get("failure_reason")
        or grading.get("reason")
        or exception.get("exception_type")
    )
    if _verifier_build_failure(exception):
        failure_class = "verifier"
        failure_reason = "verifier-build-failed"
    elif _legacy_fable_empty_workspace(path, str(model or "unknown")):
        # Older Fable trials used the relay's enabled-thinking path. The
        # malformed tool call left an empty workspace, so grader-side
        # installation/collection errors are downstream symptoms of the
        # provider/adapter defect rather than model behavior.
        failure_class = "infrastructure"
        failure_reason = "provider-tool-schema-empty-input"
    return {
        "task_id": _canonical_task_id(payload.get("task_name"), path.parent.name),
        "trial_name": str(payload.get("trial_name") or path.parent.name),
        "model": str(model or "unknown"),
        "result_path": str(path),
        "reward": _float_or_none(rewards.get("reward")),
        "test_pass_rate": _float_or_none(rewards.get("test_pass_rate")),
        "valid": _bool_or_none(grading.get("valid")),
        "passed": _int_or_none(counts.get("passed")),
        "expected_total": _int_or_none(grading.get("expected_total")),
        "failure_class": failure_class,
        "failure_reason": failure_reason,
        "termination_reason": exception.get("exception_type"),
        "started_at": payload.get("started_at"),
        "finished_at": payload.get("finished_at"),
        "input_tokens": _int_or_none(_mapping(payload.get("agent_result")).get("n_input_tokens")),
        "output_tokens": _int_or_none(_mapping(payload.get("agent_result")).get("n_output_tokens")),
        "cost_usd": _float_or_none(_mapping(payload.get("agent_result")).get("cost_usd")),
    }


def load_results(roots: list[Path]) -> tuple[pl.DataFrame, list[dict[str, str]]]:
    """Load normalized trial rows and parse errors into a Polars DataFrame."""

    rows: list[dict[str, Any]] = []
    errors: list[dict[str, str]] = []
    for path in result_paths(roots):
        try:
            rows.append(normalize_result(path))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError, TypeError, ValueError) as exc:
            errors.append({"path": str(path), "error": str(exc)})
    return pl.DataFrame(rows), errors


def summarize_results(frame: pl.DataFrame) -> dict[str, Any]:
    """Compute valid-task macro scores and failure counts without raw-test weighting."""

    if frame.is_empty():
        return {"task_scores": [], "model_summary": [], "failure_summary": []}
    task_scores = (
        frame.filter(pl.col("valid") == True)  # noqa: E712
        .filter(pl.col("reward").is_not_null())
        .group_by(["model", "task_id"])
        .agg(
            pl.col("reward").mean().alias("task_score"),
            pl.len().alias("attempts"),
        )
        .sort(["model", "task_id"])
    )
    model_summary = (
        task_scores.group_by("model")
        .agg(
            pl.col("task_score").mean().alias("macro_task_score"),
            pl.len().alias("valid_tasks"),
            pl.col("attempts").sum().alias("valid_attempts"),
        )
        .sort("model")
    )
    failures = (
        frame.filter(~pl.col("valid").fill_null(False))
        .with_columns(
            pl.coalesce(
                [pl.col("failure_class"), pl.col("termination_reason"), pl.lit("unknown")]
            ).alias("classification")
        )
        .group_by("classification")
        .agg(pl.len().alias("trials"))
        .sort("classification")
    )
    return {
        "task_scores": task_scores.to_dicts(),
        "model_summary": model_summary.to_dicts(),
        "failure_summary": failures.to_dicts(),
    }


def _is_trial_result(path: Path) -> bool:
    """Distinguish Harbor trial results from job-level result.json files."""

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return True
    return isinstance(payload, dict) and "trial_name" in payload


def _canonical_task_id(task_name: object, fallback: str) -> str:
    """Normalize Harbor namespace-qualified names to catalog task IDs."""

    if isinstance(task_name, str) and task_name:
        return task_name.rsplit("/", 1)[-1]
    return fallback


def _mapping(value: object) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _read_grading(trial_dir: Path) -> dict[str, Any]:
    matches = sorted(
        path
        for path in trial_dir.rglob("grading.json")
        if path.is_file() and path.parent.name == "verifier"
    )
    if len(matches) != 1:
        return {}
    try:
        value = json.loads(matches[0].read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return {}
    return value if isinstance(value, dict) else {}


def _verifier_build_failure(exception: dict[str, Any]) -> bool:
    message = str(exception.get("exception_message") or "").casefold()
    return "docker compose command failed" in message or "failed to solve" in message


def _legacy_fable_empty_workspace(path: Path, model: str) -> bool:
    if model != "anthropic/claude-fable-5":
        return False
    log_path = path.parent / "agent" / "openhands_sdk.txt"
    try:
        log = log_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return False
    if "Error validating tool" not in log or "LLM produced empty" not in log:
        return False
    workspace = path.parent / "artifacts" / "workspace"
    if not workspace.is_dir():
        return True
    try:
        return not any(item.is_file() for item in workspace.rglob("*"))
    except OSError:
        return False


def _float_or_none(value: object) -> float | None:
    return float(value) if isinstance(value, (int, float)) else None


def _int_or_none(value: object) -> int | None:
    return int(value) if isinstance(value, (int, float)) else None


def _bool_or_none(value: object) -> bool | None:
    return value if isinstance(value, bool) else None


__all__ = ["load_results", "normalize_result", "result_paths", "summarize_results"]
