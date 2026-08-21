# `tsfresh` Static Provenance Audit

**Status: blocked.** This directory is an audit record only. It contains no
Harbor task descriptor, public instruction projection, Oracle solution,
verifier script, dependency bundle, or hidden test bytes. Legacy files, shared
dataset files, and conversion-loop state were not modified.

## Legacy Contract

The four legacy inputs under `test_files/tsfresh/` were read without editing:

| File | Bytes | SHA-256 | Parsed value |
| --- | ---: | --- | --- |
| `start.md` | 145,900 | `dc1689a734028b177cda85556ed8d95413206d3985c8476f783f341e3aa70c2e` | Public repository-generation instruction |
| `test_case_count.txt` | 3 | `8d1ede4f889e0ed6f0823d8c1821905b9de37a0f851dc270df0dbf72b3c93641` | Declared denominator `317` |
| `test_commands.json` | 67 | `3bd822b96ae432d75e8a3d09a40c856f17f3164f200f1eb0fee6b684be49ace9` | `pip install -e .`; `pytest --continue-on-collection-errors tests` |
| `test_files.json` | 9 | `af7f0b2bd342822f2fa8e6a9fda610570f911f30d3108379ea4184c0866727c3` | Protected path `tests` |

The count changed from `371` to `317` in repository commit
`781a1da1ee41fb8edb0bed22f586d69111610edf`; the command and protected path
did not change with that edit. No frozen collection, node-id manifest, JUnit
file, or structured skip record is retained.

## Immutable Verifier Image

The conversion-loop record and a read-only registry manifest request resolve:

```text
ghcr.io/multimodal-art-projection/nl2repobench/tsfresh@sha256:8f94130037f814033e7632fc4e3271b171e3c69b1d7fd795e7b3010ec477b950
```

The manifest is `linux/amd64`; its raw JSON SHA-256 is the same
`8f94130037f814033e7632fc4e3271b171e3c69b1d7fd795e7b3010ec477b950`. Config
digest: `sha256:adfd607709908f55d45697b91215dd13b8386d09520b4fe34d11af94bb0dffbb`.
The config reports CPython `3.10.18`, image creation
`2025-09-16T06:51:04.742199895Z`, and `PYTHON_VERSION=3.10.18`.

| Image content | Layer digest | Compressed bytes |
| --- | --- | ---: |
| protected `/workspace` test tree | `sha256:d5ffef440ab359f5951cf5cacac3fbace02705dab701a3ae7c08caf8450c29c8` | 42,368 |
| `setup.py` copied to `/workspace` | `sha256:d557701d5fc7a2b8beab61b7fa5fd92c212358aa219c2b56bbfae4257d8d07a0` | 483 |
| `setup.cfg` copied to `/workspace` | `sha256:a9c8b617034241126971515b1ee15d1cf6651735eff364374ecc1fe66643da47` | 2,193 |
| source checkout at `/tsfresh` | `sha256:0cb0d59280b636ec40aa8cd21c3a06ef60992bbff3445448a6d41e5a686def01` | 12,076,712 |

Image history setup commands are unpinned:

```text
pip install pytest pytest-xdist
pip install --upgrade pip
pip install dask distributed nbformat mock pytest pyarrow pandas pytest-cov
cd /tsfresh && python -m pytest
```

The historical pytest layer retains no collection/JUnit result and is not an
Oracle or frozen-denominator record.

## Source, License, And Overlays

The image checkout records:

- Upstream: `https://github.com/blue-yonder/tsfresh.git`.
- Full revision: `6e3786bea915b72a4eabfa7b7ed163b62b87da18`.
- Tree: `727c0801590a57daaa9475f9ddf1ac2c0edbbdee`.
- Archive command: `git archive --format=tar 6e3786bea915b72a4eabfa7b7ed163b62b87da18`.
- Unprefixed archive: 10,475,520 bytes, SHA-256
  `87aedea5cbe8e3414b54f3203700efc36244482822cacdeb7f821410bc88eb50`.
- License: MIT from `LICENSE.txt`; 1,092 bytes, SHA-256
  `1804283622c8e51a4427aaa772d5ca522f89932fd610b294055435922af1c748`, Git
  blob `8bfb04f23477f39c877dfa93054f1c50ec0198b3`.

All tracked source files are exact at that revision except the benchmark build
`Dockerfile` overlay:

- image bytes SHA-256 `e4e34ef588d47b1190adc748685b3f2a1fd3ae6ec66cdec2ecb3e81186f4259d`;
- upstream blob `594dc321bbf447d1b9e5a66342a2b2fea7ec6f5f`;
- image blob `dc71315db55c2c8ed4b602bd9f5212f66410658a`;
- normalized diff SHA-256 `8ef2f585ceb468b38a16db8677b09c9ed38a388062bd594d844f317d01893335`.

The 39 retained test/support files are byte-identical to the locked source
tree: 299,243 bytes, canonical path/size/SHA-256 inventory digest
`20c476ad7aca0d7671383d7ce9e8d77a2a3e9e8e725078eba05a0e65a717ad3e`.
The setup blobs also match exactly:

```text
setup.py  feed972942cae0f4011121d5e1a5fc453caf62b5
setup.cfg e0053a148bbf87294db418b670503dd3a9ea54c4
```

No hidden test bytes are copied into this audit.

## Denominator Audit

Static AST inventory of the 26 pytest-pattern files found 320 unique class
test methods and two module-level test functions. Duplicate method names in a
Python class were counted once because later definitions overwrite earlier
ones. The single `pytest.mark.parametrize` in
`units/feature_selection/test_fdr_control.py` has 10 cases:

```text
unique base test definitions:  322
parametrization expansion:      +9
static candidate nodes:        331
legacy declared denominator:   317
```

The visible environment-sensitive skips account for 11 unique notebook
methods in `integrations/test_notebooks.py` (`TEST_NOTEBOOKS != "y"`) and
three matrix-profile methods when the optional `matrixprofile` dependency is
unavailable. Thus `331 - 11 - 3 = 317` is numerically consistent with the
legacy count for the inspected image environment. This is static evidence
only: no final-image collection or node-id record is retained, so collection
stability and the exact effective denominator remain unproven for publication.

## Publication Blockers

### 1. Dependency closure is not reviewably frozen

`setup.cfg` declares lower bounds rather than a resolved runtime closure
(`requests`, `numpy`, `pandas`, `scipy`, `statsmodels`, `patsy`, `pywavelets`,
`scikit-learn`, `tqdm`, `stumpy`, and `cloudpickle`). The image history adds
unversioned pytest/test/data packages and upgrades pip without hashes. No
hash-locked requirements file, wheelhouse, dependency artifact, or complete
offline installation manifest is retained. The immutable image preserves one
historical filesystem, but not a reviewable dependency closure for a
production separate verifier.

### 2. The declared suite requires live network access

The legacy command runs all `tests`. Before assertions, these tests download
remote data:

- `tests/integrations/examples/test_har_dataset.py` requests
  `https://github.com/MaxBenChrist/human-activity-dataset/blob/master/UCI%20HAR%20Dataset.zip?raw=True`.
- `tests/integrations/examples/test_robot_execution_failures.py` and
  `tests/integrations/test_full_pipeline.py` request
  `https://raw.githubusercontent.com/MaxBenChrist/robot-failure-dataset/master/lp1.data.txt`.

A no-network verifier cannot execute the frozen suite. A public-network
verifier makes its score depend on mutable remote services and data.

### 3. No separate candidate boundary exists

The frozen tests directly import and execute candidate `tsfresh` modules,
including `tsfresh.examples.*`, `tsfresh`, `tsfresh.transformers.*`,
`tsfresh.feature_*`, and `tsfresh.utilities.*`. The only declared setup is
editable installation plus direct pytest execution. No tsfresh candidate-
client/RPC adapter or trusted subprocess contract exists. A legacy-style
verifier would import candidate code in the trusted pytest process, contrary
to the separate-verifier requirement, and candidate packaging/import hooks
could reach collection or reporting.

## Decision And Reopen Conditions

Keep `tsfresh` **blocked**. Do not create `task.toml`, `instruction.md`, a
Harbor 1.4 tree, private fixture references, or an Oracle solution from this
evidence.

To reopen:

1. Collect the final verifier image and preserve a stable node-id/skip record
   reconciling the `317` legacy count; do not silently change the denominator.
2. Provide a hash-locked offline Python dependency artifact, or an explicitly
   reviewed immutable image-backed closure with reproducible provenance.
3. Replace remote dataset downloads with approved immutable local fixtures, or
   version the task around an explicitly networked metric contract.
4. Provide a reviewed candidate-client/subprocess adapter for direct API,
   fixture, and CLI interactions, then run Oracle and negative controls later.

## Static Validation

Completed without starting Docker, Harbor, Oracle, or pytest:

- Read `AGENTS.md`, `CONTRIBUTING.md`, the four legacy files, conversion-loop,
  metadata/verifier guidance, and neighboring blocked-audit conventions.
- Parsed and SHA-256 hashed every legacy artifact and both JSON files.
- Read external conversion-loop image metadata and revalidated immutable
  manifest, config, relevant layers, and history with read-only requests and
  temporary extraction.
- Resolved full source SHA, tree, MIT license, deterministic archive hash,
  and all test/setup/source differences.
- Compared all 39 retained test/support paths and both setup files with the
  locked upstream revision; only image-build `Dockerfile` is an overlay.
- Inventory-counted pytest-pattern files and parametrization with Python AST;
  found 331 static candidate nodes, with 14 visible environment skips
  reconciling the legacy effective count to 317.
- Searched the frozen test/source tree for network downloads, direct candidate
  imports, pytest skips, and subprocess notebook execution.

No tests were added or executed. No Docker/Harbor/Oracle process was run. No
files are staged.
