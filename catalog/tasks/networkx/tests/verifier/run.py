from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

RUNUSER = "/usr/sbin/runuser"
ADAPTER_PATH = Path("/tmp/candidate-site/networkx_verifier_adapter.py")
CASES: dict[str, Any] = {
    "graph-basics": {"nodes": [1, 2, 3], "edges": [[1, 2], [2, 3]], "order": 3, "size": 2},
    "graph-data": {"graph": "demo", "node": "red", "edge": 2},
    "graph-degree": {"degree": [[0, 1], [1, 2], [2, 2], [3, 1]], "weighted": [[0, 1], [1, 2], [2, 2], [3, 1]]},
    "digraph": {"succ": [3], "pred": [1, 3], "in": 2, "out": 1},
    "multigraph": {"keys": ["first", 1], "count": 2, "weights": [1, 2]},
    "convert-edgelist": {"dict": {"1": [2, 3], "2": [1, 3], "3": [2, 1]}, "edges": [[1, 2, {}], [1, 3, {}], [2, 3, {}]]},
    "convert-dict": [["a", "b"], ["b", "c"]],
    "shortest-path": {"path": [0, 1, 2, 3, 4], "length": 4, "all": {"0": [2, 1, 0], "1": [2, 1], "2": [2], "3": [2, 3], "4": [2, 3, 4]}},
    "weighted-path": {"path": ["a", "c", "b"], "length": 2},
    "all-shortest": [[0, 1, 3], [0, 2, 3]],
    "bfs": {"tree": [[0, 1], [0, 2], [1, 3], [2, 4]], "succ": {"0": [1, 2], "1": [3], "2": [4]}},
    "dfs": [0, 1, 3, 2, 4],
    "connected": {"components": [[0, 1, 2], [3, 4]], "connected": False},
    "strongly-connected": [[0, 1], [2]],
    "topological": ["shop", "cook", "eat"],
    "dag-longest": [0, 1, 3],
    "generators": {"path": [[0, 1], [1, 2], [2, 3]], "cycle": [[0, 1], [0, 3], [1, 2], [2, 3]], "complete": 6, "grid": 7},
    "relabel": {"nodes": ["a", "b", "c"], "edges": [["a", "b"], ["b", "c"]]},
    "subgraph": {"nodes": [1, 2, 3], "edges": [[1, 2], [2, 3]]},
    "compose": [[0, 1], [1, 2], [2, 3]],
    "degree-centrality": {"0": 0.5, "1": 1.0, "2": 0.5},
    "clustering": {"triangle": 1.0, "path": 0},
    "triangles": {"0": 1, "1": 1, "2": 1, "3": 0},
    "attributes": {"nodes": {"1": "source", "2": "middle"}, "edges": {"(1, 2)": 4, "(2, 3)": 7}},
    "node-link": {"nodes": ["a", "b", "c"], "edges": [["a", "b"], ["b", "c"]]},
    "is-tree": {"tree": True, "forest": True, "density": 0.5},
    "path-weight": 3,
    "to-directed": [[0, 1], [1, 0], [1, 2], [2, 1]],
    "exception-node": "networkx.exception.NetworkXError",
    "exception-path": "networkx.exception.NodeNotFound",
    "exception-null": "networkx.exception.NetworkXPointlessConcept",
    "copy-isolation": {"original": [0, 1], "copy": [0, 1, 3]},
    "update": {"nodes": [["a", {"x": 1}], ["b", {}]], "edges": [["a", "b"]]},
    "graph-name": {"name": "x", "graph": "initial"},
    "weighted-degree": 5,
    "number-of": {"nodes": 2, "edges": 2},
    "add-path": [[0, 1], [1, 2]],
}


def invoke(case: str) -> dict[str, Any]:
    command = [RUNUSER, "-u", "candidate", "--", "/usr/bin/env", "HOME=/tmp", "TMPDIR=/tmp", "PATH=/usr/local/bin:/usr/bin:/bin", "PYTHONNOUSERSITE=1", "PYTHONDONTWRITEBYTECODE=1", "/usr/local/bin/python", "-I", "-B", str(ADAPTER_PATH), "--candidate-site", "/tmp/candidate-site", "--case", case]
    try:
        # Keep the full 37-case suite within the task's cumulative call budget
        # even when a candidate deliberately hangs every child invocation.
        completed = subprocess.run(command, capture_output=True, text=True, timeout=4, check=False)
    except (OSError, subprocess.SubprocessError) as exc:
        return {"ok": False, "exception_type": type(exc).__name__, "message": str(exc)}
    lines = [line for line in completed.stdout.splitlines() if line.strip()]
    if completed.returncode != 0 or len(lines) != 1:
        return {"ok": False, "exception_type": "CandidateProcessError", "message": completed.stderr[-1000:]}
    try:
        result = json.loads(lines[0])
    except json.JSONDecodeError as exc:
        return {"ok": False, "exception_type": "CandidateProtocolError", "message": str(exc)}
    return result if isinstance(result, dict) else {"ok": False, "exception_type": "CandidateProtocolError"}


def main() -> int:
    readable_adapter = ADAPTER_PATH
    readable_adapter.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(Path(__file__).with_name("adapter.py"), readable_adapter)
    os.chmod(readable_adapter, 0o555)
    leaves = []
    for case, expected in CASES.items():
        result = invoke(case)
        actual = result.get("value") if result.get("ok") is True else result.get("exception_type")
        passed = actual == expected
        leaves.append({"id": f"networkx/{case}", "status": "passed" if passed else "failed", "message": "" if passed else json.dumps({"actual": actual, "expected": expected}, sort_keys=True, default=str)[:1000]})
    print(json.dumps({"schema_version": "1.0", "leaves": leaves}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
