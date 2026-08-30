# Build `tiktoken`

Create a complete, installable Python project named `tiktoken` from an empty
workspace. Implement the deterministic core of the frozen `tiktoken` 0.14.0
API described here. The evaluation is offline and uses a separate child
process to import the candidate; do not depend on a preinstalled `tiktoken`,
the verifier files, or network access at runtime.

## Project Description

`tiktoken` is a byte-pair-encoding (BPE) tokenizer. An `Encoding` splits text
with a regex, merges byte pieces according to ranked vocabulary entries, and
maps token IDs back to bytes or text. The package also exposes deterministic
model-name mappings, local BPE file loaders, and a small educational BPE
trainer.

This task is an explicit offline adaptation of the upstream package. The
upstream release contains a Rust/PyO3 accelerator and public encoding
constructors whose vocabulary files are fetched from object storage. A
portable pure-Python implementation is accepted and preferred: the scored
contract never performs a network request and does not require a native
extension or the large remote vocabulary files. Preserve the public behavior
of the APIs below.

## Supports

- Provide an installable distribution and import package named `tiktoken`,
  with `tiktoken.__version__ == "0.14.0"` and `tiktoken.__all__` containing
  `Encoding`, `encoding_for_model`, `encoding_name_for_model`, `get_encoding`,
  and `list_encoding_names`.
- Use a normal `pyproject.toml` build backend. Runtime dependencies may be
  `regex` and `requests`, both exact-pinned by the build environment; no
  other third-party package is required and no dependency may be downloaded
  during evaluation.
- Make `tiktoken.core`, `tiktoken.load`, `tiktoken.model`,
  `tiktoken.registry`, `tiktoken._educational`, and
  `tiktoken_ext.openai_public` importable. Include `tiktoken/py.typed`.
- Keep normal operations local. `read_file` may read a caller-supplied local
  path; no documented scored operation may call a URL, subprocess, or service.

## API Usage Guide

### `tiktoken.Encoding`

Import path: `from tiktoken import Encoding`.

```python
Encoding(name: str, *, pat_str: str,
         mergeable_ranks: dict[bytes, int],
         special_tokens: dict[str, int],
         explicit_n_vocab: int | None = None)
```

`mergeable_ranks` maps non-special byte strings to their integer token ranks.
The rank determines merge priority: lower-ranked adjacent pairs are merged
first. `special_tokens` maps reserved text strings to token IDs. If
`explicit_n_vocab` is supplied, require the number of entries and the highest
token ID to agree with it. `repr(encoding)` is `<Encoding 'name'>`,
`max_token_value` is the highest ID, `n_vocab` is one greater, and
`special_tokens_set`, `eot_token`, `is_special_token`, and `token_byte_values`
expose the corresponding read-only/derived values.

`encode_ordinary(text) -> list[int]` ignores special-token recognition.
`encode(text, *, allowed_special=set(), disallowed_special="all") -> list[int]`
recognizes special strings only when allowed and otherwise raises `ValueError`
for a disallowed special string. Passing `disallowed_special=()` treats it as
ordinary text; passing `allowed_special="all"` allows every special token.
Inputs are Unicode strings. Lone surrogate code points are replaced in the
same way as UTF-8 replacement before tokenization.

The regex pattern is applied to each text input. Each matched UTF-8 byte piece
is BPE-encoded. `encode_single_token(str | bytes) -> int` requires one known
token and raises `KeyError` otherwise. `decode_bytes(tokens) -> bytes`,
`decode(tokens, errors="replace") -> str`,
`decode_single_token_bytes(token) -> bytes`, and
`decode_tokens_bytes(tokens) -> list[bytes]` reverse the operation and raise
`KeyError` for unknown IDs. `decode_with_offsets(tokens)` returns
`(decoded_text, offsets)` where each offset is the Unicode-character index at
which that token's bytes begin. `decode_batch`, `decode_bytes_batch`,
`encode_batch`, and `encode_ordinary_batch` preserve input order and accept a
`num_threads` keyword; deterministic sequential execution is sufficient.

`encode_to_numpy` is optional when NumPy is unavailable, but when implemented
it returns a `uint32` array. `encode_with_unstable` returns a pair of stable
tokens and possible completion token sequences; an empty completion list is
valid for an implementation that has no unstable suffix candidates.

For the following concrete fixture, the expected merge result is part of the
public contract and is useful for local checks:

```python
ranks = {bytes([i]): i for i in range(256)}
ranks.update({b"he": 256, b"ll": 257, b"hell": 258, b"hello": 259})
enc = Encoding("fixture", pat_str=r"[A-Za-z]+|\\s+|[^A-Za-z\\s]+",
               mergeable_ranks=ranks, special_tokens={"<|end|>": 300})
assert enc.encode("hello", disallowed_special=()) == [259]
assert enc.decode([259]) == "hello"
```

### Registry and model helpers

`list_encoding_names() -> list[str]` returns a deterministic list containing
the seven upstream names: `gpt2`, `r50k_base`, `p50k_base`, `p50k_edit`,
`cl100k_base`, `o200k_base`, and `o200k_harmony`. `get_encoding(name)` returns
an `Encoding` for those names and raises `ValueError` for an unknown name.
The offline adaptation may use a compact local vocabulary for these built-ins;
it must not fetch remote files. `encoding_name_for_model(model_name)` maps
known exact names and documented prefixes to those encoding names and raises
`KeyError` for an unknown model. `encoding_for_model` composes the two helpers.

### `tiktoken.load`

`check_hash(data, expected_hash) -> bool` compares SHA-256 hex digests.
`read_file(path)` reads a local file. `read_file_cached(path, expected_hash=None)`
uses `TIKTOKEN_CACHE_DIR` when set, otherwise a temporary cache, and checks an
optional SHA-256 digest. `load_tiktoken_bpe(path, expected_hash=None)` parses
non-empty lines of base64 token plus integer rank into a byte-to-rank dict and
raises `ValueError` for malformed lines or a digest mismatch.
`dump_tiktoken_bpe(ranks, path)` writes entries ordered by rank. The
`data_gym_to_mergeable_bpe_ranks` helper accepts two local files and produces
the equivalent byte-rank mapping; it must preserve the documented hash checks.

### `tiktoken._educational`

`bpe_encode(mergeable_ranks, input, visualise=None) -> list[int]` performs the
same ranked byte-pair merge for a byte string. `bpe_train(data, vocab_size,
pat_str, visualise=None) -> dict[bytes, int]` starts with byte symbols and
learns the most frequent adjacent pair until the requested vocabulary size or
no merge remains. Ties must be resolved deterministically. `SimpleBytePairEncoding`
wraps these operations with `encode`, `decode_bytes`, `decode`,
`decode_tokens_bytes`, `train`, and `from_tiktoken`.

## Implementation Notes

- The candidate starts from zero files. Keep implementation and packaging
  files separate from hidden verifier files. Do not write reward, JUnit, or
  collection files from candidate code.
- Use a real ranked BPE implementation, not a lookup table for hidden cases.
  All participating token bytes must be reversible; unknown token IDs must
  raise the specified exception.
- Regex matching, keyword/model mapping, local file parsing, pickling, batch
  ordering, special-token errors, and Unicode replacement are observable.
  Preserve exception types and normal `functools`/`pickle` behavior.
- The scored contract excludes the upstream benchmark scripts, optional
  `blobfile`, NumPy acceleration, live URL fetching, huge remote vocabularies,
  and private upstream tests. These exclusions are an intentional bounded
  adaptation, not permission to omit the documented core API.
