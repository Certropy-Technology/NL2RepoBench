# `plac` Static Provenance Audit

Status: **blocked**. This directory is an audit record only. No Harbor task
descriptor, public instruction copy, verifier bundle, Oracle bundle, or hidden
test bytes are included.

## Legacy Contract

- Legacy task: `test_files/plac/`.
- Declared denominator: `28` (`test_case_count.txt`, SHA-256
  `59e19706d51d39f66711c2653cd7eb1291c94d9b55eb14bda74ce4dc636d015a`).
- Declared test paths: `doc/test_ishelve.py`,
  `doc/test_ishelve_more.py`, `doc/test_pi.py`, `doc/test_plac.py`,
  `doc/test_runp.py`, and `doc/test_server.py`.
- `test_commands.json`: `pip install -e .`; `pytest
  --continue-on-collection-errors doc` (file SHA-256
  `a62e68b6d425858056f6e93029ed8dc641b4e0261f0ae49311ee039b480ab851`).
- `test_files.json` SHA-256:
  `5486a9f2ee26f4c85243b055105b4672400cacb37deee5a57001cd0b959c5449`.
- Public legacy instruction SHA-256:
  `fe027755364e116ccc63d2308084acd0fad5c1a9458fe09abdd7d4c687f96528`.

The task history shows the denominator changed from `25` to `28` in commit
`781a1da1ee41fb8edb0bed22f586d69111610edf`; the six declared paths did not
change. Static AST inventory of the six image test files finds 28 test
functions/items before parametrization, matching the legacy denominator.

| Image path | Tests | Image SHA-256 |
| --- | ---: | --- |
| `doc/test_ishelve.py` | 1 | `6efdad8657d26896c674cf5f93bcaaad148865cb71404ee36667fb9ebe4ab50e` |
| `doc/test_ishelve_more.py` | 1 | `eccf6d79bc2ac2e60e295ccaabdd68cabc971b4f3baae3ebfdb61834198c042c` |
| `doc/test_pi.py` | 1 | `d6baf1caff4afbacfd548cd85cdcbd78db06882fc041c44e2d5909e893accb86` |
| `doc/test_plac.py` | 22 | `3908880aec6a85bba616651c79b6b0c4fe2ccb57bc4f3af5d54fcb6fcfbd4e46` |
| `doc/test_runp.py` | 2 | `faff75b4b9348c3e04516764ead04f394a03ce52b6dfec669e3529564a4b599d` |
| `doc/test_server.py` | 1 | `961b8accf51f461390ea47950c5426a624b9d47b2634f7f2f96602ff3ee8b5c1` |

## Source Provenance

- Upstream: `https://github.com/micheles/plac`.
- Image `/plac/.git/HEAD` resolves to full commit
  `0da08718131023893894e484d1a8133647e55e1d` (`v1.4.5`, "changes for PyPI
  documentation").
- Unprefixed source archive command: `git -C /tmp/plac-upstream archive
  --format=tar 0da08718131023893894e484d1a8133647e55e1d`.
- Git archive SHA-256: `9b58509fedcb5d1a07e3bebd5756e699764bfaa60d514d5aa3e6978bdd10fdb7`;
  size `286720` bytes.
- License: BSD-2-Clause, evidenced by upstream `LICENSE.txt` and GitHub's
  license endpoint. License size `1324` bytes; SHA-256
  `31534c0e71f22db819ab9ebf7d58b410cd7695b3e09b3329d2e1edcfc303a959`.
- Upstream metadata identifies version `1.4.5`, `py_modules` for `plac`,
  `plac_core`, `plac_ext`, and `plac_tk`, and no non-stdlib runtime
  requirement beyond its conditional `argparse` check.

## Per-Path Comparison

The image fixture layer is
`sha256:d8a0292666a08ea4f43b68e593ddbf50e6f733964ebbbfd3ba33a98714bdf958`.
Its Python test files use CRLF; comparisons below tested both exact bytes and
upstream bytes converted to CRLF.

| Path | Upstream blob at `0da0871` | Result |
| --- | --- | --- |
| `doc/test_ishelve.py` | `9bdaacc05cd8010cb13e288b643b6948bf267d3c` | match after CRLF normalization |
| `doc/test_ishelve_more.py` | `8a1c9490a256a57d1988085cf590387a4295b290` | match after CRLF normalization |
| `doc/test_pi.py` | `4b34c2fb85cd5ee70b51ae7087f701d07d78c6c6` | match after CRLF normalization |
| `doc/test_plac.py` | `277349b7ea528dcfccad4334482170e845d59fab` | match after CRLF normalization |
| `doc/test_runp.py` | `b0c1953fa15e71ff4c040fc8cff0b69c935889bb` | **mismatch**: image adds `sys`, `pytest`, and Windows `skipif` decorators; normalized blob `9925af6b9e0babdddbd33231351a23617c2deb08` is absent from all upstream history |
| `doc/test_server.py` | `e04926b5709ba2d41dc5ff6562f41259346d9571` | **mismatch**: image adds `sys`, `pytest`, and a Windows `skipif` decorator; normalized blob `0daaaede3937af6740fb9d6847e09cdbdabb35df` is absent from all upstream history |

The two skip overlays have no source revision, commit, or owner-approved
overlay manifest. Assigning them to the upstream commit would fabricate test
provenance. The denominator is numerically coherent, but the complete frozen
test-path provenance is not.

## Image Evidence

- Requested immutable verifier image:
  `ghcr.io/multimodal-art-projection/nl2repobench/plac@sha256:300c6477c35e43d05021f07652dbad70adc3641472eafd02434df1e5df0449e1`.
- Registry manifest resolved to exactly that digest; platform `linux/amd64`.
- Config digest: `sha256:6070fa07479b9a83f4c226464abefc9fd45b6b0e7bf5b4a9418af339a552469f`.
- Config reports Python `3.10.11`, pip `23.0.1`, setuptools `65.5.1`, and
  working directory `/workspace`.
- The `1.0` tag was observed to resolve to the requested digest but is not
  used as provenance.
- Source checkout layer: `sha256:4a1ec18a59c2382c5b5cc4ca4cd15bd0315f33234cc48969c8e22266a3b47996`.
- Image history records install from `/plac`, `pytest`, and cleanup of
  `/plac`; this is not treated as an Oracle or runtime result.

## Decision

Keep `plac` **blocked**. Do not create `catalog/tasks/plac/task.toml`,
`instruction.md`, Harbor Dockerfiles, private test references, or an Oracle
solution from this evidence. Do not run Docker, Harbor, Oracle, or legacy
pytest while the GPT/Fable queues are active.

To reopen, obtain an owner-approved immutable artifact for the two skip
overlays, or replace them with the exact upstream test blobs at a declared full
revision. Then collect in the final verifier image, freeze the denominator from
collection, provision private test/command/dependency/Oracle artifacts, and run
the required Oracle and control gates in a separate campaign.

## Static Validation

Evidence commands were run without starting Docker or Harbor: `git clone
--no-tags https://github.com/micheles/plac.git /tmp/plac-upstream`; `git
rev-parse`, `git archive`, `git show` for the source/license; GitHub API license
metadata; registry token/manifest/config/layer inspection via `curl`; Python
AST inventory of the six extracted paths; SHA-256 comparison of every legacy,
image, and upstream test file; and `git rev-list --objects --all` to check for
the two normalized overlay blobs.

No tests were added or executed for this blocked audit. Shared scripts,
dataset manifests, and legacy task files were not edited.
