# Frozen Inventory

- Upstream: `https://github.com/python-trio/sniffio`
- Revision: `6996e05d9b9debe32f42f709c8041e744f850478`
- Git describe at the shallow frozen checkout: `6996e05`
- Distribution version in the frozen source: `1.3.1+dev`
- License: MIT OR Apache-2.0, with `LICENSE.MIT` and `LICENSE.APACHE2` present.
- `git archive --format=tar` digest: `sha256:1bcb3387980cdb5adac666e1edacabc2976807b9c053d1c4a3781b9f648cda68`.
- Archive size: 81,920 bytes.
- Implementation files: `sniffio/__init__.py`, `sniffio/_impl.py`, `sniffio/_version.py`, and `sniffio/py.typed`.
- No native extensions and no runtime third-party dependencies.
- Build backend: `setuptools.build_meta`; build requirements are `setuptools >= 64` and `setuptools_scm >= 6.4`, with `packaging` in the resolved closure.
- Upstream pytest collection on CPython 3.12: 4 leaves, 3 passed and 1 skipped because Curio is intentionally broken on Python 3.12 in the frozen upstream test.
- Production verifier collection: 21 deterministic JSON leaves, all executed in candidate-side child processes.

## Public API Inventory

| Import path | Shape | Contract |
| --- | --- | --- |
| `sniffio.current_async_library` | zero-argument function | Returns a runtime label or raises `AsyncLibraryNotFoundError`. |
| `sniffio.current_async_library_cvar` | `ContextVar` | Default `None`; explicit value overrides runtime sniffing. |
| `sniffio.thread_local` | `threading.local` instance | `name` defaults to `None`; its value overrides the ContextVar in the same thread. |
| `sniffio.AsyncLibraryNotFoundError` | exception class | Subclass of `RuntimeError`. |
| `sniffio.__version__` | string | Exactly `1.3.1+dev`. |
