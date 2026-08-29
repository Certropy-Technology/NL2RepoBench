# Fonttools Task Traceability

The public contract is a reviewed, bounded projection of the frozen upstream revision `e7e00f1b16aef6ede850206df3c100ccde27b2d3`. The private verifier uses only the child-side JSON boundary; it does not import candidate code in the trusted verifier process.

| Contract area | Frozen upstream evidence | Adaptation |
| --- | --- | --- |
| Rectangle and point helpers | `Tests/misc/arrayTools_test.py` and doctests in `Lib/fontTools/misc/arrayTools.py` | Primitive tuple/list inputs and deterministic numeric outputs |
| Fixed-point conversions | `Tests/misc/fixedTools_test.py` and doctests in `Lib/fontTools/misc/fixedTools.py` | Primitive numeric/string calls; warning-producing version conversion is observed by return value |
| Text and binary helpers | `Tests/misc/textTools_test.py`, `Tests/misc/py23_test.py`, and doctests in `Lib/fontTools/misc/textTools.py` | JSON-safe text cases plus child-side scripts for bytes and `Tag` behavior |
| Affine transforms | `Tests/misc/transform_test.py` and doctests in `Lib/fontTools/misc/transform.py` | Child calls to immutable tuple methods with exact return-shape checks |
| Circle geometry | `Tests/colorLib/geometry_test.py` and `Lib/fontTools/colorLib/geometry.py` | Child-side stateful scripts cover rounding, containment, movement, and concentricity |
| Font construction and loading | `Tests/fontBuilder/fontBuilder_test.py`, `Tests/ttLib/ttFont_test.py`, and `Tests/ttLib/ttGlyphSet_test.py` | Generated in-memory minimal TrueType fixture avoids external binary assets |
| Packaging | `setup.py`, `setup.cfg`, and upstream packaging tests | Candidate install is supervised; package metadata and `fonttools --help` are checked through the child boundary |

The static inventory records the full upstream scale separately: 377 implementation Python files, 172 test files, 2,456 discovered test definitions, and source digest `sha256:199bc565192da925cddda9ec9b4a3678b2179bf0e5da68ccefd1bfdbe38dc8b2`. The task denominator is intentionally the 60-leaf bounded adapter suite, not the unmodified upstream collection.
