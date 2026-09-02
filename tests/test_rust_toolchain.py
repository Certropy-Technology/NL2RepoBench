from __future__ import annotations

from pathlib import Path

import pytest
from pydantic import ValidationError

from nl2repobench.harbor.rust_toolchain import (
    RustToolchainLock,
    load_rust_toolchain_lock,
)

ROOT = Path(__file__).parents[1]


def test_checked_in_rust_toolchain_is_strictly_provisional() -> None:
    lock = load_rust_toolchain_lock(ROOT / "toolchain.rust.dev.lock.toml")

    assert lock.status == "provisional-unlocked"
    assert lock.cargo_vv_sha256 is None
    assert lock.miri_sysroot_tree_digest is None
    assert lock.production_ready is False
    assert not any(
        name in lock.model_fields_set
        for name in (
            "cargo_vv_sha256",
            "rustc_vv_sha256",
            "cargo_executable_sha256",
            "rustc_executable_sha256",
            "cargo_miri_executable_sha256",
            "miri_sysroot_tree_digest",
        )
    )


@pytest.mark.parametrize(
    ("extra", "message"),
    [
        ('cargo_vv_sha256 = ""\n', "must omit actual probe fields"),
        ('cargo_vv_sha256 = "sha256:' + "1" * 64 + '"\n', "must omit actual"),
        ('unknown = true\n', "Extra inputs"),
    ],
)
def test_provisional_rust_toolchain_rejects_actuals_and_unknown_fields(
    tmp_path: Path, extra: str, message: str
) -> None:
    source = (ROOT / "toolchain.rust.dev.lock.toml").read_text(encoding="utf-8")
    path = tmp_path / "toolchain.rust.dev.lock.toml"
    path.write_text(source + extra, encoding="utf-8")

    with pytest.raises((ValueError, ValidationError), match=message):
        load_rust_toolchain_lock(path)


def test_locked_probe_shape_requires_every_actual_digest() -> None:
    provisional = load_rust_toolchain_lock(ROOT / "toolchain.rust.dev.lock.toml")
    payload = provisional.model_dump(
        exclude=set(type(provisional).model_fields) - provisional.model_fields_set
    )
    payload["status"] = "locked"

    with pytest.raises(ValidationError, match="requires every actual field"):
        RustToolchainLock.model_validate(payload)

    for name in (
        "cargo_vv_sha256",
        "rustc_vv_sha256",
        "cargo_executable_sha256",
        "rustc_executable_sha256",
        "cargo_miri_executable_sha256",
        "miri_sysroot_tree_digest",
    ):
        payload[name] = "sha256:" + "1" * 64
    locked = RustToolchainLock.model_validate(payload)
    assert locked.status == "locked"
    assert locked.production_ready is False


def test_rust_toolchain_tuple_has_no_fallback(tmp_path: Path) -> None:
    source = (ROOT / "toolchain.rust.dev.lock.toml").read_text(encoding="utf-8")
    path = tmp_path / "toolchain.rust.dev.lock.toml"
    path.write_text(source.replace("2026-08-20", "2026-08-21"), encoding="utf-8")

    with pytest.raises(ValidationError):
        load_rust_toolchain_lock(path)


def test_stable_rust_release_lock_is_independent_and_exact() -> None:
    stable = load_rust_toolchain_lock(ROOT / "toolchain.rust.stable.lock.toml")
    assert stable.release_id == "rust-stable-1.97.1-v1"
    assert stable.rustc_version == "1.97.1"
    assert stable.cargo_version == "1.97.1"
    assert stable.miri_status == "unavailable"
    assert stable.production_ready is False
