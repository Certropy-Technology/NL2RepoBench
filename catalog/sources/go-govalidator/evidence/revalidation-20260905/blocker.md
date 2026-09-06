# Revalidation Blocker

- Task: `go-govalidator` version `0.1.0`
- Source revision: `3dd3875e2b081a20d6eed935913a482fea14ecd0`
- Frozen source digest: `sha256:a96caf17ed4882595950607d2567b4da764725c0de74b9ba60459a5f54f8090d`
- Queue source digest after instruction migration: `sha256:ee522ba38bd567f2ae337f6e2352b1b7835d2e78485fd0c20309e7de9d799de8`
- Network policy: `no-network`; GitHub, codeload, registries, DNS, and Go proxy remain forbidden.

## Declared Artifact Checks

All declared private artifacts were present and matched their exact size and
SHA-256 values before compilation:

| Artifact | Size | SHA-256 |
| --- | ---: | --- |
| Oracle bundle | 682 bytes | `sha256:1e739fa656ee2a65c04122fd92abdb14b02a1131ef0521baefc6b2cc03b6121a` |
| Go module bundle | 534 bytes | `sha256:6ec73ae163a52b09e0e18a056e10c991074a45d0ed10d77f462dc5a46041efe6` |
| Verifier bundle | 1993 bytes | `sha256:469cc530fa4be6f6f4466776f6e999f69ba2668e002efbafe434e442265ecc7c` |

The Oracle bundle contains only `solve.sh`; it does not contain `source.tar`
or another installable source payload. Its script clones
`https://github.com/asaskevich/govalidator.git` at runtime and therefore cannot
be executed under this task's NoNetwork contract.

## Compile Checks

Using `toolchain.go.lock.toml`, Harbor 0.21.0, and the repository private
artifact root `.nl2repo/artifacts`:

```text
uv run nl2repo harbor compile catalog/sources/go-govalidator --output .nl2repo/revalidation-20260905/go-govalidator/compile-a --toolchain toolchain.go.lock.toml --artifact-root .nl2repo/artifacts --allow-private
exit_code=0
uv run nl2repo harbor compile catalog/sources/go-govalidator --output .nl2repo/revalidation-20260905/go-govalidator/compile-b --toolchain toolchain.go.lock.toml --artifact-root .nl2repo/artifacts --allow-private
exit_code=0
bundle_manifest_sha256=sha256:2ad1659709e4a2366a7b31399defb8471c47ed3d6f6136b9e4e3170d267b222b (both outputs)
byte_identity=passed
```

The outputs were ignored temporary directories and are not evidence paths or
committed runtime projections.

## Bounded Local Recovery

The following offline checks were run before declaring the blocker:

```text
tar -xzf <Oracle CAS object> and inspect archive members
exit_code=0; members=./,./solve.sh; source.tar=absent
search retained historical handoff/archive directories for go-govalidator/source.tar
exit_code=0; no matching source payload found
search current .nl2repo artifacts, catalog evidence, retained runs, and Go module/build caches for revision/digest
exit_code=0 or bounded timeout on large cache traversal; no exact source archive was found
```

A module cache, a cache zip, a different archive format, or generated build
output would not be equivalent to the declared Git archive digest and was not
accepted as a replacement. The historical `production-evidence.json` remains
unchanged because its receipts reference an earlier compiled manifest and are
invalidated by the instruction migration.

## Blocker and Next Step

Status is an artifact/verifier blocker for this revalidation attempt, not an
unsupported-source determination. Do not authorize a source host or run the
Oracle/control matrix. The parent integrator should recover `source.tar` from a
trusted local archive/CAS backup, then verify the exact revision
`3dd3875e2b081a20d6eed935913a482fea14ecd0`, the Git archive digest above, and
the archive inventory before registering a replacement private bundle. After
that, recompile twice and rerun the complete NoNetwork-capable Harbor Oracle and
control matrix against the new final manifest.
