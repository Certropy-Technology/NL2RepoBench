# go-radix instruction revalidation blocker

## Classification

- Task: `go-radix`
- Revision: `54df44f2176c4a553657a4f0dbe6fdb108288be3`
- Current source digest after instruction migration: `sha256:23a9fa07112c625cb49cadfc9945011b96a5fa997c4f70f85cc17b4ea56ee879`
- Frozen upstream source archive digest: `sha256:71091da25cb789fffd397ff8b4e1b460e88dda2ef31ae981d520426f26b8ff47`
- Frozen upstream source archive size: `30720` bytes
- Oracle bundle digest and size: `sha256:892a9726938a9bec8afad2a7b94ac86d7ddf653a8dcdf52dcd0e1a04e6c39f4b`, `803` bytes
- Oracle bundle inventory: one `solve.sh` file, `1418` bytes after unpacking; it contains no source archive or installable source payload.
- Failure class: `artifact-or-verifier`
- Network policy: `no-network`; no source host, registry, DNS, or Go proxy was authorized.

## Validation completed

- Queue digest check: passed; queue expects `sha256:23a9fa07112c625cb49cadfc9945011b96a5fa997c4f70f85cc17b4ea56ee879`.
- Declared private artifacts: Oracle `803/803`, module bundle `412/412`, verifier bundle `1382/1382`; all SHA-256 checks passed.
- `uv run nl2repo task validate-source catalog/sources/go-radix`: exit `0`.
- `uv run python scripts/validate_instruction_quality.py`: exit `0` (`instruction quality passed`).
- Go shell syntax, JSON, and TOML checks: exit `0`.
- Production compile A with locked `toolchain.go.lock.toml` and parent private artifact root: exit `0`.
- Production compile B with the same inputs: exit `0`.
- Compile manifest A and B: both `sha256:e18be2d81a535656ffd0d4a9993de27e1dff019a96e5566f5bd48a0a4aec206b`.
- Full compiled file-list digest A and B: both `sha256:920fb4f13bcdd66964a0b459ce2c3119f0bfafd8033e9992b7ed64d994134e22`.
- Harbor Oracle and controls: not run because the Oracle payload is absent and its `solve.sh` requires forbidden runtime GitHub access.

## Local recovery search

All searches were bounded and performed offline. No candidate was accepted by filename,
directory name, or archive format alone.

1. Command: `tar -tvf .nl2repo/artifacts/private/sha256/89/892a9726938a9bec8afad2a7b94ac86d7ddf653a8dcdf52dcd0e1a04e6c39f4b`; exit `0`. Result: the complete bundle inventory contains only `solve.sh` (803-byte outer bundle; 1418-byte extracted script), with no `source.tar`.
2. Command: `for root in .nl2repo/authoring-live/worktrees .nl2repo/authoring-live/handoffs .nl2repo/authoring-live/discovery; do find "$root" -path '*go-radix*' -print; done`; exit `0` (bounded output). Result: task-local metadata/evidence and retained authoring records only; no frozen source archive. The retained run archive was also checked and contained receipts/workspace outputs but no frozen Oracle archive.
3. Command: `git rev-list --objects --all | rg 'go-radix|radix.*source\\.tar'`; exit `0`. Result: catalog source and generated projection paths only; no source archive object.
4. Command: `find .nl2repo/artifacts/private/sha256 -type f -name '71091da25cb789fffd397ff8b4e1b460e88dda2ef31ae981d520426f26b8ff47'`; exit `0`, no output. Result: no CAS object matched the frozen source archive digest; the declared Oracle, module, and verifier objects were separately present and hash-valid.
5. Command: `find "$(go env GOMODCACHE)/github.com/armon/go-radix" -type f`; exit `1` because the task module-cache directory does not exist. Result: no `github.com/armon/go-radix` download cache was present; the Go build cache is compiled output and cannot prove archive bytes.
6. Command: `rg -n '54df44f2176c4a553657a4f0dbe6fdb108288be3|71091da25cb789fffd397ff8b4e1b460e88dda2ef31ae981d520426f26b8ff47' .nl2repo/authoring-live/state .nl2repo/authoring-live/handoffs`; exit `0`. Result: retained claims/logs reference runtime fetches and old receipts but contain no hash-verifiable source payload.

## Next step

The parent integrator must recover or register a private payload whose inner source archive is
exactly `30720` bytes with SHA-256
`71091da25cb789fffd397ff8b4e1b460e88dda2ef31ae981d520426f26b8ff47`, and whose revision is
`54df44f2176c4a553657a4f0dbe6fdb108288be3`. After CAS registration, update only the private
Oracle bundle reference through the parent compiler flow, compile twice again, then run a
fresh Harbor `0.21.0` Oracle and all supported controls. Do not reuse prior receipts.
