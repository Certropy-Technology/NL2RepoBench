"""Content provenance for checked-in runtime-adapter slice evidence."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


def _digest_tree(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(path)
    digest = hashlib.sha256()
    if path.is_file():
        digest.update(path.read_bytes())
        return digest.hexdigest()
    for child in sorted(path.rglob("*")):
        if not child.is_file() or "__pycache__" in child.parts or child.suffix == ".pyc":
            continue
        relative = child.relative_to(path).as_posix().encode("utf-8")
        data = child.read_bytes()
        digest.update(len(relative).to_bytes(8, "big"))
        digest.update(relative)
        digest.update(len(data).to_bytes(8, "big"))
        digest.update(data)
    return digest.hexdigest()


def slice_provenance(
    root: Path,
    *,
    runtime: str,
    package_manager: str,
    bundle_manifest: Path,
) -> dict[str, Any]:
    source_name = "node-pnpm-synthetic" if runtime == "node" else "go-google-uuid"
    toolchain_name = (
        "toolchain.node.dev.lock.toml"
        if runtime == "node"
        else "toolchain.go.dev.lock.toml"
    )
    control_name = (
        "run_pnpm_harbor_controls.sh"
        if runtime == "node"
        else "run_go_harbor_controls.sh"
    )
    source = root / "catalog/sources" / source_name
    manifest = json.loads(bundle_manifest.read_text(encoding="utf-8"))
    return {
        "schema_version": "p2-slice-provenance-v1",
        "runtime": runtime,
        "package_manager": package_manager,
        "source_tree_sha256": _digest_tree(source),
        "implementation_tree_sha256": _digest_tree(root / "src/nl2repobench"),
        "toolchain_sha256": _digest_tree(root / toolchain_name),
        "control_script_sha256": _digest_tree(root / "scripts" / control_name),
        "slice_verifier_sha256": _digest_tree(root / "scripts/verify_p2_vertical_slices.py"),
        "bundle_manifest_sha256": _digest_tree(bundle_manifest),
        "canonical_manifest_digest": manifest.get("canonical_manifest_digest"),
    }


__all__ = ["slice_provenance"]
