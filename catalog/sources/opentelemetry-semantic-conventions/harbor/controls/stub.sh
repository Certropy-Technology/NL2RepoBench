#!/usr/bin/env bash
set -euo pipefail
rm -rf /workspace/*
mkdir -p /workspace/opentelemetry/semconv/{attributes,metrics,resource,trace}
cat > /workspace/pyproject.toml <<'TOML'
[build-system]
requires = ["setuptools==80.10.2"]
build-backend = "setuptools.build_meta"
[project]
name = "opentelemetry-semantic-conventions"
version = "0.0.0"
[tool.setuptools.packages.find]
where = ["."]
TOML
for f in /workspace/opentelemetry/__init__.py /workspace/opentelemetry/semconv/__init__.py /workspace/opentelemetry/semconv/attributes/__init__.py /workspace/opentelemetry/semconv/metrics/__init__.py /workspace/opentelemetry/semconv/resource/__init__.py /workspace/opentelemetry/semconv/trace/__init__.py; do : > "$f"; done
: > /workspace/opentelemetry/semconv/py.typed
printf '%s\n' '__version__ = "0.0.0"' > /workspace/opentelemetry/semconv/version.py
printf '%s\n' 'class Schemas: pass' > /workspace/opentelemetry/semconv/schemas.py
for f in http_attributes db_attributes service_attributes client_attributes server_attributes exception_attributes error_attributes; do : > "/workspace/opentelemetry/semconv/attributes/$f.py"; done
for f in http_metrics db_metrics; do : > "/workspace/opentelemetry/semconv/metrics/$f.py"; done
