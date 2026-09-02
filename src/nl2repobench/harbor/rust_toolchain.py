"""Strict Rust toolchain tuple and provisional/locked probe contract."""

from __future__ import annotations

import re
import tomllib
from pathlib import Path
from typing import Literal, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

MAX_RUST_TOOLCHAIN_LOCK_BYTES = 64 * 1024
_HEX_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_DIGEST = re.compile(r"^sha256:[0-9a-f]{64}$")

EXPECTED_RUST_TOOLCHAIN = {
    "expected_channel_date": "2026-08-20",
    "expected_channel_manifest_sha256": (
        "8ccaced09f209becc9c732ff86e5ec3373cc4b45e3ccd80c1cfb06bbabd88807"
    ),
    "expected_rustc_first_line": "rustc 1.100.0-nightly (f7d782a3b 2026-08-19)",
    "expected_rustc_commit": "f7d782a3be46d6bb4b9792fe69a61db389ba1769",
    "expected_cargo_first_line": "cargo 1.100.0-nightly (514c56dd7 2026-08-19)",
    "expected_cargo_commit": "514c56dd7321eecbfdcf9b6479519cf4edfab906",
    "expected_miri_version": "0.1.0-nightly",
    "expected_target": "x86_64-unknown-linux-gnu",
    "expected_host": "x86_64-unknown-linux-gnu",
    "expected_platform": "linux/amd64",
    "expected_debian_base": (
        "docker.io/library/debian@sha256:"
        "5ae3c39ebd15e229dcedd5cee596b2497182493d41ff162e824ba13fc1b2b867"
    ),
    "expected_cargo_archive_sha256": (
        "0de1039680eb7c1c31f6c45aecde18b90fb8517a42439dfd389d287adf4f8114"
    ),
    "expected_rustc_archive_sha256": (
        "5ddf6a2472eb778bb4bf57c1bbe118913d5958ec59baf399283d42ed40b5d1be"
    ),
    "expected_rust_std_archive_sha256": (
        "64600c72503dfe1c8c6f69e3a933cb6ca984fe898016d3d65116160727dc54b2"
    ),
    "expected_miri_archive_sha256": (
        "a81cfe5594285eafa010aff6d1891aaf05e204bb6acb6f8bf7ba522f04d1f44d"
    ),
    "expected_rust_src_archive_source": "verified-channel-manifest",
}

_ACTUAL_FIELDS = (
    "cargo_vv_sha256",
    "rustc_vv_sha256",
    "cargo_executable_sha256",
    "rustc_executable_sha256",
    "cargo_miri_executable_sha256",
    "miri_sysroot_tree_digest",
)


class RustToolchainLock(BaseModel):
    """R9 tuple plus the first probe fields; it is not an image identity."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    schema_version: Literal["1.0"]
    status: Literal["provisional-unlocked", "locked"]
    expected_channel_date: Literal["2026-08-20"]
    expected_channel_manifest_sha256: str
    expected_rustc_first_line: Literal[
        "rustc 1.100.0-nightly (f7d782a3b 2026-08-19)"
    ]
    expected_rustc_commit: Literal[
        "f7d782a3be46d6bb4b9792fe69a61db389ba1769"
    ]
    expected_cargo_first_line: Literal[
        "cargo 1.100.0-nightly (514c56dd7 2026-08-19)"
    ]
    expected_cargo_commit: Literal[
        "514c56dd7321eecbfdcf9b6479519cf4edfab906"
    ]
    expected_miri_version: Literal["0.1.0-nightly"]
    expected_target: Literal["x86_64-unknown-linux-gnu"]
    expected_host: Literal["x86_64-unknown-linux-gnu"]
    expected_platform: Literal["linux/amd64"]
    expected_debian_base: Literal[
        "docker.io/library/debian@sha256:"
        "5ae3c39ebd15e229dcedd5cee596b2497182493d41ff162e824ba13fc1b2b867"
    ]
    expected_cargo_archive_sha256: str
    expected_rustc_archive_sha256: str
    expected_rust_std_archive_sha256: str
    expected_miri_archive_sha256: str
    expected_rust_src_archive_source: Literal["verified-channel-manifest"]
    cargo_vv_sha256: str | None = None
    rustc_vv_sha256: str | None = None
    cargo_executable_sha256: str | None = None
    rustc_executable_sha256: str | None = None
    cargo_miri_executable_sha256: str | None = None
    miri_sysroot_tree_digest: str | None = None

    @model_validator(mode="after")
    def validate_exact_tuple(self) -> Self:
        for name, expected in EXPECTED_RUST_TOOLCHAIN.items():
            if getattr(self, name) != expected:
                raise ValueError(f"{name} does not match the frozen Rust tuple")
        for name in (
            "expected_channel_manifest_sha256",
            "expected_cargo_archive_sha256",
            "expected_rustc_archive_sha256",
            "expected_rust_std_archive_sha256",
            "expected_miri_archive_sha256",
        ):
            if not _HEX_SHA256.fullmatch(getattr(self, name)):
                raise ValueError(f"{name} must be a lowercase SHA-256")
        actuals = {name: getattr(self, name) for name in _ACTUAL_FIELDS}
        if self.status == "provisional-unlocked":
            supplied = [name for name in _ACTUAL_FIELDS if name in self.model_fields_set]
            if supplied:
                raise ValueError(
                    "provisional Rust lock must omit actual probe fields: "
                    + ", ".join(supplied)
                )
        else:
            missing = [name for name, value in actuals.items() if value is None]
            if missing:
                raise ValueError(
                    "locked Rust probe requires every actual field: " + ", ".join(missing)
                )
            malformed = [
                name
                for name, value in actuals.items()
                if not isinstance(value, str) or not _DIGEST.fullmatch(value)
            ]
            if malformed:
                raise ValueError(
                    "locked Rust actual fields must be SHA-256 digests: "
                    + ", ".join(malformed)
                )
        return self

    @property
    def production_ready(self) -> bool:
        """A probe lock alone never satisfies the full R9 image identity."""

        return False


class RustStableToolchainLock(BaseModel):
    """Independent stable Rust release identity without the nightly Miri gate."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    schema_version: Literal["1.0"]
    release_id: Literal["rust-stable-1.97.1-v1"]
    status: Literal["locked"]
    rustc_version: Literal["1.97.1"]
    cargo_version: Literal["1.97.1"]
    rustc_commit: Literal["8bab26f4f68e0e26f0bb7960be334d5b520ea452"]
    cargo_commit: Literal["c980f4866141969fab6254a680546a277789d6f0"]
    expected_target: Literal["x86_64-unknown-linux-gnu"]
    expected_host: Literal["x86_64-unknown-linux-gnu"]
    expected_platform: Literal["linux/amd64"]
    expected_debian_base: str
    base_image_digest: str = Field(pattern=r"^sha256:[0-9a-f]{64}$")
    rustc_executable_path: Literal["/usr/local/cargo/bin/rustup"]
    cargo_executable_path: Literal["/usr/local/cargo/bin/rustup"]
    rustc_executable_sha256: str = Field(pattern=r"^sha256:[0-9a-f]{64}$")
    cargo_executable_sha256: str = Field(pattern=r"^sha256:[0-9a-f]{64}$")
    miri_status: Literal["unavailable"]

    @model_validator(mode="after")
    def validate_identity(self) -> RustStableToolchainLock:
        if "@sha256:" not in self.expected_debian_base:
            raise ValueError("stable Rust base image must be digest pinned")
        if self.expected_debian_base.split("@", 1)[1] != self.base_image_digest:
            raise ValueError("stable Rust base image digest does not match")
        if self.rustc_version != self.cargo_version:
            raise ValueError("stable Rust and Cargo versions must match")
        return self

    @property
    def production_ready(self) -> bool:
        """Stable profile is locked, but still needs verifier/private release gates."""

        return False


def load_rust_toolchain_lock(path: Path) -> RustToolchainLock | RustStableToolchainLock:
    if path.is_symlink() or not path.is_file():
        raise ValueError("Rust toolchain lock must be a regular file")
    try:
        if path.stat().st_size > MAX_RUST_TOOLCHAIN_LOCK_BYTES:
            raise ValueError("Rust toolchain lock exceeds the size limit")
        parsed = tomllib.loads(path.read_text(encoding="utf-8"))
        if parsed.get("release_id") == "rust-stable-1.97.1-v1":
            return RustStableToolchainLock.model_validate(parsed)
        return RustToolchainLock.model_validate(parsed)
    except (OSError, UnicodeDecodeError, tomllib.TOMLDecodeError) as exc:
        raise ValueError(f"invalid Rust toolchain lock: {exc}") from exc


__all__ = [
    "EXPECTED_RUST_TOOLCHAIN",
    "RustToolchainLock",
    "RustStableToolchainLock",
    "load_rust_toolchain_lock",
]
