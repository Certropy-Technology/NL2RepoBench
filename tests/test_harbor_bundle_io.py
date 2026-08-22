from __future__ import annotations

import io
import os
import tarfile
from pathlib import Path

import pytest

from nl2repobench.harbor.bundle_io import (
    BundleArchiveDuplicateError,
    BundleArchiveLinkError,
    BundleArchiveMemberCountError,
    BundleArchiveMemberSizeError,
    BundleArchivePathError,
    BundleArchiveTotalSizeError,
    BundleLimits,
    BundleTreePathError,
    copy_bundle_tree,
    extract_bundle_archive,
)


def _tar_bytes(
    members: list[tuple[str, bytes, str]],
) -> bytes:
    buffer = io.BytesIO()
    with tarfile.open(fileobj=buffer, mode="w") as archive:
        for name, content, kind in members:
            info = tarfile.TarInfo(name)
            info.mode = 0o751 if name.endswith(".sh") else 0o640
            if kind == "directory":
                info.type = tarfile.DIRTYPE
                archive.addfile(info)
            elif kind == "symlink":
                info.type = tarfile.SYMTYPE
                info.linkname = "outside"
                archive.addfile(info)
            else:
                info.size = len(content)
                archive.addfile(info, io.BytesIO(content))
    return buffer.getvalue()


def _write_archive(path: Path, members: list[tuple[str, bytes, str]]) -> None:
    path.write_bytes(_tar_bytes(members))


def test_extract_bundle_archive_copies_modes_and_nested_files(tmp_path: Path) -> None:
    archive = tmp_path / "bundle.tar"
    _write_archive(
        archive,
        [
            ("nested", b"", "directory"),
            ("nested/run.sh", b"echo ok\n", "file"),
        ],
    )

    destination = tmp_path / "extracted"
    extract_bundle_archive(
        archive,
        destination,
        limits=BundleLimits(max_members=4, max_member_bytes=32, max_total_bytes=64),
    )

    script = destination / "nested/run.sh"
    assert script.read_bytes() == b"echo ok\n"
    assert script.stat().st_mode & 0o777 == 0o751


@pytest.mark.parametrize(
    ("name", "error"),
    [
        ("../escape.txt", BundleArchivePathError),
        ("/absolute.txt", BundleArchivePathError),
        ("link", BundleArchiveLinkError),
    ],
)
def test_extract_bundle_archive_rejects_unsafe_members(
    tmp_path: Path, name: str, error: type[ValueError]
) -> None:
    kind = "symlink" if name == "link" else "file"
    archive = tmp_path / "unsafe.tar"
    _write_archive(archive, [(name, b"bad", kind)])

    with pytest.raises(error):
        extract_bundle_archive(
            archive,
            tmp_path / "extracted",
            limits=BundleLimits(max_members=4, max_member_bytes=32, max_total_bytes=64),
        )


def test_extract_bundle_archive_rejects_duplicate_and_size_limits(tmp_path: Path) -> None:
    duplicate = tmp_path / "duplicate.tar"
    _write_archive(duplicate, [("same.txt", b"one", "file"), ("same.txt", b"two", "file")])
    with pytest.raises(BundleArchiveDuplicateError):
        extract_bundle_archive(
            duplicate,
            tmp_path / "duplicate-out",
            limits=BundleLimits(max_members=4, max_member_bytes=32, max_total_bytes=64),
        )

    oversized = tmp_path / "oversized.tar"
    _write_archive(oversized, [("large.txt", b"12345", "file")])
    with pytest.raises(BundleArchiveMemberSizeError):
        extract_bundle_archive(
            oversized,
            tmp_path / "oversized-out",
            limits=BundleLimits(max_members=4, max_member_bytes=4, max_total_bytes=64),
        )

    total = tmp_path / "total.tar"
    _write_archive(total, [("one.txt", b"1234", "file"), ("two.txt", b"5678", "file")])
    with pytest.raises(BundleArchiveTotalSizeError):
        extract_bundle_archive(
            total,
            tmp_path / "total-out",
            limits=BundleLimits(max_members=4, max_member_bytes=8, max_total_bytes=7),
        )


def test_extract_bundle_archive_streams_member_limit(tmp_path: Path) -> None:
    archive = tmp_path / "many.tar"
    _write_archive(archive, [("one.txt", b"1", "file"), ("two.txt", b"2", "file")])

    with pytest.raises(BundleArchiveMemberCountError):
        extract_bundle_archive(
            archive,
            tmp_path / "many-out",
            limits=BundleLimits(max_members=1, max_member_bytes=8, max_total_bytes=64),
        )


def test_copy_bundle_tree_is_deterministic_and_rejects_symlinks(tmp_path: Path) -> None:
    source = tmp_path / "source"
    source.mkdir()
    script = source / "run.sh"
    script.write_bytes(b"run\n")
    os.chmod(script, 0o751)
    copied = tmp_path / "copied"
    copy_bundle_tree(source, copied)
    assert (copied / "run.sh").read_bytes() == b"run\n"
    assert (copied / "run.sh").stat().st_mode & 0o777 == 0o751

    outside = tmp_path / "outside"
    outside.write_bytes(b"outside")
    (source / "escape").symlink_to(outside)
    with pytest.raises(BundleTreePathError):
        copy_bundle_tree(source, tmp_path / "rejected")
