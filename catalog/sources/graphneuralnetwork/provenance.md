# graphneuralnetwork provenance

## Source lock

- upstream: `https://github.com/shenweichen/GraphNeuralNetwork`
- revision: `ff3ac3838287d28bee6f6ef0302584c4f4858528` (fetched pinned, never remote HEAD)
- license: MIT (`LICENSE` present at the pinned revision)
- `sha256(git archive --format=tar <revision>)` = `87ed47cd36eb0c977d89a44a9d7b08c12f2c0817362e92401f152c3ed1e71183`,
  matching the recorded `[source].source_digest`. Unchanged by this repair.
- submodules: none

## Environment re-base

The task previously pinned a legacy Python 3.10.11 image. The production verifier copies its
trusted runtime into a hardcoded `/usr/local/lib/python3.12/site-packages` path, so a 3.10 base
cannot start the verifier at all. Re-based under the standing pre-approval:

| field | before | after |
| --- | --- | --- |
| `base_image` | `ghcr.io/multimodal-art-projection/nl2repobench/graphneuralnetwork` | `python:3.12.14-slim-bookworm` |
| `base_image_digest` | `sha256:6388582535fd9c56af5a69eef057a136c3ec4ae54ae26156b6db843286d62152` | `sha256:356b0d18f9385f4bdcc673af60e1e64c9d1504952e4ec36ee32044c722a6bc4e` |
| `python_version` | `3.10.11` | `3.12.14` |
| `os_name` | `debian-bullseye` | `debian-12` |
| `[task] version` | `0.1.0` | `0.2.0` |

`instruction.md` was updated only where it stated the old interpreter version
(`Target Python 3.10.11` -> `Target Python 3.12.14`). No other instruction text changed.

### Frozen denominator survived the re-base

The frozen upstream suite was re-collected on the new base before any other change, using the
pinned dependency closure (`tensorflow-cpu==2.19.0`, `networkx==3.4.2`):

```
pip install --no-deps --no-build-isolation -e .
python -m pytest tests --continue-on-collection-errors -q
-> 1 failed, 3 passed   (4 collected)
```

4 collected equals `[tests].expected_total = 4`, so the denominator holds and no rescope was
needed. The single upstream failure is the known NetworkX drift: upstream
`tests/graphsage_test.py` calls `nx.from_scipy_sparse_matrix`, removed in NetworkX 3.x.

The frozen `gnn` package imports the legacy `tensorflow.python.keras.*` tree, so 3.12 viability
was verified directly rather than assumed: the `tensorflow_cpu-2.19.0-cp312` wheel still ships
154 `tensorflow/python/keras/*` members, and `from tensorflow.python.keras.optimizer_v1 import
Adam` plus all four `gnn` modules import cleanly on 3.12.14.

## Registered private artifacts

The public catalog carries digest references only. No wheels, hidden test bytes or source
archive are stored in the catalog tree.

| bundle | digest | size_bytes |
| --- | --- | --- |
| dependency lock | `sha256:a30e649e38343eebfe8322f4c75c14e36752e5d3a48bae529988273f0cfa4b1c` | 5118 |
| verifier | `sha256:993115d21018f68eaac97de122a3fe176ab3068b0842b065787109d986615f9b` | 30720 |
| oracle | `sha256:e0ca03295ab9bdb4d9dab1791b9aeddb9efce0c79c3d9a476c6830637b84e66e` | 34099200 |

- Dependency lock: `requirements.lock.txt` only, with every pin carrying `--hash=sha256:`.
  The compiler copies the lock into both Docker build contexts and installs the closure during
  image build; no wheelhouse or vendored dependency directory enters the generated task.
- Verifier bundle: `run.py` (entrypoint) and `adapter.py`, protocol `custom-json-v1`.
- Oracle bundle: `solve.sh` (mode 0755) and `source.tar` at the tar root.

## Oracle solution path

`solve.sh` is purely local: it verifies `/solution/source.tar` against the recorded source digest
and extracts it into `/workspace`. The earlier hand-written `git fetch` form was removed because
the agent phase is `no-network` and fetching would risk exposing the reference implementation.
Consequently an Oracle run needs no host authorization, and
`uv run nl2repo task lint-network` reports no findings for this task.

## Verifier

Protocol `custom-json-v1`, entrypoint `run.py`, four leaves matching the frozen denominator.

`run.py` is trusted and never imports candidate code. Each leaf runs `adapter.py` in a child
process via `runuser -u candidate -- env ... python -I -B`, and only an allowlisted case-name
token crosses the boundary; never Python source, import paths or shell fragments. Because
`python -I` ignores `PYTHONPATH`, the adapter explicitly inserts both `/tmp/candidate-site` and
`/opt/candidate-dependencies/site` on `sys.path`. Since the compiler installs `/tests/verifier`
as root-only (`COPY --chmod=0500`), trusted `run.py` stages the adapter bytes into a
candidate-owned scratch directory itself.

The slice is deterministic, offline and CPU-only: fixed seeds, a generated small Cora-format
fixture in a temporary directory, `TF_ENABLE_ONEDNN_OPTS=0` and `CUDA_VISIBLE_DEVICES=-1`.

| leaf id | covers |
| --- | --- |
| `data-pipeline-and-splits` | `load_data_v1`, adjacency symmetry, `preprocess_features` row-normalisation and finiteness, `preprocess_adj` symmetric and row modes, `get_splits` mask shapes/dtype/disjointness |
| `gcn-featureless-training` | `GCN` featureless construction, input arity, `num_class` output width, masked full-graph fit, finite loss, normalised predictions, `GraphConvolution` layer identity |
| `gat-multihead-attention-training` | `GAT` multi-head construction, masked full-graph fit, `GATLayer` concat and mean reduction, rejection of a non-positive head count |
| `graphsage-mean-aggregator-training` | `sample_neighs` limited and unlimited row/count contracts, `GraphSAGE` input arity, masked full-graph fit, `MeanAggregator` |

The NetworkX compatibility concern from the prior repair stays on the verifier side: the verifier
builds the graph itself and selects `from_scipy_sparse_array` when present, falling back to
`from_scipy_sparse_matrix`. Candidates are never required to reintroduce a removed NetworkX API.

## Evidence

Frozen denominator source: `frozen-collection`, 4 items, re-collected on the re-based image.

| check | result | artifact |
| --- | --- | --- |
| publication gaps | `[]` | `TaskManifest.publication_gaps()` |
| compile without `--allow-incomplete` | exit 0 | `uv run nl2repo harbor compile catalog/sources/graphneuralnetwork --toolchain toolchain.lock.toml --output /tmp/graphneuralnetwork-verify --artifact-root .nl2repo/artifacts --allow-private` |
| Oracle | `valid=true`, collected 4 == expected 4, passed 4, reward 1.0, 51s | `.nl2repo/runs/oracle/graphneuralnetwork-final/2026-08-24__18-42-30/graphneuralnetwork__x6YZhLs/verifier/grading.json` |
| stub control | `valid=true`, reward 0.0, passed 0/4 | `.nl2repo/runs/oracle/graphneuralnetwork-stub/2026-08-24__18-38-19/graphneuralnetwork-stub__vm9SHmc/verifier/grading.json` |
| forgery control | `valid=true`, reward 0.0, passed 0/4, forged reward files ignored | `.nl2repo/runs/oracle/graphneuralnetwork-forgery/2026-08-24__18-39-06/graphneuralnetwork-forgery__kJTqkm6/verifier/grading.json` |
| empty control | `valid=true`, reward 0.0, collected 0 | `.nl2repo/runs/oracle/graphneuralnetwork-empty/2026-08-24__18-40-07/graphneuralnetwork-empty__FJH9mb9/verifier/grading.json` |
| offline verifier | `public_network_available: false`, `pypi.org:443` and `1.1.1.1:443` unreachable in Oracle and all control receipts | receipt-specific `network.json` paths in `production-evidence.json` |
| network policy lint | 0 errors, 0 findings for this task | `uv run nl2repo task lint-network` |

## Decisions

1. Took the pre-approved base-image re-base after confirming the denominator survived.
2. Pinned `tensorflow-cpu==2.19.0` rather than `tensorflow==2.19.0`: the slice must be CPU-only
   and deterministic, and the CPU wheel avoids roughly a gigabyte of unused CUDA payload. Both
   still ship the legacy `tensorflow.python.keras` tree the frozen source requires.
3. Moved `networkx` from the stale `2.8.8` pin to `3.4.2`, the version resolvable and tested on
   3.12. This is why the verifier owns graph construction and selects the available SciPy
   constructor.
4. `candidate_total_timeout_sec = 1200`: the catalog schema requires install budget plus call
   budget plus a 60s reserve to stay under `verifier_timeout_sec = 1800`.
5. Set `agent_network_mode = "no-network"` in the catalog `[harbor]` profile so the compiled
   Harbor profile matches the declared `[environment.network_policy]`.
6. Removed the stale hand-written `harbor/{environment,solution,tests,task.toml,instruction.md}`
   scaffolding. Those files described the old 3.10 image and an obsolete pytest-based grader, and
   the compiler no longer consumes them for a production task; `harbor/controls/` is retained,
   matching the layout of the already-published tasks.

## Remaining gates

Blind review and spec traceability review are still pending, as is pilot execution. Lifecycle is
therefore `controls-passed`, not `published`.
