#!/usr/bin/env python3
"""Child-side observation adapter for the bounded sqlparse contract."""
from __future__ import annotations

import argparse
from io import StringIO
import json
from pathlib import Path
import sys
import traceback


def _configure_candidate(candidate_site: str) -> None:
    while candidate_site in sys.path:
        sys.path.remove(candidate_site)
    sys.path.insert(0, candidate_site)


def _pairs(stream):
    return [[str(token_type), value] for token_type, value in stream]


def _non_ws_pairs(stream):
    return [
        [str(token_type), value]
        for token_type, value in stream
        if not str(token_type).startswith("Token.Text.Whitespace")
    ]


def api_surface():
    import sqlparse
    from sqlparse.exceptions import SQLParseError
    from sqlparse.lexer import Lexer

    modules = [
        "sqlparse.engine",
        "sqlparse.filters",
        "sqlparse.formatter",
        "sqlparse.keywords",
        "sqlparse.lexer",
        "sqlparse.sql",
        "sqlparse.tokens",
        "sqlparse.utils",
    ]
    for name in modules:
        __import__(name)
    return {
        "version": sqlparse.__version__,
        "all": list(sqlparse.__all__),
        "root": {name: callable(getattr(sqlparse, name, None)) for name in ("parse", "parsestream", "format", "split")},
        "classes": [SQLParseError.__mro__[1].__name__, Lexer.__name__],
        "modules": modules,
    }


def token_hierarchy():
    from sqlparse import tokens as T

    return {
        "names": [
            str(T.Keyword),
            str(T.Keyword.DML),
            str(T.Name.Placeholder),
            str(T.Literal.String.Single),
            str(T.Number.Float),
        ],
        "membership": [
            T.Keyword.DML in T.Keyword,
            T.Name.Placeholder in T.Name,
            T.String.Single in T.Literal,
            T.Operator.Comparison in T.Operator,
            T.Punctuation in T.Keyword,
        ],
        "aliases": [
            T.DML is T.Keyword.DML,
            T.String is T.Literal.String,
            T.Number is T.Literal.Number,
        ],
    }


def tokenize_simple():
    from sqlparse import lexer

    return {
        "generator": type(lexer.tokenize("select * from foo; ")).__name__,
        "tokens": _pairs(lexer.tokenize("select * from foo;")),
    }


def tokenize_literals():
    from sqlparse import lexer

    text = "VALUES (-7, .5, 6.02e23, 'it''s', \"Col\", `tick`, [bracket]);"
    return _non_ws_pairs(lexer.tokenize(text))


def tokenize_comments_placeholders():
    from sqlparse import lexer

    text = "-- head\nSELECT :name, :1, ?, %s, %(item)s, $tag /* tail */"
    return _non_ws_pairs(lexer.tokenize(text))


def lexer_inputs():
    from sqlparse import lexer
    from sqlparse.lexer import Lexer

    default_one = Lexer.get_default_instance()
    default_two = Lexer.get_default_instance()
    stream = StringIO("SELECT ö")
    return {
        "singleton": default_one is default_two,
        "stream": _pairs(lexer.tokenize(stream)),
        "bytes": _pairs(lexer.tokenize("SELECT café".encode("latin-1"), encoding="latin-1")),
        "error": _pairs(lexer.tokenize("FOO{"))[-1],
    }


def lexer_customization():
    from sqlparse import keywords
    from sqlparse import tokens as T
    from sqlparse.lexer import Lexer

    custom = Lexer()
    custom.clear()
    custom.set_SQL_REGEX(keywords.SQL_REGEX)
    custom.add_keywords({"FOOBAR": T.Keyword})
    first = _non_ws_pairs(custom.get_tokens("foobar baz"))
    custom.default_initialization()
    second = _non_ws_pairs(custom.get_tokens("select foobar"))
    return {"custom": first, "reset": second, "is_keyword": [str(x) for x in custom.is_keyword("select")]}


def split_basic():
    import sqlparse

    text = "select 'a;b' AS value; select 2;"
    return {
        "normal": sqlparse.split(text),
        "stripped": sqlparse.split(text, strip_semicolon=True),
    }


def split_comments():
    import sqlparse

    text = "select 1; -- first\nselect 2;\n"
    return sqlparse.split(text)


def split_dollar_quoted():
    import sqlparse

    text = "CREATE FUNCTION f() RETURNS void AS $$BEGIN RAISE NOTICE 'x;y'; END;$$ LANGUAGE plpgsql; SELECT 2;"
    return sqlparse.split(text)


def parsestream_behavior():
    import sqlparse

    generator = sqlparse.parsestream(StringIO("SELECT 1; UPDATE t SET x = 2;"))
    statements = list(generator)
    return {
        "generator": type(generator).__name__,
        "values": [str(statement) for statement in statements],
        "types": [statement.get_type() for statement in statements],
        "classes": [type(statement).__name__ for statement in statements],
    }


def parse_preservation():
    import sqlparse

    text = "select\r\n* from café;"
    statements = sqlparse.parse(text)
    return {
        "container": type(statements).__name__,
        "count": len(statements),
        "value": str(statements[0]),
        "type": statements[0].get_type(),
        "first": [str(statements[0].token_first().ttype), statements[0].token_first().normalized],
    }


def statement_types():
    import sqlparse

    inputs = [
        "SELECT 1",
        "INSERT INTO t VALUES (1)",
        "UPDATE t SET x = 1",
        "DELETE FROM t",
        "CREATE TABLE t (x int)",
        "DROP TABLE t",
        "WITH q AS (SELECT 1) SELECT * FROM q",
        "EXPLAIN SELECT 1",
        "foo bar",
    ]
    return [[text, sqlparse.parse(text)[0].get_type()] for text in inputs]


def identifier_metadata():
    import sqlparse
    from sqlparse import sql

    statement = sqlparse.parse('SELECT sch.tbl.col AS "Alias" FROM db.users u')[0]
    select_identifier = next(token for token in statement.tokens if isinstance(token, sql.Identifier))
    from_seen = False
    table_identifier = None
    for token in statement.tokens:
        if token.normalized == "FROM":
            from_seen = True
        elif from_seen and isinstance(token, sql.Identifier):
            table_identifier = token
            break
    assert table_identifier is not None
    return {
        "select": {
            "value": str(select_identifier),
            "name": select_identifier.get_name(),
            "real": select_identifier.get_real_name(),
            "parent": select_identifier.get_parent_name(),
            "alias": select_identifier.get_alias(),
            "has_alias": select_identifier.has_alias(),
            "wildcard": select_identifier.is_wildcard(),
        },
        "table": {
            "value": str(table_identifier),
            "name": table_identifier.get_name(),
            "real": table_identifier.get_real_name(),
            "parent": table_identifier.get_parent_name(),
            "alias": table_identifier.get_alias(),
        },
    }


def identifier_list():
    import sqlparse
    from sqlparse import sql

    statement = sqlparse.parse("SELECT a, b AS bee, sch.c, d.* FROM tbl")[0]
    group = next(token for token in statement.tokens if isinstance(token, sql.IdentifierList))
    identifiers = list(group.get_identifiers())
    return [
        {
            "value": str(identifier),
            "name": identifier.get_name(),
            "real": identifier.get_real_name(),
            "parent": identifier.get_parent_name(),
            "alias": identifier.get_alias(),
            "wildcard": identifier.is_wildcard(),
        }
        for identifier in identifiers
    ]


def function_parameters():
    import sqlparse
    from sqlparse import sql

    statement = sqlparse.parse("SELECT calc(a, 2, nested('x')) AS value")[0]
    identifier = next(token for token in statement.tokens if isinstance(token, sql.Identifier))
    function = next(token for token in identifier.tokens if isinstance(token, sql.Function))
    parameters = list(function.get_parameters())
    return {
        "name": function.get_name(),
        "alias": identifier.get_alias(),
        "parameter_values": [str(parameter) for parameter in parameters],
        "parameter_classes": [type(parameter).__name__ for parameter in parameters],
        "within": [parameter.within(sql.Function) for parameter in parameters],
    }


def where_comparison():
    import sqlparse
    from sqlparse import sql

    statement = sqlparse.parse("SELECT * FROM users WHERE age >= 18 AND status = 'active'")[0]
    where = next(token for token in statement.tokens if isinstance(token, sql.Where))
    comparisons = [token for token in where.tokens if isinstance(token, sql.Comparison)]
    return {
        "where": str(where),
        "comparisons": [
            {
                "value": str(comparison),
                "left": str(comparison.left),
                "right": str(comparison.right),
                "operator": next(
                    token.value
                    for token in comparison.tokens
                    if str(token.ttype) == "Token.Operator.Comparison"
                ),
            }
            for comparison in comparisons
        ],
    }


def nested_groups():
    import sqlparse
    from sqlparse import sql

    statement = sqlparse.parse("SELECT (a + 2) AS total FROM (SELECT a FROM t) sub")[0]
    groups = [type(token).__name__ for token in statement.get_sublists()]
    parentheses = [token for token in statement.flatten() if token.value in {"(", ")"}]
    inner_name = next(token for token in statement.flatten() if token.value == "a")
    return {
        "groups": groups,
        "flatten": [[str(token.ttype), token.value] for token in statement.flatten()],
        "parentheses": [token.value for token in parentheses],
        "within_identifier": inner_name.within(sql.Identifier),
        "offset_token": statement.get_token_at_offset(8).value,
    }


def token_helpers():
    import sqlparse
    from sqlparse import sql
    from sqlparse import tokens as T

    keyword = sql.Token(T.Keyword, "select")
    name = sql.Token(T.Name, "Foo")
    statement = sqlparse.parse("  SELECT /*x*/ col FROM tbl")[0]
    first_all = statement.token_first(skip_ws=False)
    first_code = statement.token_first(skip_ws=True, skip_cm=True)
    select_index = statement.token_index(first_code)
    next_index, next_token = statement.token_next(select_index, skip_ws=True, skip_cm=True)
    previous_index, previous_token = statement.token_prev(next_index, skip_ws=True, skip_cm=True)
    return {
        "keyword": {
            "normalized": keyword.normalized,
            "is_keyword": keyword.is_keyword,
            "match_exact": keyword.match(T.Keyword, "SELECT"),
            "match_regex": keyword.match(T.Keyword, r"SEL.*", regex=True),
        },
        "name": {
            "normalized": name.normalized,
            "case_sensitive": name.match(T.Name, "foo"),
            "exact": name.match(T.Name, "Foo"),
        },
        "navigation": {
            "first_all": first_all.value,
            "first_code": first_code.value,
            "next": [next_index, next_token.value, type(next_token).__name__],
            "previous": [previous_index, previous_token.value],
        },
    }


def format_case():
    import sqlparse

    text = 'select Foo, "Bar" from MyTable where Foo = 1; -- select Foo\n'
    return {
        "upper_lower": sqlparse.format(text, keyword_case="upper", identifier_case="lower"),
        "capitalize_upper": sqlparse.format(text, keyword_case="capitalize", identifier_case="upper"),
    }


def format_whitespace_comments():
    import sqlparse

    text = "/* lead */\nselect  a  -- inline\nfrom   t  where ( 1 = 2 )\n"
    return {
        "comments": sqlparse.format(text, strip_comments=True),
        "both": sqlparse.format(text, strip_comments=True, strip_whitespace=True),
    }


def format_operators():
    import sqlparse

    text = "SELECT a+b*c, x>=10, payload->>'name' FROM t"
    return sqlparse.format(text, use_space_around_operators=True)


def format_reindent():
    import sqlparse

    text = "select a,b,sum(c) as total from sales where x=1 and y in (select y from allowed) order by a,b"
    return sqlparse.format(text, keyword_case="upper", reindent=True, indent_width=2)


def format_layout_options():
    import sqlparse

    text = "select alpha,beta,gamma,delta from sample where alpha=1"
    return {
        "comma_first": sqlparse.format(
            text,
            keyword_case="upper",
            reindent=True,
            comma_first=True,
            wrap_after=12,
            indent_width=4,
        ),
        "tabs": sqlparse.format(
            "select a,b from t where x=1",
            keyword_case="upper",
            reindent=True,
            indent_tabs=True,
        ),
    }


def format_string_output():
    import sqlparse

    return {
        "truncate": sqlparse.format("SELECT 'abcdefghijkl', name FROM t", truncate_strings=8, truncate_char="[...]"),
        "python": sqlparse.format("SELECT 1;\nSELECT 'x';", keyword_case="lower", output_format="python"),
        "sql": sqlparse.format("select 1", output_format="sql"),
    }


def format_invalid_options():
    import sqlparse

    checks = [
        {"keyword_case": "sideways"},
        {"identifier_case": "sideways"},
        {"output_format": "json"},
        {"indent_width": 0},
        {"wrap_after": -1},
        {"comma_first": "yes"},
    ]
    results = []
    for options in checks:
        try:
            sqlparse.format("select 1", **options)
        except BaseException as error:
            results.append([type(error).__name__, str(error)])
        else:
            results.append([None, None])
    return results


SCENARIOS = {
    "api-surface": api_surface,
    "token-hierarchy": token_hierarchy,
    "tokenize-simple": tokenize_simple,
    "tokenize-literals": tokenize_literals,
    "tokenize-comments-placeholders": tokenize_comments_placeholders,
    "lexer-inputs": lexer_inputs,
    "lexer-customization": lexer_customization,
    "split-basic": split_basic,
    "split-comments": split_comments,
    "split-dollar-quoted": split_dollar_quoted,
    "parsestream-behavior": parsestream_behavior,
    "parse-preservation": parse_preservation,
    "statement-types": statement_types,
    "identifier-metadata": identifier_metadata,
    "identifier-list": identifier_list,
    "function-parameters": function_parameters,
    "where-comparison": where_comparison,
    "nested-groups": nested_groups,
    "token-helpers": token_helpers,
    "format-case": format_case,
    "format-whitespace-comments": format_whitespace_comments,
    "format-operators": format_operators,
    "format-reindent": format_reindent,
    "format-layout-options": format_layout_options,
    "format-string-output": format_string_output,
    "format-invalid-options": format_invalid_options,
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scenario", choices=sorted(SCENARIOS), required=True)
    parser.add_argument("--candidate-site", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    _configure_candidate(args.candidate_site)
    try:
        value = SCENARIOS[args.scenario]()
        report = {"schema_version": "1.0", "scenario": args.scenario, "ok": True, "value": value}
    except BaseException as error:
        report = {
            "schema_version": "1.0",
            "scenario": args.scenario,
            "ok": False,
            "error": type(error).__name__,
            "message": str(error),
            "traceback": traceback.format_exc()[-3000:],
        }
    args.output.write_text(json.dumps(report, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
