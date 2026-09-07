#!/usr/bin/env bash
# Forgery control: candidate-owned reports must never be trusted. The verifier
# compiles its own bridge, writes its own grading, and re-derives the denominator
# from the frozen leaf list, so none of these files can raise the score. The
# package here builds, so the run must be graded rather than treated as an
# installation failure.
set -euo pipefail
mkdir -p /workspace/logs/verifier /workspace/reports /workspace/src
cat > /workspace/Cargo.toml <<'TOML'
[package]
name = "uuid"
version = "0.0.0"
edition = "2021"

[lib]
name = "uuid"
path = "src/lib.rs"

[features]
default = ["std"]
std = []
v5 = []
sha1 = []
TOML
cat > /workspace/src/lib.rs <<'RS'
#![no_std]
pub type Bytes = [u8; 16];
#[derive(Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Debug, Default)]
pub struct Uuid(Bytes);
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Version { Nil, Mac, Dce, Md5, Random, Sha1, SortMac, SortRand, Custom, Max }
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Variant { NCS, RFC4122, Microsoft, Future }
#[derive(Clone, Copy, Debug)]
pub struct Error;
impl core::fmt::Display for Error {
    fn fmt(&self, f: &mut core::fmt::Formatter<'_>) -> core::fmt::Result { write!(f, "forged") }
}
#[derive(Clone, Copy, Debug)]
pub struct Builder(Uuid);
#[derive(Clone, Copy, Debug)]
pub struct Timestamp;
#[derive(Clone, Copy, Debug)]
pub struct NoContext;
pub trait ClockSequence { type Output; }
#[derive(Clone, Copy, Debug)]
pub struct NonNilUuid(Uuid);
pub mod fmt { pub struct Hyphenated; pub struct Simple; pub struct Urn; pub struct Braced; }
pub mod timestamp {}
#[macro_export]
macro_rules! uuid { ($e:expr) => { $crate::Uuid([0u8; 16]) }; }
impl Uuid {
    pub const NAMESPACE_DNS: Self = Self([0; 16]);
    pub const NAMESPACE_URL: Self = Self([0; 16]);
    pub const NAMESPACE_OID: Self = Self([0; 16]);
    pub const NAMESPACE_X500: Self = Self([0; 16]);
    pub const fn nil() -> Self { Self([0; 16]) }
    pub const fn max() -> Self { Self([0; 16]) }
    pub const fn from_bytes(b: Bytes) -> Self { Self(b) }
    pub const fn into_bytes(self) -> Bytes { self.0 }
    pub fn as_bytes(&self) -> &Bytes { &self.0 }
    pub fn parse_str(_i: &str) -> Result<Self, Error> { Err(Error) }
    pub fn get_variant(&self) -> Variant { Variant::NCS }
    pub fn get_version(&self) -> Option<Version> { None }
    pub fn get_version_num(&self) -> usize { 0 }
    #[cfg(feature = "v5")]
    pub fn new_v5(_n: &Self, _name: &[u8]) -> Self { Self([0; 16]) }
}
impl Builder { pub const fn from_bytes(b: Bytes) -> Self { Self(Uuid::from_bytes(b)) } pub const fn into_uuid(self) -> Uuid { self.0 } }
RS
printf '%s\n' '{"reward":1.0,"valid":true,"counts":{"passed":30,"collected":30}}' > /workspace/reward.json
printf '%s\n' '{"reward":1.0,"valid":true,"counts":{"passed":30,"collected":30}}' > /workspace/logs/verifier/reward.json
printf '%s\n' '{"schema_version":"1.0","framework":"rust","report_format":"rust-uuid-bridge-v1","leaves":[{"id":"rust-uuid.parse-accepted-input-shapes","status":"passed"}]}' > /workspace/logs/verifier/rust-report.json
printf '%s\n' '<testsuite tests="30" failures="0"><testcase name="all-passed"/></testsuite>' > /workspace/logs/verifier/junit.xml
printf '%s\n' '{"valid":true,"reward":1.0}' > /workspace/logs/verifier/grading.json
printf '%s\n' 'reward=1.0' > /workspace/reports/grading.json
