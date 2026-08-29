#!/usr/bin/env python3
"""Private deterministic checks for the regex public contract."""
from __future__ import annotations

import json
from typing import Any, Callable

from nl2repobench.verification import candidate_client as cc


def script(source: str, expected: Any) -> bool:
    result = cc.execute_script(source, timeout_sec=12.0)
    if not result.ok:
        raise AssertionError(f"candidate script error: {result.exception_type}: {result.exception_message}")
    if result.value != expected:
        raise AssertionError(f"expected {expected!r}, got {result.value!r}")
    return True


def call(module: str, attribute: str, *args: Any, **kwargs: Any) -> cc.CandidateCallResult:
    return cc.call(module, attribute, *args, timeout_sec=12.0, **kwargs)


def equal(result: cc.CandidateCallResult, expected: Any) -> bool:
    return result.ok and result.value == expected


def error(result: cc.CandidateCallResult, suffix: str) -> bool:
    return not result.ok and (result.exception_type or "").endswith(suffix)


def checks() -> list[tuple[str, Callable[[], bool]]]:
    names = ["__version__", "DEFAULT_VERSION", "RegexFlag", "Regex", "Pattern", "Match", "error", "compile", "template", "purge", "cache_all", "escape", "match", "fullmatch", "prefixmatch", "search", "sub", "subf", "subn", "subfn", "split", "splititer", "findall", "finditer", "VERSION0", "VERSION1", "V0", "V1", "ASCII", "A", "BESTMATCH", "B", "DEBUG", "D", "ENHANCEMATCH", "E", "FULLCASE", "F", "IGNORECASE", "I", "LOCALE", "L", "MULTILINE", "M", "POSIX", "P", "REVERSE", "R", "DOTALL", "S", "UNICODE", "U", "WORD", "W", "VERBOSE", "X"]
    return [
        ("root-exports", lambda: script(f"import regex\nresult = sorted({names!r}) == sorted(x for x in {names!r} if hasattr(regex, x))", True)),
        ("version", lambda: script("import regex, importlib.metadata\nresult = [regex.__version__, importlib.metadata.version('regex')]", ["2026.8.12", "2026.8.12"])),
        ("compile-attributes", lambda: script("import regex\np=regex.compile(r'(?P<word>\\w+)', regex.I)\nresult=[p.pattern,int(p.flags),p.groups,dict(p.groupindex),type(p).__name__]", ["(?P<word>\\w+)", 8226, 1, {"word": 1}, "Pattern"])),
        ("search-span", lambda: script("import regex\nm=regex.search('cat','a cat')\nresult=[m.group(),list(m.span()),m.start(),m.end()]", ["cat", [2,5], 2, 5])),
        ("match-groups", lambda: script("import regex\nm=regex.match(r'(?P<first>\\w+)-(\\d+)','abc-42')\nresult=[m.group(0),m.group(1),m['first'],list(m.groups()),m.groupdict(),m.lastindex,m.lastgroup]", ["abc-42", "abc", "abc", ["abc", "42"], {"first": "abc"}, 2, "first"])),
        ("fullmatch-prefix", lambda: script("import regex\nresult=[bool(regex.fullmatch('a+','aaa')),bool(regex.prefixmatch('a+','aaab')),regex.match('a+','bbb') is None]", [True, True, True])),
        ("findall-scalar", lambda: equal(call("regex", "findall", r"\d+", "a1 b22"), ["1", "22"])),
        ("findall-tuples", lambda: equal(call("regex", "findall", r"(a)(b)?", "ab ac"), [["a", "b"], ["a", ""]])),
        ("finditer-order", lambda: script("import regex\nresult=[[m.group(),list(m.span())] for m in regex.finditer(r'\\w+','one two')]", [["one", [0,3]], ["two", [4,7]]] )),
        ("sub-callable", lambda: script("import regex\nresult=regex.sub(r'\\d+',lambda m:str(int(m.group())+1),'a1 b20')", "a2 b21")),
        ("subn-count", lambda: equal(call("regex", "subn", "x", "y", "x x", 1), ["y x", 1])),
        ("split-captures", lambda: equal(call("regex", "split", r"[,;]", "a,b;c"), ["a", "b", "c"])),
        ("bytes-api", lambda: script("import regex\nm=regex.search(rb'(?P<x>ab)',b'--ab--')\nresult=[m.group().decode(),m.group('x').decode(),list(m.span()),[x.decode() for x in regex.findall(rb'\\w+',b'a 2')]]", ["ab", "ab", [2,4], ["a", "2"]])),
        ("ignorecase-fullcase", lambda: script("import regex\nresult=bool(regex.fullmatch('STRASSE','straße',regex.I|regex.FULLCASE))", True)),
        ("version1-nested-set", lambda: equal(call("regex", "findall", r"(?V1)[[a-z]--[aeiou]]", "abcde"), ["b", "c", "d"])),
        ("unicode-properties", lambda: equal(call("regex", "findall", r"\p{Script=Greek}+", "abc αβ Γ"), ["αβ", "Γ"])),
        ("grapheme", lambda: equal(call("regex", "findall", r"\X", "a\u0301b"), ["a\u0301", "b"])),
        ("fuzzy-match", lambda: script("import regex\nm=regex.search(r'(?:cat){e<=1}','cut')\nresult=[m.group(),list(m.fuzzy_counts),[list(x) for x in m.fuzzy_changes]]", ["cut", [1,0,0], [[1], [], []]])),
        ("overlapped", lambda: script("import regex\nresult=[list(m.span()) for m in regex.finditer('aba','ababa',overlapped=True)]", [[0,3], [2,5]])),
        ("reverse-order", lambda: equal(call("regex", "findall", r"(?r)\w+", "one two"), ["two", "one"])),
        ("partial-match", lambda: script("import regex\nm=regex.match('abcdef','abc',partial=True)\nresult=[m.group(),m.partial,list(m.span())]", ["abc", True, [0,3]])),
        ("scanner", lambda: script("import regex\ns=regex.compile(r'\\w+').scanner('a bb')\nresult=[m.group() for m in iter(s.search,None)]", ["a", "bb"])),
        ("repeated-captures", lambda: script("import regex\nm=regex.match(r'(?P<x>a)+','aaa')\nresult=[m.group(),m.captures('x'),[list(x) for x in m.spans('x')]]", ["aaa", ["a","a","a"], [[0,1],[1,2],[2,3]]] )),
        ("branch-reset", lambda: script("import regex\nm=regex.match(r'(?|(a)|(b))','b')\nresult=[m.group(),list(m.groups())]", ["b", ["b"]])),
        ("named-list", lambda: script("import regex\np=regex.compile(r'\\L<words>',words=['cat','dog'])\nresult=[p.findall('dog cat'),sorted(p.named_lists['words'])]", [["dog","cat"], ["cat","dog"]])),
        ("posix-longest", lambda: script("import regex\nresult=regex.search(r'(?p)a|ab','ab').group()", "ab")),
        ("fuzzy-changes", lambda: script("import regex\nm=regex.search(r'(?:abc){e<=1}','axc')\nresult=[list(m.fuzzy_counts),list(m.fuzzy_changes[0]),list(m.fuzzy_changes[1])]", [[1,0,0], [1], []])),
        ("escape-text", lambda: script("import regex\nresult=regex.escape('a.b c',literal_spaces=True)", r"a\.b c")),
        ("escape-bytes", lambda: script("import regex\nresult=regex.escape(b'a.b').decode()", r"a\.b")),
        ("cache-controls", lambda: script("import regex\nregex.cache_all(False);regex.purge();regex.cache_all(True)\nresult=True", True)),
        ("type-error", lambda: script("import regex\ntry:\n regex.search('a',b'a')\n result=False\nexcept TypeError:\n result=True", True)),
        ("invalid-pattern", lambda: error(call("regex", "compile", "["), "error")),
        ("pattern-methods", lambda: script("import regex\np=regex.compile('a+')\nm=p.match('aaa')\nresult=[m.group(),p.findall('a aa'),p.split('a-b')]", ["aaa", ["a","aa"], ["", "-b"]])),
        ("match-projection", lambda: script("import regex\nm=regex.search(r'(a)?b','b')\nresult=[m.group(0),m.group(1),list(m.span(1)),m.start(1),m.end(1),m.lastindex]", ["b", None, [-1,-1], -1, -1, None])),
        ("subf-format", lambda: equal(call("regex", "subf", r"(?P<x>\w+)", r"{x}!", "hi"), "hi!")),
        ("splititer", lambda: script("import regex\nresult=list(regex.splititer(',','a,b,c'))", ["a","b","c"])),
        ("timeout-validation", lambda: script("import regex\ntry:\n regex.search('a','a',timeout=0)\n result=False\nexcept TimeoutError:\n result=True", True)),
    ]


def main() -> None:
    leaves = []
    for leaf_id, check in checks():
        try:
            passed = bool(check())
            message = ""
        except BaseException as exc:
            passed = False
            message = f"{type(exc).__name__}: {exc}"
        leaves.append({"id": leaf_id, "status": "passed" if passed else "failed", "message": message})
    print(json.dumps({"schema_version": "1.0", "leaves": leaves}, sort_keys=True))


if __name__ == "__main__":
    main()
