#!/usr/bin/env bash
set -euo pipefail
cat > /workspace/pyproject.toml <<'TOML'
[build-system]
requires = ["setuptools==84.0.0"]
build-backend = "setuptools.build_meta"
[project]
name = "ghapi"
version = "2.1.3"
[tool.setuptools]
packages = ["ghapi"]
TOML
mkdir -p /workspace/ghapi
cat > /workspace/ghapi/__init__.py <<'PY'
__version__ = "2.1.3"
PY
cat > /workspace/ghapi/core.py <<'PY'
def date2gh(value): return ""
def gh2date(value): return None
def dep_key(value): return ""
def local_dep_graph(root): return {}
def dep_closure(name, graph): return set()
def dep_order(graph, names=None): return []
def dep_dependents(graph, names=None): return {}
def issue_body(tmpl, sections): return ""
class GhRows(list): pass
PY
cat > /workspace/ghapi/page.py <<'PY'
def parse_link_hdr(header): return {}
async def paged(*args, **kwargs):
    if False: yield None
async def pages(*args, **kwargs): return []
def sync_paged(*args, **kwargs): return iter(())
PY
cat > /workspace/ghapi/auth.py <<'PY'
class _Scope:
    repo = "repo"
Scope = _Scope()
def scope_str(*values): return ""
PY
cat > /workspace/ghapi/all.py <<'PY'
from .core import *
from .page import *
from .auth import *
PY
touch /workspace/ghapi/py.typed
