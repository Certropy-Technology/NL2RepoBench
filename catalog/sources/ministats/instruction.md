# Build `ministats`

## Project Description

Create the `ministats` project from an empty workspace. This is a repository-generation task for the frozen `python` package contract, task specification version `1.0.0`, at source revision `unknown`. Implement the public behavior described by the local inventories and the task-specific detail below; do not copy upstream source or tests. The supported scope is python, packaging, unicode, cli.

## Natural Language Instruction

Starting with an empty `workspace/`, create an installable `ministats` project. Implement every public/core API named in the API Usage Guide, its package exports, and its documented integration points. Preserve observable input types, return shapes, ordering, determinism, state changes, and documented exception behavior. The project must be usable through its declared `ministats` import path (or the package root for this Node task), and all required modules must be present in the directory structure below.

The task-specific specification retained below supplies the detailed behavior for each API family. Treat it as the contract: do not add unrelated APIs, replace deterministic behavior with randomized or time-dependent behavior, or weaken error handling.

## Supports

- Language/runtime: `python` on `3.12`; target environment metadata declares `Linux`.
- Distribution/package: `ministats`; import/root name: `ministats`. Package manager: `pip`.
- Install from the repository root with `python -m pip install . --no-deps`. Build metadata must be complete and agree with the package entry point.
- Dependency status in the frozen source metadata is `unknown`. Use only dependencies declared by the task and available in the preinstalled build image; standard-library modules are not third-party runtime dependencies.
- NoNetwork boundary: agent, candidate, verifier, Oracle, and controls run with `network_mode=no-network`. Do not access GitHub, PyPI, npm registries, Go proxy, DNS, or external services at runtime. Do not fetch source or dependencies during implementation or package use.

## Project Directory Structure

```text
workspace/
├── pyproject.toml
├── ministats/
│   └── __init__.py
└── README.md
```

The tree is the minimum public project layout. Add a module only when it corresponds to a documented import path or package resource. Do not place publicly unavailable evaluator code, non-public evaluation material, Oracle payloads, dependency caches, or trusted reports in this workspace.

## API Usage Guide

The public/core API families recorded in the local inventory are: Public API, `normalize`, `tokenize`, `summarize`, Command line interface.

For each listed family, the detailed contract below defines the import path or CLI entry, signature, accepted inputs, return type/shape, ordering and determinism, state or I/O side effects, errors, and examples. Implement the complete public surface, including root re-exports and aliases where the specification names them. If an API is stateful, preserve mutation and repeated-call behavior; if it is pure, do not introduce global state.

## Implementation Notes

Keep the implementation self-contained and deterministic under the declared runtime. The candidate repository must install from the workspace root, import through the documented public path, and run without external services. Preserve package metadata, module semantics (ESM/CommonJS or Python import behavior), serialization formats, resource cleanup, and boundary behavior described below. publicly unavailable evaluator adapters and non-public evaluation details are not part of the implementation.

## Examples

Ordinary project examples:

```bash
cd workspace
python -m pip install . --no-deps
```

```python
# Import the public package and use the task-specific APIs documented below.
from ministats import *
```

The retained task-specific examples below provide ordinary API calls and combinations grounded in the frozen inventory. Keep their result shapes and ordering exact.

## Error Handling and Boundary Conditions

- Empty inputs, malformed values, missing resources, duplicate values, and unsupported options must follow the task-specific error contracts below; do not silently coerce or discard information unless explicitly specified.
- Repeated calls must remain deterministic. Filesystem, process, clock, random, native, callback, and serialization boundaries are supported only where the local specification documents them.
- Network attempts are prohibited and must not be used as a fallback. Installation failures, missing offline dependencies, or unsupported external capabilities are environment/source concerns, not reasons to invent behavior.


## Source-derived task detail

# Build the `ministats` Python package

Create a complete, installable Python project in `/workspace`. The workspace starts empty.

The distribution name must be `ministats-bench`, and the import package must be `ministats`. Use a `src/` layout and support Python 3.10 or newer. The project must have no runtime dependencies.

## Public API

`ministats.__version__` must be `"1.0.0"`. Re-export these functions from `ministats`:

```python
def normalize(text: str) -> str: ...
def tokenize(text: str) -> list[str]: ...
def summarize(text: str, top: int = 3) -> dict[str, object]: ...
```

### `normalize`

1. Reject non-string input with `TypeError`.
2. Apply Unicode NFKC normalization.
3. Apply Unicode-aware case folding.
4. Replace each run of whitespace with one ASCII space.
5. Remove leading and trailing whitespace.

Examples:

```python
normalize("  Hello\tWORLD  ") == "hello world"
normalize("ＣＡＴ") == "cat"
```

### `tokenize`

Normalize the input, then return every maximal run of Unicode alphanumeric characters. Punctuation, symbols, whitespace, and underscores are separators. Preserve token order and duplicates.

Examples:

```python
tokenize("One, TWO_one 2026!") == ["one", "two", "one", "2026"]
tokenize("") == []
```

### `summarize`

Reject a non-integer `top` with `TypeError` and a negative `top` with `ValueError`. Return a dictionary with exactly these keys:

- `characters`: the number of Unicode code points in the original input;
- `words`: the number of tokens;
- `unique_words`: the number of distinct tokens;
- `top_words`: up to `top` `(token, count)` tuples.

Sort `top_words` by descending count and then ascending token for ties. A `top` value of zero returns an empty list.

## Command line interface

Provide both the `ministats` console command and `python -m ministats`.

```text
ministats [TEXT] [--top N] [--pretty]
```

- If `TEXT` is omitted, read all text from standard input.
- `--top` defaults to `3` and has the same non-negative constraint as the Python API.
- Print the `summarize` result as UTF-8 JSON followed by a newline.
- Use JSON object keys in sorted order.
- `--pretty` uses an indentation level of 2; otherwise output one compact line.
- Invalid CLI arguments must use normal `argparse` behavior and a non-zero exit code.

Include a concise README with installation and API/CLI examples. You may add your own tests, but the finished project must install with `pip install .`.
