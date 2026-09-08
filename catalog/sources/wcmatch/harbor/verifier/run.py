"""Private deterministic scenarios for the wcmatch public contract.

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
        'fnm_basic_match',
        "import wcmatch.fnmatch as fnm; result = fnm.fnmatch('test.txt', '*.txt')",
        {"ok": True, "value": True},
    ),
    (
        'fnm_basic_nomatch',
        "import wcmatch.fnmatch as fnm; result = fnm.fnmatch('test.py', '*.txt')",
        {"ok": True, "value": False},
    ),
    (
        'fnm_question_mark',
        "import wcmatch.fnmatch as fnm; result = fnm.fnmatch('a', '?')",
        {"ok": True, "value": True},
    ),
    (
        'fnm_question_mark_multi',
        "import wcmatch.fnmatch as fnm; result = fnm.fnmatch('ab', '??')",
        {"ok": True, "value": True},
    ),
    (
        'fnm_star_nonempty',
        "import wcmatch.fnmatch as fnm; result = fnm.fnmatch('x', '*')",
        {"ok": True, "value": True},
    ),
    (
        'fnm_ignorecase_upper',
        "import wcmatch.fnmatch as fnm; result = fnm.fnmatch('TEST.TXT', '*.txt', flags=fnm.IGNORECASE)",
        {"ok": True, "value": True},
    ),
    (
        'fnm_ignorecase_mixed',
        "import wcmatch.fnmatch as fnm; result = fnm.fnmatch('TeSt.TxT', 'test.txt', flags=fnm.IGNORECASE)",
        {"ok": True, "value": True},
    ),
    (
        'fnm_case_sensitive',
        "import wcmatch.fnmatch as fnm; result = fnm.fnmatch('TEST.TXT', '*.txt')",
        {"ok": True, "value": False},
    ),
    (
        'fnm_extmatch_plus',
        "import wcmatch.fnmatch as fnm; result = fnm.fnmatch('test.txt', '+(test).txt', flags=fnm.EXTMATCH)",
        {"ok": True, "value": True},
    ),
    (
        'fnm_extmatch_star',
        "import wcmatch.fnmatch as fnm; result = fnm.fnmatch('', '*(test)', flags=fnm.EXTMATCH)",
        {"ok": True, "value": True},
    ),
    (
        'fnm_extmatch_question',
        "import wcmatch.fnmatch as fnm; result = fnm.fnmatch('test', '?(test)', flags=fnm.EXTMATCH)",
        {"ok": True, "value": True},
    ),
    (
        'fnm_extmatch_at',
        "import wcmatch.fnmatch as fnm; result = fnm.fnmatch('test', '@(test|other)', flags=fnm.EXTMATCH)",
        {"ok": True, "value": True},
    ),
    (
        'fnm_extmatch_exclaim',
        "import wcmatch.fnmatch as fnm; result = fnm.fnmatch('other', '!(test)', flags=fnm.EXTMATCH)",
        {"ok": True, "value": True},
    ),
    (
        'fnm_brace_simple',
        "import wcmatch.fnmatch as fnm; result = fnm.fnmatch('file1.txt', 'file{1,2}.txt', flags=fnm.BRACE)",
        {"ok": True, "value": True},
    ),
    (
        'fnm_brace_nomatch',
        "import wcmatch.fnmatch as fnm; result = fnm.fnmatch('file3.txt', 'file{1,2}.txt', flags=fnm.BRACE)",
        {"ok": True, "value": False},
    ),
    (
        'fnm_brace_range',
        "import wcmatch.fnmatch as fnm; result = fnm.fnmatch('file5.txt', 'file{1..9}.txt', flags=fnm.BRACE)",
        {"ok": True, "value": True},
    ),
    (
        'fnm_filter_basic',
        "import wcmatch.fnmatch as fnm; result = sorted(fnm.filter(['a.txt', 'b.py', 'c.txt'], '*.txt'))",
        {"ok": True, "value": ["a.txt", "c.txt"]},
    ),
    (
        'fnm_filter_empty',
        "import wcmatch.fnmatch as fnm; result = fnm.filter(['a.py', 'b.js'], '*.txt')",
        {"ok": True, "value": []},
    ),
    (
        'fnm_filter_ignorecase',
        "import wcmatch.fnmatch as fnm; result = sorted(fnm.filter(['A.TXT', 'b.py'], '*.txt', flags=fnm.IGNORECASE))",
        {"ok": True, "value": ["A.TXT"]},
    ),
    (
        'fnm_translate_type',
        "import wcmatch.fnmatch as fnm; result = isinstance(fnm.translate('*.txt'), tuple)",
        {"ok": True, "value": True},
    ),
    (
        'fnm_translate_pattern_usage',
        "import wcmatch.fnmatch as fnm; import re; patterns, _ = fnm.translate('*.txt'); result = bool(re.match(patterns[0], 'test.txt'))",
        {"ok": True, "value": True},
    ),
    (
        'glob_match_basic',
        "import wcmatch.glob as glob; result = glob.globmatch('dir/file.txt', 'dir/*.txt')",
        {"ok": True, "value": True},
    ),
    (
        'glob_match_doublestar',
        "import wcmatch.glob as glob; result = glob.globmatch('a/b/c/file.txt', '**/file.txt', flags=glob.GLOBSTAR)",
        {"ok": True, "value": True},
    ),
    (
        'glob_match_question',
        "import wcmatch.glob as glob; result = glob.globmatch('a/b', '?/?')",
        {"ok": True, "value": True},
    ),
    (
        'glob_nomatch_doublestar',
        "import wcmatch.glob as glob; result = glob.globmatch('file.txt', 'dir/**/*.txt', flags=glob.GLOBSTAR)",
        {"ok": True, "value": False},
    ),
    (
        'glob_ignorecase',
        "import wcmatch.glob as glob; result = glob.globmatch('DIR/FILE.TXT', 'dir/file.txt', flags=glob.IGNORECASE)",
        {"ok": True, "value": True},
    ),
    (
        'glob_extmatch',
        "import wcmatch.glob as glob; result = glob.globmatch('test.txt', '+(test).txt', flags=glob.EXTMATCH)",
        {"ok": True, "value": True},
    ),
    (
        'glob_brace',
        "import wcmatch.glob as glob; result = glob.globmatch('file1.txt', 'file{1,2,3}.txt', flags=glob.BRACE)",
        {"ok": True, "value": True},
    ),
    (
        'glob_filter_basic',
        "import wcmatch.glob as glob; result = sorted(glob.globfilter(['a/b.txt', 'c/d.py', 'e/f.txt'], '*/*.txt'))",
        {"ok": True, "value": ["a/b.txt", "e/f.txt"]},
    ),
    (
        'glob_filter_doublestar',
        "import wcmatch.glob as glob; result = sorted(glob.globfilter(['a/b/c.txt', 'd.txt'], '**/*.txt', flags=glob.GLOBSTAR))",
        {"ok": True, "value": ["a/b/c.txt", "d.txt"]},
    ),
    (
        'glob_translate_type',
        "import wcmatch.glob as glob; result = isinstance(glob.translate('*.txt'), tuple)",
        {"ok": True, "value": True},
    ),
    (
        'glob_translate_usage',
        "import wcmatch.glob as glob; import re; patterns, _ = glob.translate('*.txt'); result = bool(re.match(patterns[0], 'file.txt'))",
        {"ok": True, "value": True},
    ),
    (
        'pathlib_match_basic',
        "import wcmatch.pathlib as wcp; p = wcp.Path('file.txt'); result = p.match('*.txt')",
        {"ok": True, "value": True},
    ),
    (
        'pathlib_match_pattern',
        "import wcmatch.pathlib as wcp; p = wcp.Path('dir/file.txt'); result = p.match('*/*.txt')",
        {"ok": True, "value": True},
    ),
    (
        'pathlib_match_ignorecase',
        "import wcmatch.pathlib as wcp; p = wcp.Path('FILE.TXT'); result = p.match('*.txt', flags=wcp.IGNORECASE)",
        {"ok": True, "value": True},
    ),
    (
        'fnm_escape_star',
        "import wcmatch.fnmatch as fnm; result = fnm.fnmatch('*.txt', fnm.escape('*.txt'))",
        {"ok": True, "value": True},
    ),
    (
        'fnm_escape_question',
        "import wcmatch.fnmatch as fnm; result = fnm.fnmatch('?.py', fnm.escape('?.py'))",
        {"ok": True, "value": True},
    ),
    (
        'glob_escape_star',
        "import wcmatch.glob as glob; result = glob.globmatch('*.txt', glob.escape('*.txt'))",
        {"ok": True, "value": True},
    ),
    (
        'fnm_is_magic_true',
        "import wcmatch.fnmatch as fnm; result = fnm.is_magic('*.txt')",
        {"ok": True, "value": True},
    ),
    (
        'fnm_is_magic_false',
        "import wcmatch.fnmatch as fnm; result = fnm.is_magic('file.txt')",
        {"ok": True, "value": False},
    ),
    (
        'fnm_is_magic_question',
        "import wcmatch.fnmatch as fnm; result = fnm.is_magic('file?.txt')",
        {"ok": True, "value": True},
    ),
    (
        'glob_is_magic_doublestar',
        "import wcmatch.glob as glob; result = glob.is_magic('**/*.txt')",
        {"ok": True, "value": True},
    ),
    (
        'fnm_charclass_digit',
        "import wcmatch.fnmatch as fnm; result = fnm.fnmatch('file5.txt', 'file[0-9].txt')",
        {"ok": True, "value": True},
    ),
    (
        'fnm_charclass_letter',
        "import wcmatch.fnmatch as fnm; result = fnm.fnmatch('fileA.txt', 'file[A-Z].txt')",
        {"ok": True, "value": True},
    ),
    (
        'fnm_charclass_negation',
        "import wcmatch.fnmatch as fnm; result = fnm.fnmatch('fileX.txt', 'file[!0-9].txt')",
        {"ok": True, "value": True},
    ),
    (
        'fnm_charclass_list',
        "import wcmatch.fnmatch as fnm; result = fnm.fnmatch('a', '[abc]')",
        {"ok": True, "value": True},
    ),
    (
        'fnm_empty_pattern',
        "import wcmatch.fnmatch as fnm; result = fnm.fnmatch('', '')",
        {"ok": True, "value": True},
    ),
    (
        'fnm_empty_name',
        "import wcmatch.fnmatch as fnm; result = fnm.fnmatch('', 'test')",
        {"ok": True, "value": False},
    ),
    (
        'fnm_unicode',
        "import wcmatch.fnmatch as fnm; result = fnm.fnmatch('文件.txt', '*.txt')",
        {"ok": True, "value": True},
    ),
    (
        'glob_unicode',
        "import wcmatch.glob as glob; result = glob.globmatch('文档/文件.txt', '*/文件.txt')",
        {"ok": True, "value": True},
    ),
    (
        'fnm_combined_flags',
        "import wcmatch.fnmatch as fnm; result = fnm.fnmatch('TEST', '{test,other}', flags=fnm.BRACE | fnm.IGNORECASE)",
        {"ok": True, "value": True},
    ),
    (
        'glob_combined_flags',
        "import wcmatch.glob as glob; result = glob.globmatch('DIR/FILE.TXT', '{dir,other}/*.txt', flags=glob.BRACE | glob.IGNORECASE)",
        {"ok": True, "value": True},
    ),
    (
        'fnm_compile_match',
        "import wcmatch.fnmatch as fnm; matcher = fnm.compile('*.txt'); result = matcher.match('test.txt')",
        {"ok": True, "value": True},
    ),
    (
        'fnm_compile_nomatch',
        "import wcmatch.fnmatch as fnm; matcher = fnm.compile('*.txt'); result = matcher.match('test.py')",
        {"ok": True, "value": False},
    ),
    (
        'glob_compile_match',
        "import wcmatch.glob as glob; matcher = glob.compile('*/*.txt'); result = matcher.match('dir/file.txt')",
        {"ok": True, "value": True},
    ),
    (
        'fnm_matcher_filter',
        "import wcmatch.fnmatch as fnm; matcher = fnm.compile('*.txt'); result = sorted(matcher.filter(['a.txt', 'b.py', 'c.txt']))",
        {"ok": True, "value": ["a.txt", "c.txt"]},
    ),
    (
        'glob_matcher_filter',
        "import wcmatch.glob as glob; matcher = glob.compile('*/*.txt'); result = sorted(matcher.filter(['a/b.txt', 'c.py', 'd/e.txt']))",
        {"ok": True, "value": ["a/b.txt", "d/e.txt"]},
    ),
    (
        'fnm_dotmatch_hidden',
        "import wcmatch.fnmatch as fnm; result = fnm.fnmatch('.hidden', '*', flags=fnm.DOTMATCH)",
        {"ok": True, "value": True},
    ),
    (
        'fnm_no_dotmatch',
        "import wcmatch.fnmatch as fnm; result = fnm.fnmatch('.hidden', '*')",
        {"ok": True, "value": False},
    ),
    (
        'glob_dotmatch',
        "import wcmatch.glob as glob; result = glob.globmatch('.config/file', '*/*', flags=glob.DOTMATCH)",
        {"ok": True, "value": True},
    ),
    (
        'fnm_negate_negateall',
        "import wcmatch.fnmatch as fnm; result = fnm.fnmatch('test.py', '!*.txt', flags=fnm.NEGATE | fnm.NEGATEALL)",
        {"ok": True, "value": True},
    ),
    (
        'fnm_negate_list',
        "import wcmatch.fnmatch as fnm; result = fnm.fnmatch('test.txt', ['*', '!*.txt'], flags=fnm.NEGATE)",
        {"ok": True, "value": False},
    ),
    (
        'fnm_split_pipe',
        "import wcmatch.fnmatch as fnm; result = fnm.fnmatch('test.txt', '*.txt|*.py', flags=fnm.SPLIT)",
        {"ok": True, "value": True},
    ),
    (
        'fnm_split_both',
        "import wcmatch.fnmatch as fnm; result = fnm.fnmatch('test.py', '*.txt|*.py', flags=fnm.SPLIT)",
        {"ok": True, "value": True},
    ),
    (
        'fnm_bracket_simple',
        "import wcmatch.fnmatch as fnm; result = fnm.fnmatch('a', '[a-z]')",
        {"ok": True, "value": True},
    ),
    (
        'fnm_bracket_digit',
        "import wcmatch.fnmatch as fnm; result = fnm.fnmatch('5', '[0-9]')",
        {"ok": True, "value": True},
    ),
    (
        'fnm_bracket_upper',
        "import wcmatch.fnmatch as fnm; result = fnm.fnmatch('Z', '[A-Z]')",
        {"ok": True, "value": True},
    ),
    (
        'glob_sep_match',
        "import wcmatch.glob as glob; result = glob.globmatch('a/b/c', 'a/*/c')",
        {"ok": True, "value": True},
    ),
    (
        'glob_sep_doublestar_deep',
        "import wcmatch.glob as glob; result = glob.globmatch('a/b/c/d/e.txt', 'a/**/e.txt', flags=glob.GLOBSTAR)",
        {"ok": True, "value": True},
    ),
    (
        'fnm_multi_star',
        "import wcmatch.fnmatch as fnm; result = fnm.fnmatch('prefix_middle_suffix', 'prefix*middle*suffix')",
        {"ok": True, "value": True},
    ),
    (
        'fnm_multi_question',
        "import wcmatch.fnmatch as fnm; result = fnm.fnmatch('abc', '???')",
        {"ok": True, "value": True},
    ),
    (
        'fnm_filter_nomatch',
        "import wcmatch.fnmatch as fnm; result = fnm.filter(['a.py', 'b.js', 'c.go'], '*.txt')",
        {"ok": True, "value": []},
    ),
    (
        'glob_filter_nomatch',
        "import wcmatch.glob as glob; result = glob.globfilter(['a/b.py', 'c/d.js'], '*/*.txt')",
        {"ok": True, "value": []},
    ),
    (
        'fnm_brace_multiple',
        "import wcmatch.fnmatch as fnm; result = fnm.fnmatch('file.py', 'file.{txt,py,js}', flags=fnm.BRACE)",
        {"ok": True, "value": True},
    ),
    (
        'fnm_brace_prefix',
        "import wcmatch.fnmatch as fnm; result = fnm.fnmatch('test_file.txt', '{test,prod}_*.txt', flags=fnm.BRACE)",
        {"ok": True, "value": True},
    ),
    (
        'fnm_extmatch_nested',
        "import wcmatch.fnmatch as fnm; result = fnm.fnmatch('testtest', '+(test)', flags=fnm.EXTMATCH)",
        {"ok": True, "value": True},
    ),
    (
        'fnm_extmatch_optional_absent',
        "import wcmatch.fnmatch as fnm; result = fnm.fnmatch('', '?(test)', flags=fnm.EXTMATCH)",
        {"ok": True, "value": True},
    ),
    (
        'fnm_extmatch_not',
        "import wcmatch.fnmatch as fnm; result = fnm.fnmatch('file.py', '!(*.txt)', flags=fnm.EXTMATCH)",
        {"ok": True, "value": True},
    ),
    (
        'pathlib_extmatch',
        "import wcmatch.pathlib as wcp; p = wcp.Path('test.txt'); result = p.match('+(test).txt', flags=wcp.EXTMATCH)",
        {"ok": True, "value": True},
    ),
    (
        'pathlib_brace',
        "import wcmatch.pathlib as wcp; p = wcp.Path('file1.txt'); result = p.match('file{1,2}.txt', flags=wcp.BRACE)",
        {"ok": True, "value": True},
    ),
    (
        'fnm_case_lower',
        "import wcmatch.fnmatch as fnm; result = fnm.fnmatch('test', 'TEST')",
        {"ok": True, "value": False},
    ),
    (
        'fnm_case_ignorecase_exact',
        "import wcmatch.fnmatch as fnm; result = fnm.fnmatch('test', 'TEST', flags=fnm.IGNORECASE)",
        {"ok": True, "value": True},
    ),
    (
        'fnm_filter_empty_list',
        "import wcmatch.fnmatch as fnm; result = fnm.filter([], '*.txt')",
        {"ok": True, "value": []},
    ),
    (
        'glob_filter_empty_list',
        "import wcmatch.glob as glob; result = glob.globfilter([], '*.txt')",
        {"ok": True, "value": []},
    ),
    (
        'glob_globstar_flag',
        "import wcmatch.glob as glob; result = hasattr(glob, 'GLOBSTAR')",
        {"ok": True, "value": True},
    ),
    (
        'fnm_star_wildcard',
        "import wcmatch.fnmatch as fnm; result = fnm.fnmatch('anything', '*')",
        {"ok": True, "value": True},
    ),
    (
        'fnm_multiple_dots',
        "import wcmatch.fnmatch as fnm; result = fnm.fnmatch('file.tar.gz', '*.gz')",
        {"ok": True, "value": True},
    ),
    (
        'glob_relative_path_explicit',
        "import wcmatch.glob as glob; result = glob.globmatch('./file.txt', './*.txt')",
        {"ok": True, "value": True},
    ),
    (
        'fnm_brace_nested',
        "import wcmatch.fnmatch as fnm; result = fnm.fnmatch('a1', '{a,b}{1,2}', flags=fnm.BRACE)",
        {"ok": True, "value": True},
    ),
    (
        'glob_root_match',
        "import wcmatch.glob as glob; result = glob.globmatch('file.txt', 'file.txt')",
        {"ok": True, "value": True},
    ),
]

assert len(CASES) == 90, f"Expected 90 cases, got {len(CASES)}"


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
