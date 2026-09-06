# micromatch instruction-migration revalidation blocker

- Task: `micromatch`
- Revalidation date: `2026-09-05`
- Expected current catalog source digest: `sha256:08d22bd04498f6207436d3408f2fb5ce118a4aa48da5f31ec4840965e9f86262`
- Frozen upstream revision: `8bd704ec0d9894693d35da425d827819916be920`
- Frozen source archive digest: `sha256:cfb37abf1f9134a4160f8db24574d537d533b217c9708047c995dd3d346d6239`
- Lifecycle: unchanged at `controls-passed`; this is not a lifecycle transition.
- Historical `production-evidence.json`: unchanged. No generated projection or shared
  infrastructure was modified.

## Completed checks

`uv run nl2repo task validate-source catalog/sources/micromatch` passed and reported the
expected current catalog source digest. Harbor `0.21.0`, Node `24.19.0`, npm `11.17.0`,
and `toolchain.node.lock.toml` were used. The four declared private CAS objects were
present and matched their declared size and SHA-256 values:

| artifact | size | SHA-256 |
| --- | ---: | --- |
| dependency npm bundle | 583680 | `sha256:d5b3662d1978b0c00da652ffb1615f37f1fc12dfe2f9eadbf1d03342feab5ee4` |
| commands bundle | 10240 | `sha256:fda65a1fae7a54d9433921e0c28ac2311ec9dbefc0b8c54efe69c954ad4433f7` |
| private tests bundle | 30720 | `sha256:7a8e7257ad49f7829472c838cb98e488a786643406604c389ec9e9b47eb841c0` |
| Oracle bundle | 655360 | `sha256:57823e7d3693383a5eb095c55db2ca694ba32305e0a8ed5e4a679c3336b89363` |

The Oracle bundle was unpacked offline. It contains `package-lock.json`, `solve.sh`, and
`source.tar`; the latter is 645120 bytes and hashes to the frozen source digest above.
The materializer verifies that digest before copying the source and does not execute a
network fetch. The lock file only contains package metadata and no runtime source-fetch
command.

## Deterministic production compiles

Both commands used the current source, the locked Node/npm toolchain, the parent private
CAS, `--allow-private`, and no `--allow-incomplete`:

```text
uv run nl2repo harbor compile catalog/sources/micromatch --output <ignored-compile-a> --toolchain toolchain.node.lock.toml --artifact-root <parent-private-CAS> --allow-private
uv run nl2repo harbor compile catalog/sources/micromatch --output <ignored-compile-b> --toolchain toolchain.node.lock.toml --artifact-root <parent-private-CAS> --allow-private
diff -rq <ignored-compile-a>/micromatch <ignored-compile-b>/micromatch
```

Both compiles exited `0`; `diff -rq` reported no differences. Both generated bundles
contain 120 files, have raw bundle-manifest SHA-256
`sha256:36857936081ac0c2727a3fe7758fffc328c1a9a644d63660eb52c7958cee2db7`, and have
canonical manifest digest
`sha256:fee2a8788604806007269c95d0a5851d68b83378fa2bc1c1050630a159f995de`.
Every manifest entry matched the generated file's size and SHA-256.

## Artifact-path blocker

The newly compiled bundle contains npm cache index metadata with an absolute historical
authoring path:

```text
<historical-authoring-worktree>/ignored-cache/node-discovery-20260826-r1/micromatch/oracle-probe/micromatch-4.0.8.tgz
```

The same path is present in both deterministic outputs. This violates the projection
artifact hygiene requirement: generated runtime content must not embed authoring
worktree paths. The old checked-in projection was not replaced, and no Harbor Oracle,
empty, stub, forgery, timeout, or offline result is claimed from this compile. The
compiler output is retained only in the ignored revalidation directory for parent audit.

## Remediation

Normalize or rebuild the npm cache bundle so its cache index contains no authoring or
worktree absolute paths, register the resulting exact bytes in parent-owned private CAS,
then compile twice again with `toolchain.node.lock.toml` and `--allow-private`. After
the normalized projection passes leak and manifest checks, run the complete Harbor
`0.21.0` NoNetwork Oracle/control matrix and persist fresh durable receipts under this
directory before changing production evidence or replacing `catalog/tasks/micromatch`.
Do not alter the lifecycle, denominator, or historical production evidence solely due
to this artifact-path blocker.
