## Project Description

Haml ("HTML Abstraction Markup Language") is an elegant, structured templating
engine for HTML and XML. Instead of writing markup tags by hand and nesting them
visually, a Haml document expresses element structure through **indentation**, so
the template is a tree that reads exactly like the markup it produces. Alongside
markup, a Haml document embeds Ruby code: lines that *emit* a Ruby expression and
lines that only *run* Ruby code.

Your task is to implement a reusable subset of a Haml engine in pure Ruby. Given a
template string, your engine must produce the rendered output string: expand
indented markup into nested elements, evaluate embedded Ruby, apply HTML escaping
rules, serialise attributes, and reject malformed indentation with a dedicated
error class. The rendered result is a plain Ruby `String`; no file I/O, network,
or shell work is involved.

Scope is deliberately bounded to the documented behaviour below. Templates outside
that subset (filters, `%=`-style legacy helpers, Ruby comments with `/#/`,
`<!DOCTYPE>` handling, Tilt/Rails integration, `Haml::Helpers`, whitespace
deviation markers such as `<`/`>`/`~`, and multiline continuation with `|`) are not
part of the contract and may be left unimplemented.

## Natural Language Instruction (Prompt)

1. Create a Ruby library named `haml` in `/workspace` that can be loaded with
   `require "haml"` after adding `lib` to the load path.
2. Define the module `Haml` with at least:
   - `Haml::Template`, the public template object used to render documents;
   - `Haml::Error`, an exception class inheriting from `StandardError`.
3. `Haml::Template.new(options = {}) { template_source }` must accept an options
   Hash (which you may ignore for the documented subset) and a block whose return
   value is the template source. It must not read from disk.
4. `Haml::Template#render(scope = Object.new, locals = {})` must compile and run
   the template and return the complete rendered output as a single `String`. It
   must not print, log, or mutate global state, and repeated calls with equal
   arguments must return equal strings.
5. Implement the document model: each non-blank line is either a tag line, a
   loud-script line, a silent-script line, or plain text. A line indented deeper
   than the previous one becomes a child of the previous line; dedenting closes
   elements. Indentation is measured in spaces (two spaces per level in all
   supported documents).
6. Implement output formatting: every emitted line is terminated by `"\n"`, and
   child content is emitted on its own lines without added indentation.
7. Implement Ruby evaluation for embedded expressions and the escaping rules of
   `=`, `&=` and `!=`, described in the API guide below.
8. Implement attribute serialization for the `%tag{ ... }` hash syntax, keeping the
   author-written order and quoting values with single quotes.
9. Raise `Haml::Error` when the document's indentation is inconsistent with its
   structure, as specified below; do not silently re-indent or guess.
10. Keep the library dependency-free: only the Ruby standard library may be
    required at runtime. `bundle install` must succeed with no gems to download.

## Environment Configuration

- Operating system: Debian bookworm (`linux/amd64`).
- Language runtime: MRI Ruby **3.4.10**.
- Package manager: Bundler **2.6.9**.
- The verifier and the agent both run with **no network access**. No public gem
  may be fetched at test time; a runtime dependency on any third-party gem makes
  the project unusable in this environment and must be avoided.
- The workspace must therefore provide `Gemfile` and `Gemfile.lock` that resolve
  with zero third-party gems, so that `bundle install --local` succeeds offline.
- Rendering is deterministic: no clock, randomness, environment variable,
  filesystem or process interaction may influence the rendered string.

## Haml Project Architecture

### Project Directory Structure

```text
workspace/
├── Gemfile                  # source "https://rubygems.org"; no gem declarations
├── Gemfile.lock             # lockfile with an empty DEPENDENCIES section
└── lib/
    ├── haml.rb              # entry point required by the tests
    └── haml/                # optional internals (parser, compiler, runtime)
        └── ...
```

Requirements implied by that layout:

- `require "haml"` must succeed and define `Haml::Template` and `Haml::Error`.
- `lib/haml.rb` may split its implementation across further files under
  `lib/haml/`, but it must not require any gem outside the Ruby standard library.
- Rendering happens entirely in-process. Do not spawn processes, open sockets, or
  write files during `render`; the verifier treats leftover child processes and
  workspace changes as failures.
- Templates are passed as strings; there is no template lookup path, no caching
  layer, and no on-disk template compilation in this subset.

## API Usage Guide

### `Haml::Error`

```ruby
Haml::Error < StandardError
```

Raised for documents this engine refuses to compile. It is a normal exception
class: callers may rescue it, and subclasses are allowed but must still be
rescuable as `Haml::Error`.

### `Haml::Template.new`

```ruby
Haml::Template.new(options = {}) { template_source } -> Haml::Template
```

- `options` is a Hash of engine options. For the documented subset every key may
  be ignored; the defaults below always apply.
- The block supplies the template source and is called exactly once, at
  construction time. Construction must not raise for the documents in this
  subset; compilation failures surface from `render` as `Haml::Error`.

### `Haml::Template#render`

```ruby
render(scope = Object.new, locals = {}) -> String
```

- Returns the rendered document. The value is a mutable `String`; compare it
  exactly, including newlines.
- `scope` is the object the embedded Ruby evaluates against; `locals` provides
  named variables usable in the template.
- The engine may not raise for a valid document, and returns `""` for a document
  that produces no output.

### Tag lines: `%name`

```ruby
Haml::Template.new { "%span hello" }.render          # => "<span>hello</span>\n"
Haml::Template.new { "%div" }.render                 # => "<div></div>\n"
```

- `%name` opens an element named `name`; text after a single space becomes its
  content, on the same line.
- An empty element renders as `<name></name>` rather than a self-closing tag.
- A tag line with children emits the open tag, the rendered children (each on its
  own line, unindented), then the close tag:

  ```ruby
  Haml::Template.new { "%ul\n  %li Salt\n  %li Pepper" }.render
  # => "<ul>\n<li>Salt</li>\n<li>Pepper</li>\n</ul>\n"
  ```

### Text lines and Ruby interpolation

```ruby
Haml::Template.new { "Plain text" }.render           # => "Plain text\n"
Haml::Template.new { '1#{ 1 + 1 }3' }.render         # => "123\n"
```

- A line that is not a tag or script marker is literal text, emitted verbatim
  followed by `"\n"`.
- `#{ ... }` inside text or inside tag content is evaluated as Ruby and its
  `to_s` is inlined. Interpolation may nest; escaping is **not** applied to text
  lines or interpolated fragments in this subset.

### Loud script: `=`

```ruby
Haml::Template.new { "= 1 + 2" }.render                    # => "3\n"
Haml::Template.new { "%p= 2 * 21" }.render                 # => "<p>42</p>\n"
Haml::Template.new { "%p= '<b>'" }.render                  # => "<p>&lt;b&gt;</p>\n"
Haml::Template.new { "%p&= '<b>'" }.render                 # => "<p>&lt;b&gt;</p>\n"
Haml::Template.new { "%p!= '<b>'" }.render                 # => "<p><b></b></p>\n"
```

- A line beginning with `= ` evaluates the Ruby expression and emits its `to_s`
  followed by `"\n"`.
- `= ` after a tag (`%tag= expr`) emits the value as that tag's content.
- Escaping applies to the string result of a loud script: `&`, `<`, `>` and `'`
  become `&amp;`, `&lt;`, `&gt;` and `&#39;`. Escaping is the default for `=` and
  is forced by `&=`; `!=` disables it and emits the value verbatim.
- `nil` renders as the empty string, and non-String values are converted with
  `to_s` before escaping is considered.

### Silent script: `-`

```ruby
Haml::Template.new { "- total = 2 + 3\n= total" }.render   # => "5\n"
Haml::Template.new { "- if 1 < 2\n  ok" }.render           # => "ok\n"
Haml::Template.new { "- [1, 2].each do |n|\n  = n" }.render
# => "1\n2\n"
```

- A line beginning with `- ` runs Ruby code and emits nothing itself.
- Silent lines support Ruby blocks: the indented lines below them form the block
  body, exactly like a tag's children. Only the block's own emitted output is
  kept, and the closing `end` line contributes no output.

### Attributes: `%tag{ ... }`

```ruby
Haml::Template.new { "%span{ :class => 'foo', id: 'bar' } text" }.render
# => "<span class='foo' id='bar'>text</span>\n"
```

- The Hash literal between braces is evaluated as Ruby (symbol or string keys,
  old hashrocket or Ruby 3 keyword syntax) and must produce a Hash.
- Attributes are emitted in Hash insertion order, each as ` name='value'`, with
  the value escaped for HTML attribute context; `'` becomes `&#39;`.
- `true` renders the attribute name with no value (`<span data-flag>`), while
  `false` and `nil` omit the attribute entirely.
- A `:class` value that is an Array joins its elements with a single space.
- Attribute markup appears before any content, inside the open tag.

### Indentation errors

```ruby
Haml::Template.new { "%body\n  %div\n        %p" }.render
# raises Haml::Error
```

- Indentation defines nesting, so a line that indents more than one level deeper
  than its predecessor, a document that mixes tabs and spaces for indentation, or
  a dedent that matches no previously opened indentation level is a compile-time
  error and must raise `Haml::Error`.
- The error must be raised while compiling the template (before any output is
  produced), and `render` must not return a partial document in that case.

### Determinism and isolation

- `render` depends only on the template source, the scope and the locals. Calling
  it twice on the same object returns equal strings, and one template never
  changes how another template renders.

## Implementation Notes

- The deliverable is an in-process string transformer. `render` returns one
  `String`; it must not print, log, mutate global state, read or write files,
  open sockets, or spawn processes, because the verifier treats leftover child
  processes and workspace changes as failures.
- `require "haml"` is the only supported entry point. `lib/haml.rb` may split its
  internals under `lib/haml/` but must not require any gem outside the Ruby
  standard library.
- `Gemfile` and `Gemfile.lock` must resolve with zero third-party gems so that
  `bundle install --local` succeeds with no network access.
- Indentation is measured in spaces, two per level in all supported documents.
  A line that uses tabs, mixes tabs and spaces, or dedents to a level that was
  never opened raises `Haml::Error` while the template compiles, before any
  output is produced, and `render` must not return a partial document.
- Every emitted line ends with `"\n"`, child content goes on its own lines with
  no added indentation, and serialized attributes keep author-written order with
  single-quoted values.
- Templates are passed as strings, so there is no template lookup path, no
  caching layer, and no on-disk compilation in this subset. Rendering depends
  only on the template source, the scope, and the locals: equal calls return
  equal strings, and one template never changes how another renders.
- Constructs outside the documented subset (filters, `%=`-style legacy helpers,
  `/#/` Ruby comments, `<!DOCTYPE>` handling, Tilt or Rails integration,
  `Haml::Helpers`, the `<`/`>`/`~` whitespace markers, and `|` multiline
  continuations) are out of scope and may be left unimplemented.
