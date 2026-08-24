# Project Description

Create a Python 3 project named `autojump`: a smart directory navigation
utility for terminal users. It maintains a weighted directory database,
selects paths from ordered search terms, and provides shell integration for
commands such as `j`, `jc`, and `jo`.

The project must work from an empty workspace and must preserve paths as the
user entered them. It should be usable without a network service or a
third-party runtime dependency.

## Supports

- Provide the implementation modules under `bin/`, the shell integration
  files, `tools/autojump_ipython.py`, `install.py`, and `uninstall.py`.
- Python 3.12 on Debian 12.
- The repository root must be installable with a standard offline
  `pip install .` (PEP 517 or legacy source install), so include packaging
  metadata such as `pyproject.toml` that declares the `bin` and `tools`
  packages. Build requirements must resolve without network access.
- `python install.py` is the supported manual installation command. It must
  work in a clean POSIX shell environment and support dry-run, user, custom,
  and system installation modes exposed by its command-line parser.
- Keep the implementation importable directly from the repository, including
  as a top-level `autojump_utils`, `autojump_match`, `autojump_data`, and
  `autojump` module when the `bin/` directory is on `sys.path`. The project
  may use only Python's standard library at runtime; test-only tools are not
  runtime dependencies.
- Store the directory database as tab-separated `weight<TAB>path` records in
  the platform-appropriate user data directory. Handle UTF-8 paths and paths
  containing spaces.
- Provide shell scripts for the supported shells and an IPython helper. Shell
  commands should quote paths safely and should not require a network service.

## API Usage Guide

### Directory Database: `bin.autojump_data`

Expose `BACKUP_THRESHOLD` and `Entry`, where `Entry` has `path` and `weight`
fields. Implement:

- `load(config) -> dict[str, float]`: read `config['data_path']`; return an
  empty mapping when it does not exist, ignore malformed records, and recover
  from the configured backup after an I/O or end-of-file error.
- `save(config, data) -> None`: create the parent directory, persist all
  path/weight pairs, replace the data file atomically, and create or refresh
  `config['backup_path']` when the backup is absent or older than
  `BACKUP_THRESHOLD`.
- `dictify(entries) -> dict`: map each `Entry.path` to its weight.
- `entriefy(data) -> iterator[Entry]`: convert mapping items to `Entry` values.
- `load_backup(config) -> dict` and `migrate_osx_xdg_data(config) -> None` for
  backup recovery and migration from the old macOS XDG location.

### Matching: `bin.autojump_match`

Expose `match_anywhere(needles, haystack, ignore_case=False)`,
`match_consecutive(needles, haystack, ignore_case=False)`, and
`match_fuzzy(needles, haystack, ignore_case=False, threshold=0.6)`. Each
returns an iterator of the original `Entry` values in input order.

- `match_anywhere` requires every needle to occur in the path in the supplied
  order, but permits other characters and path components between needles.
- `match_consecutive` requires the supplied needles to match path components
  in order at the end of the path; characters inside a component may vary.
- Matching honors `ignore_case`, handles Unicode, and treats literal wildcard
  characters in a needle as ordinary characters.
- `match_fuzzy` compares the final path component with the final needle and
  returns entries meeting the requested similarity threshold.

### Utilities: `bin.autojump_utils`

Expose the public helpers `create_dir`, `encode_local`, `get_tab_entry_info`,
`get_pwd`, `has_uppercase`, `in_bash`, `is_autojump_sourced`, `is_linux`,
`is_osx`, `is_windows`, `is_python2`, `is_python3`, `move_file`,
`print_entry`, `print_local`, `print_tab_menu`, `sanitize`, `surround_quotes`,
`unico`, `first`, `second`, `last`, and `take`.

- `first`, `second`, and `last` return the corresponding item from an
  iterable, or `None` when it is unavailable. `take(n, iterable)` yields at
  most the first `n` items.
- `sanitize` removes trailing separators while preserving the root path.
- `has_uppercase` detects uppercase Unicode characters. `in_bash` and
  `is_autojump_sourced` reflect the shell environment. The platform helpers
  report the current operating system.
- `get_tab_entry_info(entry, separator)` returns
  `(needle, index, path)` for completion entries of the form
  `needle<separator>index<separator>path`; absent parts are `None`.
- `surround_quotes` quotes non-empty paths when running under bash, and the
  printing helpers emit the corresponding localized path/text output.

### Main command: `bin.autojump`

Expose `VERSION`, `FUZZY_MATCH_THRESHOLD`, `TAB_ENTRIES_COUNT`,
`TAB_SEPARATOR`, `set_defaults`, `parse_arguments`, `add_path`,
`decrease_path`, `detect_smartcase`, `find_matches`,
`handle_tab_completion`, `purge_missing_paths`, `print_stats`, and `main`.

- `set_defaults()` returns platform-specific `data_path` and `backup_path`.
- `add_path(data, path, weight=10)` strips a trailing separator and increases
  an existing entry using the utility's weighted update rule. The home
  directory is a protected special case and must not be added.
- `decrease_path(data, path, weight=15)` reduces an entry without going below
  zero. Both update functions return `(data, Entry)`.
- `detect_smartcase(needles)` selects case-insensitive matching only when no
  needle contains an uppercase character. `find_matches` filters missing
  paths and the current directory when requested, orders candidates by
  weight/path, and combines consecutive, fuzzy, and anywhere matching.
- `purge_missing_paths(entries)` keeps only entries whose paths exist.
- `parse_arguments()` reads `sys.argv` and supports positional directory
  terms plus `-a/--add`, `-i/--increase`, `-d/--decrease`, `--complete`,
  `--purge`, `-s/--stat`, and `-v/--version`.
- `main(args)` handles add, increase, decrease, completion, purge, stats, and
  jump operations. A non-Windows invocation that has not sourced the shell
  integration reports the setup problem and returns a nonzero status.

### Installation, removal, and compatibility modules

`install.py` must expose `SUPPORTED_SHELLS`, `cp`, `get_shell`, `mkdir`,
`modify_autojump_sh`, `modify_autojump_lua`,
`show_post_installation_message`, `parse_arguments`, and `main`.
`uninstall.py` must expose its removal helpers, `parse_arguments`, and `main`.
The helpers honor their dry-run flags and do not delete unrelated files.

`bin.autojump_argparse` should provide the parser and namespace/action symbols
needed by the project as a compatible command-line parsing surface.
`tools.autojump_ipython.j(path)` should provide the IPython directory-jump
helper when IPython is available.

## Implementation Notes

Use deterministic ordering wherever an API returns multiple entries. Keep
database writes safe against interrupted replacement and preserve a usable
backup. Shell scripts may call the Python command, but they must produce
shell-safe path output and support completion metadata. Keep platform-specific
branches explicit so Linux behavior remains usable while macOS and Windows
paths and shell files remain supported.

Example data interaction:

```python
from bin.autojump_data import Entry, load, save
from bin.autojump_match import match_anywhere

config = {"data_path": "/tmp/autojump.txt", "backup_path": "/tmp/autojump.txt.bak"}
save(config, {"/home/user/projects": 10.0})
entries = load(config)
matches = list(match_anywhere(["projects"], (Entry(path, weight) for path, weight in entries.items())))
```

The repository should include a usable installation flow and shell assets,
but it must not depend on copying the verifier's tests or on test-specific
fixtures to implement the behavior above.
