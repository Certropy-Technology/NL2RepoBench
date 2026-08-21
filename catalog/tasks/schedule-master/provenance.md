# `schedule-master` Provenance

## Naming

The legacy benchmark task ID is `schedule-master` and is intentionally retained.
The Python distribution and import package implemented by the task are both named
`schedule`.

## Frozen Verifier

- Tagged source: `ghcr.io/multimodal-art-projection/nl2repobench/schedule-master:1.0`
- Immutable linux/amd64 manifest: `sha256:903e864b08437cacb1dbf4305f6ecc1443d09c6af7a714e2d81c4c5fee2d6677`
- Image creation timestamp: `2025-08-20T00:41:20.233994797Z`
- Runtime: Python 3.12.3 on Debian 12
- Relevant frozen packages: pytest 8.4.1 and pytz 2025.2
- Hidden path: `/workspace/test_schedule.py`
- Hidden bytes: 66,477 bytes, 1,592 lines
- Hidden SHA-256: `05bba4db69922fc2a9722451e668bb0bcc86d9a1b26550864abd7a631c46c66a`
- Hidden Git blob ID: `350ab5602d5f91b8044a9c78c738d7567ea6a520`
- Frozen effective collection: 81 tests, with no skipped cases in the pinned image

The verifier starts with `TZ=UTC`, `LANG=C.UTF-8`, and `LC_ALL=C.UTF-8`. The
frozen test module then selects an explicit POSIX Europe/Berlin timezone and
calls `time.tzset()`. Remote timezone behavior is supplied by the pytz version
inside the immutable verifier image, so host timezone and host tzdata do not
participate in grading.

## Source Revision

Upstream is `https://github.com/dbader/schedule`. The immutable source revision
is release 1.2.2 commit:

`82a43db1b938d8fdf60103bd41f329e06c8d3651`

The verifier image's `pyproject.toml` and `setup.py` exactly match Git blobs
`8f8ab03e8a264c41986524b616c7e5425d96407e` and
`3b340337d8ca8f43dfaf5d7560124eef54a6b75c` at that commit. The upstream test
blob is `f497826d1dca3c209ec55d205553ff4660268ab5`. The benchmark changed only its
import surface from the upstream explicit import list to a wildcard import;
the remainder of the test bytes is identical. This intentionally checks the
package's unified export surface without changing any behavioral assertion.

Reproduce the source archive digest with:

```bash
git -C /tmp/schedule archive --format=tar \
  82a43db1b938d8fdf60103bd41f329e06c8d3651 | sha256sum
```

Expected result:

`718fc6887ae9165aaf5f751780416ead8ce82844a2f615543f43acfaac7d4cff`

## License

`LICENSE.txt` at the pinned revision contains the standard MIT license and has
SHA-256 `30a8352c318ce1b645acde0299697342d4380ed2637d7ca18a8ad25661e3b41b`.
The same revision also declares `MIT License` in `pyproject.toml`, `MIT` in
`setup.py`, and the classifier `License :: OSI Approved :: MIT License`.
