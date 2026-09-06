# google-auth Revalidation Blocker

Status: `blocked for revalidation` (artifact/verifier blocker). The existing
source lifecycle and production evidence remain unchanged at `controls-passed`;
this record only documents why the post-instruction-migration receipts cannot
be refreshed under the mandatory NoNetwork policy.

## Frozen Source

- Task: `google-auth` version `0.2.0`
- Revision: `b4d97179f151d5ff37e6c7dbbd190a84c7d936a9`
- Declared source archive digest: `sha256:c78d2dfa82d178bfff82dc803ca9c6aa1d836947849082ea6caafd2a63574e89`
- Declared source archive size: `2,949,120` bytes
- Current instruction-migration source digest: `sha256:714a91464cd57fbe259788b7d0d316da3b93ec9c2d9bef746e043b565c8e703d`

## Artifact Checks

The declared private artifacts were available and verified before this blocker
was recorded:

| artifact | digest | size |
| --- | --- | ---: |
| dependency lock | `sha256:dbb0487545ec7c74e5deaa0f4a3f4e7ef31a62d8820128dfb499c1751ba1b1c6` | 712 |
| verifier bundle | `sha256:b809ff4081afa8ad1c7161ad7e7e4953a7d43cf1c35b9e382265e438f802eb2d` | 30,720 |
| Oracle bundle | `sha256:24795a7aedebd541803cf4243a7d52af575c325d7d8f2eeb79b92f0a04a13dd0` | 10,240 |

The Oracle bundle unpacked to exactly one file, `solve.sh` (979 bytes). Its
script initializes a repository and fetches revision
`b4d97179f151d5ff37e6c7dbbd190a84c7d936a9` from GitHub at runtime. It does not
contain `source.tar` or another installable source payload.

## Bounded Recovery Commands

All searches were local and did not authorize or contact an external host.
Exit codes and outcomes:

```text
uv run nl2repo task validate-source catalog/sources/google-auth
exit 0; source_digest=sha256:714a91464cd57fbe259788b7d0d316da3b93ec9c2d9bef746e043b565c8e703d

sha256sum --check --strict <declared-CAS-artifacts>
exit 0; dependency lock, verifier bundle, and Oracle bundle matched declared sizes and digests

tar -tf <oracle-bundle>
exit 0; one member: solve.sh

find <private-CAS> -type f -size 2949120c -print
exit 0; no files found

find <authoring-work> <authoring-live> <retained-runs> -type f \\
  \( -name source.tar -o -name source.tar.gz -o -name oracle.bundle.tar \\
  -o -name oracle-bundle.tar \) ... sha256sum ...
exit 124; bounded scan timed out without a digest match

find <task-local-and-historical-google-auth-copies> -type f \\
  \( -name source.tar -o -name source.tar.gz -o -name oracle-source.tar \) ...
exit 124; bounded task-local scan timed out without a digest match

uv run nl2repo harbor compile catalog/sources/google-auth \\
  --output <isolated-compile-a> --toolchain toolchain.lock.toml \\
  --artifact-root <parent-CAS> --allow-private
exit 0

uv run nl2repo harbor compile catalog/sources/google-auth \\
  --output <isolated-compile-b> --toolchain toolchain.lock.toml \\
  --artifact-root <parent-CAS> --allow-private
exit 0; compile-a and compile-b were byte-identical
```

## Blocking Rule

Running Harbor Oracle would require allowing the Oracle's GitHub fetch, which is
forbidden for this revalidation. No Oracle or control was run from this changed
bundle, and no old receipt was reused. The missing exact source bytes are an
artifact/verifier blocker, not a model or infrastructure result.

## Next Step

Parent integration should provide and register a private bundle containing the
exact package subtree archive for revision
`b4d97179f151d5ff37e6c7dbbd190a84c7d936a9` with digest
`sha256:c78d2dfa82d178bfff82dc803ca9c6aa1d836947849082ea6caafd2a63574e89`
and size `2,949,120` bytes. Then update the Oracle payload binding, compile the
source twice, and rerun the complete NoNetwork Oracle/control matrix against the
new final manifest. Until then, the post-migration revalidation status is
`blocked` and the prior production evidence must not be replaced.
