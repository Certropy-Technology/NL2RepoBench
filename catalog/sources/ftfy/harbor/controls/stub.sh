#!/usr/bin/env bash
set -euo pipefail
mkdir -p /workspace/ftfy
cat > /workspace/pyproject.toml <<'EOF'
[build-system]
requires = []
build-backend = "hatchling.build"
[project]
name = "ftfy"
version = "6.3.1"
requires-python = ">=3.9"
EOF
cat > /workspace/ftfy/__init__.py <<'EOF'
__version__ = "6.3.1"
def fix_text(text, *args, **kwargs): return text
def fix_text_segment(text, *args, **kwargs): return text
def fix_encoding(text): return text
def guess_bytes(data): return data.decode("utf-8", "replace"), "utf-8"
EOF
cat > /workspace/ftfy/fixes.py <<'EOF'
def unescape_html(text): return text
def fix_surrogates(text): return text
def remove_control_chars(text): return text
def remove_terminal_escapes(text): return text
EOF
touch /workspace/ftfy/py.typed
