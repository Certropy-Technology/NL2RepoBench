from __future__ import annotations

import json

from nl2repobench.verification.candidate_client import execute_script


LEAF_IDS = [
    "metadata-version",
    "metadata-runtime-dependencies",
    "root-exports",
    "compatibility-imports",
    "construct-memory-root",
    "iterdir-order-types",
    "implied-directories",
    "read-text-bytes",
    "text-encodings",
    "write-text-binary",
    "open-directory-error",
    "open-binary-argument-errors",
    "open-missing-error",
    "joinpath-division",
    "pathlike-source",
    "parent-and-at",
    "writable-archive-mutation",
    "repeat-read-keeps-archive-open",
    "subclass-preservation",
    "string-and-repr",
    "filename-name-root-parent",
    "suffixes-and-stem",
    "unnamed-root",
    "glob-basic",
    "glob-recursive",
    "glob-directories",
    "glob-character-sets",
    "glob-invalid-patterns",
    "path-match",
    "equality-and-hash",
    "symlink-mode",
    "relative-to",
    "pickle-roundtrip",
    "traversable-interface",
    "complete-dirs-getinfo",
    "complete-dirs-inject",
    "malformed-and-special-names",
    "overlay-compatibility",
]


SCENARIO = r'''
import importlib
import importlib.metadata
import importlib.resources.abc
import io
import pathlib
import pickle
import stat
import tempfile
import zipfile

import zipp


outcomes = []


def record(identifier, check):
    try:
        check()
    except BaseException as exc:
        outcomes.append({
            "id": identifier,
            "status": "failed",
            "message": f"{type(exc).__module__}.{type(exc).__qualname__}: {exc}"[:1000],
        })
    else:
        outcomes.append({"id": identifier, "status": "passed"})


def ensure(condition, message="assertion failed"):
    if not condition:
        raise AssertionError(message)


def raises(expected, operation):
    try:
        operation()
    except expected:
        return
    except BaseException as exc:
        raise AssertionError(f"expected {expected.__name__}, got {type(exc).__name__}") from exc
    raise AssertionError(f"expected {expected.__name__}")


def archive_fixture(*, explicit_dirs=False):
    data = io.BytesIO()
    archive = zipfile.ZipFile(data, "w")
    archive.writestr("a.txt", b"content of a")
    archive.writestr("b/c.txt", b"content of c")
    archive.writestr("b/d/e.txt", b"content of e")
    archive.writestr("b/f.txt", b"content of f")
    archive.writestr("g/h/i.txt", b"content of i")
    archive.writestr("j/k.bin", b"content of k")
    archive.writestr("j/l.baz", b"content of l")
    archive.writestr("j/m.bar", b"content of m")
    archive.writestr("n.txt", b"a.txt")
    archive.infolist()[-1].external_attr |= stat.S_IFLNK << 16
    if explicit_dirs:
        zipp.CompleteDirs.inject(archive)
    archive.filename = "alpharep.zip"
    return archive


def test_metadata_version():
    ensure(importlib.metadata.version("zipp") == "4.1.0")
    ensure(importlib.metadata.metadata("zipp")["Name"] == "zipp")


def test_metadata_runtime_dependencies():
    requires = importlib.metadata.requires("zipp")
    ensure(all("extra ==" in requirement for requirement in (requires or [])), requires)


def test_root_exports():
    ensure(zipp.__all__ == ["Path"], zipp.__all__)
    ensure(zipp.Path.__module__ == "zipp")
    ensure(hasattr(zipp, "CompleteDirs") and hasattr(zipp, "FastLookup"))


def test_compatibility_imports():
    ensure(importlib.import_module("zipp.glob"))
    ensure(importlib.import_module("zipp.compat"))
    ensure(importlib.import_module("zipp.compat.overlay"))


def test_construct_memory_root():
    archive = archive_fixture()
    root = zipp.Path(archive)
    ensure(root.at == "" and root.root is archive)
    ensure(root.is_dir() and root.exists() is False)


def test_iterdir_order_types():
    root = zipp.Path(archive_fixture())
    children = list(root.iterdir())
    ensure([item.at for item in children] == ["a.txt", "n.txt", "b/", "g/", "j/"])
    ensure([item.is_file() for item in children[:2]] == [True, True])
    ensure(all(item.is_dir() for item in children[2:]))
    raises(NotADirectoryError, lambda: next(children[0].iterdir()))


def test_implied_directories():
    root = zipp.Path(archive_fixture())
    ensure((root / "b").at == "b/" and (root / "b").is_dir())
    ensure([item.at for item in (root / "b").iterdir()] == ["b/c.txt", "b/f.txt", "b/d/"])
    ensure((root / "g" / "h" / "i.txt").read_text(encoding="utf-8") == "content of i")


def test_read_text_bytes():
    member = zipp.Path(archive_fixture()) / "a.txt"
    ensure(member.read_text(encoding="utf-8") == "content of a")
    ensure(member.read_text("utf-8") == "content of a")
    ensure(member.read_bytes() == b"content of a")


def test_text_encodings():
    data = io.BytesIO()
    archive = zipfile.ZipFile(data, "w")
    archive.writestr("text/utf16.txt", "snowman: \u2603".encode("utf-16"))
    archive.writestr("text/bad.bin", b"bad: \xff\xff")
    archive.filename = "encoding.zip"
    root = zipp.Path(archive)
    ensure((root / "text" / "utf16.txt").read_text("utf-16") == "snowman: \u2603")
    ensure((root / "text" / "bad.bin").read_text("utf-8", errors="ignore") == "bad: ")
    raises(TypeError, lambda: (root / "text" / "bad.bin").read_text("utf-8", encoding="utf-8"))


def test_write_text_binary():
    archive = zipfile.ZipFile(io.BytesIO(), "w")
    root = zipp.Path(archive)
    with (root / "file.bin").open("wb") as stream:
        stream.write(b"binary")
    with (root / "file.txt").open("w", encoding="utf-8") as stream:
        stream.write("text")
    ensure(archive.read("file.bin") == b"binary")
    ensure(archive.read("file.txt") == b"text")


def test_open_directory_error():
    root = zipp.Path(archive_fixture())
    raises(IsADirectoryError, lambda: (root / "b").open())


def test_open_binary_argument_errors():
    member = zipp.Path(archive_fixture()) / "a.txt"
    raises(ValueError, lambda: member.open("rb", encoding="utf-8"))
    raises(ValueError, lambda: member.open("rb", "utf-8"))


def test_open_missing_error():
    root = zipp.Path(archive_fixture())
    raises(FileNotFoundError, lambda: (root / "missing.txt").open())


def test_joinpath_division():
    root = zipp.Path(archive_fixture())
    ensure(root.joinpath("b", "d", "e.txt").read_text(encoding="utf-8") == "content of e")
    ensure((root / "b" / "c.txt").read_text(encoding="utf-8") == "content of c")


def test_pathlike_source():
    with tempfile.TemporaryDirectory() as directory:
        target = pathlib.Path(directory) / "sample.zip"
        with zipfile.ZipFile(target, "w") as archive:
            archive.writestr("x.txt", "x")
        root = zipp.Path(target)
        ensure((root / pathlib.PurePosixPath("x.txt")).read_text(encoding="utf-8") == "x")
        root.root.close()


def test_parent_and_at():
    root = zipp.Path(archive_fixture())
    ensure((root / "foo" / "bar").at == "foo/bar")
    ensure((root / "a").parent.at == "")
    ensure((root / "a" / "b").parent.at == "a/")
    ensure((root / "b/").parent.at == "")
    ensure((root / "missing/").parent.at == "")


def test_writable_archive_mutation():
    archive = archive_fixture()
    root = zipp.Path(archive)
    archive.writestr("new.txt", "new")
    archive.writestr("later/item.txt", "later")
    ensure((root / "new.txt").read_text(encoding="utf-8") == "new")
    ensure((root / "later" / "item.txt").read_text(encoding="utf-8") == "later")


def test_repeat_read_keeps_archive_open():
    with tempfile.TemporaryDirectory() as directory:
        target = pathlib.Path(directory) / "repeat.zip"
        archive = archive_fixture()
        archive.close()
        target.write_bytes(archive.fp.getvalue() if archive.fp else b"")
        # Recreate because ZipFile clears fp on close.
        with zipfile.ZipFile(target, "w") as writer:
            writer.writestr("a.txt", "content")
        with zipfile.ZipFile(target) as reader:
            for _ in range(2):
                ensure(zipp.Path(reader, "a.txt").read_text(encoding="utf-8") == "content")
            ensure(reader.fp is not None)


def test_subclass_preservation():
    class Child(zipp.Path):
        pass
    child = Child(archive_fixture()) / "b" / "c.txt"
    ensure(isinstance(child, Child))
    ensure(isinstance(child.parent, Child))


def test_string_and_repr():
    root = zipp.Path(archive_fixture())
    child = root / "b" / "c.txt"
    ensure(str(root) == "alpharep.zip")
    ensure(str(child) == "alpharep.zip/b/c.txt")
    ensure(repr(child) == "Path('alpharep.zip', 'b/c.txt')", repr(child))


def test_filename_name_root_parent():
    root = zipp.Path(archive_fixture())
    ensure(root.filename == pathlib.Path("alpharep.zip"))
    ensure(root.name == "alpharep.zip")
    ensure(root.parent == pathlib.Path("."))
    root.root.filename = "dir/sample.zip"
    ensure(root.parent == pathlib.Path("dir"))


def test_suffixes_and_stem():
    root = zipp.Path(archive_fixture())
    target = root / "folder" / "name.tar.gz"
    ensure(target.name == "name.tar.gz")
    ensure(target.suffix == ".gz")
    ensure(target.suffixes == [".tar", ".gz"])
    ensure(target.stem == "name.tar")
    ensure((root / ".gitignore").suffixes == [] and (root / ".gitignore").stem == ".gitignore")


def test_unnamed_root():
    archive = archive_fixture()
    archive.filename = None
    root = zipp.Path(archive)
    ensure(str(root) == ":zipfile:")
    ensure(str(root / "foo") == ":zipfile:/foo")
    raises(TypeError, lambda: root.name)
    raises(TypeError, lambda: root.filename)
    raises(TypeError, lambda: root.parent)
    ensure((root / "b").name == "b")


def test_glob_basic():
    root = zipp.Path(archive_fixture())
    ensure([item.at for item in root.glob("b/*.txt")] == ["b/c.txt", "b/f.txt"])
    ensure([item.at for item in root.glob("b/c.*")] == ["b/c.txt"])
    ensure(list(root.glob("*.xt")) == [])


def test_glob_recursive():
    root = zipp.Path(archive_fixture())
    globbed = [item.at for item in root.glob("**/*.txt")]
    rglobbed = [item.at for item in root.rglob("*.txt")]
    ensure(globbed == rglobbed)
    ensure(globbed == ["b/c.txt", "b/d/e.txt", "b/f.txt", "g/h/i.txt"])


def test_glob_directories():
    root = zipp.Path(archive_fixture())
    ensure([item.at for item in root.glob("b")] == ["b/"])
    ensure([item.at for item in root.glob("g*/h*")] == ["g/h/"])
    ensure(list(root.glob("*/i.txt")) == [])
    ensure([item.at for item in root.rglob("*/i.txt")] == ["g/h/i.txt"])


def test_glob_character_sets():
    root = zipp.Path(archive_fixture())
    ensure([item.at for item in root.glob("a?txt")] == ["a.txt"])
    ensure([item.at for item in root.glob("a[.]txt")] == ["a.txt"])
    ensure([item.at for item in root.glob("j/?.b[ai][nz]")] == ["j/k.bin", "j/l.baz"])


def test_glob_invalid_patterns():
    root = zipp.Path(archive_fixture())
    raises(ValueError, lambda: list(root.glob("")))
    raises(ValueError, lambda: list(root.glob("**bad")))


def test_path_match():
    root = zipp.Path(archive_fixture())
    ensure((root / "b" / "c.txt").match("*.txt"))
    ensure(not root.match("*.txt"))


def test_equality_and_hash():
    archive = archive_fixture()
    root = zipp.Path(archive)
    ensure(root == zipp.Path(archive))
    ensure(root != root / "a.txt")
    ensure(root / "a.txt" == root / "a.txt")
    ensure(hash(root / "a.txt") == hash(root / "a.txt"))
    ensure(root in {root})


def test_symlink_mode():
    root = zipp.Path(archive_fixture())
    ensure(not (root / "a.txt").is_symlink())
    ensure((root / "n.txt").is_symlink())


def test_relative_to():
    root = zipp.Path(archive_fixture())
    ensure((root / "b" / "c.txt").relative_to(root / "b") == "c.txt")
    ensure((root / "b" / "d" / "e.txt").relative_to(root / "b") == "d/e.txt")


def test_pickle_roundtrip():
    with tempfile.TemporaryDirectory() as directory:
        target = pathlib.Path(directory) / "pickle.zip"
        with zipfile.ZipFile(target, "w") as archive:
            archive.writestr("b/c.txt", "content")
        restored = pickle.loads(pickle.dumps(zipp.Path(target, "b/")))
        ensure((restored / "c.txt").read_text(encoding="utf-8") == "content")
        restored.root.close()


def test_traversable_interface():
    root = zipp.Path(archive_fixture())
    ensure(isinstance(root, importlib.resources.abc.Traversable))


def test_complete_dirs_getinfo():
    complete = zipp.CompleteDirs.make(archive_fixture())
    names = complete.namelist()
    ensure(names[-5:] == ["b/", "b/d/", "g/h/", "g/", "j/"])
    ensure(complete.resolve_dir("b") == "b/")
    ensure(complete.getinfo("b/").filename == "b/")
    raises(KeyError, lambda: complete.getinfo("missing/"))


def test_complete_dirs_inject():
    archive = archive_fixture()
    returned = zipp.CompleteDirs.inject(archive)
    ensure(returned is archive)
    ensure([name for name in archive.namelist() if name.endswith("/")] == ["b/", "b/d/", "g/h/", "g/", "j/"])


def test_malformed_and_special_names():
    data = io.BytesIO()
    archive = zipfile.ZipFile(data, "w")
    archive.writestr("/hidden.txt", b"hidden")
    archive.writestr("../parent.txt", b"parent")
    archive.writestr("V: NMS.flac", b"audio")
    info = zipfile.ZipInfo("foo\\bar")
    archive.writestr(info, b"backslash")
    archive.filename = ""
    root = zipp.Path(archive)
    ensure([item.at for item in root.iterdir()] == ["V: NMS.flac", "foo\\bar", "../"])
    ensure((root / ".." / "parent.txt").read_bytes() == b"parent")
    ensure((root / "V: NMS.flac").read_bytes() == b"audio")
    ensure((root / "foo\\bar").name == "foo\\bar")


def test_overlay_compatibility():
    overlay = importlib.import_module("zipp.compat.overlay")
    ensure(overlay.zipfile.Path is zipp.Path)
    ensure(overlay.zipfile._path is zipp)
    ensure(overlay.zipfile.ZipFile is zipfile.ZipFile)
    hash(overlay.zipfile)


checks = [
    ("metadata-version", test_metadata_version),
    ("metadata-runtime-dependencies", test_metadata_runtime_dependencies),
    ("root-exports", test_root_exports),
    ("compatibility-imports", test_compatibility_imports),
    ("construct-memory-root", test_construct_memory_root),
    ("iterdir-order-types", test_iterdir_order_types),
    ("implied-directories", test_implied_directories),
    ("read-text-bytes", test_read_text_bytes),
    ("text-encodings", test_text_encodings),
    ("write-text-binary", test_write_text_binary),
    ("open-directory-error", test_open_directory_error),
    ("open-binary-argument-errors", test_open_binary_argument_errors),
    ("open-missing-error", test_open_missing_error),
    ("joinpath-division", test_joinpath_division),
    ("pathlike-source", test_pathlike_source),
    ("parent-and-at", test_parent_and_at),
    ("writable-archive-mutation", test_writable_archive_mutation),
    ("repeat-read-keeps-archive-open", test_repeat_read_keeps_archive_open),
    ("subclass-preservation", test_subclass_preservation),
    ("string-and-repr", test_string_and_repr),
    ("filename-name-root-parent", test_filename_name_root_parent),
    ("suffixes-and-stem", test_suffixes_and_stem),
    ("unnamed-root", test_unnamed_root),
    ("glob-basic", test_glob_basic),
    ("glob-recursive", test_glob_recursive),
    ("glob-directories", test_glob_directories),
    ("glob-character-sets", test_glob_character_sets),
    ("glob-invalid-patterns", test_glob_invalid_patterns),
    ("path-match", test_path_match),
    ("equality-and-hash", test_equality_and_hash),
    ("symlink-mode", test_symlink_mode),
    ("relative-to", test_relative_to),
    ("pickle-roundtrip", test_pickle_roundtrip),
    ("traversable-interface", test_traversable_interface),
    ("complete-dirs-getinfo", test_complete_dirs_getinfo),
    ("complete-dirs-inject", test_complete_dirs_inject),
    ("malformed-and-special-names", test_malformed_and_special_names),
    ("overlay-compatibility", test_overlay_compatibility),
]

for identifier, check in checks:
    record(identifier, check)

result = outcomes
'''


def main() -> None:
    response = execute_script(SCENARIO, timeout_sec=45.0)
    leaves: list[dict[str, str]]
    if response.ok and isinstance(response.value, list):
        by_id = {
            item.get("id"): item
            for item in response.value
            if isinstance(item, dict) and isinstance(item.get("id"), str)
        }
        leaves = []
        for identifier in LEAF_IDS:
            item = by_id.get(identifier)
            if item is None or item.get("status") not in {"passed", "failed"}:
                leaves.append({
                    "id": identifier,
                    "status": "failed",
                    "message": "candidate scenario omitted a valid leaf outcome",
                })
                continue
            leaf = {"id": identifier, "status": str(item["status"])}
            if leaf["status"] == "failed":
                leaf["message"] = str(item.get("message", "scenario failed"))[:1000]
            leaves.append(leaf)
    else:
        message = (
            f"{response.exception_type}: {response.exception_message}"
            if not response.ok
            else "candidate scenario returned an invalid report"
        )
        leaves = [
            {"id": identifier, "status": "failed", "message": message[:1000]}
            for identifier in LEAF_IDS
        ]
    print(json.dumps({"schema_version": "1.0", "leaves": leaves}, sort_keys=True))


if __name__ == "__main__":
    main()
