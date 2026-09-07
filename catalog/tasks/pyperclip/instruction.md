# pyperclip

## Project Description

Build an installable `pyperclip` project from an empty `workspace/`. The project must reproduce the public, local behavior documented in this instruction, including its package entry points, return shapes, ordering, state changes, and documented exceptions. This is a repository-generation task: the agent creates the build metadata and source modules rather than editing an existing implementation.

Distribution identity: `pyperclip`; public import package begins at `pyperclip`.
The scope is the deterministic local API described below. Network services, undeclared external state, and behavior not represented by the public contract are outside the task.

## Natural Language Instruction

Create the complete project in an empty workspace and make it installable with the command in the environment section. Implement these task-specific capability families from the local API contract:

1. `Primary operations`: expose the documented public entry points, signatures, inputs, outputs, and error behavior.
2. `copy(text)`: preserve the documented object or module behavior, including state and side effects.
3. `paste() -> str`: preserve ordering, determinism, serialization, and boundary semantics where specified.
4. `is_available() -> bool`: make the public package usable through the documented import path or command-line entry.

Do not add speculative APIs or substitute a different package. Keep the implementation self-contained, ensure imports work after installation, and use the exact public names and signatures in the API Usage Guide. A small implementation is acceptable only when it still satisfies every documented contract.

## Supports or Environment Configuration

- CPython 3.12.4 on the pinned Linux image.
- Distribution identity: `pyperclip`; public import package begins at `pyperclip`.
- Install from the workspace with `python -m pip install .`; do not download packages during evaluation.
- Declared build/runtime packages are supplied by the frozen evaluation image: `setuptools==80.10.2`, `wheel==0.45.1`, `pytest==8.3.5`, `iniconfig==2.0.0`, `packaging==24.2`, `pluggy==1.5.0`
- Build metadata and package data must be present in the workspace and agree with the public import paths below.
- Agent, candidate, evaluator, Oracle, and control execution are network-isolated. Do not access GitHub, package registries, DNS, databases, or external services at runtime.
- Use deterministic local inputs. Do not rely on the current wall clock, host-specific absolute paths, undeclared environment variables, or an installed copy of the target package.

## Project Directory Structure

```text
workspace/
├── pyproject.toml
├── package/
│   ├── __init__.py
│   └── (public modules documented in API Usage Guide)
```

The tree lists agent-owned public project files only. Add additional public modules when required by the API Usage Guide, but keep their import paths consistent with package metadata. Do not create evaluator-only files, hidden fixtures, or private reports in the generated project.

## API Usage Guide

The following is the task-specific public contract recovered from the local instruction and inventory. For every function, class, method, constant, export, and command named below, preserve its complete signature, accepted input domain, return type and shape, ordering, determinism, state/side effects, exceptions, and examples. When the source contract gives an optional argument or a compatibility alias, it is part of the required surface.

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

## Implementation Notes

- Keep the root exports and module paths stable after installation; do not make behavior depend on the repository's current directory.
- Preserve explicit ordering guarantees. When the contract does not promise an order, do not introduce a new observable order accidentally.
- Propagate documented exceptions and avoid replacing them with generic errors. Validate malformed, empty, boundary, and repeated inputs as described by the API contract.
- Keep filesystem, process, terminal, and resource effects bounded and local. Close files and other resources on both success and failure.
- Do not copy an upstream checkout, implementation source, or evaluation-only material into the generated project. Implement the public behavior from this specification.

## Examples

The examples below are retained from the local task specification. They are starting points for ordinary calls and boundary/error behavior; their exact output and exception semantics remain governed by the API Usage Guide.

### Example 1: ordinary usage
```text
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

### Example 2: ordinary usage
```text
import pyperclip

assert pyperclip.is_available() is False
try:
    pyperclip.copy("text")
except pyperclip.PyperclipException:
    pass
```

### Example 3: boundary or error behavior
```text
pyperclip.set_clipboard("no")
assert pyperclip.is_available() is True
```

### Example 4: boundary or error behavior
```text
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


## Error Handling and Boundary Conditions

- Empty inputs, invalid types, malformed text or paths, unavailable resources, duplicate calls, and cancellation/timeout cases must follow the exception and return-value contracts documented for the relevant API.
- Do not silently coerce values, reorder results, swallow exceptions, or use a fallback dependency unless the API section explicitly requires that behavior.
- File and environment operations must use caller-provided paths and documented defaults only; never read undeclared host files or network resources.
- The implementation must remain usable in the stated NoNetwork environment. A missing optional integration should expose the documented availability or error behavior rather than attempting an online install.
- Security-sensitive inputs must be treated as data. Do not execute strings, load untrusted code, or interpolate shell commands unless that behavior is explicitly part of the documented public API.
