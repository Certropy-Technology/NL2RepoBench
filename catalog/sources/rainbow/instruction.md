## Project Description

Rainbow is a pure-Ruby library for colorizing text printed to ANSI terminals.
Instead of mutating a string, it presents a string through a *presenter* object
whose color and style methods each return a **new** string wrapped in ANSI
Select Graphic Rendition (SGR) escape sequences, so that calls can be chained
and the original text is never modified.

This task covers a deterministic, pure-Ruby subset that is enough to build real
command-line output helpers:

- global enable/disable of colorization;
- independent per-instance wrapper objects that each hold their own state;
- foreground and background color from an ANSI color index, a named ANSI color,
  an RGB triplet, or a hexadecimal color string;
- text style attributes (bright, faint, italic, underline, blink, inverse, hide,
  cross-out, reset) and their aliases;
- composition of already-colorized text, including exact SGR insertion and
  single-trailing-reset behavior;
- removal of SGR sequences from a string.

The implementation must be usable from an empty workspace through
`require "rainbow"` with no third-party runtime gems, no native extensions, and
no network access. All documented results are plain strings with byte-exact
escape sequences; the same input must always produce the same output.

## Natural Language Instruction (Prompt)

Please create a Ruby project named `rainbow` that implements the documented
Rainbow-compatible colorization subset. The project should include the following
functions:

1. Global presenter entry point: a top-level `Rainbow(string)` method returns a
   presenter for that string, and `Rainbow.enabled` / `Rainbow.enabled=` read and
   write the global colorization switch. Every color or style method called on a
   presenter reflects the global switch at the moment the presenter was created.
2. Independent wrapper instances: `Rainbow.new` returns a `Rainbow::Wrapper`
   that starts with a copy of the current global switch and can be enabled or
   disabled on its own through `#enabled` / `#enabled=` without changing the
   global switch or any other wrapper. `#wrap(string)` returns a presenter for
   that string.
3. Color specification: `#color(*)` (aliases `#foreground`, `#fg`) and
   `#background(*)` (alias `#bg`) accept exactly one or exactly three values.
   One value may be an Integer ANSI index, a Symbol ANSI color name, or a
   hexadecimal `String`; three values are an `Integer` RGB triplet in
   `0..255`. Each accepted form has one documented SGR code list.
4. Style attributes: `#reset`, `#bright` (alias `#bold`), `#faint` (alias
   `#dark`), `#italic`, `#underline`, `#blink`, `#inverse`, `#hide`, and
   `#cross_out` (alias `#strike`) each wrap the text in the documented SGR
   code. The eight ANSI color names are also callable as zero-argument methods
   (`#red`, `#blue`, and so on).
5. Enabled/disabled output: when colorization is enabled, methods return the
   documented wrapped string; when it is disabled, every documented color and
   style method returns the text with **no** escape bytes at all, and chaining
   stays safe.
6. Exact composition: applying a method to text that already begins with SGR
   sequences inserts the new sequence after that leading run, and a string that
   already ends with the reset sequence is not reset twice.
7. SGR removal: `Rainbow.uncolor(string)` deletes complete SGR sequences and
   keeps every other byte.
8. Error contract: invalid color specifications raise `ArgumentError`, and
   unknown presenter methods raise `NoMethodError`.
9. Core file requirements: provide a valid `Gemfile`, matching `Gemfile.lock`,
   `rainbow.gemspec`, `lib/rainbow.rb`, `lib/rainbow/version.rb`, and
   `lib/rainbow/` support files that `lib/rainbow.rb` loads. Do not copy the
   upstream repository, upstream tests, verifier files, or reference source into
   the generated project.

## Environment Configuration

### Ruby Version

The project is evaluated on MRI Ruby `3.4.10` with Bundler `2.6.9` on
Linux/amd64.

### Core Dependency Library Versions

```plain
ruby      3.4.10
bundler   2.6.9
```

`rainbow` has **no third-party runtime gem dependencies**. The Ruby standard
library may be used, but standard-library modules are not gem dependencies and
must not be declared as external packages. The verifier installs the candidate
using Bundler in offline mode. Do not use a `GIT`, `PATH`, or plugin dependency
source, native extensions, or runtime network access.

## Rainbow Project Architecture

### Project Directory Structure

Create an installable project with this public structure or an equivalent
standard Ruby Gem layout:

```plain
workspace/
├── Gemfile
├── Gemfile.lock
├── rainbow.gemspec
└── lib/
    ├── rainbow.rb
    └── rainbow/
        ├── color.rb
        ├── global.rb
        ├── null_presenter.rb
        ├── presenter.rb
        ├── string_utils.rb
        ├── version.rb
        └── wrapper.rb
```

`lib/rainbow.rb` is the only required entry point: `require "rainbow"` must
define the top-level `Rainbow` method, the `Rainbow` module functions
`Rainbow.global`, `Rainbow.enabled`, `Rainbow.enabled=`, and `Rainbow.uncolor`,
and `Rainbow.new`. `lib/rainbow/version.rb` must define the `Rainbow::VERSION`
String constant so the gemspec can read it. Supporting Ruby files under
`lib/rainbow/` are loaded by `lib/rainbow.rb`; extra internal files and internal
class names are free as long as the documented public behavior holds. Keep
runtime files inside the project; do not read from an external checkout or write
outside application-requested paths.

### Out Of Scope

The task contract is the behavior documented in this guide. The following
extras are not part of it and an implementation may omit them entirely: the
`rainbow/refinement` and `rainbow/ext/string` alternate activation styles,
large X11/web color-name tables beyond the ten names listed in section 3,
terminal size detection, and any interpretation of the caller's TTY state.

## API Usage Guide

### Core API Imports

```ruby
require "rainbow"

Rainbow(string)          # top-level presenter method
Rainbow.global           # => Rainbow::Wrapper (the global wrapper)
Rainbow.enabled          # => true / false
Rainbow.enabled = value  # set the global switch
Rainbow.uncolor(string)  # => String with SGR sequences removed
Rainbow.new              # => Rainbow::Wrapper (independent instance)
Rainbow::VERSION         # => String
```

### 1. `Rainbow()` - Build A Presenter

```ruby
Rainbow(string) -> presenter (a String)
```

**Parameters**:

- `string` (`Object`): the text to present. Non-`String` values are converted
  with `to_s` before use.

**Return Value**: a presenter that is a `String` subclass, so it can be used
wherever a `String` is expected and can be concatenated with `+`. `#to_s`
returns the wrapped text. The argument is never mutated, and the presenter is a
new object rather than the receiver.

**State dependency**: the presenter inherits the value of `Rainbow.enabled` at
the moment `Rainbow(string)` is called. Later changes to the global switch do not
change an already-created presenter.

**Usage Example**:

```ruby
Rainbow.enabled = true
Rainbow("hello").red
# => "\e[31mhello\e[0m"

Rainbow.enabled = false
Rainbow("hello").red
# => "hello"
```

### 2. `Rainbow.new` / `Rainbow::Wrapper` - Independent Instances

```ruby
Rainbow.new -> Rainbow::Wrapper
wrapper.enabled      -> true / false
wrapper.enabled = v  -> v
wrapper.wrap(string) -> presenter (a String)
```

`Rainbow.new` starts with a copy of the current `Rainbow.enabled`. `#wrap`
behaves exactly like `Rainbow()` but depends only on that wrapper's own switch.
`Rainbow::Wrapper.new` without arguments is enabled by default.

**Usage Example**:

```ruby
Rainbow.enabled = true
one = Rainbow.new
two = Rainbow.new
one.enabled = false

one.wrap("hello").red   # => "hello"
two.wrap("hello").red   # => "\e[31mhello\e[0m"
Rainbow("hello").red    # => "\e[31mhello\e[0m"  (global is still enabled)
```

### 3. `#color` / `#background` - Color Specification

```ruby
presenter.color(*values)       -> presenter (a String)
presenter.foreground(*values)  # alias of #color
presenter.fg(*values)          # alias of #color
presenter.background(*values)  -> presenter (a String)
presenter.bg(*values)          # alias of #background
```

**Parameters**: exactly one or exactly three values.

| Form | Example | SGR codes |
| --- | --- | --- |
| Integer ANSI index | `1` | `[30 + n]` foreground, `[40 + n]` background |
| Symbol ANSI name | `:red` | the name's index, then the same offsets |
| Hexadecimal String | `"#FFC482"` | `[38, 5, code]` / `[48, 5, code]` |
| Integer RGB triplet | `115, 23, 98` | `[38, 5, code]` / `[48, 5, code]` |

The valid ANSI color names and their indices are:

```plain
black 0   red 1   green 2   yellow 3
blue  4   magenta 5  cyan 6  white 7
default 9
```

For an RGB triplet `(r, g, b)` the 256-color palette code is computed with
integer-truncated division:

```plain
domain(v) = (6 * (v / 256.0)).to_i      # truncates toward zero, so 0..5
code      = 16 + 36 * domain(r) + 6 * domain(g) + domain(b)
```

A `String` color is a hexadecimal RGB triplet: an optional leading `#` followed
by exactly six hexadecimal digits (case-insensitive), parsed as two digits per
component (`r` = digits 1-2, `g` = digits 3-4, `b` = digits 5-6) and then
mapped with the same `code` formula as an RGB triplet.

**Return Value**: a new presenter containing the SGR-wrapped text.

**Usage Example**:

```ruby
Rainbow.enabled = true
Rainbow("hello").color(1)          # => "\e[31mhello\e[0m"
Rainbow("hello").color(:red)       # => "\e[31mhello\e[0m"
Rainbow("hello").color(:default)   # => "\e[39mhello\e[0m"
Rainbow("hello").bg(:yellow)       # => "\e[43mhello\e[0m"
Rainbow("hello").background(0)     # => "\e[40mhello\e[0m"
Rainbow("hello").color(115, 23, 98) # => "\e[38;5;90mhello\e[0m"
Rainbow("hello").color("#FFC482")   # => "\e[38;5;223mhello\e[0m"
Rainbow("hello").color("ffc482")    # => "\e[38;5;223mhello\e[0m"
```

**Error contract**: `ArgumentError` is raised when the number of values is not 1
or 3, when a Symbol name is not one of the ten listed names, when any RGB
component is outside `0..255`, or when a `String` is not a valid hexadecimal
triplet. Do not depend on the exception message text.

### 4. Style Attributes

Each method returns a new presenter wrapping the text in one SGR code:

| Method | Alias | SGR code |
| --- | --- | --- |
| `#reset` | - | `0` |
| `#bright` | `#bold` | `1` |
| `#faint` | `#dark` | `2` |
| `#italic` | - | `3` |
| `#underline` | - | `4` |
| `#blink` | - | `5` |
| `#inverse` | - | `7` |
| `#hide` | - | `8` |
| `#cross_out` | `#strike` | `9` |

The eight ANSI color names `#black`, `#red`, `#green`, `#yellow`, `#blue`,
`#magenta`, `#cyan`, `#white` are also zero-argument foreground color methods.

**Usage Example**:

```ruby
Rainbow.enabled = true
Rainbow("hola!").blue.bright.underline
# => "\e[34m\e[1m\e[4mhola!\e[0m"
Rainbow("s").strike    # => "\e[9ms\e[0m"
Rainbow("s").dark      # => "\e[2ms\e[0m"
Rainbow("s").reset     # => "\e[0ms\e[0m"
```

Methods are chainable, and chain order is significant: each call wraps the
result of the previous one, so the SGR sequences appear in call order.

### 5. Deterministic SGR Composition

Wrapping text with codes `c1;c2;...` produces, in order:

1. the leading run of complete SGR sequences already present at the very start
   of the text, unchanged;
2. the new sequence `\e[c1;c2;...m`;
3. the remaining text;
4. a trailing `\e[0m`, **unless** the text already ends with `\e[0m`.

An SGR sequence is `\e[`, zero or more digits and semicolons, then `m`. A
color specification that produces several codes joins them with `;` into a
**single** sequence, as in `\e[38;5;90m`.

**Usage Example**:

```ruby
Rainbow.enabled = true
Rainbow("\e[32mgreen\e[0m").red   # => "\e[32m\e[31mgreen\e[0m"
Rainbow("x\e[0m").red             # => "\e[31mx\e[0m"
Rainbow(Rainbow("x").red).green   # => "\e[31m\e[32mx\e[0m"
Rainbow("A\e[31mB").red           # => "\e[31mA\e[31mB\e[0m"
Rainbow("hello").color(:red).bright # => "\e[31m\e[1mhello\e[0m"
```

Note that an escape sequence in the **middle** of the text is not part of the
leading run and is left where it is.

### 6. Disabled Output

When the controlling switch is off, `Rainbow(string)` and `wrapper.wrap(string)`
return a null presenter: every documented color and style method returns the
text with no escape bytes, and chaining those methods keeps returning the same
unchanged text.

```ruby
Rainbow.enabled = false
Rainbow("hello").red                       # => "hello"
Rainbow("hello").red.bright.bg(:blue)      # => "hello"
Rainbow("hello").red.include?("\e")        # => false
Rainbow("hello").reset                     # => "hello"
```

### 7. `Rainbow.uncolor` - Remove SGR Sequences

```ruby
Rainbow.uncolor(string) -> String
```

**Parameters**:

- `string` (`String`): text that may contain SGR sequences.

**Return Value**: a new `String` with every complete SGR sequence deleted. All
other bytes, including other escape sequences such as `\e[K`, are preserved, and
the result is unchanged when the input contains no SGR sequence or is already
uncolored.

**Usage Example**:

```ruby
Rainbow.uncolor("\e[1;31mA\e[0m B\e[K \e[38;5;90mC")
# => "A B\e[K C"
Rainbow.uncolor("plain")   # => "plain"
Rainbow.uncolor("\e[0m")   # => ""
```

### 8. Unknown Methods

A presenter responds to the documented color and style methods and to nothing
else that is not a `String` method. Calling an unknown method such as
`Rainbow("hello").not_a_color` raises `NoMethodError`, whether or not
colorization is enabled.

## Implementation Notes

- Pure Ruby with byte-exact escape sequences: a presenter returns a new `String`
  wrapped in ANSI SGR codes and never mutates the original text.
- `require "rainbow"` must work from an empty workspace with no third-party
  runtime gem, no native extension, and no network access, backed by `Gemfile`,
  `Gemfile.lock`, `rainbow.gemspec`, `lib/rainbow.rb`, `lib/rainbow/version.rb`,
  and the `lib/rainbow/` support files that `lib/rainbow.rb` loads.
- The global switch is read when a presenter is created, so a color or style
  method reflects `Rainbow.enabled` at that moment. `Rainbow.new` copies the
  global switch into an independent `Rainbow::Wrapper` whose `#enabled=` changes
  neither the global switch nor any other wrapper.
- Color specifications are arity-checked: exactly one Integer ANSI index, Symbol
  ANSI color name, or hexadecimal `String`, or exactly three Integers forming an
  RGB triplet in `0..255`. Each accepted form has one documented SGR code list,
  anything else raises `ArgumentError`, and unknown presenter methods raise
  `NoMethodError`.
- Composition is exact: a new sequence is inserted after an existing leading run
  of SGR sequences, and text that already ends with the reset sequence is not
  reset twice. When colorization is disabled, every documented color and style
  method returns text containing no escape bytes at all and chaining stays safe.
- `Rainbow.uncolor` deletes complete SGR sequences and keeps every other byte.
- The same input must always produce the same output, so no documented result may
  depend on wall-clock time, locale, or random numbers.
- Do not copy the upstream repository, upstream tests, verifier files, or
  reference source into the generated project.
