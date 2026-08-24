# `ipytest` Static Provenance Audit

Status: **blocked**. This audit is paired with a parseable source descriptor
and hash-bound remediation evidence. It is not a publishable Harbor task; no
Harbor runtime, Oracle solution, verifier bundle, private test archive, or
binary fixture is included, and `catalog/tasks/ipytest/` remains absent.

The legacy task identity remains `ipytest`; this audit does not modify
`test_files/ipytest/`, the dataset catalog, or conversion-loop state.

## Legacy Contract

- Legacy source: `test_files/ipytest/`.
- Declared denominator: `74`; `test_case_count.txt` SHA-256:
  `eb624dbe56eb6620ae62080c10a273cab73ae8eca98ab17b731446a31c79393a`.
- Commands, in order: `pip install -e .`, then
  `pytest --continue-on-collection-errors tests`.
  `test_commands.json` SHA-256:
  `3bd822b96ae432d75e8a3d09a40c856f17f3164f200f1eb0fee6b684be49ace9`.
- Protected path: `tests`; `test_files.json` SHA-256:
  `af7f0b2bd342822f2fa8e6a9fda610570f911f30d3108379ea4184c0866727c3`.
- Public instruction SHA-256:
  `acf918728b54a36113125f4d957f68eaded879b3247b3421d3bf32f21b0690ca`.

The legacy count and command shape are internally consistent, but the count
file is not a frozen pytest collection record. The source instruction is
therefore not sufficient evidence for a Harbor fixed denominator.

## Immutable Verifier Image

The conversion-loop state file is not present in this isolated worktree. The
immutable image reference below is recovered from the prior immutable image
probe evidence and must be reconciled with the canonical conversion-loop state
before this task is reopened:

```text
ghcr.io/multimodal-art-projection/nl2repobench/ipytest@sha256:2cf01b4aff01af5c56515be0a24d3abfe07e4d1cbfebef19b8d7b18e0d3acd09
```

Static image inventory from that probe:

- Image working directory: `/workspace`.
- Image Python: `3.10.11`; pip: `23.0.1`.
- Key installed distributions: `coverage==7.11.3`, `hatchling==1.27.0`,
  `ipython==8.37.0`, `nbval==0.11.0`, `packaging==25.0`, `pytest==9.0.1`,
  `pytest-asyncio==1.3.0`, `pytest-cov==7.0.0`, and `ruff==0.14.5`.
- The image contains `/workspace/pyproject.toml` and the frozen test tree at
  `/workspace/tests`. The image command is an idle `tail -f /dev/null`, not a
  separate candidate verifier contract.

The image has no retained structured collection report, JUnit collection
manifest, or node-id artifact in the available evidence. The historical
image build and installed package inventory are not Oracle or offline-control
results.

## Upstream Source Lock

- Upstream repository: `https://github.com/chmp/ipytest.git`.
- Full revision:
  `ea052c6ee76121d8504ec5ad35aa3b3fec9a7846`.
- Revision identity: tag `v0.14.3b1`, merge commit
  `Merge pull request #126 from chmp/fix/release`, committed
  `2025-02-16T19:15:55+01:00`.
- Git tree: `207c262542f5d3d25b5b02bddd010332fc4f12ce`.
- Reproducible source archive command:

  ```bash
  git -C /tmp/ipytest-upstream archive --format=tar \
    ea052c6ee76121d8504ec5ad35aa3b3fec9a7846 | sha256sum
  ```

  The archive is `307200` bytes with SHA-256
  `71ee968ab4f92fb7fea81008ca6e9687311c1b594118c1da18e28182b16ad8c9`.
- License: **MIT**, evidenced by `License.md` at this revision and the
  `license = "MIT"` plus MIT classifier in `pyproject.toml`.
  `License.md` is 1,090 bytes, Git blob
  `a96b5cf46f816d546643497e55cc721ad7b0d9a2`, and SHA-256
  `ea4244a34e9f87053db8477b6ba18c58628ff905820527fa62b8a605c7b1d4f6`.

The source revision is resolved as a source baseline plus an image build
overlay. All frozen test paths normalize to exact upstream blobs at this
revision, and exhaustive reachable-history lookup found no upstream object
for the image's raw CRLF blobs. This distinction is retained below rather
than representing the image as an unmodified checkout.

## Frozen Test Comparison

The image contains 20 files under the protected `tests` path. Every file is
byte-different from the Git checkout only because the image copy uses CRLF;
after `CRLF -> LF` normalization, every file is byte-identical to the
corresponding path at revision `ea052c6...`. The two paths for
`TestIssue101_Conftest.ipynb` intentionally resolve to the same upstream blob.

The raw image manifest is path-sorted as `path<TAB>size<TAB>sha256` and has
SHA-256 `2a60920c48887ed7280130ba0044404e1dff3034e5a41bca9044bd7fdbed907c`;
the 20 files total 33,256 bytes. Hidden bytes remain in the immutable image
and are not copied into this repository.

| Frozen path | Bytes | Image SHA-256 | Upstream Git blob |
| --- | ---: | --- | --- |
| `tests/TestAsync.ipynb` | 1787 | `883179b3f11a207f0ab36a82dd49e232fcac97da99c12f30bb3e5b6d4193526a` | `588740455ed74b6fd7a7643af2d5b91fab62b7f8` |
| `tests/TestCoverage.ipynb` | 4528 | `31ddb6199d4077c5b9ea0b1f11aa5d9323c00e43d6264f0974f25594e6cd812f` | `b5eed0d4b67a8c58f407bbc90134069b6372df2d` |
| `tests/TestCoverageWithConfig/.coveragerc` | 35 | `10541b6e547d0c379ae99c7facdd548358af4843518cd1607c45fd4c4bdc5b8d` | `35f472c74f8e9974236966b86a232851758c7385` |
| `tests/TestCoverageWithConfig/TestCoverage.ipynb` | 4260 | `29842d8832475f323abd8bf8df4dc8dec218c894b52b162f6230b295a55bfb38` | `f9b912f6a55ee77a0292e8397bc2d7502542e54d` |
| `tests/TestCoverageWithConfig/TestCoverageWarning.ipynb` | 1419 | `2e3f935ccb2c6b494afc161d89d9e62902ad950eafd3283b8bb080dc5521f40a` | `4a58cfddae4b34f3dc23a3dcb017b151797a4645` |
| `tests/TestDoctestIssue.ipynb` | 1039 | `bb109f3914b076349dc5a22848a22859e1757aaa0bf5df3d89d444788c80b21c` | `60a86fedb8cf104669fbffe375d3dc8c225ad4ab` |
| `tests/TestIntegration.ipynb` | 3274 | `c17a2de7cd28f1368caead76f3e80f94dc526672c2d67cac7ad4c85eb061064f` | `f011d5eb9761a62e83c5803af3441cb175f55b46` |
| `tests/TestIssue101_Conftest.ipynb` | 664 | `d075f7a298f1dd1f8325aaf4e750a134ceb0a2eaf6e57cc603ba357f52902986` | `735f6f5f2794d612829c4cec2c9064cf0724b861` |
| `tests/TestIssue21_Doctests.ipynb` | 1530 | `8733c2ea9b23878fa5fddf859d5854e2d6f38640c19042a4ddf9075acc12e521` | `52e61ec135ba1be762c4bba2c5d70821cbfb0424` |
| `tests/TestRaiseOnError.ipynb` | 1511 | `781852b9e8830a5128053789b45a24df2a9743eda0f6d8138b3af8f298de7453` | `e4f30c0afe3ae4062707110a8ad728798ad78e83` |
| `tests/conftest.py` | 2702 | `47efd70c686422109f90e4affcd866f73e228b8c854254f87a1706988f62ce53` | `3fed225900b06bc6e98a1db487d20a38bcdb7d30` |
| `tests/empty_module.py` | 0 | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` | `e69de29bb2d1d6434b8b29ae775ad8c2e48c5391` |
| `tests/nested/TestIssue101_ConftestNested.ipynb` | 664 | `d075f7a298f1dd1f8325aaf4e750a134ceb0a2eaf6e57cc603ba357f52902986` | `735f6f5f2794d612829c4cec2c9064cf0724b861` |
| `tests/test_config.py` | 511 | `c71f3ce6acea6b49ccc460c9e07cca9467ce33973467d4568b09ae3d1bd83b9a` | `caf4a3582fd877e010038507654914000adde871` |
| `tests/test_doctest.py` | 306 | `c56f59a03a48f27c13fd0d75168721de42b7267aeece92fa16b50f1be15b9fd7` | `d9d086d6aea2bf95dd92aae5b5a31f5095413b8a` |
| `tests/test_force_reload.py` | 750 | `6957a397f718e1787acea77f0fcc580772f3a4cb74ceb50f4c9fedf022e936ba` | `e61c13b0d0cfd20568156a3fdcbab1ee2edb6945` |
| `tests/test_ipytest.py` | 5282 | `7e0a7deba3e722a1abe221af2deb956035cde59b22017b41ee985ebf2172108c` | `e3d16c12c209b09b683f9e7de8c7eef7401aa29b` |
| `tests/test_ipytest_cov.py` | 1095 | `f50dfc3bf59a02529e27a3b267f05341ef56787a0e16cdb033a94aedca52f8e6` | `eb583347f1c6139f7471a65c0aa738121fa9c419` |
| `tests/test_issue_71.py` | 1346 | `58965e8f03ecd3938dff698f44a722d24ad926e8dcc386db5ba3b170abccbc4f` | `b192ce010803d74f30c8f62919ddaa2b4414ce50` |
| `tests/test_raise_on_error.py` | 553 | `907d8e63e182d802002db3933cdda1444fcad1c98150e41d43f54e4bde9650ea` | `5ac815423e4b8c4ac85a2b54fdd5f42ed664aa57` |

## Packaging Overlay

The image's packaging file is `/workspace/pyproject.toml`, not `setup.py`.
After line-ending normalization:

- Image file: 1,514 raw bytes, SHA-256
  `328ec0af2bdbde368750a962e94f2cb5f91b0b86064b00c6ab3b403461f7dbc9`.
- Upstream file at the pinned revision: 1,484 bytes, Git blob
  `d4e4eb1980f492aceff9a5bd5978c7482da94138`, SHA-256
  `1808d3083e1ba46404fefed9e4780c0642ae136e5fe4cbb0e5ba1f918da1f45c`.
- The image removes `readme = "Readme.md"` and
  `include = ["License.md"]`; the remaining content matches after newline
  normalization.

This is a packaging/build overlay, not an upstream commit. It must be
represented explicitly if the task is ever reopened; the source archive above
must not be described as the exact image filesystem.

## Denominator Audit

Static AST inspection of the 20 frozen files finds 29 ordinary Python test
functions and a 66-case lower bound after statically expanding literal
`pytest.mark.parametrize` lists. The total is not a collection proof: one
parameter list is derived from `ipytest.__all__`, and notebook collection is
performed by `nbval`. No frozen pytest collection, JUnit, node-id, or skipped
case artifact is available. Consequently, the legacy `74` cannot be promoted
to `expected_total_source = "frozen-collection"` in a task manifest.

Changing the denominator to any statically inferred value would alter the
legacy metric. Retain `74` only as the legacy declaration until a final
verifier image records stable collection and proves `collected - skipped = 74`.

## Verifier Boundary And Environment Gaps

The frozen tests import `ipytest`, `ipytest._config`, and `ipytest._impl`
directly and exercise IPython state, pytest plugins, notebook execution,
coverage hooks, and module reload behavior in-process. The available legacy
image evidence contains no task-specific `candidate_client` or subprocess RPC
adapter. A verifier that simply prepends `/workspace` or `/tmp/candidate` to
the root pytest process would directly import candidate code in the trusted
verifier, which violates the required separate-verifier boundary.

Other unresolved gates are:

- **Offline dependency lock**: the image site-package inventory is not a
  submitted hash-locked wheelhouse. `ipykernel`/`pyzmq` and related packages
  include native components whose wheel and system dependency closure is not
  recorded here.
- **Network boundary**: no Harbor verifier image, `network_mode = "none"`
  execution record, route evidence, or offline install proof exists for this
  task. The immutable legacy image reference alone does not prove a no-network
  verifier.
- **Oracle and controls**: no Oracle, empty, stub, forgery, or offline run was
  executed in this static-only lane.

These are verifier/environment blockers, not model failures.

## Decision

Keep `ipytest` **blocked**. The source descriptor records this terminal state;
do not create a Harbor 1.4 runtime directory or any hidden fixture copy from
the current evidence.
The upstream revision, MIT license, archive digest, image reference, and
test/setup overlays are sufficiently documented for a future reopen, but the
fixed denominator and compliant candidate boundary are not proven.

To reopen, first preserve the private image fixture and its normalization
manifest, then either:

1. build a dedicated no-network verifier with a task-approved subprocess/RPC
   adapter for notebook/IPython behavior, lock all Python/native dependencies
   offline, and collect a stable effective denominator of 74; or
2. explicitly author a new task version with a different verifier contract and
   reviewed denominator rather than silently changing the legacy task.

## Static Validation

The following checks were completed without starting Docker, Harbor, or
pytest:

- Read `AGENTS.md` and `CONTRIBUTING.md`, then inspected the legacy four-file
  contract and neighboring provenance-audit formats.
- Resolved the immutable image reference from prior conversion-loop probe
  evidence; no image process was started in this lane.
- Cloned/inspected the upstream Git history at `/tmp/ipytest-upstream`,
  resolved the full commit, checked all reachable test blobs, and verified
  the deterministic archive and license hashes.
- Compared all 20 image test files after CRLF normalization and compared the
  image/upstream `pyproject.toml` files.
- Performed Python AST inventory only; no test collection or test execution.
- Verified the audit is task-local with a task-scoped diff review.
