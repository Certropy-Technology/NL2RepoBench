# ruff: noqa: E501
"""Auditable, read-only-by-default import of the Phase 1 authoring tree.

The manifest is deliberately a closed list of authorities.  It is not a
compatibility reader for the live loop and it never creates controllers for
owners found in old claim files.
"""
from __future__ import annotations

import hashlib
import json
import re
import stat as statmod
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, cast

from .scheduler import Scheduler

MANIFEST_SCHEMA = "authoring-live-manifest/v2"
_SHA = re.compile(r"^[0-9a-f]{64}$")
_SECRET = re.compile(
    r"(?:BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY|(?:api[_-]?key|secret|password|token)\s*[:=])",
    re.I,
)
_STATUS = {
    "pending": "pending", "claimed": "claimed", "preparing": "preparing",
    "authoring": "authoring", "handoff_ready": "handoff_ready", "stale": "stale",
    "integrating": "integrating", "integration_retry": "integration_retry",
    "archiving": "archiving", "archive_retry": "archive_retry", "cleaning": "cleaning",
    "cleanup_retry": "cleanup_retry", "complete": "complete", "blocked": "blocked",
    "excluded": "excluded", "cancelled": "cancelled",
    "running": "authoring", "released": "stale",
}


class MigrationError(ValueError):
    """A manifest, source, or import invariant failed."""


@dataclass(frozen=True)
class ManifestLane:
    lane_id: str
    batch_id: str
    language: str
    kind: str
    queue_source: str
    state_authority: str
    plan_source: str | None = None

    def as_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "lane_id": self.lane_id, "batch_id": self.batch_id, "language": self.language,
            "kind": self.kind, "queue_source": self.queue_source,
            "state_authority": self.state_authority,
        }
        if self.plan_source is not None:
            result["plan_source"] = self.plan_source
        return result


def _sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _relative(root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError as exc:
        raise MigrationError(f"path escapes authoring root: {path}") from exc


def _check_file(root: Path, relative: str, *, max_size: int = 64 * 1024 * 1024,
                allow_external: bool = False) -> dict[str, Any]:
    location = Path(relative)
    if location.is_absolute() and not allow_external:
        raise MigrationError(f"non-contained manifest path: {relative}")
    raw_path = location if location.is_absolute() else root / location
    if raw_path.is_symlink():
        raise MigrationError(f"symlink authority is forbidden: {relative}")
    path = location.resolve() if location.is_absolute() else raw_path
    if not location.is_absolute() and ".." in location.parts:
        raise MigrationError(f"non-contained manifest path: {relative}")
    # lstat every component: resolving a symlink is not an acceptable authority.
    if location.is_absolute():
        cursor = path
        while cursor != cursor.parent:
            if cursor.is_symlink():
                raise MigrationError(f"symlink authority is forbidden: {relative}")
            cursor = cursor.parent
    else:
        cursor = root
        for part in location.parts:
            cursor /= part
            if cursor.is_symlink():
                raise MigrationError(f"symlink authority is forbidden: {relative}")
    try:
        stat = path.stat()
    except FileNotFoundError as exc:
        raise MigrationError(f"missing authority: {relative}") from exc
    if not path.is_file() or not statmod.S_ISREG(stat.st_mode):
        raise MigrationError(f"authority is not a regular file: {relative}")
    if stat.st_size > max_size:
        raise MigrationError(f"authority exceeds size limit: {relative}")
    if stat.st_mode & 0o022:
        raise MigrationError(f"authority is group/world writable: {relative}")
    raw = path.read_bytes()
    if _SECRET.search(raw.decode("utf-8", errors="replace")):
        raise MigrationError(f"secret-shaped authority: {relative}")
    return {"path": relative, "mode": stat.st_mode & 0o777, "size": stat.st_size, "sha256": _sha(path)}


def _json_file(root: Path, relative: str, *, allow_external: bool = False) -> dict[str, Any]:
    record = _check_file(root, relative, allow_external=allow_external)
    try:
        location = Path(relative)
        path = location if location.is_absolute() else root / location
        json.loads(path.read_text(encoding="utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise MigrationError(f"invalid JSON authority: {relative}") from exc
    return record


def _lane_from_path(root: Path, path: Path, *, kind: str, language: str, source: str,
                    plan: str | None, state: str | None = None) -> ManifestLane:
    batch = path.stem
    return ManifestLane(f"{kind}-{language}-{batch}", batch, language, kind, source,
                        state or f"state/{batch}", plan)


def generate_manifest(live_root: Path | str, *, cutover_id: str) -> dict[str, Any]:
    """Generate the seven Phase 1 authorities without touching them."""
    root = Path(live_root).expanduser().resolve()
    if not cutover_id or cutover_id.lower() == "current" or not re.fullmatch(r"[A-Za-z0-9._:-]{1,200}", cutover_id):
        raise MigrationError("cutover_id must be explicit and immutable (not current)")
    lanes: list[ManifestLane] = []
    plans = root / "plans"
    queues = root / "queues"
    for plan in sorted(plans.glob("*-wave2-*.json")):
        batch = plan.stem
        queue_batch = batch.replace("-author-wave2-", "-wave2-")
        state = queues / f"{queue_batch}.json"
        language = batch.split("-", 1)[0]
        if language not in {"python", "node", "go"} or not state.exists():
            continue
        descriptor = json.loads(plan.read_text(encoding="utf-8"))
        source = str(descriptor.get("candidate_input", ""))
        if not source:
            raise MigrationError(f"base plan has no external queue: {plan.name}")
        lanes.append(_lane_from_path(root, plan, kind="base", language=language,
                                     source=source, plan=_relative(root, plan),
                                     state=_relative(root, state)))
    generated = root / "supervisor" / "generated-lanes.json"
    if generated.exists():
        try:
            descriptors = json.loads(generated.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise MigrationError("invalid generated-lanes.json") from exc
        for descriptor in descriptors:
            batch = str(descriptor["batch_id"])
            language = str(descriptor["language"])
            source_path = Path(str(descriptor["queue"]))
            if source_path.is_absolute():
                source_path = Path(_relative(root, source_path))
            state_path = Path(str(descriptor.get("queue_state", f"state/{batch}")))
            if state_path.is_absolute():
                state_path = Path(_relative(root, state_path))
            plan_source = str(descriptor.get("plan", "")) or None
            if plan_source is not None and Path(plan_source).is_absolute():
                plan_source = _relative(root, Path(plan_source))
            lanes.append(ManifestLane(f"generated-{language}-{batch}", batch, language, "generated",
                                      source_path.as_posix(), state_path.as_posix(),
                                      plan_source))
    if len(lanes) != 7:
        raise MigrationError(f"expected exactly seven lane authorities, found {len(lanes)}")
    records: list[dict[str, Any]] = []
    for lane in lanes:
        item = lane.as_dict()
        item["queue"] = _json_file(root, lane.queue_source, allow_external=lane.kind == "base")
        state_dir = root / lane.state_authority
        if state_dir.is_file():
            state_files = [_json_file(root, lane.state_authority)]
        else:
            if state_dir.is_symlink() or not state_dir.is_dir():
                raise MigrationError(f"missing or symlinked state authority: {lane.state_authority}")
            state_files = []
            for state_file in sorted(state_dir.glob("claims/*.json")):
                state_files.append(_json_file(root, _relative(root, state_file)))
        claim_dir = root / "state" / lane.batch_id / "claims"
        if claim_dir.is_dir():
            known = {record["path"] for record in state_files}
            for claim_file in sorted(claim_dir.glob("*.json")):
                relative = _relative(root, claim_file)
                if relative not in known:
                    state_files.append(_json_file(root, relative))
        item["state"] = {"path": lane.state_authority, "files": state_files}
        if lane.plan_source:
            item["plan"] = _json_file(root, lane.plan_source, allow_external=lane.kind == "generated")
        records.append(item)
    registry = _json_file(root, "supervisor/generated-lanes.json")
    manifest: dict[str, Any] = {
        "schema_version": MANIFEST_SCHEMA, "cutover_id": cutover_id,
        "root_name": root.name, "lanes": records,
        "generated_at": None,
        "registry": registry,
    }
    inventory: list[dict[str, Any]] = []
    inventory_roots = ["plans", "queues", "state", "supervisor", "archive-receipts", "logs", "pids"]
    for directory in inventory_roots:
        base = root / directory
        if base.is_dir():
            for path in sorted(p for p in base.rglob("*") if p.is_file()):
                inventory.append(_check_file(root, _relative(root, path)))
    for filename in ("supervisor.pid", "supervisor.lock", "archive.lock"):
        path = root / filename
        if path.exists():
            inventory.append(_check_file(root, filename))
    for record in records:
        if Path(record["queue_source"]).is_absolute():
            inventory.append(_check_file(root, record["queue_source"], allow_external=True))
    manifest["inventory"] = inventory
    encoded = json.dumps(manifest, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()
    manifest["manifest_sha256"] = hashlib.sha256(encoded).hexdigest()
    return manifest


def validate_manifest(manifest: dict[str, Any], live_root: Path | str) -> None:
    if manifest.get("schema_version") != MANIFEST_SCHEMA:
        raise MigrationError("unsupported authoring-live manifest schema")
    if not manifest.get("cutover_id") or str(manifest["cutover_id"]).lower() == "current":
        raise MigrationError("manifest requires immutable cutover_id")
    lanes = manifest.get("lanes")
    if not isinstance(lanes, list) or len(lanes) != 7:
        raise MigrationError("manifest must contain exactly seven lanes")
    required_top = {"schema_version", "cutover_id", "root_name", "lanes", "generated_at",
                    "registry", "inventory", "manifest_sha256"}
    if set(manifest) != required_top:
        raise MigrationError("manifest schema has missing or extra fields")
    supplied_digest = manifest["manifest_sha256"]
    unsigned = {key: value for key, value in manifest.items() if key != "manifest_sha256"}
    recomputed = hashlib.sha256(json.dumps(unsigned, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()).hexdigest()
    if supplied_digest != recomputed:
        raise MigrationError("manifest digest mismatch")
    if manifest.get("generated_at") is not None:
        raise MigrationError("generated_at must be null in a frozen manifest")
    root = Path(live_root).resolve()
    registry = _json_file(root, "supervisor/generated-lanes.json")
    if not isinstance(manifest.get("registry"), dict):
        raise MigrationError("manifest registry inventory is malformed")
    if manifest["registry"].get("sha256") != registry["sha256"]:
        raise MigrationError("generated-lanes registry hash drift")
    try:
        registry_payload = json.loads((root / "supervisor/generated-lanes.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise MigrationError("generated-lanes registry is invalid") from exc
    registry_lanes: set[tuple[str, str, str, str, str]] = set()
    for descriptor in registry_payload:
        queue = Path(str(descriptor["queue"]))
        state = Path(str(descriptor["queue_state"]))
        plan = Path(str(descriptor["plan"]))
        registry_lanes.add((str(descriptor["batch_id"]), str(descriptor["language"]),
                            _relative(root, queue) if queue.is_absolute() else queue.as_posix(),
                            _relative(root, state) if state.is_absolute() else state.as_posix(),
                            _relative(root, plan) if plan.is_absolute() else plan.as_posix()))
    inventory = manifest.get("inventory")
    if not isinstance(inventory, list) or not inventory:
        raise MigrationError("manifest file inventory is required")
    declared_paths: set[str] = set()
    for record in inventory:
        if not isinstance(record, dict) or not isinstance(record.get("path"), str):
            raise MigrationError("malformed inventory record")
        location = str(record["path"])
        actual = _check_file(root, location, allow_external=Path(location).is_absolute())
        if record.get("sha256") != actual["sha256"] or record.get("size") != actual["size"] or record.get("mode") != actual["mode"]:
            raise MigrationError(f"inventory drift: {location}")
        declared_paths.add(location)
    expected_paths: set[str] = set()
    for directory in ("plans", "queues", "state", "supervisor", "archive-receipts", "logs", "pids"):
        base = root / directory
        if base.is_dir():
            expected_paths.update(_relative(root, path) for path in base.rglob("*") if path.is_file())
    expected_paths.update(filename for filename in ("supervisor.pid", "supervisor.lock", "archive.lock") if (root / filename).is_file())
    expected_paths.update(str(lane["queue_source"]) for lane in lanes if Path(str(lane["queue_source"])).is_absolute())
    if declared_paths != expected_paths:
        raise MigrationError("manifest file inventory set drift")
    seen: set[str] = set()
    kinds: dict[str, int] = {"base": 0, "generated": 0}
    batches: set[str] = set()
    for lane in lanes:
        if not isinstance(lane, dict) or lane.get("lane_id") in seen:
            raise MigrationError("duplicate or malformed lane")
        if set(lane) != {"lane_id", "batch_id", "language", "kind", "queue_source",
                         "state_authority", "queue", "state"} | ({"plan_source", "plan"} if lane.get("kind") == "base" else {"plan_source", "plan"}):
            raise MigrationError("lane schema has missing or extra fields")
        seen.add(str(lane.get("lane_id")))
        language, kind, batch = lane.get("language"), lane.get("kind"), lane.get("batch_id")
        if language not in {"python", "node", "go"} or kind not in kinds or not isinstance(batch, str) or batch in batches:
            raise MigrationError("invalid lane topology")
        batches.add(batch)
        kinds[str(kind)] += 1
        for key in ("queue_source", "state_authority"):
            value = lane.get(key)
            external = key == "queue_source" and kind == "base"
            if not isinstance(value, str) or (Path(value).is_absolute() and not external) or (not Path(value).is_absolute() and ".." in Path(value).parts):
                raise MigrationError(f"invalid {key}")
        queue_record = _json_file(root, str(lane["queue_source"]), allow_external=kind == "base")
        declared = lane.get("queue")
        if not isinstance(declared, dict) or declared.get("sha256") != queue_record["sha256"]:
            raise MigrationError(f"hash drift: {lane['queue_source']}")
        if lane.get("plan_source"):
            plan_record = _json_file(root, str(lane["plan_source"]), allow_external=kind == "generated")
            declared_plan = lane.get("plan")
            if not isinstance(declared_plan, dict) or declared_plan.get("sha256") != plan_record["sha256"]:
                raise MigrationError(f"hash drift: {lane['plan_source']}")
        queue_source = str(lane["queue_source"])
        state_source = str(lane["state_authority"])
        plan_source = str(lane["plan_source"])
        if kind == "base" and (not Path(queue_source).is_absolute()
                                or not state_source.startswith("queues/")
                                or not plan_source.startswith("plans/")):
            raise MigrationError("base lane authority relationship is invalid")
        if kind == "generated" and (not queue_source.startswith("supervisor/queues/")
                                     or not state_source.startswith("queues/")
                                     or not plan_source.startswith("plans/")):
            raise MigrationError("generated lane authority relationship is invalid")
        state = lane.get("state", {})
        if not isinstance(state, dict) or state.get("path") != lane["state_authority"] or not isinstance(state.get("files"), list):
            raise MigrationError("state inventory is incomplete")
        actual_state_paths = {str(record.get("path")) for record in state["files"] if isinstance(record, dict)}
        expected_state_paths = {str(lane["state_authority"])}
        claim_dir = root / "state" / str(lane["batch_id"]) / "claims"
        if claim_dir.is_dir():
            expected_state_paths.update(_relative(root, path) for path in claim_dir.glob("*.json"))
        if actual_state_paths != expected_state_paths:
            raise MigrationError(f"state file set drift: {lane['batch_id']}")
        for record in state.get("files", []):
            if not isinstance(record, dict) or record.get("path") is None:
                raise MigrationError("malformed state record")
            actual = _json_file(root, str(record["path"]))
            if record.get("sha256") != actual["sha256"]:
                raise MigrationError(f"hash drift: {record['path']}")
    if kinds != {"base": 3, "generated": 4}:
        raise MigrationError("manifest must contain three base and four generated lanes")
    actual_generated = {(str(lane["batch_id"]), str(lane["language"]), str(lane["queue_source"]), str(lane["state_authority"]), str(lane["plan_source"])) for lane in lanes if lane["kind"] == "generated"}
    if actual_generated != registry_lanes:
        raise MigrationError("generated lane descriptors do not match frozen registry")


def _classify_failure(item: dict[str, Any]) -> str | None:
    value = item.get("failure_class")
    allowed = {"source", "spec", "environment", "verifier", "model", "infrastructure"}
    if value in allowed:
        return str(value)
    reason = str(item.get("reason") or item.get("error") or "").lower()
    if any(word in reason for word in ("collision", "already exists", "remote object")):
        return "infrastructure"
    if any(word in reason for word in ("timeout", "disk", "docker", "network", "process")):
        return "infrastructure"
    if any(word in reason for word in ("license", "revision", "source")):
        return "source"
    if any(word in reason for word in ("verifier", "test", "manifest")):
        return "verifier"
    return "infrastructure" if value else None


def classify_integration_failure(value: str | dict[str, Any]) -> str:
    """Classify legacy failures without retrying or deleting collision records."""
    item = value if isinstance(value, dict) else {"reason": value}
    result = _classify_failure(item)
    if result:
        return result
    reason = str(item.get("reason") or item.get("error") or "").lower()
    if any(word in reason for word in ("source", "license", "revision")):
        return "source"
    if any(word in reason for word in ("verifier", "test", "manifest")):
        return "verifier"
    return "infrastructure"


def _has_final_receipt_chain(item: dict[str, Any]) -> bool:
    receipts = item.get("receipts", item.get("operation_receipts", []))
    if not isinstance(receipts, list):
        return False
    completed = {(str(r.get("operation_kind", r.get("kind", ""))), str(r.get("status", "")))
                for r in receipts if isinstance(r, dict) and _receipt_contract_valid(r)}
    return {("integration", "pushed"), ("archive", "verified"), ("cleanup", "applied")} <= completed


def _receipt_contract_valid(receipt: dict[str, Any]) -> bool:
    operation = str(receipt.get("operation_kind", receipt.get("kind", "")))
    status = str(receipt.get("status", ""))
    if status == "pushed":
        return operation == "integration" and bool(receipt.get("external_ref")) and bool(re.fullmatch(r"[0-9a-f]{40}", str(receipt.get("commit_sha", ""))))
    if status == "verified":
        return operation == "archive" and bool(receipt.get("manifest_key")) and all(_SHA.fullmatch(str(receipt.get(key, ""))) for key in ("manifest_sha256", "source_snapshot_sha256", "evidence_sha256")) and int(receipt.get("object_count", 0) or 0) > 0 and int(receipt.get("byte_count", 0) or 0) > 0
    if status == "applied":
        return operation == "cleanup" and bool(receipt.get("evidence_path")) and bool(_SHA.fullmatch(str(receipt.get("evidence_sha256", ""))))
    return False


def import_manifest(manifest: dict[str, Any], live_root: Path | str, *, db_path: Path | str | None = None,
                    dry_run: bool = True, barrier: Any = None) -> dict[str, Any]:
    """Import into a temporary scheduler DB; ``dry_run=False`` still requires a temp DB."""
    validate_manifest(manifest, live_root)
    root = Path(live_root).resolve()
    observed_barrier = barrier() if barrier is not None else barrier_check(root, manifest=manifest)
    if not isinstance(observed_barrier, dict) or observed_barrier.get("stopped") is not False:
        raise MigrationError("mandatory migration barrier did not complete as observe-only")
    temp_dir: tempfile.TemporaryDirectory[str] | None = None
    if dry_run or db_path is None:
        temp_dir = tempfile.TemporaryDirectory(prefix="authoring-import-")
        db = Path(temp_dir.name) / "scheduler.sqlite3"
    else:
        db = Path(db_path).resolve()
        if root == db or root in db.parents:
            raise MigrationError("import DB must not be the live authoring tree")
        if db.exists() or Path(str(db) + "-wal").exists() or Path(str(db) + "-shm").exists():
            raise MigrationError("import staging database must be fresh")
    db.parent.mkdir(parents=True, exist_ok=True)
    scheduler = Scheduler(db, supplied_root=db.parent)
    scheduler.init()
    conn = scheduler._import_connection()
    counts: dict[str, int] = {}
    committed = False
    try:
        conn.execute("BEGIN IMMEDIATE")
        conn.execute("INSERT OR REPLACE INTO schema_meta(key,value) VALUES('import_mode','1')")
        for lane in manifest["lanes"]:
            lane_id = str(lane["lane_id"])
            kind, language = str(lane["kind"]), str(lane["language"])
            conn.execute("INSERT OR IGNORE INTO lanes(lane_id,batch_id,language,kind,status,queue_path,queue_sha256,plan_path,plan_sha256,state_path,state_sha256,source_reports_json,fairness_rank,last_dispatch_seq,created_at,updated_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,datetime('now'),datetime('now'))",
                         (lane_id, lane["batch_id"], language, kind, "active", lane["queue_source"], lane["queue"]["sha256"], lane.get("plan_source", "plan.json"), (lane.get("plan") or {}).get("sha256", "0"*64), lane["state_authority"], None, "[]", 0, 0))
            queue_path = Path(str(lane["queue_source"]))
            queue_data = json.loads((queue_path if queue_path.is_absolute() else root / queue_path).read_text(encoding="utf-8"))
            state_path = Path(str(lane["state_authority"]))
            state_data: dict[str, Any] = {}
            if (root / state_path).is_file():
                state_data = json.loads((root / state_path).read_text(encoding="utf-8"))
            state_items = state_data.get("items", {}) if isinstance(state_data, dict) else {}
            queue_items = queue_data.get("queue", []) if isinstance(queue_data, dict) else []
            if not isinstance(queue_items, list):
                raise MigrationError("immutable queue authority must contain top-level queue list")
            items = {}
            for candidate in queue_items:
                if isinstance(candidate, dict) and candidate.get("candidate_id"):
                    candidate_key = str(candidate["candidate_id"])
                    merged = dict(candidate)
                    if isinstance(state_items, dict) and isinstance(state_items.get(candidate_key), dict):
                        merged.update(state_items[candidate_key])
                    items[candidate_key] = merged
            for candidate_id, item in items.items():
                if not isinstance(item, dict):
                    continue
                package = str(item.get("package") or candidate_id)
                selection = cast(dict[str, Any], item.get("selection")) if isinstance(item.get("selection"), dict) else {}
                revision = str(selection.get("revision") or "0" * 40)
                if len(revision) != 40:
                    revision = "0" * 40
                upstream = str(selection.get("upstream_url") or item.get("upstream_url") or "unknown")
                digest = hashlib.sha256(json.dumps({"package": package, "revision": revision, "upstream": upstream}, sort_keys=True).encode()).hexdigest()
                conn.execute("INSERT OR IGNORE INTO candidate_identities VALUES(?,?,?,?,?,?,?,datetime('now'))", (digest, language, package, upstream, str(selection.get("source_kind", "legacy")), revision, json.dumps(selection, sort_keys=True)))
                conn.execute("INSERT OR IGNORE INTO candidates VALUES(?,?,?,?,?,?,datetime('now'),datetime('now'))", (candidate_id, lane_id, digest, int(item.get("ordinal", 0) or 0), "existing" if item.get("status") == "complete" else "candidate", json.dumps({"legacy_status": item.get("status"), "legacy": item}, sort_keys=True)))
                task_id = f"{lane_id}:{candidate_id}:legacy"
                legacy_status = str(item.get("status", "pending"))
                state = _STATUS.get(legacy_status, "blocked")
                if legacy_status == "complete" and not _has_final_receipt_chain(item):
                    state = "handoff_ready"
                failure = _classify_failure(item)
                reason = str(item.get("reason") or item.get("release_reason") or "legacy import")
                terminal = reason if state in {"complete", "blocked", "excluded", "cancelled"} else None
                attempt_limit = max(1, int(item.get("attempt_limit", 3) or 3))
                attempts = min(attempt_limit, max(0, int(item.get("attempts", item.get("authoring_attempts", 0)) or 0)))
                retry_limit = max(0, int(item.get("retry_limit", 3) or 0))
                retry_count = min(retry_limit, max(0, int(item.get("retry_count", item.get("retries", 0)) or 0)))
                release_limit = max(0, int(item.get("release_limit", 3) or 0))
                release_count = min(release_limit, max(0, int(item.get("release_count", item.get("releases", 0)) or 0)))
                conn.execute("INSERT OR IGNORE INTO tasks(task_id,candidate_id,lane_id,task_release,state,attempt_limit,authoring_attempts,retry_limit,retry_count,release_count,release_limit,integration_attempts,integration_retry_count,integration_retry_limit,archive_attempts,archive_retry_count,archive_retry_limit,cleanup_attempts,cleanup_retry_count,cleanup_retry_limit,input_ordinal,last_failure_class,last_failure_reason,terminal_reason,created_at,updated_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,datetime('now'),datetime('now'))",
                             (task_id, candidate_id, lane_id, "legacy", state, attempt_limit, attempts, retry_limit, retry_count, release_count, release_limit, int(item.get("integration_attempts", 0) or 0), int(item.get("integration_retry_count", 0) or 0), max(0, int(item.get("integration_retry_limit", 3) or 0)), int(item.get("archive_attempts", 0) or 0), int(item.get("archive_retry_count", 0) or 0), max(0, int(item.get("archive_retry_limit", 3) or 0)), int(item.get("cleanup_attempts", 0) or 0), int(item.get("cleanup_retry_count", 0) or 0), max(0, int(item.get("cleanup_retry_limit", 3) or 0)), int(item.get("ordinal", 0) or 0), failure, reason if failure else None, terminal))
                for artifact in item.get("artifacts", []) if isinstance(item.get("artifacts"), list) else []:
                    artifact_path = str(artifact.get("path", "")) if isinstance(artifact, dict) else str(artifact)
                    artifact_digest = str(artifact.get("sha256", "")) if isinstance(artifact, dict) else ""
                    candidate_path = Path(artifact_path)
                    if candidate_path.is_file() and not candidate_path.is_symlink():
                        artifact_digest = _sha(candidate_path)
                        artifact_size = candidate_path.stat().st_size
                        scan = "passed"
                    else:
                        artifact_size = int(artifact.get("size_bytes", 0)) if isinstance(artifact, dict) else 0
                        scan = "not-run"
                    if _SHA.fullmatch(artifact_digest):
                        conn.execute("INSERT OR IGNORE INTO artifacts(artifact_id,task_id,trial_id,kind,path,sha256,size_bytes,secret_scan_status,created_at) VALUES(?,?,?,?,?,?,? ,?,datetime('now'))", (f"legacy:{artifact_digest}:{task_id}", task_id, None, "legacy-reference", artifact_path, artifact_digest, artifact_size, scan))
                receipts = item.get("receipts", item.get("operation_receipts", []))
                if isinstance(receipts, list):
                    for index, receipt in enumerate(receipts):
                        if not isinstance(receipt, dict):
                            continue
                        operation = str(receipt.get("operation_kind", receipt.get("kind", "")))
                        status = str(receipt.get("status", "failed"))
                        if operation not in {"integration", "archive", "cleanup"} or status not in {"started", "committed", "pushed", "verified", "applied", "failed", "collision"}:
                            continue
                        receipt_id = f"legacy:{task_id}:{operation}:{index}"
                        fields = dict(receipt)
                        fields.pop("operation_kind", None)
                        idempotency = "legacy:" + hashlib.sha256(json.dumps(receipt, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
                        conn.execute("INSERT OR IGNORE INTO operation_receipts(receipt_id,task_id,operation_kind,operation_attempt,retry_no,idempotency_key,status,source_digest,generated_digest,commit_sha,external_ref,manifest_key,manifest_sha256,source_snapshot_sha256,object_count,byte_count,evidence_path,evidence_sha256,actor_scope,actor_lease_id,failure_class,failure_reason,receipt_json,started_at,created_at,updated_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,datetime('now'),datetime('now'),datetime('now'))", (receipt_id, task_id, operation, int(receipt.get("operation_attempt", 1) or 1), int(receipt.get("retry_no", 0) or 0), idempotency, status, receipt.get("source_digest"), receipt.get("generated_digest"), receipt.get("commit_sha"), receipt.get("external_ref"), receipt.get("manifest_key"), receipt.get("manifest_sha256"), receipt.get("source_snapshot_sha256"), receipt.get("object_count"), receipt.get("byte_count"), receipt.get("evidence_path"), receipt.get("evidence_sha256"), receipt.get("actor_scope", "archive" if operation == "archive" else "integration"), "legacy-import", receipt.get("failure_class"), receipt.get("failure_reason"), json.dumps(fields, sort_keys=True)))
                counts[state] = counts.get(state, 0) + 1
        # Claim files are evidence only.  Importing owner/controller rows would fabricate live actors.
        for lane in manifest["lanes"]:
            for record in lane["state"].get("files", []):
                path = root / record["path"]
                try:
                    payload = json.loads(path.read_text(encoding="utf-8"))
                except (OSError, json.JSONDecodeError):
                    payload = {}
                claim = payload.get("claim", payload) if isinstance(payload, dict) else {}
                owner = str(claim.get("owner") or claim.get("owner_uuid") or "")
                if owner:
                    conn.execute("INSERT OR IGNORE INTO legacy_actor_evidence VALUES(?,?,?,?,?,?,?,?,?,datetime('now'))", (f"{lane['batch_id']}:{path.stem}", record["path"], owner, str(claim.get("pid") or ""), str(claim.get("starttime") or ""), str(claim.get("boot_id") or ""), str(lane["batch_id"]), record["sha256"], "historical-owner"))
                else:
                    conn.execute("INSERT OR IGNORE INTO orphan_claim_evidence VALUES(?,?,?,?,?,?,?,?,?,?,?,datetime('now'))", (f"{lane['batch_id']}:{path.stem}", record["path"], str(claim.get("candidate_id") or ""), str(claim.get("package") or ""), owner, str(claim.get("status") or ""), str(claim.get("lease_expires_at") or ""), str(claim.get("attempts") or ""), record["sha256"], "orphan-claim", "legacy claim evidence; no live controller imported"))
        failures = root / "supervisor" / "integration-failures.json"
        if failures.is_file():
            try:
                payload = json.loads(failures.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                payload = {}
            if isinstance(payload, dict):
                for package, failure in payload.items():
                    classification = classify_integration_failure(failure if isinstance(failure, dict) else str(failure))
                    reason = json.dumps(failure, sort_keys=True)
                    raw_digest = hashlib.sha256(reason.encode()).hexdigest()
                    conn.execute("INSERT OR IGNORE INTO orphan_claim_evidence VALUES(?,?,?,?,?,?,?,?,?,?,?,datetime('now'))", (f"integration-failure:{package}", "supervisor/integration-failures.json", "", str(package), "", "", "", "", raw_digest, "unmapped-claim", f"legacy integration failure classification={classification}; collision cleanup forbidden"))
                    if "collision" in reason.lower() or "remote object" in reason.lower():
                        task = conn.execute("SELECT t.task_id FROM tasks t JOIN candidates c ON c.candidate_id=t.candidate_id AND c.lane_id=t.lane_id JOIN candidate_identities i ON i.identity_digest=c.identity_digest WHERE i.package=? LIMIT 1", (package,)).fetchone()
                        if task is not None:
                            conn.execute("INSERT OR IGNORE INTO operation_receipts(receipt_id,task_id,operation_kind,operation_attempt,retry_no,idempotency_key,status,failure_class,failure_reason,evidence_path,evidence_sha256,actor_scope,actor_lease_id,receipt_json,started_at,created_at,updated_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,datetime('now'),datetime('now'),datetime('now'))", (f"legacy-collision:{package}", task["task_id"], "archive", 1, 0, "legacy-collision:" + raw_digest, "collision", "infrastructure", reason, "supervisor/integration-failures.json", raw_digest, "archive", "legacy-import", reason))
        for record in manifest.get("inventory", []):
            path_name = str(record.get("path", "")) if isinstance(record, dict) else ""
            if not path_name.startswith("archive-receipts/") or not path_name.endswith(".json"):
                continue
            receipt_path = root / path_name
            try:
                archive = json.loads(receipt_path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            if not isinstance(archive, dict) or not archive.get("package"):
                continue
            task = conn.execute("SELECT t.task_id FROM tasks t JOIN candidates c ON c.candidate_id=t.candidate_id AND c.lane_id=t.lane_id JOIN candidate_identities i ON i.identity_digest=c.identity_digest WHERE i.package=? LIMIT 1", (archive["package"],)).fetchone()
            if task is None or not archive.get("handoff_sha256"):
                continue
            raw_digest = _sha(receipt_path)
            objects = archive.get("objects", [])
            idempotency = "legacy:" + hashlib.sha256(receipt_path.read_bytes()).hexdigest()
            conn.execute("INSERT OR IGNORE INTO operation_receipts(receipt_id,task_id,operation_kind,operation_attempt,retry_no,idempotency_key,status,manifest_key,manifest_sha256,source_snapshot_sha256,object_count,byte_count,evidence_path,evidence_sha256,actor_scope,actor_lease_id,receipt_json,started_at,created_at,updated_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,datetime('now'),datetime('now'),datetime('now'))", (f"legacy-archive:{path_name}", task["task_id"], "archive", 1, 0, idempotency, "verified", path_name, raw_digest, archive["handoff_sha256"], int(archive.get("object_count", len(objects)) or 0), int(archive.get("bytes_verified", 0) or 0), path_name, raw_digest, "archive", "legacy-import", json.dumps(archive, sort_keys=True)))
        # Actors remain live during observation; bind the imported rows to the
        # same frozen bytes one last time before the staging transaction commits.
        validate_manifest(manifest, live_root)
        conn.execute("DELETE FROM schema_meta WHERE key='import_mode'")
        conn.commit()
        committed = True
    finally:
        if not committed and conn.in_transaction:
            conn.rollback()
        conn.close()
        if not committed:
            for suffix in ("", "-wal", "-shm"):
                candidate = Path(str(db) + suffix)
                if candidate.exists() and candidate.is_file():
                    candidate.unlink()
    result = {"schema_version": MANIFEST_SCHEMA, "cutover_id": manifest["cutover_id"], "dry_run": dry_run, "db_path": str(db), "counts": counts, "digest": _sha(db), "barrier": observed_barrier}
    if temp_dir is not None:
        result["temporary"] = True
        temp_dir.cleanup()
    return result


def barrier_check(live_root: Path | str, *, manifest: dict[str, Any] | None = None) -> dict[str, Any]:
    """Observe actors and leases without signalling, stopping, or locking them."""
    root = Path(live_root).resolve()
    pids = []
    for pid_file in (root / "supervisor.pid",):
        if pid_file.is_file():
            try:
                pids.append(int(pid_file.read_text().strip()))
            except ValueError:
                pass
    return {"barrier": "observed", "stopped": False, "actors": pids,
            "manifest_cutover_id": (manifest or {}).get("cutover_id"),
            "observed_at": __import__("datetime").datetime.now(__import__("datetime").UTC).isoformat()}


# Explicit names used by operators and downstream Phase 2 tooling.
generate_authoring_live_manifest = generate_manifest
verify_manifest = validate_manifest
dry_run_import = import_manifest
