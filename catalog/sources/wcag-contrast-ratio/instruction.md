# Build wcag-contrast-ratio Package

## Project Description

Recreate the `wcag-contrast-ratio` library from scratch in an empty workspace. The
library implements the colour-contrast portion of the Web Content Accessibility
Guidelines (WCAG 2.0): given two colours it computes a contrast ratio using
relative luminance, and it answers whether that ratio satisfies the AA and AAA
conformance levels for normal or large text.

The intended users are accessibility auditors, design-system tooling, and test
suites that need to check foreground/background colour pairs without pulling in a
full graphics stack. The whole library is pure Python and depends only on the
standard library.

## Supports

- Python 3.12 (the reference implementation uses `from __future__ import division`
  and otherwise plain Python 3 syntax).
- No runtime dependencies of any kind.
- Installation is done from the project root with an editable, isolated-free
  install, for example:
  `python -m pip install --no-build-isolation --no-deps --no-index -e .`
- The distributable package name is `wcag-contrast-ratio`; the importable module is
  `wcag_contrast_ratio`.
- The module must expose its public API through the package `__init__`, i.e.
  `import wcag_contrast_ratio` is enough to reach every documented function. The
  implementation lives in a `wcag_contrast_ratio/contrast.py` submodule that the
  package re-exports with a star import; the submodule must declare
  `__all__ = ["rgb", "passes_AA", "passes_AAA"]`.
- There is no command-line entry point.

## API Usage Guide

### `rgb(rgb1, rgb2)`

```python
rgb(rgb1, rgb2)
```

- `rgb1`, `rgb2`: 3-tuples (or any unpackable sequence of exactly three values)
  `(r, g, b)` giving the colour channels. Each channel is a float in the closed
  range `[0.0, 1.0]`, where `0.0` is no intensity and `1.0` is full intensity.
  Values are in the sRGB colour space, *not* 0-255 integers.
- Returns: a `float`, the WCAG contrast ratio between the two colours. The ratio
  is always `>= 1.0`; it is defined as
  `(L_lighter + 0.05) / (L_darker + 0.05)` where `L` is the relative luminance
  of each colour, so the argument order does not matter and the result is
  symmetric.
- Relative luminance is the WCAG standard weighting
  `0.2126*r + 0.7152*g + 0.0722*b` over *linearised* channels, where a channel `v`
  is linearised by `v / 12.92` when `v <= 0.03928` and by
  `((v + 0.055) / 1.055) ** 2.4` otherwise.
- Exceptions: if any channel of either colour falls outside `[0.0, 1.0]`, a
  `ValueError` is raised with the message `"r is out of valid range (0.0 - 1.0)"`,
  `"g is out of valid range (0.0 - 1.0)"`, or
  `"b is out of valid range (0.0 - 1.0)"`, naming the offending channel. Channels
  are validated for `rgb1` first and then `rgb2`, and within a colour in the order
  r, g, b.
- Deterministic: identical inputs always produce the identical float.

Examples:

```python
import wcag_contrast_ratio as contrast

contrast.rgb((1.0, 1.0, 1.0), (0.0, 0.0, 0.0))   # 21.0 (black on white)
contrast.rgb((0.0, 0.0, 0.0), (0.0, 0.0, 0.0))   # 1.0 (a colour against itself)
contrast.rgb((0.0, 0.0, 0.0), (1.0, 1.0, 1.0))   # 21.0 (order does not matter)
```

### `passes_AA(contrast, large=False)`

```python
passes_AA(contrast, large=False)
```

- `contrast`: a `float` contrast ratio, typically the result of `rgb(...)`. The
  value is compared as-is; it is not recomputed or clamped.
- `large`: a `bool`. `False` (the default) applies the normal-text threshold;
  `True` applies the large-text threshold, which is more permissive because large
  glyphs need less contrast.
- Returns: a `bool`. The normal-text threshold is `contrast >= 4.5`; the
  large-text threshold is `contrast >= 3.0`. Both comparisons are inclusive, so a
  ratio exactly equal to the threshold passes.
- No exceptions: any numeric value is accepted.

Examples:

```python
contrast.passes_AA(4.5)              # True  (exactly at the normal threshold)
contrast.passes_AA(4.4999)           # False
contrast.passes_AA(3.0, large=True)  # True  (exactly at the large threshold)
contrast.passes_AA(2.9999, large=True)  # False
```

### `passes_AAA(contrast, large=False)`

```python
passes_AAA(contrast, large=False)
```

- Parameters have the same meaning as for `passes_AA`.
- Returns: a `bool`. The normal-text threshold is `contrast >= 7.0`; the
  large-text threshold is `contrast >= 4.5`. Both comparisons are inclusive.
- No exceptions.

Examples:

```python
contrast.passes_AAA(7.0)              # True
contrast.passes_AAA(6.9999)           # False
contrast.passes_AAA(4.5, large=True)  # True
contrast.passes_AAA(4.4999, large=True)  # False
```

## Implementation Notes

- Keep the module free of I/O, global state, and randomness; every function must
  be a pure function of its arguments.
- The two conformance predicates must be usable with a ratio produced from any
  source, not only from `rgb`, so they must not re-validate their argument.
- The channel-range check belongs to `rgb` alone. Rejecting out-of-range input is
  part of the public contract and the exact message text is asserted.
- Channel ordering within a colour is r, then g, then b; and `rgb1` is validated
  before `rgb2`. An input that violates several constraints at once must report the
  first violation in that order.
- `large` is keyword-usable and defaults to `False` in both predicates.
