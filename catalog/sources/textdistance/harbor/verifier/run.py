"""Private deterministic scenarios for the textdistance public contract.

Each scenario runs as the unprivileged candidate in an isolated subprocess and
must be derivable from the public instruction. The candidate runner executes
the script and reads the ``result`` binding.
"""

from __future__ import annotations

import json

from nl2repobench.verification.candidate_client import execute_script


def _run(source: str, expected: object) -> tuple[str, object]:
    observed = execute_script(source, timeout_sec=20.0)
    actual: dict[str, object] = {"ok": observed.ok, "value": observed.value}
    if not observed.ok:
        actual["exception_type"] = observed.exception_type
        actual["exception_message"] = observed.exception_message
    return "passed" if actual == expected else "failed", actual


CASES: list[tuple[str, str, object]] = [
    (
        'hamming_1',
        "import textdistance\nr = textdistance.hamming('test', 'text')\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": 1},
    ),
    (
        'hamming_2',
        "import textdistance\nr = textdistance.hamming('hello', 'hallo')\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": 1},
    ),
    (
        'hamming_3',
        "import textdistance\nr = textdistance.hamming('abc', 'xyz')\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": 3},
    ),
    (
        'hamming_4',
        "import textdistance\nr = textdistance.hamming('', '')\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": 0},
    ),
    (
        'hamming_5',
        "import textdistance\nr = textdistance.hamming('same', 'same')\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": 0},
    ),
    (
        'hamming_6',
        "import textdistance\nr = textdistance.hamming('python', 'jython')\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": 1},
    ),
    (
        'hamming_7',
        "import textdistance\nr = textdistance.hamming('1234', '1235')\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": 1},
    ),
    (
        'hamming_8',
        "import textdistance\nr = textdistance.hamming('algorithm', 'logarithm')\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": 3},
    ),
    (
        'levenshtein_1',
        "import textdistance\nr = textdistance.levenshtein('kitten', 'sitting')\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": 3},
    ),
    (
        'levenshtein_2',
        "import textdistance\nr = textdistance.levenshtein('saturday', 'sunday')\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": 3},
    ),
    (
        'levenshtein_3',
        "import textdistance\nr = textdistance.levenshtein('', 'abc')\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": 3},
    ),
    (
        'levenshtein_4',
        "import textdistance\nr = textdistance.levenshtein('abc', '')\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": 3},
    ),
    (
        'levenshtein_5',
        "import textdistance\nr = textdistance.levenshtein('same', 'same')\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": 0},
    ),
    (
        'levenshtein_6',
        "import textdistance\nr = textdistance.levenshtein('book', 'back')\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": 2},
    ),
    (
        'levenshtein_7',
        "import textdistance\nr = textdistance.levenshtein('horse', 'ros')\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": 3},
    ),
    (
        'levenshtein_8',
        "import textdistance\nr = textdistance.levenshtein('intention', 'execution')\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": 5},
    ),
    (
        'levenshtein_9',
        "import textdistance\nr = textdistance.levenshtein('a', 'b')\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": 1},
    ),
    (
        'levenshtein_10',
        "import textdistance\nr = textdistance.levenshtein('abc', 'def')\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": 3},
    ),
    (
        'jaro_winkler_1',
        "import textdistance\nr = round(textdistance.jaro_winkler('martha', 'marhta'), 6)\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": 0.961111},
    ),
    (
        'jaro_winkler_2',
        "import textdistance\nr = round(textdistance.jaro_winkler('dixon', 'dicksonx'), 6)\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": 0.813333},
    ),
    (
        'jaro_winkler_3',
        "import textdistance\nr = round(textdistance.jaro_winkler('same', 'same'), 6)\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": 1},
    ),
    (
        'jaro_winkler_4',
        "import textdistance\nr = round(textdistance.jaro_winkler('', ''), 6)\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": 1},
    ),
    (
        'jaro_winkler_5',
        "import textdistance\nr = round(textdistance.jaro_winkler('frederick', 'frederick'), 6)\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": 1},
    ),
    (
        'jaro_winkler_6',
        "import textdistance\nr = round(textdistance.jaro_winkler('jones', 'johnson'), 6)\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": 0.832381},
    ),
    (
        'jaro_winkler_7',
        "import textdistance\nr = round(textdistance.jaro_winkler('abc', 'xyz'), 6)\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": 0.0},
    ),
    (
        'jaro_winkler_8',
        "import textdistance\nr = round(textdistance.jaro_winkler('hello', 'hallo'), 6)\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": 0.88},
    ),
    (
        'jaro_1',
        "import textdistance\nr = round(textdistance.jaro('martha', 'marhta'), 6)\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": 0.944444},
    ),
    (
        'jaro_2',
        "import textdistance\nr = round(textdistance.jaro('dixon', 'dicksonx'), 6)\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": 0.766667},
    ),
    (
        'jaro_3',
        "import textdistance\nr = round(textdistance.jaro('same', 'same'), 6)\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": 1},
    ),
    (
        'jaro_4',
        "import textdistance\nr = round(textdistance.jaro('', ''), 6)\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": 1},
    ),
    (
        'jaro_5',
        "import textdistance\nr = round(textdistance.jaro('jones', 'johnson'), 6)\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": 0.790476},
    ),
    (
        'jaro_6',
        "import textdistance\nr = round(textdistance.jaro('abc', 'xyz'), 6)\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": 0.0},
    ),
    (
        'damerau_levenshtein_1',
        "import textdistance\nr = textdistance.damerau_levenshtein('ca', 'abc')\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": 3},
    ),
    (
        'damerau_levenshtein_2',
        "import textdistance\nr = textdistance.damerau_levenshtein('abc', 'acb')\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": 1},
    ),
    (
        'damerau_levenshtein_3',
        "import textdistance\nr = textdistance.damerau_levenshtein('abcd', 'abdc')\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": 1},
    ),
    (
        'damerau_levenshtein_4',
        "import textdistance\nr = textdistance.damerau_levenshtein('', 'abc')\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": 3},
    ),
    (
        'damerau_levenshtein_5',
        "import textdistance\nr = textdistance.damerau_levenshtein('same', 'same')\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": 0},
    ),
    (
        'damerau_levenshtein_6',
        "import textdistance\nr = textdistance.damerau_levenshtein('ab', 'ba')\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": 1},
    ),
    (
        'damerau_levenshtein_7',
        "import textdistance\nr = textdistance.damerau_levenshtein('abc', 'bca')\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": 2},
    ),
    (
        'damerau_levenshtein_8',
        "import textdistance\nr = textdistance.damerau_levenshtein('abcdef', 'badcef')\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": 2},
    ),
    (
        'jaccard_1',
        "import textdistance\nr = round(textdistance.jaccard('abc', 'abc'), 6)\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": 1},
    ),
    (
        'jaccard_2',
        "import textdistance\nr = round(textdistance.jaccard('abc', 'def'), 6)\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": 0.0},
    ),
    (
        'jaccard_3',
        "import textdistance\nr = round(textdistance.jaccard('abc', 'bcd'), 6)\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": 0.5},
    ),
    (
        'jaccard_4',
        "import textdistance\nr = round(textdistance.jaccard('hello', 'world'), 6)\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": 0.25},
    ),
    (
        'jaccard_5',
        "import textdistance\nr = round(textdistance.jaccard('python', 'pythonic'), 6)\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": 0.75},
    ),
    (
        'jaccard_6',
        "import textdistance\nr = round(textdistance.jaccard('test', 'testing'), 6)\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": 0.571429},
    ),
    (
        'jaccard_7',
        "import textdistance\nr = round(textdistance.jaccard('', ''), 6)\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": 1},
    ),
    (
        'jaccard_8',
        "import textdistance\nr = round(textdistance.jaccard('a', 'a'), 6)\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": 1},
    ),
    (
        'sorensen_dice_1',
        "import textdistance\nr = round(textdistance.sorensen_dice('abc', 'abc'), 6)\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": 1},
    ),
    (
        'sorensen_dice_2',
        "import textdistance\nr = round(textdistance.sorensen_dice('abc', 'def'), 6)\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": 0.0},
    ),
    (
        'sorensen_dice_3',
        "import textdistance\nr = round(textdistance.sorensen_dice('abc', 'bcd'), 6)\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": 0.666667},
    ),
    (
        'sorensen_dice_4',
        "import textdistance\nr = round(textdistance.sorensen_dice('hello', 'world'), 6)\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": 0.4},
    ),
    (
        'sorensen_dice_5',
        "import textdistance\nr = round(textdistance.sorensen_dice('python', 'pythonic'), 6)\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": 0.857143},
    ),
    (
        'sorensen_dice_6',
        "import textdistance\nr = round(textdistance.sorensen_dice('', ''), 6)\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": 1},
    ),
    (
        'sorensen_dice_7',
        "import textdistance\nr = round(textdistance.sorensen_dice('same', 'same'), 6)\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": 1},
    ),
    (
        'lcsseq_1',
        "import textdistance\nr = textdistance.lcsseq('abcde', 'ace')\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": "ace"},
    ),
    (
        'lcsseq_2',
        "import textdistance\nr = textdistance.lcsseq('AGGTAB', 'GXTXAYB')\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": "GTAB"},
    ),
    (
        'lcsseq_3',
        "import textdistance\nr = textdistance.lcsseq('abc', 'xyz')\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": ""},
    ),
    (
        'lcsseq_4',
        "import textdistance\nr = textdistance.lcsseq('same', 'same')\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": "same"},
    ),
    (
        'lcsseq_5',
        "import textdistance\nr = textdistance.lcsseq('', '')\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": ""},
    ),
    (
        'lcsseq_6',
        "import textdistance\nr = textdistance.lcsseq('abcdef', 'fedcba')\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": "a"},
    ),
    (
        'lcsseq_7',
        "import textdistance\nr = textdistance.lcsseq('programming', 'gaming')\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": "gaming"},
    ),
    (
        'ratcliff_obershelp_1',
        "import textdistance\nr = round(textdistance.ratcliff_obershelp('abc', 'abc'), 6)\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": 1},
    ),
    (
        'ratcliff_obershelp_2',
        "import textdistance\nr = round(textdistance.ratcliff_obershelp('abc', 'def'), 6)\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": 0.0},
    ),
    (
        'ratcliff_obershelp_3',
        "import textdistance\nr = round(textdistance.ratcliff_obershelp('alexander', 'alexandre'), 6)\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": 0.888889},
    ),
    (
        'ratcliff_obershelp_4',
        "import textdistance\nr = round(textdistance.ratcliff_obershelp('hello', 'hallo'), 6)\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": 0.8},
    ),
    (
        'ratcliff_obershelp_5',
        "import textdistance\nr = round(textdistance.ratcliff_obershelp('python', 'pythonic'), 6)\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": 0.857143},
    ),
    (
        'ratcliff_obershelp_6',
        "import textdistance\nr = round(textdistance.ratcliff_obershelp('', ''), 6)\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": 1},
    ),
    (
        'ratcliff_obershelp_7',
        "import textdistance\nr = round(textdistance.ratcliff_obershelp('same', 'same'), 6)\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": 1},
    ),
    (
        'cosine_1',
        "import textdistance\nr = round(textdistance.cosine('abc', 'abc'), 6)\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": 1},
    ),
    (
        'cosine_2',
        "import textdistance\nr = round(textdistance.cosine('abc', 'def'), 6)\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": 0.0},
    ),
    (
        'cosine_3',
        "import textdistance\nr = round(textdistance.cosine('abc', 'bcd'), 6)\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": 0.666667},
    ),
    (
        'cosine_4',
        "import textdistance\nr = round(textdistance.cosine('hello', 'world'), 6)\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": 0.4},
    ),
    (
        'cosine_5',
        "import textdistance\nr = round(textdistance.cosine('python', 'pythonic'), 6)\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": 0.866025},
    ),
    (
        'cosine_6',
        "import textdistance\nr = round(textdistance.cosine('', ''), 6)\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": 1},
    ),
    (
        'cosine_7',
        "import textdistance\nr = round(textdistance.cosine('same', 'same'), 6)\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": 1},
    ),
]

assert len(CASES) == 76, f"Expected 76 cases, got {len(CASES)}"


def main() -> None:
    leaves: list[dict[str, object]] = []
    for case_id, source, expected in CASES:
        status, actual = _run(source, expected)
        leaf: dict[str, object] = {"id": case_id, "status": status}
        if status == "failed":
            leaf["message"] = json.dumps(actual, ensure_ascii=False, sort_keys=True, default=repr)
        leaves.append(leaf)
    print(json.dumps({"schema_version": "1.0", "leaves": leaves}, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
