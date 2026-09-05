# ESLint instruction-migration revalidation blocker

- Task: `eslint`
- Revalidation date: `2026-09-05`
- Expected catalog source digest: `sha256:a2b9c116a2b99aa15cc95d02de84ebee9798fff34eb9247caa2101162835496b`
- Frozen upstream revision: `c27bc926e496985eb7911c09eb60914b2e4b5d0f`
- Lifecycle: unchanged at `controls-passed`; this evidence does not transition the task.
- Historical `production-evidence.json`: unchanged because its receipts are from an older authorized run and are not valid no-network revalidation receipts.

## Completed checks

`uv run nl2repo task validate-source catalog/sources/eslint` passed with the expected catalog digest. The instruction quality validator passed. The four private CAS artifacts declared by `task.toml` were present with matching sizes and SHA-256 values: dependency bundle `sha256:1da1b847f34dc599a15227303a513ce9f8f1141879b03784d5862b1d12760573`, commands `sha256:5dfd03f3f2b3b9277e32bdbb3b3f39f0d228aca278d0686ae823352640634c1e`, tests `sha256:924a6b6366e3a63f56c4d3e2fa5e3cc209bcd2098492072221974e87765bd073`, and Oracle `sha256:8737925e27ba190fa20dc3cfa4ec19bc014e638ee65a7197cdeac03c0bfdfc87`.

## Deterministic production compiles

Both no-network commands used the current source, `toolchain.node.lock.toml`, the private CAS, `--allow-private`, and no host authorization:

```text
uv run nl2repo harbor compile catalog/sources/eslint --output .nl2repo/eslint-revalidation-compile-a --toolchain toolchain.node.lock.toml --artifact-root .nl2repo/artifacts --allow-private
uv run nl2repo harbor compile catalog/sources/eslint --output .nl2repo/eslint-revalidation-compile-b --toolchain toolchain.node.lock.toml --artifact-root .nl2repo/artifacts --allow-private
diff -rq .nl2repo/eslint-revalidation-compile-a/eslint .nl2repo/eslint-revalidation-compile-b/eslint
```

Both compiles exited `0`; the byte comparison passed. The generated bundle has 621 manifest entries and 622 files including its manifest. The raw manifest SHA-256 is `sha256:8b4841089e9707fa535f310b4f8107d3a1cadc678a33a1a443354418a44e4067` and its canonical manifest digest is `sha256:8ba4e9d7c0444926d275c5150474b61f96fc6de9bd3c480e6b8874568c649986`. See `compile-a-summary.json` and `compile-b-summary.json`.

## NoNetwork blocker

The hash-bound Oracle bundle contains `solve.sh` and `oracle-package-lock.json`. Its `solve.sh` invokes `node:https.get` against `https://codeload.github.com/eslint/eslint/tar.gz/<pinned revision>` at runtime, then verifies the downloaded archive and runs `npm pack`. This violates the revalidation contract requiring Agent, candidate, verifier, Oracle, and controls to run without network access. The historical run explicitly used `--allow-agent-host codeload.github.com`; no such authorization was granted in this revalidation.

Oracle and all controls were therefore not run. No Oracle, grading, network, collection, result, or failure-set receipt is claimed for this revalidation. The existing historical production evidence remains untouched. See `oracle-bundle-inspection.json` for member hashes and the exact runtime-fetch classification.

## Remediation

Register a replacement private Oracle bundle containing a local revision- and archive-digest-verified payload, or replace the Oracle script with an immutable source-local payload. Recompile twice against that replacement and run the complete Harbor `0.21.0` Oracle, empty, stub, forgery, and offline matrix. Persist every receipt under this evidence directory before updating production evidence. Do not authorize `codeload.github.com`, reuse historical receipts, lower the denominator, or change lifecycle solely because this infrastructure/verifier blocker exists.

## Command evidence

The executed command summary is tracked at `command-log.txt` with SHA-256 `sha256:a151940e6ae9204ce0da2eb6b1e3adc055e3d50d171f86aa8373fb304c1d9fad`.
