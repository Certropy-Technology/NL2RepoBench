# idna authoring audit

- Frozen upstream: `https://github.com/kjd/idna`
- Revision: `e2073db14d28d1c3299649dd0c2dd4205b43ebfd`
- License: BSD-3-Clause (`LICENSE.md`)
- Source archive digest: `sha256:9f05c7eabad5785cddefcb84a85230194b42dccb20b349027135854db25161f8` for `git archive --format=tar --prefix=idna/ HEAD`
- Upstream baseline: `6444 passed, 1 skipped, 56 subtests passed` under CPython 3.12 and pytest 9.1.1 with the upstream test root and no repository pytest configuration.
- Public implementation modules: `__init__`, `core`, `codec`, `compat`, `cli`, `intranges`, `idnadata`, `uts46data`, `package_data`, and `__main__`.
- Production verifier denominator: 25 fixed JSON leaves covering library, errors, codec, compatibility, packaging metadata, and CLI contracts through the separate candidate subprocess boundary.
- Excluded from scoring: upstream fuzz/property expansion and repository-only tooling; their behavior is represented by bounded deterministic examples rather than trusted imports of candidate code.
