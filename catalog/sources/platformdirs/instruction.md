# platformdirs

## Project Description

Build an installable `platformdirs` project from an empty `workspace/`. The project must reproduce the public, local behavior documented in this instruction, including its package entry points, return shapes, ordering, state changes, and documented exceptions. This is a repository-generation task: the agent creates the build metadata and source modules rather than editing an existing implementation.

Distribution identity: `platformdirs`; public import package begins at `platformdirs`.
The scope is the deterministic local API described below. Network services, undeclared external state, and behavior not represented by the public contract are outside the task.

## Natural Language Instruction

Create the complete project in an empty workspace and make it installable with the command in the environment section. Implement these task-specific capability families from the local API contract:

1. `Package exports`: expose the documented public entry points, signatures, inputs, outputs, and error behavior.
2. `Unix directory properties`: preserve the documented object or module behavior, including state and side effects.
3. `XDG environment behavior`: preserve ordering, determinism, serialization, and boundary semantics where specified.
4. `Path properties and convenience functions`: make the public package usable through the documented import path or command-line entry.

Do not add speculative APIs or substitute a different package. Keep the implementation self-contained, ensure imports work after installation, and use the exact public names and signatures in the API Usage Guide. A small implementation is acceptable only when it still satisfies every documented contract.

## Supports or Environment Configuration

- CPython 3.12.14 on the pinned Linux image.
- Distribution identity: `platformdirs`; public import package begins at `platformdirs`.
- Install from the workspace with `python -m pip install .`; do not download packages during evaluation.
- Declared build/runtime packages are supplied by the frozen evaluation image: `setuptools==80.10.2`, `wheel==0.45.1`
- Build metadata and package data must be present in the workspace and agree with the public import paths below.
- Agent, candidate, evaluator, Oracle, and control execution are network-isolated. Do not access GitHub, package registries, DNS, databases, or external services at runtime.
- Use deterministic local inputs. Do not rely on the current wall clock, host-specific absolute paths, undeclared environment variables, or an installed copy of the target package.

## Project Directory Structure

```text
workspace/
├── pyproject.toml
├── a/
│   ├── __init__.py
│   └── (public modules documented in API Usage Guide)
```

The tree lists agent-owned public project files only. Add additional public modules when required by the API Usage Guide, but keep their import paths consistent with package metadata. Do not create evaluator-only files, hidden fixtures, or private reports in the generated project.

## API Usage Guide

The following is the task-specific public contract recovered from the local instruction and inventory. For every function, class, method, constant, export, and command named below, preserve its complete signature, accepted input domain, return type and shape, ordering, determinism, state/side effects, exceptions, and examples. When the source contract gives an optional argument or a compatibility alias, it is part of the required surface.

## Package exports

Provide `AppDirs`, `PlatformDirs`, `PlatformDirsABC`, `__version__`, and
`__version_info__`, together with the public `user_*` and `site_*` convenience
functions and matching `*_path` functions exposed by the package. `AppDirs`
is a backwards-compatible alias of `PlatformDirs`, and the selected Unix
class must be a subclass of `PlatformDirsABC`.

The following public class constructor is required:

```python
PlatformDirs(
    appname: str | None = None,
    appauthor: str | False | None = None,
    version: str | None = None,
    roaming: bool = False,
    multipath: bool = False,
    opinion: bool = True,
    ensure_exists: bool = False,
    use_site_for_root: bool = False,
)
```

`appauthor` is accepted for API compatibility. Unix paths use `appname` and
`version` as path components; `appauthor` does not add an extra Unix path
component. When either `appname` or `version` is absent, omit that component.

## Unix directory properties

`Unix` implements these string properties. A property access may create the
result only when `ensure_exists=True`:

- User directories: `user_data_dir`, `user_config_dir`, `user_cache_dir`,
  `user_state_dir`, `user_log_dir`, `user_runtime_dir`,
  `user_documents_dir`, `user_downloads_dir`, `user_pictures_dir`,
  `user_videos_dir`, `user_music_dir`, `user_desktop_dir`,
  `user_projects_dir`, `user_publicshare_dir`, `user_templates_dir`,
  `user_fonts_dir`, `user_preference_dir`, `user_bin_dir`, and
  `user_applications_dir`.
- Shared directories: `site_data_dir`, `site_config_dir`, `site_cache_dir`,
  `site_state_dir`, `site_log_dir`, `site_runtime_dir`,
  `site_applications_dir`, and `site_bin_dir`.

On Unix, the default bases are:

| Property family | Default base |
| --- | --- |
| user data | `~/.local/share` |
| user config | `~/.config` |
| user cache | `~/.cache` |
| user state | `~/.local/state` |
| user log | user state, with an opinionated `log` child by default |
| site data | `/usr/local/share` and `/usr/share` |
| site config | `/etc/xdg` |
| site cache | `/var/cache` |
| site state | `/var/lib` |
| site log | `/var/log` |
| site runtime | `/run` |
| user applications | `~/.local/share/applications` |
| site applications | `/usr/local/share/applications` and `/usr/share/applications` |
| user fonts | `~/.local/share/fonts` |
| user bin | `~/.local/bin` |
| site bin | `/usr/local/bin` |

Append `appname` and then `version` to the applicable base when they are
provided. With `multipath=True`, `site_data_dir`, `site_config_dir`, and
`site_applications_dir` join all configured shared bases with `os.pathsep`;
the corresponding `*_path` properties select the first item.

`user_preference_dir` is the same path as `user_config_dir`. `opinion=False`
leaves `user_log_dir` at the state directory instead of appending `log`.

## XDG environment behavior

Honor nonblank, surrounding-whitespace-trimmed values of these variables:

- `XDG_DATA_HOME` -> `user_data_dir` and the user fonts/applications bases;
- `XDG_CONFIG_HOME` -> `user_config_dir`;
- `XDG_CACHE_HOME` -> `user_cache_dir`;
- `XDG_STATE_HOME` -> `user_state_dir`;
- `XDG_RUNTIME_DIR` -> both runtime directory properties;
- `XDG_DATA_DIRS` -> the ordered shared data bases;
- `XDG_CONFIG_DIRS` -> the ordered shared config bases.

Split shared directory variables on `os.pathsep`, discard blank or
whitespace-only entries, and preserve the remaining order. An unset, empty,
or separator-only value falls back to the defaults above. `~` in user media
variables is expanded using `HOME`.

The user media properties use `XDG_DOCUMENTS_DIR`, `XDG_DOWNLOAD_DIR`,
`XDG_PICTURES_DIR`, `XDG_VIDEOS_DIR`, `XDG_MUSIC_DIR`, `XDG_DESKTOP_DIR`,
`XDG_PROJECTS_DIR`, `XDG_PUBLICSHARE_DIR`, and `XDG_TEMPLATES_DIR` when set.
Otherwise use the corresponding `user-dirs.dirs` entry under
`$XDG_CONFIG_HOME/user-dirs.dirs` (or `~/.config/user-dirs.dirs`) and expand
`$HOME`; if no entry is available, use `~/Documents`, `~/Downloads`,
`~/Pictures`, `~/Movies`, `~/Music`, `~/Desktop`, `~/Projects`, `~/Public`,
or `~/Templates` as appropriate.

`iter_data_dirs`, `iter_config_dirs`, `iter_cache_dirs`, `iter_state_dirs`,
`iter_log_dirs`, and `iter_runtime_dirs` yield the user directory first and
the shared directory second, except that a multipath shared directory yields
each configured base. The iterator values are strings.

## Path properties and convenience functions

For every `*_dir` property or convenience function in the public slice,
provide a matching `*_path` property or function returning `pathlib.Path`.
The path value represents the same directory string. The convenience
functions accept the same named options as their corresponding constructor
fields and return the selected property for a fresh `PlatformDirs` instance.

## Module command

`python -m platformdirs` must exit successfully and print a deterministic
report beginning with `-- platformdirs 4.11.3 --`. The report must include
the names of the public directory properties for an example application. It
must not require a desktop session or external service.


- Keep platform-specific imports isolated to their modules. The Linux
  verification contract does not require Windows, macOS, or Android native
  APIs to be available.
- Do not replace the directory library with a process-global cache or a
  memory-only fake. Each `PlatformDirs` instance must retain the constructor
  options that determine its output.
- Do not create directories as an import side effect. Creation is opt-in via
  `ensure_exists` and is checked only on the relevant property access.
- Preserve deterministic ordering for multipath values and iterators.
- Avoid including tests, verifier code, or platform-specific native fixtures
  in the package runtime.

The verifier observes the package from a separate child process and compares
only bounded JSON values, path strings, booleans, and command output. It does
not import the candidate package in the separate evaluator process.

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
PlatformDirs(
    appname: str | None = None,
    appauthor: str | False | None = None,
    version: str | None = None,
    roaming: bool = False,
    multipath: bool = False,
    opinion: bool = True,
    ensure_exists: bool = False,
    use_site_for_root: bool = False,
)
```

### Example 2: ordinary usage
```text
PlatformDirs(
    appname: str | None = None,
    appauthor: str | False | None = None,
    version: str | None = None,
    roaming: bool = False,
    multipath: bool = False,
    opinion: bool = True,
    ensure_exists: bool = False,
    use_site_for_root: bool = False,
)
```

### Example 3: boundary or error behavior
```text
PlatformDirs(
    appname: str | None = None,
    appauthor: str | False | None = None,
    version: str | None = None,
    roaming: bool = False,
    multipath: bool = False,
    opinion: bool = True,
    ensure_exists: bool = False,
    use_site_for_root: bool = False,
)
```

### Example 4: boundary or error behavior
```text
PlatformDirs(
    appname: str | None = None,
    appauthor: str | False | None = None,
    version: str | None = None,
    roaming: bool = False,
    multipath: bool = False,
    opinion: bool = True,
    ensure_exists: bool = False,
    use_site_for_root: bool = False,
)
```


## Error Handling and Boundary Conditions

- Empty inputs, invalid types, malformed text or paths, unavailable resources, duplicate calls, and cancellation/timeout cases must follow the exception and return-value contracts documented for the relevant API.
- Do not silently coerce values, reorder results, swallow exceptions, or use a fallback dependency unless the API section explicitly requires that behavior.
- File and environment operations must use caller-provided paths and documented defaults only; never read undeclared host files or network resources.
- The implementation must remain usable in the stated NoNetwork environment. A missing optional integration should expose the documented availability or error behavior rather than attempting an online install.
- Security-sensitive inputs must be treated as data. Do not execute strings, load untrusted code, or interpolate shell commands unless that behavior is explicitly part of the documented public API.
