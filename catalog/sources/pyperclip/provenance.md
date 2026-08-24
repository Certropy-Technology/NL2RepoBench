# Pyperclip Repair Evidence

## Status

`oracle-passed`: remediation replaces the two-assertion unavailable-backend check with a separate, offline verifier and a deterministic adapter contract. The generic compiled Oracle passed `10/10` with reward `1.0`; empty/stub/forgery evidence is recorded in `provenance/oracle.md`, while timeout, blind review and pilot remain pending.

## Source and environment

- Upstream revision: `f5326bfd7c5448b40051dd261a7304657977b838`.
- License: BSD-3-Clause (`LICENSE.txt` at the frozen revision).
- Archive digest: `sha256:4e80effb92cd84116a2541bb5aa4df7d7832761c04600322f558265ba73c0275`.
- Runtime/base lock and package hashes: `evidence/environment-lock.json` and `evidence/wheelhouse.sha256`. All source, build, and wheelhouse probes used `.work/`; no large files were written to `/tmp`.

## Verifier contract

The separate verifier copies candidate workspace into a verifier-owned path, installs editable with `--no-index --no-deps --no-build-isolation`, and runs fixed tests as an unprivileged user with network disabled. It performs collection before execution and writes trusted `reward.json`, `grading.json`, and JSON leaf results. Frozen collection is 10 and fixed denominator is 10; skipped leaves are disallowed.

The fixture adapter is external to the candidate and returns only JSON-safe values. The candidate's lazy detector is tested in a headless environment and must raise `PyperclipException`; the in-memory pair is injected through `determine_clipboard` to test coercion and round trips without claiming desktop clipboard support.

## Bounded platform attempts

The Linux host has no display/session requirement for the repaired contract. Mocked xclip and Wayland probes completed successfully against the frozen source. Windows, macOS, Cygwin, WSL, Qt, and live helper processes were not available in this Linux verifier and remain unexercised; they are not auto-blocked, but should be covered by a platform matrix before publication.

## Local Oracle evidence

A bounded local Docker verifier run against the frozen upstream source completed with `collected=10`, `passed=10`, `skipped=0`, `valid=true`, and `reward=1.0` under `--network=none`. The source-only oracle bundle is addressed in `task.toml`; this is a task-local baseline evidence record, not a model run.
