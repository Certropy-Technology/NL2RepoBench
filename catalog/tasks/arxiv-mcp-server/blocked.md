# `arxiv-mcp-server` Static Conversion Audit

Status: **blocked**. This directory is an audit record only. It does not
contain a Harbor task, an Oracle solution, a copied instruction, or hidden
test bytes. No dataset, shared index, conversion-loop state, or legacy task
file is changed by this audit.

## Legacy Contract

- Legacy source: `test_files/arxiv-mcp-server/`.
- Declared denominator: `23`; `test_case_count.txt` SHA-256
  `535fa30d7e25dd8a49f1536779734ec8286108d115da5045d77f3b4185d8f790`.
- Commands: `touch README.md && pip install -e .`, then `pytest
  --continue-on-collection-errors tests`; `test_commands.json` SHA-256
  `4c284fd236e0b4ad61b94ad22958bbc49291e185a335a8e7acfceae8f4bce44c`.
- Protected path: `tests`; `test_files.json` SHA-256
  `af7f0b2bd342822f2fa8e6a9fda610570f911f30d3108379ea4184c0866727c3`.
- Public instruction SHA-256:
  `5b7583cb0fbb3c984bdd52426a51e34bdf5a914302a182f6b81935640bd6586c`.
  It specifies application version `0.2.11`.

## Verifier Image

- Conversion-loop immutable reference:
  `ghcr.io/multimodal-art-projection/nl2repobench/arxiv-mcp-server@sha256:1e8074506767811ba7445749212b1f4eece516b003766112ce76b07c4fc2f3c8`.
- Registry inspection returned the same manifest digest and platform
  `linux/amd64`. The image config digest is
  `sha256:3f5013515b9786eb7a6e15c38602a93f6a247b0dbe41133b9a5b57bfe43c11df`.
- The config records Python `3.12.4`, working directory `/workspace`, and an
  image creation time of `2025-11-12T08:21:51.888905241Z`.
- Frozen tests are supplied by layer
  `sha256:84ddb632fa317502e65b20b65accc4834fe2358da10164e8109f72ccc6a1ff87`.
  The copied source checkout is in layer
  `sha256:64d2a21055c96f3673841df3390b6c62cba09ac890b7847529e1e44bf6d39d96`.
- Image history records copying the tests and checkout, installing
  `.[test,dev]`, successfully creating a `RUN pytest` layer, and then
  removing the checkout. The resulting pytest cache is in layer
  `sha256:493ae3697d9cd876b40ba9f6db4f9af7ced71e564f3df3085156b9fb938de454`.
  This build history is static evidence, not an Oracle gate result.

## Source Provenance

- Upstream repository:
  `https://github.com/blazickjp/arxiv-mcp-server`.
- The image checkout's `.git/HEAD` resolves to full revision
  `057e2000be7b56823239815b0fe7c7fc0dbced96`, a merge commit dated
  `2025-08-18T21:04:10-07:00`. The commit is reachable from upstream `main`
  and identifies project version `0.3.1`.
- Deterministic archive command: `git archive --format=tar
  057e2000be7b56823239815b0fe7c7fc0dbced96`. The archive is `133120` bytes
  with SHA-256
  `5dc518ca180b1222a9ced442a86e8f758f80e2f0f45d4ba80ae9b790b5a7b6e3`.
- Repository license: Apache-2.0. The commit's root `LICENSE` is the Apache
  License 2.0 text, has Git blob
  `261eeb9e9f8b2b4b0d119366dda99c6fd7d35c64`, is `11357` bytes, and has
  SHA-256
  `c71d239df91726fc519c6eb72d318ec65820627232b2f796219e87dcf35d0ab4`.
  GitHub's commit-specific license endpoint also detects `Apache-2.0`.
- The revision's `pyproject.toml` nevertheless declares `MIT`. Upstream
  later described that field as needing alignment with Apache-2.0 in commit
  `06754d799d5b6f8450cc73a2e46d19f78b368bdb`. The conflicting package
  metadata is retained here as provenance evidence rather than hidden.
- After CRLF normalization, the image working tree matches revision
  `057e2000be7b56823239815b0fe7c7fc0dbced96` except that the image copy
  removes `readme = "README.md"` from `pyproject.toml`. The upstream archive
  above is the source lock; the image-local packaging relaxation is not
  represented as upstream content.

## Frozen Test Comparison

The image contains seven test source files. Their bytes are not copied into
this repository. Every file uses CRLF in the image and, after line-ending
normalization, every Git blob matches the same path at revision
`057e2000be7b56823239815b0fe7c7fc0dbced96`.

| Frozen path | Bytes | Image SHA-256 | Normalized upstream blob |
| --- | ---: | --- | --- |
| `tests/conftest.py` | 2214 | `be699be4b462c158e0441a0b5637fd0f0a9dc52b60365f2066d4a1f63d62a841` | `ea872f2e0976d150cd25ecbfa26bfe0b5537d36b` |
| `tests/prompts/conftest.py` | 1428 | `e0726fb2ca0c5cbebe360bedb73966b6985b1e74de68685f17a5b7eee576c7b5` | `1bc07680b62ee93be7350629f8b05eb49e30f667` |
| `tests/prompts/test_prompt_integration.py` | 1416 | `e8325e9acf23a2b3dcf8d0675c54a4acf03923f3d24444b422f8196194cc8dc5` | `4760459ad2d4e48aecf7fbfe237e7fbafc30620b` |
| `tests/prompts/test_prompts.py` | 1789 | `db4ac6c6384cd7b8c55df22ada775113b123f4d006de2f0a0d7619d03bc7ee9c` | `7ccdae2fc59b3d4887824475743ca67f91d68817` |
| `tests/test_config.py` | 5388 | `7c2d068115dfb320e000301c2b21e3a8f057694f6fc0829647d94aab61ac63a9` | `54e862eb6481debde1681cf39e772a231ee41c4a` |
| `tests/tools/test_download.py` | 2961 | `ba637a8c296ac426adf1cee63fdac6c1494ad32c445115ff8641381aebb8cd22` | `234d413323f2480d5ffb7cfa73cad94559298404` |
| `tests/tools/test_search.py` | 6598 | `f62bc2dd1bb987128c42f37f9223747bea77812e9c4219073838e32117b878c5` | `149f41055127e16ca2b3e3e53f86240af1d1dcf9` |

The successful image build left a pytest `nodeids` cache with 31 unique
items. The cache file has SHA-256
`98da0cd24d697b5017b61e0a192967f436b485b4f016f9e4602672b605be8408`
and no `lastfailed` cache entry. Independent AST inventory also finds 31
ordinary test functions, no parametrization, and no skip, skip-if, xfail, or
import-or-skip marker or call. The effective frozen denominator is therefore
31, not the legacy declaration of 23.

The drift has a specific upstream boundary. Revision
`6d3419a3ea43cfd95391d2ef3b59ef58d2bf557d` identifies version `0.2.11`
and has 23 statically inventoried tests. Six of the seven normalized image
test files still match that revision, while `tests/tools/test_search.py` was
expanded by the later `0.3.x` history. The legacy instruction and denominator
refer to `0.2.11`; the pinned image source and tests refer to `0.3.1`.

## Decision

Keep `arxiv-mcp-server` **blocked** for `version-drift` and
`collection-mismatch`. A Harbor verifier pinned to 23 would reject its own
31-item collection. Changing the denominator to 31 would silently change the
legacy metric while retaining a public instruction that specifies the older
project behavior. Either choice would make provenance or scoring incoherent.

Do not create or publish a Harbor 1.4 bundle from this evidence. To reopen,
choose one coherent version boundary: rebuild an immutable verifier from the
`0.2.11` revision and freeze its 23-item collection, or explicitly author a
new task version for revision `057e2000be7b56823239815b0fe7c7fc0dbced96`
with a reviewed `0.3.1` instruction and a structured 31-item collection.
After that choice, provision an offline dependency closure and run the three
Oracle gates plus empty, stub, forgery, and offline controls in a later
execution phase.

## Static Validation

No Docker, Harbor, pytest execution, or network-dependent candidate behavior
was run. Evidence came from registry manifest/config/layer inspection, the
image's existing pytest cache, Git object and archive comparison, commit-
specific GitHub license metadata, SHA-256 manifests, and Python AST parsing.
