from __future__ import annotations

import json
import os
import pathlib
import re
import sys
import tempfile
import warnings


def record(results: dict[str, object], name: str, function) -> None:
    try:
        results[name] = bool(function())
    except BaseException as exc:  # Candidate behavior is reported, not trusted.
        results[name] = {"error": type(exc).__name__, "message": str(exc)[:300]}


def main() -> None:
    candidate_site = pathlib.Path(sys.argv[1]).resolve()
    sys.path.insert(0, str(candidate_site))
    warnings.simplefilter("ignore", DeprecationWarning)

    import pathspec
    from pathspec import GitIgnoreSpec, PathSpec
    from pathspec.pattern import Pattern, RegexPattern
    from pathspec.patterns.gitignore.basic import GitIgnoreBasicPattern
    from pathspec.patterns.gitwildmatch import GitWildMatchPattern
    from pathspec.util import (
        AlreadyRegisteredError,
        CheckResult,
        RecursionError as PathRecursionError,
        append_dir_sep,
        check_match_file,
        detailed_match_files,
        iter_tree_entries,
        iter_tree_files,
        lookup_pattern,
        match_file,
        normalize_file,
        register_pattern,
    )

    out: dict[str, object] = {}
    record(out, "exports.root", lambda: all(hasattr(pathspec, name) for name in (
        "GitIgnoreSpec", "PathSpec", "Pattern", "RegexPattern", "RecursionError",
        "lookup_pattern", "__author__", "__copyright__", "__credits__",
        "__license__", "__version__",
    )))
    record(out, "exports.version", lambda: pathspec.__version__ == "1.1.1")
    record(out, "exports.factory", lambda: lookup_pattern("gitwildmatch") is GitWildMatchPattern)

    record(out, "pattern.include", lambda: (Pattern(True).include, Pattern(False).include, Pattern(None).include) == (True, False, None))
    def abstract_raises() -> bool:
        try:
            Pattern(True).match_file("a")
        except NotImplementedError:
            return True
        return False
    record(out, "pattern.abstract", abstract_raises)
    record(out, "regex.match", lambda: RegexPattern(r"[.]py$").match_file("x.py") is not None)
    record(out, "regex.no-match", lambda: RegexPattern(r"[.]py$").match_file("x.txt") is None)
    record(out, "regex.precompiled", lambda: RegexPattern(re.compile(r"^a"), False).include is False)
    record(out, "regex.value-semantics", lambda: RegexPattern("abc") == RegexPattern("abc") and str(RegexPattern("abc")) == "abc")

    record(out, "wildmatch.star", lambda: GitWildMatchPattern("*.py").match_file("src/a.py") is not None)
    record(out, "wildmatch.negation", lambda: GitWildMatchPattern("!*.tmp").include is False)
    record(out, "wildmatch.comment", lambda: GitWildMatchPattern("# note").include is None)
    record(out, "wildmatch.escape-comment", lambda: GitWildMatchPattern(r"\#name").match_file("#name") is not None)
    record(out, "wildmatch.double-star", lambda: GitWildMatchPattern("**/build/").match_file("a/build/x") is not None)
    record(out, "wildmatch.character-class", lambda: GitWildMatchPattern("[ab].txt").match_file("b.txt") is not None)
    record(out, "wildmatch.escape-api", lambda: GitWildMatchPattern.escape("a[b]*#?!") == r"a\[b\]\*\#\?\!")
    def invalid_pattern() -> bool:
        try:
            GitWildMatchPattern("foo\\")
        except ValueError:
            return True
        return False
    record(out, "wildmatch.invalid", invalid_pattern)

    spec = PathSpec.from_lines("gitwildmatch", ["*.py", "!test_*.py"], backend="simple")
    record(out, "pathspec.length", lambda: len(spec) == 2)
    record(out, "pathspec.match-file", lambda: spec.match_file("pkg/main.py") and not spec.match_file("test_main.py"))
    record(out, "pathspec.match-files-order", lambda: list(spec.match_files(["a.py", "test_a.py", "b.py"])) == ["a.py", "b.py"])
    record(out, "pathspec.check-file", lambda: spec.check_file("test_a.py") == CheckResult("test_a.py", False, 1))
    record(out, "pathspec.check-files", lambda: [x.include for x in spec.check_files(["a.py", "a.txt"])] == [True, None])
    record(out, "pathspec.negate", lambda: list(spec.match_files(["a.py", "a.txt"], negate=True)) == ["a.txt"])
    record(out, "pathspec.generator-lines", lambda: PathSpec.from_lines("gitwildmatch", (x for x in ["*.txt"]), backend="simple").match_file("a.txt"))
    def rejects_string_lines() -> bool:
        try:
            PathSpec.from_lines("gitwildmatch", "*.py", backend="simple")
        except TypeError:
            return True
        return False
    record(out, "pathspec.reject-string-lines", rejects_string_lines)
    record(out, "pathspec.add", lambda: len(spec + PathSpec.from_lines("gitwildmatch", ["*.txt"], backend="simple")) == 3)
    def inplace() -> bool:
        left = PathSpec.from_lines("gitwildmatch", ["*.py"], backend="simple")
        left += PathSpec.from_lines("gitwildmatch", ["*.txt"], backend="simple")
        return len(left) == 2 and left.match_file("x.txt")
    record(out, "pathspec.iadd", inplace)
    record(out, "pathspec.equality", lambda: PathSpec.from_lines("gitwildmatch", ["*.py"], backend="simple") == PathSpec.from_lines("gitwildmatch", ["*.py"], backend="simple"))
    record(out, "pathspec.repr", lambda: "backend='simple'" in repr(spec) and "patterns=" in repr(spec))

    git = GitIgnoreSpec.from_lines(["build/", "!build/keep.txt", "*.log"], backend="simple")
    record(out, "gitignore.default-factory", lambda: len(git.patterns) == 3)
    record(out, "gitignore.directory", lambda: git.match_file("build/a.bin"))
    record(out, "gitignore.reinclude", lambda: not git.match_file("build/keep.txt"))
    record(out, "gitignore.last-rule", lambda: GitIgnoreSpec.from_lines(["*.txt", "!important.txt"], backend="simple").check_file("important.txt").index == 1)
    def reject_basic() -> bool:
        try:
            GitIgnoreSpec.from_lines(["*.py"], GitIgnoreBasicPattern, backend="simple")
        except TypeError:
            return True
        return False
    record(out, "gitignore.reject-basic", reject_basic)

    record(out, "util.normalize", lambda: normalize_file("./a\\b.txt", separators=("\\",)) == "a/b.txt")
    pats = [GitWildMatchPattern("*.txt"), GitWildMatchPattern("!b.txt")]
    record(out, "util.match-file", lambda: match_file(pats, "a.txt") and not match_file(pats, "b.txt"))
    record(out, "util.check-last", lambda: check_match_file(enumerate(pats), "b.txt") == (False, 1))
    record(out, "util.details", lambda: list(detailed_match_files(pats, ["a.txt", "b.txt"])) == ["a.txt"])
    def registration() -> bool:
        name = "nl2repo-pathspec-private"
        register_pattern(name, GitWildMatchPattern, override=True)
        try:
            register_pattern(name, GitWildMatchPattern)
        except AlreadyRegisteredError as exc:
            return exc.name == name and exc.pattern_factory is GitWildMatchPattern
        return False
    record(out, "util.registration", registration)

    with tempfile.TemporaryDirectory(prefix="pathspec-child-") as temporary:
        root = pathlib.Path(temporary)
        (root / "sub").mkdir()
        (root / "a.txt").write_text("a", encoding="utf-8")
        (root / "sub" / "b.py").write_text("b", encoding="utf-8")
        record(out, "filesystem.files", lambda: set(iter_tree_files(root, follow_links=False)) == {"a.txt", os.path.join("sub", "b.py")})
        record(out, "filesystem.entries", lambda: {(x.path, x.is_dir(), x.is_file()) for x in iter_tree_entries(root, follow_links=False)} == {("a.txt", False, True), ("sub", True, False), (os.path.join("sub", "b.py"), False, True)})
        record(out, "filesystem.append-dir", lambda: append_dir_sep(root / "sub").endswith(os.sep) and not append_dir_sep(root / "a.txt").endswith(os.sep))

    out["runtime.uid"] = os.getuid() == 10001
    print(json.dumps({"schema_version": "1.0", "results": out}, sort_keys=True))


if __name__ == "__main__":
    main()
