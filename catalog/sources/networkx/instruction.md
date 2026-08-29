# Project Description

Implement `networkx`, a pure-Python library for creating, manipulating, and studying graphs and networks. The package must be installable from the repository with `python -m pip install --no-deps --no-build-isolation .` and importable as `import networkx as nx`.

The implementation should provide a coherent graph model and algorithms rather than a collection of disconnected stubs. Preserve insertion order where the Python data model exposes it, return the documented NetworkX view/iterator types, and raise the package's documented exception classes for invalid graph operations.

# Supports

The task contract covers these public areas:

- `networkx.Graph`, `DiGraph`, `MultiGraph`, and `MultiDiGraph`, including node and edge data, degree views, copying, updates, and directed/undirected conversion.
- Conversion helpers such as `from_edgelist`, `to_edgelist`, `from_dict_of_lists`, and `to_dict_of_lists`.
- Deterministic algorithms including `shortest_path`, `shortest_path_length`, `all_shortest_paths`, `bfs_tree`, `bfs_successors`, `dfs_preorder_nodes`, `connected_components`, `is_connected`, `strongly_connected_components`, `topological_sort`, `dag_longest_path`, `is_tree`, `is_forest`, `density`, `degree_centrality`, `clustering`, and `triangles`.
- Deterministic generators including `path_graph`, `cycle_graph`, `complete_graph`, and `grid_2d_graph`.
- Relabeling, graph composition, node/edge attribute helpers, and JSON node-link round trips.
- Stable exception behavior for missing nodes, absent paths, and invalid concepts.

The evaluation is offline and uses small in-memory graphs. Optional NumPy, SciPy, pandas, Matplotlib, backend plugins, random fixtures, large performance tests, and external services are outside this contract.

# API Usage Guide

Use the package under the `networkx` import name. Examples:

```python
import networkx as nx

graph = nx.Graph()
graph.add_nodes_from([(1, {"kind": "source"}), 2])
graph.add_edge(1, 2, weight=3)
assert list(graph.edges(data=True)) == [(1, 2, {"weight": 3})]
assert nx.shortest_path(graph, 1, 2) == [1, 2]
```

`Graph` and `DiGraph` accept an optional graph-like data argument and `**attr`; `add_node(node, **attr)` adds or updates one node, `add_nodes_from(nodes, **attr)` accepts nodes or `(node, attr_dict)` pairs, `add_edge(u, v, **attr)` adds or updates an edge, and `add_edges_from(ebunch, **attr)` accepts 2-tuples or 3-tuples. `nodes`, `edges`, and `degree` are views that support iteration and lookup. `has_node`, `has_edge`, `neighbors`, `successors`, and `predecessors` query the graph.

`shortest_path(G, source=None, target=None, weight=None)` returns a node list, a source-to-target mapping, or an all-pairs mapping according to the supplied endpoints. `shortest_path_length` follows the same endpoint convention and returns lengths. With `weight=None`, each edge has unit cost; with `weight="weight"`, the named edge attribute is used. `all_shortest_paths` yields every shortest node list in deterministic graph order.

`bfs_tree(G, source, depth_limit=None)` returns a directed traversal tree. `bfs_successors` and `dfs_preorder_nodes` return iterators. `connected_components`, `strongly_connected_components`, and `topological_sort` return iterators over sets or nodes; materialize them with `list`/`sorted` when comparing results. `is_connected` applies to undirected graphs and raises `NetworkXPointlessConcept` for a null graph.

`from_edgelist` and `from_dict_of_lists` construct graphs; their inverse helpers produce iterators or dictionaries. `nx.node_link_data(G)` returns a JSON-compatible dictionary, and `nx.node_link_graph(data)` reconstructs a graph. `relabel_nodes(G, mapping, copy=True)` returns a relabeled graph when copying and mutates the original when `copy=False`.

Most graph mutators return `None`; algorithm results are ordinary Python values, iterators, or graph views. Missing nodes raise `nx.NodeNotFound`, unreachable targets raise `nx.NetworkXNoPath`, and connectivity predicates on a null graph raise `nx.NetworkXPointlessConcept`.

# Implementation Notes

Use the standard library only for the required runtime contract. The project metadata must declare the setuptools build backend, the `networkx` package, and a Python 3.12-compatible version. Keep graph mutation and algorithm behavior deterministic for the same insertion order. Do not contact the network, invoke external graph backends, or depend on optional scientific packages.

The verifier calls the candidate through a separate child process and a JSON adapter. It does not import candidate modules in the trusted verifier process. Keep public imports and package metadata complete enough for the documented examples and for installation into a target directory.
