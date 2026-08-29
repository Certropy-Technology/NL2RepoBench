# Authoring Probes

The candidate source was downloaded from the immutable GitHub commit and
extracted into the task-local authoring work directory. `pyproject.toml` was
parsed and confirms `setuptools.build_meta`, Python `>=3.12,!=3.14.1`,
`license = "BSD-3-Clause"`, and an empty runtime dependency list.

The source-only collection probe used the frozen tree's `networkx/tests`,
`networkx/classes/tests`, and the changed connectivity cuts suite. It collected
1,584 parametrized nodes under the local Python 3.12 environment; optional
NumPy tests were skipped because NumPy is deliberately outside the zero-runtime
dependency contract. The production verifier instead uses 37 deterministic
JSON cases and does not import candidate code in its trusted process.

The local adapter smoke copied the reference package into `/tmp/candidate-site`
and returned 37/37 expected results. The first probe exposed four adapter
expectation defects (edge tuple sorting, SCC iteration order, missing-node
exception class, and an absent graph node); those expectations were corrected
and the rerun returned 37/37.

The first Harbor call-hang control exposed a verifier budget defect: a 12-second
per-child timeout could exceed the 240-second cumulative candidate-call budget
across 37 leaves and produced `valid=false` with
`verifier-internal-error`. The task-local verifier was changed to a bounded
4-second child timeout, rebuilt as private bundle
`sha256:a8eeab7e95d71ff75d05b913898df70a886fe348ca663bb5a81ec16e123b8678`,
and the final call-hang rerun completed `valid=true`, 37 collected, 0 passed.
