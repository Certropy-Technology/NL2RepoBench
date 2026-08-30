"""Private deterministic scenarios for the wcwidth public contract."""

# Scenario source strings are intentionally kept together for auditability.
# ruff: noqa: E501

from __future__ import annotations

import json

from nl2repobench.verification.candidate_client import execute_script


def _run(source: str, expected: object) -> dict[str, object]:
    observed = execute_script(source, timeout_sec=20.0)
    actual: dict[str, object] = {"ok": observed.ok, "value": observed.value}
    if not observed.ok:
        actual["exception_type"] = observed.exception_type
        actual["exception_message"] = observed.exception_message
    return {"status": "passed" if actual == expected else "failed", "actual": actual}


CASES: list[tuple[str, str, object]] = [
    (
        "metadata",
        "import wcwidth\nresult = [wcwidth.__version__, list(wcwidth.__all__), list(wcwidth.list_versions()), list(wcwidth.list_term_programs())[:3]]",
        {"ok": True, "value": ["0.8.3", ["wcwidth", "wcswidth", "wcstwidth", "width", "iter_sequences", "iter_graphemes", "iter_graphemes_reverse", "grapheme_boundary_before", "ljust", "rjust", "center", "wrap", "clip", "strip_sequences", "list_versions", "list_term_programs", "propagate_sgr", "Hyperlink", "HyperlinkParams", "TextSizing", "TextSizingParams"], ["17.0.0"], ["alacritty", "apple_terminal", "bobcat"]]},
    ),
    (
        "legacy-module",
        "import importlib\nm = importlib.import_module('wcwidth.wcwidth')\nresult = [m.wcwidth('A'), hasattr(m, 'wcswidth')]",
        {"ok": True, "value": [1, True]},
    ),
    (
        "wcwidth-basic",
        "from wcwidth import wcwidth\nresult = [wcwidth('A'), wcwidth('\\u4e2d'), wcwidth('\\x00'), wcwidth('\\x1b'), wcwidth('\\u0301'), wcwidth('\\U0001f642')]",
        {"ok": True, "value": [1, 2, 0, -1, 0, 2]},
    ),
    (
        "wcswidth-basic",
        "from wcwidth import wcswidth\nresult = [wcswidth('A\\u4e2d\\U0001f642'), wcswidth('A\\x1bB'), wcswidth('A\\u4e2d\\U0001f642', 2), wcswidth('A\\u4e2d\\U0001f642', 99)]",
        {"ok": True, "value": [5, -1, 3, 5]},
    ),
    (
        "ambiguous",
        "from wcwidth import wcwidth, wcswidth\nresult = [wcwidth('\\u00b7'), wcwidth('\\u00b7', ambiguous_width=2), wcswidth('\\u00b7\\u4e2d', ambiguous_width=2)]",
        {"ok": True, "value": [1, 2, 4]},
    ),
    (
        "graphemes",
        "from wcwidth import iter_graphemes\nresult = list(iter_graphemes('e\\u0301\\U0001f469\\u200d\\U0001f4bb\\U0001f1fa\\U0001f1f8'))",
        {"ok": True, "value": ["e\u0301", "\U0001f469\u200d\U0001f4bb", "\U0001f1fa\U0001f1f8"]},
    ),
    (
        "reverse-boundary",
        "from wcwidth import iter_graphemes_reverse, grapheme_boundary_before\ns='e\\u0301\\U0001f469\\u200d\\U0001f4bb'\nresult = [list(iter_graphemes_reverse(s)), grapheme_boundary_before(s, 0), grapheme_boundary_before(s, 2), grapheme_boundary_before(s, 99)]",
        {"ok": True, "value": [["\U0001f469\u200d\U0001f4bb", "e\u0301"], 0, 0, 2]},
    ),
    (
        "virama-and-emoji",
        "from wcwidth import wcswidth\nresult = [wcswidth('क्'), wcswidth('\\u2764\\ufe0f'), wcswidth('\\U0001f1fa\\U0001f1f8')]",
        {"ok": True, "value": [1, 2, 2]},
    ),
    (
        "iter-sequences",
        "from wcwidth import iter_sequences, strip_sequences\ns='\\x1b[31mred\\x1b[0m'\nresult = [[list(item) for item in iter_sequences(s)], strip_sequences(s)]",
        {"ok": True, "value": [[["\u001b[31m", True], ["red", False], ["\u001b[0m", True]], "red"]},
    ),
    (
        "width-sgr",
        "from wcwidth import width\nresult = [width('\\x1b[31mred\\x1b[0m'), width('\\x1b]8;;https://x\\x07link\\x1b]8;;\\x07')]",
        {"ok": True, "value": [3, 4]},
    ),
    (
        "width-controls",
        "from wcwidth import width\nresult = [width('a\\x08b'), width('a\\tb'), width('a\\rbc'), width('a\\x1b[31mb')]",
        {"ok": True, "value": [1, 9, 2, 2]},
    ),
    (
        "width-ignore",
        "from wcwidth import width\nresult = [width('a\\x1b[31mb', control_codes='ignore'), width('a\\x08b', control_codes='ignore')]",
        {"ok": True, "value": [2, 2]},
    ),
    (
        "width-kitty",
        "from wcwidth import width\nresult = [width('\\x1b]66;w=4;AB\\x07'), width('\\x1b]66;s=2;AB\\x07')]",
        {"ok": True, "value": [4, 4]},
    ),
    (
        "alignment",
        "from wcwidth import ljust, rjust, center\nresult = [ljust('\\u4e2d', 4), rjust('\\u4e2d', 4), center('\\u4e2d', 5)]",
        {"ok": True, "value": ["\u4e2d  ", "  \u4e2d", "  \u4e2d "]},
    ),
    (
        "wrap-ascii",
        "from wcwidth import wrap\nresult = wrap('hello world', 4)",
        {"ok": True, "value": ["hell", "o wo", "rld"]},
    ),
    (
        "wrap-cjk",
        "from wcwidth import wrap\nresult = wrap('中文测试', 4)",
        {"ok": True, "value": ["中文", "测试"]},
    ),
    (
        "wrap-sgr",
        "from wcwidth import wrap\nresult = wrap('\\x1b[31mred\\x1b[0m', 2)",
        {"ok": True, "value": ["\u001b[31mre\u001b[0m", "\u001b[31md\u001b[0m"]},
    ),
    (
        "clip-cjk",
        "from wcwidth import clip\nresult = [clip('中文测试', 0, 3), clip('中文测试', 1, 5)]",
        {"ok": True, "value": ["中 ", " 文 "]},
    ),
    (
        "clip-controls",
        "from wcwidth import clip\nresult = [clip('a\\x08b', 0, 1), clip('a\\tb', 0, 4)]",
        {"ok": True, "value": ["b", "a   "]},
    ),
    (
        "clip-sgr",
        "from wcwidth import clip\nresult = clip('\\x1b[31mred\\x1b[0m', 1, 3)",
        {"ok": True, "value": "\u001b[31med\u001b[0m"},
    ),
    (
        "sgr-propagation",
        "from wcwidth import propagate_sgr\nresult = propagate_sgr(['\\x1b[31mred', 'next'])",
        {"ok": True, "value": ["\u001b[31mred\u001b[0m", "\u001b[31mnext\u001b[0m"]},
    ),
    (
        "hyperlink-params",
        "from wcwidth import HyperlinkParams\np=HyperlinkParams('https://x','id=1')\nresult=[p.make_open(),p.make_close()]",
        {"ok": True, "value": ["\u001b]8;id=1;https://x\u0007", "\u001b]8;;\u0007"]},
    ),
    (
        "hyperlink-unit",
        "from wcwidth import Hyperlink, HyperlinkParams\nh=Hyperlink(HyperlinkParams('https://x','id=1'),'link')\nresult=[h.display_width(),h.make_sequence()]",
        {"ok": True, "value": [4, "\u001b]8;id=1;https://x\u0007link\u001b]8;;\u0007"]},
    ),
    (
        "text-sizing-params",
        "from wcwidth import TextSizingParams\np=TextSizingParams.from_params('s=2:w=4')\nresult=[list(p),p.make_sequence(),repr(p)]",
        {"ok": True, "value": [[2, 4, 0, 0, 0, 0], "s=2:w=4", "TextSizingParams(scale=2, width=4)"]},
    ),
    (
        "text-sizing-unit",
        "from wcwidth import TextSizing, TextSizingParams\nt=TextSizing(TextSizingParams(scale=2,width=2),'AB','\\x07')\nresult=[t.display_width(),t.make_sequence()]",
        {"ok": True, "value": [4, "\u001b]66;s=2:w=2;AB\u0007"]},
    ),
    (
        "text-sizing-parse",
        "from wcwidth import TextSizingParams\nresult=[list(TextSizingParams.from_params('s=99:w=-2')), list(TextSizingParams.from_params('s=x:w=2'))]",
        {"ok": True, "value": [[7, 0, 0, 0, 0, 0], [1, 2, 0, 0, 0, 0]]},
    ),
    (
        "n-argument",
        "from wcwidth import wcswidth\nresult=[wcswidth('abc',0),wcswidth('abc',2),wcswidth('abc',99)]",
        {"ok": True, "value": [0, 2, 3]},
    ),
    (
        "terminal-override",
        "from wcwidth import wcstwidth\nresult=[wcstwidth('\\u2764\\ufe0f',term_program=False),wcstwidth('\\u2764\\ufe0f',term_program='xterm')]",
        {"ok": True, "value": [2, 1]},
    ),
    (
        "determinism-1",
        "from wcwidth import wcswidth\nresult=[wcswidth('A\\u4e2d\\U0001f642') for _ in range(3)]",
        {"ok": True, "value": [5, 5, 5]},
    ),
    (
        "determinism-2",
        "from wcwidth import wrap\nresult=[wrap('中文 hello',5),wrap('中文 hello',5)]",
        {"ok": True, "value": [["中文", "hello"], ["中文", "hello"]]},
    ),
    (
        "determinism-3",
        "from wcwidth import iter_sequences\ns='\\x1b[1mA\\x1b[0m'\nresult=[[[list(item) for item in iter_sequences(s)]][0],[[list(item) for item in iter_sequences(s)]][0]]",
        {"ok": True, "value": [[["\u001b[1m", True], ["A", False], ["\u001b[0m", True]], [["\u001b[1m", True], ["A", False], ["\u001b[0m", True]]]},
    ),
    (
        "determinism-4",
        "from wcwidth import list_versions, list_term_programs\nresult=[list_versions()==list_versions(), list_term_programs()==list_term_programs(), list_term_programs()==tuple(sorted(list_term_programs()))]",
        {"ok": True, "value": [True, True, True]},
    ),
    (
        "public-types",
        "import wcwidth\nresult=[list(wcwidth.HyperlinkParams._fields), list(wcwidth.TextSizingParams._fields), callable(wcwidth.wrap), callable(wcwidth.clip)]",
        {"ok": True, "value": [["url", "params", "terminator"], ["scale", "width", "numerator", "denominator", "vertical_align", "horizontal_align"], True, True]},
    ),
    (
        "strict-text-sizing",
        "from wcwidth import TextSizingParams\ntry:\n TextSizingParams.from_params('q=1', control_codes='strict')\nexcept ValueError as exc:\n result=[type(exc).__name__, 'Unknown text sizing field' in str(exc)]",
        {"ok": True, "value": ["ValueError", True]},
    ),
    (
        "wcstwidth-profile",
        "from wcwidth import wcstwidth\nresult=[wcstwidth('A\\u4e2d', term_program=False), wcstwidth('A\\u4e2d', term_program='xterm')]",
        {"ok": True, "value": [3, 3]},
    ),
    (
        "alignment-fill",
        "from wcwidth import ljust, rjust\nresult=[ljust('A',3,fillchar='.'),rjust('A',3,fillchar='.') ]",
        {"ok": True, "value": ["A..", "..A"]},
    ),
]


def main() -> None:
    leaves: list[dict[str, object]] = []
    for case_id, source, expected in CASES:
        outcome = _run(source, expected)
        leaf: dict[str, object] = {"id": case_id, "status": outcome["status"]}
        if outcome["status"] == "failed":
            leaf["message"] = json.dumps(outcome["actual"], ensure_ascii=False, sort_keys=True)
        leaves.append(leaf)
    print(json.dumps({"schema_version": "1.0", "leaves": leaves}, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
