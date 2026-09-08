# Colorama — ANSI color formatting for terminal output

## Project Description

Build the `colorama` library from an empty workspace. Colorama is a small pure-Python library that lets you emit ANSI escape sequences so that colored text output, cursor movement, and screen/line clearing work in terminals. It provides:

- Named color constants for foreground (`Fore`), background (`Back`), and text attributes (`Style`).
- Low-level ANSI helpers in the `ansi` module.
- A `Cursor` helper for cursor movement and positioning.
- `init()` / `deinit()` / `reinit()` for wrapping `stdout`/`stderr` so colors work on Windows as well as POSIX terminals, plus `just_fix_windows_console()`.
- The `AnsiToWin32` class, which converts ANSI sequences for Windows consoles.

You must produce an installable Python package named `colorama` (version **0.4.6**) whose public API matches the documented behavior below. The package must be importable as `import colorama` and expose the described submodules and constants.

## Supports

- Pure-Python package; no third-party runtime dependencies.
- Requires Python >= 3.7.
- Installable via `pip install .` (the build backend is **hatchling**, with the version read from `colorama/__init__.py`).
- The package installs a top-level `colorama` package with submodules `ansi`, `initialise`, `ansitowin32`, and constants `Fore`, `Back`, `Style`; plus a `Cursor` helper and an `AnsiToWin32` class.

## API Usage Guide

### Module-level constants (`from colorama import Fore, Back, Style`)

Each of `Fore`, `Back`, and `Style` exposes uppercase string constants holding the ANSI escape prefix for that attribute.

- `Fore`: `BLACK`, `RED`, `GREEN`, `YELLOW`, `BLUE`, `MAGENTA`, `CYAN`, `WHITE`, `RESET`, plus `LIGHTBLACK_EX` / `LIGHTRED_EX` / `LIGHTGREEN_EX` / `LIGHTYELLOW_EX` / `LIGHTBLUE_EX` / `LIGHTMAGENTA_EX` / `LIGHTCYAN_EX` / `LIGHTWHITE_EX` for the bright variants.
  - `RED == "\x1b[31m"`, `GREEN == "\x1b[32m"`, `BLUE == "\x1b[34m"`, `YELLOW == "\x1b[33m"`, `BLACK == "\x1b[30m"`, `WHITE == "\x1b[37m"`, `CYAN == "\x1b[36m"`, `MAGENTA == "\x1b[35m"`, `RESET == "\x1b[39m"`.
  - `LIGHTRED_EX == "\x1b[91m"`, `LIGHTGREEN_EX == "\x1b[92m"`, `LIGHTBLUE_EX == "\x1b[94m"`, `LIGHTYELLOW_EX == "\x1b[93m"`, `LIGHTCYAN_EX == "\x1b[96m"`, `LIGHTMAGENTA_EX == "\x1b[95m"`, `LIGHTWHITE_EX == "\x1b[97m"`, `LIGHTBLACK_EX == "\x1b[90m"`.
- `Back`: mirrors `Fore` but for background, so `Back.RED == "\x1b[41m"`, `Back.GREEN == "\x1b[42m"`, `Back.BLUE == "\x1b[44m"`, `Back.YELLOW == "\x1b[43m"`, `Back.BLACK == "\x1b[40m"`, `Back.WHITE == "\x1b[47m"`, `Back.CYAN == "\x1b[46m"`, `Back.MAGENTA == "\x1b[45m"`, `Back.RESET == "\x1b[49m"`, and `LIGHT*_EX` variants up to `\x1b[107m`.
- `Style`: `BRIGHT == "\x1b[1m"`, `DIM == "\x1b[2m"`, `NORMAL == "\x1b[22m"`, `RESET_ALL == "\x1b[0m"`.

### `ansi` module (`from colorama import ansi`)

Provides low-level ANSI helpers.

- `ansi.CSI` — the CSI introducer string `"\x1b["`.
- `ansi.OSC` — the OSC introducer string `"\x1b]";`.
- `ansi.BEL` — the bell character `"\x07"`.
- `ansi.code_to_chars(code)` — given an integer code, returns `CSI + str(code) + "m"`. E.g. `code_to_chars(31) == "\x1b[31m"`.
- `ansi.clear_screen(mode=2)` — returns `CSI + str(mode) + "J"`. `clear_screen() == "\x1b[2J"`, `clear_screen(0) == "\x1b[0J"`, `clear_screen(1) == "\x1b[1J"`.
- `ansi.clear_line(mode=2)` — returns `CSI + str(mode) + "K"`, e.g. `clear_line() == "\x1b[2K"`, `clear_line(0) == "\x1b[0K"`, `clear_line(1) == "\x1b[1K"`.
- `ansi.set_title(title)` — returns `OSC + "0;" + title + BEL`. `set_title("") == "\x1b]0;;\x07"`.
- `ansi.code_to_chars` accepts a numeric string argument as well (e.g. `"31"`).

### `Cursor` class (`from colorama import Cursor`)

Cursor movement/positioning helpers, each returning an ANSI escape string.

- `Cursor.UP(n=1)` — `"\x1b[<n>A"`; `Cursor.UP() == "\x1b[1A"`, `Cursor.UP(3) == "\x1b[3A"`.
- `Cursor.DOWN(n=1)` — `"\x1b[<n>B"`.
- `Cursor.FORWARD(n=1)` — `"\x1b[<n>C"`.
- `Cursor.BACK(n=1)` — `"\x1b[<n>D"`.
- `Cursor.POS(x=1, y=1)` — `"\x1b[<y>;<x>H"`; `Cursor.POS() == "\x1b[1;1H"`, `Cursor.POS(2, 3) == "\x1b[3;2H"`.

### `init` / `deinit` / `reinit` / `just_fix_windows_console`

- `colorama.init(**kwargs)` — callable; accepts `autoreset`, `strip`, `convert`, `wrap`, and `force` flags. On POSIX where wrapping is not needed, it may be a no-op that still must be callable. Passing conflicting options (e.g. `wrap=False` with `convert=True`) raises `ValueError`.
- `colorama.deinit()` — callable; restores the original streams.
- `colorama.reinit()` — callable.
- `colorama.just_fix_windows_console()` — callable; on POSIX it is a safe no-op.
- `colorama.text` — a callable wrapper object that accepts text and color/background/attributes and returns the colored string.

### `AnsiToWin32` class

- `from colorama.ansitowin32 import AnsiToWin32`.
- `AnsiToWin32(stream, convert=None, strip=None, autoreset=False)` — callable constructor. `AnsiToWin32(None)` is valid.
- `write(text)` — writes the text to the underlying stream.
- `should_wrap()` — returns a boolean; on non-Windows it returns `False`.
- `reset_all()` — resets all attributes (returns the reset sequence).
- `convert()` — property accessor for the conversion flag.
- `stream` — the wrapped stream attribute.

## Implementation Notes

- All ANSI strings use `\x1b` (ESC) as the introducer; do not use the literal characters backslash + "0" + "3" + "3".
- The constants are fixed strings; concatenating `Fore` and `Back` (e.g. `Fore.RED + Back.BLUE`) produces the combined escape prefix, and appending text followed by `Style.RESET_ALL` restores the default.
- `code_to_chars`, `clear_screen`, `clear_line`, and `set_title` must produce deterministic, spec-compliant escape strings (never embed runtime state).
- `Cursor` methods must default to `1` (`UP`/`DOWN`/`FORWARD`/`BACK`) or `(1, 1)` (`POS`), and accept an explicit positive integer argument.
- `init`/`deinit`/`reinit`/`just_fix_windows_console` must be importable and callable without side effects that would break the test harness; on a POSIX, non-Windows environment `should_wrap()` returns `False`.
- The package must expose `__version__ == "0.4.6"`.
