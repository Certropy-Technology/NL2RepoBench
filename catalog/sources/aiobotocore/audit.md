# aiobotocore authoring audit

## Freeze

- Upstream: `https://github.com/aio-libs/aiobotocore`
- Revision: `c92e345814ad97e5ec0633dbd34be5d26ee90dd3`
- License: Apache-2.0, from upstream `LICENSE`
- Git tree: `2a48a871c93623ecd8711967530cf5e3e5526cc2`
- Raw `git archive --format=tar` SHA-256: `6118ac737ce18ff5e3ed0190e7cf8298a98ef2acd68e046f733050fe8934bc0d`
- Freeze command: `git fetch --depth=1 origin c92e345814ad97e5ec0633dbd34be5d26ee90dd3; git archive --format=tar c92e345814ad97e5ec0633dbd34be5d26ee90dd3 | sha256sum`
- Toolchain probe: CPython 3.12.11, uv 0.11.32, Linux amd64/glibc.

## Inventory and scope decision

The frozen tree contains 38 Python package modules (8,681 lines), 61 Python
test files (16,820 lines), and 572 named test functions. The upstream suite
also contains network, TLS, proxy, Docker, Moto, credential-process, metadata,
and live-service paths. Those paths are not deterministic in a no-network
model run and are not used as the denominator.

The production verifier is a separate custom-json-v1 subprocess adapter with
24 deterministic leaves. It covers package version and exports, async session
and region/model loading, configuration validation/merge, S3 and DynamoDB
metadata, paginator/waiter construction, async response/body behavior, and
ordered stubbed calls including typed errors. All expected values were probed
against the frozen source after installing its exact dependency closure.

## Dependency and build remediation

The upstream build backend is Hatchling with the fancy PyPI README plugin.
Both are pinned in the private hash lock together with the complete runtime
closure. The lock is installed only in the image build phase; candidate
installation uses `--no-build-isolation` against that preinstalled closure.
The Agent and separate Verifier are `no-network`. The Oracle solution alone
fetches the frozen revision and verifies the archive digest.

The task-local private artifacts are:

- dependency lock: `sha256:ed2c1e136e723c10b1d9b830411572588e795ac6faac6d8b897e69892c9796b2`, 65,273 bytes;
- verifier bundle: `sha256:0967f4078fd55cae526291a0b87d1ef124aa706d82ed8dc9ca230c7a8f1c8a01`, 20,480 bytes;
- Oracle bundle: `sha256:7d03e9131e394e80ddf9a1012a743569fb55b053fa45ffc32aa9b41ed74f6d2e`, 10,240 bytes.

No Harbor Agent Run was started from this lane.
