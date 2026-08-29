from __future__ import annotations

import json
import sys

from nl2repobench.verification.candidate_client import execute_script, run_console


def _group(ids: list[str], source: str) -> list[dict[str, object]]:
    observed = execute_script(source, timeout_sec=60.0)
    values = observed.value if observed.ok and isinstance(observed.value, list) else []
    leaves = []
    for index, case_id in enumerate(ids):
        passed = index < len(values) and values[index] is True
        leaves.append({
            "id": case_id,
            "status": "passed" if passed else "failed",
            "message": "scenario assertion failed" if not passed else "",
        })
    return leaves


def main() -> int:
    leaves: list[dict[str, object]] = []
    leaves.extend(_group(
        [
            "array-01-empty-bounds", "array-02-bounds", "array-03-integer-bounds",
            "array-04-update-none", "array-05-update-existing", "array-06-point-inside-edge",
            "array-07-point-outside", "array-08-points-mask", "array-09-vector-length",
            "array-10-round-int16", "array-11-normalize-rect", "array-12-scale-rect",
            "array-13-offset-rect", "array-14-inset-rect", "array-15-section",
            "array-16-union", "array-17-area", "array-18-quantize",
        ],
        """
from fontTools.misc import arrayTools as a
def ok(fn):
    try:
        return bool(fn())
    except BaseException:
        return False
result = [
    ok(lambda: a.calcBounds([]) == (0, 0, 0, 0)),
    ok(lambda: a.calcBounds([(2, -1), (5, 4), (-3, 0)]) == (-3, -1, 5, 4)),
    ok(lambda: a.calcIntBounds([(0.4, -0.6), (1.6, 2.2)]) == (0, -1, 2, 2)),
    ok(lambda: a.updateBounds(None, (2, 3)) == (2, 3, 2, 3)),
    ok(lambda: a.updateBounds((-2, -1, 2, 3), (4, 5)) == (-2, -1, 4, 5)),
    ok(lambda: a.pointInRect((0, 5), (0, 0, 10, 10))),
    ok(lambda: not a.pointInRect((11, 5), (0, 0, 10, 10))),
    ok(lambda: a.pointsInRect([(0, 0), (5, 5), (11, 5)], (0, 0, 10, 10)) == [True, True, False]),
    ok(lambda: a.vectorLength((3, 4)) == 5.0),
    ok(lambda: a.asInt16([0, 0.1, 0.5, 0.9, 1.5]) == [0, 0, 1, 1, 2]),
    ok(lambda: a.normRect((100, 200, 0, 10)) == (0, 10, 100, 200)),
    ok(lambda: a.scaleRect((10, 20, 50, 150), 1.5, 2) == (15.0, 40, 75.0, 300)),
    ok(lambda: a.offsetRect((10, 20, 30, 40), 5, 6) == (15, 26, 35, 46)),
    ok(lambda: a.insetRect((10, 20, 50, 60), 5, 10) == (15, 30, 45, 50)),
    ok(lambda: a.sectRect((0, 0, 4, 4), (2, 2, 8, 8)) == (True, (2, 2, 4, 4))),
    ok(lambda: a.unionRect((0, 0, 4, 4), (2, -2, 8, 8)) == (0, -2, 8, 8)),
    ok(lambda: a.rectArea((0, 0, 10, 20)) == 200),
    ok(lambda: a.quantizeRect((72.3, -218.4, 1201.3, 919.1), 10) == (70, -220, 1210, 920)),
]
"""))
    leaves.extend(_group(
        [
            "fixed-19-to-float", "fixed-20-to-fixed", "fixed-21-round-trip",
            "fixed-22-fixed-string", "fixed-23-string-fixed", "fixed-24-string-round-trip",
            "fixed-25-float-string", "fixed-26-version-small", "fixed-27-version-long",
            "fixed-28-version-hex",
        ],
        """
from fontTools.misc import fixedTools as f
def ok(fn):
    try:
        return bool(fn())
    except BaseException:
        return False
result = [
    ok(lambda: f.fixedToFloat(-10139, 14) == -0.61883544921875),
    ok(lambda: f.floatToFixed(-0.61884, 14) == -10139),
    ok(lambda: f.floatToFixedToFloat(-0.61884, 14) == -0.61883544921875),
    ok(lambda: f.fixedToStr(-10139, 14) == '-0.61884'),
    ok(lambda: f.strToFixed('-0.61884', 14) == -10139),
    ok(lambda: f.strToFixedToFloat('-0.61884', 14) == -0.61883544921875),
    ok(lambda: f.floatToFixedToStr(-0.61883544921875, 14) == '-0.61884'),
    ok(lambda: f.ensureVersionIsLong(1.0) == 65536),
    ok(lambda: f.ensureVersionIsLong(65536) == 65536),
    ok(lambda: f.versionToFixed('0x00010000') == 65536),
]
"""))
    leaves.extend(_group(
        [
            "text-29-hex-decode", "text-30-binary-number", "text-31-number-binary",
            "text-32-case-sort", "text-33-text-identity", "text-34-string-join",
            "text-35-safe-eval", "text-36-byte-ordinal", "text-37-empty-join",
            "text-38-hex-case", "text-39-binary-padding-tag",
        ],
        """
from fontTools.misc import textTools as t
def ok(fn):
    try:
        return bool(fn())
    except BaseException:
        return False
result = [
    ok(lambda: t.deHexStr('0a ff 10') == b'\\x0a\\xff\\x10'),
    ok(lambda: t.binary2num('1010 0011') == 163),
    ok(lambda: t.num2binary(163, 8) == '10100011'),
    ok(lambda: t.caselessSort(['b', 'A', 'a']) == ['A', 'a', 'b']),
    ok(lambda: t.tostr('fontTools') == 'fontTools'),
    ok(lambda: t.strjoin(['font', 'tools'], '::') == 'font::tools'),
    ok(lambda: t.safeEval('[1, 2, 3]') == [1, 2, 3]),
    ok(lambda: t.byteord(65) == 65),
    ok(lambda: t.strjoin([]) == ''),
    ok(lambda: t.hexStr([10, 255, 16]) == '0aff10'),
    ok(lambda: t.tobytes('abc') == b'abc' and t.pad(b'abcde', 4) == b'abcde\\x00\\x00\\x00' and t.Tag(b'head').tobytes() == b'head' and t.bytesjoin(['a', 'b'], b':') == b'a:b'),
]
"""))
    leaves.extend(_group(
        [
            "transform-40-point", "transform-41-points", "transform-42-vector",
            "transform-43-vectors", "transform-44-translate", "transform-45-scale",
            "transform-46-rotate", "transform-47-skew", "transform-48-compose",
            "transform-49-reverse-compose", "transform-50-inverse", "transform-51-postscript",
            "transform-52-bool",
        ],
        """
from math import pi
from fontTools.misc.transform import Transform
def ok(fn):
    try:
        return bool(fn())
    except BaseException:
        return False
t = Transform(2, 0, 0, 3, 1, 6)
result = [
    ok(lambda: t.transformPoint((100, 100)) == (201, 306)),
    ok(lambda: t.transformPoints([(0, 0), (1, 2)]) == [(1, 6), (3, 12)]),
    ok(lambda: t.transformVector((3, -4)) == (6, -12)),
    ok(lambda: t.transformVectors([(3, -4), (5, -6)]) == [(6, -12), (10, -18)]),
    ok(lambda: t.translate(4, 5) == Transform(2, 0, 0, 3, 9, 21)),
    ok(lambda: t.scale(2, 3) == Transform(4, 0, 0, 9, 1, 6)),
    ok(lambda: Transform().rotate(pi / 2) == Transform(0, 1, -1, 0, 0, 0)),
    ok(lambda: abs(Transform().skew(pi / 4).yx - 1) < 1e-12 and Transform().skew(pi / 4).xx == 1),
    ok(lambda: t.transform((4, 3, 2, 1, 5, 6)) == Transform(8, 9, 4, 3, 11, 24)),
    ok(lambda: t.reverseTransform((4, 3, 2, 1, 5, 6)) == Transform(8, 6, 6, 3, 21, 15)),
    ok(lambda: t.inverse() == Transform(0.5, 0, 0, 1 / 3, -0.5, -2)),
    ok(lambda: t.toPS() == '[2 0 0 3 1 6]'),
    ok(lambda: not bool(Transform())),
]
"""))
    leaves.extend(_group(
        ["geometry-53-round-circle", "geometry-54-containment", "geometry-55-move-concentric", "geometry-56-stable-containment"],
        """
from fontTools.colorLib.geometry import Circle, round_start_circle_stable_containment
def ok(fn):
    try:
        return bool(fn())
    except BaseException:
        return False
def _move_check(c):
    same = c.concentric(Circle((1, 2), 9))
    c.move(4, -1)
    return same and c.centre == (5, 1)

result = [
    ok(lambda: (lambda r: r.centre == (1, 3) and r.radius == 3)(Circle((1.2, 2.8), 3.4).round())),
    ok(lambda: Circle((3, 4), 2).inside(Circle((0, 0), 10)) and not Circle((0, 0), 10).inside(Circle((3, 4), 2))),
    ok(lambda: _move_check(Circle((1, 2), 3))),
    ok(lambda: (lambda r: r.centre == (1, 1) and r.radius == 1)(round_start_circle_stable_containment((1.2, 1.2), 1.0, (0.0, 0.0), 5.0))),
]
"""))
    leaves.extend(_group(
        ["font-57-builder-round-trip", "font-59-ttfont-empty", "font-60-transform-immutability"],
        """
from io import BytesIO
from fontTools.fontBuilder import FontBuilder
from fontTools.misc.transform import Transform
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib import TTFont, newTable
def ok(fn):
    try:
        return bool(fn())
    except BaseException:
        return False
def build_font():
    fb = FontBuilder(1000, isTTF=True)
    fb.setupGlyphOrder(['.notdef', 'A'])
    fb.setupCharacterMap({65: 'A'})
    pen = TTGlyphPen(None)
    pen.moveTo((0, 0)); pen.lineTo((0, 700)); pen.lineTo((500, 700)); pen.lineTo((500, 0)); pen.closePath()
    fb.setupGlyf({'.notdef': TTGlyphPen(None).glyph(), 'A': pen.glyph()})
    fb.setupHorizontalMetrics({'.notdef': (600, 0), 'A': (600, 0)})
    fb.setupHorizontalHeader(ascent=800, descent=-200)
    fb.setupOS2(sTypoAscender=800, sTypoDescender=-200, usWinAscent=800, usWinDescent=200)
    fb.setupNameTable({'familyName': 'Example', 'styleName': 'Regular', 'uniqueFontIdentifier': 'Example Regular', 'fullName': 'Example Regular', 'psName': 'Example-Regular'})
    fb.setupPost(); fb.setupMaxp()
    stream = BytesIO(); fb.save(stream)
    return TTFont(BytesIO(stream.getvalue()))
result = [
    ok(lambda: (lambda f: f.getGlyphOrder() == ['.notdef', 'A'] and f.getBestCmap() == {65: 'A'} and f['maxp'].numGlyphs == 2 and newTable('head').tableTag == 'head')(build_font())),
    ok(lambda: TTFont().keys() == ['GlyphOrder'] and TTFont().get('head') is None and not TTFont().isLoaded('head')),
    ok(lambda: (lambda original: original == Transform() and original.translate(3, 4) != original)(__import__('fontTools.misc.transform', fromlist=['Transform']).Transform())),
]
"""))
    console = run_console("fonttools", ["--help"])
    leaves.append({
        "id": "font-58-console-help",
        "status": "passed" if console.returncode == 0 and "fonttools" in (console.stdout + console.stderr).lower() else "failed",
        "message": "fonttools console entry point did not produce help",
    })
    if len(leaves) != 60 or len({leaf["id"] for leaf in leaves}) != 60:
        print(f"internal leaf count error: {len(leaves)}", file=sys.stderr)
        return 2
    print(json.dumps({"schema_version": "1.0", "leaves": leaves}, sort_keys=True))
    return 1 if any(leaf["status"] == "failed" for leaf in leaves) else 0


if __name__ == "__main__":
    raise SystemExit(main())
