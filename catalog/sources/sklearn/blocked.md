# `sklearn` Static Provenance Audit

Status: **blocked**. This directory is an audit record only. It contains no
`task.toml`, public Harbor instruction copy, Harbor bundle, Oracle solution,
verifier code, hidden test bytes, or copied source. No dataset file, shared
index, conversion-loop state, legacy artifact, or other task directory was
edited.

## Legacy Contract

- Legacy task: `test_files/sklearn/`.
- Public instruction: `start.md`, 52,980 bytes, SHA-256
  `19828b897af3dfed2717ddaf5dfa08124709aea8ec30e596faef18348f56aa80`.
- Declared denominator: `70`, from `test_case_count.txt` (2 bytes, SHA-256
  `ff5a1ae012afa5d4c889c50ad427aaf545d31a4fac04ffc1c4d03d403ba4250a`).
- Commands, in order: `pip install -e .`, then
  `pytest --continue-on-collection-errors tests`.
  `test_commands.json` is 67 bytes, SHA-256
  `3bd822b96ae432d75e8a3d09a40c856f17f3164f200f1eb0fee6b684be49ace9`.
- Protected path: `tests` (`test_files.json` is 9 bytes, SHA-256
  `af7f0b2bd342822f2fa8e6a9fda610570f911f30d3108379ea4184c0866727c3`).

The legacy command and JSON files are syntactically valid. Static AST
inspection of the immutable image fixture finds 60 test functions in
`test_dataframe_mapper.py`, four in `test_features_generator.py`, four in
`test_pipeline.py`, and two in `test_transformers.py`, for 70 ordinary test
functions. No parametrization, collection hook, skip, or xfail marker was
found. This numerical agreement does not establish a frozen pytest
collection; no collection or pytest run was performed. The count therefore
cannot be promoted to the required `expected_total_source =
"frozen-collection"`.

## Immutable Verifier Image

The conversion-loop state outside this worktree records an available
`linux/amd64` image:

```text
ghcr.io/multimodal-art-projection/nl2repobench/sklearn@sha256:9fd839ad0484eec3b795f10acc725c22d8da85b4827c3aa436b23dfd52c7662a
```

Registry manifest and config evidence:

- Manifest digest: `sha256:9fd839ad0484eec3b795f10acc725c22d8da85b4827c3aa436b23dfd52c7662a`.
- Config digest: `sha256:f8054de7613ec628925b85bb48cd96fddad24234cee09f13041bef7991fd4d58`.
- Architecture/OS: `amd64/linux`.
- Working directory: `/workspace`.
- Command: `tail -f /dev/null`.
- Image Python: `3.9.24` (`PYTHON_VERSION` in the image config).
- Relevant fixture layers: tests
  `sha256:75a1144dde85182f9d237bbfb3b9d3bb1e95a2645ae6da7e7e588fd7ff3e1ffd`
  (79,521 compressed bytes), `setup.py`
  `sha256:a886960189adcbda6c32c98ed7b435fb790ea102bf502aad6758692bf757183f`
  (762 bytes), and `setup.cfg`
  `sha256:2861d5c28eb3bdd15b55ecfbf5f984f6cfb9451be090f99d773d6357352a1fae`
  (169 bytes).

The image history copies only `tests`, `setup.py`, and `setup.cfg` into
`/workspace`; it does not contain an upstream implementation tree. Its build
history installs the following runtime/test set:

```text
numpy==1.26.0
pandas==2.3.1
scikit-learn==0.24.2
scipy==1.11.4
pytest==8.4.1
```

Observed transitive distributions include `joblib==1.5.2`,
`threadpoolctl==3.6.0`, `python-dateutil==2.9.0.post0`, `pytz==2025.2`,
`tzdata==2025.2`, `six==1.17.0`, `packaging==25.0`, `pluggy==1.6.0`,
`iniconfig==2.1.0`, `Pygments==2.19.2`, `exceptiongroup==1.3.0`,
`tomli==2.3.0`, and `typing_extensions==4.15.0`.

## Upstream Source And License

The image paths match the following upstream repository and commit
after line-ending normalization:

- Repository: `https://github.com/scikit-learn-contrib/sklearn-pandas`.
- Full commit: `c9db2d6dcbf515eade751073f43318e43cae5177`.
- Commit tree: `670cef0716befa011fb54a0143f1543a7aa764c0`.
- Parent: `fa3b7266886e684e3696deda46b529da84dc9d48`.
- Subject: `Add new complex dataframe transform test for 2d cell data (#254)`.
- Commit time: `2022-07-17T13:23:59-07:00`.
- Reproducible archive command:
  `git archive --format=tar c9db2d6dcbf515eade751073f43318e43cae5177`.
- Unprefixed archive: 204,800 bytes, SHA-256
  `edba02f6df85331bf769f220530e58c7d5da137cf932be94c385fae23b9bdff7`.

The revision has a `LICENSE` file (2,406 bytes, Git blob
`fb27143ad859ecc793ea4bf4a25d177309481cec`, SHA-256
`231463ff94b75a57381da63b17b28cd9209753110fe151002cc98d758d8b096d`). The
text grants broad use, modification, and redistribution rights and embeds a
BSD-style notice for the derived `DataFrameMapper` code. However, GitHub's
license API reports `key=other`, `spdx_id=NOASSERTION`; the repository does
not provide an unambiguous SPDX identifier for the combined custom license.
This prevents a trustworthy `source.license_spdx` value in a publishable
catalog task until the license is owner-approved or represented as an
explicit reviewed license reference.

## Test, Setup, And Source Overlays

The image fixture contains these files. Text files are CRLF and all copied
files have mode `0755`; the upstream files are LF and mode `0644`. After
CRLF-to-LF normalization, every content hash matches the locked commit:

| Path | Image SHA-256 | Upstream normalized SHA-256 | Result |
| --- | --- | --- | --- |
| `tests/test_data/cars.csv.gz` | `8393a0d6711abbe66db6de74e0fc947ee69e039baac36d8887004dfd27eebf74` | `8393a0d6711abbe66db6de74e0fc947ee69e039baac36d8887004dfd27eebf74` | exact bytes; mode overlay |
| `tests/test_dataframe_mapper.py` | `8af3e2bce075345b4798420f321b49cbadc00eae67ae62c220cea3c95f342a13` | `0681f314cdc0ff65093df1a219eb914db76ab85bc1806e84996b00ac4c509716` | CRLF/mode overlay only |
| `tests/test_features_generator.py` | `995028c7ff46cf74111f41f46141d88b0fc667e3b9520046e632c51fea42b5c0` | `2a5155c1e8535daabc97a6b9afdbbc9c180310048ca7d050d541d1201577b23c` | CRLF/mode overlay only |
| `tests/test_pipeline.py` | `d2f69aaea92d8b53f7b87c72abae4fda0b90012b9ff0ff3ddb93310709533cfc` | `d2bdbccfac68f4801844c35315af85639c4c8d65b74e0f8be47d377b979fd526` | CRLF/mode overlay only |
| `tests/test_transformers.py` | `bae3404eec61d9bd92a1a06f287a2b4f696a1f60d716b0c64ded252ef1a2f7da` | `94af6991c5e6155a0ef34e87cc6484a90d610e03cf96c18311d2d9fc4a8e747e` | CRLF/mode overlay only |
| `setup.py` | `67dc4a521c65f2484489d4c9b168af15240b1df3c043b26a82e7f2396e5835e9` | `b2dae5b2401d61719a6b94da739e1be9d01e63872dde82afd519844b428b70c2` | CRLF/mode overlay only |
| `setup.cfg` | `918d74110638e4b14997b2a47d9270e9d16a95298aad5d227bbc2d154653af90` | `6f5621b18366e67c70348b965a34fd8e9a5c02bd9f8b7b3504ee9c28900d3dd0` | CRLF/mode overlay only |

No semantic test, setup, or source overlay was found in the copied image
files, and no image implementation source was present to compare. The
line-ending and mode differences are reproducible packaging overlays, but
must remain documented rather than being called an unmodified source tree.

## Publication Blockers

The source commit and image digest are immutable and the content overlay is
understood, but publication is not coherent for the following independent
reasons:

1. **License metadata is unresolved.** The upstream license is a custom
   combined notice and GitHub returns `NOASSERTION`; no reviewed SPDX mapping
   is available for `source.license_spdx`.
2. **The denominator is not frozen.** `70` is only the legacy count and a
   static AST total. No collection/JUnit/node-id artifact exists, and this
   lane did not run pytest. A changed collection would silently change the
   metric unless the final verifier rejects the mismatch.
3. **Dependency closure is not locked offline.** The image build uses
   networked `pip install` commands and no hash-locked wheelhouse or equivalent
   artifact is available. The image's `scikit-learn==0.24.2` also conflicts
   with the public instruction's `scikit-learn>=1.3.0` declaration.
4. **The candidate boundary is unproven and currently non-compliant.** The
   frozen tests directly import `sklearn_pandas` and exercise pandas/sklearn
   objects in the pytest process. No task-specific `candidate_client`
   subprocess/RPC adapter exists. A root/trusted pytest process that imports
   candidate code directly violates the separate-verifier contract.
5. **Environment metadata differs from the public instruction.** The
   instruction states Python `3.9.23`; the immutable image config is Python
   `3.9.24`. This requires an explicit reviewed environment/version decision,
   not silent normalization.

Do not create a Harbor 1.4 bundle or alter the legacy denominator to bypass
these findings. To reopen, obtain reviewed license provenance, collect the
final verifier image and freeze `collected - skipped`, lock the complete
offline dependency closure, resolve the Python version contract, and adapt
the behavior checks to an approved candidate subprocess boundary. Only then
should task-local Harbor assets be generated and passed to the parent for
Oracle and control gates.

## Static Validation

No Docker image build, container execution, Harbor run, Oracle, or pytest
execution was performed. Static work consisted of:

- Reading `AGENTS.md` and `CONTRIBUTING.md`.
- Hashing and parsing all four legacy artifacts.
- Reading the conversion-loop record for the immutable image reference.
- Inspecting the registry manifest/config and OCI layers without starting a
  container; extracting only temporary setup/test metadata for comparison.
- Cloning the upstream repository, resolving the full commit, comparing all
  image test/setup files, hashing the unprefixed Git archive and license, and
  checking the GitHub license metadata.
- Parsing the frozen Python tests with `ast` and checking the test inventory.
- Verifying that this task directory contains only this blocked audit file.
