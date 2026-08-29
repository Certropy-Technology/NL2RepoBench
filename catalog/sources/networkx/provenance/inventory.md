# Inventory

The frozen tree contains 583 Python files and 267 test files under `networkx/`,
with 4,486 statically declared test functions/classes. The upstream test suite
also includes optional NumPy/SciPy/pandas/Matplotlib paths, backend plugins,
large/random workloads, documentation doctests, and environment-sensitive
fixtures.

The production denominator is a 37-leaf custom-json-v1 deterministic contract.
It exercises graph and multidigraph mutation, multiedges, conversion helpers,
weighted and unweighted shortest paths, BFS/DFS, connected and strongly
connected components, topological sorting, DAG longest paths, generators,
relabeling, subgraphs, composition, centrality, clustering, triangles,
attributes, node-link serialization, tree/forest predicates, directed
conversion, exception classes, copying, updates, weighted degree, counts, and
path construction. Optional scientific integrations and external backends are
explicitly outside this offline contract.
