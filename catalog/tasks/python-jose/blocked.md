# `python-jose` Static Conversion Audit

**Status: blocked.** This directory intentionally contains only this audit record.
No Harbor task descriptor, generated `harbor/` tree, Oracle script, private test
artifact, dependency bundle, or hidden test bytes are checked in. The legacy
projection, dataset files, and conversion-loop state were not modified.

A digest-pinned verifier image exists and the likely upstream revision and
license can be identified. Publication is nevertheless blocked by the
unapproved image overlays, missing offline dependency closure, incomplete
frozen-denominator evidence, and the lack of a task-specific candidate
subprocess boundary for this in-process cryptographic test suite.

## Audit scope and static-only rule

This audit used repository files, detached upstream Git history, read-only OCI
registry manifest/config/layer downloads, archive and file hashes, and static
source/pytest-cache inspection. It did **not** start Docker or a container, run
Harbor, run Oracle, run pytest, install a candidate, or alter shared loop/dataset
state.

## Legacy contract

The four inputs under `test_files/python-jose/` were read without editing:

| Artifact | Bytes | SHA-256 | Parsed meaning |
| --- | ---: | --- | --- |
| `start.md` | 64,808 | `19f1e3ea7097a0aaca6ddab9933fceec4678b297b277a8f665fb5b736b68139d` | Public instruction |
| `test_case_count.txt` | 3 | `ad21a2b810af49a8b9241e10dfce3a016987441cc93aa72feae47dd017ddf0bb` | Declared effective denominator `458` |
| `test_commands.json` | 67 | `3bd822b96ae432d75e8a3d09a40c856f17f3164f200f1eb0fee6b684be49ace9` | `pip install -e .`; then `pytest --continue-on-collection-errors tests` |
| `test_files.json` | 9 | `af7f0b2bd342822f2fa8e6a9fda610570f911f30d3108379ea4184c0866727c3` | Protected path `tests` |

The legacy command and protected path are internally parseable, but they do not
prove a frozen source revision, image contents, dependency lock, or effective
collection denominator.

## Immutable verifier image

The conversion-loop record reports an available `linux/amd64` image:

```text
ghcr.io/multimodal-art-projection/nl2repobench/python-jose@sha256:f058417e9d37765bee5686e548fe6fb39aa486374fcaf79f8df88f71c168a776
```

The corresponding tagged reference is
`ghcr.io/multimodal-art-projection/nl2repobench/python-jose:1.0`.
A read-only Docker Distribution v2 manifest request returned the same manifest
digest. Static image metadata:

- config digest: `sha256:ccd9a569a37b5bcd8602a2c9d37c9176eb43172b9df80a03cd52bc7134d3176d`;
- config size: 12,275 bytes;
- platform: `linux/amd64`;
- image-created timestamp: `2025-08-28T07:39:07.057011343Z`;
- Python: `3.10.11`; pip: `23.0.1`; setuptools: `65.5.1`;
- working directory: `/workspace`; configured command: `bash`.

Relevant immutable layers and their history purposes are:

| Layer purpose | Compressed layer digest | Size |
| --- | --- | ---: |
| initial `/workspace/tests` copy | `sha256:812c9e6257e224af1f67d785fcb64df6e4a68bafc2787151ead7483db7b7886b` | 131,870 |
| `/workspace/setup.py` copy | `sha256:1884d2eb94a912a49c4b0372cfda491545d79ea6d9c51dea662d02e20fa1b969` | 190 |
| `/workspace/requirements.txt` copy | `sha256:f20e76f27d1c434809584de51a672bd356165188e443bfbd0404386ffd802fa2` | 180 |
| `/workspace/requirements-dev.txt` copy | `sha256:5a45b5c8f22585973797768d941062964bfdfb36e8783ff85462eb95afe29c5b` | 251 |
| `/workspace/requirements-rtd.txt` copy | `sha256:6a73d5a184a2ec3eae546fb080550644e2247e3264112c03b5d4b5ab92568594` | 147 |
| `/workspace/pyproject.toml` copy | `sha256:019fb6897330fd77a0fa0d19554d0f1be7104497bf7f24be8d4ff64c4c01dc18` | 412 |
| `/python-jose` source-tree copy | `sha256:5ffeb6d0ba71b807c8ee52f6e9ec7746f8ce98bf79d4aaa2dbdca7055b412d04` | 205,043 |
| editable install | `sha256:53a9f391429aacc2638d9d0875010997ab10dc41ebfcbf6502cd09730172fe78` | 5,042,015 |
| `requirements.txt` install | `sha256:27c7455e9ad25f4cb6f32d109fa30fe892324a6b69989443fcb06ca7812c7c92` | 5,033,354 |
| extra crypto/test install | `sha256:64adf6ad717061e9960a40dcb1c0dcf37900defcf41aa919a4c6b13ab748a772` | 17,985,417 |
| post-test pytest cache | `sha256:80e1cff683048813434ea7a697fe601969d9f40f6c7d0156a922a4f1b0478da0` | 206,448 |

The image history explicitly records these build commands:

```text
cd /python-jose && pip install -e . -i https://pypi.tuna.tsinghua.edu.cn/simple/
cd /python-jose && pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
cd /python-jose && pip install cryptography pytest pytest-cov flake8 -i https://pypi.tuna.tsinghua.edu.cn/simple/
cd /python-jose && pytest
```

The mirror URLs and mutable requirement resolution are evidence of how the
legacy image was built, not an offline Harbor dependency lock.

## Upstream source and license lock

The image implementation/source tree has a strong match to the public upstream
repository:

- repository: `https://github.com/mpdavis/python-jose`;
- full revision: `018b310ddb8b50dcfd09a0c152117835a21dd656`;
- tag: `3.5.0`;
- subject: `Prepare release 3.5.0 (#388)`;
- revision date: `2025-05-28T13:25:04-04:00`;
- upstream tree: `d657035ab4a6c5a426f215339b49e934f8eefbc0`;
- deterministic archive command: `git archive --format=tar 018b310ddb8b50dcfd09a0c152117835a21dd656`;
- archive SHA-256: `29c61d9b78824ef3934abe5d9ad9602a11ef5e6d80525a07001ca47d800a13b6`;
- SPDX license: `MIT`;
- upstream `LICENSE` blob: `8e99ab94ecf432c3654fed4fe65ef09b3ca72be9`;
- upstream/image `LICENSE` SHA-256: `a5e618eee6d496f77ad8ae70fea6edf148159558e2d228787d9076c900a2f926` (1,081 bytes).

Static comparison of the 66 non-bytecode files in `/python-jose` against that
revision found 48 exact upstream blobs and 18 differing paths. The source
implementation and license therefore have a plausible immutable provenance,
but the image is **not** an unmodified checkout of the upstream archive.

## Test, setup, and source overlays

The initial `/workspace/tests` layer and the `tests/` subtree in the source
layer are byte-identical. The protected test inventory contains 21 files,
140,399 bytes, and has this path/size/SHA-256 manifest digest:

```text
de1eccc2504523208131c9db613ced28302182890923caaf5fce0550b507a10b
```

The source-tree inventory (excluding `__pycache__`) contains 66 files,
296,389 bytes, with manifest digest:

```text
c8bc0c4a1816674db6cbe2219c5aeac32c9a427be370796e59626d258abccfa4
```

The 18 image-vs-upstream differences are listed below. `image_sha256` is the
file in the immutable image source layer; `upstream_blob` is the blob at the
locked 3.5.0 revision.

| Path | Image SHA-256 | Upstream blob |
| --- | --- | --- |
| `setup.cfg` | `ca9ac669eda29fb7164b13af382301bcc94c3e247e1352cf1f375d2d80fc2e58` | `e4e3d1922d5e1d2f638ed85f3ad1ab380f0b4d30` |
| `tests/algorithms/test_AES.py` | `1c96cda87dec4df5c1a0beb1c13d48b4649847ecb70c98182be2b18c3e238dab` | `9d06017ceef9b355e8e8943bc053e79eb9cdba7b` |
| `tests/algorithms/test_AES_compat.py` | `670a68dd519e16fb728700fe4072ed7d6293be01fe4d1e8ea02da899c2f94261` | `4f05bed5e0c9a74ec6bc1397cb2aac53e08d8dd3` |
| `tests/algorithms/test_EC.py` | `81d17ed8fd3245f4d71e388d81dc0639c7ec322e429416a352792f3beb420e93` | `d8602a2b1c20816b1089c78ee3433cea1d8b4732` |
| `tests/algorithms/test_EC_compat.py` | `744c4e87b286d50de91bd5259ffcad8135bfc0ddd4c84535d0e3d26fe035a029` | `1bb7373a7be5ff6fe0ea014e87f655e1e0f17e47` |
| `tests/algorithms/test_HMAC.py` | `3169c73c328c69af4a565429487d484424fe7f68277a2843b94f4b9e9a9095ca` | `2b0859ec469ad0a2c84aadcbac440296451d0fc9` |
| `tests/algorithms/test_HMAC_compat.py` | `83ce771b4811ed69febb7cf99bf39b1d4adb4165b3f9329c9a9c33ba384e96c6` | `f2fb899c82157c829f5d0a3859dbdb4884476599` |
| `tests/algorithms/test_RSA.py` | `ad0843512410587cb478b5abb2c85adb6b6aef8be53a053566b8adf23254fa68` | `b181993c8f1b0598db8b34d5f50e35e6c95412d3` |
| `tests/algorithms/test_RSA_compat.py` | `c6ffd6c000eb44e3568c455cf90e9dddab1662d6500d4ba9419a358cba5c75d2` | `02eb3f675f312da45826588e4e6a5c7b5dbd838d` |
| `tests/algorithms/test_base.py` | `8d5bae166818899ff594b4f9850e882439a877aaf157f70dc605e520c71d6a19` | `85c8a80848628fd810620c0268074768d7e61446` |
| `tests/rfc/test_rfc7520.py` | `8811808c33df0982727576f49bf723fa80489d2874945dcf0ce235a23a8f25db` | `9052f65c3cb97eefd643d8e311b7f163b63754b7` |
| `tests/test_backends.py` | `70ceee0cdb6205da5967619b5d746299428948489dbc161130574323bc6e9d0e` | `4ce71a7d12bdda84d8233900bf7dd10af3d91c6d` |
| `tests/test_firebase.py` | `6ec27a03a61379874787459fc5bc60e291586619f207cfd0215cc19392f82642` | `1096591c2d87c68b7d1a5175cfcfe267553db402` |
| `tests/test_jwe.py` | `c35f89cd9289e061c0f747d333e08f205213fe76bbe22f181d1b994974d38b21` | `6ab9971996e5734d639deb9583414a1c44b93264` |
| `tests/test_jwk.py` | `dc3402e77e4141d3e4c0a3e136d47b775a333176aa75e50bba10ec4dc1fee54f` | `e8009d64e678289f6e7940f1b270a04c927a5d07` |
| `tests/test_jws.py` | `c62b6d97587525443657af917e87e7dd5060855ed5a0888b8b5df050474ce5cc` | `1609b6b599ec1d7d36119a1011ec295d4b569b8d` |
| `tests/test_jwt.py` | `44acffe8b99d43088c65987990b236eedb32189510aaf5b5b98fae13381efe1d` | `f9d54cd1df03bf24be20a54af2bc0d1de43ddf20` |
| `tests/test_utils.py` | `161027eac85a46f32eb372bc46f035b2c16213f3fba9d4f229c239fc1943842f` | `2fbb08dcb3457b662b5c28c6fc548226692dc3ad` |

The stable SHA-256 of the normalized 18-file unified-diff audit is
`7e5398e1ee6e9df7b0aa5ef236f9a87a68fa3af82d04d49fb13decd573761a01`.
The observed overlay classes are:

- `setup.cfg`: comments out `long_description = file: README.rst`;
- algorithm/RFC tests: replace named imports with wildcard imports;
- `test_jwt.py`, `test_jwe.py`, `test_firebase.py`, and related files: move
  imports into test bodies and alter import surfaces;
- no immutable overlay manifest, owner approval, patch artifact, or source
  lock field for these changes is present in the conversion-loop record.

These differences are not a harmless archive projection: the test imports and
in-test import timing affect collection and candidate/verifier behavior. The
image test contract must be locked separately from the upstream source before
publication.

## Denominator audit

The legacy file declares an effective denominator of `458`. The immutable image
contains a post-build pytest cache from the recorded `cd /python-jose && pytest`
step. Its node-id cache is 47,052 bytes, SHA-256
`da1f3441ce82fecb793aa3eeb418411247b798ac1860240f3ca2bf1c47147c2e`, and lists
**470** collected node IDs:

| Test path | Cached node IDs |
| --- | ---: |
| `tests/algorithms/test_AES.py` | 6 |
| `tests/algorithms/test_AES_compat.py` | 9 |
| `tests/algorithms/test_EC.py` | 18 |
| `tests/algorithms/test_EC_compat.py` | 20 |
| `tests/algorithms/test_HMAC.py` | 3 |
| `tests/algorithms/test_HMAC_compat.py` | 12 |
| `tests/algorithms/test_RSA.py` | 21 |
| `tests/algorithms/test_RSA_compat.py` | 120 |
| `tests/algorithms/test_base.py` | 6 |
| `tests/rfc/test_rfc7520.py` | 3 |
| `tests/test_asn1.py` | 4 |
| `tests/test_backends.py` | 4 |
| `tests/test_firebase.py` | 3 |
| `tests/test_jwe.py` | 125 |
| `tests/test_jwk.py` | 10 |
| `tests/test_jws.py` | 43 |
| `tests/test_jwt.py` | 61 |
| `tests/test_utils.py` | 2 |
| **Total** | **470** |

The arithmetic difference is 12. Static inspection gives a plausible
explanation: `test_RSA_compat.py` skips the pure-RSA backend for the two OAEP
algorithms across the two RSA keys and the three backend pairings containing
that backend (12 runtime skips). However, the image retains no JUnit, skip
report, collection JSON, or build stdout. The cache proves collected node IDs,
not the effective `passed / (collected - skipped)` denominator. Therefore the
legacy `458` denominator is not independently frozen by an auditable
collection artifact. Do not silently replace it with `470` or infer the
12-case exclusion during publication.

## Dependency closure blocker

The checked-in image evidence is not a production offline dependency bundle.
The image's copied requirement files are:

```text
requirements.txt:
  pycryptodome
  rsa
  ecdsa != 0.15
  pyasn1

requirements-dev.txt:
  PyYAML==5.4.1
  cov-core==1.15.0
  coverage==7.8.2
  coveralls==4.0.1
  cryptography==45.0.3
  docopt==0.6.2
  pytest==8.3.5
  pytest-cov==6.1.1
  -r requirements.txt
```

Neither file pins hashes, and the image then installs additional packages
from a public mirror. Static metadata in the immutable layers shows, among
others, `python-jose==3.5.0`, `ecdsa==0.19.1`, `rsa==4.9.1`, `pyasn1==0.6.1`,
`pycryptodome==3.23.0`, `cryptography==45.0.6`, `pytest==8.4.1`,
`pytest-cov==6.2.1`, `flake8==7.3.0`, `cffi==1.17.1`, `pycparser==2.22`,
`packaging==25.0`, `pluggy==1.6.0`, `typing_extensions==4.14.1`, `tomli==2.2.1`,
`coverage==7.10.3`, and their transitive packages. These installed versions
are useful image observations but are not a content-addressed wheelhouse.

No dependency artifact, `requirements.lock.txt` with hashes, wheelhouse, build
transcript, or conversion-loop dependency reference exists for this task.
A Harbor verifier with `network_mode = "no-network"` cannot reproduce the
legacy editable install from the available evidence. This alone blocks a
production image-backed bundle.

## Candidate/verifier boundary blocker

The protected suite is not a subprocess-safe black-box contract. Static source
inspection shows direct in-process imports and stateful operations throughout
the suite, including:

- direct imports of `jose`, `jose.jwt`, `jose.jws`, `jose.jwe`, `jose.jwk`, and
  backend classes;
- direct construction and cross-comparison of RSA, EC, AES, HMAC, and native
  backend key objects;
- monkeypatching candidate internals such as `jose.constants.JWE_SIZE_LIMIT`
  and backend random-byte providers;
- direct exception, serialization, PEM/JWK, and object identity assertions;
- pytest fixtures and parametrized tests that pass candidate classes/functions
  as live Python objects.

The repository's production verifier contract requires trusted tests to call a
candidate subprocess/API boundary and explicitly says that real tasks without
a task adapter must remain blocked; trusted pytest must not directly import the
candidate. No python-jose RPC/CLI adapter or candidate-client test rewrite is
present. A path-prepend `.pth` or direct pytest invocation would put the
candidate and trusted test/report process in the same interpreter and would
not satisfy the separate-verifier boundary.

## Other publication gates

No Harbor Oracle run, three-run Oracle stability record, empty control, stub
control, forgery control, or offline verifier proof exists for this task. Those
runs are intentionally outside this static-only lane and must not be inferred
from the legacy image's historical `pytest` build layer.

The public instruction is also a generated, implementation-heavy prompt rather
than a reviewed task-specific contract. In particular, it names a `jose/init.py`
path while the upstream package uses `jose/__init__.py`, and it describes
backend/re-export surfaces that are changed by the image's wildcard/deferred
imports. This should receive a separate specification/traceability review if
the provenance blockers are resolved.

## Decision and unblock requirements

Keep `python-jose` **blocked**. Do not create `task.toml`, `instruction.md`,
`harbor/`, or any private test artifact in this lane.

To reopen, provide all of the following as versioned evidence:

1. An explicit source lock for `018b310ddb8b50dcfd09a0c152117835a21dd656`
   plus the MIT license/archive digest above, and an approved immutable overlay
   manifest for the 18 image-only files (or rebuild the verifier from exact
   upstream tests without changing the legacy contract).
2. A frozen collection/JUnit/skip manifest proving `458` effective cases and
   preserving the exact 12-case skip semantics, or a reviewed versioned metric
   change with a new task identity.
3. A complete hash-locked offline candidate/verifier dependency bundle,
   including all crypto backends and build tools required by the editable
   installation.
4. A reviewed python-jose candidate adapter that keeps hidden tests, trusted
   pytest, and grading reports outside the candidate process while preserving
   the upstream assertions.
5. Three independent valid Harbor Oracle runs followed by empty/stub/forgery/
offline controls in a later execution lane.

## Static validation commands

The following commands were used (all are static; none starts Docker, Harbor,
Oracle, pytest, or a candidate):

```text
git ls-remote https://github.com/mpdavis/python-jose.git ...
git clone --filter=blob:none https://github.com/mpdavis/python-jose.git /tmp/python-jose-upstream
git archive --format=tar 018b310ddb8b50dcfd09a0c152117835a21dd656 | sha256sum
curl -sS ... ghcr.io/v2/.../python-jose/manifests/sha256:f058417e...
curl -sS ... ghcr.io/v2/.../python-jose/blobs/sha256:...
tar -tzf /tmp/python-jose-registry/layer-*.tar.gz
tar -xzf /tmp/python-jose-registry/layer-*.tar.gz -C /tmp/python-jose-image-audit
sha256sum ...
python3 - <<'PY'  # source/blob, inventory, and pytest-cache inspection only
...
PY
```
