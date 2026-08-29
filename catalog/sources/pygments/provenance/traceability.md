# Pygments Traceability

| Scenario group | Public contract | Private leaf IDs |
| --- | --- | --- |
| Package metadata | `__version__`, root exports | metadata |
| Token model | lazy token tree, repr, split, subtype, conversion | tokens |
| Lexing | root `lex`, Python/JSON/JavaScript and options | python-lex, json-lex, javascript-lex, strip-options, bytes-lex, custom-regex |
| Lookup | alias, filename, MIME, guessing, built-in registry | lookup-name, lookup-filename, lookup-mime, lookup-guess, lookup-count, all-lexers-shape |
| Formatting | HTML, terminal, LaTeX, RTF, SVG, outfile, high-level highlight | html-format, html-full, terminal-format, latex-format, rtf-format, svg-format, outfile, highlight |
| Styles/utilities | named styles, escaping, option parsing, deduplication, shebang, regex optimization | style, escape, bool, int, duplicates, shebang, regexopt |
| Errors/CLI | invalid lookup errors and command entry point | invalid-lexer, invalid-formatter, cli-help, cli-highlight |

The adapter reconstructs only declarative requests in the candidate subprocess.
Trusted code never imports candidate modules; it receives one bounded JSON line
per scenario and validates the fixed leaf IDs and projected values.
