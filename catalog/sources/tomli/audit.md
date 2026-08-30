# tomli authoring audit

The candidate is frozen at commit
`5a77b12a7a9f052ce5a20c335d2825658f6aea52`. The unprefixed Git archive and MIT
license bytes are digest-bound in `task.toml`. Source inspection found a pure
Python `src/tomli` package with Flit Core as its only build dependency and no
runtime dependency.

The source-only baseline was installed with `pip install .` under CPython
3.14.6 and passed 17 of 18 unittest methods; the one skipped test requires
Python 3.15. The hidden contract intentionally uses a separate JSON verifier
because the current Harbor production boundary cannot let trusted pytest
import candidate code directly. Its 32 leaves preserve the parser's
observable public behavior, including invalid syntax and error coordinates.

Candidate installation is performed with the build dependency from the private
hash lock during image build. Candidate and verifier execution are
no-network. The Oracle bundle is the only place that fetches upstream source,
and its script asserts both the exact commit and archive digest before
materializing `/workspace`.
