# `h11` Provenance and Remediation

Source acquisition was performed in the task-local authoring work directory:

```text
.nl2repo/authoring-work/python-author-wave2-20260828/h11/upstream
```

Commands and observations:

- `git clone --no-checkout https://github.com/python-hyper/h11 ...`: exit 0.
- `git checkout --detach 62c5068c971579d61fa1b55373390e12f25fd856`: exit 0.
- `git rev-parse HEAD`: exact requested revision.
- `git archive --format=tar HEAD | sha256sum`: `503ed1fbb3efd07a9145b2f5ed05169728319e75d8117a4ef986e3aa91ea33f4`.
- `git show HEAD:LICENSE.txt | sha256sum`: `37db5bb85926db28a427a25867f10b1232003aea1be69ccb851138adb8e6f361`.
- `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONPATH=. python3 -m pytest --collect-only -q -o addopts='' -p no:cacheprovider`: 78 collected, exit 0.
- The same runner without disabling repository coverage addopts produced 78
  passed but exit 1 because the parent `nl2repobench` coverage plugin measured
  0% coverage; this is retained as harness evidence and is not used as the
  task's verifier.

Environment remediation uses CPython 3.12.14 / Debian 12 amd64 with the
digest-pinned `python:3.12.14-slim-bookworm` image. The package has no runtime
dependencies, so only setuptools and wheel are present in the candidate build
lock. No wheelhouse, vendor directory, or `--no-index` install is used.

## Harbor evidence

The refreshed source validation, network lint, and production compile were
run from the assigned worktree on 2026-08-28. The compile used Harbor 0.21.0,
`toolchain.lock.toml`, `.nl2repo/artifacts`, and `--allow-private`; it emitted
`.nl2repo/compile-handoff-final-h11/h11` with manifest SHA-256
`b666c65d67379b97bc955522f207a203d686ab3a57ae77222b17bbfb6eeb2273`.

Official Harbor runs used distinct job and output roots:

- Oracle: `.nl2repo/runs/h11-oracle-loop-20260828`, 24/24, reward 1.0,
  valid, exit 0, no exceptions.
- Empty (`nop`): `.nl2repo/runs/h11-empty-loop-20260828`, documented empty
  installation exception, reward 0.0, exit 0, no exceptions.
- Stub: `.nl2repo/runs/h11-stub-loop-20260828`, 0/24, reward 0.0, valid,
  exit 0, no exceptions.
- Forgery: `.nl2repo/runs/h11-forgery-loop-20260828`, 0/24, reward 0.0,
  verifier-owned, valid, exit 0, no exceptions.

All four verifier receipts include a network record with
`public_network_available=false`; the `1.1.1.1:443` and `pypi.org:443`
probes were false. The machine-readable receipt index is
`production-evidence.json`. The official runs were not Agent Runs and did not
modify the source archive or public task contract.

The official matrix used the locally available image for the locked tag. Its
observed image ID was
`sha256:55f9ac341e8782cbd31e57abe8e6ee2941dab68526894c2386a70f5f96c3fce7`,
not the toolchain-locked
`sha256:70525a5fbee81f4d202b7f7de14857fe78f961ce2ec3995efd1a4850e45c7ea5`.
An offline runtime probe confirmed fork commit
`930e9b1daee0f5d2c7f3b261f045527a0ddae87d`, OpenHands SDK/tools 1.43.1,
and LiteLLM 1.93.0, but version equivalence does not replace immutable image
identity. This is an integration release blocker and requires a matrix rerun
with the exact locked image.
