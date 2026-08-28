# exceptiongroup Authoring Audit

The frozen upstream revision is `0c6cfbf677f6b50df17311cfdad01e9ff17310aa`,
with MIT licensing and source archive digest
`sha256:70913d01619162478935e3cf3a56721e85375e4f535928aa59f1273e7572e3bd`.
The archive has 30 regular files and is described by Git as
`1.3.1-6-g0c6cfbf`; the installed distribution version is `1.3.1.post6`.

The source-only baseline was installed through the Flit-SCM build backend with
the 1,330-byte hash-locked private dependency closure. CPython 3.12.11 and
pytest 8.3.5 collected 103 upstream tests and completed 91 passed / 12
skipped. The production contract freezes 34 deterministic JSON verifier leaves
covering the root API, exception-group construction and recursive operations,
`catch`, group-aware `suppress`, formatting, metadata, and packaging marker.

The trusted verifier never imports candidate code. Each leaf launches the
candidate through the repository's UID-10001 child boundary with bounded CPU,
address space, output, file descriptor, and cumulative wall-time limits. The
candidate dependency lock, verifier bundle, and Oracle solve bundle are private
content-addressed artifacts. Agent and verifier execution use `no-network`;
only the Oracle receives run-scoped `github.com` authorization.

Final production compile and Harbor 0.21 Oracle passed with 34/34 and reward
1.0. Final stub and forgery controls collected all 34 leaves and scored 14/34
and 15/34 respectively. Install and call hang controls completed with reward
0.0. Empty workspace produced the documented candidate-installation-failed
0/34 exception. A final direct `--network none` replay of the Oracle workspace
passed 34/34 with `public_network_available=false`.
