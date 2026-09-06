# jsonlines instruction-revalidation blocker

Revalidation stopped before compile and Harbor execution. The queue requires the
current migrated source digest
`sha256:3a185f61141fed92c162d5c0ece99edc9dd7357081018ccc82ff63579e7dbc49`;
`uv run nl2repo task validate-source catalog/sources/jsonlines` reported that
same digest and exited `0`. The instruction SHA-256 is
`sha256:5e69984b3abce556f21a565885c3863f9a4ad4bdbea1ac095e0accb6ebc0ac9e`.

The current lifecycle and `production-evidence.json` were deliberately left
unchanged. Their receipts predate the migrated instruction and are not claimed
as current revalidation evidence.

## Missing private artifacts

| Declaration | Digest | Bytes | Configured private CAS result |
| --- | --- | ---: | --- |
| `dependencies.lock_artifact` | `sha256:20ed7127abfff312a28b82beacd113204107222df88db0a656bab6403a6c2034` | 558 | missing |
| `verifier.bundle` | `sha256:e1e953f420f49ef8d846cbc415e40ac272c1abbf26c736a09aadb9beb41d8ba3` | 30,720 | missing |
| `oracle_bundle` | `sha256:823aa329652e4b1ed29375c82b7abbddc0aaea2c87c6fcf0190674eff8d0792f` | 81,920 | missing |

The checked-in generated runtime supplies two exact inner inputs but not either
missing outer private bundle:

- `catalog/tasks/jsonlines/environment/candidate-requirements.lock.txt` is
  exactly 558 bytes with SHA-256
  `20ed7127abfff312a28b82beacd113204107222df88db0a656bab6403a6c2034`.
- `catalog/tasks/jsonlines/solution/source.tar` is exactly 71,680 bytes with
  SHA-256 `fd839af51a766d70dccb95db84e6bcf741f55b01ed756b817be4838f202407a6`.
  This agrees with `task.toml`, `solution/solve.sh`, and the frozen source
  identity for revision `43d1a30b9634f8b715b6af3f2473927caa1e704d`.

Those members do not prove the missing bundle layouts, ordering, or outer bytes,
so they are not a replacement proposal.

## Bounded local recovery search

All checks were performed without external-network authorization:

1. The configured private CAS was checked at the digest-derived paths; all
   three declarations were absent.
2. `catalog/tasks/jsonlines/` was inspected. It contains the exact dependency
   lock and source archive above, plus the extracted verifier files, but no
   30,720-byte verifier bundle or 81,920-byte Oracle bundle.
3. Historical local worktrees, retained recovery manifests, and agent handoff
   artifacts were searched for the exact declared SHA-256 values and for files
   with the declared outer sizes. No hash-matching outer bundle was found. A
   broader archive scan was bounded by timeout and produced no exact match.
4. Git history was checked for the two declared bundle digests. It identifies
   the original task-introduction commit but contains no Git-tracked private
   bundle bytes.

`artifact-check.json` records the exact source/lock recovery evidence and
missing outer artifacts in machine-readable form.

## Next step

Failure class: `artifact-or-verifier`.

The parent integrator must recover or construct a separately reviewed private
Oracle and verifier bundle from trusted local inputs, register its new digest in
the shared CAS, update the source declaration, then run double compilation and
the complete NoNetwork Oracle/control matrix. No source host, registry, DNS, or
external service was authorized here; no compile, Harbor Oracle, or control was
run with unresolved artifacts.
