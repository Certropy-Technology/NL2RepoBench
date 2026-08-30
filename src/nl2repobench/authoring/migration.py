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


def _check_file(root: Path, relative: str, *, max_size: int = 64 * 1024 * 1024) -> dict[str, Any]:
    path = root / relative
    if Path(relative).is_absolute() or ".." in Path(relative).parts:
        raise MigrationError(f"non-contained manifest path: {relative}")
    # lstat every component: resolving a symlink is not an acceptable authority.
    cursor = root
    for part in Path(relative).parts:
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


def _json_file(root: Path, relative: str) -> dict[str, Any]:
    record = _check_file(root, relative)
    try:
        json.loads((root / relative).read_text(encoding="utf-8"))
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
        queue = queues / f"{queue_batch}.json"
        language = batch.split("-", 1)[0]
        if language not in {"python", "node", "go"} or not queue.exists():
            continue
        lanes.append(_lane_from_path(root, plan, kind="base", language=language,
                                     source=_relative(root, queue), plan=_relative(root, plan)))
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
            lanes.append(ManifestLane(f"generated-{language}-{batch}", batch, language, "generated",
                                      source_path.as_posix(), state_path.as_posix()))
    if len(lanes) != 7:
        raise MigrationError(f"expected exactly seven lane authorities, found {len(lanes)}")
    records: list[dict[str, Any]] = []
    for lane in lanes:
        item = lane.as_dict()
        item["queue"] = _json_file(root, lane.queue_source)
        state_dir = root / lane.state_authority
        if state_dir.is_file():
            state_files = [_json_file(root, lane.state_authority)]
        else:
            if state_dir.is_symlink() or not state_dir.is_dir():
                raise MigrationError(f"missing or symlinked state authority: {lane.state_authority}")
            state_files = []
            for state_file in sorted(state_dir.glob("claims/*.json")):
                state_files.append(_json_file(root, _relative(root, state_file)))
        item["state"] = {"path": lane.state_authority, "files": state_files}
        if lane.plan_source:
            item["plan"] = _json_file(root, lane.plan_source)
        records.append(item)
    manifest: dict[str, Any] = {
        "schema_version": MANIFEST_SCHEMA, "cutover_id": cutover_id,
        "root_name": root.name, "lanes": records,
        "generated_at": __import__("datetime").datetime.now(__import__("datetime").UTC).isoformat(),
    }
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
    root = Path(live_root).resolve()
    seen: set[str] = set()
    for lane in lanes:
        if not isinstance(lane, dict) or lane.get("lane_id") in seen:
            raise MigrationError("duplicate or malformed lane")
        seen.add(str(lane.get("lane_id")))
        for key in ("queue_source", "state_authority"):
            value = lane.get(key)
            if not isinstance(value, str) or Path(value).is_absolute() or ".." in Path(value).parts:
                raise MigrationError(f"invalid {key}")
        queue = _json_file(root, str(lane["queue_source"]))
        declared = lane.get("queue")
        if isinstance(declared, dict) and declared.get("sha256") != queue["sha256"]:
            raise MigrationError(f"hash drift: {lane['queue_source']}")
        if lane.get("plan_source"):
            plan = _json_file(root, str(lane["plan_source"]))
            declared_plan = lane.get("plan")
            if isinstance(declared_plan, dict) and declared_plan.get("sha256") != plan["sha256"]:
                raise MigrationError(f"hash drift: {lane['plan_source']}")
        state = lane.get("state", {})
        for record in state.get("files", []):
            if not isinstance(record, dict) or record.get("path") is None:
                raise MigrationError("malformed state record")
            actual = _json_file(root, str(record["path"]))
            if record.get("sha256") != actual["sha256"]:
                raise MigrationError(f"hash drift: {record['path']}")


def _classify_failure(item: dict[str, Any]) -> str | None:
    value = item.get("failure_class")
    if value:
        return str(value)
    reason = str(item.get("reason") or "").lower()
    if any(word in reason for word in ("timeout", "disk", "docker", "network", "process")):
        return "infrastructure"
    if any(word in reason for word in ("collision", "already exists", "remote object")):
        return "integration-collision"
    return None


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
    return "unknown"


def import_manifest(manifest: dict[str, Any], live_root: Path | str, *, db_path: Path | str | None = None,
                    dry_run: bool = True, barrier: Any = None) -> dict[str, Any]:
    """Import into a temporary scheduler DB; ``dry_run=False`` still requires a temp DB."""
    validate_manifest(manifest, live_root)
    root = Path(live_root).resolve()
    observed_barrier = barrier() if barrier is not None else barrier_check(root, manifest=manifest)
    if not isinstance(observed_barrier, dict) or observed_barrier.get("stopped") is not False:
        raise MigrationError("mandatory migration barrier did not complete as observe-only")
    temp_dir: tempfile.TemporaryDirectory[str] | None = None
    if db_path is None:
        temp_dir = tempfile.TemporaryDirectory(prefix="authoring-import-")
        db = Path(temp_dir.name) / "scheduler.sqlite3"
    else:
        db = Path(db_path).resolve()
        if root == db or root in db.parents:
            raise MigrationError("import DB must not be the live authoring tree")
    db.parent.mkdir(parents=True, exist_ok=True)
    scheduler = Scheduler(db, supplied_root=db.parent)
    if not db.exists() or db.stat().st_size == 0:
        scheduler.init()
    conn = scheduler.connect()
    counts: dict[str, int] = {}
    try:
        conn.execute("INSERT OR REPLACE INTO schema_meta(key,value) VALUES('import_mode','1')")
        for lane in manifest["lanes"]:
            lane_id = str(lane["lane_id"])
            kind, language = str(lane["kind"]), str(lane["language"])
            conn.execute("INSERT OR IGNORE INTO lanes(lane_id,batch_id,language,kind,status,queue_path,queue_sha256,plan_path,plan_sha256,state_path,state_sha256,source_reports_json,fairness_rank,last_dispatch_seq,created_at,updated_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,datetime('now'),datetime('now'))",
                         (lane_id, lane["batch_id"], language, kind, "active", lane["queue_source"], lane["queue"]["sha256"], lane.get("plan_source", "plan.json"), (lane.get("plan") or {}).get("sha256", "0"*64), lane["state_authority"], None, "[]", 0, 0))
            queue_data = json.loads((root / lane["queue_source"]).read_text(encoding="utf-8"))
            items = queue_data.get("items", {}) if isinstance(queue_data, dict) else {}
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
                state = _STATUS.get(str(item.get("status", "pending")), "blocked")
                failure = _classify_failure(item)
                reason = str(item.get("reason") or item.get("release_reason") or "legacy import")
                terminal = reason if state in {"complete", "blocked", "excluded", "cancelled"} else None
                conn.execute("INSERT OR IGNORE INTO tasks(task_id,candidate_id,lane_id,task_release,state,attempt_limit,authoring_attempts,retry_limit,retry_count,release_count,release_limit,integration_attempts,integration_retry_count,integration_retry_limit,archive_attempts,archive_retry_count,archive_retry_limit,cleanup_attempts,cleanup_retry_count,cleanup_retry_limit,input_ordinal,last_failure_class,last_failure_reason,terminal_reason,created_at,updated_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,datetime('now'),datetime('now'))",
                             (task_id, candidate_id, lane_id, "legacy", state, max(1, int(item.get("attempt_limit", 3) or 3)), int(item.get("attempts", 0) or 0), 3, 0, 0, 3, 0, 0, 3, 0, 0, 3, 0, 0, 3, int(item.get("ordinal", 0) or 0), failure, reason if failure else None, terminal))
                for artifact in item.get("artifacts", []) if isinstance(item.get("artifacts"), list) else []:
                    artifact_path = str(artifact)
                    artifact_digest = hashlib.sha256(artifact_path.encode()).hexdigest()
                    conn.execute("INSERT OR IGNORE INTO artifacts(artifact_id,task_id,trial_id,kind,path,sha256,size_bytes,secret_scan_status,created_at) VALUES(?,?,?,?,?,?,?,'not-run',datetime('now'))", (f"legacy:{artifact_digest}", task_id, None, "legacy-reference", artifact_path, artifact_digest, len(artifact_path)))
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
                classification = "historical-owner" if owner else "orphan-claim"
                conn.execute("INSERT OR IGNORE INTO orphan_claim_evidence VALUES(?,?,?,?,?,?,?,?,?,?,?,datetime('now'))", (f"{lane['batch_id']}:{path.stem}", record["path"], str(claim.get("candidate_id") or ""), str(claim.get("package") or ""), owner, str(claim.get("status") or ""), str(claim.get("lease_expires_at") or ""), str(claim.get("attempts") or ""), record["sha256"], classification, "legacy claim evidence; no live controller imported"))
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
        conn.execute("INSERT OR REPLACE INTO schema_meta(key,value) VALUES('import_mode','0')")
        conn.commit()
    finally:
        conn.close()
        if temp_dir is not None:
            # The result is intentionally a digest/count receipt, not a persistent live database.
            pass
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
