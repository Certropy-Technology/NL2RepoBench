# String Width Traceability

| Public contract | Private behavior group | Frozen leaves | Coverage |
| --- | --- | ---: | --- |
| package identity and ESM export | package shape | 3 | name/version/type/export map, declaration, callable default |
| ordinary and East Asian widths | basic and East Asian width | 10 | ASCII, CJK, mixed text, non-string values, long input, ambiguous option |
| terminal control behavior | controls and ANSI | 7 | tabs, controls, newlines, CSI/OSC stripping and counted escape bytes |
| grapheme and combining behavior | combining and Hangul | 8 | combining marks, spacing marks, Hangul syllable pieces, malformed surrogate |
| emoji presentation | emoji and variation | 12 | RGI emoji, ZWJ, keycaps, flags, regional indicators, skin tone, VS15/VS16 |
| boundaries and repeatability | boundaries and determinism | 13 | ignorable characters, prepend, soft hyphen, long mixed strings, stable repeats |

The 53 rows above are the complete frozen denominator. The verifier calls only
the default export through a UID-separated candidate subprocess and derives all
counts from individual `node:test` leaves. No private assertion needs a network
service, mutable clock, filesystem path, callback, symbol, or candidate-owned
report. The 229 upstream AVA declarations are inventory evidence, not a copied
production test suite.
