# Project Description

`astor` is a Python library designed for easy manipulation of Python source code via the Abstract Syntax Tree (AST). It provides functionality to read Python source code, convert it to an AST, modify the AST, and write it back to Python source code. The library focuses on round-trip conversion (source → AST → source) while maintaining readability and handling edge cases across different Python versions.

Key features include:
- Round-trip conversion: Convert Python source to AST and back to source code
- Pretty-printing: Dump AST structures in a more readable format than the built-in `ast` module
- Modified AST support: Doesn't require line numbers, `ctx`, or other compilation metadata for round-trips
- Non-recursive tree walking: Flexible tree traversal with before/after/skip node visit control

The library is based on code originally written by Armin Ronacher, with extensive testing and corner-case handling for Python 2.7 and Python 3.4+.

# Natural Language Instruction

Implement a Python package named `astor` that provides AST manipulation and source code generation capabilities. The package must:

1. Convert Python AST nodes back to source code using `astor.to_source()`
2. Pretty-print AST structures using `astor.dump_tree()`
3. Parse Python files into AST using `astor.parse_file()` or `astor.code_to_ast`
4. Support round-trip conversion: source → AST → source with deterministic output
5. Handle various Python constructs: assignments, functions, classes, control flow, comprehensions, lambdas, operators, imports, exceptions
6. Provide `SourceGenerator` class for customizable code generation
7. Export utility functions for AST manipulation through `astor.node_util`, `astor.op_util`, and `astor.tree_walk`
8. Include proper packaging with `setup.py` or `setup.cfg` for setuptools-based builds

The package name is `astor`, the import name is `astor`, and it must be installable via pip with no runtime dependencies beyond the Python standard library.

# Supports (Environment Configuration)

- Python: 2.7, 3.4+ (target: 3.12)
- Package Manager: pip (setuptools build backend)
- Build System: `setuptools` or `setuptools.build_meta`
- Runtime Dependencies: None (uses only Python standard library: `ast`, `os`, `warnings`)
- Installation: `pip install .` or `pip install -e .`
- Testing: pytest (optional, for development)
- No network access required during runtime

# Project Directory Structure

```
workspace/
├── setup.py (or setup.cfg + pyproject.toml)
├── astor/
│   ├── __init__.py
│   ├── code_gen.py
│   ├── node_util.py
│   ├── op_util.py
│   ├── file_util.py
│   ├── tree_walk.py
│   ├── source_repr.py
│   ├── string_repr.py
│   └── VERSION
```

# API Usage Guide

## Module: `astor`

The root module exports primary functions for AST manipulation and code generation:

### `to_source(node, indent_with=' ' * 4, add_line_information=False, pretty_source=None) -> str`

Convert an AST node to Python source code.

- **Parameters:**
  - `node` (ast.AST): An AST node (typically `ast.Module` from `ast.parse()`)
  - `indent_with` (str): String used for indentation (default: 4 spaces)
  - `add_line_information` (bool): Whether to add line number comments (default: False)
  - `pretty_source` (callable): Optional function to process the source
- **Returns:** Python source code as a string, typically ending with a newline
- **Example:**
  ```python
  import ast
  import astor
  
  tree = ast.parse('x = 1')
  source = astor.to_source(tree)
  # Returns: 'x = 1\n'
  ```

### `dump_tree(node, indent='  ', **kw) -> str`

Pretty-print an AST node structure.

- **Parameters:**
  - `node` (ast.AST): An AST node to dump
  - `indent` (str): Indentation string (default: 2 spaces)
  - `**kw`: Additional keyword arguments
- **Returns:** String representation of the AST structure
- **Example:**
  ```python
  import ast
  import astor
  
  tree = ast.parse('x = 1')
  dump = astor.dump_tree(tree)
  # Returns AST structure with nodes, attributes, and values
  ```

### `parse_file(filename) -> ast.Module`

Parse a Python file into an AST.

- **Parameters:**
  - `filename` (str): Path to Python file
- **Returns:** `ast.Module` node
- **Example:**
  ```python
  import astor
  
  tree = astor.parse_file('script.py')
  source = astor.to_source(tree)
  ```

### `code_to_ast`

A `CodeToAst` instance providing file parsing utilities. Accessible as `astor.code_to_ast.parse_file()`.

## Class: `SourceGenerator`

A class for generating Python source code from AST nodes with customization options.

- Located in `astor.code_gen` module
- Can be subclassed for custom code generation behavior
- Handles all Python AST node types
- **Example:**
  ```python
  import ast
  from astor.code_gen import SourceGenerator
  
  tree = ast.parse('def f(x): return x + 1')
  source = SourceGenerator('', tree).to_source()
  ```

## Module: `astor.node_util`

Utilities for AST node manipulation:

- `iter_node(node)`: Iterate over all nodes in an AST
- `strip_tree(node)`: Remove line numbers and other metadata from AST
- `dump_tree(node)`: Pretty-print AST structure

## Module: `astor.op_util`

Utilities for operator handling:

- `get_op_symbol(op, name)`: Get symbol for an operator
- `get_op_precedence(node)`: Get precedence value for an operator node
- `symbol_data`: Dictionary mapping operators to symbols

## Module: `astor.tree_walk`

Non-recursive tree walking utilities:

- `TreeWalk`: Class for flexible AST traversal with before/after/skip hooks

# Implementation Notes

## Round-Trip Behavior

The `to_source()` function is deterministic for a given AST input. String literals may be normalized (e.g., `"hello"` becomes `'hello'`), but the semantic meaning is preserved. Whitespace and formatting follow Python conventions with configurable indentation.

## Python Version Compatibility

The package should work on Python 2.7 and Python 3.4+ (>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*). For this implementation, target Python 3.12 compatibility with the standard library `ast` module.

## AST Node Coverage

The implementation must handle:
- **Statements:** assignments, function definitions, class definitions, imports, control flow (if/for/while), exception handling (try/except/finally), with statements, return/yield/pass/break/continue
- **Expressions:** binary operations, unary operations, comparisons, boolean operations, function calls, attribute access, subscripting, comprehensions (list/set/dict/generator), lambda expressions, literals
- **Special constructs:** decorators, annotations, tuple unpacking, augmented assignments

## Installation

The package uses setuptools for building and installation. A minimal `setup.py` or `setup.cfg` + `pyproject.toml` configuration is sufficient. The package must be installable with:

```bash
pip install -e .
```

## Version File

Include a `VERSION` file in the `astor/` directory containing the version string (e.g., `0.8.1`). The `__init__.py` should read this file to set `__version__`.

## No External Dependencies

The package must not depend on any external packages at runtime. Only use Python standard library modules (`ast`, `os`, `warnings`, `sys`, etc.).
