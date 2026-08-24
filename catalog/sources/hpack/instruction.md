# Build `hpack`

Create a complete, installable Python project named `hpack` from an empty
workspace. It is a pure-Python implementation of HPACK header compression for
HTTP/2. The required behavior is the behavior described here, not a copy of
the source tree or a hard-coded response table.

## Project Description

The package encodes ordered HTTP header fields into RFC 7541 HPACK header
blocks and decodes header blocks back into ordered header fields. It must
implement the static table, a stateful dynamic table, indexed and literal
representations, integer prefix encoding, optional Huffman coding, table-size
updates, sensitive/never-indexed fields, and decompressed header-list limits.

The distribution name and import package are both `hpack`. The root package
must report version `4.2.0` and re-export the documented classes and
exceptions. Normal package operations are local and deterministic for a fixed
input and object state. They must not contact a network, start a process, or
read a service.

## Supports

- Support CPython 3.10 and newer Python 3 versions in the source's supported
  range. Python 3.9 support is not required.
- Use a `src/hpack/` package layout and provide an installable build described
  by `pyproject.toml`. Include `hpack/py.typed` package data.
- Declare no third-party runtime dependencies. Build, test, lint, and
  documentation tools are not runtime imports of the installed package.
- The package must import from a clean runtime containing only the Python
  standard library. The verifier tests and fixture files are not runtime
  package data.
- Preserve the root import paths, public exception hierarchy, tuple behavior,
  byte/string conversion behavior, and state changes described below.

## API Usage Guide

### Root exports and exceptions

`hpack.__all__` must expose these names:

```text
Decoder, Encoder, HPACKDecodingError, HPACKError, HeaderTuple,
InvalidTableIndex, InvalidTableIndexError, InvalidTableSizeError,
NeverIndexedHeaderTuple, OversizedHeaderListError
```

`hpack.__version__` is the string `"4.2.0"`. The exception hierarchy is:

```text
HPACKError(Exception)
`-- HPACKDecodingError(HPACKError)
    |-- InvalidTableIndexError(HPACKDecodingError)
    |   `-- InvalidTableIndex(InvalidTableIndexError)
    |-- InvalidTableSizeError(HPACKDecodingError)
    `-- OversizedHeaderListError(HPACKDecodingError)
```

`InvalidTableIndex` remains available as the compatibility spelling. Invalid
wire data, invalid indexes, invalid UTF-8 header data, truncated fields, and
overlong integer encodings must raise an hpack decoding exception rather than
leaking `IndexError` or `UnicodeDecodeError`.

### Header tuple metadata

```python
HeaderTuple(*args)
NeverIndexedHeaderTuple(*args)
```

Both classes are tuple subclasses and compare equal to equivalent ordinary
two-tuples. They unpack and index exactly like tuples. `HeaderTuple.indexable`
is `True`; `NeverIndexedHeaderTuple.indexable` is `False`. Decoding a field
encoded with the never-indexed representation must preserve that subclass.

The ordinary public header shape is `(name, value)`. Names and values may be
Unicode strings or bytes at the encoder boundary. The decoder returns Unicode
strings by default and raw bytes when `raw=True`.

### Integer coding helpers

```python
from hpack.hpack import decode_integer, encode_integer

encode_integer(integer: int, prefix_bits: int) -> bytearray
decode_integer(data: bytes | memoryview, prefix_bits: int) -> tuple[int, int]
```

`prefix_bits` must be in the inclusive range 1 through 8. Encoding a negative
integer or using an invalid prefix raises `ValueError`. The encoder uses the
HPACK prefix integer representation and returns at least one byte. The decoder
returns the integer and the number of consumed bytes. Empty, truncated, or
overlong variable-integer input raises `HPACKDecodingError`. Values through
the implementation's supported unsigned 32-bit boundary must round-trip.

### `Encoder`

```python
from hpack import Encoder

Encoder()
Encoder.header_table_size -> int
Encoder.header_table_size = value
Encoder.encode(headers, huffman: bool = True) -> bytes
Encoder.add(to_add: tuple[bytes, bytes], sensitive: bool,
            huffman: bool = False) -> bytes
```

An encoder owns a fresh dynamic header table with default size 4096 bytes.
Changing `header_table_size` resizes that table immediately. A changed size is
emitted as one or more HPACK table-size updates at the beginning of the next
encoded block, in the order the changes were made. Assigning the existing size
does not emit an update.

`encode` accepts any of these forms:

- a mapping from string/bytes names to string/bytes values;
- an iterable of two-tuples `(name, value)`;
- an iterable of three-tuples `(name, value, sensitive)` where the third value
  controls whether the field may be indexed; or
- an iterable of `HeaderTuple` or `NeverIndexedHeaderTuple` objects. These
  tuple subclasses must contain exactly two elements and carry the indexing
  decision in `indexable`.

Bytes are preserved. Strings are encoded as UTF-8. Other values, when
accepted by the implementation, are converted with `str(value)` and then
UTF-8 encoded. A mapping is reordered so names beginning with `:` are emitted
before ordinary names; order within each group follows the mapping iteration
order. For a non-mapping iterable the caller's order is preserved, and the
caller is responsible for putting HTTP/2 pseudo-header fields first.

With `huffman=True`, literal names and values use the HPACK Huffman coding
when represented as literals. With `huffman=False`, literal bytes are emitted
without Huffman coding. A perfect static or dynamic table match uses an
indexed representation. A name-only match uses an indexed-name literal. A
normal literal is added to the dynamic table; a sensitive or never-indexed
field is not added. Repeated calls use the same dynamic table and therefore
may produce different blocks for the same headers.

### `Decoder`

```python
from hpack import Decoder

Decoder(max_header_list_size: int = 65536)
Decoder.header_table_size -> int
Decoder.header_table_size = value
Decoder.decode(data: bytes, raw: bool = False) -> list[HeaderTuple]
```

A decoder owns a fresh dynamic table with default size 4096 bytes. It accepts a
complete HPACK header block and returns fields in decoded order. With
`raw=False`, each name and value is decoded as UTF-8. With `raw=True`, the
returned tuple fields remain bytes. Invalid UTF-8 with `raw=False` raises
`HPACKDecodingError`.

The decoder accepts table-size updates only at the beginning of a block and
can consume multiple consecutive updates there. `max_allowed_table_size`
sets the largest table size a peer may announce. If the peer exceeds it, or
does not shrink after the local maximum is reduced, raise
`InvalidTableSizeError`. A table-size update after a header field raises
`HPACKDecodingError`.

`max_header_list_size` limits the decompressed size of one block. Count each
decoded field as `32 + len(name) + len(value)`. If the limit is exceeded, raise
`OversizedHeaderListError`; the decoder is not reusable after that exception.
An invalid static or dynamic table index raises `InvalidTableIndex` (which is
also an `InvalidTableIndexError`). Truncated names, values, Huffman strings,
or integer encodings raise `HPACKDecodingError`.

### Huffman modules

```python
from hpack.huffman import HuffmanEncoder
from hpack.huffman_constants import REQUEST_CODES, REQUEST_CODES_LENGTH
from hpack.huffman_table import decode_huffman

HuffmanEncoder(huffman_code_list: list[int],
               huffman_code_list_lengths: list[int])
HuffmanEncoder.encode(bytes_to_encode: bytes | None) -> bytes
decode_huffman(huffman_string: bytes | bytearray | memoryview | None) -> bytes
```

`REQUEST_CODES` and `REQUEST_CODES_LENGTH` are the 257-entry RFC 7541 request
Huffman tables. `HuffmanEncoder.encode` returns an empty byte string for empty
or falsey input and pads encoded bits with ones to an octet boundary.
`decode_huffman` returns decoded bytes, returns `b""` for empty input, and
raises `HPACKDecodingError` for invalid or incomplete Huffman input.

### Header table module

```python
from hpack.table import HeaderTable, table_entry_size

table_entry_size(name: bytes, value: bytes) -> int
HeaderTable()
HeaderTable.get_by_index(index: int) -> tuple[bytes, bytes]
HeaderTable.add(name: bytes, value: bytes) -> None
HeaderTable.search(name: bytes, value: bytes)
HeaderTable.maxsize -> int
HeaderTable.maxsize = value
```

`table_entry_size` returns `32 + len(name) + len(value)`. `HeaderTable` combines
the RFC 7541 static table and a newest-first dynamic deque. The static table
has 61 entries and `STATIC_TABLE_LENGTH == 61`; indexes are one-based, with
the static table before dynamic entries. Index zero and out-of-range indexes
raise `InvalidTableIndex`.

The default dynamic maximum is 4096. Adding an entry whose size exceeds the
maximum clears the dynamic table. Otherwise the entry is inserted at the
front and the oldest entries are evicted until the current size is within the
maximum. Setting the maximum to zero or a negative value clears the table;
other reductions evict from the oldest end. `dynamic_entries`, `resized`, and
the current-size bookkeeping must reflect these operations.

The `search` result is `None` for no name match, `(index, name, None)` for a
name-only match, and `(index, name, value)` for a perfect match.

## Implementation Notes

- Implement the RFC 7541 representations and the complete 257-symbol Huffman
  table. Do not replace compression with a lookup table containing only the
  examples in this document.
- Preserve state across sequential calls on one `Encoder` or `Decoder`.
  Header-table snapshots used by a diagnostic adapter must be newest first.
- Keep pseudo-header ordering, duplicate header fields, empty values, Unicode,
  arbitrary bytes, sensitive fields, table-size changes, and malformed input
  distinct. Do not normalize duplicate fields into a mapping.
- The public package has a native Python boundary containing bytes, tuple
  subclasses, deque state, and exceptions. If a subprocess or CLI adapter is
  added for testing, use a JSON-safe representation rather than changing the
  native API: represent byte strings as base64 strings, ordered fields as an
  array of records, and `indexable` as an explicit boolean.
- A JSON-safe stateful adapter should execute a bounded sequence of operations
  in one child process so dynamic-table state is not lost between requests.
  It should return encoded blocks, decoded fields, table snapshots, and
  exception type/message as JSON values. Do not use JSON object keys for header
  names because that would lose ordering and duplicate fields.
- A suitable adapter request shape is an object with an `operations` array;
  each operation is one of `encode`, `decode`, `encode_decode`,
  `integer_encode`, `integer_decode`, `huffman_encode`, or `huffman_decode`.
  The exact resource limits and hidden expected values belong to the verifier,
  not this public specification.
- Do not add runtime dependencies merely because pytest, Hypothesis, linters,
  or documentation tools are used during development. Do not include the
  upstream tests or their large fixture corpus in the installed runtime
  package.
