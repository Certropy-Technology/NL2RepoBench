# `ydata-profiling` Static Provenance and Verifier Audit

**Status: blocked.** This directory is an audit record only. It contains no
Harbor task descriptor, public-instruction projection, Oracle solution,
verifier scripts, dependency wheelhouse, or hidden test bytes. The legacy
files, dataset manifests, conversion-loop state, and other task directories
were not modified.

## Decision

Do not create a Harbor 1.4 bundle from the current evidence. The upstream
revision is recoverable and the image test path set is identifiable, but the
publication boundary is not coherent:

1. The declared denominator has no frozen collection/node-id evidence in the
   image or repository. The image contains dynamic parametrization, skips, and
   Spark startup handling that can change the effective count.
2. The no-network verifier cannot demonstrate the frozen `pip install -e .`
   setup closure: the package declares build requirements that are absent from
   the image, and no hash-locked wheelhouse or dependency artifact exists.
3. Several protected tests download external datasets at runtime. No complete
   offline dataset cache is present, and adding one would be a new fixture
   contract rather than a projection of the legacy image.
4. The image contains an unapproved `tests/conftest.py` behavior overlay and
   CRLF/executable-mode transformations. The overlay changes Spark skip
   behavior and is not represented by an immutable owner-approved manifest.
5. The production verifier must not let trusted pytest directly import the
   candidate. This suite has 118 direct candidate import statements across 36
   module paths and exercises live pandas, Spark, notebook, report, and
   rendering objects. No ydata-profiling subprocess/RPC adapter exists.

These are task/environment/verifier blockers, not model results. Do not lower
`2182`, silently remove network-dependent tests, or use the reference package
that appears in an image lower layer to make the conversion look complete.

## Legacy contract

The four legacy artifacts under `test_files/ydata-profiling/` were read without
editing:

| Artifact | Bytes | SHA-256 | Parsed meaning |
| --- | ---: | --- | --- |
| `start.md` | 393,036 | `a6336471d5d289b4cebdd0a3ec2c64d836af4177acd42612893bcefdbf410a99` | Public repository-generation instruction |
| `test_case_count.txt` | 4 | `93989d0f14e7ec638a3c6a29372246b56628ae42d36820ed73f3669a99e9491b` | Declares `2182` (no trailing newline) |
| `test_commands.json` | 67 | `3bd822b96ae432d75e8a3d09a40c856f17f3164f200f1eb0fee6b684be49ace9` | `pip install -e .`; `pytest --continue-on-collection-errors tests` |
| `test_files.json` | 9 | `af7f0b2bd342822f2a8e6a9fda610570f911f30d3108379ea4184c0866727c3` | Protected path `tests` |

The command and path values parse as JSON arrays. The declared count is the
legacy metric denominator; it is not a collection manifest.

## Immutable verifier image

The conversion-loop record at
`/root/NL2RepoBench/.nl2repo/conversion-loop/state.json` assigns this
`linux/amd64` image:

```text
ghcr.io/multimodal-art-projection/nl2repobench/ydata-profiling@sha256:baa1353a886ceaea1c411d3b88abe66adcd1407619922c874498260a7a708c15
```

The registry manifest response was digest-checked:

- Docker manifest digest: `sha256:baa1353a886ceaea1c411d3b88abe66adcd1407619922c874498260a7a708c15`;
- manifest bytes: `3457`;
- manifest body SHA-256: `baa1353a886ceaea1c411d3b88abe66adcd1407619922c874498260a7a708c15`;
- config digest: `sha256:91e5c06d17cf0acd19b7750ee4be4206c3cb4976290bfe43a27df20a3153142a`;
- config JSON bytes: `15,626`;
- config platform: `linux/amd64`, Python `3.11.7`, working directory `/workspace`, command `tail -f /dev/null`.

The relevant immutable layers are:

| Image history operation | Compressed layer digest | Bytes |
| --- | --- | ---: |
| `COPY /app/tests /workspace/tests/` | `sha256:e668309d644438d353f96d1611194b94070a84567635d9613bd611a1852f06cb` | 188,213 |
| `COPY /app/pyproject.toml /workspace/pyproject.toml` | `sha256:fb98f61d0bb6c84e183100af76b4f6a07be8fd5980a9b7590ce401065ce18963` | 1,803 |
| `COPY /app/setup.py /workspace/setup.py` | `sha256:5f0030304eda943003605fa4fcbc3dcb57b184005266d582eb063cd9778e6461` | 396 |
| copy builder site-packages | `sha256:3161415820e1a9055a5262a17f976d3d9a84e5d8f38c754dd963b0d8844e15c5` | 730,626,261 |
| copy builder `/usr/local/bin` | `sha256:37fe377c1d023ade834274567f0e6c416841d7631c839cc4c3d04e85b56c041f` | 26,843 |
| `pip uninstall -y ydata-profiling` | `sha256:aeae5b14719b8a926d326c7319863a2831d8f3465717a8bd45426e34472b68d8` | 2,024,672 |
| `pip install --no-cache-dir ... pytest` | `sha256:fdef78dcbb22a14f149504b45595c50ffc0d701c82e813f1c2480368d5ef4ee9` | 5,148 |

The image history records a Tsinghua mirror for the final pytest install and
copies the dependency tree from `/app`; it does not record a source archive,
lockfile, wheelhouse, or reproducible build command for that dependency tree.
No image was started.

## Upstream source and license lock

The image contents and installed reference package resolve to:

- repository: `https://github.com/ydataai/ydata-profiling`;
- full commit: `de97bd4a50ed49ef0c7aad452c9f5fc389cd2d48`;
- tree: `d5d9df778d84c5cc4888bf5cc602aabb2c491388`;
- parent: `7a43975cd037d5cd2b77d6c4c1472acec9bf91d8`;
- commit date: `2025-09-19T16:25:00-05:00`;
- subject: `feat: modernize dependencies and expand Python support (#1778)`.

The deterministic source archive was produced with
`git archive --format=tar de97bd4a50ed49ef0c7aad452c9f5fc389cd2d48`:

```text
size: 25,303,040 bytes
sha256: 4a45f925a8d07129b4aac3db0bf7860b52216c0ee38c6deae25cc323ca453498
```

License evidence is coherent at the source level:

- path: `LICENSE` (there is no `LICENSE.md` at this revision);
- Git blob: `2ca9866eb1ed290ace870040aae777f36d9b420c`;
- file bytes: `1,133`;
- file SHA-256: `94ef35ca6a81b18c9f8c03adeb5a816f97947d1e16991959b881ceb267211dd9`;
- SPDX: `MIT` / GitHub API `MIT License`.

The source `pyproject.toml` nevertheless declares
`license = {file = "LICENSE.md"}` while only `LICENSE` exists. The image
workspace does not copy either license file. This packaging/source-boundary
mismatch must be resolved or explicitly accepted before publication.

## Test, setup, and source overlays

The image test layer contains exactly the same 86 regular paths as
`tests/` at the locked commit: 82 Python files, three notebooks, and
`issues/data/sample_eda_df.pkl`. It contains no extra or missing regular test
path. A path/size/raw-SHA manifest (entries sorted as
`path<TAB>bytes<TAB>sha256`) is:

```text
count: 86
bytes: 208,761
raw manifest sha256: f3ace823fed94019ed007f05324c1f08acf1ef517cc881174a9bae7f0864d3ea
LF-normalized manifest sha256: ea7ea3cb05f96e59576a8ba7335199f78f2906b302c9b3e394b2362899af8299
```

The corresponding upstream test manifest has 86 paths, 204,159 bytes, and
SHA-256 `e88a2ad946a1ac3eeab77291173a1643f168ff2affc1c5b981a9020cfc456834`.
All 86 image files are mode `0755` and text files use CRLF; upstream blobs are
mode `0644` and LF. After line-ending normalization, 85 of 86 files are
byte-identical to the locked source. The sole functional test overlay is:

- `tests/conftest.py`: image adds
  `from pyspark.errors.exceptions.base import PySparkRuntimeError` and catches
  that exception while creating `SparkContext`, converting it to
  `pytest.skip("Spark backend not available")`;
- upstream normalized SHA-256: `1bc65feee60c44230706d01f6aa907edd5d560c98c772bfefeb1866ce69afc5b`;
- image normalized SHA-256: `37d5a5f7e7828c7eb445cbc91a71631cf167e9753fed341f4480f76095f2a6f9`;
- stable two-file overlay patch SHA-256: `ffac38be2c9dcc3dd7b12c8a9ccf6675b5549b994a74448dc5672d480a0ebc85`.

(The two normalized SHA values above are retained as provenance identifiers;
the source and image patch was inspected without copying test bytes into this
repository.)

The copied setup metadata is also source-identifiable after LF normalization:

| Path | Image raw SHA-256 | Upstream blob | Normalized SHA-256 |
| --- | --- | --- | --- |
| `pyproject.toml` | `b635b94c39d081aabdef3cdc20751fb3e971338d5d825f63cfc3ce1464c256f` | `eec36aa0b3458a1bb56789a662974148af37deee` | `e101fc89fa325f0c9ce98267456a8e9dd05d7026dcf2dec4916e8b796193fabd` |
| `setup.py` | `2c7ebf1b04186effdd4520efb7dae570d46809fae8f9a7b1a136e07344453613` | `4824966a122e9058b45c556b82318923ebb6c46e` | `a2d7a24ac094be19227d0ebbc0b1cad10efd6ce6cfa0f4540039ce0b42e1c9d2` |

Both image files are mode `0755` with CRLF; the upstream files are mode
`0644` with LF. The content itself matches after normalization.

The builder site-packages layer contains a complete reference
`ydata_profiling` installation: 230 regular package files compare exactly to
`src/ydata_profiling` at the locked commit, plus generated `version.py`. Its
metadata says version `0.0.dev0` and `direct_url.json` is
`{"dir_info": {}, "url": "file:///app"}`. The later uninstall layer writes
whiteouts for `ydata_profiling`, `pandas_profiling`, their console scripts, and
the ydata dist-info directory, so they are absent from the final merged view.
A derived verifier must not expose lower-layer reference files or use them as
the candidate implementation.

## Denominator and fixture audit

The legacy count `2182` has no corresponding frozen collection record in the
repository or image. Static inspection of the protected tree found:

- 196 `test*` function definitions;
- 33 `pytest.mark.parametrize` decorators, including dynamic argument
  builders that cannot be expanded from AST alone;
- 15 skip/xfail or runtime-skip sites;
- 82 compiled test `.pyc` files in the image layer (506,894 bytes), but no
  `.pytest_cache`, node-id list, JUnit XML, collection JSON, or test result
  artifact.

Consequently, static path equality does not establish that the effective
collection is 2,182, nor which parametrized/skipped cases belong in the fixed
denominator. Running pytest to regenerate the denominator is explicitly
outside this audit and would have to be a separate freeze stage.

The tests also are not self-contained under a no-network verifier. Runtime
fetches include, among others:

```text
https://data.nasa.gov/docs/legacy/meteorite_landings/Meteorite_Landings.csv
https://raw.githubusercontent.com/openeventdata/scraper/master/whitelist_urls.csv
https://raw.githubusercontent.com/ydataai/coursera-ml/master/week-1/people-example.csv
http://www.stata-press.com/data/r15/auto2.dta
https://raw.githubusercontent.com/datasciencedojo/datasets/master/titanic.csv
https://raw.githubusercontent.com/mrichman/clickstream-pandas/master/products.tsv
https://archive.ics.uci.edu/static/public/222/bank+marketing.zip
https://github.com/Teradata/kylo/raw/master/samples/sample-data/parquet/userdata2.parquet
https://ndownloader.figshare.com/files/5976042
```

`ydata_profiling.utils.cache.cache_file` downloads a missing file into the
candidate project `data/` directory. The image test layer has only the checked
in `sample_eda_df.pkl`; no complete `data/` cache or URL-pinned fixture archive
was found. Leaving the verifier online changes the required offline contract;
materializing those datasets requires an approved private artifact and a new
freeze/collection record.

## Dependency closure and candidate boundary

The copied site-packages layer contains 122 distributions. A sorted
`Name<TAB>Version` manifest is 2,014 bytes with SHA-256
`cda2f3ca35555a205b8830e6213fe6881666e9c7b628de3f35e535502c5fdda0`. Relevant
observed versions are:

```text
Python             3.11.7
pytest             8.4.2
pandas             2.3.3
numpy              2.1.3
scipy              1.15.3
matplotlib         3.10.0
pydantic           2.12.3
PyYAML             6.0.3
visions            0.7.6
phik               0.12.5
numba              0.61.0
pyarrow            21.0.0
pyspark            4.0.1
nbval              0.11.0
coverage           7.11.0
pytest-cov         7.0.0
requests           2.32.5
statsmodels        0.14.5
seaborn            0.13.2
typeguard           4.4.4
imagehash          4.3.1
wordcloud          1.9.4
dacite             1.9.2
```

The source build-system requires `setuptools>=72.0.0,<80.0.0`,
`setuptools-scm>=8.0.0,<9.0.0`, and `wheel>=0.38.4,<1.0.0`. The final image
has setuptools `65.5.1` and wheel `0.42.0`; no `setuptools-scm` distribution
is present. With the frozen `pip install -e .` command, build-isolation and
network resolution are therefore not proven satisfiable offline. No
standalone lockfile, wheelhouse, artifact URI, or hash list is present.

This is also not a safe generic separate verifier. AST inspection found 118
candidate import statements across 36 `ydata_profiling` module paths. Tests
construct and inspect `ProfileReport`, `Settings`, summarizers, typesets,
pandas DataFrames, Spark DataFrames/Spark sessions, HTML renderables, and
notebook state in-process. A JSON-only candidate client cannot preserve those
interactions without a task-specific adapter. Trusted pytest direct-importing
candidate modules would violate the production verifier boundary in
`AGENTS.md`; no approved ydata-profiling adapter is available.

## Reopen conditions

Reopen only after all of the following are versioned and privately available:

1. An owner-approved manifest for the `conftest.py` overlay and line-ending/
   mode normalization, or an exact upstream test image;
2. a collection/node-id record proving the fixed denominator and skip policy;
3. an offline, hash-locked build/dependency artifact satisfying the declared
   build-system and runtime closure, plus an approved plan for every external
   dataset;
4. a task-specific candidate-client/RPC adapter preserving the direct object
   and Spark/notebook assertions, with verifier-owned JUnit/reward output;
5. later three-run Oracle and empty/stub/forgery/offline controls.

## Static validation performed

- Read `AGENTS.md` and `CONTRIBUTING.md`, the legacy four-file contract, and
  neighboring task audit conventions.
- Parsed and SHA-256 hashed all legacy artifacts; validated both JSON arrays.
- Read the conversion-loop record and verified the immutable registry manifest,
  config digest, and relevant layer digests by download/hash/list inspection.
- Cloned the upstream GitHub repository, resolved the full commit, reproduced
  the unprefixed `git archive` and MIT license hashes, and compared source,
  test, setup, and installed-package paths.
- Built static test inventories and AST counts; searched for network fixtures,
  skip/parametrize sites, candidate imports, collection caches, and result
  artifacts.

No Docker container/image was started. No pytest, Harbor, Oracle, or negative
control was run. No hidden test bytes were copied into this repository.
