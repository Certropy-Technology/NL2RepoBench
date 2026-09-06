# NoNetwork Oracle Replacement Proposal

## Scope

The current private Oracle bundle is present and hash-verified, but its
`solve.sh` fetches GitHub before generating an embedded pure-Python task
adaptation. Runtime network is forbidden for Oracle in this revalidation.

The ignored replacement bundle is available for parent-only review and CAS
registration at:

```text
.nl2repo/jiter-revalidation-20260905/replacement-oracle.tar
```

It is not a source archive and is not copied into this public source tree.

## Proposed Binding

| Field | Value |
| --- | --- |
| media type | `application/vnd.nl2repobench.private-bundle+tar` |
| outer SHA-256 | `sha256:a8c5c33e7b32bffc8a055e4fece0a01450e5e1dca9fdc39624edcdfd41b1cc6a` |
| outer size | `10240` bytes |
| archive entry | `solve.sh`, mode `0755`, size `5362` bytes |
| inner SHA-256 | `sha256:241e0b37e143b109716c609e6c1dce24ef73bac9d8e142fec457e7b53bee86b2` |
| prior Oracle outer SHA-256 | `sha256:019efb1b405ef966bcac507279b3c3532d439c62301a828c2957c742d336a260` |
| prior `solve.sh` SHA-256 | `sha256:d8a489b3b3f6e11bebb07d857cdd4c27b613eefc77ab8618d99dedadb90eeb3a` |

The parent may replace only `[oracle_bundle]` after independently reproducing
the tar, verifying all hashes, and completing a semantic review.

## Exact Change

The replacement deletes only the old script's declarations for the upstream
URL/revision/archive hash and its `git clone`, `git fetch`, `git archive`, and
archive checksum preflight. Its final status message is updated to say that it
built the existing pure-Python task adaptation. No generated package file,
parser behavior, verifier contract, command, or control behavior is changed.

The generated adaptation body from `rm -rf "$ROOT"/*` through its final
`return value` is byte-identical in both scripts:

```text
sha256:d5236528d8e091d7a9d53f72bbc3ffdf8b6d11d09175380166faf2b3f910ad7e
5215 bytes
```

Static inspection of the replacement has no URL, Git, curl, wget, registry, or
DNS command. `bash -n` passed.

## Local Verification

The replacement was executed locally and the private verifier's frozen
32-scenario contract passed `32/32`, `reward = 1.0`. The compact local smoke
receipt was deliberately not copied here because it contains private leaf IDs;
its ignored-file SHA-256 is
`sha256:9a650376715b5b8c6c5a9f879a717a76fce68feb3c2216325010c038b009321e`.

One Docker `--network none` smoke attempt was bounded to 300 seconds and timed
out before execution while the shared Docker host had 38 running containers.
This is infrastructure evidence, not an Oracle result. No Harbor compile or
Harbor Oracle/control run was started against the unregistered replacement.

## Parent Next Step

Reconstruct and register the proposed bundle in private CAS, update
`[oracle_bundle]`, recompile twice, then rerun fresh Harbor Oracle, empty,
stub, forgery, and offline controls. Reject this proposal and retain the
current packaged lifecycle if semantic review finds the removed preflight had
any behavior beyond unused source verification.
