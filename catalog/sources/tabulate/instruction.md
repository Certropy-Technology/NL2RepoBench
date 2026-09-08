# Project Description

`tabulate` is a Python library for pretty-printing tabular data in various text formats. It formats two-dimensional data (lists of lists, dictionaries, dataclasses, etc.) as tables suitable for console output, markdown files, reStructuredText, LaTeX, HTML, and other markup languages. The library automatically detects column types, aligns values appropriately, and supports numerous table styles with customizable formatting options.

The project enables users to:
- Format tabular data from multiple input types (lists, dicts, dataclasses, NumPy arrays, Pandas DataFrames)
- Choose from over 30 built-in table formats (plain, simple, grid, github, psql, html, latex, etc.)
- Control number formatting, alignment, missing value representation, and column wrapping
- Add headers and row indices with flexible positioning
- Generate publication-ready tables for documentation and reports

The library is designed for console applications, data visualization, test output formatting, and automated report generation.

# Natural Language Instruction

Your task is to create a Python package named `tabulate` that provides table formatting functionality. The package must:

1. **Core API**: Implement a `tabulate()` function that formats tabular data into text tables with configurable formats
2. **Format Support**: Support at least these table formats: `plain`, `simple`, `grid`, `fancy_grid`, `github`, `psql`, `rounded_grid`, `pipe`, `orgtbl`, `rst`, `mediawiki`, `html`, `latex`
3. **Input Flexibility**: Accept various input types including lists of lists, dictionaries of iterables, lists of dictionaries, and lists of dataclasses
4. **Header Control**: Support explicit headers, firstrow-as-headers mode, and dictionary keys as headers
5. **Alignment**: Provide automatic type detection and alignment (decimal, left, right, center) with per-column overrides
6. **Number Formatting**: Support customizable float and integer formatting with proper alignment
7. **Missing Values**: Handle None/missing values with configurable replacement strings
8. **Row Indices**: Allow showing/hiding row indices with custom index iterables
9. **Export Functions**: Provide `tabulate_formats` (list of format names) and `simple_separated_format()` helper
10. **CLI Utility**: Include a command-line interface accessible via `python -m tabulate` for basic table formatting

The package must be installable as an editable package with `pip install -e .` and import as `from tabulate import tabulate, tabulate_formats, simple_separated_format`.

Critical constraints:
- All numeric alignment must respect decimal point positioning when `numalign="decimal"`
- Table formats must produce consistent character-exact output matching format specifications
- The package must work without runtime network access or external dependencies (except optional wcwidth)
- Column width detection must handle ANSI escape sequences in strings properly

# Environment Configuration (Supports)

- **Language**: Python 3.12
- **Package Manager**: pip
- **Build System**: setuptools with dynamic versioning via setuptools_scm
- **Installation**: `pip install --no-build-isolation --no-deps --no-index -e .`
- **Runtime Dependencies**: None (wcwidth is optional for wide character support)
- **Network Policy**: No network access during installation, testing, or runtime
- **Operating System**: Debian 12 (amd64)
- **Python Version Requirement**: >=3.10

The build backend (setuptools and setuptools_scm) is preinstalled in the image. The package must install without network access using the preinstalled build dependencies.

# Project Directory Structure

```
workspace/
├── pyproject.toml              # Project metadata and build configuration
├── LICENSE                      # MIT license file
├── README.md                    # Package documentation
└── tabulate/
    └── __init__.py              # Main module with tabulate() function and exports
```

The package should be structured as a single-module package where all functionality is contained in `tabulate/__init__.py`. The module must export `tabulate`, `tabulate_formats`, and `simple_separated_format` as public API.

# API Usage Guide

## Main Function: `tabulate()`

Import path: `from tabulate import tabulate`

```python
def tabulate(
    tabular_data,
    headers=(),
    tablefmt="simple",
    floatfmt=_DEFAULT_FLOATFMT,
    intfmt=_DEFAULT_INTFMT,
    numalign=_DEFAULT_ALIGN,
    stralign=_DEFAULT_ALIGN,
    missingval=_DEFAULT_MISSINGVAL,
    showindex="default",
    disable_numparse=False,
    colglobalalign=None,
    colalign=None,
    preserve_whitespace=False,
    maxcolwidths=None,
    headersglobalalign=None,
    headersalign=None,
    rowalign=None,
    maxheadercolwidths=None,
    break_long_words=True,
    break_on_hyphens=True,
) -> str
```

**Purpose**: Format tabular data as a text table in the specified format.

**Parameters**:

- `tabular_data`: The data to format. Accepts:
  - List of lists: `[[val1, val2], [val3, val4]]`
  - List of dictionaries: `[{"a": 1, "b": 2}, {"a": 3, "b": 4}]`
  - Dictionary of iterables: `{"a": [1, 3], "b": [2, 4]}`
  - List of dataclasses
  - Any iterable of iterables
  
- `headers`: Column headers. Can be:
  - Empty tuple `()` (default): No headers
  - List of strings: Explicit header names
  - `"firstrow"`: Use first data row as headers
  - `"keys"`: Use dictionary keys or column indices as headers

- `tablefmt` (str): Output format. Default: `"simple"`. Supported formats include:
  - `"plain"`: Columns separated by double space, no decorations
  - `"simple"`: Simple format with header separator (Pandoc style)
  - `"grid"`: Grid tables with `+`, `-`, `|` characters
  - `"fancy_grid"`: Grid with box-drawing characters (╒═╤╕)
  - `"github"`: GitHub-flavored Markdown tables
  - `"pipe"`: Pipe tables with alignment colons
  - `"orgtbl"`: Emacs org-mode tables
  - `"psql"`: PostgreSQL-style output
  - `"rst"`: reStructuredText grid tables
  - `"mediawiki"`: MediaWiki table syntax
  - `"html"`: HTML table with proper escaping
  - `"latex"`: LaTeX tabular environment
  - `"rounded_grid"`: Grid with rounded corners (╭─┬╮)
  - And many others (see `tabulate_formats`)

- `floatfmt` (str or list): Format spec for floats. Default: `"g"`. Examples: `".2f"`, `".3e"`. Can be a list of format specs (one per column).

- `intfmt` (str or list): Format spec for integers. Default: `""` (no formatting). Can be a list of format specs.

- `numalign` (str or None): Alignment for numeric columns. Options: `"decimal"` (default), `"right"`, `"center"`, `"left"`, `None` (disable).

- `stralign` (str or None): Alignment for string columns. Options: `"left"` (default), `"right"`, `"center"`, `None` (disable).

- `missingval` (str or list): String to display for `None` values. Default: `""`. Can be a list (one per column).

- `showindex` (str or bool or iterable): Control row index display:
  - `"default"`: Show index for pandas DataFrames only
  - `"always"` or `True`: Always show index column (0, 1, 2, ...)
  - `"never"` or `False`: Never show index
  - Iterable: Use provided values as custom index

- `disable_numparse` (bool): If True, disable automatic number type detection. Default: `False`.

- `colglobalalign` (str or None): Global alignment override for all columns before `colalign`. Options: `None`, `"right"`, `"center"`, `"decimal"`, `"left"`.

- `colalign` (list or None): Per-column alignment starting from leftmost column. Each element can be `"global"` (no override), `"right"`, `"center"`, `"decimal"`, `"left"`, or `None`.

- `preserve_whitespace` (bool): If True, preserve leading/trailing whitespace in cells. Default: `False`.

- `maxcolwidths` (int, list, or None): Maximum width for column content. If int, applies to all columns. If list, per-column limits.

- `headersglobalalign` (str or None): Global alignment for headers. Options: `None` (follow column alignment), `"right"`, `"center"`, `"left"`.

- `headersalign` (list or None): Per-header alignment. Each element can be `"global"`, `"same"` (follow column), `"right"`, `"center"`, `"left"`.

- `rowalign` (str, list, or None): Vertical alignment for multiline cells. Options: `"top"`, `"center"`, `"bottom"`, or None.

- `maxheadercolwidths` (int, list, or None): Maximum width for header content.

- `break_long_words` (bool): Break words longer than column width. Default: `True`.

- `break_on_hyphens` (bool): Break lines at hyphens. Default: `True`.

**Returns**: A string containing the formatted table.

**Examples**:

Simple list formatting:
```python
from tabulate import tabulate

data = [[1, 2.34], [-56, 8.999], [2, 10001]]
print(tabulate(data))
# Output:
# ---  ---------
#   1      2.34
# -56      8.999
#   2  10001
# ---  ---------
```

With headers:
```python
data = [["Alice", "F", 24], ["Bob", "M", 19]]
headers = ["Name", "Sex", "Age"]
print(tabulate(data, headers=headers, tablefmt="grid"))
# Output:
# +-------+-----+-----+
# | Name  | Sex | Age |
# +=======+=====+=====+
# | Alice | F   |  24 |
# +-------+-----+-----+
# | Bob   | M   |  19 |
# +-------+-----+-----+
```

Dict of iterables:
```python
data = {"Name": ["Alice", "Bob"], "Age": [24, 19]}
print(tabulate(data, headers="keys", tablefmt="github"))
# Output:
# | Name  | Age |
# |-------|-----|
# | Alice |  24 |
# | Bob   |  19 |
```

Custom float formatting:
```python
data = [[1.2345, 2.3456], [3.4567, 4.5678]]
print(tabulate(data, floatfmt=".2f"))
```

Missing value handling:
```python
data = [["spam", 1, None], ["eggs", 42, 3.14]]
print(tabulate(data, missingval="?"))
```

## Module-Level Variables

### `tabulate_formats`

Import path: `from tabulate import tabulate_formats`

**Type**: `list[str]`

**Description**: A sorted list of all available table format names. Use this to discover supported formats or validate user input.

**Example**:
```python
from tabulate import tabulate_formats
print(tabulate_formats[:5])  # ['asciidoc', 'colon_grid', 'double_grid', ...]
```

### `simple_separated_format()`

Import path: `from tabulate import simple_separated_format`

```python
def simple_separated_format(separator: str) -> TableFormat
```

**Purpose**: Create a custom table format using a specified separator character.

**Parameters**:
- `separator` (str): The separator string to use between columns

**Returns**: A `TableFormat` object that can be passed to `tabulate(tablefmt=...)`

**Example**:
```python
from tabulate import tabulate, simple_separated_format

data = [["Alice", 24], ["Bob", 19]]
custom_fmt = simple_separated_format(" | ")
print(tabulate(data, tablefmt=custom_fmt))
```

## Command-Line Interface

The package provides a CLI utility accessible via:

```bash
python -m tabulate [options]
```

The CLI reads tabular data from standard input and outputs formatted tables. It supports various input formats (CSV, JSON lines) and can accept header specifications via command-line arguments.

# Implementation Notes

## Type Detection and Alignment

The `tabulate()` function must automatically detect column types:
- **Integer**: Strings representing integers without decimal points
- **Float**: Strings with decimal points or scientific notation
- **Bool**: Strings like "True", "False" 
- **String**: Everything else

Numeric columns align on decimal points by default (`numalign="decimal"`). This means:
- The decimal separator (`.`) should vertically align across rows
- Integer numbers are treated as having an implicit decimal point at the end
- Negative signs are part of the number and count toward alignment

String columns left-align by default (`stralign="left"`).

## Table Format Specifications

Each format has specific character requirements:

- **plain**: Double-space separation, no borders
- **simple**: Header separator with dashes, double-space columns
- **grid**: Full box with `+`, `-`, `|`, `=` (under header)
- **fancy_grid**: Box-drawing characters: `╒═╤╕` (top), `╞═╪╡` (header), `├─┼┤` (between), `╘═╧╛` (bottom), `│` (vertical)
- **github**: Markdown pipes with header separator: `|---|---|`
- **psql**: PostgreSQL style with `+`, `-`, `|`
- **rounded_grid**: Rounded corners using `╭`, `╮`, `╰`, `╯`, with `─`, `┬`, `┴`, `├`, `┤`, `┼`, `│`
- **rst**: reStructuredText grid tables
- **html**: Proper HTML `<table>`, `<thead>`, `<tbody>`, `<tr>`, `<th>`, `<td>` with HTML escaping
- **latex**: LaTeX `\begin{tabular}...\end{tabular}` environment

## Headers Behavior

- When `headers=()` (empty), no header row is printed
- When `headers="firstrow"`, the first data row is extracted and used as headers
- When `headers="keys"`, dictionary keys become headers (in dict order for Python 3.7+)
- Explicit headers list can be shorter than the number of columns (applies to rightmost columns)

## Missing Value Handling

`None` values in data are replaced with the `missingval` string before formatting. The default is an empty string. The `missingval` parameter can be:
- A single string applied to all columns
- A list of strings (one per column)

## Number Formatting

- `floatfmt`: Python format specification for floats (e.g., `".2f"`, `".3e"`, `"g"`)
- `intfmt`: Format specification for integers (e.g., `"d"`, `"08d"`)
- Both can be lists for per-column formatting
- Format specs follow Python's format specification mini-language

## Multiline Content

When cell values contain newline characters (`\n`), the table formatter:
- Splits cells into multiple lines
- Aligns content within each cell vertically (controlled by `rowalign`)
- Maintains column widths across all lines of multiline rows

## Column Width Control

- `maxcolwidths`: Limits column content width by wrapping text
- Text wrapping respects word boundaries (unless `break_long_words=True`)
- Hyphens can be break points (controlled by `break_on_hyphens`)
- ANSI escape sequences are not counted toward visible width

## ANSI Escape Sequences

The library correctly handles ANSI color codes and other escape sequences:
- Escape sequences don't count toward visible string width
- Alignment calculations use visible character count only
- Strip ANSI codes when calculating widths for padding

## Output Determinism

All table outputs must be deterministic given the same inputs and parameters:
- Dictionary key order follows insertion order (Python 3.7+)
- No random components in formatting
- Consistent spacing and alignment rules

## Error Handling

- Invalid format names in `tablefmt` should raise `ValueError`
- Mismatched header counts are handled gracefully (headers apply to rightmost columns)
- Empty data (empty list, empty dict) produces valid output with just headers if provided
- Non-serializable values should be converted to strings via `str()`

## Dataclass Support

The library must support Python dataclasses as input:
```python
from dataclasses import dataclass
from tabulate import tabulate

@dataclass
class Person:
    name: str
    age: int

data = [Person("Alice", 24), Person("Bob", 19)]
print(tabulate(data, headers="keys"))
```

Dataclass fields become columns, field names become headers when `headers="keys"`.

## Separating Lines

Some formats support separating lines between data rows (not just after headers). When a row consists entirely of a special sentinel value indicating a line separator, a horizontal line is drawn at that position.

## Global and Per-Column Alignment

Alignment precedence (highest to lowest):
1. Per-column `colalign` (when not `"global"`)
2. Global `colglobalalign` 
3. Type-based defaults (`numalign` for numbers, `stralign` for strings)

Similarly for headers:
1. Per-header `headersalign` (when not `"global"` or `"same"`)
2. Global `headersglobalalign`
3. Follow column alignment

## CLI Implementation

The command-line interface should:
- Read data from stdin
- Accept format selection via `--format` or `-f`
- Support header specification via `--headers` option
- Output formatted table to stdout
- Handle errors gracefully with appropriate exit codes

Entry point in `pyproject.toml`:
```toml
[project.scripts]
tabulate = "tabulate:_main"
```

## Package Metadata

The `pyproject.toml` must include:
- `name = "tabulate"`
- `requires-python = ">=3.10"`
- Build system: `setuptools` and `setuptools_scm[toml]>=3.4.3`
- Dynamic version determination via setuptools_scm
- MIT license specification
- Console script entry point for CLI

## Version Handling

The package uses `setuptools_scm` for dynamic version determination. In environments where git is unavailable or the version cannot be determined, the `__version__` attribute should fall back gracefully to "unknown" or read from package metadata via `importlib.metadata.version("tabulate")`.

# Examples

## Basic Table Formats

Plain format (no decorations):
```python
from tabulate import tabulate
data = [["spam", 41.9999], ["eggs", 451.0]]
print(tabulate(data, tablefmt="plain"))
# spam   41.9999
# eggs  451
```

Simple format (Pandoc simple tables):
```python
print(tabulate(data, headers=["strings", "numbers"], tablefmt="simple"))
# strings      numbers
# ---------  ---------
# spam         41.9999
# eggs        451
```

Grid format (full borders):
```python
print(tabulate(data, headers=["strings", "numbers"], tablefmt="grid"))
# +-----------+-----------+
# | strings   |   numbers |
# +===========+===========+
# | spam      |   41.9999 |
# +-----------+-----------+
# | eggs      |  451      |
# +-----------+-----------+
```

GitHub Markdown:
```python
print(tabulate(data, headers=["strings", "numbers"], tablefmt="github"))
# | strings   |   numbers |
# |-----------|-----------|
# | spam      |   41.9999 |
# | eggs      |  451      |
```

## Advanced Formatting

Dictionary of lists with custom alignment:
```python
data = {"Name": ["Alice", "Bob", "Charlie"], "Score": [95.5, 87.3, 92.1]}
result = tabulate(data, headers="keys", tablefmt="psql", floatfmt=".1f", colalign=["left", "center"])
print(result)
```

Handling missing values:
```python
data = [["complete", 100, 5.5], ["missing", None, None], ["partial", 50, None]]
print(tabulate(data, headers=["Status", "Value", "Score"], missingval="N/A"))
```

Row indices:
```python
data = [["Alice", 24], ["Bob", 19]]
print(tabulate(data, headers=["Name", "Age"], showindex=True, tablefmt="grid"))
# Shows a column with indices 0, 1, 2, ...
```

Custom index labels:
```python
print(tabulate(data, headers=["Name", "Age"], showindex=["A", "B"], tablefmt="simple"))
```

## Error Handling and Boundary Conditions

Empty data:
```python
print(tabulate([], headers=["A", "B"]))
# Should produce just the header with no data rows
```

No headers, no data:
```python
print(tabulate([]))
# Should produce minimal or empty output
```

Unicode content:
```python
data = [["日本", "Tokyo"], ["中国", "Beijing"]]
print(tabulate(data, headers=["Country", "Capital"], tablefmt="grid"))
# Should handle Unicode characters correctly
```

Mixed types:
```python
data = [[1, "two", 3.0, True, None]]
print(tabulate(data, missingval="NULL"))
```

## HTML and LaTeX Output

HTML with escaping:
```python
data = [["<script>alert('xss')</script>", "safe"]]
print(tabulate(data, tablefmt="html"))
# Should escape HTML special characters: &lt;script&gt;...
```

LaTeX table:
```python
data = [["alpha", 1], ["beta", 2]]
print(tabulate(data, headers=["Greek", "Value"], tablefmt="latex"))
# Should produce: \begin{tabular}{lr} ... \end{tabular}
```

## Format Discovery

List all available formats:
```python
from tabulate import tabulate_formats
for fmt in tabulate_formats:
    print(fmt)
# Outputs: asciidoc, colon_grid, double_grid, ...
```

Validate format:
```python
user_format = "github"
if user_format in tabulate_formats:
    print(tabulate(data, tablefmt=user_format))
```

## Security

HTML output must properly escape special characters to prevent XSS:
- `<` → `&lt;`
- `>` → `&gt;`
- `&` → `&amp;`
- `"` → `&quot;`
- `'` → `&#x27;`

The `html` format performs escaping. There is also an `unsafehtml` format that does not escape (for trusted content).

LaTeX output should escape special LaTeX characters:
- `\`, `{`, `}`, `%`, `&`, `#`, `_`, `^`, `~`, `$`

## Testing Considerations

Verifier tests will check:
- Exact string output for various format styles
- Correct alignment of decimal numbers
- Header positioning and separator lines
- Missing value replacement
- Float and integer formatting
- Column width calculations
- HTML/LaTeX special character escaping
- Multiline cell handling
- Edge cases (empty data, single column, very long values)

The verifier will compare the exact string output from `tabulate()` against expected reference outputs for deterministic scenarios.
