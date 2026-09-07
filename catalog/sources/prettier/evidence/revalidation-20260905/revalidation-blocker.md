# Prettier instruction revalidation blocker

Status: `artifact-or-verifier-blocked`

The queue entry requires a fresh post-instruction-migration final manifest and
NoNetwork Oracle/control receipts. The queue source digest is
`sha256:330d7dde4b6127781b2aa200b09e2534b6d6429fbb64d66bdef5c156d191eb7d`.
`uv run nl2repo task validate-source catalog/sources/prettier` completed with
exit code 0 and reported that digest before this evidence was written.

## Verified declarations

The source declares revision `d9969c57343d48a4d1fac12f3f5c4b2fd82d8da5`,
source digest `sha256:5fced228479ca4235fcb722849f8e1f000640109596f9f1fcea69349c9e49523`,
and Node 24.19.0/npm 11.17.0. The four private artifact references were
checked against the local artifact store by exact byte size and SHA-256:

| artifact | declared size | declared SHA-256 | result |
| --- | ---: | --- | --- |
| npm dependency bundle | 441 | `sha256:5a8aa0bf14255b209f02b32406efb53b91ddc5375b083e7227bb4256c9b4993e` | exact match |
| command plan | 176 | `sha256:ecade7e4a7652dc33367d2c5ce2971815591d9ae5bc4482e009eb1fa3af6552a` | exact match |
| private test bundle | 4498 | `sha256:f98a038556db218216adbbbb73aee0b9e5153597bb26311b55175ec6db301c43` | exact match |
| Oracle bundle | 3109794 | `sha256:5b013b000ababaf1f51cd5cc8faad6127e15e51dfe3f7ce16c0391d433b384bf` | exact match |

The Oracle bundle contains only `prettier-3.10.0-dev.tgz` and `solve.sh`.
The package payload is 3,111,428 bytes with SHA-256
`sha256:46b3480b5463675322ee8dd080d3d3e993e6ba709c70cef183bc75b84cb20521`
and identifies as `prettier@3.10.0-dev`; it is not the frozen upstream
source archive. The generated solution script still executes a runtime
`git fetch` from GitHub and its source archive digest check therefore cannot
complete under the required universal NoNetwork policy.

## Commands and results

| command | exit/result |
| --- | --- |
| `uv run nl2repo task validate-source catalog/sources/prettier` | `0`; queue source digest verified |
| `uv run --frozen --project harbor-runner harbor --version` | `0`; Harbor `0.21.0` |
| `uv run nl2repo task lint-network --tasks-root catalog/sources --include-generated` | not run here; source policy is explicitly `no-network`, and generated runtime is parent-owned |
| exact-size/SHA-256 scan of all four declared local CAS artifacts | passed; all four exact matches |
| bounded local search for frozen source archive by declared digest | no match established before bounded scan timeout |
| `uv run nl2repo harbor compile ... --toolchain toolchain.node.lock.toml --artifact-root .nl2repo/artifacts --allow-private` | not run; compilation cannot produce a valid fresh Oracle while the only Oracle payload fetches GitHub |
| Harbor Oracle and controls | skipped; no valid NoNetwork source payload exists |

## Remediation

Parent must recover or register an exact archive/tree for revision
`d9969c57343d48a4d1fac12f3f5c4b2fd82d8da5` with the declared source digest,
or replace the runtime-fetching Oracle bundle with a parent-reviewed private
payload. After that, compile twice with `toolchain.node.lock.toml`, compare
the final manifests, and run a fresh NoNetwork Oracle plus empty, stub,
forgery, install-script, loader-hook, hang, and offline controls. No lifecycle,
production-evidence, generated projection, or private payload was modified by
this worker.
