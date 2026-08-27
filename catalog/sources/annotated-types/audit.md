# `annotated-types` authoring audit

Status: **awaiting-agent-run** after local source, verifier, and production
compile gates.  This record summarizes the frozen input and the task-local
checks; it does not claim that a future model Agent Run has been performed.

## Frozen source

- Upstream: `https://github.com/annotated-types/annotated-types`
- Revision: `ceb950e81a79403c911990ce960ecc6f46733508`
- Source archive: unprefixed `git archive --format=tar HEAD`
- License: MIT; license file is 1083 bytes and has SHA-256
  `fe1049884b1a0d9342901e88e07f32925d24b3121d9972b6a6805fb9824b095d`
- Archive SHA-256 and byte size are recorded in `task.toml` after the archive
  was produced twice from the detached revision.

The package is pure Python, has no runtime dependencies, and uses Hatchling as
its build backend.  The upstream tests collected 256 deterministic cases and
passed 256/256 under CPython 3.12 with plugin autoload disabled.

## Scope and verifier

The public contract covers the root exports, frozen metadata dataclasses,
grouped iteration semantics, protocol behavior, predicate representations,
generic `Annotated` aliases, and documentation aliases.  The private verifier
contains 60 fixed behavioral leaves and invokes candidate code only in a child
process with a candidate-owned import path.  It owns the collection, JUnit,
and reward reports.

## Network and artifact policy

The candidate and verifier run with no network.  The only build-time third-party
package is the hash-locked Hatchling build closure.  Oracle uses the bundled
archive and verifies its digest before restoring the source; it does not expose
the reference archive to the model Agent.
