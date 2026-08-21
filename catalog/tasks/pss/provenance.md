# PSS Provenance Audit

Status: `packaged` task-local Harbor draft. This audit was completed without
starting Docker, Harbor, pytest, Oracle, or a negative-control run. The parent
must complete the three-run Oracle gate and empty/stub/forgery/offline controls
before any dataset publication decision.

## Legacy Contract

The four legacy inputs were inspected without modifying them:

| File | Bytes | SHA-256 | Frozen meaning |
| --- | ---: | --- | --- |
| `test_files/pss/start.md` | 36,785 | `c3184e68a707bb8f6196973fbe0cd50c0cc135a2b2d24aebd93f5c53efdf65e7` | Public repository-generation instruction |
| `test_files/pss/test_case_count.txt` | 2 | `25fc0e7096fc653718202dc30b0c580b8ab87eac11a700cba03a7c021bc35b0c` | Declared effective denominator `46` |
| `test_files/pss/test_commands.json` | 66 | `69c951a45d31bb01099b9f222f19e8682b19c94407e0436fe85ece8248ca92b7` | `pip install -e .`; then `pytest --continue-on-collection-errors test` |
| `test_files/pss/test_files.json` | 8 | `ecfd160805b1b0481fd0793c745be3b45d2054582de1c4df5d9b8fa4d78e7fbc` | Protected path `test` |

The task-local `instruction.md` and `harbor/instruction.md` are byte-identical
to `start.md`. The Harbor verifier replaces the candidate's `test` tree with
the immutable fixture from the pinned image after the editable install.

## Immutable Verifier Image

The conversion-loop state at
`/root/NL2RepoBench/.nl2repo/conversion-loop/state.json` assigned:

```text
ghcr.io/multimodal-art-projection/nl2repobench/pss@sha256:38e0fcf6fb1a74781d6d57c524c750be9e56f0173193733c4a23cf6e8c8d1459
```

The record resolves to `linux/amd64`. Registry inspection resolved a Docker
Distribution manifest v2 with config digest
`sha256:4628f0ee1c8bf6cf26c1fd5e26b62b8dcd1c44b35758cec25905c945257b9718`.
The config reports CPython `3.10.11`, pip `23.0.1`, working directory
`/workspace`, and a Debian 11.7 base. The image was created at
`2025-09-17T08:14:36.994000302Z`.

Relevant immutable image layers are:

| Purpose | Compressed layer digest | Bytes |
| --- | --- | ---: |
| Initial hidden-test copy (`COPY ./pss-main/test /workspace`) | `sha256:015b0a71392c3d4262a238e5c42ac6bfd563dacaa13daaaf01db1e58441ad2d8` | 34,582 |
| Source copy (`COPY ./pss-main /pss`) | `sha256:5885cc585c4606d660087df8d07669b762d5bd13722c0ccd95524281de7c397c` | 222,610 |
| Legacy editable install | `sha256:fc42b06721ecd708b8b916a6a6563dfc2b4f97de3ebe3fa3053ca3d1dbfd1f70` | 3,509,180 |
| Test/runtime dependencies | `sha256:b41dd23be2ca498b32135ab65e1c72c94c767407cc4d6061a853680ebcd4fa42` | 5,396,431 |
| Frozen image collection cache | `sha256:2d9be19f36849bf613dcf34f3935fe782cdb87141a138f7a611582ee787d4438` | 143,058 |
| Final immutable workspace fixture copy | `sha256:961fb1b97d1f65533fb77ed095f88b1f25b4698a2d2d7db52ff929675868ef82` | 11,056 |

The final fixture is copied from `/workspace/test` into the derived verifier
image at build time. Hidden test bytes are not tracked in this catalog task.
The derived Dockerfile creates a private SHA-256 manifest inside the verifier
image and freezes the fixture read-only; the manifest is never supplied to the
agent image.

The image history records `pip install -e .`, installation of `colorama` and
`pytest`, and `cd /pss && pytest`. Installed test/runtime distributions read
from the immutable layer are:

```text
colorama==0.4.6
exceptiongroup==1.3.0
iniconfig==2.1.0
packaging==25.0
pluggy==1.6.0
Pygments==2.19.2
pytest==8.4.1
tomli==2.2.1
typing_extensions==4.14.1
```

This is image evidence, not a standalone hash-locked offline dependency
bundle. The catalog therefore keeps `[dependencies].status = "unknown"` and
the lifecycle below `published`.

## Frozen Test Inventory And Denominator

The final `/workspace/test` fixture contains 79 regular files totaling 50,293
bytes. Its deterministic path/hash manifest is 8,014 bytes with SHA-256
`a96a99bebf5625c230bf8032a144f24cbaad3ca423a302a441fe5abf7520c321`.

The image's pytest cache contains exactly 46 node IDs. The cache file is 3,062
bytes with SHA-256
`23ae80faa75a385ff97d3b40b869c4c99a92ab6dd208c3dd22859331deb2f3b0`.
Static AST inventory found no parametrization, skip, or xfail decorators; raw
collection and effective denominator are therefore both 46:

| Module | Bytes | Image SHA-256 | Static test items |
| --- | ---: | --- | ---: |
| `test_contentmatcher.py` | 4,308 | `1073a08cfa1383a3ff5f71cbe6c40178fe9df414e2a2fedc7db7242b6ab0b6dd` | 7 |
| `test_driver.py` | 7,843 | `08d99396f4004cfd1b3d3acf95cc47284430c6a59d9d8e622d483763ea4f7dca` | 7 |
| `test_filefinder.py` | 7,960 | `ce4731e67d935c54316c34bda854d41d0bd7cb3ea7798ab6b32b3445cf862d6e` | 5 |
| `test_pssmain.py` | 26,422 | `8da13876f18b2bf0e4fd3cff98fb08c5611daac033c474030ffebda07d7dd770` | 27 |

The remaining 75 fixture files are package-free test data, `__init__.py`, and
the test `utils.py`. The Harbor grader requires `collected == 46` and
`collected - skipped == 46`; collection mismatch is invalid and earns zero.

## Upstream Source And License Lock

Exhaustive comparison of the image source-copy layer against all 329 reachable
commits in `https://github.com/eliben/pss` selected this full revision as the
maximal source baseline. Among 111 comparable tracked paths at this revision,
106 are byte-identical and the only five differences are the setup file and
the four test-module overlays documented below:

```text
b40cf0b6f1b8f8cb965144317e9ab7902b5fcb0b
```

It is the 2025-06-21 commit `Add .4th as supported extension for Forth`, with
tree `aafc9fe9904efd6fab40dd8dde8bf4db75764ef5`. The reproducible source lock
is:

```bash
git archive --format=tar \
  b40cf0b6f1b8f8cb965144317e9ab7902b5fcb0b > pss-source.tar
sha256sum pss-source.tar
```

Expected archive size is 266,240 bytes and expected SHA-256 is
`2c86bef90a85c8d09fd0a66d64d183f9960bc46f1489fce629303a92b43bee9b`.
`harbor/solution/solve.sh` fetches and verifies this exact revision and archive
before materializing `/workspace`.

The upstream `LICENSE` is 1,589 bytes, Git blob
`0d14322b963c11c98e8fc2957d2ff3f738a6f64f`, and SHA-256
`54f6df3757daa8bcf326903a793e794cd5b5efa53bffa529eb03ec01a9d90114`. It
states that pss is public-domain software and includes the standard Unlicense
text; `Unlicense` is the text-based SPDX mapping recorded in `task.toml`.
The vendored `psslib/colorama/LICENSE.txt` is the New BSD / BSD-3-Clause
license (SHA-256
`15137d6c822e3ab097093a33c3a39a9df699f373f6438867ad534ff60762a947`).
GitHub's license API returns no SPDX identifier for the public-domain file, so
the catalog value is based on the checked license text rather than an API
claim.

## Test Overlay Audit

The image fixture is not an unmodified upstream test tree. All 79 paths are
present at the pinned upstream revision, and 75 are byte-identical. Four test
modules are benchmark overlays:

| Path | Upstream blob / SHA-256 | Image SHA-256 | Image Git-blob SHA-1 |
| --- | --- | --- | --- |
| `test/test_contentmatcher.py` | `81c86cfdc879304addc62e23c403cd9b1591da77` / `32e2fe5b256b1b7ada635f5546d7fa57944fd994d171f834db45d79fba8f5f60` | `1073a08cfa1383a3ff5f71cbe6c40178fe9df414e2a2fedc7db7242b6ab0b6dd` | `86004acc66e0327d42413be7d6701bf2a3ad9479` |
| `test/test_driver.py` | `1f34a373b866cc7f65a15e7a858f3d3692d03d10` / `1c5b694f560dbefeaa7850660d99e73af7d7848698038e7f3ebec3152ee25d3e` | `08d99396f4004cfd1b3d3acf95cc47284430c6a59d9d8e622d483763ea4f7dca` | `b1a1935864df832e3730ef85a3e76029ca9366d2` |
| `test/test_filefinder.py` | `db897e0395c7eac21d488ee26ac32d991d812ab9` / `91a075402880678b4d55c3ca1b6c8cb2c010ae9d114427c368574c79778ef474` | `ce4731e67d935c54316c34bda854d41d0bd7cb3ea7798ab6b32b3445cf862d6e` | `11993bcbf1b7ac488a73b26b719d78f3d7321e00` |
| `test/test_pssmain.py` | `95d6aef722d7e6a1b77e000fe5c60acc101dc14` / `cb870c17a7a8f85e994db27ec9852c87005920793158925e7b4818bbec8f3ccd` | `8da13876f18b2bf0e4fd3cff98fb08c5611daac033c474030ffebda07d7dd770` | `c6a2d7370f59c50dbd738fbbb8bcd0f6e8980167` |

The table separates upstream Git blob IDs from SHA-256 file hashes; the image
Git-blob IDs are only content fingerprints for the immutable fixture. The
normalized overlay blobs were searched against every reachable upstream object
and none was found. Changes include wildcard imports, delayed
imports, revised exclusion-pattern assertions, and disabled duplicate test
blocks; they are pinned by the immutable image and must not be silently
represented as upstream source tests.

The image's `setup.py` is also an overlay. The source-copy version used during
the recorded image build has SHA-256
`76af02ec75a0c6ea60ccece300e706c162103a332acfa98eb8ddaacd95475a7e` (upstream
b40 SHA-256 `90d908f279a717927076ecf73f7d8e13f5d8c2e5d6c2aa7203405d18c66bf45`)
and comments out README long-description/fallback setup logic. The final
`/workspace/setup.py` layer has SHA-256
`a79a941804d6a6ce4cc800de87a2744a9ab5ce61860d210d9f11004c2a3dd98e` and is a
further simplified setup overlay. Neither setup overlay is used as a hidden
test; the Harbor Oracle fetches the pinned upstream source archive, while the
verifier obtains only the protected `test` tree from the image.

The image build's existing `RUN cd /pss && pytest` layer and its 46-node cache
show that the overlayed source/test pair was internally collection-compatible.
This is static image evidence, not a fresh Oracle result and not a substitute
for the parent gate.

## Boundary And Recommendation

The frozen tests import only Python standard-library modules, the pss package,
and the vendored formatter support; no network service, database, GUI, or
external process is required by the test inventory. The verifier can therefore
run with `network_mode = "no-network"`. The agent environment remains public
because the Oracle solution fetches the immutable Git revision.

Residual risks to resolve at the parent gate:

1. The public prompt asks for dependency declarations, while the pinned
   upstream `setup.py` has no `install_requires`; pss vendors colorama, and the
   verifier image separately supplies top-level `colorama==0.4.6`.
2. The image setup/test overlays are pinned and auditable but are not upstream
   Git blobs; an Oracle run must confirm that the clean b40 source archive
   remains compatible with the image-pinned tests.
3. The agent base is the repository toolchain's pinned Python 3.12 image while
   the legacy verifier is Python 3.10.11; cross-version behavior is not yet
   gated.
4. No standalone hash-locked offline wheelhouse or separate candidate-client
   verifier contract is recorded in this task-local draft.

Keep this task at `packaged` until the parent records three independent valid
Oracle runs with stable collection `46` and reward at least `0.80`, followed by
empty, packaging/stub, forgery, and offline controls. Do not add `pss` to a
shared dataset in this lane. If the parent cannot accept the image-pinned test
and setup overlays, replace this package with a blocked audit rather than
silently rewriting the denominator or claiming upstream test parity.

## Static Validation Record

Completed in this lane without Docker/Harbor/pytest execution:

- legacy four-file SHA-256 and JSON/count inspection;
- conversion-loop state read for the immutable image reference;
- registry manifest/config/layer retrieval and digest verification via HTTP;
- source clone, full-SHA/tree/archive/license resolution, and exhaustive path/blob comparison;
- image layer extraction under `/tmp`, dependency metadata inspection, AST test inventory, pytest-cache node-ID count, and reachable-object overlay search;
- task TOML parsing, shell syntax checks, Python grader compilation, instruction parity, and repository diff inspection.

The task-local files contain no hidden test bytes, image layers, source archive,
run results, Oracle reward, or control result.
