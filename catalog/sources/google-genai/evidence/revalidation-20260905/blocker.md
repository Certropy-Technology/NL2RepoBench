# google-genai revalidation blocker

## Result

This revalidation is blocked as an artifact/verifier blocker. The instruction
migration source digest is unchanged, and no lifecycle or prior production
evidence file was modified. Harbor compile and all Harbor runs were intentionally
not started because the trusted Oracle payload cannot be executed under the
required NoNetwork policy.

- Task: `google-genai`, version `0.1.0`
- Queue source digest: `sha256:17796a5958502912556f78c1b4afd4145b855f1ed30b649d459c026c5f515445`
- Frozen upstream revision: `66518c9104b15a89225ee255fe03d906c7e4cb35`
- Required upstream Git archive: 44,800,000 bytes,
  `sha256:3e7ba8998c9bf652f892ee871a28277e3dfb5bfb6a9a7cf6a2e7c29483a08f12`
- Frozen verifier denominator: 40 leaves
- Network policy: `no-network`; no source-host authorization was used

## Declared CAS verification

All declared private artifacts are present in the parent CAS and match their
declared size and digest. They do not provide the frozen upstream source archive.

| Artifact | Size | SHA-256 |
| --- | ---: | --- |
| dependency lock | 48,729 | `sha256:d2ef79f7a68c430c7193acf86f4044d3bad95d269206da01353071843036a7bf` |
| verifier bundle | 20,480 | `sha256:35ab4da3f82d8cc23b51af96551f25b9613082dabcbfa8ab61d9cd80ada1722c` |
| Oracle bundle | 10,240 | `sha256:f112beb65f0e9365fd117b0e72f2c357d1539148fdf2d9a79100ba41408007c4` |

## Bounded offline recovery

Commands were run from the integration checkout or this isolated worktree;
all paths below are local. No network command was run.

1. `uv run nl2repo task validate-source catalog/sources/google-genai`
   - exit `0`; reported source digest `sha256:17796a5958502912556f78c1b4afd4145b855f1ed30b649d459c026c5f515445`
   and status `controls-passed`.
2. `sha256sum` and `stat` on the three parent-CAS paths listed above
   - exit `0` for each; all sizes and digests matched.
3. `tar -tf` on the Oracle bundle
   - exit `0`; members were only `./` and `./solve.sh`.
4. Extracting `solve.sh` and inspecting its source references
   - exit `0`; it fetches `https://github.com/googleapis/python-genai` at the
   frozen revision and verifies a generated archive digest. It does not contain
   `source.tar`.
5. `rg --files -g '*google-genai*/source.tar' -g '*google-genai*/source.tar.gz' -g '*google-genai*/oracle-source.tar' .nl2repo/authoring-live`
   - exit `1`; no matching source payload was found.
6. Bounded search for 44,800,000-byte `source.tar`/`source.tar.gz`/
   `oracle-source.tar` files under `.nl2repo`
   - exit `124` after the 45-second bound; no result was emitted.
7. `rg --files -g '*google*genai*' -g '*genai*' /root/.cache/uv /root/.cache/pip`
   - exit `0`; only uv package metadata, an editable wheel, and unrelated
   integration files were found. The editable wheel has no upstream Git archive
   and was not treated as an equivalent payload.
8. Retained authoring claims/logs for the original task
   - exit `0`; they record an incomplete authoring handoff and no retained
   source archive or task-local Oracle payload.

## Next step

The parent integrator should locate or register a trusted private payload whose
outer bytes are exactly the required source archive (44,800,000 bytes and the
digest above), or reconstruct that exact Git archive from an already retained
local checkout while verifying the frozen commit and archive digest. After
parent CAS registration, rerun source validation, compile twice, and execute the
complete NoNetwork Oracle/control matrix against a new final manifest. Do not
authorize GitHub or reuse the prior receipts to clear this blocker.
