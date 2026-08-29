# Ruff bounded-contract traceability

| Private leaf | Public contract section | Frozen upstream evidence |
| --- | --- | --- |
| package metadata, version, console script | Package and command metadata | `pyproject.toml`, `python/ruff/` |
| help and rule documentation | `ruff check`, `ruff rule` | `crates/ruff/src`, `crates/ruff/tests/cli` |
| F401 default, JSON, stdin, `noqa`, fixing | `ruff check` | `crates/ruff/tests/cli/lint.rs` |
| TOML selection, ignore, line length, isolated, missing config | Lint configuration | `crates/ruff/tests/cli/lint.rs` and configuration snapshots |
| format stdin, check, rewrite, diff, final newline | `ruff format` | `crates/ruff/tests/cli/format.rs` |

The verifier invokes the candidate console entry point only in an unprivileged
subprocess. It does not import the candidate package in the trusted process.
Each leaf maps to a behavior explicitly described in `instruction.md`.
