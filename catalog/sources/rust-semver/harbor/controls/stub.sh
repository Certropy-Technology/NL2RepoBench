#!/usr/bin/env bash
# Stub control: a package that compiles and links but implements none of the
# contracted behaviour. The verifier must still collect all 26 leaves.
set -euo pipefail

find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
mkdir -p /workspace/src
cat > /workspace/Cargo.toml <<'CARGO_TOML'
[package]
name = "semver"
version = "0.0.0"
edition = "2018"

[features]
default = ["std"]
std = []

[lib]
path = "src/lib.rs"

[dependencies]
CARGO_TOML
cat > /workspace/Cargo.lock <<'CARGO_LOCK'
version = 4

[[package]]
name = "semver"
version = "0.0.0"
CARGO_LOCK
cat > /workspace/src/lib.rs <<'STUB_RS'
// Deliberately inert: present so the candidate package builds, absent behaviour.
#![no_std]
pub struct Version;
pub struct VersionReq;
pub struct Comparator;
pub struct Prerelease;
pub struct BuildMetadata;
pub enum Op { Exact }
pub struct Error;
STUB_RS
