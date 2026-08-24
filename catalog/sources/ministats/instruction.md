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
