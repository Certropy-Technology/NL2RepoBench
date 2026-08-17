#!/usr/bin/env bash
set -euo pipefail

mkdir -p /workspace/src/ministats

cat > /workspace/pyproject.toml <<'EOF'
[build-system]
requires = ["setuptools>=70", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "ministats-bench"
version = "1.0.0"
description = "Small Unicode-aware text statistics library"
readme = "README.md"
requires-python = ">=3.10"
dependencies = []

[project.scripts]
ministats = "ministats.__main__:main"

[tool.setuptools.packages.find]
where = ["src"]
EOF

cat > /workspace/README.md <<'EOF'
# ministats

`ministats` normalizes Unicode text, tokenizes it, and reports deterministic word statistics.

```bash
pip install .
ministats "Red blue red" --top 1
```

```python
from ministats import normalize, summarize, tokenize

normalize("  Hello\tWORLD  ")
tokenize("One, TWO_one 2026!")
summarize("Red blue red", top=1)
```
EOF

cat > /workspace/src/ministats/core.py <<'EOF'
from __future__ import annotations

from collections import Counter
import unicodedata


def normalize(text: str) -> str:
    if not isinstance(text, str):
        raise TypeError("text must be a string")
    normalized = unicodedata.normalize("NFKC", text).casefold()
    return " ".join(normalized.split())


def tokenize(text: str) -> list[str]:
    normalized = normalize(text)
    tokens: list[str] = []
    current: list[str] = []

    for character in normalized:
        if character.isalnum():
            current.append(character)
        elif current:
            tokens.append("".join(current))
            current.clear()

    if current:
        tokens.append("".join(current))
    return tokens


def summarize(text: str, top: int = 3) -> dict[str, object]:
    if not isinstance(top, int):
        raise TypeError("top must be an integer")
    if top < 0:
        raise ValueError("top must be non-negative")

    tokens = tokenize(text)
    counts = Counter(tokens)
    ordered = sorted(counts.items(), key=lambda item: (-item[1], item[0]))
    return {
        "characters": len(text),
        "words": len(tokens),
        "unique_words": len(counts),
        "top_words": ordered[:top],
    }
EOF

cat > /workspace/src/ministats/__init__.py <<'EOF'
from .core import normalize, summarize, tokenize

__version__ = "1.0.0"

__all__ = ["__version__", "normalize", "summarize", "tokenize"]
EOF

cat > /workspace/src/ministats/__main__.py <<'EOF'
from __future__ import annotations

import argparse
import json
import sys

from .core import summarize


def non_negative_integer(value: str) -> int:
    parsed = int(value)
    if parsed < 0:
        raise argparse.ArgumentTypeError("must be non-negative")
    return parsed


def main() -> None:
    parser = argparse.ArgumentParser(prog="ministats")
    parser.add_argument("text", nargs="?")
    parser.add_argument("--top", type=non_negative_integer, default=3)
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args()

    text = args.text if args.text is not None else sys.stdin.read()
    indent = 2 if args.pretty else None
    print(json.dumps(summarize(text, args.top), ensure_ascii=False, sort_keys=True, indent=indent))


if __name__ == "__main__":
    main()
EOF
