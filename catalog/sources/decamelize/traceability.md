# Decamelize Specification Traceability

| Public contract | Private behavior group | Coverage |
| --- | --- | --- |
| Package identity and ESM root export | package-shape | name, version, type, default callable |
| Basic conversion | basic-conversion | empty/short text, lower-to-upper boundaries, punctuation, digits |
| Acronym handling | acronym-boundaries | URL/String, GUI/label, all-uppercase text |
| Unicode handling | unicode | uppercase/lowercase Unicode boundary conversion |
| Separator option | separator | custom, multi-character, and empty separators |
| Uppercase preservation | preserve-uppercase | acronym runs, one-letter boundaries, digit runs |
| Error contract | validation | non-string text and separator TypeErrors |
| Determinism and side effects | boundary | input/options remain unchanged |

Reverse review found no scored assertion requiring a callback, external service,
filesystem fixture, native addon, locale, TTY, clock, or candidate-controlled
report. The upstream timing checks are retained in provenance but excluded from
the fixed denominator because wall-clock thresholds are not deterministic
scoring behavior.
