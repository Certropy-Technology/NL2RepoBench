# Revalidation Blocker: Frozen Oracle Payload Unavailable

## Task and source authority

- Task: `go-humanize`
- Source revision: `4d1d9082551ec085912e7d2253a33ae547fca000`
- Frozen source archive digest: `sha256:ce579ea6d7e8afd59ea2c9b3f8040984cc7ccb1fddc52e938a52ce64f265b9d4`
- Frozen source archive size: not declared in `task.toml`; the source digest is the authoritative archive identity.
- Current queued source digest: `sha256:135c3e9b4f5bc8bbb28ad89bc0c9533040e343c2ef4d575e20b43a8437583565`
- Declared Oracle bundle: `artifact://private/sha256:2f30447997dd0e3dece96ea66e38208a297aa67e89f6ec81361f55d433e38964`
- Declared Oracle bundle size: `600` bytes
- Declared dependency bundle: `artifact://private/sha256:ed5e8103205597cbf2294e04870b5278c31f1f23e51299f697f5652ae7058453` (`477` bytes)
- Declared verifier bundle: `artifact://private/sha256:e59d7e1bf2e35fabf43fc8aa155b9cef8ad923a4a2453c2c5759422d753265a9` (`1068` bytes)

The queued digest was validated before this file was created with:

```text
uv run nl2repo task validate-source catalog/sources/go-humanize
exit 0
source_digest: sha256:135c3e9b4f5bc8bbb28ad89bc0c9533040e343c2ef4d575e20b43a8437583565
```

## Bounded local recovery

All searches were read-only and used no source-host, registry, DNS, Go proxy, or external-service authorization.

```text
sha256sum <parent-CAS>/private/sha256/2f/2f30447997dd0e3dece96ea66e38208a297aa67e89f6ec81361f55d433e38964
exit 0
2f30447997dd0e3dece96ea66e38208a297aa67e89f6ec81361f55d433e38964  <parent-CAS>/private/sha256/2f/2f30447997dd0e3dece96ea66e38208a297aa67e89f6ec81361f55d433e38964
size: 600 bytes
```

The Oracle bundle contains only `./solve.sh`; it performs a runtime GitHub fetch and
does not contain `source.tar` or another installable source payload. Its declared
source revision and archive digest are present in the script, but runtime fetching is
forbidden by this task's NoNetwork policy.

```text
rg -n 'go-humanize|4d1d9082551ec085912e7d2253a33ae547fca000|ce579ea6d7e8afd59ea2c9b3f8040984cc7ccb1fddc52e938a52ce64f265b9d4' \
  task-local-evidence historical-handoffs authoring-archives retained-runs
exit 0/1 (no matching source payload; matches are metadata/instructions only)
```

```text
find task-local-evidence historical-handoffs authoring-archives retained-runs \
  -type f \( -path '*go-humanize*' -o -name '*source*.tar' \)
exit 0
result: no matching go-humanize source archive
```

The local Go module cache contains metadata for the frozen revision:

```text
<local-go-module-cache>/cache/download/github.com/dustin/go-humanize/@v/v0.0.0-20251125001511-4d1d9082551e.info
{"Version":"v0.0.0-20251125001511-4d1d9082551e","Time":"2025-11-25T00:15:11Z","Origin":{"VCS":"git","Hash":"4d1d9082551ec085912e7d2253a33ae547fca000","Ref":""}}
```

The corresponding module zip is absent. The only available module archive is the
different tagged `v1.0.1` zip:

```text
sha256sum <local-go-module-cache>/cache/download/github.com/dustin/go-humanize/@v/v1.0.1.zip
exit 0
319404ea84c8a4e2d3d83f30988b006e7dd04976de3e1a1a90484ad94679fa46  <local-go-module-cache>/cache/download/github.com/dustin/go-humanize/@v/v1.0.1.zip
size: 27015 bytes
```

Its module metadata identifies revision `9ec74ab2f7a7161664182fd4e5e292fccffbc75f`,
not the frozen revision. A deterministic tar reconstruction from that different tree
produced `sha256:5d3b216b42db5cc5d71eec0ac214233ad09796c2a6139e9a87094e961afd6f37`
(`92160` bytes), which does not equal `ce579...`; it is not an accepted replacement.

## Result

The dependency and verifier bundles exist and match their declared outer digests, but
the Oracle's frozen source bytes cannot be proven locally. No replacement private
bundle was constructed, no shared CAS was modified, and no compiler, Harbor run, or
network Oracle was started. Existing lifecycle and production evidence remain
unchanged.

Static checks after recording this blocker:

```text
uv run nl2repo task validate-source catalog/sources/go-humanize
exit 0
uv run python scripts/validate_instruction_quality.py
exit 0
bash -n catalog/sources/go-humanize/harbor/controls/*.sh
gofmt -d catalog/sources/go-humanize/harbor/tests/bridge.go
exit 0 (no diff)
uv run nl2repo task lint-network --include-generated
exit 1 (catalog-wide pre-existing error); go-humanize findings: 1 warning, 0 errors
```

The network warning is the expected Oracle source-host authorization advisory for the
runtime-fetching `solution/solve.sh`; this revalidation did not authorize that host.
The new evidence directory contains exactly this blocker file, has no absolute or
ignored run paths, and remains unstaged for parent review.

## Next step

Parent integration should recover or register a source archive whose bytes exactly
match revision `4d1d9082551ec085912e7d2253a33ae547fca000` and digest
`sha256:ce579ea6d7e8afd59ea2c9b3f8040984cc7ccb1fddc52e938a52ce64f265b9d4`.
After parent CAS registration, update the Oracle bundle to a local verified payload,
recompile twice, and rerun the complete Oracle/control matrix against the resulting
final manifest. Until then, retain lifecycle status `controls-passed` with prior
production evidence unchanged.
