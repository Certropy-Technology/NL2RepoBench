## Project Description

Tilt is a generic Ruby interface to many template engines. It maps file
extensions to template implementation classes, loads template source either
from a file or from an in-memory string, compiles that source once, and then
renders it inside an arbitrary Ruby scope with local variables and an optional
block. Because the engines themselves are optional, the generic layer can be
exercised entirely with the built-in `StringTemplate`, which treats its data as
a Ruby double-quoted string supporting `#{}` interpolation.

This task reimplements a bounded, deterministic, pure-Ruby subset of that
generic interface: template registration through an extension mapping, template
instantiation from a string or file source, compilation-and-render with locals,
evaluation inside a caller-supplied scope object, support for `yield` into a
block, a simple template cache, and the source-argument contract that a
template must be built from a file or a block. It must not contact network
services or depend on any native or external template-engine gem.

## Natural Language Instruction (Prompt)

Please create a Ruby project named `tilt` that implements the documented
Tilt-compatible generic template interface. The project should include the
following functions:

1. Generic template base class `Tilt::Template`. Its constructor
   `Tilt::Template.new(file = nil, line = nil, options = nil) { |template| ...
   }` loads template source from the block's return value when a block is
   given, or from the file on disk otherwise. When neither `file` nor a block
   is supplied it raises `ArgumentError`. Expose the loaded template source
   through the `#data` reader, the source path through `#file`, and the
   engine options through `#options` (a Hash, defaulting to empty).
2. `Tilt::StringTemplate`, a subclass of `Tilt::Template` whose data is
   evaluated as a Ruby string, so `#{...}` interpolation is performed at
   render time. It is available after `require "tilt/string"`.
3. `#render(scope = nil, locals = nil, &block)` compiles the template once and
   evaluates it, returning the resulting `String`. The template body runs as if
   inside the `scope` object: instance variables and methods of `scope` are
   visible to `#{}` interpolation. When `scope` is omitted, evaluation happens
   in a fresh plain object. Each key of the `locals` hash becomes a local
   variable of the same name during evaluation. If a block is given, the
   template may call `yield` to insert the block's return value. Rendering the
   same template more than once returns the same string and reuses the
   compiled body.
4. `Tilt::Mapping`, the extension-to-class registry, with
   `#register(template_class, *extensions)`, `#registered?(extension)`, and
   `#[](name_or_file)`. `#[]` returns the class registered for an extension
   when given a bare extension such as `"foo"`, and also matches the last
   extension of a longer name such as `"hello.foo"`; it returns `nil` when no
   registered extension matches. Registering a class under several extensions
   maps each of them to that same class.
5. The module-level `Tilt` interface `Tilt.register`, `Tilt.[]`,
   `Tilt.registered?`, and `Tilt.new`, which delegate to a shared default
   mapping; `Tilt.new(file, line = nil, options = nil, &block)` selects the
   template class for the file extension and instantiates it, forwarding the
   arguments and block.
6. `Tilt::Cache`, a small template cache whose `#fetch(*key)` returns the value
   produced by the block for a key on the first call and the identical cached
   object on every later call for the same key, with `#clear` resetting it.
7. Core file requirements: provide a valid `Gemfile`, matching
   `Gemfile.lock`, gemspec, `lib/tilt.rb`, `lib/tilt/template.rb`,
   `lib/tilt/mapping.rb`, and `lib/tilt/string.rb`. The package must load with
   `require "tilt"` and `require "tilt/string"` on Ruby 3.4. Do not copy the
   upstream repository, upstream tests, verifier files, or reference source
   into the generated project, and do not add any third-party runtime gem
   dependency.

## Environment Configuration

### Ruby Version

The project is evaluated on MRI Ruby `3.4.10` with Bundler `2.6.9` on
Linux/amd64.

### Core Dependency Library Versions

```plain
ruby      3.4.10
bundler   2.6.9
```

The required implementation is pure Ruby with no runtime gem dependencies. The
Ruby standard library may be used, but standard-library modules are not gem
dependencies and must not be declared as external packages. The verifier
installs the candidate with Bundler in offline mode from an empty gem cache. Do
not use a `GIT`, `PATH`, or plugin dependency source, native extensions, or
runtime network access, and do not depend on a preinstalled copy of Tilt or any
external template engine.

## Tilt Project Architecture

### Project Directory Structure

Create an installable project with this public structure or an equivalent
standard Ruby Gem layout:

```plain
workspace/
├── Gemfile
├── Gemfile.lock
├── tilt.gemspec
└── lib/
    ├── tilt.rb
    └── tilt/
        ├── template.rb
        ├── mapping.rb
        └── string.rb
```

`lib/tilt.rb` defines the `Tilt` module, its default mapping delegation, the
`Tilt::Mapping` registry, and the `Tilt::Cache`, and loads `tilt/template` and
`tilt/mapping`. `lib/tilt/template.rb` defines `Tilt::Template`.
`lib/tilt/string.rb` defines `Tilt::StringTemplate` as a subclass of
`Tilt::Template` and must be loadable on its own via `require "tilt/string"`.
Additional internal Ruby files are allowed when they are loaded by these public
entry points. Keep all runtime files inside the project; do not read template
data from an external checkout and do not write outside application-requested
paths.

## API Usage Guide

### Core API Imports

```ruby
require "tilt"
require "tilt/string"

Tilt
Tilt::Template
Tilt::StringTemplate
Tilt::Mapping
Tilt::Cache
```

### 1. `Tilt::Template` - Generic base class

```ruby
Tilt::Template.new(file = nil, line = nil, options = nil) { |template| ... }
```

**Parameters**:

- `file` (`String` or `nil`): path whose contents provide the template data.
- `line` (`Integer` or `nil`): starting line number for backtraces; defaults to
  `1`.
- `options` (`Hash` or `nil`): engine options, exposed unchanged through
  `#options`; defaults to an empty Hash.

**Block**: When a block is given it receives the template instance and its
String return value becomes the template data instead of reading `file`.

**Return Value**: a new template instance.

**Error contract**: raising `ArgumentError` is required when neither `file` nor
a block is supplied (message conventionally `"file or block required"`).

```ruby
template = Tilt::Template.new("/tmp/view.str")          # reads file data
inline = Tilt::Template.new { |t| "Hello World!" }     # block supplies data
inline.data                                            # => "Hello World!"
inline.render                                          # => "Hello World!"
```

### 2. `Tilt::StringTemplate` - String source behavior

`Tilt::StringTemplate` is a `Tilt::Template` whose data is treated as a Ruby
double-quoted string, so `#{...}` interpolation is evaluated at render time in
the rendering scope.

```ruby
Tilt::StringTemplate.new { "Hello World!" }.render
# => "Hello World!"
Tilt::StringTemplate.new { "Hello\nWorld!\n" }.render
# => "Hello\nWorld!\n"        (exact bytes, 13 bytes total)
```

Reading `#data` returns the un-evaluated source string exactly as supplied:

```ruby
Tilt::StringTemplate.new { "abc" }.data   # => "abc"
```

### 3. `#render` - Locals, scope, block, and reuse

```ruby
template.render(scope = nil, locals = nil, &block) -> String
```

**Parameters**:

- `scope` (`Object` or `nil`): object used as `self` while evaluating the
  template body. When `nil`, evaluation uses a fresh plain object so that only
  `locals`, `yield`, and Ruby built-ins resolve.
- `locals` (`Hash` or `nil`): each `Symbol` or `String` key becomes a local
  variable of that name holding the corresponding value.

**Block**: When given, `yield` inside the template body returns the block's
result.

**Return Value**: the rendered `String`. Rendering is idempotent: calling
`#render` repeatedly on the same instance yields the same string, and the
compiled body is reused rather than re-parsed.

```ruby
Tilt::StringTemplate.new { "Hey #{name}!" }.render(Object.new, name: "Joe")
# => "Hey Joe!"

scope = Object.new
scope.instance_variable_set(:@name, "Joe")
Tilt::StringTemplate.new { "Hey #{@name}!" }.render(scope)
# => "Hey Joe!"

Tilt::StringTemplate.new { "Hey #{yield}!" }.render { "Joe" }
# => "Hey Joe!"
```

### 4. `Tilt::Mapping` - Engine registration and lookup

```ruby
mapping = Tilt::Mapping.new
mapping.register(template_class, *extensions) -> nil
mapping.registered?(extension) -> true | false
mapping[name_or_file] -> template_class | nil
```

**Parameters**:

- `template_class` (`Class`): any class; the mapping stores and returns it
  unchanged.
- `extensions` (`String`, one or more): file extensions such as `"foo"`.

**`#[]` behavior**: `mapping["foo"]` returns the class registered under
`"foo"`; `mapping["hello.foo"]` matches on the trailing extension `"foo"` and
returns the same class; `mapping["foo.baz"]` returns `nil` when `"baz"` is not
registered.

```ruby
stub = Class.new
mapping.register(stub, "foo", "bar")
mapping["foo"]          # => stub
mapping["hello.foo"]    # => stub
mapping["foo.baz"]      # => nil
mapping.registered?("bar")   # => true
mapping.registered?("baz")   # => false
```

### 5. Module-level `Tilt` delegation

`Tilt.register`, `Tilt[]`, `Tilt.registered?`, and `Tilt.new` forward to a
single shared default `Tilt::Mapping`. `Tilt.new(file, line = nil, options =
nil, &block)` looks up the class for `file`'s extension and instantiates it
with the same arguments; it raises when no class is registered for that file.

```ruby
Tilt["str"]   # => Tilt::StringTemplate  (after require "tilt/string")
```

### 6. `Tilt::Cache` - Template cache

```ruby
cache = Tilt::Cache.new
cache.fetch(*key) { value } -> Object
cache.clear -> void
```

`#fetch` evaluates the block only on the first call for a given key and caches
its result; every later `#fetch` for the same key returns the identical cached
object, so `first.equal?(second)` is `true`. The block may legitimately return
`nil`, which is also cached. `#clear` discards all cached entries.

```ruby
cache = Tilt::Cache.new
template = Tilt::StringTemplate.new { "" }
a = cache.fetch("greet") { template }
b = cache.fetch("greet") { Object.new }
a.equal?(template) && b.equal?(template)   # => true
```

## Implementation Notes

- Everything happens in-process: no network access, and no native or external
  template-engine gem may be required. The generic layer is exercised through the
  built-in `Tilt::StringTemplate`, which evaluates its data as a Ruby
  double-quoted string so `#{}` interpolation happens at render time.
- Loading contract: `require "tilt"` and `require "tilt/string"` must work on
  Ruby 3.4 from `lib/tilt.rb`, `lib/tilt/template.rb`, `lib/tilt/mapping.rb`, and
  `lib/tilt/string.rb`, with a `Gemfile`/`Gemfile.lock` pair that declares no
  third-party runtime gem so offline `bundle install --local` succeeds.
- A template must be built from a file or from a block: `Tilt::Template.new`
  given neither raises `ArgumentError`, and `#data`, `#file`, and `#options`
  expose the loaded source, its path, and a Hash of engine options that defaults
  to empty.
- Source is compiled once and the compiled body is reused, so rendering the same
  template more than once returns the same string. `#render` evaluates the body
  as if inside the supplied `scope` object (a fresh plain object when omitted),
  binds each `locals` key as a local variable of that name, and yields to a given
  block.
- Extension lookup maps a bare extension such as `"foo"` and also matches the
  last extension of a longer name such as `"hello.foo"`, returning `nil` when
  nothing registered matches; registering one class under several extensions maps
  each of them to that same class. `Tilt.register`, `Tilt.[]`,
  `Tilt.registered?`, and `Tilt.new` delegate to a shared default mapping.
- `Tilt::Cache#fetch(*key)` returns the block's value on the first call and the
  identical cached object on every later call for the same key, and `#clear`
  resets it.
- No documented result may depend on wall-clock time, locale, environment, or the
  current working directory.
- Do not copy the upstream repository, upstream tests, verifier files, or
  reference source into the generated project.
