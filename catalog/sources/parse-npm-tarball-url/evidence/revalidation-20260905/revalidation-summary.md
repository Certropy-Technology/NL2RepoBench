# parse-npm-tarball-url instruction revalidation

## Result

This post-migration revalidation is **blocked on artifact closure**. The queue
entry requested a fresh compile and Harbor matrix against source digest
`sha256:0e71a37a937bf3301b0bcb7bda0902ff35d83e71fdf169e0673e4e36e57c7df5`,
which `validate-source` confirmed before this evidence was written. No task
metadata, lifecycle, production evidence, generated projection, or historical
receipt was changed.

The source archive is locally reproducible from the existing generated
projection (`51200` bytes, SHA-256
`cd10dd7f52286e08ac646447dab6312bc072f89b5deca56122bb9405f429ccf2`), but
that projection is parent-owned and is not accepted as a replacement for the
missing private runtime artifacts. The required fresh compile failed closed
before bundle generation because the declared npm dependency artifact was not
available in the local CAS.

## Commands and results

All runtime/network-sensitive commands were run with the task's declared
NoNetwork policy; no source host, registry, DNS, or external service was
authorized.

| command | result | evidence |
| --- | --- | --- |
| `uv run nl2repo task validate-source catalog/sources/parse-npm-tarball-url` | passed; source digest `sha256:0e71a37a937bf3301b0bcb7bda0902ff35d83e71fdf169e0673e4e36e57c7df5` | pre-mutation queue/source check |
| `uv run nl2repo --help` | passed | CLI inventory |
| `uv run --frozen --project harbor-runner harbor --version` | passed; Harbor `0.21.0` | runtime inventory |
| `uv run nl2repo harbor compile catalog/sources/parse-npm-tarball-url --output <staging-output>/parse-npm-tarball-url --toolchain toolchain.node.lock.toml --artifact-root <private-cas> --allow-private` | failed closed; missing `sha256:ec634ced2458053d631f3c0700c791678d463198f966e19d4bcd2815808b3057` | compile probe |
| bounded local CAS exact-byte scan | passed as a negative result; dependency artifact missing (declared `135192` bytes), test bundle `sha256:6c08d505abd0581f533082cba7abb65edac25522abdd09867056cb36c23c8824` (`3430` bytes), and Oracle bundle `sha256:3e4f7b8a4624900ad83a82abcdd61f3aab41b7a18188f86a46850f49b8acc4e3` (`13440` bytes) not found | artifact-check.json |
| bounded historical handoff/projection search | passed as a negative result; no accepted private dependency or Oracle payload beyond the existing generated projection | artifact-check.json |
| `uv run nl2repo task lint-network --tasks-root catalog/sources` | passed; `error_count=0` (repository warnings unrelated) | network gate |
| `bash -n` on task control scripts | passed | syntax gate |
| `node --check` on task private/runtime `.mjs` files | passed | syntax gate |
| `git diff --check` | passed | final hygiene gate |

The commands artifact was independently present at the declared exact CAS
location with size `236` bytes and SHA-256
`cab621dcaf7260f80d7c66f04c60ed005c26aa2b0a374856ead7c4cd08bf995e`; this
does not compensate for the missing dependency closure, test bundle, or Oracle
bundle and therefore no Harbor run was started.

## Gate matrix

| gate | status | reason |
| --- | --- | --- |
| source digest and source validation | passed | exact queue digest validated before mutation |
| immutable source payload | locally present only through parent generated projection | not copied or treated as a new private artifact |
| npm dependency closure | blocked | exact declared artifact missing from local CAS |
| private test bundle | blocked | exact declared `3430`-byte bundle absent from local CAS |
| Oracle bundle | blocked | exact declared `13440`-byte bundle absent from local CAS |
| compile twice | skipped | compiler failed before bundle creation |
| Oracle | skipped | no accepted current compiled bundle |
| empty/stub/forgery/offline controls | skipped | no accepted current compiled bundle; historical receipts are stale after instruction migration |

## Remediation

Parent should recover or register, outside this source-local patch, the exact
three missing private CAS objects after byte/size/provenance review: npm
dependency bundle `sha256:ec634ced2458053d631f3c0700c791678d463198f966e19d4bcd2815808b3057`
(`135192` bytes), test bundle
`sha256:6c08d505abd0581f533082cba7abb65edac25522abdd09867056cb36c23c8824`
(`3430` bytes), and Oracle bundle
`sha256:3e4f7b8a4624900ad83a82abcdd61f3aab41b7a18188f86a46850f49b8acc4e3`
(`13440` bytes). Then recompile twice from this source with the locked Node
toolchain and rerun a fresh Harbor 0.21.0 Oracle plus every supported control
under NoNetwork. Do not reuse the historical 2026-08-25 receipts.

