"""Untrusted-side adapter for the GraphNeuralNetwork hidden slice.

This module is launched by ``run.py`` in a child process as the ``candidate``
user with ``python -I``. It imports the candidate package, exercises exactly one
allowlisted case, and writes a small JSON verdict file. Nothing is imported
from the candidate inside the trusted parent process.

``python -I`` ignores ``PYTHONPATH``, so both the installed candidate site and
the preinstalled runtime dependency site are inserted explicitly below.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
import traceback
from pathlib import Path

CANDIDATE_SITE = os.environ.get("NL2REPO_CANDIDATE_SITE", "/tmp/candidate-site")
DEPENDENCY_SITE = os.environ.get(
    "NL2REPO_CANDIDATE_DEPENDENCIES", "/opt/candidate-dependencies/site"
)
for _entry in (CANDIDATE_SITE, DEPENDENCY_SITE):
    if _entry and _entry not in sys.path:
        sys.path.insert(0, _entry)

NODES_PER_CLASS = 30
CLASS_LABELS = ("Theory", "Methods", "Systems")
FEATURE_DIM = 12
SEED = 1024


def _synthetic_cora(directory: Path) -> None:
    """Write a deterministic Cora-format ``.content``/``.cites`` pair.

    The upstream loader is format-driven, so a small generated citation graph
    exercises the same parsing, one-hot encoding, symmetrisation and split
    behaviour as the real corpus while staying offline and fast.
    """
    import numpy as np

    node_count = NODES_PER_CLASS * len(CLASS_LABELS)
    generator = np.random.default_rng(SEED)
    content_lines = []
    for index in range(node_count):
        label = CLASS_LABELS[index % len(CLASS_LABELS)]
        # Every row keeps at least one non-zero entry so row normalisation
        # never divides by zero.
        features = generator.integers(0, 2, size=FEATURE_DIM)
        features[index % FEATURE_DIM] = 1
        cells = "\t".join(str(int(value)) for value in features)
        content_lines.append(f"{1000 + index}\t{cells}\t{label}")
    (directory / "cora.content").write_text("\n".join(content_lines) + "\n", encoding="utf-8")

    edges = []
    for index in range(node_count):
        for offset in (1, 7):
            neighbor = (index + offset) % node_count
            if neighbor != index:
                edges.append(f"{1000 + index}\t{1000 + neighbor}")
    (directory / "cora.cites").write_text("\n".join(edges) + "\n", encoding="utf-8")


def _load_graph(directory: Path) -> dict[str, object]:
    import numpy as np

    from gnn.utils import load_data_v1, preprocess_features

    _synthetic_cora(directory)
    adj, features, y_train, y_val, y_test, train_mask, val_mask, test_mask = load_data_v1(
        "cora", path=f"{directory}{os.sep}"
    )
    dense_features = np.asarray(preprocess_features(features), dtype="float32")
    return {
        "adj": adj,
        "features": dense_features,
        "y_train": np.asarray(y_train),
        "y_val": np.asarray(y_val),
        "train_mask": np.asarray(train_mask),
        "val_mask": np.asarray(val_mask),
        "y_test": np.asarray(y_test),
        "test_mask": np.asarray(test_mask),
    }


def _prepare_tensorflow():
    import numpy as np
    import tensorflow as tf

    # The frozen public API is built on the legacy graph-mode Keras tree, which
    # requires eager execution to be disabled before any model is constructed.
    if tf.__version__ >= "2.0.0":
        tf.compat.v1.disable_eager_execution()
    np.random.seed(SEED)
    tf.compat.v1.set_random_seed(SEED)
    try:
        from tensorflow.python.keras.optimizers import Adam
    except ImportError:
        from tensorflow.python.keras.optimizer_v1 import Adam
    return tf, Adam


def _check(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def _finite(array) -> bool:
    import numpy as np

    return bool(np.all(np.isfinite(np.asarray(array, dtype="float64"))))


def _case_data_pipeline(directory: Path) -> None:
    """Loader, adjacency normalisation and split contracts."""
    import numpy as np
    import scipy.sparse as sp

    from gnn.utils import get_splits, preprocess_adj

    graph = _load_graph(directory)
    adj = graph["adj"]
    node_count = NODES_PER_CLASS * len(CLASS_LABELS)
    _check(adj.shape == (node_count, node_count), f"adjacency shape was {adj.shape}")
    _check(sp.issparse(adj), "load_data_v1 must return a sparse adjacency matrix")
    difference = abs(adj - adj.T)
    _check(difference.max() == 0 if difference.nnz else True, "adjacency must be symmetric")

    features = graph["features"]
    _check(features.shape == (node_count, FEATURE_DIM), f"feature shape was {features.shape}")
    _check(_finite(features), "normalised features must stay finite")
    row_sums = np.asarray(features).sum(axis=1)
    _check(bool(np.allclose(row_sums, 1.0, atol=1e-5)), "feature rows must be row-normalised")

    normalized = preprocess_adj(adj, symmetric=True)
    _check(sp.issparse(normalized), "preprocess_adj must return a sparse matrix")
    _check(normalized.shape == adj.shape, f"normalised adjacency shape was {normalized.shape}")
    _check(_finite(normalized.toarray()), "normalised adjacency must stay finite")
    _check(
        float(abs(preprocess_adj(adj, symmetric=False)).max()) > 0.0,
        "row-normalised adjacency must be non-trivial",
    )

    labels = graph["y_train"] + graph["y_val"] + graph["y_test"]
    _check(labels.shape == (node_count, len(CLASS_LABELS)), f"label shape was {labels.shape}")
    y_train, y_val, y_test, train_mask, val_mask, test_mask = get_splits(labels)
    for name, mask in (("train", train_mask), ("val", val_mask), ("test", test_mask)):
        _check(np.asarray(mask).shape == (node_count,), f"{name} mask shape was {mask.shape}")
        _check(np.asarray(mask).dtype == bool, f"{name} mask must be boolean")
    _check(bool(train_mask.any()), "training mask must select nodes")
    _check(bool(val_mask.any()), "validation mask must select nodes")
    _check(not bool((train_mask & val_mask).any()), "train and validation masks must be disjoint")
    for name, split in (("train", y_train), ("val", y_val), ("test", y_test)):
        _check(np.asarray(split).shape == labels.shape, f"{name} labels shape was {split.shape}")


def _fit_full_graph(model, model_input, graph, tf) -> None:
    import numpy as np

    node_count = graph["y_train"].shape[0]
    history = model.fit(
        model_input,
        graph["y_train"],
        sample_weight=graph["train_mask"],
        validation_data=(model_input, graph["y_val"], graph["val_mask"]),
        batch_size=node_count,
        epochs=1,
        shuffle=False,
        verbose=0,
        callbacks=[],
    )
    losses = [float(value) for value in history.history.get("loss", [])]
    _check(bool(losses), "training must record a loss value")
    _check(_finite(losses), f"training loss was not finite: {losses}")
    predictions = np.asarray(model.predict(model_input, batch_size=node_count))
    _check(
        predictions.shape == (node_count, len(CLASS_LABELS)),
        f"prediction shape was {predictions.shape}",
    )
    _check(_finite(predictions), "predictions must be finite")
    _check(
        bool(np.allclose(predictions.sum(axis=1), 1.0, atol=1e-4)),
        "model output must be normalised class scores",
    )


def _case_gcn(directory: Path, feature_less: bool) -> None:
    import numpy as np

    from gnn.gcn import GCN, GraphConvolution
    from gnn.utils import preprocess_adj

    tf, Adam = _prepare_tensorflow()
    graph = _load_graph(directory)
    adj = preprocess_adj(graph["adj"])
    node_count = adj.shape[-1]

    if feature_less:
        model_input = [np.arange(node_count), adj]
        feature_dim = node_count
    else:
        model_input = [graph["features"], adj]
        feature_dim = graph["features"].shape[-1]

    model = GCN(
        adj.shape[-1],
        feature_dim,
        16,
        graph["y_train"].shape[1],
        dropout_rate=0.5,
        l2_reg=2.5e-4,
        feature_less=feature_less,
    )
    _check(len(model.inputs) == 2, f"GCN must accept two inputs, got {len(model.inputs)}")
    _check(
        tuple(model.outputs[0].shape.as_list())[-1] == len(CLASS_LABELS),
        f"GCN output width was {model.outputs[0].shape.as_list()}",
    )
    model.compile(
        optimizer=Adam(0.01),
        loss="categorical_crossentropy",
        weighted_metrics=["categorical_crossentropy", "acc"],
    )
    _fit_full_graph(model, model_input, graph, tf)

    layer = GraphConvolution(8, dropout_rate=0.0, use_bias=True, l2_reg=0.0)
    _check(callable(layer), "GraphConvolution instances must be callable Keras layers")
    _check(
        isinstance(layer, tf.keras.layers.Layer)
        or "Layer" in {base.__name__ for base in type(layer).__mro__},
        "GraphConvolution must be a Keras layer",
    )


def _case_gat(directory: Path) -> None:
    import scipy.sparse as sp

    from gnn.gat import GAT, GATLayer

    tf, Adam = _prepare_tensorflow()
    graph = _load_graph(directory)
    adj = graph["adj"] + sp.eye(graph["adj"].shape[0])
    dense_adj = adj.toarray()

    model = GAT(
        adj_dim=dense_adj.shape[0],
        feature_dim=graph["features"].shape[1],
        num_class=graph["y_train"].shape[1],
        num_layers=2,
        n_attn_heads=8,
        att_embedding_size=8,
        dropout_rate=0.6,
        l2_reg=2.5e-4,
        use_bias=True,
    )
    _check(len(model.inputs) == 2, f"GAT must accept two inputs, got {len(model.inputs)}")
    model.compile(
        optimizer=Adam(lr=0.005),
        loss="categorical_crossentropy",
        weighted_metrics=["categorical_crossentropy", "acc"],
    )
    _fit_full_graph(model, [graph["features"], dense_adj], graph, tf)

    concat = GATLayer(att_embedding_size=4, head_num=3, reduction="concat")
    mean = GATLayer(att_embedding_size=4, head_num=3, reduction="mean")
    _check(concat is not mean, "GATLayer must build independent instances")
    raised = False
    try:
        GATLayer(att_embedding_size=4, head_num=0)
    except Exception:  # noqa: BLE001 - any clear failure satisfies the contract
        raised = True
    _check(raised, "GATLayer must reject a non-positive head count")


def _case_graphsage(directory: Path) -> None:
    import networkx as nx
    import numpy as np

    from gnn.graphsage import GraphSAGE, MeanAggregator, sample_neighs
    from gnn.utils import preprocess_adj

    tf, Adam = _prepare_tensorflow()
    graph = _load_graph(directory)
    # NetworkX 3.x renamed the SciPy constructor; the verifier builds the graph
    # itself, so it selects the constructor available in the frozen runtime.
    from_sparse = getattr(nx, "from_scipy_sparse_array", None) or nx.from_scipy_sparse_matrix
    networkx_graph = from_sparse(graph["adj"], create_using=nx.DiGraph())
    adj = preprocess_adj(graph["adj"])

    indexes = np.arange(adj.shape[0])
    model_input = [graph["features"], np.asarray(indexes, dtype=np.int32)]
    neighbor_maxlen = []
    for sample_num in (10, 25):
        sampled, counts = sample_neighs(networkx_graph, indexes, sample_num, self_loop=False)
        sampled = np.asarray(sampled)
        counts = np.asarray(counts)
        _check(
            sampled.shape[0] == indexes.shape[0],
            f"sample_neighs must return one row per node, got {sampled.shape}",
        )
        _check(
            counts.shape[0] == indexes.shape[0],
            f"sample_neighs must return one count per node, got {counts.shape}",
        )
        _check(int(counts.max()) == sample_num, f"sampled width was {int(counts.max())}")
        model_input.append(sampled)
        neighbor_maxlen.append(int(counts.max()))

    everything, all_counts = sample_neighs(networkx_graph, indexes[:5], None)
    _check(len(everything) == 5, "unlimited sampling must return one row per requested node")
    _check(len(all_counts) == 5, "unlimited sampling must return one count per requested node")

    model = GraphSAGE(
        feature_dim=graph["features"].shape[1],
        neighbor_num=neighbor_maxlen,
        n_hidden=16,
        n_classes=graph["y_train"].shape[1],
        use_bias=True,
        activation=tf.nn.relu,
        aggregator_type="mean",
        dropout_rate=0.5,
        l2_reg=2.5e-4,
    )
    _check(
        len(model.inputs) == 2 + len(neighbor_maxlen),
        f"GraphSAGE input count was {len(model.inputs)}",
    )
    model.compile(
        Adam(0.01),
        "categorical_crossentropy",
        weighted_metrics=["categorical_crossentropy", "acc"],
    )
    _fit_full_graph(model, model_input, graph, tf)

    aggregator = MeanAggregator(
        units=8, input_dim=graph["features"].shape[1], neigh_max=neighbor_maxlen[0]
    )
    _check(aggregator is not None, "MeanAggregator must be constructible")


CASES = {
    "data-pipeline-and-splits": _case_data_pipeline,
    "gcn-featureless-training": lambda directory: _case_gcn(directory, feature_less=True),
    "gat-multihead-attention-training": _case_gat,
    "graphsage-mean-aggregator-training": _case_graphsage,
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--case", required=True, choices=sorted(CASES))
    parser.add_argument("--output", required=True, type=Path)
    arguments = parser.parse_args()
    verdict: dict[str, str] = {"status": "failed"}
    try:
        with tempfile.TemporaryDirectory(prefix="gnn-fixture-") as temporary:
            CASES[arguments.case](Path(temporary))
        verdict = {"status": "passed"}
    except BaseException:  # noqa: BLE001 - the verdict must record every failure
        verdict = {"status": "failed", "message": traceback.format_exc(limit=6)[-900:]}
    arguments.output.write_text(json.dumps(verdict, sort_keys=True), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
