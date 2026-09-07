## Project Description

RubyZip is a pure-Ruby library for reading and writing ZIP archives. It models an
archive as a set of named entries, each carrying uncompressed size, a CRC-32
checksum, a compression method, and optional comment, and it exposes two stream
families for authoring and reading archives either on the filesystem or entirely
in memory. This task covers a deterministic, in-memory subset of that public
surface: creating archives, enumerating and reading entries, inspecting per-entry
compression metadata and checksums, streaming an entry's bytes, directory entries,
and the error contract for a missing entry.

The implementation must be loadable with `require "zip"`, work with the Ruby
standard library only, run from an empty workspace, and behave identically across
repeated runs. It must not contact network services or depend on native extensions.

## Natural Language Instruction (Prompt)

Please create a Ruby project named `rubyzip` that implements the documented
RubyZip-compatible archive API. The project should include the following
functions:

1. Archive authoring: `Zip::OutputStream.write_buffer(io) { |zos| ... }` accepts a
   writable IO (a `StringIO` in this task), yields a stream on which
   `put_next_entry(name)` starts a new entry and `write(bytes)` appends data to
   the current entry, and returns an IO whose `string` is the completed ZIP
   archive bytes; read the archive from the returned object. Each written entry must record its uncompressed `size`, its
   CRC-32 `crc`, and its `compression_method`.
2. In-memory archive reading: `Zip::File.open_buffer(io) { |zf| ... }` parses a ZIP
   archive held in a `StringIO`, yields a `Zip::File` handle, and supports
   enumerating entries with `each`/`entries` (in stored order), looking up a single
   entry with `get_entry`/`find_entry`, reading a whole entry with `read`, and
   streaming an entry with `get_input_stream(name) { |is| ... }`.
3. Entry naming and paths: entry names preserve the exact relative path strings
   used at authoring time, including nested separators (`"dir/a.txt"`) and
   trailing-slash directory markers (`"folder/"`). Directory entries created via
   `put_next_entry("folder/")` are reported with that trailing slash and may carry
   no data. Entry `name` returns the stored name unchanged.
4. Compression methods and metadata: writing an entry with the default method uses
   DEFLATE; an entry can also be authored with the STORED (no compression) method.
   Reading back an entry must report the matching `compression_method` integer
   (`STORED == 0`, `DEFLATED == 8`), the correct uncompressed `size`, and the
   standard CRC-32 (IEEE, as produced by `Zlib.crc32`) of the entry's contents.
5. Error and absence contract: `find_entry` returns `nil` for a name that is not
   present, while `get_entry` raises an `Errno::ENOENT` for the same missing name.
   Reading or streaming a present entry returns exactly the bytes written.

## Environment Configuration

### Ruby Version

The project is evaluated on MRI Ruby `3.4.10` with Bundler `2.6.9` on
Linux/amd64.

### Core Dependency Library Versions

```plain
ruby      3.4.10
bundler   2.6.9
```

The required implementation is pure Ruby with no external Gem dependencies. It may
use only the Ruby standard library (for example `stringio`, `zlib`, `fileutils`,
`tempfile`, `delegate`, `singleton`, `English`, and `rbconfig`); standard-library
modules are not Gem dependencies and must not be declared as external packages in
the `Gemfile`. The verifier installs the candidate with Bundler in offline mode
against an empty dependency set, so the `Gemfile` must declare no runtime gems and
the `Gemfile.lock` must carry no runtime `specs`. Do not use a `GIT`, `PATH`, or
plugin dependency source, native extensions, or runtime network access.

## RubyZip Project Architecture

### Project Directory Structure

Create an installable project with this public structure or an equivalent standard
Ruby Gem layout:

```plain
workspace/
├── Gemfile
├── Gemfile.lock
├── rubyzip.gemspec
└── lib/
    ├── zip.rb
    └── zip/
        ├── version.rb
        ├── constants.rb
        ├── entry.rb
        ├── entry_set.rb
        ├── central_directory.rb
        ├── file.rb
        ├── output_stream.rb
        ├── input_stream.rb
        ├── decompressor.rb
        ├── compressor.rb
        ├── inflater.rb
        └── deflater.rb
```

`lib/zip.rb` is the public entry point required by `require "zip"`; it defines the
`Zip` module and loads the supporting files under `lib/zip/`. The exact split among
the supporting files is an implementation detail, as long as `require "zip"` loads
the public classes and constants described below. Keep all runtime code inside the
project's `lib/`; do not read from an external checkout or require a preinstalled
copy of rubyzip.

## API Usage Guide

### Core API Imports

```ruby
require "zip"

Zip::File
Zip::Entry
Zip::OutputStream

Zip::Entry::STORED    # => 0
Zip::Entry::DEFLATED  # => 8
```

All archive work in this task happens through in-memory `StringIO` buffers; no
filesystem paths are required by the scored contract.

### 1. `Zip::OutputStream.write_buffer(io) { |zos| ... }` - Author an Archive

**Function**: Build a complete ZIP archive in memory.

```ruby
Zip::OutputStream.write_buffer(io) { |zos| ... } -> io
```

**Parameters**:

- `io` (`StringIO`): a writable buffer to receive the archive bytes.

**Return Value**: a writable IO whose `string` is the finished archive. Use
the returned object rather than assuming the passed-in `io` was mutated.

Inside the block, call `zos.put_next_entry(name, comment = '', extra = ...,
compression_method = Zip::Entry::DEFLATED, level = ...)` to begin an entry and
`zos.write(data)` to append bytes to the current entry. Omitting
`compression_method` selects DEFLATE; passing `Zip::Entry::STORED` stores bytes
uncompressed. A directory entry is created with a trailing-slash name such as
`"folder/"` and may receive no writes. Each authored entry must record the exact
name, the total uncompressed `size` written to it, the CRC-32 of those bytes, and
the compression method actually used.

### 2. `Zip::File.open_buffer(io) { |zf| ... }` - Read an Archive

**Function**: Parse a ZIP archive held in a buffer and yield a `Zip::File` handle.

```ruby
Zip::File.open_buffer(io) { |zf| ... } -> Object
```

**Parameters**:

- `io` (`StringIO`): a readable buffer containing archive bytes.

**Return Value**: not specified by this contract - compute every result you
need inside the block (with the standard implementation the block's value is
not propagated to the caller).

The handle supports the reading and inspection operations described below. Entries
are reported in the order stored in the archive.

#### 2.1 `entries` / `each` - Enumerate Entries

```ruby
zf.entries() -> Array<Zip::Entry>
zf.each { |entry| ... } # yields each Zip::Entry in stored order
```

`zf.entries.map(&:name)` returns the stored names in order. The number of entries
is `zf.entries.size`.

#### 2.2 `read(name)` - Read a Whole Entry

```ruby
zf.read(entry) -> String
```

**Parameters**:

- `entry` (`String` or `Zip::Entry`): the entry name or object to read.

**Return Value**: the full decompressed bytes of that entry as a `String`.

#### 2.3 `get_input_stream(name) { |is| ... }` - Stream an Entry

```ruby
zf.get_input_stream(entry) { |is| ... } -> Object
```

**Parameters**:

- `entry` (`String` or `Zip::Entry`): the entry to open for reading.

**Return Value**: the block's return value; the yielded `is` responds to `read`,
returning the entry's decompressed bytes.

#### 2.4 `find_entry` / `get_entry` - Look Up a Single Entry

```ruby
zf.find_entry(name) -> Zip::Entry | nil
zf.get_entry(name)  -> Zip::Entry
```

**Parameters**:

- `name` (`String`): the entry name.

`find_entry` returns `nil` when the name is absent. `get_entry` returns the entry
when present and raises `Errno::ENOENT` when absent. A returned entry exposes
`name`, `size` (uncompressed byte count), `crc` (CRC-32 integer), and
`compression_method` (`0` for STORED, `8` for DEFLATED).

### Worked Example

```ruby
require "stringio"
require "zip"

archive = Zip::OutputStream.write_buffer(StringIO.new) do |zos|
  zos.put_next_entry("dir/a.txt")
  zos.write "hello"
  zos.put_next_entry("stored.bin", '', nil, Zip::Entry::STORED)
  zos.write "AAAA"
end.string

Zip::File.open_buffer(StringIO.new(archive)) do |zf|
  zf.entries.map(&:name)               # => ["dir/a.txt", "stored.bin"]
  zf.read("dir/a.txt")                 # => "hello"
  e = zf.get_entry("stored.bin")
  [e.size, e.crc, e.compression_method] # => [4, 2601322737, 0]
end
```

The CRC-32 value is the standard IEEE CRC-32 of the entry's uncompressed bytes
(equal to `Zlib.crc32("AAAA")` above). All operations must be deterministic and
must not depend on locale, wall-clock time, random state, the filesystem, or
network access. The scored contract covers the operations shown in this guide;
unrelated upstream rubyzip surface (encryption, filesystem overlays, on-disk
`Zip::File.open`, archive comments, and entry `extract`) is outside this task.

## Implementation Notes

- Pure Ruby only: no native extensions, no third-party runtime gem, and no
  network access. The library must load with `require "zip"` from an empty
  workspace using only the Ruby standard library.
- This subset works entirely on in-memory archives: `Zip::OutputStream.write_buffer`
  and `Zip::File.open_buffer` are exercised with a `StringIO`, and the object
  returned by authoring is the same object the reader consumes.
- Every written entry records its uncompressed `size`, its CRC-32 (`IEEE`, as
  produced by `Zlib.crc32`), and its `compression_method`, where `STORED == 0`
  and `DEFLATED == 8`; the default write method is DEFLATE.
- Entry names are stored and returned unchanged, including nested separators such
  as `"dir/a.txt"` and trailing-slash directory markers such as `"folder/"`, and
  enumeration by `each`/`entries` follows stored order. A directory entry may
  carry no data.
- Absence splits by method: `find_entry` returns `nil` for a name that was not
  written, while `get_entry` raises `Errno::ENOENT` for that same name. Reading
  or streaming a present entry returns exactly the bytes written.
- Behaviour must be identical across repeated runs, so nothing may depend on
  filesystem state outside the project, wall-clock time, locale, or hash ordering.
- Do not copy the upstream repository, upstream tests, verifier files, or
  reference source into the generated project.
