# Project Description

This candidate is retained as blocked at the immutable Google Code Search
revision `74a12a911a79b901d1158c48d011b2da1b090fc9`. The source is a pure-Go
search/index project with regular-expression, trigram, sparse-set, on-disk
index, and command-line components.

## Supports

No production task is currently supported. The source archive and license were
verified, and the upstream tests pass on Linux/amd64 with Go `1.26.5`, but a
production task needs a complete offline dependency/verifier artifact closure
and a reviewed child-side adapter. No `catalog/tasks/go-codesearch` runtime is
created while this blocker remains.

## API Usage Guide

The public source includes packages under `index`, `regexp`, and `sparse`, plus
the `cgrep`, `cindex`, `csearch`, and `csweb` commands. The index package opens,
maps, writes, checks, and searches files; the commands traverse arbitrary file
trees, read external files, optionally index ZIP archives, and serve HTTP.
The Linux implementation uses `syscall.Mmap`, while other files contain
platform-specific mmap and unsafe code. These behaviors cannot be reduced to a
reviewed deterministic JSON child protocol without choosing a narrower public
contract and freezing its adapter and test denominator.

## Implementation Notes

The prior stream-error patch proposed a bounded bridge for a subset of APIs,
but its referenced private Oracle, verifier, and module bundles are absent from
the available CAS. It therefore cannot be compiled or treated as evidence of a
complete task. Remediation is to decide and review a deterministic scope,
materialize the complete private artifacts, implement the separate verifier,
and rerun collection, Oracle, and controls against the resulting final bundle.

## Blocker

The blocker is verifier and artifact infrastructure, not a fabricated model
score. The source-health probe is recorded in
`evidence/dependency-probe.log`; it is not a production denominator.
