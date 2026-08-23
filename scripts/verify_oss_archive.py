#!/usr/bin/env python3
"""Verify an OSS archive before optionally removing local run artifacts.

The uploader writes a deterministic object manifest and stores the same
SHA-256 digest as OSS user metadata.  This command checks both the local
manifest and every remote object.  Local deletion is an explicit final step
and is never attempted when a remote size, checksum, or object is missing.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

SHA256 = re.compile(r"^[0-9a-f]{64}$")
SECRET_PATTERNS = (
    re.compile(r"(?<![A-Za-z0-9])sk-[A-Za-z0-9_-]{40,256}(?![A-Za-z0-9_-])"),
    re.compile(r"LTAI[A-Za-z0-9]{12,}"),
    re.compile(r"AKIA[A-Z0-9]{12,}"),
)


@dataclass(frozen=True)
class ObjectRecord:
    key: str
    size: int
    sha256: str


def _read_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"invalid JSON {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise ValueError(f"manifest must be a JSON object: {path}")
    return payload


def resolve_archive_config(
    campaign_or_manifest: Path,
) -> tuple[Path, str, Path | None, tuple[Path, ...]]:
    """Resolve archive paths, the remote key, and local integrity roots."""

    payload = _read_json(campaign_or_manifest)
    archive = payload.get("archive")
    if isinstance(archive, dict):
        manifest_value = archive.get("manifest")
        remote_key = archive.get("remote_manifest_key")
        local_value = archive.get("local_runs_dir")
        if not isinstance(manifest_value, str) or not isinstance(remote_key, str):
            raise ValueError("campaign archive requires manifest and remote_manifest_key")
        manifest_path = (campaign_or_manifest.parent / manifest_value).resolve()
        local_root = (
            (campaign_or_manifest.parent / local_value).absolute()
            if isinstance(local_value, str)
            else None
        )
        raw_roots = archive.get("local_upload_roots", [])
        if not isinstance(raw_roots, list) or not all(isinstance(item, str) for item in raw_roots):
            raise ValueError("campaign archive local_upload_roots must be a list of paths")
        local_roots = tuple((campaign_or_manifest.parent / item).absolute() for item in raw_roots)
        if local_root is not None and local_root not in local_roots:
            local_roots = (*local_roots, local_root)
        return manifest_path, remote_key, local_root, local_roots
    raise ValueError(
        "direct object manifests require a campaign archive section with "
        "manifest and remote_manifest_key"
    )


def load_object_manifest(path: Path) -> tuple[ObjectRecord, ...]:
    payload = _read_json(path)
    if payload.get("hash_algorithm") != "sha256":
        raise ValueError(f"unsupported manifest hash algorithm: {path}")
    raw_objects = payload.get("objects")
    if not isinstance(raw_objects, list):
        raise ValueError(f"manifest objects must be a list: {path}")
    records: list[ObjectRecord] = []
    seen: set[str] = set()
    for index, raw in enumerate(raw_objects):
        if not isinstance(raw, dict):
            raise ValueError(f"manifest object {index} must be an object")
        key = raw.get("key")
        size = raw.get("size")
        digest = raw.get("sha256")
        if not isinstance(key, str) or not key.startswith("nl2repobench/"):
            raise ValueError(f"manifest object {index} has an invalid OSS key")
        if key in seen:
            raise ValueError(f"manifest contains duplicate key: {key}")
        if not isinstance(size, int) or size < 0:
            raise ValueError(f"manifest object {key} has invalid size")
        if not isinstance(digest, str) or not SHA256.fullmatch(digest):
            raise ValueError(f"manifest object {key} has invalid sha256")
        seen.add(key)
        records.append(ObjectRecord(key=key, size=size, sha256=digest))
    return tuple(records)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_local_runs(records: tuple[ObjectRecord, ...], runs_dir: Path) -> list[str]:
    """Compare the local run tree with the exact object manifest."""

    if not runs_dir.is_dir():
        return [f"local runs directory does not exist: {runs_dir}"]
    try:
        from upload_runs_to_oss import iter_run_uploads
    except ImportError as exc:  # pragma: no cover - only occurs outside repo root
        return [f"cannot import uploader for local verification: {exc}"]

    expected = {
        record.key: record
        for record in records
        if record.key.startswith("nl2repobench/runs/")
    }
    actual = {item.key: item for item in iter_run_uploads(runs_dir)}
    errors: list[str] = []
    for key in sorted(set(expected) - set(actual)):
        errors.append(f"local run object is missing: {key}")
    for key in sorted(set(actual) - set(expected)):
        errors.append(f"local run object is absent from manifest: {key}")
    for key in sorted(set(expected) & set(actual)):
        record = expected[key]
        item = actual[key]
        if item.size != record.size:
            errors.append(f"local size mismatch for {key}: {item.size} != {record.size}")
        if item.sha256 != record.sha256:
            errors.append(f"local checksum mismatch for {key}")
    return errors


def scan_for_secrets(root: Path) -> list[str]:
    """Return file paths containing secret-shaped values, never the values."""

    findings: list[str] = []
    if root.is_symlink():
        return [str(root)]
    if not root.exists():
        return findings
    paths = [root] if root.is_file() else sorted(root.rglob("*"))
    for path in paths:
        if path.is_symlink():
            findings.append(str(path))
            continue
        if not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        if any(pattern.search(text) for pattern in SECRET_PATTERNS):
            findings.append(str(path))
    return findings


def _header(response: Any, name: str) -> str | None:
    headers = getattr(response, "headers", None)
    if headers is None:
        return None
    wanted = name.casefold()
    for key, value in headers.items():
        if str(key).casefold() == wanted:
            return str(value)
    return None


def verify_remote_objects(bucket: Any, records: tuple[ObjectRecord, ...]) -> list[str]:
    errors: list[str] = []
    for record in records:
        try:
            response = bucket.get_object(record.key)
        except Exception as exc:  # noqa: BLE001 - preserve key-specific archive evidence
            errors.append(f"remote object unavailable {record.key}: {exc}")
            continue
        digest = hashlib.sha256()
        remote_size = 0
        while True:
            try:
                chunk = response.read(1024 * 1024)
            except TypeError:
                chunk = response.read()
            if not chunk:
                break
            digest.update(chunk)
            remote_size += len(chunk)
        if remote_size != record.size:
            errors.append(f"remote size mismatch for {record.key}: {remote_size} != {record.size}")
        if digest.hexdigest() != record.sha256:
            errors.append(f"remote payload checksum mismatch for {record.key}")
    return errors


def verify_remote_manifest(bucket: Any, key: str, local_manifest: Path) -> list[str]:
    errors: list[str] = []
    try:
        response = bucket.get_object(key)
        remote_bytes = response.read()
    except Exception as exc:  # noqa: BLE001 - preserve archive evidence
        return [f"remote manifest unavailable {key}: {exc}"]
    local_bytes = local_manifest.read_bytes()
    if remote_bytes != local_bytes:
        errors.append(f"remote manifest content mismatch: {key}")
    local_digest = hashlib.sha256(local_bytes).hexdigest()
    if _header(response, "x-oss-meta-sha256") not in {None, local_digest}:
        errors.append(f"remote manifest checksum metadata mismatch: {key}")
    return errors


def remove_local_runs(runs_dir: Path, *, repo_root: Path) -> None:
    if runs_dir.is_symlink():
        raise ValueError(f"refusing to remove symlink run directory: {runs_dir}")
    resolved = runs_dir.resolve()
    trusted_root = (repo_root / ".nl2repo" / "runs").resolve()
    if not resolved.is_dir() or resolved == trusted_root:
        raise ValueError(f"refusing to remove unsafe or missing run directory: {runs_dir}")
    try:
        resolved.relative_to(trusted_root)
    except ValueError as exc:
        raise ValueError(f"run directory must be below {trusted_root}: {runs_dir}") from exc
    shutil.rmtree(resolved)


def validate_upload_roots(roots: tuple[Path, ...]) -> list[str]:
    errors: list[str] = []
    for root in roots:
        if any(component.is_symlink() for component in _path_components(root)):
            errors.append(f"upload root contains a symlink component: {root}")
        elif not root.exists():
            errors.append(f"upload root is missing: {root}")
    return errors


def _path_components(path: Path) -> tuple[Path, ...]:
    absolute = path.absolute()
    parts = absolute.parts
    cursor = Path(parts[0])
    components = [cursor]
    for part in parts[1:]:
        cursor /= part
        components.append(cursor)
    return tuple(components)


def build_bucket() -> Any:
    try:
        import oss2
    except ImportError as exc:
        raise RuntimeError("install oss2 before remote OSS verification") from exc
    key_id = os.environ.get("OSS_ACCESS_KEY_ID")
    key_secret = os.environ.get("OSS_ACCESS_KEY_SECRET")
    if not key_id or not key_secret:
        raise RuntimeError("set OSS_ACCESS_KEY_ID and OSS_ACCESS_KEY_SECRET")
    return oss2.Bucket(
        oss2.Auth(key_id, key_secret),
        "https://oss-ap-southeast-1.aliyuncs.com",
        "dingshang-sg",
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True, help="Campaign JSON manifest.")
    parser.add_argument("--local-runs-dir", type=Path)
    parser.add_argument("--delete-local", action="store_true")
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    args = parser.parse_args()

    try:
        manifest_path, remote_key, configured_runs, upload_roots = resolve_archive_config(
            args.manifest
        )
        records = load_object_manifest(manifest_path)
        runs_dir = args.local_runs_dir or configured_runs
        errors: list[str] = []
        errors.extend(validate_upload_roots(upload_roots))
        if runs_dir is not None and runs_dir.exists():
            errors.extend(validate_local_runs(records, runs_dir))
        for root in upload_roots:
            errors.extend(f"secret-shaped content in {path}" for path in scan_for_secrets(root))
        bucket = build_bucket()
        errors.extend(verify_remote_objects(bucket, records))
        errors.extend(verify_remote_manifest(bucket, remote_key, manifest_path))
        if errors:
            for error in errors:
                print(error, file=sys.stderr)
            return 1
        if args.delete_local:
            if runs_dir is None:
                raise ValueError("--delete-local requires local_runs_dir")
            remove_local_runs(runs_dir, repo_root=args.repo_root)
        print(
            json.dumps(
                {
                    "manifest": str(manifest_path),
                    "remote_manifest_key": remote_key,
                    "objects": len(records),
                    "local_deleted": bool(args.delete_local),
                },
                sort_keys=True,
            )
        )
        return 0
    except (OSError, ValueError, RuntimeError) as exc:
        print(f"OSS archive verification failed: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
