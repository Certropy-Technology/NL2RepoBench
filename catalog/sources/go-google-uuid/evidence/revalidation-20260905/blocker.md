# Instruction revalidation blocker

- Task: `go-google-uuid`
- Revalidation source digest (current queue):
  `sha256:c56d9e2d6b74d86702792b51cf74bffbd4cf6f3e194bed1e8fd7a5a2b50d3fa3`
- Frozen upstream revision:
  `0f11ee6918f41a04c201eceeadf612a377bc7fbc`
- Frozen source archive digest:
  `sha256:e24d1eb2f3787e8e47cacff5c9ef5e7286ef6406a22da2da036fd2a19fa5c049`
- Existing lifecycle and production evidence were preserved. No runtime or
  production evidence was changed.

## Artifact checks

All declared private CAS objects were present and byte-valid before compile:

| artifact | declared size | declared SHA-256 | result |
| --- | ---: | --- | --- |
| Oracle bundle | 634 bytes | `sha256:b2e6480ce864c6679e1390fd7e5d18c99caee12048a89cd9b9175ee598ef92b0` | exact |
| Go module bundle | 505 bytes | `sha256:c37e4b325aea1739f2cd129def35c1a5accdbe4b4c8952bf26e214bb18051e0c` | exact |
| verifier bundle | 585 bytes | `sha256:d55dc65ce99a7d706ba1ad135ec9e1d571ae6d9ff1b62a2488074a52c1f09999` | exact |

The Oracle bundle contains only `solve.sh`; it runs `git fetch` against
`https://github.com/google/uuid` and does not contain `source.tar`. The available
Go module cache contains `github.com/google/uuid` v1.6.0, whose zip digest is
`sha256:d0f02f377217f42702e259684e06441edbf5140dddcc34ba9bea56038b38a6ed`,
not the frozen archive digest. It is a different revision and archive payload
and was not substituted.

## Bounded recovery search

The following local sources were checked without network access:

1. Current Oracle bundle and current `catalog/tasks/go-google-uuid/` projection:
   no source archive; both expose the fetch-only Oracle script.
2. Task-local `evidence/`, `harbor/`, and retained task files: no source archive.
3. Historical local worktrees under
   `<integration-root>/.nl2repo/authoring-live/worktrees`
   and retained `go-google-uuid` compiled/control reports: no matching source
   archive or payload bytes.
4. Local handoff records under
   `<agent-session-root>/subagent-artifacts/handoffs`:
   no source payload matching the frozen revision and digest.
5. Local Go module cache under `<go-cache-root>/pkg/mod`: only the nonmatching v1.6.0
   zip was available.

## Commands and results

```text
uv run nl2repo task validate-source catalog/sources/go-google-uuid
exit 0; source_digest=sha256:c56d9e2d6b74d86702792b51cf74bffbd4cf6f3e194bed1e8fd7a5a2b50d3fa3

uv run nl2repo harbor compile catalog/sources/go-google-uuid --output .nl2repo/go-google-uuid-compile-a --toolchain toolchain.go.lock.toml --artifact-root <integration-root>/.nl2repo/artifacts --allow-private
exit 0; manifest=sha256:070aefcab148a1304d034f72243544806eea6cd4160bc8dda2045955d200eaf9

uv run nl2repo harbor compile catalog/sources/go-google-uuid --output .nl2repo/go-google-uuid-compile-b --toolchain toolchain.go.lock.toml --artifact-root <integration-root>/.nl2repo/artifacts --allow-private
exit 0; manifest=sha256:070aefcab148a1304d034f72243544806eea6cd4160bc8dda2045955d200eaf9

cmp .nl2repo/go-google-uuid-compile-a/go-google-uuid/bundle.manifest.json .nl2repo/go-google-uuid-compile-b/go-google-uuid/bundle.manifest.json
exit 0; byte-identical=true

uv run --frozen --project harbor-runner harbor --version
exit 0; 0.21.0

bash -n catalog/sources/go-google-uuid/harbor/controls/*.sh
exit 0; seven control scripts parsed successfully
```

## Blocker and next step

`failure_class = artifact-or-verifier`: the frozen Oracle source payload cannot
be executed under the mandatory NoNetwork policy because its only source
acquisition path is a runtime GitHub fetch, and no exact local archive is
available to replace it. Harbor Oracle and controls were intentionally not run;
old receipts were not reused. The next step is for the parent integrator to
locate or register a CAS object whose bytes exactly match the frozen archive
digest, then recompile this source twice and rerun the complete Oracle/control
matrix against the new manifest.
