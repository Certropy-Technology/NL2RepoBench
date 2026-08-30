# Build `tokenizers`

Create a complete installable Python distribution named `tokenizers` from an empty workspace. The frozen upstream package is a fast tokenizer library backed by a Rust extension. The evaluator is offline and calls the implementation through a separate child-process boundary.

## Project Description

Implement the public Python package exposed by Hugging Face tokenizers at revision `d5827816baedcbf1cb5b452dea8048150b6872df`. The package combines a configurable `Tokenizer` pipeline with model, normalizer, pre-tokenizer, decoder, processor, and trainer components. It also provides five convenience tokenizer classes for common BPE, WordPiece, and Unigram workflows.

## Supports

- Support CPython 3.10+; verification uses CPython 3.12 on Linux amd64.
- The distribution must be installable with `python -m pip install . --no-deps --no-build-isolation` after the declared build closure is preinstalled. Runtime execution must not download anything.
- Expose `tokenizers.__version__` as `0.23.2-dev.0` and keep the top-level re-exports and submodule imports described below.
- Declare the runtime dependency `huggingface_hub>=0.16.4,<2.0` in distribution metadata; it is preinstalled by the evaluator, and local tokenizer operations must not invoke it or access the network.
- A Rust extension is optional as an implementation technique: a compatible pure-Python implementation is acceptable, but all specified observable behavior must match.
- Do not require network, model downloads, Hugging Face Hub access, sentencepiece protobuf files, or platform services for the frozen behavior.

## API Usage Guide

### Top-level package and model pipeline

`tokenizers` exports `Tokenizer`, `Encoding`, `AddedToken`, `NormalizedString`, `PreTokenizedString`, `Regex`, `Token`, `models`, `normalizers`, `pre_tokenizers`, `processors`, `trainers`, `decoders`, and `__version__`. The model namespace exposes `BPE`, `WordLevel`, `WordPiece`, and `Unigram`.

`Tokenizer(model)` constructs a pipeline. Assign `normalizer`, `pre_tokenizer`, `post_processor`, and `decoder` components through their public attributes. `encode(sequence, pair=None, is_pretokenized=False, add_special_tokens=True) -> Encoding` accepts text or a list/tuple of pre-tokenized strings. `encode_batch(inputs, is_pretokenized=False, add_special_tokens=True) -> list[Encoding]` preserves input order. Invalid input types raise a useful exception rather than silently coercing data.

`Encoding` exposes `ids`, `tokens`, `type_ids`, `attention_mask`, `special_tokens_mask`, `offsets`, `word_ids`, and `sequence_ids`. `decode(ids, skip_special_tokens=True) -> str` reconstructs text according to the configured decoder. `get_vocab(with_added_tokens=True) -> dict[str, int]`, `get_vocab_size(with_added_tokens=True) -> int`, `token_to_id(token) -> int | None`, and `id_to_token(id) -> str | None` expose vocabulary state.

`add_tokens(tokens) -> int` and `add_special_tokens(tokens) -> int` add ordinary or special `str`/`AddedToken` values and return the number newly added. Added tokens must be respected by later encoding. `to_str(pretty=False) -> str`, `save(path, pretty=True)`, `from_str(data)`, and `from_file(path)` provide JSON serialization and round trips.

`enable_padding(direction="right", pad_to_multiple_of=None, pad_id=0, pad_type_id=0, pad_token="[PAD]", length=None)` configures batch padding; `no_padding()` disables it and `padding` reports either `None` or the current configuration. `enable_truncation(max_length, stride=0, strategy="longest_first")` limits encoded sequences and `truncation` reports the configuration; `no_truncation()` disables it. Padding and truncation are deterministic and preserve masks and offsets.

### Components and trainers

Expose the component constructors from their submodules, including `normalizers.Lowercase`, `NFKC`, `Sequence`, `Replace`, `BertNormalizer`; `pre_tokenizers.Whitespace`, `WhitespaceSplit`, `BertPreTokenizer`, `ByteLevel`, `Metaspace`; `decoders.WordPiece`, `BPEDecoder`, `ByteLevel`, `Metaspace`; `processors.TemplateProcessing`, `BertProcessing`, `ByteLevel`; and `trainers.BpeTrainer`, `WordLevelTrainer`, `WordPieceTrainer`, `UnigramTrainer`.

`Tokenizer.train(files, trainer)` reads local text files. `Tokenizer.train_from_iterator(iterator, trainer, length=None)` consumes an iterator of strings. Trainers honor `vocab_size`, `min_frequency`, `special_tokens`, and their model-specific options. Training must produce a usable vocabulary and deterministic subsequent encoding; it must not use a network source.

### Convenience tokenizers

Import `CharBPETokenizer`, `ByteLevelBPETokenizer`, `SentencePieceBPETokenizer`, `SentencePieceUnigramTokenizer`, and `BertWordPieceTokenizer` from `tokenizers.implementations` and the package root. Each constructor configures a low-level pipeline and provides `encode`, `encode_batch`, `decode`, `get_vocab`, `get_vocab_size`, `add_tokens`, `add_special_tokens`, `train`, and `train_from_iterator`. `BertWordPieceTokenizer` applies its `lowercase` and special-token settings; the BPE wrappers configure their documented pre-tokenizer/decoder pair.

### Boundary behavior

Unknown tokens use the model's configured unknown token when present. Encoding records character offsets into the original input and word indices. A pair with `TemplateProcessing` inserts declared special tokens and correct type IDs. `async_encode_batch` and `async_encode_batch_fast` return the same ordered encodings as their synchronous counterparts. `Tokenizer` must not contact the Hub during import or ordinary local operations.

## Implementation Notes

- Keep package metadata, top-level re-exports, submodule imports, and the install path consistent. The hidden verifier owns its reports and invokes candidate code only in bounded UID-isolated child processes.
- Use standard-library-only implementation code unless a dependency is necessary for the declared package metadata. The preinstalled `huggingface_hub` dependency is not permission to access the network.
- Preserve deterministic ordering in vocabulary mappings, batch results, serialization, and training for the same inputs.
- Filesystem serialization and local training are allowed; live Hub downloads, SentencePiece model protobuf parsing, multiprocessing discovery, and free-threaded/platform-specific integration are outside this task's frozen denominator.
