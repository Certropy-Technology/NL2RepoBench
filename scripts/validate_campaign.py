#!/usr/bin/env python3
"""Validate the evidence manifest for a package-to-Harbor campaign.

The campaign manifest is an index of evidence, not a replacement for catalog
source files.  Published status, language, revision, license, and Harbor
assets are read from the repository; the manifest supplies immutable
selection, Oracle/control, model-run, and archive references.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import sys
import tomllib
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

TARGET_MODELS = frozenset({"gpt-5.6-sol", "claude-fable-5"})
LANGUAGES = frozenset({"python", "node"})
SHA_PATTERN = re.compile(r"^(?:[0-9a-f]{40}|[0-9a-f]{64})$")
LICENSE_UNKNOWN = frozenset({"", "unknown", "unresolved", "NOASSERTION"})
ALLOWED_FAILURE_CLASSES = frozenset(
    {"source", "spec", "environment", "verifier", "model", "infrastructure"}
)
REQUIRED_CONTROLS = frozenset({"empty", "stub", "forgery", "timeout", "offline"})


def _read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"invalid JSON {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"JSON root must be an object: {path}")
    return value


def _read_toml(path: Path) -> dict[str, Any]:
    try:
        return tomllib.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, tomllib.TOMLDecodeError) as exc:
        raise ValueError(f"invalid TOML {path}: {exc}") from exc


def _parse_date(value: Any, field: str) -> datetime:
    if not isinstance(value, str):
        raise ValueError(f"{field} must be an ISO date")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"{field} must be an ISO date: {value}") from exc
    return parsed.replace(tzinfo=parsed.tzinfo or UTC)


def _months_old(as_of: datetime, activity: datetime) -> int:
    months = (as_of.year - activity.year) * 12 + as_of.month - activity.month
    if as_of.day < activity.day:
        months -= 1
    return months


def _required_dict(value: Any, field: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{field} must be an object")
    return value


def _campaign_root(path: Path) -> Path:
    return path.parent.parent if path.parent.name == "reports" else path.parent


def _validate_candidate(candidate: Any, *, as_of: datetime, task_id: str) -> None:
    data = _required_dict(candidate, f"tasks[{task_id}].candidate")
    source_kind = data.get("source_kind")
    if source_kind not in {"pypi", "npm", "github"}:
        raise ValueError(f"{task_id}: candidate.source_kind must be pypi, npm, or github")
    revision = data.get("revision")
    if not isinstance(revision, str) or SHA_PATTERN.fullmatch(revision) is None:
        raise ValueError(f"{task_id}: candidate.revision must be a complete immutable SHA")
    license_spdx = data.get("license_spdx")
    if not isinstance(license_spdx, str) or license_spdx in LICENSE_UNKNOWN:
        raise ValueError(f"{task_id}: candidate.license_spdx is unresolved")
    observed_at = _parse_date(data.get("observed_at"), f"{task_id}.candidate.observed_at")
    if observed_at > as_of:
        raise ValueError(f"{task_id}: candidate evidence is dated after campaign as_of")
    activity_value = data.get("last_activity") or data.get("last_release")
    activity = _parse_date(activity_value, f"{task_id}.candidate.last_activity")
    if activity > as_of:
        raise ValueError(f"{task_id}: candidate activity is dated after campaign as_of")
    if _months_old(as_of, activity) > 36:
        raise ValueError(f"{task_id}: candidate activity is older than 36 months")
    stars = data.get("stars")
    downloads = data.get("monthly_downloads")
    if not isinstance(stars, int) or stars < 0:
        raise ValueError(f"{task_id}: candidate.stars must be a non-negative integer")
    if not isinstance(downloads, int) or downloads < 0:
        raise ValueError(f"{task_id}: candidate.monthly_downloads must be non-negative")
    if stars < 100 and downloads < 1_000:
        raise ValueError(f"{task_id}: candidate does not meet stars/download threshold")
    evidence_url = data.get("evidence_url")
    if not isinstance(evidence_url, str) or not evidence_url.startswith("https://"):
        raise ValueError(f"{task_id}: candidate.evidence_url must be an HTTPS source")


def _validate_oracle(task: dict[str, Any], task_id: str) -> None:
    runs = task.get("oracle_runs")
    if not isinstance(runs, list) or len(runs) != 1:
        raise ValueError(f"{task_id}: oracle_runs must contain exactly one run")
    expected: int | None = None
    collections: set[int] = set()
    for index, raw in enumerate(runs):
        run = _required_dict(raw, f"{task_id}.oracle_runs[{index}]")
        if run.get("valid") is not True:
            raise ValueError(f"{task_id}: Oracle run {index + 1} is not valid")
        reward = run.get("reward")
        if (
            isinstance(reward, bool)
            or not isinstance(reward, (int, float))
            or not math.isfinite(float(reward))
            or not 0 <= reward <= 1
            or reward < 0.80
        ):
            raise ValueError(f"{task_id}: Oracle run {index + 1} is below reward 0.80")
        total = run.get("expected_total")
        collected = run.get("collected_total")
        if (
            isinstance(total, bool)
            or not isinstance(total, int)
            or total <= 0
            or isinstance(collected, bool)
            or not isinstance(collected, int)
        ):
            raise ValueError(f"{task_id}: Oracle run {index + 1} lacks collection evidence")
        if total != collected:
            raise ValueError(f"{task_id}: Oracle collection mismatch in run {index + 1}")
        oracle_ceiling = run.get("oracle_ceiling")
        failure_set = run.get("failure_set")
        if (
            isinstance(oracle_ceiling, bool)
            or not isinstance(oracle_ceiling, (int, float))
            or not math.isfinite(float(oracle_ceiling))
            or abs(float(oracle_ceiling) - float(reward)) > 1e-9
        ):
            raise ValueError(f"{task_id}: Oracle ceiling must equal the recorded reward")
        if not isinstance(failure_set, list) or not all(
            isinstance(item, str) and item for item in failure_set
        ):
            raise ValueError(f"{task_id}: Oracle failure_set must be a list of test IDs")
        if reward < 1.0 and not isinstance(run.get("reason"), str):
            raise ValueError(f"{task_id}: sub-1.0 Oracle requires a failure reason")
        if expected is None:
            expected = total
        elif expected != total:
            raise ValueError(f"{task_id}: Oracle frozen denominator changed across runs")
        collections.add(collected)
    if len(collections) != 1:
        raise ValueError(f"{task_id}: Oracle collection is unstable")


def _validate_controls(task: dict[str, Any], task_id: str) -> None:
    controls = _required_dict(task.get("controls"), f"tasks[{task_id}].controls")
    required_controls = set(REQUIRED_CONTROLS)
    if task.get("language") == "node":
        required_controls.update({"install-script", "loader-hook", "hang"})
    missing = required_controls - set(controls)
    if missing:
        raise ValueError(f"{task_id}: missing controls: {', '.join(sorted(missing))}")
    for name in sorted(required_controls):
        result = _required_dict(controls[name], f"{task_id}.controls.{name}")
        if result.get("passed") is not True:
            raise ValueError(f"{task_id}: control {name} did not pass")
        evidence = result.get("evidence")
        if not isinstance(evidence, list) or not evidence or not all(
            isinstance(item, str) and item for item in evidence
        ):
            raise ValueError(f"{task_id}: control {name} lacks evidence references")
        result_kind = result.get("result")
        if not isinstance(result_kind, str) or not result_kind:
            raise ValueError(f"{task_id}: control {name} lacks a structured result")
        if name in {"empty", "stub"}:
            reward = result.get("reward")
            if (
                isinstance(reward, bool)
                or not isinstance(reward, (int, float))
                or not math.isfinite(float(reward))
                or not 0 <= reward <= 0.20
            ):
                raise ValueError(f"{task_id}: control {name} reward is not near zero")
        elif name in {"forgery", "loader-hook", "offline"}:
            reward = result.get("reward")
            if (
                isinstance(reward, bool)
                or not isinstance(reward, (int, float))
                or not math.isfinite(float(reward))
                or not 0 <= reward < 1
            ):
                raise ValueError(f"{task_id}: control {name} was not bounded below a full score")
        else:
            if result.get("completed") is not True:
                raise ValueError(f"{task_id}: control {name} did not complete")


def _validate_model_runs(task: dict[str, Any], task_id: str) -> None:
    raw_runs = task.get("model_runs")
    if not isinstance(raw_runs, list):
        raise ValueError(f"{task_id}: model_runs must be a list")
    by_model: dict[str, dict[str, Any]] = {}
    for raw in raw_runs:
        run = _required_dict(raw, f"{task_id}.model_runs[]")
        model = run.get("model")
        if model not in {*TARGET_MODELS, "oracle"}:
            raise ValueError(f"{task_id}: unsupported model run: {model}")
        if model in by_model:
            raise ValueError(f"{task_id}: duplicate model run record: {model}")
        attempts = run.get("attempts")
        if not isinstance(attempts, int) or attempts < 1:
            raise ValueError(f"{task_id}: {model} must have at least one attempt")
        failure_class = run.get("failure_class")
        if failure_class is not None and failure_class not in ALLOWED_FAILURE_CLASSES:
            raise ValueError(f"{task_id}: invalid model failure class: {failure_class}")
        status = run.get("status")
        valid = run.get("valid")
        if status not in {"completed", "failed"} or not isinstance(valid, bool):
            raise ValueError(f"{task_id}: model {model} lacks coherent status/valid fields")
        if status == "completed" and (valid is not True or failure_class is not None):
            raise ValueError(f"{task_id}: completed model {model} must be valid without failure")
        if status == "failed" and (valid is not False or failure_class is None):
            raise ValueError(
                f"{task_id}: failed model {model} requires failure class and valid=false"
            )
        if attempts > 1 and failure_class != "infrastructure":
            raise ValueError(f"{task_id}: only infrastructure failures may be retried for {model}")
        by_model[model] = run
    missing = TARGET_MODELS - set(by_model)
    if missing:
        raise ValueError(f"{task_id}: missing model runs: {', '.join(sorted(missing))}")


def _validate_existing_oss_runs(task: dict[str, Any], task_id: str) -> None:
    refs = task.get("oss_run_refs")
    if not isinstance(refs, list) or not refs:
        raise ValueError(f"{task_id}: existing OSS task requires oss_run_refs")
    for index, raw in enumerate(refs):
        ref = _required_dict(raw, f"{task_id}.oss_run_refs[{index}]")
        if ref.get("source") != "oss":
            raise ValueError(f"{task_id}: OSS exemption reference is not OSS-backed")
        if ref.get("task_id") != task_id:
            raise ValueError(f"{task_id}: OSS exemption task_id mismatch")
        model = ref.get("model")
        if model not in TARGET_MODELS:
            raise ValueError(f"{task_id}: OSS exemption has unsupported model")
        if ref.get("status") not in {"completed", "errored"}:
            raise ValueError(f"{task_id}: OSS exemption run is not finished")
        evidence_keys = ref.get("evidence_keys")
        if not isinstance(evidence_keys, list) or not any(
            isinstance(key, str) and key.endswith("result.json") for key in evidence_keys
        ):
            raise ValueError(f"{task_id}: OSS exemption lacks result evidence")
        if ref.get("revision_binding") not in {"matched", "unbound-legacy"}:
            raise ValueError(f"{task_id}: OSS exemption lacks revision binding classification")
        prefix = ref.get("prefix")
        if not isinstance(prefix, str) or not prefix.startswith("nl2repobench/runs/"):
            raise ValueError(f"{task_id}: OSS exemption lacks a valid run prefix")


def validate_campaign(
    campaign_path: Path,
    *,
    catalog_root: Path,
    minimum_tasks: int = 500,
    allow_below_target: bool = False,
) -> dict[str, Any]:
    campaign = _read_json(campaign_path)
    if campaign.get("schema_version") != "1.0":
        raise ValueError("campaign schema_version must be 1.0")
    as_of = _parse_date(campaign.get("as_of"), "campaign.as_of")
    inventory_meta = campaign.get("oss_run_inventory")
    if inventory_meta is not None:
        inventory_meta = _required_dict(inventory_meta, "campaign.oss_run_inventory")
        inventory_value = inventory_meta.get("path")
        expected_digest = inventory_meta.get("sha256")
        if not isinstance(inventory_value, str) or not isinstance(expected_digest, str):
            raise ValueError("campaign OSS inventory requires path and sha256")
        inventory_path = (_campaign_root(campaign_path) / inventory_value).resolve()
        if not inventory_path.is_file():
            raise ValueError(f"campaign OSS inventory is missing: {inventory_path}")
        actual_digest = "sha256:" + hashlib.sha256(inventory_path.read_bytes()).hexdigest()
        if actual_digest != expected_digest:
            raise ValueError("campaign OSS inventory hash differs from campaign")
        inventory = _read_json(inventory_path)
        if inventory.get("source") != "oss":
            raise ValueError("campaign OSS inventory is not OSS-sourced")
    datasets = campaign.get("datasets")
    if not isinstance(datasets, list) or not datasets:
        raise ValueError("campaign.datasets must be a non-empty list")
    dataset_map: dict[str, dict[str, Any]] = {}
    languages: set[str] = set()
    for raw in datasets:
        dataset = _required_dict(raw, "campaign.datasets[]")
        dataset_id = dataset.get("dataset_id")
        language = dataset.get("language")
        if not isinstance(dataset_id, str) or not dataset_id:
            raise ValueError("campaign dataset_id must be non-empty")
        if language not in LANGUAGES:
            raise ValueError(f"dataset {dataset_id}: unsupported language {language}")
        if dataset_id in dataset_map:
            raise ValueError(f"duplicate dataset_id: {dataset_id}")
        dataset_map[dataset_id] = dataset
        languages.add(language)
    if len(languages) > 1 and len(dataset_map) == 1:
        raise ValueError("Python and Node tasks must use separate dataset records")

    raw_tasks = campaign.get("tasks")
    if not isinstance(raw_tasks, list):
        raise ValueError("campaign.tasks must be a list")
    task_ids: set[str] = set()
    valid_tasks: list[dict[str, Any]] = []
    errors: list[str] = []
    for raw in raw_tasks:
        try:
            task = _required_dict(raw, "campaign.tasks[]")
            task_id = task.get("task_id")
            if not isinstance(task_id, str) or not task_id:
                raise ValueError("task_id must be non-empty")
            if task_id in task_ids:
                raise ValueError("duplicate task_id")
            task_ids.add(task_id)
            dataset_id = task.get("dataset_id")
            if dataset_id not in dataset_map:
                raise ValueError("references an unknown dataset")
            language = task.get("language")
            if language != dataset_map[dataset_id].get("language"):
                raise ValueError("language does not match dataset")
            source_path = catalog_root / task_id / "task.toml"
            source = _read_toml(source_path)
            lifecycle = _required_dict(source.get("lifecycle"), f"{task_id}.lifecycle")
            if lifecycle.get("status") != "published":
                raise ValueError("catalog lifecycle is not published")
            metadata = _required_dict(source.get("metadata"), f"{task_id}.metadata")
            if metadata.get("language") != language:
                raise ValueError("catalog language does not match campaign")
            source_lock = _required_dict(source.get("source"), f"{task_id}.source")
            revision = source_lock.get("revision")
            if not isinstance(revision, str) or SHA_PATTERN.fullmatch(revision) is None:
                raise ValueError("catalog source revision is not immutable")
            if source_lock.get("license_spdx") in LICENSE_UNKNOWN:
                raise ValueError("catalog license is unresolved")
            candidate = _required_dict(task.get("candidate"), f"{task_id}.candidate")
            if candidate.get("revision") != revision:
                raise ValueError("candidate and catalog source revisions differ")
            if str(candidate.get("upstream_url", "")).rstrip("/") != str(
                source_lock.get("upstream_url", "")
            ).rstrip("/"):
                raise ValueError("candidate and catalog upstream URLs differ")
            harbor_task = catalog_root / task_id / "harbor/task.toml"
            if not harbor_task.is_file():
                raise ValueError("Harbor task bundle is missing")
            _validate_candidate(candidate, as_of=as_of, task_id=task_id)
            if task.get("existing_oss") is True:
                _validate_existing_oss_runs(task, task_id)
            else:
                _validate_oracle(task, task_id)
                _validate_model_runs(task, task_id)
            _validate_controls(task, task_id)
            valid_tasks.append(task)
        except (OSError, ValueError) as exc:
            label = raw.get("task_id", "<unknown>") if isinstance(raw, dict) else "<unknown>"
            errors.append(f"{label}: {exc}")
    if errors:
        raise ValueError("campaign validation errors:\n" + "\n".join(errors))
    if len(valid_tasks) < minimum_tasks and not allow_below_target:
        raise ValueError(
            f"publishable task count {len(valid_tasks)} is below required minimum {minimum_tasks}"
        )
    return {
        "schema_version": "1.0",
        "campaign_id": campaign.get("campaign_id"),
        "as_of": campaign["as_of"],
        "task_count": len(valid_tasks),
        "minimum_tasks": minimum_tasks,
        "status": "releaseable" if len(valid_tasks) >= minimum_tasks else "below-target",
        "dataset_count": len(dataset_map),
        "languages": sorted(languages),
        "new_task_count": campaign.get("new_task_count"),
        "archive": campaign.get("archive"),
        "tasks": [task["task_id"] for task in valid_tasks],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("campaign", type=Path)
    parser.add_argument("--catalog-root", type=Path, default=Path("catalog/tasks"))
    parser.add_argument("--minimum-tasks", type=int, default=500)
    parser.add_argument("--allow-below-target", action="store_true")
    args = parser.parse_args()
    try:
        report = validate_campaign(
            args.campaign,
            catalog_root=args.catalog_root,
            minimum_tasks=args.minimum_tasks,
            allow_below_target=args.allow_below_target,
        )
    except ValueError as exc:
        print(f"campaign validation failed: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
