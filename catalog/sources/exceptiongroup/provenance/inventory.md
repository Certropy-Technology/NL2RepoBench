# Frozen Inventory

- Upstream: `https://github.com/agronholm/exceptiongroup`
- Revision: `0c6cfbf677f6b50df17311cfdad01e9ff17310aa`
- Git describe: `1.3.1-6-g0c6cfbf`
- Installed SCM version: `1.3.1.post6`
- License: MIT, with the bundled PSF license notice for adapted standard
  library code.
- Git archive: 30 regular files, 174,080 bytes,
  `sha256:70913d01619162478935e3cf3a56721e85375e4f535928aa59f1273e7572e3bd`.
- Runtime: CPython 3.7+, evaluated with CPython 3.12.

The source package has five implementation modules, a `py.typed` marker, and
no native code. Its sole conditional runtime dependency is
`typing-extensions >= 4.6.0; python_version < "3.13"`. The PEP 517 backend is
`flit_scm`; a source checkout requires the build backend to generate
`exceptiongroup/_version.py`.

The upstream pytest tree contains 103 collected leaves on CPython 3.12.11.
The frozen baseline using pytest 8.3.5 completed with 91 passed and 12 skipped;
skips are version-gated pre-3.11 traceback behavior and unavailable Ubuntu
Apport integration. The production verifier uses a deterministic 36-leaf
JSON-safe contract rather than importing candidate code in the trusted
process.
