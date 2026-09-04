from __future__ import annotations

import hashlib
import io
import tarfile

import pytest

from nl2repobench.storage.canonical_ustar import (
    CanonicalEntry,
    CanonicalUstarError,
    encode_ustar,
    tree_digest,
)


def test_empty_canonical_ustar_is_one_zero_record() -> None:
    data = encode_ustar(())

    assert data == b"\0" * 10_240
    assert hashlib.sha256(data).hexdigest() == (
        "84ff92691f909a05b224e1c56abb4864f01b4f8e3c854e4bb4c7baf1d3f6d652"
    )


def test_canonical_ustar_round_trips_modes_and_bytes() -> None:
    entries = (
        CanonicalEntry("bin/", "directory", 0o555),
        CanonicalEntry("bin/run.sh", "file", 0o555, b"#!/bin/sh\n"),
        CanonicalEntry("lock.txt", "file", 0o444, b"locked\n"),
    )

    data = encode_ustar(entries)
    with tarfile.open(fileobj=io.BytesIO(data), mode="r:") as archive:
        assert archive.getnames() == ["bin", "bin/run.sh", "lock.txt"]
        assert archive.getmember("bin/run.sh").mode == 0o555
        assert archive.extractfile("lock.txt").read() == b"locked\n"  # type: ignore[union-attr]
    assert tree_digest(entries).startswith("sha256:")


def test_canonical_ustar_rejects_unsorted_or_unsafe_entries() -> None:
    with pytest.raises(CanonicalUstarError, match="sorted"):
        encode_ustar(
            (
                CanonicalEntry("z", "file", 0o444, b"z"),
                CanonicalEntry("a", "file", 0o444, b"a"),
            )
        )
    with pytest.raises(CanonicalUstarError, match="unsafe"):
        encode_ustar((CanonicalEntry("../escape", "file", 0o444, b"x"),))
