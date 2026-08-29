from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any


def typename(exc: BaseException) -> str:
    return f"{type(exc).__module__}.{type(exc).__qualname__}"


def exercise(case: str) -> Any:
    import networkx as nx

    if case == "graph-basics":
        g = nx.Graph()
        g.add_nodes_from([(1, {"role": "a"}), 2, 3])
        g.add_edges_from([(1, 2), (2, 3)])
        return {"nodes": list(g.nodes), "edges": [list(e) for e in g.edges], "order": g.order(), "size": g.size()}
    if case == "graph-data":
        g = nx.Graph(name="demo")
        g.add_node("a", color="red")
        g.add_edge("a", "b", weight=2)
        return {"graph": g.graph["name"], "node": g.nodes["a"]["color"], "edge": g["a"]["b"]["weight"]}
    if case == "graph-degree":
        g = nx.path_graph(4)
        return {"degree": [[n, d] for n, d in g.degree], "weighted": [[n, d] for n, d in g.degree(weight="weight")]}
    if case == "digraph":
        g = nx.DiGraph([(1, 2), (2, 3), (3, 2)])
        return {"succ": list(g.successors(2)), "pred": list(g.predecessors(2)), "in": g.in_degree(2), "out": g.out_degree(2)}
    if case == "multigraph":
        g = nx.MultiGraph()
        g.add_edge("a", "b", key="first", weight=1)
        g.add_edge("a", "b", weight=2)
        return {"keys": list(g["a"]["b"]), "count": g.number_of_edges("a", "b"), "weights": sorted(d["weight"] for d in g["a"]["b"].values())}
    if case == "convert-edgelist":
        g = nx.from_edgelist([(1, 2), (2, 3), (3, 1)])
        return {"dict": {str(k): list(v) for k, v in nx.to_dict_of_lists(g).items()}, "edges": sorted((e[0], e[1], e[2]) for e in nx.to_edgelist(g))}
    if case == "convert-dict":
        g = nx.from_dict_of_lists({"a": ["b"], "b": ["a", "c"], "c": ["b"]})
        return sorted(sorted(e) for e in g.edges)
    if case == "shortest-path":
        g = nx.path_graph(5)
        return {"path": nx.shortest_path(g, 0, 4), "length": nx.shortest_path_length(g, 0, 4), "all": nx.shortest_path(g, 2)}
    if case == "weighted-path":
        g = nx.Graph()
        g.add_weighted_edges_from([("a", "b", 5), ("a", "c", 1), ("c", "b", 1)])
        return {"path": nx.shortest_path(g, "a", "b", weight="weight"), "length": nx.shortest_path_length(g, "a", "b", weight="weight")}
    if case == "all-shortest":
        g = nx.Graph([(0, 1), (1, 3), (0, 2), (2, 3)])
        return [list(p) for p in nx.all_shortest_paths(g, 0, 3)]
    if case == "bfs":
        g = nx.Graph([(0, 1), (0, 2), (1, 3), (2, 4)])
        return {"tree": list(nx.bfs_tree(g, 0).edges), "succ": {str(k): list(v) for k, v in nx.bfs_successors(g, 0)}}
    if case == "dfs":
        return list(nx.dfs_preorder_nodes(nx.Graph([(0, 1), (0, 2), (1, 3), (2, 4)]), 0))
    if case == "connected":
        g = nx.Graph([(0, 1), (1, 2), (3, 4)])
        return {"components": [sorted(c) for c in nx.connected_components(g)], "connected": nx.is_connected(g)}
    if case == "strongly-connected":
        g = nx.DiGraph([(0, 1), (1, 0), (1, 2)])
        return sorted((sorted(c) for c in nx.strongly_connected_components(g)), key=lambda c: c[0])
    if case == "topological":
        g = nx.DiGraph([("cook", "eat"), ("shop", "cook")])
        return list(nx.topological_sort(g))
    if case == "dag-longest":
        g = nx.DiGraph([(0, 1), (0, 2), (1, 3), (2, 3)])
        return nx.dag_longest_path(g)
    if case == "generators":
        return {"path": list(nx.path_graph(4).edges), "cycle": list(nx.cycle_graph(4).edges), "complete": nx.complete_graph(4).number_of_edges(), "grid": nx.grid_2d_graph(2, 3).number_of_edges()}
    if case == "relabel":
        g = nx.path_graph(3)
        h = nx.relabel_nodes(g, {0: "a", 1: "b", 2: "c"})
        return {"nodes": list(h.nodes), "edges": [list(e) for e in h.edges]}
    if case == "subgraph":
        g = nx.Graph([(0, 1), (1, 2), (2, 3)])
        return {"nodes": list(g.subgraph([1, 2, 3]).nodes), "edges": [list(e) for e in g.subgraph([1, 2, 3]).edges]}
    if case == "compose":
        return sorted(nx.compose(nx.path_graph(3), nx.Graph([(2, 3)])).edges)
    if case == "degree-centrality":
        result = nx.degree_centrality(nx.path_graph(3))
        return {str(k): round(v, 6) for k, v in result.items()}
    if case == "clustering":
        return {"triangle": nx.clustering(nx.Graph([(0, 1), (1, 2), (2, 0)]), 0), "path": nx.clustering(nx.path_graph(3), 1)}
    if case == "triangles":
        return nx.triangles(nx.Graph([(0, 1), (1, 2), (2, 0), (2, 3)]))
    if case == "attributes":
        g = nx.Graph([(1, 2), (2, 3)])
        nx.set_node_attributes(g, {1: "source", 2: "middle"}, "label")
        nx.set_edge_attributes(g, {(1, 2): 4, (2, 3): 7}, "weight")
        return {"nodes": nx.get_node_attributes(g, "label"), "edges": {str(k): v for k, v in nx.get_edge_attributes(g, "weight").items()}}
    if case == "node-link":
        from networkx.readwrite import json_graph
        g = nx.Graph([("a", "b"), ("b", "c")])
        data = json_graph.node_link_data(g)
        h = json_graph.node_link_graph(data)
        return {"nodes": list(h.nodes), "edges": sorted(sorted(e) for e in h.edges)}
    if case == "is-tree":
        return {"tree": nx.is_tree(nx.path_graph(4)), "forest": nx.is_forest(nx.Graph([(0, 1), (2, 3)])), "density": round(nx.density(nx.path_graph(4)), 6)}
    if case == "path-weight":
        g = nx.Graph()
        g.add_edge("a", "b", cost=3)
        return nx.path_weight(g, ["a", "b"], "cost")
    if case == "to-directed":
        return list(nx.path_graph(3).to_directed().edges)
    if case == "exception-node":
        try:
            nx.Graph().neighbors("missing")
        except Exception as exc:
            return typename(exc)
    if case == "exception-path":
        try:
            nx.shortest_path(nx.Graph([(1, 2)]), 1, 3)
        except Exception as exc:
            return typename(exc)
    if case == "exception-null":
        try:
            nx.is_connected(nx.Graph())
        except Exception as exc:
            return typename(exc)
    if case == "copy-isolation":
        g = nx.path_graph(2)
        h = g.copy()
        h.add_node(3)
        return {"original": list(g.nodes), "copy": list(h.nodes)}
    if case == "update":
        g = nx.Graph()
        g.update(nodes=[("a", {"x": 1}), "b"], edges=[("a", "b")])
        return {"nodes": list(g.nodes(data=True)), "edges": list(g.edges)}
    if case == "graph-name":
        g = nx.Graph(name="initial")
        g.add_node(1)
        nx.set_node_attributes(g, {1: "x"}, "kind")
        return {"name": g.nodes[1]["kind"], "graph": g.graph["name"]}
    if case == "weighted-degree":
        g = nx.Graph()
        g.add_edge(0, 1, weight=2)
        g.add_edge(0, 2, weight=3)
        return g.degree(0, weight="weight")
    if case == "number-of":
        g = nx.MultiDiGraph([(0, 1), (0, 1)])
        return {"nodes": nx.number_of_nodes(g), "edges": nx.number_of_edges(g)}
    if case == "add-path":
        g = nx.Graph()
        nx.add_path(g, [0, 1, 2])
        return list(g.edges)
    raise ValueError(f"unknown case: {case}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate-site", required=True)
    parser.add_argument("--case", required=True)
    args = parser.parse_args()
    if os.path.realpath(args.candidate_site) != "/tmp/candidate-site":
        raise ValueError("candidate site is unavailable")
    sys.path.insert(0, args.candidate_site)
    try:
        value = exercise(args.case)
    except BaseException as exc:
        print(json.dumps({"ok": False, "exception_type": typename(exc), "message": str(exc)}))
    else:
        print(json.dumps({"ok": True, "value": value}, sort_keys=True, default=list))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
