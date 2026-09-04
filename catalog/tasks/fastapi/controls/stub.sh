#!/usr/bin/env bash
set -euo pipefail
find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
mkdir -p /workspace/fastapi
cat > /workspace/pyproject.toml <<'EOF'
[build-system]
requires = ["setuptools==80.10.2", "wheel==0.45.1"]
build-backend = "setuptools.build_meta"

[project]
name = "fastapi"
version = "0.141.1"

[tool.setuptools]
packages = ["fastapi"]
EOF
cat > /workspace/fastapi/__init__.py <<'EOF'
__version__ = "0.141.1"
class _Stub:
    def __init__(self, *args, **kwargs):
        raise TypeError("stub")
FastAPI = APIRouter = Depends = Security = Path = Query = Header = Cookie = Body = Form = File = BackgroundTasks = _Stub
class HTTPException(Exception):
    pass
EOF
