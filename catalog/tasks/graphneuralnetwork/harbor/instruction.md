# GraphNeuralNetwork

## Project Description
Build a Python package named `GraphNeuralNetwork` that provides reusable graph neural network components for node classification. The package must support GCN, GAT, and GraphSAGE models, graph data loading and preprocessing, and Keras-compatible training and evaluation.
The project should be usable from a clean checkout and should include the Cora data layout used by the examples.

## Supports
- Target Python 3.10.11 and provide a conventional `setup.py` for editable installation.
- Declare the runtime dependencies needed by the public package, including TensorFlow, NetworkX, NumPy, SciPy-compatible sparse operations, scikit-learn, and Matplotlib.
- Put the importable package in `gnn/` and expose a coherent public entry point from `gnn/__init__.py`.
- Keep model inputs and outputs shape-stable for full-graph node classification and preserve sparse adjacency support where the API accepts it.
- Do not require a remote service or network access when loading the checked-in Cora data.

## API Usage Guide

### Package
- `gnn` is the package namespace. It should expose the primary `GCN`, `GAT`, and `GraphSAGE` model factories and a package version.
- The implementation modules are `gnn.gcn`, `gnn.gat`, `gnn.graphsage`, and `gnn.utils`.

### Data Utilities
- `gnn.utils.load_data_v1(dataset="cora", path="../data/cora/")` loads a content/cites graph. Return `(adj, features, y_train, y_val, y_test, train_mask, val_mask, test_mask)`. `adj` is a SciPy sparse adjacency matrix, `features` is a node-feature matrix, labels are one-hot arrays with one array per split, and masks are boolean node selectors.
- `gnn.utils.preprocess_adj(adj, symmetric=True)` adds self connections and returns a normalized sparse adjacency matrix. Use symmetric normalization when `symmetric` is true and row normalization otherwise.
- `gnn.utils.preprocess_features(features)` row-normalizes a feature matrix and returns a dense matrix with the same node and feature dimensions. Rows with no features must remain finite.
- `gnn.utils.get_splits(y)` returns split label arrays and boolean masks for training, validation, and test nodes.
- Preserve the utility behavior needed by the standard Cora files, including one-hot label encoding and conversion of directed edge data to a symmetric graph.

### GCN
- `gnn.gcn.GCN(adj_dim, feature_dim, n_hidden, num_class, num_layers=2, activation=tf.nn.relu, dropout_rate=0.5, l2_reg=0, feature_less=True)` returns a TensorFlow Keras model for node classification. It accepts a feature or feature-index input together with an adjacency input and returns one class-probability vector per node.
- The factory must support multiple layers, configurable hidden width, activation, dropout, L2 regularization, and featureless mode. The final output has `num_class` columns and normalized class scores.
- `gnn.gcn.GraphConvolution(units, activation=tf.nn.relu, dropout_rate=0.5, use_bias=True, l2_reg=0, feature_less=False, seed=1024, **kwargs)` is a Keras layer. Calling it with `[features, adjacency]` applies dropout, graph propagation, a trainable feature transform, optional bias, and the configured activation.

### GAT
- `gnn.gat.GAT(adj_dim, feature_dim, num_class, num_layers=2, n_attn_heads=8, att_embedding_size=8, dropout_rate=0.0, l2_reg=0.0, use_bias=True)` returns a Keras node-classification model accepting `[features, adjacency]` and producing one class-probability vector per node.
- `gnn.gat.GATLayer(att_embedding_size=8, head_num=8, dropout_rate=0.5, l2_reg=0, activation=tf.nn.relu, reduction="concat", use_bias=True, seed=1024, **kwargs)` implements multi-head graph attention. It must support `concat` and mean head reduction, configurable attention width, dropout, bias, activation, and regularization. Non-positive head counts are invalid.
- The layer accepts feature and adjacency tensors, masks attention to graph connections, and returns a two-dimensional node embedding whose width follows the selected reduction mode.

### GraphSAGE
- `gnn.graphsage.GraphSAGE(feature_dim, neighbor_num, n_hidden, n_classes, use_bias=True, activation=tf.nn.relu, aggregator_type="mean", dropout_rate=0.0, l2_reg=0)` returns a Keras model. Its inputs are the full feature matrix, central-node indices, and one sampled-neighbor tensor for each value in `neighbor_num`.
- `gnn.graphsage.MeanAggregator(units, input_dim, neigh_max, concat=True, dropout_rate=0.0, activation=tf.nn.relu, l2_reg=0, use_bias=False, seed=1024, **kwargs)` combines central-node and neighbor features using mean aggregation and returns the configured output width.
- `gnn.graphsage.PoolingAggregator(units, input_dim, neigh_max, aggregator="meanpooling", concat=True, dropout_rate=0.0, activation=tf.nn.relu, l2_reg=0, use_bias=False, seed=1024)` supports mean-pooling and max-pooling neighbor aggregation.
- `gnn.graphsage.sample_neighs(G, nodes, sample_num=None, self_loop=False, shuffle=True)` obtains neighbors from a NetworkX-like graph. With no sample limit it returns all neighbors; with a limit it samples that many per node, uses replacement when necessary, optionally includes the node itself, and optionally shuffles. Return `(sampled_neighbors, sampled_counts)` as NumPy arrays.

### Training and Evaluation
- Model factories return uncompiled Keras models so callers can choose an optimizer, loss, weighted metrics, callbacks, batch size, and epoch count.
- The models must work with categorical cross-entropy and node masks passed through Keras `sample_weight`, including validation data using a validation mask.
- Full-graph calls must preserve node ordering between features, adjacency, labels, and masks. Training and prediction must produce finite tensors with the documented shapes.
- Standard Keras callbacks, including early stopping and model checkpointing, should be usable without special adapters.

### Packaging and Examples
- `setup.py` must install the `gnn` package and declare its runtime dependencies. `requirements.txt` should list the same core dependency family.
- Include example entry points for running the GCN, GAT, and GraphSAGE workflows on Cora. Examples may assume the checked-in `data/cora/` layout.

## Behavior and Error Contracts
- Public functions accept NumPy arrays and SciPy sparse matrices in the forms described above and preserve node counts and feature widths.
- Empty or zero-valued feature rows must not create NaN or infinite normalized values.
- Invalid model configuration values, such as a non-positive attention head count or incompatible tensor dimensions, should fail clearly rather than silently changing shape.
- Neighbor sampling must return one result row and one count for every requested node, including graphs with fewer neighbors than the requested sample size.
- Repeated model construction with the same dimensions must expose compatible Keras input and output contracts; random initialization may remain stochastic.

## Implementation Notes
- Keep the implementation compatible with TensorFlow 2.x while retaining the public signatures and Keras layer behavior described here.
- Use sparse graph representations for data loading and preprocessing where practical; dense conversion is acceptable only at the model boundary that requires it.
- Keep implementation details, private helpers, and training data out of the public API. The package should be installable from the repository root with the legacy editable-install command.
- The checked-in source data is local and deterministic. Do not fetch Cora or any other dataset at import time.

## Completion Criteria
- A fresh workspace can install the package with `pip install -e .` and import `GCN`, `GAT`, `GraphSAGE`, and the documented utilities.
- The three model families can be built with their documented constructor arguments and used in a masked full-graph Keras training call.
- Cora loading, adjacency preprocessing, feature normalization, and neighbor sampling preserve the documented return shapes and finite-value guarantees.
- The project contains the required package modules, setup metadata, local data layout, and runnable examples.
