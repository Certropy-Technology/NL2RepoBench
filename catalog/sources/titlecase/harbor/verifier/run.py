"""Private deterministic scenarios for the titlecase public contract.

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
        'basic_lowercase',
        "from titlecase import titlecase\nr = titlecase('hello world')\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": "Hello World"},
    ),
    (
        'basic_uppercase',
        "from titlecase import titlecase\nr = titlecase('HELLO WORLD')\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": "Hello World"},
    ),
    (
        'basic_mixed',
        "from titlecase import titlecase\nr = titlecase('Hello World')\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": "Hello World"},
    ),
    (
        'empty_string',
        "from titlecase import titlecase\nr = titlecase('')\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": ""},
    ),
    (
        'small_word_article',
        "from titlecase import titlecase\nr = titlecase('a thing')\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": "A Thing"},
    ),
    (
        'small_word_the',
        "from titlecase import titlecase\nr = titlecase('the quick brown fox')\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": "The Quick Brown Fox"},
    ),
    (
        'small_word_and',
        "from titlecase import titlecase\nr = titlecase('alice and bob')\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": "Alice and Bob"},
    ),
    (
        'small_word_in',
        "from titlecase import titlecase\nr = titlecase('in the beginning')\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": "In the Beginning"},
    ),
    (
        'small_word_of',
        "from titlecase import titlecase\nr = titlecase('lord of the rings')\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": "Lord of the Rings"},
    ),
    (
        'small_word_at',
        "from titlecase import titlecase\nr = titlecase('at the door')\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": "At the Door"},
    ),
    (
        'small_word_by',
        "from titlecase import titlecase\nr = titlecase('by the way')\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": "By the Way"},
    ),
    (
        'small_word_for',
        "from titlecase import titlecase\nr = titlecase('for the win')\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": "For the Win"},
    ),
    (
        'small_word_to',
        "from titlecase import titlecase\nr = titlecase('to be or not to be')\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": "To Be or Not to Be"},
    ),
    (
        'small_word_with',
        "from titlecase import titlecase\nr = titlecase('dance with me')\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": "Dance With Me"},
    ),
    (
        'small_first',
        "from titlecase import titlecase\nr = titlecase('the beginning')\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": "The Beginning"},
    ),
    (
        'small_last',
        "from titlecase import titlecase\nr = titlecase('afraid of')\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": "Afraid Of"},
    ),
    (
        'small_both',
        "from titlecase import titlecase\nr = titlecase('a tale of')\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": "A Tale Of"},
    ),
    (
        'colon_subphrase',
        "from titlecase import titlecase\nr = titlecase('title: a subtitle')\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": "Title: A Subtitle"},
    ),
    (
        'question_subphrase',
        "from titlecase import titlecase\nr = titlecase('what is it? a mystery')\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": "What Is It? A Mystery"},
    ),
    (
        'semicolon_subphrase',
        "from titlecase import titlecase\nr = titlecase('first; the second')\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": "First; The Second"},
    ),
    (
        'hyphen_basic',
        "from titlecase import titlecase\nr = titlecase('end-to-end')\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": "End-to-End"},
    ),
    (
        'hyphen_small',
        "from titlecase import titlecase\nr = titlecase('a-b')\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": "A-B"},
    ),
    (
        'hyphen_multiple',
        "from titlecase import titlecase\nr = titlecase('one-two-three')\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": "One-Two-Three"},
    ),
    (
        'slash_basic',
        "from titlecase import titlecase\nr = titlecase('word/word')\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": "Word/Word"},
    ),
    (
        'slash_phrase',
        "from titlecase import titlecase\nr = titlecase('a title and/or string')\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": "A Title and/or String"},
    ),
    (
        'slash_complex',
        "from titlecase import titlecase\nr = titlecase('dance with me/let\\'s face the music and dance')\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": "Dance With Me/Let's Face the Music and Dance"},
    ),
    (
        'all_caps_simple',
        "from titlecase import titlecase\nr = titlecase('THIS IS A TEST')\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": "This Is a Test"},
    ),
    (
        'all_caps_mixed',
        "from titlecase import titlecase\nr = titlecase('this is a TEST')\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": "This Is a TEST"},
    ),
    (
        'acronym_att',
        "from titlecase import titlecase\nr = titlecase('what is AT&T\\'s problem?')\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": "What Is AT&T's Problem?"},
    ),
    (
        'acronym_qna',
        "from titlecase import titlecase\nr = titlecase('Q&A with steve jobs')\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": "Q&A With Steve Jobs"},
    ),
    (
        'acronym_sec',
        "from titlecase import titlecase\nr = titlecase('the SEC\\'s apple probe')\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": "The SEC's Apple Probe"},
    ),
    (
        'acronym_consonants',
        "from titlecase import titlecase\nr = titlecase('words with all consonants like cnn are acronyms')\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": "Words With All Consonants Like CNN Are Acronyms"},
    ),
    (
        'vs_short',
        "from titlecase import titlecase\nr = titlecase('this v that')\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": "This v That"},
    ),
    (
        'vs_dot',
        "from titlecase import titlecase\nr = titlecase('this v. that')\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": "This v. That"},
    ),
    (
        'vs_full',
        "from titlecase import titlecase\nr = titlecase('this vs that')\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": "This vs That"},
    ),
    (
        'vs_full_dot',
        "from titlecase import titlecase\nr = titlecase('this vs. that')\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": "This vs. That"},
    ),
    (
        'mac_name',
        "from titlecase import titlecase\nr = titlecase('macbeth')\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": "Macbeth"},
    ),
    (
        'mc_name',
        "from titlecase import titlecase\nr = titlecase('mcdonald')\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": "McDonald"},
    ),
    (
        'apostrophe_its',
        "from titlecase import titlecase\nr = titlecase('it\\'s')\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": "It's"},
    ),
    (
        'apostrophe_dont',
        "from titlecase import titlecase\nr = titlecase('don\\'t')\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": "Don't"},
    ),
    (
        'apostrophe_lets',
        "from titlecase import titlecase\nr = titlecase('let\\'s')\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": "Let's"},
    ),
    (
        'apostrophe_possessive',
        "from titlecase import titlecase\nr = titlecase('steve\\'s')\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": "Steve's"},
    ),
    (
        'numbers_ordinal',
        "from titlecase import titlecase\nr = titlecase('34th 3rd 2nd')\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": "34th 3rd 2nd"},
    ),
    (
        'numbers_year',
        "from titlecase import titlecase\nr = titlecase('in 2023')\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": "In 2023"},
    ),
    (
        'quote_single',
        "from titlecase import titlecase\nr = titlecase('\\'by the way, small word at the start but within quotes.\\'')\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": "'By the Way, Small Word at the Start but Within Quotes.'"},
    ),
    (
        'quote_double',
        'from titlecase import titlecase\nr = titlecase(\'"a trick, perhaps?"\')\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r',
        {"ok": True, "value": "\"A Trick, Perhaps?\""},
    ),
    (
        'quote_subphrase',
        "from titlecase import titlecase\nr = titlecase('sub-phrase: \\'a trick, perhaps?\\'')\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": "Sub-Phrase: 'A Trick, Perhaps?'"},
    ),
    (
        'punct_exclaim',
        "from titlecase import titlecase\nr = titlecase('hello world!')\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": "Hello World!"},
    ),
    (
        'punct_question',
        "from titlecase import titlecase\nr = titlecase('what is this?')\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": "What Is This?"},
    ),
    (
        'punct_mixed',
        "from titlecase import titlecase\nr = titlecase('oh! what a day.')\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": "Oh! What a Day."},
    ),
    (
        'consonants_cnn',
        "from titlecase import titlecase\nr = titlecase('cnn')\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": "CNN"},
    ),
    (
        'consonants_bbc',
        "from titlecase import titlecase\nr = titlecase('bbc news')\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": "BBC News"},
    ),
    (
        'consonants_short',
        "from titlecase import titlecase\nr = titlecase('st')\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": "St"},
    ),
    (
        'callback_tcp',
        "from titlecase import titlecase\nr = titlecase('a simple tcp wrapper', callback=lambda w, **k: w.upper() if w.upper() in ['TCP', 'UDP'] else None)\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": "A Simple TCP Wrapper"},
    ),
    (
        'callback_udp',
        "from titlecase import titlecase\nr = titlecase('tcp and udp wrapper', callback=lambda w, **k: w.upper() if w.upper() in ['TCP', 'UDP'] else None)\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": "TCP and UDP Wrapper"},
    ),
    (
        'inline_period_us',
        "from titlecase import titlecase\nr = titlecase('in the U.S. economy')\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": "In the U.S. Economy"},
    ),
    (
        'inline_period_initials',
        "from titlecase import titlecase\nr = titlecase('J.R.R. tolkien')\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": "J.R.R. Tolkien"},
    ),
    (
        'preserve_iphone',
        "from titlecase import titlecase\nr = titlecase('the iPhone is great')\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": "The iPhone Is Great"},
    ),
    (
        'preserve_ipad',
        "from titlecase import titlecase\nr = titlecase('iPad vs android')\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": "iPad vs Android"},
    ),
    (
        'multiline_basic',
        "from titlecase import titlecase\nr = titlecase('line one\\nline two')\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": "Line One\nLine Two"},
    ),
    (
        'multiline_empty',
        "from titlecase import titlecase\nr = titlecase('line one\\n\\nline two', preserve_blank_lines=True)\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": "Line One\n\nLine Two"},
    ),
    (
        'complex_jobs',
        "from titlecase import titlecase\nr = titlecase('Q&A with steve jobs: \\'that\\'s what happens in technology\\'')\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": "Q&A With Steve Jobs: 'That's What Happens in Technology'"},
    ),
    (
        'complex_att',
        "from titlecase import titlecase\nr = titlecase('apple deal with AT&T falls through')\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": "Apple Deal With AT&T Falls Through"},
    ),
    (
        'complex_subphrase',
        "from titlecase import titlecase\nr = titlecase('starting sub-phrase with a small word: a trick, perhaps?')\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": "Starting Sub-Phrase With a Small Word: A Trick, Perhaps?"},
    ),
    (
        'complex_hyphen_sub',
        "from titlecase import titlecase\nr = titlecase('starting a hyphen delimited sub-phrase with a small word - a trick, perhaps?')\nif isinstance(r, tuple):\n    r = list(r)\nif isinstance(r, list) and r and isinstance(r[0], tuple):\n    r = [list(item) for item in r]\nresult = r",
        {"ok": True, "value": "Starting a Hyphen Delimited Sub-Phrase With a Small Word - A Trick, Perhaps?"},
    ),
]

assert len(CASES) == 65, f"Expected 65 cases, got {len(CASES)}"


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
