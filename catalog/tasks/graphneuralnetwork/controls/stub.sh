#!/usr/bin/env bash
# Stub control: a minimally importable but non-functional gnn package.
# The package installs and imports, so the verifier reaches its cases, but no
# real behaviour exists and every leaf must fail.
set -euo pipefail

find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
mkdir -p /workspace/gnn

cat > /workspace/pyproject.toml <<'PYPROJECT'
[build-system]
requires = ["setuptools==80.10.2", "wheel==0.45.1"]
build-backend = "setuptools.build_meta"

[project]
name = "gnn"
version = "0.0.0"
description = "Stub control package for the graphneuralnetwork task."

[tool.setuptools.packages.find]
where = ["."]
include = ["gnn*"]
PYPROJECT

cat > /workspace/gnn/__init__.py <<'PACKAGE'
__version__ = "0.0.0"
PACKAGE

cat > /workspace/gnn/utils.py <<'UTILS'
def load_data_v1(dataset="cora", path="../data/cora/"):
    return None


def preprocess_adj(adj, symmetric=True):
    return adj


def preprocess_features(features):
    return features


def get_splits(y):
    return None
UTILS

cat > /workspace/gnn/gcn.py <<'GCN'
class GraphConvolution:
    def __init__(self, *args, **kwargs):
        pass


def GCN(*args, **kwargs):
    return None
GCN

cat > /workspace/gnn/gat.py <<'GAT'
class GATLayer:
    def __init__(self, *args, **kwargs):
        pass


def GAT(*args, **kwargs):
    return None
GAT

cat > /workspace/gnn/graphsage.py <<'GRAPHSAGE'
class MeanAggregator:
    def __init__(self, *args, **kwargs):
        pass


class PoolingAggregator:
    def __init__(self, *args, **kwargs):
        pass


def sample_neighs(G, nodes, sample_num=None, self_loop=False, shuffle=True):
    return [], []


def GraphSAGE(*args, **kwargs):
    return None
GRAPHSAGE
