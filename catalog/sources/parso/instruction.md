# Build the parso Package

## Project Description

**parso** is a Python parser that supports error recovery and round-trip parsing for different Python versions. It consists of a small API to parse Python code and analyze the resulting syntax tree. Parso was originally part of the Jedi project and was extracted to be useful for other projects as well.

Key features:
- Parse Python code and generate an abstract syntax tree (AST)
- Support for multiple Python versions (3.6 through 3.14)
- Error recovery: can parse code with syntax errors
- Round-trip parsing: `parse(code).get_code() == code`
- List multiple syntax errors in Python files
- Typed stubs for better IDE support

## Natural Language Instruction

Your task is to build a complete, working implementation of the **parso** package version 0.8.7 from an empty workspace.

The package must:

1. **Provide a `parse()` function** that takes Python source code as a string and returns a Module object representing the parsed syntax tree
2. **Return proper AST node types** including Module, PythonNode, various statement and expression nodes, and leaf nodes
3. **Support node inspection** through properties like `.type`, `.children`, `.value`, `.end_pos`, and method `.get_code()`
4. **Handle error recovery** by creating error nodes for invalid syntax
5. **Support all Python language constructs** including functions, classes, imports, control flow statements, literals, operators, comprehensions, decorators, async/await, f-strings, and more

The implementation must pass a comprehensive test suite covering:
- Basic parsing of expressions, statements, and literals
- Function and class definitions
- Control flow structures (if, for, while, try, with)
- All operator types (arithmetic, comparison, logical, bitwise)
- Data structures (lists, dicts, tuples, sets, comprehensions)
- Advanced features (decorators, async/await, generators, f-strings)
- Node type inspection and code regeneration
- Position tracking

## Environment Configuration

**Language:** Python 3.12

**Package Manager:** pip

**Installation Method:**
```bash
python -m pip install --no-build-isolation --no-deps --no-index -e .
```

**Dependencies:** None (parso has no runtime dependencies)

## Supports

**Operating System:** Debian 12 (amd64)

**Python Version:** 3.12

**License:** MIT License (with some PSF-licensed files from Python stdlib)

## Project Directory Structure

The package should be installed from `/workspace` with the following structure:

```
workspace/
├── parso/
│   ├── __init__.py          # Main module with parse() function and __version__
│   ├── python/
│   │   ├── __init__.py
│   │   ├── grammar*.txt     # Python grammar definition files
│   │   ├── tree.py          # AST node classes (Module, PythonNode, etc.)
│   │   └── parser.py        # Parser implementation
│   ├── tree.py              # Base tree node classes
│   ├── parser.py            # Base parser
│   ├── pgen2/               # Parser generator (from Python stdlib)
│   │   ├── __init__.py
│   │   ├── generator.py
│   │   └── ...
│   ├── tokenize.py          # Tokenizer (adapted from Python stdlib)
│   ├── token.py             # Token definitions
│   └── py.typed             # PEP 561 marker for type stubs
├── setup.py                 # Installation metadata
├── LICENSE.txt              # MIT license text
└── README.rst              # Project documentation
```

## API Usage Guide

### Core Parsing API

```python
import parso

# Parse Python code
module = parso.parse('x = 1 + 2')

# Get the first statement
stmt = module.children[0]
print(stmt.type)  # 'expr_stmt'

# Get code back
print(stmt.get_code())  # 'x = 1 + 2'
```

### Node Types and Properties

**Module:** The root node of a parsed Python file
- `children`: List of statement nodes and an EndMarker

**PythonNode:** Internal nodes in the AST
- `type`: String identifier of the node type (e.g., 'funcdef', 'if_stmt', 'arith_expr')
- `children`: List of child nodes
- `get_code()`: Returns the source code string for this node

**Leaf Nodes:** Terminal nodes representing tokens
- `type`: Token type (e.g., 'name', 'number', 'string', 'keyword', 'operator')
- `value`: String value of the token
- `end_pos`: Tuple (line, column) indicating end position

### Common Node Types

**Statements:**
- `expr_stmt`: Expression statement (assignments, standalone expressions)
- `funcdef`: Function definition
- `classdef`: Class definition
- `if_stmt`: If statement
- `for_stmt`: For loop
- `while_stmt`: While loop
- `with_stmt`: With statement
- `try_stmt`: Try-except statement
- `import_name`: Import statement
- `import_from`: From-import statement
- `return_stmt`: Return statement
- `raise_stmt`: Raise statement
- `assert_stmt`: Assert statement
- `del_stmt`: Del statement
- `global_stmt`: Global statement
- `async_stmt`: Async function definition
- `decorated`: Decorated function or class

**Expressions:**
- `arith_expr`: Arithmetic expression (+ -)
- `term`: Multiplicative expression (* / // %)
- `power`: Power expression (**)
- `factor`: Unary expression (+ - ~)
- `shift_expr`: Shift expression (<< >>)
- `and_expr`: Bitwise AND (&)
- `xor_expr`: Bitwise XOR (^)
- `or_expr`: Bitwise OR (|)
- `comparison`: Comparison expression
- `not_test`: Not expression
- `and_test`: Logical AND
- `or_test`: Logical OR
- `atom`: Basic literal (list, dict, tuple, set, etc.)
- `atom_expr`: Attribute access, subscript, or function call
- `lambdef`: Lambda expression
- `fstring`: F-string literal
- `star_expr`: Starred expression (*args)

**Leaf Types:**
- `name`: Identifier
- `number`: Numeric literal
- `string`: String literal
- `keyword`: Python keyword (def, class, if, for, etc.)
- `operator`: Operator token

### Examples

**Parse a function definition:**
```python
code = '''
def greet(name):
    return f"Hello, {name}!"
'''
module = parso.parse(code.strip())
func = module.children[0]
print(func.type)  # 'funcdef'
print(func.name.value)  # 'greet'
```

**Parse an expression:**
```python
module = parso.parse('a + b * c')
expr = module.children[0]
print(expr.type)  # 'arith_expr'
print(expr.get_code())  # 'a + b * c'
```

**Check node positions:**
```python
module = parso.parse('hello')
name = module.children[0]
print(name.end_pos)  # (1, 5)
```

## Implementation Notes

1. **Module Structure**: The package must be structured as shown in the directory layout, with `parso/__init__.py` exporting the main `parse()` function and `__version__` attribute.

2. **Grammar Files**: The `parso/python/grammar*.txt` files define the Python grammar for different versions. These use a variant of BNF notation.

3. **Parser Generator**: The `pgen2/` subpackage contains the parser generator that reads grammar files and creates parsers. This code is adapted from Python's lib2to3.

4. **Tree Structure**: All nodes inherit from base classes in `tree.py`. The tree structure must support:
   - Navigation through `.children`
   - Type identification through `.type`
   - Source reconstruction through `.get_code()`
   - Position tracking through `.start_pos` and `.end_pos`

5. **Node Types**: The parser must correctly identify all Python language constructs and assign appropriate node types. Common patterns:
   - Binary operators create nodes named after their precedence level (arith_expr, term, power, etc.)
   - Statements have names ending in '_stmt'
   - Definitions end in 'def' (funcdef, classdef, lambdef)
   - Attribute access, subscripting, and calls all use 'atom_expr' (not 'power' in Python 3.9+)

6. **Error Handling**: Invalid syntax should create `error_node` types rather than raising exceptions, allowing error recovery.

7. **Version Support**: While the implementation should target Python 3.12 as the runtime, it must be able to parse code from Python 3.6 through 3.14.

8. **Installation**: The package must install correctly using `pip install -e .` with the setuptools build backend.

9. **No External Dependencies**: The package must work without any runtime dependencies (beyond the Python standard library).

10. **get_code() Contract**: For valid Python code, calling `parse(code).get_code()` must return code that is semantically equivalent to the input (though whitespace may differ in error recovery cases).
