# termcolor - ANSI Color Formatting Library

## Project Description

`termcolor` is a Python library that provides ANSI color formatting for terminal output. It enables developers to colorize text output with colors, background highlights, and text attributes (bold, italic, underline, etc.) in a cross-platform manner. The library respects standard terminal environment variables like `NO_COLOR` and `FORCE_COLOR`, and automatically detects whether the output stream supports color.

The library is designed for command-line applications, logging systems, and any tool that needs to enhance terminal output with visual formatting. It handles Unicode text correctly, supports both named colors and RGB tuples, and provides both functional and print-based APIs.

**Out of scope**: This library does not provide curses/ncurses functionality, terminal manipulation beyond color formatting, or GUI rendering.

## Natural Language Instruction

Build a Python package named `termcolor` that provides ANSI color formatting for terminal text output. The package must:

1. Export three primary functions: `colored()`, `cprint()`, and `can_colorize()`
2. Export four constant dictionaries: `COLORS`, `HIGHLIGHTS`, `ATTRIBUTES`, and `RESET`
3. Support named colors (red, green, blue, etc.), background highlights (on_red, on_green, etc.), and text attributes (bold, italic, underline, etc.)
4. Support RGB color tuples (0-255 integer triples) for both foreground and background colors
5. Automatically detect terminal color capability via TTY detection
6. Respect environment variables: `NO_COLOR`, `ANSI_COLORS_DISABLED`, `FORCE_COLOR`, and `TERM=dumb`
7. Provide function-level overrides via `no_color` and `force_color` keyword parameters
8. Cache colorization detection results for performance
9. Be installable via `pip install .` and importable as `from termcolor import colored, cprint`

The package name for installation is `termcolor`, and the import name is also `termcolor`.

## Environment Configuration

- **Language**: Python >= 3.10
- **Package Manager**: pip (with setuptools or hatchling build backend)
- **Build System**: PEP 517 compliant (pyproject.toml-based)
- **Runtime Dependencies**: None (standard library only)
- **Test Framework**: pytest (development dependency only)
- **Installation**: Must support `pip install .` from the workspace root

The package must work in offline environments. No network access is required after installation.

## Project Directory Structure

```
workspace/
├── pyproject.toml                 # Build configuration and package metadata
├── README.md                      # Package documentation (optional)
├── src/
│   └── termcolor/
│       ├── __init__.py           # Public exports: colored, cprint, can_colorize, COLORS, etc.
│       └── termcolor.py          # Core implementation module
```

The package must be structured as a `src/` layout with the `termcolor` package under `src/termcolor/`. The `__init__.py` must re-export all public symbols from `termcolor.py`.

## API Usage Guide

### Module: `termcolor`

Import path: `from termcolor import colored, cprint, can_colorize, COLORS, HIGHLIGHTS, ATTRIBUTES, RESET`

#### Constants

**`COLORS: dict[str, int]`**

Dictionary mapping color names to ANSI foreground color codes. Keys include:
- Basic: `"black"`, `"red"`, `"green"`, `"yellow"`, `"blue"`, `"magenta"`, `"cyan"`, `"white"`
- Light variants: `"light_grey"`, `"light_red"`, `"light_green"`, `"light_yellow"`, `"light_blue"`, `"light_magenta"`, `"light_cyan"`
- Dark: `"dark_grey"`
- Aliases: `"grey"` (alias for `"black"`)

Each key maps to an integer ANSI code (30-37, 90-97).

**`HIGHLIGHTS: dict[str, int]`**

Dictionary mapping background highlight names to ANSI background color codes. Keys follow the pattern `"on_<color>"` where `<color>` matches `COLORS` keys, e.g., `"on_red"`, `"on_green"`, `"on_light_blue"`. Each key maps to an integer ANSI code (40-47, 100-107).

**`ATTRIBUTES: dict[str, int]`**

Dictionary mapping attribute names to ANSI attribute codes. Keys include:
- `"bold"` (code 1)
- `"dark"` (code 2)
- `"italic"` (code 3)
- `"underline"` (code 4)
- `"blink"` (code 5)
- `"reverse"` (code 7)
- `"concealed"` (code 8)
- `"strike"` (code 9)

**`RESET: str`**

The ANSI reset sequence `"\033[0m"` used to clear all formatting.

#### Function: `can_colorize`

```python
def can_colorize(
    *,
    no_color: bool | None = None,
    force_color: bool | None = None
) -> bool
```

**Description**: Determines whether color output should be enabled based on function parameters, environment variables, and terminal capabilities.

**Parameters**:
- `no_color` (optional): If `True`, disable color. Takes precedence over environment variables.
- `force_color` (optional): If `True`, enable color. Overridden by `no_color=True`.

**Returns**: `bool` - `True` if color should be applied, `False` otherwise.

**Decision Order** (highest to lowest precedence):
1. `no_color=True` parameter → return `False`
2. `force_color=True` parameter → return `True`
3. `ANSI_COLORS_DISABLED` environment variable set to any value → return `False`
4. `NO_COLOR` environment variable set to any non-empty value → return `False`
5. `FORCE_COLOR` environment variable set to any non-empty value → return `True`
6. `TERM=dumb` environment variable → return `False`
7. `sys.stdout` has no `fileno` attribute → return `False`
8. `os.isatty(sys.stdout.fileno())` returns `True` → return `True`, else `False`

**Caching**: Results are cached using `@functools.cache` decorator. The cache key includes `(no_color, force_color)` parameters but not the text or color arguments.

**Example**:
```python
can_colorize()  # Checks environment and TTY
can_colorize(force_color=True)  # Forces color on
can_colorize(no_color=True)  # Forces color off
```

#### Function: `colored`

```python
def colored(
    text: object,
    color: str | tuple[int, int, int] | None = None,
    on_color: str | tuple[int, int, int] | None = None,
    attrs: Iterable[str] | None = None,
    *,
    no_color: bool | None = None,
    force_color: bool | None = None,
) -> str
```

**Description**: Returns the string representation of `text` wrapped with ANSI color codes. If colorization is disabled (determined by `can_colorize()`), returns the plain string without codes.

**Parameters**:
- `text`: The object to colorize. Converted to string via `str(text)`.
- `color`: Foreground color. Either a string key from `COLORS` (e.g., `"red"`) or an RGB tuple `(r, g, b)` where each component is 0-255.
- `on_color`: Background color. Either a string key from `HIGHLIGHTS` (e.g., `"on_blue"`) or an RGB tuple.
- `attrs`: Iterable of attribute names from `ATTRIBUTES` (e.g., `["bold", "underline"]`).
- `no_color`: Override to disable colorization.
- `force_color`: Override to enable colorization.

**Returns**: `str` - The formatted string with ANSI codes if colorization is enabled, otherwise the plain string.

**Behavior**:
- If `can_colorize()` returns `False`, returns `str(text)` without any codes.
- If `color` is a string, applies the code from `COLORS[color]`.
- If `color` is a tuple `(r, g, b)`, applies ANSI 24-bit RGB foreground: `"\033[38;2;r;g;b m"`.
- If `on_color` is a string, applies the code from `HIGHLIGHTS[on_color]`.
- If `on_color` is a tuple, applies ANSI 24-bit RGB background: `"\033[48;2;r;g;b m"`.
- Each attribute in `attrs` is applied in order.
- The string is always terminated with `RESET` (`"\033[0m"`).

**Example**:
```python
colored("Hello", "red")
# When color enabled: "\033[31mHello\033[0m"
# When color disabled: "Hello"

colored("World", "green", "on_yellow", ["bold"])
# "\033[32m\033[43m\033[1mWorld\033[0m"

colored("RGB", (255, 100, 50))
# "\033[38;2;255;100;50mRGB\033[0m"
```

#### Function: `cprint`

```python
def cprint(
    text: object,
    color: str | tuple[int, int, int] | None = None,
    on_color: str | tuple[int, int, int] | None = None,
    attrs: Iterable[str] | None = None,
    *,
    no_color: bool | None = None,
    force_color: bool | None = None,
    **kwargs: Any,
) -> None
```

**Description**: Prints colorized text to standard output. This is a convenience wrapper around `print(colored(...))`.

**Parameters**: Same as `colored()`, plus:
- `**kwargs`: Additional keyword arguments passed directly to the built-in `print()` function (e.g., `end`, `file`, `sep`, `flush`).

**Returns**: `None`

**Behavior**:
- Calls `colored(text, color, on_color, attrs, no_color=no_color, force_color=force_color)` to generate the formatted string.
- Passes the result and `**kwargs` to `print()`.

**Example**:
```python
cprint("Error!", "red", attrs=["bold"])
cprint("Warning", "yellow", end="!\n")
cprint("Info", "blue", file=sys.stderr)
```

## Implementation Notes

### ANSI Escape Sequence Format

- Foreground named color: `"\033[<code>m<text>\033[0m"` where `<code>` is from `COLORS`
- Background named color: `"\033[<code>m<text>\033[0m"` where `<code>` is from `HIGHLIGHTS`
- Attribute: `"\033[<code>m<text>\033[0m"` where `<code>` is from `ATTRIBUTES`
- RGB foreground: `"\033[38;2;<r>;<g>;<b>m<text>\033[0m"`
- RGB background: `"\033[48;2;<r>;<g>;<b>m<text>\033[0m"`
- Multiple codes can be nested: `"\033[32m\033[43m\033[1mtext\033[0m"`

### Environment Variable Handling

The library must check environment variables in the following precedence:
1. `ANSI_COLORS_DISABLED` - if set to any value (including empty string), disable color
2. `NO_COLOR` - if set to any value (including empty string), disable color
3. `FORCE_COLOR` - if set to any non-empty value, enable color; empty string does not force color
4. `TERM` - if set to `"dumb"`, disable color

Use `os.environ.get()` to check these variables.

### Terminal Detection

The library must detect if the output is a TTY:
1. Check if `sys.stdout` has a `fileno` method (use `hasattr(sys.stdout, "fileno")`)
2. If not, return `False`
3. Try calling `os.isatty(sys.stdout.fileno())`
4. If `OSError` is raised, fall back to `sys.stdout.isatty()` and return its result
5. Otherwise, return the result of `os.isatty()`

### Caching Behavior

The `can_colorize()` function must use the `@functools.cache` decorator (or `@lru_cache(maxsize=None)` for Python < 3.9 compatibility). The cache key is derived only from the `no_color` and `force_color` keyword parameters. Changing the `text`, `color`, or `attrs` arguments to `colored()` should not trigger additional cache entries.

### Type Handling

- `text` parameter: Accept any object and convert to string using `str(text)`
- `color` and `on_color`: Accept `str`, `tuple[int, int, int]`, or `None`
- `attrs`: Accept any iterable of strings or `None`
- RGB tuples: Each integer must be in range 0-255 (no validation required if using specified format)

### Color and Attribute Dictionaries

The exact dictionaries must be:

```python
COLORS = {
    "black": 30, "grey": 30,
    "red": 31, "green": 32, "yellow": 33, "blue": 34, "magenta": 35, "cyan": 36,
    "light_grey": 37, "dark_grey": 90,
    "light_red": 91, "light_green": 92, "light_yellow": 93, "light_blue": 94,
    "light_magenta": 95, "light_cyan": 96, "white": 97,
}

HIGHLIGHTS = {
    "on_black": 40, "on_grey": 40,
    "on_red": 41, "on_green": 42, "on_yellow": 43, "on_blue": 44,
    "on_magenta": 45, "on_cyan": 46, "on_light_grey": 47,
    "on_dark_grey": 100, "on_light_red": 101, "on_light_green": 102,
    "on_light_yellow": 103, "on_light_blue": 104, "on_light_magenta": 105,
    "on_light_cyan": 106, "on_white": 107,
}

ATTRIBUTES = {
    "bold": 1, "dark": 2, "italic": 3, "underline": 4,
    "blink": 5, "reverse": 7, "concealed": 8, "strike": 9,
}

RESET = "\033[0m"
```

### Build Configuration

The `pyproject.toml` must declare:
- `name = "termcolor"`
- `requires-python = ">=3.10"`
- No runtime dependencies (empty `dependencies = []`)
- Package location under `src/termcolor/`
- PEP 517 compliant build backend (setuptools, hatchling, or flit)

### Public Exports

The `src/termcolor/__init__.py` must define `__all__` containing exactly:
```python
__all__ = [
    "ATTRIBUTES",
    "COLORS",
    "HIGHLIGHTS",
    "RESET",
    "can_colorize",
    "colored",
    "cprint",
]
```

## Examples

### Basic Usage

```python
from termcolor import colored, cprint

# Colorize text with a foreground color
print(colored("Hello, World!", "red"))

# Add background color
print(colored("Success", "green", "on_black"))

# Add text attributes
print(colored("Warning", "yellow", attrs=["bold", "underline"]))

# Direct print
cprint("Error", "red", attrs=["bold"])
```

### RGB Colors

```python
from termcolor import colored

# Use RGB tuple for foreground
print(colored("Purple", (128, 0, 128)))

# Use RGB tuple for background
print(colored("Custom", (255, 255, 255), (0, 0, 128)))
```

### Environment Control

```python
import os
from termcolor import colored

# Programmatic control
print(colored("Always plain", "red", no_color=True))
print(colored("Always colored", "blue", force_color=True))

# Environment variable control
os.environ["NO_COLOR"] = "1"
print(colored("Plain due to NO_COLOR", "green"))

del os.environ["NO_COLOR"]
os.environ["FORCE_COLOR"] = "1"
print(colored("Forced color", "magenta"))
```

### Print Function Integration

```python
import sys
from termcolor import cprint

# Use print keyword arguments
cprint("Log entry", "cyan", end=" | ")
cprint("Error", "red", attrs=["bold"], file=sys.stderr)
```

## Error Handling and Boundary Conditions

### Invalid Color or Attribute Names

When a named color, highlight, or attribute is not in the respective dictionary, a `KeyError` will be raised. The implementation should not catch this error; let it propagate to the caller.

### Invalid Types

- If `color` or `on_color` is neither a string, tuple, nor `None`, the behavior is undefined but should not raise an exception during formatting (the value may be ignored or cause a runtime error during string formatting).
- If `attrs` contains non-string items, iteration will proceed but dictionary lookup may fail with `KeyError` or `TypeError`.

### Empty or None Values

- `colored("text", None, None, None)` → returns `"text\033[0m"` (with RESET) if colorization is enabled
- `colored("", "red")` → returns `"\033[31m\033[0m"` if colorization is enabled
- `attrs=[]` → no attributes applied, equivalent to `attrs=None`

### Non-TTY Environment

When the output is not a TTY (e.g., piped to a file, running in CI), `can_colorize()` returns `False` by default, and no ANSI codes are added unless `force_color=True` is used.

### Cache Clearing

The cache for `can_colorize()` persists across calls. Tests that mock environment variables or `sys.stdout` should clear the cache using `can_colorize.cache_clear()` if the function is decorated with `@cache`.

## Security

This library generates ANSI escape sequences based on user input. While ANSI color codes are generally safe, be cautious when:
- Accepting `text`, `color`, or `attrs` from untrusted sources
- Displaying output in contexts where escape sequences could be misinterpreted

The library does not perform input sanitization; it is the caller's responsibility to validate inputs if security is a concern.
