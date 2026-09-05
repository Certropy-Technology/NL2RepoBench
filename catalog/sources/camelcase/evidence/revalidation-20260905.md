# camelcase instruction-migration revalidation blocker

Date: 2026-09-05
Task: `camelcase`
Version: `2.0.0`
Expected current source digest: `sha256:86da4d58160cd7bcf4981f15b52d2bea95ce3d8c8dc88a072eb387e5c3f2cefb`
Network policy: `no-network`

## Completed checks

- `uv run nl2repo task validate-source catalog/sources/camelcase` passed and
  reported the expected current source digest.
- `uv run --frozen --project harbor-runner harbor --version` reported Harbor
  `0.21.0`.
- The full source tree, instruction, task metadata, historical production
  evidence, and all declared source-local control scripts were inspected.
- The four declared private artifacts were found in the parent CAS with the
  declared sizes: dependency bundle `396` bytes, commands bundle `270` bytes,
  test bundle `3224` bytes, and Oracle bundle `794` bytes.

## Deterministic production compiles

Both commands used the current source, locked Node toolchain, absolute parent
CAS, `--allow-private`, and no runtime network authorization:

```text
uv run nl2repo harbor compile catalog/sources/camelcase --output .nl2repo/camelcase-revalidation-compile-a --toolchain toolchain.node.lock.toml --artifact-root .nl2repo/artifacts --allow-private
uv run nl2repo harbor compile catalog/sources/camelcase --output .nl2repo/camelcase-revalidation-compile-b --toolchain toolchain.node.lock.toml --artifact-root .nl2repo/artifacts --allow-private
```

Both compiles exited `0` and `diff -rq` reported no differences. The generated
bundles each contain `75` files. Their `bundle.manifest.json` bytes have SHA-256
`sha256:b4f6aeb4dee20eef0b4664f27a910bef98f510b7ca3a14544e1b97e07f3f18fd`,
and the canonical manifest digest inside is
`sha256:4a58e759b925645c20073970c06f674416ce8fca696f0473b6d40bb1d5af0233`.

## NoNetwork blocker

The compiled Oracle payload is the hash-bound private artifact
`sha256:b11f5998257d95deefab6330c19b0a6b313e58f8cf8f8bb07f1d218e37ccf906`.
Its tar contains only `solve.sh`; the extracted script is `1446` bytes with
SHA-256
`sha256:dc67f8879ab61967972cdf65dc26eafc0304bbc5b1f628e317bfedf4c9c36d6c` and performs these forbidden
runtime operations before creating `/workspace`:

```text
readonly URL='https://github.com/sindresorhus/camelcase'
git init -q "$REFERENCE"
git -C "$REFERENCE" remote add origin "$URL"
git -C "$REFERENCE" fetch -q --depth 1 origin 3146708d5ffcd91a8cbc483e4a2585a39545da48
```

The task-local source `harbor/` solution cannot override this payload because
the compiler takes the declared private `oracle_bundle` as authoritative. No
Harbor Oracle or control run was started, and no GitHub, package registry, DNS,
source host, or external service was contacted.

## Remediation

Register a new private Oracle bundle containing a locally materializing,
hash-verified source payload for revision
`3146708d5ffcd91a8cbc483e4a2585a39545da48`, or provide a local source archive
matching the frozen source digest
`sha256:823ac92218bd6beac9fcac4acbaf1e0677fa06a6e6f046cee61638bbc831e9ab`.
Update the source's `[oracle_bundle]` reference only after the replacement is
available, then compile twice again and run Harbor `0.21.0` Oracle, empty,
stub, forgery, and offline controls against that new manifest. Do not grant
GitHub authorization, reuse stale receipts, or lower the frozen denominator.

No lifecycle transition or historical production-evidence replacement was
performed. This is an artifact/verifier revalidation blocker, not a permanent
task exclusion.
