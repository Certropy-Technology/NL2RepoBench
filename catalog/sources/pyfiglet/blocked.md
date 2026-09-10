# pyfiglet candidate audit

Status: `blocked`

Blocking gate: **spec derivability** (AGENTS.md §7). The candidate is not
publishable as a 0-to-1 repository-generation task, because its hidden assertions
cannot be derived from any legitimate public instruction.

## Candidate

| Field | Value |
| --- | --- |
| task id | `pyfiglet` |
| upstream | `https://github.com/pwaller/pyfiglet` |
| revision | `e7590f2b80a403db9605750df8a51198759757ee` (tag `v1.0.4`) |
| sdist | `pyfiglet-1.0.4.tar.gz`, 1,560,615 bytes, `sha256:db9c9940ed1bf3048deff534ed52ff2dafbbc2cd7610b17bb5eca1df6d4278ef` |
| license | MIT (the bundled FIGfonts carry their own third-party terms) |
| python_requires | `>=3.9` |
| runtime dependencies | none |
| build backend | `setuptools.build_meta:__legacy__` |

Source provenance and license are known and recorded. The freeze itself is sound.

## Why this is blocked

`pyfiglet` renders text by interpreting FIGfont (`.flf`) definition files. The
sdist ships **571 font files** under `pyfiglet/fonts/`. Those files are
third-party artistic assets originating from figlet.org; they are data, not
algorithm.

Any verifier that exercises the real library therefore asserts on outputs that are
a function of that font data. The 80 calibrated scenarios in
`harbor/verifier/run.py` are genuine and reproduce exactly against the frozen
library, but they are not derivable from a public specification:

- 73 scenarios assert **exact multi-line ASCII art** for the fonts `standard`,
  `doom`, `small`, `slant`, and `banner3`. Reproducing those bytes requires the
  exact glyph definitions of each font, down to per-character sub-rows and
  smushing rules.
- One scenario asserts `len(FigletFont.getFonts()) > 100`, which requires shipping
  at least 100 distinct FIGfonts.

An agent starting from an empty workspace under `no-network` has no legitimate way
to obtain these assets. Making the task solvable would require embedding the font
files in the public instruction, which is neither a reasonable specification nor
appropriate redistribution of third-party artwork.

This is exactly the failure mode AGENTS.md §7 prohibits: writing "implement a
library like X" publicly while asserting undisclosed exact behaviour privately.

## What was completed before the block

- Source freeze, digest, license, and upstream revision verified and recorded.
- 80 scenarios authored and calibrated against the frozen library
  (`pyfiglet 1.0.4`, Python 3.12.11) with **0 mismatches**. The verifier follows
  the standard `custom-json-v1` leaf contract and is AST-clean.
- `harbor/solution/solve.sh` uses the offline bundle pattern with sha256
  verification; no network fetch.
- Seven control scripts authored.

These assets are retained so the audit is reproducible, not because the task is
publishable.

## Conditions to unblock

The candidate could only move forward if the task were **redefined** so that the
hidden assertions stop depending on undisclosed font data. Two directions, neither
of which this candidate currently satisfies:

1. Scope the task to the FIGfont *interpreter* and supply the font files as given
   input fixtures described in the public instruction, asserting on rendering
   behaviour for those provided fonts only.
2. Scope the task to the parts of the public API that are independent of font
   content, which would drop nearly all of the current assertions and leave too
   little behaviour to score meaningfully.

Until one of those is designed and re-reviewed, this candidate stays blocked. No
Oracle, control, or publication claim is made.
