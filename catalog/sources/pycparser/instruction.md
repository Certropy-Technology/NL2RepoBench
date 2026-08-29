# Build `pycparser`

Create a complete, installable pure-Python package named `pycparser` from an
empty workspace. It parses preprocessed C source into an explicit abstract
syntax tree and can generate readable C code from that tree. Do not depend on
a preinstalled copy of `pycparser`, network access, or a C compiler at runtime.

## Project Description

Implement the public behavior of the frozen pycparser 3.00 source. The parser
targets the C99 grammar with the C11 constructs covered by the API below. The
implementation must be modular across AST nodes, lexical analysis, parsing,
code generation, and AST transforms. AST construction is deterministic for
fixed source text and filename.

The scored package is the import package `pycparser`; the distribution name is
also `pycparser`. Runtime dependencies are limited to the Python standard
library. A source-only build must work without a `.git` directory.

## Supports

- Support CPython 3.10 or newer in the supported Python 3 range.
- Provide an installable package containing `pycparser/__init__.py`,
  `c_ast.py`, `c_lexer.py`, `c_parser.py`, `c_generator.py`,
  `ast_transforms.py`, and `_c_ast.cfg`.
- Normal parsing of supplied text must not contact a network. `parse_file` with
  `use_cpp=False` reads a local file only. `preprocess_file` and
  `parse_file(..., use_cpp=True)` may invoke the caller-selected local `cpp`
  executable, and must report an unavailable executable as `RuntimeError`.
- Preserve insertion order in AST child sequences and deterministic string
  output. Do not use random values, current time, or network metadata.
- Do not require Graphviz, external Python packages, generated parser tables,
  or the upstream `test2ref` helper.

## API Usage Guide

### Package and files

`pycparser.__version__` is the string `"3.00"` and `pycparser.CParser` is an
alias of `pycparser.c_parser.CParser`. `preprocess_file(filename,
cpp_path="cpp", cpp_args="")` returns the selected preprocessor's text with
universal newlines. `cpp_args` accepts either a string or a list of argument
strings. `parse_file(filename, use_cpp=False, cpp_path="cpp", cpp_args="",
parser=None, encoding=None)` reads or preprocesses a file and returns a
`c_ast.FileAST`; a supplied parser object receives `(text, filename)`.

### AST module: `pycparser.c_ast`

`Node` is the base class. Its `children()` method returns a tuple of
`(child_name, child_node)` pairs in source/field order. `show(buf=sys.stdout,
offset=0, attrnames=False, showemptyattrs=True, nodenames=False,
showcoord=False, _my_node_name=None)` recursively writes a deterministic
indented representation. `Node.__repr__` names the concrete class and its
slot values.

`NodeVisitor` provides `visit(node)` and `generic_visit(node)`. `visit` calls
`visit_<ConcreteClass>` when present, otherwise `generic_visit`; the generic
walk is preorder and a specialized visitor controls whether children are
visited.

Implement these concrete nodes with the indicated constructor fields and
`attr_names`/`children()` behavior: `ArrayDecl(type, dim, dim_quals, coord)`,
`ArrayRef(name, subscript, coord)`, `Assignment(op, lvalue, rvalue, coord)`,
`BinaryOp(op, left, right, coord)`, `Constant(type, value, coord)`, `Decl(name,
quals, align, storage, funcspec, type, init, bitsize, coord)`, `FileAST(ext,
coord)`, `FuncCall(name, args, coord)`, `FuncDecl(args, type, coord)`,
`FuncDef(decl, param_decls, body, coord)`, `ID(name, coord)`, `IdentifierType(
names, coord)`, `Return(expr, coord)`, `Compound(block_items, coord)`,
`Struct(name, decls, coord)`, `Typedef(name, quals, storage, type, coord)`,
`TypeDecl(declname, quals, align, type, coord)`, `UnaryOp(op, expr, coord)`,
`If(cond, iftrue, iffalse, coord)`, `For(init, cond, next, stmt, coord)`,
`While(cond, stmt, coord)`, `DoWhile(cond, stmt, coord)`, `Switch(cond, stmt,
coord)`, `Case(expr, stmts, coord)`, `Default(stmts, coord)`, `Enum(name,
values, coord)`, `Enumerator(name, value, coord)`, `EnumeratorList(enumerators,
coord)`, `Union(name, decls, coord)`, `PtrDecl(quals, type, coord)`, `ArrayDecl`,
`Typename(quals, type, coord)`, `Cast(to_type, expr, coord)`, `ExprList(exprs,
coord)`, `InitList(exprs, coord)`, `Label(name, stmt, coord)`, `Goto(name,
coord)`, `Break(coord)`, `Continue(coord)`, `EmptyStatement(coord)`,
`EllipsisParam(coord)`, `Pragma(string, coord)`, `NamedInitializer(name,
expr, coord)`, `CompoundLiteral(type, init, coord)`, `DeclList(decls, coord)`,
`ParamList(params, coord)`, `StaticAssert(cond, message, coord)`, `Alignas(
alignment, coord)`, and `StructRef(name, type, field, coord)`.

The constructors accept `coord=None` unless stated otherwise. `Coord(file,
line, column=None)` stringifies as `file:line` or `file:line:column`.

### Lexing: `pycparser.c_lexer`

`Token(type, value, lineno, column)` is a slots dataclass. `CLexer(error_func,
on_lbrace_func, on_rbrace_func, type_lookup_func)` supports `input(text,
filename="")`, the `filename` property, and repeated `token()` calls until
`None`. It recognizes identifiers, typedef identifiers, integer/floating/
character/string constants, C keywords, operators, punctuation, preprocessor
hashes/pragmas, and tracks line/column coordinates. The callbacks receive
lexing errors, opening/closing braces, and identifier type lookups exactly when
those events occur.

### Parsing: `pycparser.c_parser`

`CParser(lex_optimize=True, lexer=CLexer, lextab="pycparser.lextab",
yacc_optimize=True, yacctab="pycparser.yacctab", yacc_debug=False,
taboutputdir="")` accepts legacy options and builds a fresh lexer. `parse(text,
filename="", debug=False)` returns a `FileAST`, resets parser scope for every
call, preserves coordinates, distinguishes typedef names from identifiers,
and raises `ParseError` with a useful coordinate/message for invalid C.

### Generation and transforms

`CGenerator(reduce_parentheses=False)` exposes `visit(node)` and
`generic_visit(node)` and returns deterministic C text. It handles declarations,
expressions, functions, compound statements, control flow, structs/unions,
enums, casts, initializers, pragmas, and C11 atomic/static-assert forms.
When `reduce_parentheses=True`, unnecessary binary-expression parentheses may
be removed while preserving precedence.

`fix_switch_cases(switch_node)` normalizes consecutive/fall-through `case` and
`default` nodes in a `Switch` compound and returns the same switch object.
`fix_atomic_specifiers(decl)` normalizes `_Atomic(type)` declaration wrappers,
preserves coordinates, and returns the declaration object.

## Implementation Notes

Keep public exception and class identity stable across imports. Implement AST
nodes with explicit ordered fields and child discovery; do not substitute a
generic dictionary tree. Parser state must be reset between calls. File
operations are local and deterministic. The package metadata must remain
consistent with `__version__ = "3.00"` and must not require SCM state.
