# WsgiDAV Static Conversion Audit

Status: **blocked**. This is a task-local audit record only. It contains no
Harbor task descriptor, public instruction copy, Oracle solution, verifier
scripts, dependency bundle, copied upstream source, or hidden test bytes.
Only this file was added under `catalog/tasks/wsgidav/`; legacy files, dataset
files, shared scripts, and conversion-loop state were not modified.

## Legacy Contract

The four legacy inputs under `test_files/wsgidav/` were read without editing:

| Artifact | Bytes | SHA-256 | Parsed value |
| --- | ---: | --- | --- |
| `start.md` | 175,430 | `778692d89ee74e999a4dc2c279018a09329b8de0c7232afb9ee617b09058b57c` | Public repository-generation instruction |
| `test_case_count.txt` | 2 | `76a50887d8f1c2e9301755428990ad81479ee21c25b43215cf524541e0503269` | Declared effective denominator `36` |
| `test_commands.json` | 67 | `3bd822b96ae432d75e8a3d09a40c856f17f3164f200f1eb0fee6b684be49ace9` | `pip install -e .`; `pytest --continue-on-collection-errors tests` |
| `test_files.json` | 9 | `af7f0b2bd3428222f2fa8e6a9fda610570f911f30d3108379ea4184c0866727c3` | Protected path `tests` |

The JSON manifests parse as arrays. The legacy command does not disable
pytest plugins or provide a candidate subprocess/API adapter.

## Immutable Verifier Image

The isolated worktree has no `.nl2repo/conversion-loop/state.json`. Read-only
inspection of the canonical external conversion-loop records at
`/data/NL2RepoBench-current/.nl2repo/conversion-loop/state.json` and
`/root/NL2RepoBench/.nl2repo/conversion-loop/state.json` agrees on the image
identity:

```text
ghcr.io/multimodal-art-projection/nl2repobench/wsgidav@sha256:3ef3a0a7dcd179b1d500493b560e9dfb98f4b3fad4c1f37c889f51160496cf29
```

The requested tag is
`ghcr.io/multimodal-art-projection/nl2repobench/wsgidav:1.0`. The state
records platform `linux/amd64` and status `available`; the worktree state was
not created or changed. A registry manifest-only request returned the same
raw SHA-256 and `Docker-Content-Digest`:

- manifest media type: `application/vnd.docker.distribution.manifest.v2+json`;
- config digest: `sha256:d351a879fc299b732e0ad85dfc8312abc88d19efa29f00a01633b5198de09dbe`;
- manifest digest: `sha256:3ef3a0a7dcd179b1d500493b560e9dfb98f4b3fad4c1f37c889f51160496cf29`;
- layer count: `19`;
- image-created timestamp: `2025-10-27T03:58:49.5484256Z`;
- runtime: CPython `3.11.4`, pip `23.1.2`, setuptools `65.5.1`;
- working directory: `/workspace`; command: `tail -f /dev/null`.

Relevant immutable layer evidence, downloaded and extracted only under
`/tmp/wsgidav-audit/`, is:

| Image operation | Compressed layer digest | Bytes |
| --- | --- | ---: |
| Copy protected `tests/` to `/workspace/tests` | `sha256:5c2ccbe464a817dfe299adaebe271feaf8c982f52723525c9b3850ffa2c8f9ef` | 35,129 |
| Copy `setup.py` to `/workspace` | `sha256:ec5f0ab7848d8c8c59ebbc4b1f7445596cda781ad44fa598ba4567a5f787d301` | 255 |
| Copy `setup.cfg` to `/workspace` | `sha256:e99a9c48bf8650363c21aac2a47779dabc26d60720239bd77a1a2d2a3d87c135` | 1,326 |
| Copy source checkout to `/project` | `sha256:44099b6f5341277906218e6090b238cc19390ac31c2a0862b73ad9a8d4432591` | 12,237,599 |
| Install source package | `sha256:43b143b18010863ea3ff33a474abb03b4f6821901c186a02c8c5bdb59b514eb5` | 8,770,534 |
| Install test/runtime packages | `sha256:0e5fe3158a5d1d3ba69545a9495692fadb1a9e622b8c7180befa913b189536c0` | 9,673,943 |
| Historical `pytest /workspace/tests` step | `sha256:288158ec787b0dcd9813a9e7652a3a68506c27af11db4b9d216750f906de18e1` | 469,709 |

The image history shows the exact setup sequence:

```text
COPY ./wsgidav/tests /workspace/tests
COPY ./wsgidav/setup.py /workspace/
COPY ./wsgidav/setup.cfg /workspace/
COPY ./wsgidav/ /project/
pip install /project
pip install pytest WebTest Cheroot requests
pytest /workspace/tests
pip uninstall -y WsgiDAV
rm -rf /project
```

This is image-history evidence, not a Harbor collection result or Oracle
run. No Docker command, container, Harbor job, or pytest process was run.

## Upstream Source Lock And License

The retained `/project/.git` metadata identifies the exact GitHub source:

- repository: `https://github.com/mar10/wsgidav`;
- full revision: `f12b2ec970e53e5127cb8b4fcb8d153457cd4d4f`;
- tree: `6498d812feaf55e115a168b1c437f2da780c207a`;
- parent: `991a23f5f5f3f46232eacd96666e23c1b5e110b5`;
- subject: `enable uid/gid switching upon user login (#344)`;
- author date: `2025-07-11T02:56:19+08:00`;
- committer date: `2025-07-10T20:56:19+02:00`.

The deterministic archive command was run twice:

```text
git archive --format=tar f12b2ec970e53e5127cb8b4fcb8d153457cd4d4f
size: 3,389,440 bytes
sha256: fba9450b8d187adaef70eed7d32a69a7a3de5e6d5beea190ab3f825a062811c9
```

Both archive runs produced the same digest. `LICENSE` at this revision is
MIT:

- Git blob: `321f8c6344fe9ceceb1a57de1a4a1e33154279f6`;
- bytes: `1,145`;
- SHA-256: `a7989e6c15aa8e9aa23630253376e4284409a6e4d9ec7f018459bf33774177cf`.

Source URL, full SHA, archive, and license provenance are therefore
identifiable and redistributable. They do not make the image's modified test
tree an unmodified upstream test bundle.

## Test, Setup, And Source Overlay Audit

The source commit contains 193 tracked paths. Comparing the image checkout
against that full revision after normalizing CRLF checkout noise found:

- 54 raw-byte exact paths;
- 136 paths differing only by CRLF versus LF;
- 1 behavioral content overlay;
- 2 tracked files missing from the image checkout.

The image copy also changes file modes: 191 of 193 tracked source paths are
`0755` in the image working tree although the upstream Git tree records them
mostly as `0644`. All 33 image test files are `0755`. These mode and line
ending changes are image build/check-out transformations, not upstream
content provenance.

### Setup files

`setup.py` and `setup.cfg` are content-identical to the pinned upstream files
after CRLF normalization. Their raw image/source-checkout versus upstream
hashes are:

| Path | Image bytes/SHA-256 | Upstream bytes/SHA-256 | Upstream Git blob |
| --- | --- | --- | --- |
| `setup.py` | 144 / `79ea941aceba35317c7ac056fa30e8246e84978e486a9dddf73befedcd25eb78` | 137 / `32f6afa5d3d67c31e4e043630a9f84fce01b74ae2e654bf30b2694fdae19a737` | `c0b4ce41760ecde3600aa6bbd263967478b5fdd4` |
| `setup.cfg` | 2,927 / `95e4b69fdd99cc22885483ef77334082dd21bd4fa9ef09ba21cb244bbbc50ed1` | 2,823 / `d5d8334a4ad79b1f3b6c7cac56dd90c55d8f6473e6bfa440f79f6f70b09a53d5` | `f740290348f27e3f2e64f560a94a79cec234aa31` |

No functional setup overlay was found. The image package metadata resolves
to `WsgiDAV==4.3.4a1` and declares the unpinned runtime requirements
`defusedxml`, `Jinja2`, `json5`, and `PyYAML`.

### Protected test tree

The image contains 33 regular test/fixture files totaling 157,001 bytes. A
path/size/SHA-256 manifest rooted at `tests/` has SHA-256
`8ac35681702ff278afae48c139e897bdc3f8c435bd2f7782b4b24639ed27e305`.
The bytes remain in the immutable image; no test or fixture bytes are copied
into this repository.

The following two upstream files are missing from the image test tree. Each
is 58,866 bytes at the pinned source revision, with upstream SHA-256
`487d510fe61400a3c3ded7ebce703ed8a3d4682aef07ffa934b81a368d277091` and Git
blob `7ded721dfdcf9d38d8461aff5c2652849273bfca`:

```text
tests/fixtures/share/Lotosblütenstengel (蓮花莖).docx
tests/fixtures/share/subfolder/Lotosblütenstengel (蓮花莖).docx
```

The image `tests/test_wsgidav_app.py` is a behavioral overlay. It adds:

```python
@pytest.mark.skip(reason="File with special chars was removed to fix build")
```

to `ServerTest.testDirBrowser`, which asserts the missing Unicode fixture.
The image file is 9,236 bytes, SHA-256
`ac752e95878406b2efd13ad60dd95a274280f3f900634c9419dbbef8c0ee450b` (LF
normalized SHA-256 `d59108bff87cdda92fcec7da7100545b57c9abec189a413b54df924f8902ab69`).
The upstream file is 8,903 bytes, SHA-256
`f86e26c91215287196b9a6b18cf6a00d70eae2f88cde1f3641f1152007e00b3e`, Git blob
`eb5ccd15feb40f7b54bca537f31a472bdfef73f4`. The image overlay's raw Git blob
is `112ca9dc5cbd958678e8b9c364e13f8f0b4e425d`; its LF-normalized Git blob is
`a133e7d961d436f3cf3ce5103897a13f58a4a1fe`.

All other authored test paths compare exactly after line-ending
normalization. The overlay is functional: it removes coverage of directory
listing and replaces it with a skip. No owner-approved immutable overlay
manifest states its source, license, or behavioral intent.

## Denominator Audit

The image pytest cache contains 45 node IDs:

```text
/workspace/.pytest_cache/v/cache/nodeids: 45 entries
```

The declared effective denominator `36` is numerically explainable by the
frozen image environment:

| Group | Nodes | Static/environment reason |
| --- | ---: | --- |
| All cached nodes | 45 | Image cache inventory |
| `RedisTest` | -5 | `redis` is not installed; `LockStorageRedis` import is unavailable and each setup skips |
| `WsgiDAVLitmusTest` | -3 | Image history installs no `litmus` executable; each `OSError` path skips |
| `testDirBrowser` | -1 | Explicit image-only skip for the removed Unicode fixture |
| Effective denominator | **36** | `45 - 5 - 3 - 1` |

This is static/cache evidence only. No final-image collection or JUnit record
was generated in this lane, so `36` must not be promoted to a frozen
collection gate or Oracle result yet. The count itself is not the blocker;
the undocumented behavioral overlay that makes the count work is.

## Dependency Closure

The immutable image records these installed distributions after the source
and test install steps:

```text
defusedxml==0.7.1       Jinja2==3.1.6          json5==0.12.1
MarkupSafe==3.0.3       PyYAML==6.0.3           pytest==8.4.2
WebTest==3.0.7          WebOb==1.8.9            Cheroot==11.0.0
requests==2.32.5        beautifulsoup4==4.14.2  waitress==3.0.2
certifi==2025.10.5      charset-normalizer==3.4.4
idna==3.11              iniconfig==2.3.0        jaraco.functools==4.3.0
more-itertools==10.8.0  packaging==25.0         pluggy==1.6.0
Pygments==2.19.2        soupsieve==2.8          typing_extensions==4.15.0
urllib3==2.5.0
```

The image digest freezes these installed bytes, but the source requirements
and historical `pip install` commands are not hash-locked and no standalone
offline wheelhouse, dependency manifest, or candidate build plan is recorded
for this task. Replaying the legacy `pip install -e .` inside a no-network
verifier would allow candidate-selected build requirements and dependency
resolution. Replacing it with a no-dependency path or a preinstalled-path
hack would change the legacy setup contract. A complete Harbor conversion
therefore needs an approved offline install plan in addition to the image
digest.

The public instruction names exact examples including `PyYAML==6.0.2`, while
the image contains `PyYAML==6.0.3` and upstream `setup.cfg` declares an
unpinned requirement. This is an additional specification/dependency drift
that needs owner review for a publishable version.

## Candidate Boundary

The private tests directly import and exercise candidate objects in the
trusted pytest process. Examples include:

- `tests/test_lock_manager.py`: `LockManager`, `LockStorageDict`, shelve
  state, and optional Redis storage;
- `tests/test_property_manager.py`: stateful property-manager instances;
- `tests/test_wsgidav_app.py`: `WsgiDAVApp`, `FilesystemProvider`, and
