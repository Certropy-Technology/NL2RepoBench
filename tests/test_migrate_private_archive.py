from __future__ import annotations

import importlib.util
import io
import json
import subprocess
import sys
import tarfile
import unicodedata
from pathlib import Path

import pytest

from nl2repobench.storage.canonical_ustar import decode_archive, tree_digest

_SCRIPT = Path(__file__).parents[1] / "scripts/migrate_private_archive.py"
_SPEC = importlib.util.spec_from_file_location("private_archive_migration", _SCRIPT)
assert _SPEC and _SPEC.loader
_MODULE = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_MODULE)


def _legacy_tar(*members: tuple[str, bytes | None, int, str]) -> bytes:
    output = io.BytesIO()
    with tarfile.open(fileobj=output, mode="w", format=tarfile.PAX_FORMAT) as archive:
        for name, payload, mode, member_type in members:
            info = tarfile.TarInfo(name)
            info.mode = mode
            if member_type == "directory":
                info.type = tarfile.DIRTYPE
                info.size = 0
                archive.addfile(info)
            else:
                assert payload is not None
                info.size = len(payload)
                archive.addfile(info, io.BytesIO(payload))
    return output.getvalue()


def test_helper_migrates_gzip_tar_and_preserves_executable_class() -> None:
    output = io.BytesIO()
    with tarfile.open(fileobj=output, mode="w:gz", format=tarfile.GNU_FORMAT) as archive:
        for name, payload, mode in (
            ("./run.sh", b"#!/bin/sh\n", 0o700),
            ("data/value.txt", b"value", 0o644),
        ):
            info = tarfile.TarInfo(name)
            info.mode = mode
            info.size = len(payload)
            archive.addfile(info, io.BytesIO(payload))
    result = _MODULE.migrate_private_archive(output.getvalue(), "test-bundle")
    members = decode_archive(result.archive)
    assert result.file_count == 2
    assert result.media_type == "application/vnd.nl2repobench.test-bundle.tar"
    assert result.tree_digest == tree_digest(tuple(member.entry for member in members))
    assert [(member.entry.path, member.entry.mode, member.data) for member in members] == [
        ("data", 0o555, None),
        ("data/value.txt", 0o444, b"value"),
        ("run.sh", 0o555, b"#!/bin/sh\n"),
    ]


@pytest.mark.parametrize(
    "name",
    ["/absolute", "../parent", "a/../b", "a//b", "a/./b", "././nested", ""],
)
def test_helper_rejects_ambiguous_paths(name: str) -> None:
    legacy = _legacy_tar((name, b"x", 0o644, "file"))
    with pytest.raises(_MODULE.PrivateArchiveMigrationError):
        _MODULE.migrate_private_archive(legacy, "test-bundle")


@pytest.mark.parametrize("member_type", ["symlink", "hardlink", "fifo"])
def test_helper_rejects_non_regular_members(member_type: str) -> None:
    output = io.BytesIO()
    with tarfile.open(fileobj=output, mode="w") as archive:
        info = tarfile.TarInfo("unsafe")
        if member_type == "symlink":
            info.type = tarfile.SYMTYPE
            info.linkname = "target"
        elif member_type == "hardlink":
            info.type = tarfile.LNKTYPE
            info.linkname = "target"
        else:
            info.type = tarfile.FIFOTYPE
        archive.addfile(info)
    with pytest.raises(_MODULE.PrivateArchiveMigrationError):
        _MODULE.migrate_private_archive(output.getvalue(), "test-bundle")


def test_helper_rejects_duplicate_and_size_limits() -> None:
    duplicate = _legacy_tar(("same", b"a", 0o644, "file"), ("same", b"b", 0o644, "file"))
    with pytest.raises(_MODULE.PrivateArchiveMigrationError, match="duplicate"):
        _MODULE.migrate_private_archive(duplicate, "test-bundle")
    oversized = _legacy_tar(("large", b"123", 0o644, "file"))
    limits = _MODULE.MigrationLimits(max_member_bytes=2, max_total_bytes=2)
    with pytest.raises(_MODULE.PrivateArchiveMigrationError, match="size limit"):
        _MODULE.migrate_private_archive(oversized, "test-bundle", limits)


def test_helper_rejects_nfc_invalid_name_and_malformed_tar() -> None:
    decomposed = unicodedata.normalize("NFD", "café")
    legacy = _legacy_tar((decomposed, b"x", 0o644, "file"))
    with pytest.raises(_MODULE.PrivateArchiveMigrationError, match="NFC"):
        _MODULE.migrate_private_archive(legacy, "test-bundle")
    with pytest.raises(_MODULE.PrivateArchiveMigrationError, match="trailer"):
        _MODULE.migrate_private_archive(b"\0" * 512, "test-bundle")


def test_helper_rejects_concatenated_gzip_tar() -> None:
    compressed = io.BytesIO()
    with tarfile.open(fileobj=compressed, mode="w:gz") as archive:
        info = tarfile.TarInfo("file")
        info.size = 1
        archive.addfile(info, io.BytesIO(b"x"))
    payload = compressed.getvalue()
    with pytest.raises(_MODULE.PrivateArchiveMigrationError, match="trailer"):
        _MODULE.migrate_private_archive(payload + payload, "test-bundle")


def test_cli_emits_only_metadata_json_and_writes_canonical_archive(tmp_path: Path) -> None:
    legacy = _legacy_tar(("file.txt", b"private payload", 0o644, "file"))
    source = tmp_path / "legacy.tar"
    destination = tmp_path / "canonical.tar"
    source.write_bytes(legacy)
    completed = subprocess.run(
        [
            sys.executable,
            str(_SCRIPT),
            "--input",
            str(source),
            "--output",
            str(destination),
            "--kind",
            "test-bundle",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert completed.returncode == 0
    metadata = json.loads(completed.stdout)
    assert set(metadata) == {
        "old_sha256",
        "old_size",
        "new_sha256",
        "new_size",
        "file_count",
        "tree_digest",
        "media_type",
    }
    assert b"private payload" not in completed.stdout.encode()
    assert decode_archive(destination.read_bytes())[0].data == b"private payload"
