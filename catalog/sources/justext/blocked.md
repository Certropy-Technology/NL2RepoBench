# jusText Static Provenance Audit

Status: **blocked**. This directory intentionally contains an audit record only;
there is no catalog `task.toml`, public-instruction copy, Harbor bundle, Oracle
script, or hidden-test byte in this worktree. No Docker, Harbor, successful pytest test run, Oracle,
or negative-control run was performed in this lane. A host `pytest --collect-only`
probe was attempted but `pytest` is not installed in the worktree environment.

The legacy identity and the test-count arithmetic are recoverable, but the
pinned verifier image contains an unapproved **functional source overlay in the
text-extraction core**. The overlay changes default classification thresholds
and paragraph boundaries in addition to making an lxml import compatible with
the image. The image's hidden tests do not provide an owner-approved patch
manifest for those changes, and the public instruction describes the upstream
thresholds. Publishing a Harbor task would therefore conflate an upstream
source revision with a derived implementation and would make the text
extraction contract non-reproducible.

## Legacy Contract

- Legacy task: `test_files/justext/`.
- Public instruction: `start.md`, 22,930 bytes, SHA-256
  `2d0d4c0e0d212d02b41ddbf2229c2cad6caea9ffb06a17a42be97fc378b57d89`.
- Declared denominator: `61`, from `test_case_count.txt` (2 bytes, SHA-256
  `d029fa3a95e174a19934857f535eb9427d967218a36ea014b70ad704bc6c8d1c`).
- Commands, in order, from `test_commands.json` (67 bytes, SHA-256
  `3bd822b96ae432d75e8a3d09a40c856f17f3164f200f1eb0fee6b684be49ace9`):

  ```text
  pip install -e .
  pytest --continue-on-collection-errors tests
  ```

- Protected legacy path, from `test_files.json` (9 bytes, SHA-256
  `af7f0b2bd342822f2fa8e6a9fda610570f911f30d3108379ea4184c0866727c3`):
  `tests`.
- The task is classified `Easy` in `test_files/task_difficulty.csv`, but that
  legacy difficulty label does not resolve the source/verifier mismatch.

The four files were parsed as JSON/text and their identities were not changed.
The requested editable-install and exact protected-test-path contract can be
reproduced, but it is not by itself evidence that the image's source checkout
was clean or that `61` was freshly collected.

## Immutable Verifier Image

The conversion-loop state at
`/root/NL2RepoBench/.nl2repo/conversion-loop/state.json` records this image:

```text
ghcr.io/multimodal-art-projection/nl2repobench/justext@sha256:8f5f01415624b39a05c64ea288f714f8be74ea4d58c2e0149dc02b148da67082
```

The state record says `status = available`, platform `linux/amd64`, and tagged
reference `ghcr.io/multimodal-art-projection/nl2repobench/justext:1.0`.
Registry inspection resolved the requested digest to a Docker distribution
manifest v2 with:

- Config digest: `sha256:1be7cc12eaa4866fdf22af25ed7b168a98f74d490ac1f2d67c8dc7c25442dd52`.
- Image creation time: `2025-09-02T14:01:02.2885596Z`.
- Runtime metadata: CPython `3.11.7`, pip `23.2.1`, setuptools `65.5.1`,
  working directory `/workspace`, and `PYTHONPATH=/project` during the
  historical test layer.
- Relevant compressed layers:

  | Purpose | Manifest digest | Compressed bytes |
  | --- | --- | ---: |
  | tests copied to `/workspace/tests` | `sha256:ae6a186bd7a8cb336d8ac51ea369635cb92c8ea15008de5323c784bcac30a185` | 4,548 |
  | source checkout copied to `/project` | `sha256:14849ec9bb110dd3abe20d6850854065d6925ab401061076837fdb85d867c4e5` | 411,779,886 |
  | normalized `setup.py` copied to `/workspace` | `sha256:853af36d5720db98858c6bc062674f413be67dab22c64a9a29756ccd16c11ee2` | 927 |

The image history records `COPY ./jusText-main/tests /workspace/tests`,
`COPY ./jusText-main/ /project/`, installation of `lxml_html_clean`,
`pip install .`, installation of `pytest pytest-cov coverage`, a historical
`pytest tests` run, uninstall of `jusText`, copying of `setup.py`, and removal
of `/project`. Thus the final `/workspace` test copy is private image input,
but the historical baseline was run against the modified `/project` tree.
The source layer also contains generated workspace material (for example a
virtual environment, coverage output, and an archive); those files are not
accepted as upstream provenance.

## Frozen Test Inventory And Denominator Evidence

The image test layer contains exactly eight files under `/workspace/tests`,
totalling 25,486 bytes. The same bytes occur in the source-copy layer. Their
hashes and comparison with the candidate upstream revision are:

| Path | Bytes | Image SHA-256 | Upstream Git blob at `9fb3340...` | Result |
| --- | ---: | --- | --- | --- |
| `tests/__init__.py` | 0 | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` | `e69de29bb2d1d6434b8b29ae775ad8c2e48c5391` | exact |
| `tests/test_classify_paragraphs.py` | 2,891 | `e64b0dbef65112b63da66c76d7bfbbb9eeafb1882bb76f479578d867e7b5b7d3` | `b1d78ff6d367e236a4cfc45e65732204ebcd3170` | overlay |
| `tests/test_core.py` | 230 | `97a800b14774ae8a98fa4521113404d2da4d58e699cede2c6647cca9f77e0c8c` | `f6ddc231cfe57dca131fb8d06c195aa6ecdd2fdb` | exact |
| `tests/test_dom_utils.py` | 4,706 | `cecac886eacf252ff9390aeaa50444a0139722a52909c62e6ed3dcc7de34e093` | `a10cb9bc5f3492ef2675a207d0e0864221aa560e` | overlay |
| `tests/test_html_encoding.py` | 5,026 | `56ee560e7d0e232f451b3bf12e4484fcd0afe5672a4add2960c27772be6875ca` | `df529999aafb70f43981279881d4942f40b74e3e` | overlay |
| `tests/test_paths.py` | 2,480 | `059520b8c7b88945beab77c2987e97f570d9047d6077ba93027ff75541221b7a` | `6c0439e2659bf2c36e820da6237401ee152845fe` | overlay |
| `tests/test_sax.py` | 6,650 | `0f857c2f3fb58ddae89b5b8169853b2c5498733eab7dc28cae66daa8c0254a60` | `be375e8d64e7895f5f32133a08c777c174d6b0c9` | overlay |
| `tests/test_utils.py` | 3,503 | `4dfa97854cf5d4460dec7edd804a8256b7f3ff11cfe9a6cb3bfe472e853d7f49` | `a91f1890ad699dd7db1680940eb60eca30aba573` | overlay |

The ordered source/test comparison manifest (path, size, image hash, upstream
blob, and result) is canonical JSON of 2,548 bytes with SHA-256
`0625d3086f9e9dbdd2e669780b6079883e7b6b8a6196d9af231001d96a8e6536`.

Static AST inventory of the image tests finds 61 ordinary `test_*` functions,
with no `pytest.mark.parametrize`, skip/xfail marker or call, and no collection
hook. This agrees numerically with the legacy declaration (`61`), but it is
not a fresh collection record and cannot establish the required frozen
collection gate. The six test-file modifications are import-only:
`from ... import *` replaces explicit imports (with the old imports commented
out in `test_classify_paragraphs.py`). No assertion body or test count changed.

The import-only test overlay is not the blocker. It does, however, mean the
hidden suite must be represented as image provenance rather than falsely
claimed to be an unmodified upstream test bundle.

## Upstream Source And License Lock Candidate

The upstream project is:

```text
https://github.com/miso-belica/jusText
```

Exhaustive comparison of the image source-copy layer against all 202 reachable
upstream commits identifies a unique maximum at the release commit
`9fb3340ad2087110348de513e4a4b6fd4f3cc839` (`v3.0.2`, dated 2025-02-25): 122
of 130 image-present upstream paths are byte-identical. One upstream-tracked
path (`MANIFEST.in`) is absent from the image source layer, and the image has
additional generated workspace paths. The next closest reachable commits
match at most 121 paths. This is the strongest recoverable upstream boundary;
it does **not** make the image tree an unmodified checkout.

For that upstream revision:

- `git archive --format=tar 9fb3340ad2087110348de513e4a4b6fd4f3cc839` is
  2,672,640 bytes with SHA-256
  `505425ef32656e4073d8dcbae0e59e77f001aa686d8e17ab630c3ff94f7edb68`.
- `LICENSE.rst` is the BSD 2-Clause license, 1,339 bytes, Git blob
  `2034117e01507a6c26731d34eedf08649124c89a`, SHA-256
  `d71c0b2234fd22e9f295986ed8f22cf425b7a4c269248d214eb8bda2a32e7179`.
- Upstream `justext/core.py` is 13,177 bytes, blob
  `fb4316d72a8e095c13b10ead978e3c0699f080f2`, SHA-256
  `b870b975ed98629ec7d310d364ca99a886e9a942ab66c19de5f8e22ca1a64724`.
- Upstream `setup.py` is 2,114 bytes, blob
  `7a2676342be02566bdcfa25929f502bf59a8f75c`, SHA-256
  `654f19e112060facb6bcc5f36c38692d017827c38399fa4842f837903baab42b`.

## Functional Source Overlay (Blocking Finding)

The image source-copy layer's `justext/core.py` is 13,201 bytes, SHA-256
`39437b8da4409444cb54aec01668ad4af919d7dd8a10edf2739e780e1f924414`, and is
not any blob in the fetched upstream history. Its differences from the
upstream revision are:

1. `from lxml.html.clean import Cleaner` becomes
   `from lxml_html_clean.clean import Cleaner` (an environment compatibility
   change).
2. `STOPWORDS_LOW_DEFAULT` changes from `0.30` to `0.20`.
3. `STOPWORDS_HIGH_DEFAULT` changes from `0.32` to `0.22`.
4. `PARAGRAPH_TAGS` adds `main` and `article` as paragraph boundaries.

Items 2--4 change the text-extraction contract. They are not described as
accepted deviations in the legacy instruction: the instruction states the
upstream default stopword thresholds (`0.30` and `0.32`) and gives no reviewed
replacement defaults. Adding `main`/`article` changes paragraph construction
and therefore link density, stopword density, and downstream classification.
The image source overlay comparison manifest for the eight modified tracked
files (including `core.py`, setup, and six test files) is canonical JSON of
2,548 bytes with SHA-256
`0625d3086f9e9dbdd2e669780b6079883e7b6b8a6196d9af231001d96a8e6536`.
No owner-approved overlay revision, patch artifact, or license/provenance
record for the functional changes is present in the loop state or repository.

The image's `setup.py` is also a build-time overlay (1,970 bytes, SHA-256
`c4b966662bffba9d72aac374baba400fc7b1f3229a7879fbe8a24e7f821b39f8`): it
replaces README/CHANGELOG long-description loading, changes dependency
spelling to `lxml`, `lxml-html-clean`, and `chardet`, and removes
`package_data`. This setup overlay is separately identifiable, but it does not
explain or authorize the functional `core.py` changes.

## Text-Extraction Risk Assessment

The retained tests do cover HTML preprocessing, comments/head removal, charset
detection, SAX paragraph construction, `<br>` boundaries, link character
counts, path bookkeeping, and heuristic classification. The image overlay
leaves those assertions intact and only broadens imports. Nevertheless, the
most important text-extraction defaults are now ambiguous:

- a candidate built from the locked upstream archive implements `0.30/0.32`
  defaults and does not treat `main`/`article` as block boundaries;
- the historical image baseline ran the modified `core.py` with `0.20/0.22`
  and `main`/`article` boundaries;
- the public instruction describes the former defaults while the image source
  embodies the latter behavior; and
- no frozen runtime collection or Oracle evidence is available in this lane
  to prove that the two implementations have the same effective score.

A Harbor `solve.sh` that silently applies the functional patch would turn the
source lock into an undocumented derived implementation. A solve script that
uses only the upstream archive would no longer reproduce the image baseline.
Either choice is unsafe for a benchmark task whose primary risk is text
extraction.

## Decision And Reopen Conditions

Keep `justext` **blocked** as a source/verifier provenance blocker, not as a
model failure. Do not create a Harbor 1.4 bundle from the current evidence.
The legacy count and image test overlay are numerically coherent, but the
functional source overlay makes the behavior boundary incoherent.

To reopen, obtain one of these explicit decisions and freeze a new immutable
artifact:

1. rebuild the verifier image from upstream revision
   `9fb3340ad2087110348de513e4a4b6fd4f3cc839`, retaining only the approved
   lxml compatibility/environment adjustment, then re-collect and freeze 61;
   or
2. approve and version the full functional patch (including threshold and
   paragraph-boundary changes), update the public instruction to state that
   contract, and preserve the patch manifest alongside the image digest.

After that source decision, a later validation lane must still run three
independent valid Oracle trials, verify stable collection and denominator, and
run empty/stub/forgery/offline controls. No shared dataset/index or conversion
state was modified here.

## Static Validation Record

The following checks were run without Docker or pytest execution:

- read `AGENTS.md` and `CONTRIBUTING.md`;
- parsed and hashed all four legacy artifacts;
- read the conversion-loop state and verified the exact immutable image ref;
- inspected the registry manifest/config and relevant layer metadata;
- extracted only the image's test/setup/source layers under `/tmp` (no
  container process) and compared paths/blobs against the upstream clone;
- enumerated all 202 reachable upstream commits and selected the unique
  122/130 path-match revision;
- computed the upstream archive, license, source, setup, test, and overlay
  hashes; and
- parsed the frozen test files with Python AST and confirmed 61 functions with
  no parametrization or skip/xfail hooks.

No Docker, Harbor, successful pytest test run, Oracle, or negative-control
command was run. The only pytest probe was the unavailable host
`pytest --collect-only` command noted above.
