# Instruction-revalidation infrastructure blocker

## Scope and immutable input

- Task: `jaraco-functools`
- Queue-bound source digest: `sha256:8b9871abd118ccf54e49e2eb3ce3f24c1496ea1b442c30116b66ca3050304336`
- Frozen upstream revision: `f7f4f3bcac8f70e01064dee9a8bde6cc8f997a17`
- Frozen source archive: `sha256:7ef01289b53574ed426a959b34621ae611bf415d17b03bb9b807f5c81e1e53ff`
- Lifecycle and prior production evidence were preserved. This record blocks only the fresh instruction-migration receipt set.

## Offline artifact and Oracle inspection

All three declared private artifacts were present in the parent CAS and matched their declared sizes and SHA-256 digests. The Oracle bundle contains `source.tar`; its inner digest matches the frozen source archive and the local `solve.sh` verifies that digest before extraction. Neither `solve.sh` nor the verifier performs a runtime source-host or registry fetch. No replacement artifact or local recovery search was required.

The verifier bundle passed Python syntax checks. Its trusted `run.py` invokes the candidate adapter through `runuser` as the candidate user, and the adapter imports the candidate only inside that child process.

## Deterministic compile

Two strict compiles used `toolchain.lock.toml`, the parent private CAS, and `--allow-private`; neither used `--allow-incomplete`. Both exited zero and were byte-identical. The current bundle manifest file SHA-256 is `sha256:0ddf957cb29d983363c328471b44d68ae38489528a426d532036f95119e61f4e`, and its canonical manifest digest is `sha256:289ea7060e870fcc52ccbaa7b7f1fd79080c82a7f87e1df5db62b15133627fef` with 59 files.

## Harbor attempts

1. The initial Harbor 0.21.0 Oracle command exited 1 before a trial because the Docker daemon was unavailable.
2. The one permitted bounded retry used a fresh job and run root. Docker was available, but Harbor raised `EnvironmentStartTimeoutError` after 600 seconds while building the Docker compose environment. The job recorded zero Oracle trials and one environment error. No Oracle solution or verifier execution occurred.

Compact attempt details and SHA-bound tracked attempt logs are recorded in `oracle-attempts.json`. The original Harbor run roots remain ignored and are not used as production evidence. No host authorization was supplied in either attempt.

## Classification and next step

- Failure class: `infrastructure`
- Current-manifest Oracle metrics: unavailable; no trial ran
- Controls: not run, because the current manifest has no successful Oracle receipt and the bounded infrastructure retry was exhausted
- Next step: after Docker build pressure subsides, the parent should run one fresh Oracle trial for canonical manifest `sha256:289ea7060e870fcc52ccbaa7b7f1fd79080c82a7f87e1df5db62b15133627fef`, followed by empty, stub, forgery, call-hang, and offline/no-egress controls. Only then may `production-evidence.json` be replaced with durable, repository-relative, SHA-bound summaries.
