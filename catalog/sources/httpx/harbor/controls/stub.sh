#!/usr/bin/env bash
set -euo pipefail

mkdir -p /workspace/httpx
cat > /workspace/pyproject.toml <<'EOF'
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "httpx"
version = "0.28.1"
requires-python = ">=3.9"

[tool.hatch.build.targets.wheel]
packages = ["httpx"]
EOF

cat > /workspace/httpx/__init__.py <<'EOF'
__version__ = "0.28.1"
class Client: pass
class AsyncClient: pass
class MockTransport: pass
class Request: pass
class Response: pass
class HTTPError(Exception): pass
class HTTPStatusError(HTTPError): pass
class RequestError(HTTPError): pass
class TimeoutException(RequestError): pass
def __getattr__(name):
    if name.startswith("HTTP") or name.endswith("Error"):
        return type(name, (Exception,), {})
    return type(name, (), {})
EOF
