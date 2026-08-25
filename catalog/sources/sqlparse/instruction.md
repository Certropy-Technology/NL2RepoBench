# Build `sqlparse`

Create a complete, installable Python project named `sqlparse` from an empty
workspace. The package is a non-validating SQL lexer, splitter, parser, and
formatter. Implement the bounded public contract below with behavior compatible
with the frozen `sqlparse` source revision whose package version is
`0.5.4.dev0`.

Do not depend on a preinstalled copy of `sqlparse`, an upstream checkout, or
network access at runtime. Do not copy source or tests from the reference
project. The implementation must tokenize and group the specified inputs for
real; hard-coded answers for the examples are not an acceptable parser.

## Project Description

`sqlparse` recognizes lexical SQL tokens without connecting to a database and
without validating a statement against a database-specific grammar. It can:

- turn text, byte strings, or text streams into `(token_type, value)` pairs;
- split scripts while respecting quoted strings, comments, and PostgreSQL
  dollar-quoted bodies;
- parse statements into a mutable tree of `Token` and `TokenList` subclasses;
- expose identifier, function, `WHERE`, comparison, and parenthesis grouping;
- normalize formatting through deterministic case, whitespace, comment,
  operator-spacing, indentation, wrapping, and output filters; and
- customize a standalone `Lexer` by replacing its regular expressions and
  keyword dictionaries.

The scored surface is the local parsing/formatting/tokenization slice in this
specification. It does not require a SQL execution engine or database schema.

## Supports

- Support CPython 3.8 and newer Python 3.x versions.
- Provide an installable distribution and import package both named
  `sqlparse`; `sqlparse.__version__` is exactly `"0.5.4.dev0"`.
- The package has no third-party runtime dependency. Build tools such as
  Hatchling are build dependencies, not runtime imports.
- Provide a PEP 517 `pyproject.toml` and a source-only build that does not need
  `.git` metadata.
- Preserve input spelling, comments, whitespace, and newline characters unless
  a documented formatting option asks to transform them.
- All operations are deterministic and local. They must not access a network,
  invoke a database, or launch a subprocess.

The command-line `sqlformat` program, documentation files, every upstream SQL
dialect edge case, and undocumented filter internals are outside this bounded
contract. They may be implemented, but the APIs below must not depend on them.

## Package and API Surface

The root package provides these callables:

```python
sqlparse.parse(sql, encoding=None) -> tuple
sqlparse.parsestream(stream, encoding=None) -> generator
sqlparse.format(sql, encoding=None, **options) -> str
sqlparse.split(sql, encoding=None, strip_semicolon=False) -> list[str]
```

Its public metadata is:

```python
sqlparse.__version__ == "0.5.4.dev0"
sqlparse.__all__ == ["engine", "filters", "formatter", "sql", "tokens", "cli"]
```

These modules are importable: `sqlparse.engine`, `sqlparse.filters`,
`sqlparse.formatter`, `sqlparse.keywords`, `sqlparse.lexer`, `sqlparse.sql`,
`sqlparse.tokens`, and `sqlparse.utils`. `SQLParseError` is an `Exception`
subclass imported from `sqlparse.exceptions`; `Lexer` is imported from
`sqlparse.lexer`.

## Token Types and `Token`

`sqlparse.tokens` supplies hierarchical singleton token types. Their string
forms and ancestry behave as follows:

```text
str(T.Keyword)               == "Token.Keyword"
str(T.Keyword.DML)           == "Token.Keyword.DML"
str(T.Name.Placeholder)      == "Token.Name.Placeholder"
str(T.Literal.String.Single) == "Token.Literal.String.Single"
str(T.Number.Float)          == "Token.Literal.Number.Float"

T.Keyword.DML in T.Keyword             is True
T.Name.Placeholder in T.Name           is True
T.String.Single in T.Literal           is True
T.Operator.Comparison in T.Operator    is True
T.Punctuation in T.Keyword             is False
T.DML is T.Keyword.DML                 is True
T.String is T.Literal.String           is True
T.Number is T.Literal.Number           is True
```

`sqlparse.sql.Token(ttype, value)` stores the string value unchanged. Keyword
tokens set `is_keyword=True` and uppercase `normalized`; non-keywords preserve
case in `normalized`. `match(ttype, values, regex=False)` requires token-type
identity, matches keywords case-insensitively, matches non-keywords
case-sensitively, and applies case-insensitive regular expressions to keyword
normalized values. For example, a keyword token `Token(T.Keyword, "select")`
has normalized value `SELECT` and matches both `"SELECT"` and regex
`r"SEL.*"`; `Token(T.Name, "Foo")` matches `"Foo"` but not `"foo"`.

`Token.within(group_class)`, `is_child_of(parent)`, and
`has_ancestor(ancestor)` inspect grouped-parent relationships.

## Lexing and Tokenization

`sqlparse.lexer.tokenize(sql, encoding=None)` returns a generator. It delegates
to `Lexer.get_default_instance().get_tokens(...)`.

For `"select * from foo;"`, the exact sequence is:

```text
(Token.Keyword.DML, "select")
(Token.Text.Whitespace, " ")
(Token.Wildcard, "*")
(Token.Text.Whitespace, " ")
(Token.Keyword, "from")
(Token.Text.Whitespace, " ")
(Token.Name, "foo")
(Token.Punctuation, ";")
```

Ignoring whitespace, tokenizing

```sql
VALUES (-7, .5, 6.02e23, 'it''s', "Col", `tick`, [bracket]);
```

produces, in order:

```text
Keyword VALUES; Punctuation (; Number.Integer -7; Punctuation ,;
Number.Float .5; Punctuation ,; Number.Float 6.02e23; Punctuation ,;
String.Single 'it''s'; Punctuation ,; String.Symbol "Col"; Punctuation ,;
Name `tick`; Punctuation ,; Name [bracket]; Punctuation ); Punctuation ;
```

The full token-type names have the `Token.` hierarchy shown above, for example
`Token.Literal.Number.Integer`, `Token.Literal.Number.Float`, and
`Token.Literal.String.Symbol`.

Ignoring whitespace, tokenizing

```sql
-- head
SELECT :name, :1, ?, %s, %(item)s, $tag /* tail */
```

produces a `Token.Comment.Single` containing `"-- head\n"`, DML `SELECT`, six
`Token.Name.Placeholder` values (`:name`, `:1`, `?`, `%s`, `%(item)s`, `$tag`)
separated by punctuation commas, and a final `Token.Comment.Multiline` value
`"/* tail */"`.

The lexer accepts `io.TextIOBase` streams. It accepts bytes and decodes with the
explicit encoding when supplied; Latin-1 bytes for `"SELECT café"` with
`encoding="latin-1"` yield DML `SELECT`, one whitespace token, and Name
`café`. An unmatched `{` is emitted as `Token.Error` rather than raising.

### Configurable `Lexer`

`Lexer.get_default_instance()` returns the same process-wide object on repeated
calls. A separate `Lexer()` supports:

```python
clear()
set_SQL_REGEX(regex_specs)
add_keywords(keyword_dict)
default_initialization()
is_keyword(value)
get_tokens(text, encoding=None)
```

After `clear()`, loading `sqlparse.keywords.SQL_REGEX`, and adding
`{"FOOBAR": T.Keyword}`, `"foobar baz"` tokenizes as Keyword `foobar`,
whitespace, Name `baz`. `default_initialization()` restores standard syntax, so
`"select foobar"` becomes DML `select`, whitespace, Name `foobar`.
`is_keyword("select")` returns `(T.Keyword.DML, "select")`.

## Statement Splitting and Streams

`split()` returns stripped statement strings while retaining a trailing
semicolon unless `strip_semicolon=True`.

```python
sqlparse.split("select 'a;b' AS value; select 2;")
# ["select 'a;b' AS value;", "select 2;"]

sqlparse.split("select 'a;b' AS value; select 2;", strip_semicolon=True)
# ["select 'a;b' AS value", "select 2"]
```

A line comment after a terminator belongs to that statement:

```python
sqlparse.split("select 1; -- first\nselect 2;\n")
# ["select 1; -- first", "select 2;"]
```

Semicolons inside PostgreSQL dollar-quoted text do not split a statement:

```python
sqlparse.split(
    "CREATE FUNCTION f() RETURNS void AS $$BEGIN RAISE NOTICE 'x;y'; "
    "END;$$ LANGUAGE plpgsql; SELECT 2;"
)
# [
#   "CREATE FUNCTION f() RETURNS void AS $$BEGIN RAISE NOTICE 'x;y'; "
#   "END;$$ LANGUAGE plpgsql;",
#   "SELECT 2;",
# ]
```

`parsestream(StringIO("SELECT 1; UPDATE t SET x = 2;"))` returns a generator of
two `Statement` objects. Their strings are `"SELECT 1; "` and
`"UPDATE t SET x = 2;"`; their `get_type()` values are `SELECT` and `UPDATE`.

## Parsing and Grouped Objects

`parse()` returns a tuple of `sqlparse.sql.Statement` objects and preserves the
original text. Parsing `"select\r\n* from café;"` returns one statement whose
string is byte-for-character identical, whose type is `SELECT`, and whose first
non-whitespace token is DML with normalized value `SELECT`.

`Statement.get_type()` ignores leading whitespace/comments, follows a leading
`WITH` CTE to its DML statement, and returns these values:

| input | result |
| --- | --- |
| `SELECT 1` | `SELECT` |
| `INSERT INTO t VALUES (1)` | `INSERT` |
| `UPDATE t SET x = 1` | `UPDATE` |
| `DELETE FROM t` | `DELETE` |
| `CREATE TABLE t (x int)` | `CREATE` |
| `DROP TABLE t` | `DROP` |
| `WITH q AS (SELECT 1) SELECT * FROM q` | `SELECT` |
| `EXPLAIN SELECT 1` | `UNKNOWN` |
| `foo bar` | `UNKNOWN` |

### `TokenList` navigation

`TokenList` is iterable and supports `token_first(skip_ws=True, skip_cm=False)`,
`token_next(index, skip_ws=True, skip_cm=False)`,
`token_prev(index, skip_ws=True, skip_cm=False)`, `token_index(token)`,
`get_sublists()`, `flatten()`, and `get_token_at_offset(offset)`.

For `"  SELECT /*x*/ col FROM tbl"`, `token_first(skip_ws=False)` is the first
single-space token, while `token_first(skip_ws=True, skip_cm=True)` is
`SELECT`. From the top-level `SELECT` index, the next token while skipping
whitespace and comments is an `Identifier` with value `col`; navigating back
returns `SELECT`.

`flatten()` recursively yields every leaf token in source order. For
`"SELECT (a + 2) AS total FROM (SELECT a FROM t) sub"`, flattened punctuation
contains `(`, `)`, `(`, `)` in that order; the first `a` is within an
`Identifier`; and offset 8 resolves to token `a`.

### Identifiers and lists

`sqlparse.sql.Identifier` provides `get_name()`, `get_real_name()`,
`get_parent_name()`, `get_alias()`, `has_alias()`, and `is_wildcard()`.
Quoted aliases are returned without quotes.

For `SELECT sch.tbl.col AS "Alias" FROM db.users u`:

- `sch.tbl.col AS "Alias"` has name/alias `Alias`, real name `tbl`, parent
  name `sch`, `has_alias()` true, and is not a wildcard;
- `db.users u` has name/alias `u`, real name `users`, and parent name `db`.

In `SELECT a, b AS bee, sch.c, d.* FROM tbl`, the select projection is an
`IdentifierList`; `get_identifiers()` yields four entries in order:

| value | name | real | parent | alias | wildcard |
| --- | --- | --- | --- | --- | --- |
| `a` | `a` | `a` | `None` | `None` | false |
| `b AS bee` | `bee` | `b` | `None` | `bee` | false |
| `sch.c` | `c` | `c` | `sch` | `None` | false |
| `d.*` | `*` | `*` | `d` | `None` | true |

### Functions, `WHERE`, and comparisons

For `SELECT calc(a, 2, nested('x')) AS value`, the grouped `Function` has name
`calc`; the enclosing identifier alias is `value`; `get_parameters()` yields
`a`, `2`, and `nested('x')` with classes `Identifier`, `Token`, and `Function`.
Each returned parameter reports that it is within a `Function`.

For `SELECT * FROM users WHERE age >= 18 AND status = 'active'`, the final
`Where` string is exactly `WHERE age >= 18 AND status = 'active'`. It contains
two `Comparison` groups. Their values/left/operator/right observations are:

```text
age >= 18          | age    | >= | 18
status = 'active'  | status | =  | 'active'
```

## Formatting

`format()` always returns a string. Quoted identifiers and comment contents are
not case-converted.

### Case conversion

For this input:

```text
select Foo, "Bar" from MyTable where Foo = 1; -- select Foo\n
```

`keyword_case="upper", identifier_case="lower"` returns:

```text
SELECT foo, "Bar" FROM mytable WHERE foo = 1; -- select Foo\n
```

`keyword_case="capitalize", identifier_case="upper"` returns:

```text
Select FOO, "Bar" From MYTABLE Where FOO = 1; -- select Foo\n
```

### Comments and whitespace

For:

```text
/* lead */
select  a  -- inline
from   t  where ( 1 = 2 )
```

`strip_comments=True` returns `"select  a\nfrom   t  where ( 1 = 2 )\n"`.
Adding `strip_whitespace=True` returns `"select a from t where (1 = 2)"`.

`use_space_around_operators=True` transforms

```text
SELECT a+b*c, x>=10, payload->>'name' FROM t
```

into

```text
SELECT a + b * c, x >= 10, payload ->> 'name' FROM t
```

### Reindentation

Formatting

```text
select a,b,sum(c) as total from sales where x=1 and y in (select y from allowed) order by a,b
```

with `keyword_case="upper", reindent=True, indent_width=2` returns exactly:

```sql
SELECT a,
       b,
       sum(c) AS total
FROM sales
WHERE x=1
  AND y IN
    (SELECT y
     FROM allowed)
ORDER BY a,
         b
```

Formatting `select alpha,beta,gamma,delta from sample where alpha=1` with
uppercase keywords, `reindent=True`, `comma_first=True`, `wrap_after=12`, and
`indent_width=4` returns:

```sql
SELECT alpha,beta
     , gamma
     , delta
FROM SAMPLE
WHERE alpha=1
```

Formatting `select a,b from t where x=1` with uppercase keywords,
`reindent=True`, and `indent_tabs=True` returns:

```text
SELECT a,\n\tb\nFROM t\nWHERE x=1
```

### String and output filters

`truncate_strings=8, truncate_char="[...]"` changes
`SELECT 'abcdefghijkl', name FROM t` to
`SELECT 'abcdefgh[...]', name FROM t`.

`output_format="sql"` leaves `select 1` as `select 1`. Formatting
`"SELECT 1;\nSELECT 'x';"` with lower-case keywords and
`output_format="python"` returns exactly:

```python
sql = 'select 1;'
sql2 = ' '
        'select \'x\';'
```

### Option validation

Invalid formatting options raise `sqlparse.exceptions.SQLParseError` with
these messages:

```text
keyword_case="sideways"    -> Invalid value for keyword_case: 'sideways'
identifier_case="sideways" -> Invalid value for identifier_case: 'sideways'
output_format="json"       -> Unknown output format: 'json'
indent_width=0              -> indent_width requires a positive integer
wrap_after=-1               -> wrap_after requires a positive integer
comma_first="yes"          -> comma_first requires a boolean value
```

## Implementation Notes

- Preserve the distinction between lexical tokenization and grouped parsing.
  `tokenize()` must not construct `Statement` objects; `parse()` must group the
  flat stream into the documented `TokenList` subclasses.
- Do not validate SQL against a database grammar. Unknown statements remain
  parseable and report `UNKNOWN` from `get_type()`.
- Preserve source-order and exact input values on tokens. Formatting constructs
  a transformed serialization without mutating the caller's input string.
- The default lexer singleton must be initialized safely, while separately
  constructed lexers remain independently configurable.
