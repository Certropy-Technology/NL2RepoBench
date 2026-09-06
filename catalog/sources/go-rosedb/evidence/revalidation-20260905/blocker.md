# Revalidation blocker: frozen Oracle source payload unavailable

- Task: `go-rosedb`
- Revalidation source digest: `sha256:63b5a06cabed533b7143d8bfbe8f1fa2667815351959b7926a8c855d301ce7bc`
- Frozen upstream revision: `bcb43052ada686ec6d1345328e8299f502d3ef01`
- Required source archive digest: `sha256:41153fd1e40c1e7b18b90d46cfcf3a4bdc93fdc54c286823d2966b01686f527e`
- Required source archive size: not declared in the source manifest or source-local freeze evidence.

## Declared private artifacts

All declared private artifacts were present and hash-verified before compilation:

| artifact | digest | size | result |
| --- | --- | ---: | --- |
| Oracle bundle | `sha256:3b1da7461f78e6260e434b32508dc80ab31508589fe42b484b713edaaef19716` | 1,164,929 bytes | matched |
| Go module bundle | `sha256:ac4281abe988fe298d9725768acefdd698c427441e9c8cd24654cde765cf821a` | 1,184,053 bytes | matched |
| Verifier bundle | `sha256:515d84e66eaa8f83b302a1eb7a603565067e1d161a3be25c207885bc66bee62a` | 717 bytes | matched |

## Bounded local recovery

The current Oracle bundle was inspected offline. Its inventory contains `solve.sh`,
`go.mod`, `go.sum`, and `module-bundle/`; it contains no `source.tar`,
`oracle-package/`, or installable frozen source payload. The current generated
runtime has no embedded source archive. The following local locations were searched
without finding a file whose SHA-256 equals the required source archive digest:

- `catalog/tasks/go-rosedb/solution/`
- repository-local authoring-work archives
- repository-local authoring handoff archives
- repository-local authoring worktrees
- repository-local historical session records for `go-rosedb`
- repository-local run archives
- local worker handoff artifacts

The historical claim and provenance confirm the same revision and digest but do not
retain source bytes. A module-cache archive or a different archive format was not
treated as equivalent.

## Commands and results

| command | result |
| --- | --- |
| `uv run nl2repo task validate-source catalog/sources/go-rosedb` | exit 0; source digest `sha256:63b5a06cabed533b7143d8bfbe8f1fa2667815351959b7926a8c855d301ce7bc` |
| `uv run --frozen --project harbor-runner harbor --version` | exit 0; Harbor `0.21.0` |
| `uv run nl2repo harbor compile ... --toolchain toolchain.go.lock.toml --artifact-root .nl2repo/artifacts --allow-private` | exit 0, twice; byte-identical 1,281-file bundles; manifest SHA-256 `42db439844885fe6d49d863a4cf98c80392d7ed001d2f7d98d0e3e7522a6352e` |
| `tar -tf <Oracle CAS artifact>` | exit 0; no source archive or installable Oracle source payload |
| bounded `find`/SHA-256 search over the local recovery paths above | exit 0; no matching `sha256:41153fd1e40c1e7b18b90d46cfcf3a4bdc93fdc54c286823d2966b01686f527e` file |

## Blocked stage and next step

Failure class: `artifact-or-verifier` (NoNetwork Oracle source payload unavailable).

The existing `harbor/solution/solve.sh` performs a runtime GitHub fetch. No source
host was authorized and no Harbor Oracle or control was run after instruction
migration. The next step is for the parent to recover or construct a private bundle
containing bytes matching the frozen revision and source archive digest, register it
in parent-owned CAS, update the private Oracle binding, compile the changed bundle
twice, and rerun Oracle plus every supported control. This blocker does not change
`task.toml` lifecycle or `production-evidence.json`.
