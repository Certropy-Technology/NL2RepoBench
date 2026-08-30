# Public Contract Traceability

| Contract area | Frozen authority | Private verifier leaves |
| --- | --- | --- |
| Root exports and ordinary imports | `tzlocal/__init__.py` | `exports`, `from-imports` |
| Distribution identity and conditional dependency | `pyproject.toml` | `metadata-name-version`, `metadata-runtime-requires` |
| Typed marker and compatibility modules | `pyproject.toml`, `tzlocal/py.typed`, package modules | `marker-and-unix-modules`, `windows-mapping-module` |
| Public call shapes | public definitions in `tzlocal/unix.py`, `tzlocal/win32.py`, `tzlocal/utils.py` | `public-signatures` |
| Named `TZ` discovery | `tzlocal/utils.py`, upstream `test_env` | `env-name-harare`, `env-zone-harare`, `env-name-berlin`, `colon-env-name`, `colon-env-zone` |
| Absolute TZif path discovery | `tzlocal/utils.py`, upstream `test_env` | `absolute-zonefile-name`, `absolute-zonefile-zone` |
| Unsupported and missing zone failures | `tzlocal/utils.py`, upstream `test_env` | `invalid-posix-zone-error`, `unknown-zone-error` |
| Independent caches | `tzlocal/unix.py`, upstream `test_get_reload` | `zone-cache`, `name-cache`, `independent-caches` |
| Reload behavior | `tzlocal/unix.py`, upstream `test_get_reload` and `test_zoneinfo_compatibility` | `reload-zone`, `reload-name`, `reload-synchronizes`, `repeated-reload` |
| Standard `ZoneInfo` compatibility | upstream `test_zoneinfo_compatibility` | `zoneinfo-type`, `harare-fixed-offset`, `new-york-fixed-offset` |
| Offset assertion success and failures | `tzlocal/utils.py`, upstream `test_assert_tz_offset` | `assert-offset-match`, `assert-offset-error`, `assert-offset-warning` |
| Environment side effects | public lookup contract | `lookup-preserves-tz-env` |

The reverse mapping is complete: every one of the 30 unique verifier leaf IDs appears exactly once above. Each scenario executes through `nl2repobench.verification.candidate_runner` with `/tmp/candidate-site` added only inside a bounded UID-10001 child.
