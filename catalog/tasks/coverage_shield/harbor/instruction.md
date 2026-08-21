# Build the `coverage_shield` project

## Project Description

Create a complete, installable Python project in `/workspace` named `coverage_shield`. The project is a local developer tool that runs a Python test suite under `coverage`, turns the report into a pandas `DataFrame`, builds a shields.io coverage-badge URL, and updates a README. It also offers optional Git staging, commit, and push integration.

The project constructs badge URLs only; it does not need to contact shields.io. The workspace starts empty, so include all package and build files needed for `pip install -e .` and `python -m coverage_shield`.

## Supports

- Target Python 3.12.
- Provide a top-level `setup.py` and a `coverage_shield/` package.
- The distribution and import-package name are both `coverage_shield`.
- The runtime third-party libraries are `coverage`, `pandas`, and `seaborn`. Use `setuptools` for packaging. `argparse`, `io`, `pathlib`, `re`, `subprocess`, and `warnings` are standard-library modules and must not be declared as PyPI runtime dependencies.
- Define `coverage_shield.__version__` as the string `"0"` and `coverage_shield.__author__` as `"Joseph Crispell"`.
- These modules must be importable:
  - `coverage_shield.unittest_coverage_functions`
  - `coverage_shield.command_line_interface_functions`
  - `coverage_shield.git_functions`
  - `coverage_shield.__main__`
- The Git integration expects the `git` executable and a Git working tree at runtime.

## API Usage Guide

### Coverage report and badge functions

All functions in this section live in `coverage_shield.unittest_coverage_functions`.

#### `parse_coverage_report`

```python
def parse_coverage_report(
    coverage_report_string: str,
    patterns_to_ignore: list[str] | None = None,
) -> pandas.DataFrame: ...
```

Parse the whitespace-aligned text emitted by `coverage report`. The input has the standard `Name`, `Stmts`, `Miss`, and `Cover` header, separator lines, per-file rows, and a final `TOTAL` row.

Return one row per file and columns named `Name`, `Stmts`, `Miss`, and `Cover`, in report order. Exclude separator and summary rows. Reset the row index before optional filtering. Convert the `Cover` values from percent strings to floats; statement and miss counts must remain numeric.

When `patterns_to_ignore` is provided, interpret each item as a regular-expression fragment. Exclude rows whose `Name` contains any of those patterns. Preserve the order of the remaining rows. Parsing errors from malformed input may propagate from pandas.

#### `run_code_coverage`

```python
def run_code_coverage(tester: str = "unittest") -> pandas.DataFrame: ...
```

Accept only `"unittest"` and `"pytest"`; reject any other tester with `ValueError`. Run the selected framework under coverage for the current directory, equivalent to:

```text
python3 -m coverage run --source=. -m <tester>
```

If that command succeeds, generate `python3 -m coverage report`, load ignore patterns from `.covignore`, parse the report, and return the resulting `DataFrame`. The test runner's standard-error progress is printed. If the coverage run fails, issue a warning containing the command failure and return an empty `DataFrame`.

#### `get_badge_colour`

```python
def get_badge_colour(value: float, colour_palette: str = "RdYlGn") -> str: ...
```

Treat `value` as a percentage on the 0 through 100 scale. Build a 100-color seaborn palette using `colour_palette` and its hexadecimal representation. Values below `0.5` select the first color. Other values select the color at Python's rounded percentage minus one. Return the selected lowercase hexadecimal string with its leading `#`. Invalid palette names may raise seaborn's normal exception.

#### `make_coverage_badge_url`

```python
def make_coverage_badge_url(
    coverage_dataframe: pandas.DataFrame | str,
    failing_colour: str = "red",
) -> str: ...
```

For a non-empty coverage `DataFrame`, calculate weighted coverage as `(sum(Stmts) - sum(Miss)) / sum(Stmts)`, convert it to a percentage, and round to one decimal place. Obtain the badge color with `get_badge_colour`. Return this URL form, omitting the color's leading `#`:

```text
https://img.shields.io/badge/coverage-<percentage>%25-<hex-colour>
```

For an empty coverage result, return `https://img.shields.io/badge/coverage-failing-<failing_colour>`. The default failure URL therefore ends in `-red`. URL generation has no network side effect.

#### `replace_regex_in_file`

```python
def replace_regex_in_file(
    file_path: pathlib.Path,
    pattern_regex: str,
    replacement: str,
    add_to_file: bool = True,
) -> None: ...
```

Read the target as text and process it line by line. A pattern is present when `re.match` succeeds on at least one complete line. If present, apply `re.sub` to every line. If absent and `add_to_file` is true, insert `replacement` as the first line. If absent and `add_to_file` is false, preserve the existing lines. Rewrite the file with `\n` separators and exactly one final newline. File-system and regular-expression errors propagate.

#### `load_patterns_to_ignore_in_coverage`

```python
def load_patterns_to_ignore_in_coverage(
    file_path: pathlib.Path = pathlib.Path(".covignore"),
) -> list[str] | None: ...
```

Return the file's non-empty lines in original order, excluding any line whose first character is `#`. Do not include blank lines. Return `None` when the file does not exist or has no usable patterns. The retained strings are regular expressions consumed by `parse_coverage_report`.

### Git functions

All functions in this section live in `coverage_shield.git_functions`.

#### `send_command`

```python
def send_command(*args, **kwargs) -> subprocess.CompletedProcess: ...
```

Run the positional arguments as one subprocess command, pass through keyword arguments such as `capture_output=True` and `text=True`, and always enable `check=True`. Return the `CompletedProcess`. A non-zero exit status raises `subprocess.CalledProcessError`.

#### `check_if_file_changed_using_git`

```python
def check_if_file_changed_using_git(file_path: pathlib.Path) -> bool: ...
```

Run `git status <file_path>` through `send_command`, capturing text output. Return false only when the output reports that there is nothing to commit; otherwise return true. Git failures propagate as `subprocess.CalledProcessError`.

#### `push_updated_readme`

```python
def push_updated_readme(
    readme_path: pathlib.Path = pathlib.Path("README.md"),
    commit_and_push: bool = True,
) -> None: ...
```

Do nothing when `check_if_file_changed_using_git` reports no change. Otherwise stage exactly `readme_path` with `git add`. When `commit_and_push` is true, commit with the message `Updated coverage badge in <readme_path>` and then run `git push`. When false, leave the file staged without committing or pushing.

### Command-line functions

These functions live in `coverage_shield.command_line_interface_functions`.

#### `build_command_line_interface`

```python
def build_command_line_interface() -> argparse.ArgumentParser: ...
```

Return an `argparse.ArgumentParser` whose program name is `coverage_shield`. Use `argparse.ArgumentDefaultsHelpFormatter` and provide these options:

| Option | Value behavior | Default |
| --- | --- | --- |
| `-d`, `--directory` | optional string value | `"."` |
| `-r`, `--readme` | optional string value | `"README.md"` |
| `-t`, `--tester` | optional string value; documented choices are `unittest` and `pytest` | `"unittest"` |
| `-g`, `--git_push` | `store_true` flag | `False` |

The parser must provide standard `-h`/`--help` behavior.

#### `parse_command_line_arguments`

```python
def parse_command_line_arguments(
    parser: argparse.ArgumentParser,
    arguments: list[str] = sys.argv[1:],
    testing: bool = False,
): ...
```

Parse `arguments` with the supplied parser. When `testing` is true, return the populated `argparse.Namespace` without running coverage, changing files, changing directory, or invoking Git.

In normal mode, change to the selected directory, run coverage with the selected tester, build a badge URL, and update the selected README. Match an existing Markdown badge with the form `![Code Coverage](...)`; add one at the top when absent. If `git_push` is set, pass the README path to `push_updated_readme`.

### Module entry point

`coverage_shield.__main__` provides:

```python
def main(arguments: list[str] = sys.argv[1:]) -> None: ...
```

Build the parser and delegate to `parse_command_line_arguments`. Calling `main(["--help"])` must use normal argparse help behavior, including raising `SystemExit` after printing help. Running `python -m coverage_shield` calls `main()`.

## Implementation Notes

- Keep coverage rows, ignore patterns, and file lines deterministic and in input order.
- Coverage is weighted by statement counts, not the arithmetic mean of per-file percentages.
- A typical README replacement call is:

```python
replace_regex_in_file(
    pathlib.Path("README.md"),
    r"\!\[Code Coverage\]\(.+\)",
    "![Code Coverage](https://img.shields.io/badge/coverage-failing-red)",
)
```

- Include a concise README describing installation, `python -m coverage_shield`, all CLI options, and `.covignore` behavior.
- You may add your own tests, but the finished project must install with `pip install -e .` from the repository root.
