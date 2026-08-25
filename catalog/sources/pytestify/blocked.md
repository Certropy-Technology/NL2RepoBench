# `pytestify` Static Provenance Audit

Status: **blocked**. This directory contains the audit, a blocked task
descriptor, and hash-bound production evidence. It contains no Harbor bundle,
Oracle solution, verifier script, grader, or hidden test bytes. The task is not
ready for Harbor publication because its frozen tests import candidate code
directly inside pytest and there is no approved candidate-client/RPC adapter or
trusted report boundary for this plugin-sensitive contract.

No legacy file, dataset file, conversion-loop state, or other task directory
was changed.

## Legacy Contract

The four legacy inputs were read without modification:

| File | Bytes | SHA-256 | Evidence |
| --- | ---: | --- | --- |
| `test_files/pytestify/start.md` | 43,514 | `a3020df1912c75918db8d75b92e72e177312f9a735835b6e6b0bc2d454581898` | Public instruction |
| `test_files/pytestify/test_case_count.txt` | 3 | `1be00341082e25c4e251ca6713e767f7131a2823b0052caf9c9b006ec512f6cb` | Declared denominator `122` |
| `test_files/pytestify/test_commands.json` | 67 | `3bd822b96ae432d75e8a3d09a40c856f17f3164f200f1eb0fee6b684be49ace9` | `pip install -e .`, then `pytest --continue-on-collection-errors tests` |
| `test_files/pytestify/test_files.json` | 9 | `af7f0b2bd342822f2fa8e6a9fda610570f911f30d3108379ea4184c0866727c3` | Protected path `tests` |

The command and path JSON parse successfully, and the count file contains
`122`. This count is a legacy declaration, not by itself a frozen pytest
collection record.

## Pinned Verifier Image

The canonical conversion-loop record at
`/root/NL2RepoBench/.nl2repo/conversion-loop/state.json` assigns this
immutable `linux/amd64` image:

```text
ghcr.io/multimodal-art-projection/nl2repobench/pytestify@sha256:2eba74e9ae27fa58dddeec96e287ec5405151e926379683fdee73272ce51423b
```

The loop also records the requested tag
`ghcr.io/multimodal-art-projection/nl2repobench/pytestify:1.0`. Read-only
registry inspection returned the same manifest digest. The image evidence is:

- manifest media type: Docker distribution manifest v2;
- config digest/size: `sha256:ba4cb34302008ed64fe5eb3549ef4c25bc24a361ce85429f78f3a24c8fafb53f`, 7,842 bytes;
- architecture/OS: `amd64` / `linux`;
- working directory: `/workspace`;
- command: `tail -f /dev/null`;
- Python: `3.9.23`;
- task-bearing final layer: `sha256:5061db7398dd34825ed4d6eb801ef5e9657247e6c1f308ba1fe4eadf7b8c44db`, 8,728,980 compressed bytes;
- observed distributions: `pytest==8.4.1`, `pytest-xdist==3.8.0`, `tokenize-rt==6.2.0`, `setuptools==58.1.0`, and `wheel==0.45.1`.

The task-bearing layer contains `/workspace/setup.py`, the protected
`/workspace/tests` tree, pytest cache files, and installed dependencies. It
also records `pytestify.egg-link` pointing at `/pytestify-main`; the source
target is not present in that task-bearing layer. A complete merged-filesystem
source proof is therefore still required.

The hidden test source files observed under the protected image path are
listed only by metadata. Their bytes remain in the pinned image and were not
copied into this repository.

| Image path | Bytes | Image SHA-256 |
| --- | ---: | --- |
| `tests/fixes/test_asserts.py` | 11,430 | `1041ac58b673788e9353b0bfc0b365192f39fb78843e611bc6784deb8df8ebc5` |
| `tests/fixes/test_base_class.py` | 1,193 | `778755ca8f5dfe450a496165793ffeaeaa854e486272f2e690af02be7c00a8a2` |
| `tests/fixes/test_funcs.py` | 2,000 | `85236e429aa7eacabd6b0c66289e0401b43ac19150096ef01098eff5a03dbbd6` |
| `tests/fixes/test_imports.py` | 1,388 | `e39ec02f01b36447cd321a506d8a866e427780a380f1bf54709f3291dc94cffe` |
| `tests/fixes/test_method_name.py` | 1,286 | `62d37c584b76955c8a82f962ef5d42ce1d09e8aa7f55adfbaeb910eb30394d88` |
| `tests/test_main.py` | 1,530 | `079453a911dae77ba2db8437095548862d19701133b5c7a6dd18d684b5477ff8` |

The six source files total 18,827 bytes. The image also contains generated
`__pycache__` files; those are not part of the frozen source inventory.

## Upstream Source And License

The source baseline resolved from package metadata, image `setup.py`, test
history, and the public GitHub repository is:

- repository: `https://github.com/dannysepler/pytestify.git`;
- immutable revision: `bee94a399074927f55a034a84b7987474dd9c9c8`;
- tag: `1.5.0`;
- revision tree: `280466d44fe20f6a1df23a18293eb198452eab89`;
- commit date: `2023-06-03T22:04:23-04:00`;
- archive command: `git -C /tmp/pytestify-upstream archive --format=tar bee94a399074927f55a034a84b7987474dd9c9c8`;
- unprefixed archive size: 81,920 bytes;
- archive SHA-256: `41b8f6b961c5f9475e20dbe0d7087ef0c4989bc2493064804c1d13c3cfe00c50`;
- SPDX license: `MIT`;
- license file: `LICENSE`, Git blob `f8c490a89063c82af22d7934a2b0ab123f575f8d`;
- license size/SHA-256: 1,056 bytes, `45bddda5d7f62bbf366f66e8fc1b8f5bf054aea4ada0dcd34756b404c63d347e`.

At this revision, `setup.cfg` declares version `1.5.0`, runtime
`tokenize-rt>=4.0.0`, Python `>=3.7`, and only the `console_scripts` entry
point `pytestify = pytestify._main:main`. It does not declare a `pytest11`
entry point. A generated candidate may still add one, which is the boundary
risk below.

The image `/workspace/setup.py` is byte-identical to upstream: image
SHA-256 `ab0b7c3fbf7d9fe6602f3f7a9c0c3e6a644000aa741ac9ee06febfc62c6eb751`,
upstream Git blob `a03590f54d8b03c2bee4276a20b3bf402d26b06c`, size 74 bytes.
The source lock is the intended upstream baseline, not a claim that the
unobserved `/pytestify-main` path is byte-identical; future materialization
must verify that explicitly.

## Test Overlay

All six image test files differ from the corresponding files at the pinned
upstream revision. The differences are only import statements:

| Path | Image SHA-256 | Upstream Git blob | Upstream SHA-256 |
| --- | --- | --- | --- |
| `tests/fixes/test_asserts.py` | `1041ac58b673788e9353b0bfc0b365192f39fb78843e611bc6784deb8df8ebc5` | `6d16ccf05f9f1b4b690324851f2afa72872c4195` | `32af16ff0a3665438f297c5035e83bc5420b671c9ae2f40fcbb893aab24e6509` |
| `tests/fixes/test_base_class.py` | `778755ca8f5dfe450a496165793ffeaeaa854e486272f2e690af02be7c00a8a2` | `732b42685f84b6fd2ea7fd987fd783cf14f7c824` | `47a195290c8dc3bfb0932627be225a684853e95fcd723f416b06c3aa1a70fd95` |
| `tests/fixes/test_funcs.py` | `85236e429aa7eacabd6b0c66289e0401b43ac19150096ef01098eff5a03dbbd6` | `fb3c93ff8a510a8b678ad8c5b3fc625c458e8a6f` | `dea99de5d61cb4308b08b0b935a2f00f463bdac765485147f22b98fa0f1413ad` |
| `tests/fixes/test_imports.py` | `e39ec02f01b36447cd321a506d8a866e427780a380f1bf54709f3291dc94cffe` | `c526f83f3b618731efcd57a415e8e89a8d9c754e` | `cb1596faf955177b68fd324785225256251e43b6a24136678e9b07ba329d3d28` |
| `tests/fixes/test_method_name.py` | `62d37c584b76955c8a82f962ef5d42ce1d09e8aa7f55adfbaeb910eb30394d88` | `d1365f03e3024ab4784d54fd32c7e9bb8d0b6cec` | `c0c149ffaa846ebb845033bd666b81fa3fc9a2f71ed083662c038cb9b05eacbc` |
| `tests/test_main.py` | `079453a911dae77ba2db8437095548862d19701133b5c7a6dd18d684b5477ff8` | `4ca7b7b6d5ae24a5a65e0f4c7d7effb5d353a076` | `5d853f88a441a3159d3f0c8f2fab918d903cdeabf3bdcb77dfca138a4fa117a7` |

The normalized, path-stable overlay diff is 1,436 bytes with SHA-256
`8e525697c4f8861fda326b3f02a5b104f10e14e22de2e015ab1566942c59f457`.
It changes the five fixes tests from named imports to wildcard imports and
changes `test_main.py` to a wildcard `_main` import while leaving the former
named import as a comment. The public instruction mentions wildcard imports,
so the overlay is understandable, but it remains benchmark-authored and
needs an owner-approved overlay manifest for publication.

## Denominator Audit

Static AST inspection of the six image test source files gives:

| File | Literal parameter cases | Ordinary test functions | Contribution |
| --- | ---: | ---: | ---: |
| `tests/fixes/test_asserts.py` | 69 | 0 | 69 |
| `tests/fixes/test_base_class.py` | 11 | 0 | 11 |
| `tests/fixes/test_funcs.py` | 16 | 0 | 16 |
| `tests/fixes/test_imports.py` | 7 | 0 | 7 |
| `tests/fixes/test_method_name.py` | 13 | 0 | 13 |
| `tests/test_main.py` | 0 | 6 | 6 |
| **Total** | **116** | **6** | **122** |

All parameter values are literal AST values. No `pytest_plugins` assignment,
pytest hook definition, skip marker, xfail marker, or custom collection hook
was found. The image cache is not usable collection evidence:
`workspace/.pytest_cache/v/cache/nodeids` contains `[]` (2 bytes, SHA-256
`4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945`), while
`lastfailed` marks all six test files. No JUnit report or structured
collection artifact is present in the available image evidence.

Thus `122` is numerically consistent with the legacy declaration and static
test shape, but cannot yet be promoted to
`expected_total_source = "frozen-collection"`. A final verifier must record
stable node IDs, collection errors, skipped cases, and
`collected - skipped = 122` before publication.

## Pytest Plugin Boundary

The frozen tests import candidate code in-process, including:

- `from pytestify.fixes.asserts import *`;
- `from pytestify.fixes.funcs import *`;
- `from pytestify._main import *`;
- calls to `main([...])` that mutate candidate-created files.

There is no task-specific candidate-client or JSON/RPC adapter in the pinned
image or this task directory. Running private tests as trusted/root pytest
would put candidate code in the trusted verifier process, violating the
separate-verifier contract. Running pytest as an unprivileged candidate
process avoids root import but leaves two integrity problems:

1. pytest plugin autoload can discover a candidate-supplied `pytest11` entry
   point from generated packaging metadata. Setting
   `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1` is necessary, but no recorded verifier
   proves it is enforced before pytest startup.
2. The candidate-owned pytest process can write or replace its JUnit output.
   A grader that trusts that file can be forged even when hidden test bytes are
   root-owned and copied from the pinned image.

The hidden tests define no pytest hooks and upstream declares no `pytest11`
entry point. That does not resolve the risk: the generated candidate may
provide arbitrary packaging metadata or import-time behavior.

Other unresolved production gates are the standalone hash-locked offline
dependency bundle, no-network verifier proof, source materialization proof,
and three valid Oracle/control runs. No Docker, Harbor, pytest, candidate
install, Oracle, or negative-control process was run in this lane.

## Decision

Keep `pytestify` **blocked**. Do not create Harbor 1.4 assets from the current
evidence. The source URL, full upstream SHA, MIT license, archive digest,
image digest, test hashes, overlay, and static denominator are recorded for a
future reopen, but the candidate/plugin/report boundary is not trustworthy.

To reopen:

1. preserve the six private test files and normalized overlay manifest from
   the pinned image without exposing them to the agent image;
2. implement and review a pytestify-specific candidate-client/RPC adapter, or
   obtain an approved verifier contract that keeps candidate imports and
   report generation outside the trusted grader;
3. disable pytest plugin autoload before candidate startup and prove that
   candidate entry points, `sitecustomize`, and import hooks cannot alter
   trusted collection or reward files;
4. lock the complete offline verifier dependency closure and materialize the
   upstream source at `bee94a399074927f55a034a84b7987474dd9c9c8`;
5. collect the final private fixture and prove a stable 122-test denominator,
   then run the three independent Oracle gates and empty, stub, forgery, and
   offline controls.

## Static Validation

Completed without Docker, Harbor, or pytest execution:

- read `AGENTS.md` and `CONTRIBUTING.md` and neighboring audit records;
- parsed all four legacy JSON/count artifacts and recorded raw hashes;
- read the canonical conversion-loop record without modifying it;
- resolved the Docker manifest, config, layer digests, platform, workdir,
  command, and image Python through read-only registry requests;
- downloaded and hash-checked task-bearing image layers, then inspected their
  file list and metadata;
- cloned the upstream GitHub repository and computed the full revision, tree,
  archive, license, and test blob identities;
- compared all six image tests with upstream and computed the normalized
  overlay digest;
- parsed the image tests with Python `ast`, expanded literal parametrization,
  and checked plugin/skip/hook markers;
- validated the blocked descriptor, explicit no-network policy, and hash-bound production-evidence record; no files are staged.
