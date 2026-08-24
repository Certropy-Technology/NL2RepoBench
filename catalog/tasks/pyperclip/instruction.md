# Project Description

Create an installable Python project named `pyperclip`. It provides one plain-text clipboard API while selecting an operating-system-specific implementation at runtime. The project must be usable as both the `pyperclip` import package and the `python -m pyperclip` command.

The library is an interface to clipboard mechanisms supplied by the host. It does not provide rich clipboard formats, clipboard history, or a persistent in-process replacement for a missing system clipboard.

# Supports

- Support Python 3.10 and newer.
- Use a `src` layout with the package at `src/pyperclip/`.
- Provide package metadata that supports `python -m pip install -e .` without downloading runtime dependencies.
- Expose `__version__ = "1.11.0"`.
- Keep imports lazy: importing `pyperclip` must not initialize Qt, access a clipboard, or launch a helper process.
- Use only the standard library for the core package. Optional platform backends may use PyObjC, `qtpy`, or PyQt5 when those packages are already installed.
- Handle plain text only. Backend copy functions coerce their argument with `str()` before encoding or writing it.
- The Linux verification environment is intentionally headless. It has no X11 or Wayland display, no `/dev/clipboard`, and no `xclip`, `xsel`, `wl-copy`, `wl-paste`, `klipper`, or `qdbus` executable. Automatic detection there must select the unavailable backend. Do not assume or simulate access to a real desktop clipboard in that environment.

The public module must define the following names, even on platforms where a backend cannot be used:

```python
copy
paste
set_clipboard
determine_clipboard
is_available
lazy_load_stub_copy
lazy_load_stub_paste
init_osx_pbcopy_clipboard
init_osx_pyobjc_clipboard
init_dev_clipboard_clipboard
init_qt_clipboard
init_xclip_clipboard
init_xsel_clipboard
init_wl_clipboard
init_klipper_clipboard
init_no_clipboard
init_windows_clipboard
init_wsl_clipboard
CheckedCall
PyperclipException
PyperclipWindowsException
PyperclipTimeoutException
_executable_exists
ENCODING
```

Set `__all__` to the four primary API names: `copy`, `paste`, `set_clipboard`, and `determine_clipboard`.

# API Usage Guide

## Primary operations

### `copy(text)`

`copy` is initially bound to `lazy_load_stub_copy`. On its first call, the stub obtains `(copy_function, paste_function)` from `determine_clipboard()`, rebinds both module globals, and delegates the call to the selected copy function.

A concrete copy backend coerces `text` with `str(text)`, writes plain text using that backend, and normally returns `None`. Thus values such as integers, booleans, `None`, and lists use their ordinary string representation; do not reject non-string values solely because of their type. Unicode text is encoded as UTF-8 for Unix helper programs, except that WSL uses UTF-16LE for `clip.exe` and Windows uses the Unicode clipboard format.

Clipboard availability and subprocess or OS failures may raise `PyperclipException`, a platform exception, or the underlying process/I/O exception described for that backend. Calling `copy` in a headless environment with no usable mechanism must raise `PyperclipException`; it must not report success after storing text in a private memory variable.

### `paste() -> str`

`paste` is initially bound to `lazy_load_stub_paste`. Its first call performs the same detection and global rebinding as `copy`, then delegates to the selected paste function. Successful backends return plain text as `str`. Calling it with no available mechanism raises `PyperclipException`.

### `is_available() -> bool`

Return `False` exactly while `copy` and `paste` are still the two lazy-load stubs. Return `True` after either automatic or explicit backend binding, including when `set_clipboard("no")` has installed unavailable callables. This reports whether selection has occurred; it does not prove that an external clipboard service is working.

## Backend selection

### `determine_clipboard() -> tuple[callable, callable]`

Return a concrete `(copy, paste)` pair without mutating the module's `copy` and `paste` globals itself. Lazy loading is responsible for assigning the returned pair.

Apply this detection order:

1. On Cygwin, use `/dev/clipboard` only when that path exists and emit a warning that Cygwin support is imperfect.
2. On Windows, use the Windows API backend.
3. On Linux whose `/proc/version` contains `microsoft` case-insensitively, use the WSL backend.
4. On macOS, use PyObjC when both Foundation and AppKit import; otherwise use `pbcopy`/`pbpaste`.
5. When `WAYLAND_DISPLAY` is nonempty and both `wl-copy` and `wl-paste` exist, use the Wayland backend.
6. When `DISPLAY` is nonempty, prefer `xclip`, then `xsel`, then Klipper when both `klipper` and `qdbus` exist. If none exists, try `qtpy`, then PyQt5.
7. Otherwise return `init_no_clipboard()`.

The detector must not choose X11 or Qt merely because a module or executable exists when `DISPLAY` is absent, and must not choose Wayland when either required command is missing.

### `set_clipboard(clipboard) -> None`

Select a backend immediately and replace the module globals `copy` and `paste` with the returned pair. Accepted string values and factories are:

| Value | Factory |
| --- | --- |
| `"pbcopy"` | `init_osx_pbcopy_clipboard` |
| `"pyobjc"` | `init_osx_pyobjc_clipboard` |
| `"qt"` | `init_qt_clipboard` |
| `"xclip"` | `init_xclip_clipboard` |
| `"xsel"` | `init_xsel_clipboard` |
| `"wl-clipboard"` | `init_wl_clipboard` |
| `"klipper"` | `init_klipper_clipboard` |
| `"windows"` | `init_windows_clipboard` |
| `"no"` | `init_no_clipboard` |

Any other value raises `ValueError` with a message that identifies the accepted values. Manual selection does not first check whether the requested external program, display, or optional package is available; initialization or later use may therefore raise the relevant import, process, or OS error.

### `_executable_exists(name) -> bool`

Return whether an executable with the supplied name can be resolved on `PATH`. On supported Python 3 versions this may use `shutil.which`.

## Backend factories

Every `init_*_clipboard()` function returns a two-item `(copy_function, paste_function)` tuple.

### `init_no_clipboard()`

Return two falsey callable objects. Calling either object with any arguments raises `PyperclipException`, which is also a `RuntimeError`. The message must say that no copy/paste mechanism was found and point to Pyperclip's setup guidance. On Linux, append guidance mentioning X11 tools (`xclip` or `xsel`) and `wl-clipboard` for Wayland.

This is the deterministic backend selected by the supplied headless environment. It is an error backend, not a memory clipboard.

### `init_osx_pbcopy_clipboard()`

The copy callable starts `pbcopy` with piped stdin and sends UTF-8 text. The paste callable starts `pbpaste` with piped stdout and decodes UTF-8 output. Close inherited file descriptors for both child processes.

### `init_osx_pyobjc_clipboard()`

Use Foundation and AppKit globals imported during detection. Copy declares the string pasteboard type and writes UTF-8 string data to the general pasteboard. Paste returns the general pasteboard's string value for that type.

### `init_qt_clipboard()`

Import `QApplication` from `qtpy.QtWidgets`, falling back to `PyQt5.QtWidgets`. Reuse `QApplication.instance()` or create `QApplication([])` when none exists. Copy calls the application clipboard's `setText`; paste returns its `text()` result converted to `str`.

### `init_xclip_clipboard()`

Return callables with signatures `copy_xclip(text, primary=False)` and `paste_xclip(primary=False)`. Use selection `c` by default and `p` when `primary=True`. Copy invokes `xclip -selection <selection>` with UTF-8 stdin. Paste invokes `xclip -selection <selection> -o`, captures stdout and stderr, ignores stderr produced for an empty clipboard, and decodes stdout as UTF-8.

### `init_xsel_clipboard()`

Return callables with signatures `copy_xsel(text, primary=False)` and `paste_xsel(primary=False)`. Use `-b` by default and `-p` for primary selection. Copy invokes `xsel <flag> -i` with UTF-8 stdin; paste invokes `xsel <flag> -o` and decodes stdout as UTF-8.

### `init_wl_clipboard()`

Return callables with signatures `copy_wl(text, primary=False)` and `paste_wl(primary=False)`. Add `-p` for primary selection. Nonempty copy text is sent as UTF-8 to `wl-copy`; an empty string invokes `wl-copy --clear` rather than piping content. Paste invokes `wl-paste -n -t text`, optionally with `-p`, and decodes stdout as UTF-8.

### `init_klipper_clipboard()`

Copy invokes `qdbus org.kde.klipper /klipper setClipboardContents` with UTF-8 text. Paste invokes `qdbus org.kde.klipper /klipper getClipboardContents`, decodes UTF-8, verifies the result has Klipper's trailing newline, and removes exactly that final newline.

### `init_dev_clipboard_clipboard()`

Copy opens `/dev/clipboard` as text and writes the coerced string. Warn when the text is empty or contains carriage returns because those cases are imperfect on Cygwin. Paste reads and returns the complete text file content.

### `init_windows_clipboard()`

Use `ctypes` and the Win32 clipboard API with `CF_UNICODETEXT`. Return callables that create a temporary window, retry `OpenClipboard` for up to approximately 0.5 seconds, and always close the clipboard and destroy the window through context managers. Copy empties the clipboard, allocates movable global memory for nonempty text, writes the terminating wide string, and transfers the handle with `SetClipboardData`. Paste returns `""` when no Unicode clipboard handle exists; otherwise it locks, reads, and unlocks the wide string.

### `init_wsl_clipboard()`

Copy invokes `clip.exe` and sends UTF-16LE text. Paste invokes PowerShell without loading a profile, asks it to base64-encode the UTF-8 bytes returned by `Get-Clipboard -Raw`, then decodes base64 and UTF-8. Nonempty PowerShell stderr raises an exception; malformed output raises `RuntimeError` describing the decoding error.

# Exception Contracts

### `PyperclipException`

Subclass `RuntimeError`. It is the common unavailable-clipboard error and base class for Pyperclip-specific platform errors.

### `PyperclipWindowsException`

Subclass `PyperclipException`. Its constructor appends the current `ctypes.WinError()` detail to the supplied operation message.

### `PyperclipTimeoutException`

Subclass `PyperclipException`. The public type must exist for callers even though automatic backend selection does not itself impose a general operation timeout.

### `CheckedCall`

Wrap a ctypes function. Calls delegate to the wrapped function; if the return value is false and `ctypes.get_errno()` is nonzero, raise `PyperclipWindowsException` naming that function. Attribute assignment on the wrapper must be forwarded to the wrapped function so callers can set `argtypes` and `restype`.

# Command-Line Interface

Provide `src/pyperclip/__main__.py` with these behaviors:

- `python -m pyperclip -c TEXT` and `--copy TEXT` copy the single following argument.
- `python -m pyperclip -c` and `--copy` with no following argument read all standard input and copy it.
- `python -m pyperclip -p` and `--paste` write pasted text to standard output without adding a newline.
- Any other invocation prints a short usage message and returns normally.

# Implementation Notes

- Set `ENCODING = "utf-8"` and use it consistently for Unix helper-process I/O.
- Keep backend-specific imports inside initialization or detection paths so importing the module succeeds on every platform.
- Close inherited file descriptors on helper subprocesses.
- Do not initialize a clipboard backend at import time. Initially bind `copy = lazy_load_stub_copy` and `paste = lazy_load_stub_paste`.
- A normal headless use is expected to fail explicitly:

```python
import pyperclip

assert pyperclip.is_available() is False
try:
    pyperclip.copy("text")
except pyperclip.PyperclipException:
    pass
```

- Explicitly installing the unavailable backend changes selection state but not usability:

```python
pyperclip.set_clipboard("no")
assert pyperclip.is_available() is True
```

## Deterministic verification boundary

The verifier may exercise the public functions through a JSON-line fixture adapter. The adapter is external to the package and may provide an in-memory `(copy, paste)` pair through `determine_clipboard`; it must not require a desktop session or persist clipboard data in the library. JSON values sent to that adapter must be converted to ordinary text by the selected copy callable, and the adapter's responses must remain JSON serializable. The package itself must still report the unavailable backend explicitly when no host clipboard mechanism exists.
