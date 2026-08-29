# Public Contract Traceability

| Contract area | Frozen authority | Private verifier coverage |
| --- | --- | --- |
| Root exports and distribution version | `sniffio/__init__.py`, `sniffio/_version.py`, `pyproject.toml` | `exports`, `version`, `marker-and-submodules` |
| Exception type and outside-context behavior | `sniffio/_impl.py`, upstream `test_basics_cvar` and `test_basics_tlocal` | `error-type`, `outside-context`, `after-asyncio` |
| ContextVar default, override, reset, and context isolation | `sniffio/_impl.py`, upstream `test_basics_cvar` | `cvar-default`, `cvar-override`, `cvar-reset`, `cvar-context-isolation` |
| Thread-local default, override, priority, and thread isolation | `sniffio/_impl.py`, upstream `test_basics_tlocal` | `thread-default`, `thread-override`, `thread-priority`, `thread-isolation` |
| Active asyncio detection and repeated lookup | `sniffio/_impl.py`, upstream `test_asyncio` | `asyncio-detection`, `asyncio-repeat`, `asyncio-nested-task` |
| No false positive when no task is running | `sniffio/_impl.py` | `imported-asyncio-outside-task` |
| Conditional Curio probe and import safety | `sniffio/_impl.py` | `no-runtime-import-side-effect`, `compatibility-imports` |

The reverse mapping is exact: the 21 verifier leaf IDs appear in the private custom verifier and each maps to one row above. The trusted verifier never imports candidate code; it sends bounded JSON scenarios to `nl2repobench.verification.candidate_runner` in UID-10001 child processes.
