# Project Description

Create an installable Python project named `fonttools` that provides a pure-Python subset of the fontTools library. The project should expose the documented modules under the `fontTools` package and be usable from an empty workspace after installation with `pip install .`. The implementation must be deterministic and must not require network access, native compilation, optional font compression libraries, or external services at runtime.

# Natural Language Instruction

Create the installable `fonttools` Python project from an empty workspace.
Implement the documented pure-Python font geometry, text, transform, builder,
pen, and font-table APIs without optional native integrations.

# Supports or Environment Configuration

- Use CPython 3.12 and the package metadata in `task.toml`; expose import
  package `fontTools` and the declared console entry point.
- Keep runtime behavior local and deterministic. Agent, candidate, verifier,
  Oracle, and controls run with no network access.

# Project Directory Structure

```text
workspace/
├── pyproject.toml
└── fontTools/
    ├── __init__.py
    ├── misc/
    ├── colorLib/geometry.py
    ├── fontBuilder.py
    ├── pens/ttGlyphPen.py
    └── ttLib/
```

# API Usage Guide

The API Usage Guide below is authoritative for module imports, function and
class signatures, return shapes, and font boundary behavior.

# Implementation Notes

Implement the bounded public subset in pure Python. Do not invent optional
compression, GUI, plotting, or native-extension behavior.

# Examples

```python
from fontTools.misc import arrayTools
arrayTools.calcBounds([(0, 1), (2, 3)])
```

```python
from fontTools.misc.transform import Transform
Transform().transformPoint((1, 2))
```

# Error Handling and Boundary Conditions

```python
arrayTools.normRect((2, 3, 0, 1))
```

```python
arrayTools.pointInRect((0, 0), (0, 0, 1, 1))
```

# Supports

- Support Python 3.12 on a Debian-based Linux environment.
- Use the package name `fonttools` and expose the import package `fontTools`.
- Provide a setuptools-compatible `setup.py` or equivalent build configuration, with version `4.63.1.dev0`, Python requirement `>=3.10`, and the `fonttools` console entry point.
- Implement these modules and public symbols: `fontTools.misc.arrayTools`, `fontTools.misc.fixedTools`, `fontTools.misc.textTools`, `fontTools.misc.transform`, `fontTools.colorLib.geometry`, `fontTools.fontBuilder`, `fontTools.pens.ttGlyphPen`, and `fontTools.ttLib`.
- Keep the core implementation pure Python. Optional extras such as Cython acceleration, WOFF compression, SciPy, lxml, and GUI or plotting integrations are outside this task.

# API Usage Guide

## `fontTools.misc.arrayTools`

Implement the functions `calcBounds(array)`, `calcIntBounds(array, round=otRound)`, `updateBounds(bounds, p, min=min, max=max)`, `pointInRect(p, rect)`, `pointsInRect(array, rect)`, `vectorLength(vector)`, `asInt16(array)`, `normRect(rect)`, `scaleRect(rect, x, y)`, `offsetRect(rect, dx, dy)`, `insetRect(rect, dx, dy)`, `sectRect(rect1, rect2)`, `unionRect(rect1, rect2)`, `rectCenter(rect)`, `rectArea(rect)`, `intRect(rect)`, `quantizeRect(rect, factor=1)`, and `pairwise(iterable, reverse=False)`.

Points are `(x, y)` pairs and rectangles are `(xMin, yMin, xMax, yMax)`. Bounds preserve the input numeric types where arithmetic permits. Empty `calcBounds` returns `(0, 0, 0, 0)`. `pointsInRect` returns a boolean list in input order; rectangle edges are included for point tests, while `sectRect` treats zero-area contact as no intersection. `normRect` orders both axes. `intRect` floors minima and ceils maxima. `quantizeRect` normalizes first, expands outward to the requested positive integer factor, and raises `ValueError` for a factor below one. `pairwise` yields adjacent pairs and closes the cycle; `reverse=True` traverses the input backwards.

## `fontTools.misc.fixedTools`

Implement `fixedToFloat(value, precisionBits)`, `floatToFixed(value, precisionBits)`, `floatToFixedToFloat(value, precisionBits)`, `fixedToStr(value, precisionBits)`, `strToFixed(string, precisionBits)`, `strToFixedToFloat(string, precisionBits)`, `floatToFixedToStr(value, precisionBits)`, `ensureVersionIsLong(value)`, and `versionToFixed(value)`, plus the constant `MAX_F2DOT14`. Fixed-point conversion uses binary fractional bits and fontTools' OpenType rounding convention. String helpers use the shortest stable decimal representation of the rounded fixed-point value. Version helpers interpret decimal strings and `0x` hexadecimal strings and convert small numeric versions to 16.16 fixed-point integers.

## `fontTools.misc.textTools`

Implement `Tag`, `readHex`, `deHexStr`, `hexStr`, `num2binary`, `binary2num`, `caselessSort`, `pad`, `tostr`, `tobytes`, `bytechr`, `byteord`, `strjoin`, `bytesjoin`, and the compatibility alias `safeEval`. Text encoding defaults to ASCII, binary/text conversions must preserve the documented error behavior, hexadecimal input may contain whitespace, and `pad` must return bytes padded with null bytes to a multiple of the requested size.

## `fontTools.misc.transform`

Implement the immutable `Transform(xx=1, xy=0, yx=0, yy=1, dx=0, dy=0)` affine tuple and the functions/constants `Identity`, `Offset(x=0, y=0)`, and `Scale(x, y=None)`. Provide `transformPoint`, `transformPoints`, `transformVector`, `transformVectors`, `translate`, `scale`, `rotate` (radians), `skew` (radians), `transform`, `reverseTransform`, `inverse`, `toPS`, `toDecomposed`, and boolean identity behavior. Matrix composition must be consistent with the point transformation convention, and transform operations must return new values without mutating the original.

## `fontTools.colorLib.geometry`

Provide `Circle(centre, radius)` with `round()`, `inside(outer_circle, tolerance=...)`, `concentric(other)`, and `move(dx, dy)`, plus `round_start_circle_stable_containment(c0, r0, c1, r1)`. Circle centers are 2-tuples, `round()` uses OpenType rounding, `move()` updates the center in place, and containment decisions must remain stable after rounding.

## Minimal font construction and loading

Provide `FontBuilder` from `fontTools.fontBuilder`, `TTGlyphPen` from `fontTools.pens.ttGlyphPen`, and `TTFont`/`newTable` from `fontTools.ttLib`. Support building a minimal TrueType font with a glyph order, character map, glyph outlines, horizontal metrics and headers, names, and a `post`/`maxp` table; saving to a binary stream; reopening with `TTFont`; reading the glyph order, best cmap, table keys, and glyph count; and creating a table object with `newTable(tag)`. Context-manager and close behavior for `TTFont` should be compatible with normal file-like use.

# Implementation Notes

- Organize the project under `Lib/fontTools` or another standard package layout that the build configuration maps to `fontTools`.
- Preserve public return shapes and exception behavior. Tuples may be represented as tuples in Python APIs; JSON-facing tools are not part of the package API.
- Do not copy private tests or depend on the upstream checkout at runtime. The evaluator runs with no network and installs only build dependencies baked into the image.
- Include enough package metadata for editable or regular installation and ensure imports work from an installed target rather than only from the repository root.
- The evaluator focuses on deterministic behavior in the API groups above. Optional native acceleration and external integrations are intentionally excluded from the required contract.
