# Project Description

Create an installable Python package named `platformdirs` that computes the
standard per-user and shared directories used by applications. The package
must work from a `src/platformdirs/` layout and expose the public convenience
functions and `PlatformDirs` classes described below.

This task freezes a deterministic Linux/Unix slice of the package. The slice
does not require a desktop session, a Windows registry, macOS APIs, Android
runtime modules, or mutation of the host platform. Paths are returned as
strings or `pathlib.Path` objects; callers choose whether directory creation
is enabled.

# Supports

- Support Python 3.10 and newer.
- Install with `python -m pip install -e .` or a normal local build without
  downloading runtime dependencies.
- Use `src/platformdirs/` as the package directory and include a static
  `platformdirs.version` module with `__version__ = "4.11.3"` and
  `__version_tuple__ = (4, 11, 3)`.
- The runtime package uses only the Python standard library.
- On the verification platform, `platformdirs.PlatformDirs` and
  `platformdirs.AppDirs` resolve to the Unix implementation. Do not require
  `sys.platform` mutation to use this contract; the verifier constructs
  `platformdirs.unix.Unix` directly when it needs explicit Unix behavior.
- `ensure_exists=False` is the default and must not create directories.
  `ensure_exists=True` may create only the requested path and its missing
  parents when a directory property or path property is accessed.
- Return JSON-safe observations at the package boundary: directory methods
  return `str`, path properties return `pathlib.Path`, and iterators yield
  strings. The package itself does not need to implement a JSON protocol.

# API Usage Guide

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

# Implementation Notes

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
not import the candidate package in the trusted verifier process.
