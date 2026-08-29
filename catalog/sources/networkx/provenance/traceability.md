# Traceability

| Contract area | Public behavior exercised | Verifier leaves |
| --- | --- | --- |
| Core classes | `Graph`, `DiGraph`, `MultiGraph`, node/edge data and views | `graph-basics`, `graph-data`, `graph-degree`, `digraph`, `multigraph` |
| Conversion | edge-list and dict-of-lists conversions | `convert-edgelist`, `convert-dict` |
| Paths and traversal | shortest paths, weights, BFS, DFS | `shortest-path`, `weighted-path`, `all-shortest`, `bfs`, `dfs`, `path-weight` |
| Connectivity and DAGs | component iterators, topological order, longest path | `connected`, `strongly-connected`, `topological`, `dag-longest` |
| Constructors and operators | generators, relabel, subgraph, compose, update | `generators`, `relabel`, `subgraph`, `compose`, `update`, `add-path` |
| Measures and attributes | centrality, clustering, triangles, attributes, degree | `degree-centrality`, `clustering`, `triangles`, `attributes`, `weighted-degree` |
| Serialization and structure | node-link data, tree/forest, directed conversion, counts | `node-link`, `is-tree`, `to-directed`, `number-of` |
| Failure and isolation | missing nodes/path, null graph, copy, graph metadata | `exception-node`, `exception-path`, `exception-null`, `copy-isolation`, `graph-name` |

The public instruction describes every contract family and its import paths,
input/result conventions, deterministic ordering expectations, and exception
boundary without exposing the adapter implementation or expected leaf data.
