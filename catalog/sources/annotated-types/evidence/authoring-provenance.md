# annotated-types authoring provenance

All commands below were run from the detached worktree with source revision
`ceb950e81a79403c911990ce960ecc6f46733508`.

| Stage | Command | Exit | Evidence |
|---|---|---:|---|
| source freeze | `git archive --format=tar HEAD` twice, followed by `sha256sum` | 0 | `.nl2repo/authoring-work/python-author-wave2-20260828/annotated-types/source.tar` (`sha256:21dc75bcb85e3a2dac6cd1c4d7dfb871b0987d7d612d6b82d9eeb7812cc59a0c`, 71680 bytes) |
| upstream collection | `PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest --collect-only -q -p no:cacheprovider tests` | 0 | 256 collected |
| upstream tests | `PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest -q -p no:cacheprovider tests` | 0 | 256 passed |
| upstream build | `uv build --wheel --out-dir .../dist` | 0 | `annotated_types-0.8.0-py3-none-any.whl` |
| source validation | `uv run nl2repo task validate-source catalog/sources/annotated-types` | 0 | source digest emitted by validator |
| network lint | `uv run nl2repo task lint-network --tasks-root catalog/sources` | 0 | 0 errors; repository-wide warnings are unrelated existing task findings |
| production compile | `uv run nl2repo harbor compile catalog/sources/annotated-types --output .nl2repo/compiled --toolchain toolchain.lock.toml --artifact-root .nl2repo/artifacts --allow-private` | 0 | `.nl2repo/compiled/annotated-types/bundle.manifest.json` |
| Oracle | Harbor 0.21.0 `annotated-types-oracle-c4` | 0 | 60/60, reward 1.0 |
| empty control | Harbor 0.21.0 `annotated-types-empty-c4` | 0 | valid install exception, 0/0, reward 0.0 |
| stub control | Harbor 0.21.0 `annotated-types-stub-c4` | 0 | valid, 1/60, reward 0.016666666666666666 |
| forgery control | Harbor 0.21.0 `annotated-types-forgery-c4` | 0 | valid, 2/60, reward 0.03333333333333333; fake workspace report ignored |

The verifier bundle is private and content-addressed under
`artifact://private/sha256:97fe251adaa32dd55cac8c2afb6b7c6539c0a6a57651065d20576bda668561e3`.
The Oracle bundle is private and content-addressed under
`artifact://private/sha256:9b6e153d6245063f041cfc9a1bedd27778046f95c798e62ed259c723999055b8`.
