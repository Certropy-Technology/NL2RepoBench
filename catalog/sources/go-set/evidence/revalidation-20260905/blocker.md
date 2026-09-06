# Revalidation blocker: missing frozen Oracle payload

- Task: `go-set`
- Source digest (current queue and pre-change validation): `sha256:3b2e0b9e88c8928b56b0ea19df9a9f2b1043b7993d0d16f5fe7ca9f49c405910`
- Frozen upstream revision: `da03b7639be5170e7b8fc7183b2d4663a4133419`
- Required source archive: `sha256:9d77361bf07b5ecfcc236a1972f9aa524209dab5f300e774ca5b068a1aea4880`, `266240` bytes
- Oracle bundle checked: `sha256:39dbabcf918c000c12f76b3aee51fbf2cf84be6da4cf031150e594d16eae548c`, `764` bytes
- Oracle bundle inventory: `solve.sh` only; it invokes `git clone` for the upstream repository and does not contain a source archive or installable package.

## Offline checks

The three declared private CAS artifacts were present and byte-verified before this blocker was written:

| Artifact | Digest | Declared/actual size |
| --- | --- | ---: |
| Oracle bundle | `sha256:39dbabcf918c000c12f76b3aee51fbf2cf84be6da4cf031150e594d16eae548c` | `764` / `764` |
| Go module bundle | `sha256:83178d96bc4df481bfff27f44d2c457d6ac01804ba22d57a026226acbac43af3` | `116579` / `116579` |
| Verifier bundle | `sha256:8076e8dda777bee1af3a3d71a12d674052f6d24f330fc737d11902356f1d31af` | `1493` / `1493` |

The Oracle bundle was inspected with `file`, `tar -tvf`, and `tar -xOf ... solve.sh`.
The following bounded local locations were searched for bytes matching the required
archive digest and size:

- Parent-owned CAS `artifacts/private/`.
- Authoring handoff directories.
- Retained worktree directories.
- Retained Harbor runs `runs/`.
- Session handoffs `subagent-artifacts/`.

The retained `archive-receipts/go/go-set-80552b8948f3ae8d.json` and historical
authoring run metadata describe the old source workspace, but contain no local source
archive bytes. No cache zip, module cache, alternate archive format, or reconstructed
payload was accepted as equivalent.

## Commands and results

All commands were run without authorizing network access:

```text
uv run nl2repo task validate-source catalog/sources/go-set
  exit 0; source_digest=sha256:3b2e0b9e88c8928b56b0ea19df9a9f2b1043b7993d0d16f5fe7ca9f49c405910

uv run nl2repo harbor compile catalog/sources/go-set --output .nl2repo/go-set-revalidation-compile-a --toolchain toolchain.go.lock.toml --artifact-root <parent-artifact-root> --allow-private
  exit 0; bundle_manifest_sha256=sha256:5008beac2865cf9abd1d5511f71752eb2f91b43e6e9911023f4d2af91aa14935

uv run nl2repo harbor compile catalog/sources/go-set --output .nl2repo/go-set-revalidation-compile-b --toolchain toolchain.go.lock.toml --artifact-root <parent-artifact-root> --allow-private
  exit 0; bundle_manifest_sha256=sha256:5008beac2865cf9abd1d5511f71752eb2f91b43e6e9911023f4d2af91aa14935

cmp compile-a/go-set/bundle.manifest.json compile-b/go-set/bundle.manifest.json
  exit 0; byte-identical
```

## Failure class and next step

- Failure class: `artifact`
- Status: revalidation blocked; the existing lifecycle and production evidence are unchanged.
- Not run: Harbor Oracle, empty, stub, forgery, and offline controls. Running the existing Oracle would violate the task's NoNetwork policy because its only source path is a runtime GitHub clone.
- Next step: obtain an authorized local copy of the exact `266240`-byte archive whose SHA-256 is `sha256:9d77361bf07b5ecfcc236a1972f9aa524209dab5f300e774ca5b068a1aea4880`. Register it in parent-owned CAS, replace the private Oracle bundle without changing the declared revision or digest, compile twice, then run the complete Harbor 0.21.0 matrix and persist durable receipts.
