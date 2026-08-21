# Records Provenance Audit

Status: `packaged`; Oracle and control runs are intentionally pending the parent
orchestrator. This task-local package contains the public specification and
Harbor scripts only. It does not contain hidden test bytes, a copied test
archive, or a generated run artifact.

## Legacy And Verifier Inputs

- Legacy task: `test_files/records/`.
- Legacy commands: `pip install -e .`; then
  `pytest --continue-on-collection-errors tests`.
- Legacy declared count: `31`.
- Verifier image:
  `ghcr.io/multimodal-art-projection/nl2repobench/records@sha256:03378b1619c4ddcfebb0f3941e8fd448fe2754cf9489f13594cb0b40551f5a2d`.
- Registry manifest media type: Docker distribution manifest v2.
- Registry manifest digest: the requested
  `sha256:03378b1619c4ddcfebb0f3941e8fd448fe2754cf9489f13594cb0b40551f5a2d`.
- Image architecture: `linux/amd64`.
- Image config digest:
  `sha256:9e4c40bd0b94778a49f7d6d2aa70e2fbeb354c0753e43651a45c5b4704ab2a46`.
- Image Python: `3.12.4`; pip: `24.0`; image build history runs
  `cd /records && pytest` after installing `requirements.txt`.

The image's `COPY ./records-master/tests /workspace/tests` layer is the source
of the private fixture. The Harbor `tests/Dockerfile` copies that directory
inside the verifier image at build time, so no hidden test file is present in
this Git tree.

The image layer contains these relevant installed distributions (metadata was
read from the OCI layer without starting the image):

```text
docopt==0.6.2
et_xmlfile==2.0.0
greenlet==3.2.4
iniconfig==2.1.0
openpyxl==3.1.5
packaging==25.0
pluggy==1.6.0
psycopg2-binary==2.9.10
Pygments==2.19.2
pytest==8.4.1
SQLAlchemy==2.0.43
tablib==3.8.0
typing_extensions==4.15.0
```

The image also carries pip `24.0`, setuptools `72.1.0`, and wheel `0.43.0`.
These versions are image evidence, not a substitute for the hash-locked
offline dependency bundle required by production publication.

## Frozen Test Evidence

The image's post-test pytest cache contains 31 node IDs. The cache file is
2411 bytes with SHA-256
`9065c5dab656ad7b296e93ce739a98bcb28843b405859f8d48d96c03ce526bcf`. The
frozen node list contains two parametrized issue tests, 23 `RecordCollection`
or `Record` tests, and six transaction/database tests. No skipped node is
listed; the fixed effective denominator is therefore `31`.

The six frozen files under `/workspace/tests` total 8663 bytes. Their image
SHA-256 values and upstream Git blob IDs are:

| Path | Bytes | Image SHA-256 | Upstream blob |
| --- | ---: | --- | --- |
| `tests/__init__.py` | 0 | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` | `e69de29bb2d1d6434b8b29ae775ad8c2e48c5391` |
| `tests/conftest.py` | 1252 | `ee39073d4f9fd5e91bf740bf227096abf0d8212a12f9c9000ae398ae4636c93c` | `086803092d54ef831751da2b3211e8d9482dcb0d` |
| `tests/test_105.py` | 144 | `84558af919e0ff2256adfb026cbda8399a86f58a9c1cce51dca074fde3364073` | `b9655b507468457a83859bc2121343a5ccbe975c` |
| `tests/test_69.py` | 143 | `58d9ba8a6b4358ece2e11b61bb70d8e14ffddbc08e2d1df1163d15ce7bc6396d` | `034bf266f057804a270e58bfa3f8d8d8e9f01953` |
| `tests/test_records.py` | 4699 | `adaf50f977a0d0a7574995e58d75dad3935b99e4e6f696f479bda7b90aae9587` | `6c6aca5a706975455ef67f87bd896eed7924ab8a` |
| `tests/test_transactions.py` | 2425 | `f830d4b33e36a27ed0930af28259f6f6064cd154489e64cea8fa47f7d8d2f759` | `c9255b33213fdad986f3d31ab9d3beffbc3b95d7` |

The ordered path/size/SHA manifest used for this audit has SHA-256
`c8ef3672fd7e4e9b18f011df2424cee108f244ff49e0376f6bd8d5a6122fb0d0`.

## Upstream Source Lock

- Upstream: `https://github.com/kennethreitz/records`.
- Revision: `72efce67874d1b40ac2a35542127e8830da49707`.
- Revision identity: release tag `v0.6.0`, commit date
  `2024-03-29T19:50:46-04:00`.
- Reproducible command:
  `git -C /tmp/records-upstream archive --format=tar 72efce67874d1b40ac2a35542127e8830da49707 | sha256sum`.
- Git archive SHA-256:
  `4e0a1b23d7d38f96182d2be29d915fa45165fddd8ec14f193acb5304a57b0e04`.
- Upstream `records.py` SHA-256:
  `e1813a36215156e8eb84ac5021880592d6f61a5382287d42a80ecb9cb1d5ad5e`.
- Upstream `requirements.txt` SHA-256:
  `af4f60028ddd03bc2ac02abb6c54d1880703b7a5b3478a1dbd4666bee8c03cc8`.

Each frozen test file and `tests/conftest.py` has the same bytes as the
corresponding path at this revision. The implementation blob is also identical
to the image copy. The v0.6.0 transaction context intentionally rolls back and
suppresses the test's raised exception; later upstream commits temporarily
changed that behavior, so the v0.6.0 pin is material to the frozen suite.

## License

The revision declares `ISC` in `setup.py`. Its `LICENSE` file is 767 bytes,
Git blob `9dfdf39d0b4c5d98c5ce1493a2780720793a3c7f`, and SHA-256
`f957a7a3c4d9293eb0659798d3648990a5c9e435acd258c9769c7f8296a26f28`.
The image copy has the same license bytes.

## Image Source Difference And Risk

The image's `/records/setup.py` is a build-time-normalized copy: it comments
out README-dependent `long_description` code because the `/records` copy does
not include `README.rst`, and it retains unbounded dependency names. Its
SHA-256 is
`17fb01695d5fed9d0542fbe50f4caee1f94bdcb220e527ab0f18bba4e5b05aa0`, rather
than the v0.6.0 upstream `setup.py` SHA-256
`226252e28d83d61f65384412e2c6661b6de9b3f7fb96306f8716ea2dc10e0f20`.
The image's `records.py`, `requirements.txt`, license, and all frozen tests
remain byte-identical to the source lock. This setup-only difference does not
change the tested API, but the parent Oracle gate should confirm that the
pinned upstream checkout installs and collects 31 tests before promotion.

## Recommendation

Keep lifecycle at `packaged` pending three independent parent Oracle runs with
`valid=true`, stable collection `31`, and reward at least `0.80`, followed by
empty/stub/forgery/offline controls. If the upstream v0.6.0 Oracle install or
collection differs from the image evidence, classify the task as an environment
or verifier blocker rather than changing the denominator or source pin.
