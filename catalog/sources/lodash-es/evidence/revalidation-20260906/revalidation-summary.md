# lodash-es instruction revalidation (2026-09-06)

The queue-provided source digest was validated before mutation as
`sha256:e10e1a64fa89df5cfbac312832c5ff41719f1c69b03aa5c966af6fe172c2e885`.
All four declared private artifacts were found in the parent-local CAS and
verified by exact size and SHA-256. The source-local empty control was added so
the current Node control registry could prepare the required empty bundle.

Three production compiles using `toolchain.node.lock.toml`, the parent CAS, and
`--allow-private` completed successfully. The two byte-comparison compiles are
identical; the current raw bundle manifest digest is
`sha256:2a794080deef8720e47f0d2e760b3a2417a9da959155cbd8c4315dc6e28ba61b`,
with canonical manifest digest
`sha256:09fbd50d058449318e562c92ed54d80ba1ede5aa5dcac60345cbd02593af1930`.

Fresh Harbor 0.21.0 no-network runs against that bundle produced:

- Oracle: valid, 30 collected, 28 passed, 2 failed, reward `28/30`;
- empty: valid `0/0`, `candidate-installation-failed`;
- stub: valid `0/30`;
- forgery: valid `0/30`, verifier-owned reward preserved;
- bounded hang: valid `0/0`, `candidate-call-failed`;
- direct verifier replay with Docker `--network none`: 30 collected, 28
  passed, reward `28/30`.

The two Oracle failures are retained in `oracle-failure-set.json`. They are
`root-export-aliases-and-conversions` and `repeatable-pure-results`; the
current candidate runner does not expose dotted default-object paths and its
response contract does not return request arguments. This is a verifier/test
contract limitation inherited by the migrated task, not a source or network
failure. Every fresh verifier network receipt reports
`public_network_available: false`.

The source remains `controls-passed`: the Oracle is valid and above the 0.80
production threshold, while the two known verifier-contract ceiling failures
are explicitly preserved. Review, pilot, projection, publication, and commit
remain parent/integrator stages.
