# Frozen Inventory

- Upstream: `https://github.com/regebro/tzlocal`
- Revision: `6ef2c295f36c6053b13dc77e59e629d943e3ac91`
- Commit date: `2026-06-29T18:09:05+02:00`
- Distribution version: `5.4.5.dev0`
- License: MIT; `LICENSE.txt` SHA-256 `d99ab209aeb16aad2c25c90ffd83c1a981e290ffff76a420a2ab03e03f041b8c`.
- Raw `git archive --format=tar` SHA-256: `c1466d3636fa00320760c2e5ae8f287c10f978a80b529690b6afb4bcdbebe935` (163,840 bytes).
- Build backend: `setuptools.build_meta`, requiring `setuptools >= 64`.
- Runtime dependencies: none on Linux; `tzdata` only when `platform_system == "Windows"`.
- Supported Python: 3.10 through 3.14 in the frozen metadata; the task runtime is CPython 3.12.11.
- Upstream collection with pytest 8.4.2 and pytest-mock 3.15.1: 20 leaves.
- Upstream baseline with the host timezone configuration: 20 passed in 0.21 seconds.
- A forced `TZ=UTC` baseline is intentionally not canonical: the upstream session fixture removes `TZ` while the host `/etc/localtime` remains Asia/Shanghai, producing one legitimate offset mismatch and 19 passes.
- Production verifier collection: 30 deterministic JSON leaves, all run in UID-10001 candidate children.

## Public API Inventory

| Import path | Frozen signature | Observable contract |
| --- | --- | --- |
| `tzlocal.get_localzone` | `() -> zoneinfo.ZoneInfo` | Return and cache the configured local zone object. |
| `tzlocal.get_localzone_name` | `() -> str` | Return and cache an identifiable IANA zone name. |
| `tzlocal.reload_localzone` | `() -> zoneinfo.ZoneInfo` | Refresh both caches and return the new local zone. |
| `tzlocal.assert_tz_offset` | `(tz, error=True)` | Return `None` for a matching offset; otherwise raise `ValueError` or emit `UserWarning`. |

The root `__all__` contains those four names in that order. `tzlocal.unix`, `tzlocal.utils`, `tzlocal.win32`, and `tzlocal.windows_tz` are compatibility modules; they are not imported by the trusted verifier process.

## Risk Inventory

- Filesystem and platform discovery are bounded by testing through public `TZ` behavior in isolated child processes.
- Current-time offset comparison is made deterministic with `TZ`, `time.tzset()`, and fixed known zones.
- `ZoneInfo` objects are converted to strings, keys, types, and fixed-date offsets inside the candidate child before JSON serialization.
- The trusted verifier never places `/tmp/candidate-site` on its own `sys.path` and never imports candidate modules.
- The model Agent receives no source host or package index authorization. The trusted Oracle alone fetches the exact source revision and checks the raw archive digest.
