#!/usr/bin/env python3
"""Child-side GitPython contract cases."""

from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path


def repo_with_config(root: str, *, bare: bool = False):
    from git import Repo

    repo = Repo.init(root, bare=bare)
    if not bare:
        with repo.config_writer() as writer:
            writer.set_value("user", "name", "Harbor Test")
            writer.set_value("user", "email", "harbor@example.invalid")
    return repo


def commit_file(repo, name: str, content: str, message: str):
    path = Path(repo.working_tree_dir) / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    repo.index.add([name])
    return repo.index.commit(message)


def case_01() -> None:
    import git
    from git import Actor, Git, Repo

    assert git.__version__ == "3.1.60"
    assert Repo and Git and Actor
    assert "Repo" in git.__all__


def case_02() -> None:
    from git import Repo

    with tempfile.TemporaryDirectory() as root:
        repo = repo_with_config(root)
        assert repo.bare is False
        assert repo.working_tree_dir == os.path.abspath(root)
        assert repo.git_dir == os.path.join(os.path.abspath(root), ".git")
        assert Repo(root).git_dir == repo.git_dir


def case_03() -> None:
    with tempfile.TemporaryDirectory() as root:
        repo = repo_with_config(root)
        commit = commit_file(repo, "hello.txt", "hello\n", "initial")
        assert len(commit.hexsha) == 40
        assert commit.message.strip() == "initial"
        assert commit.author.name == "Harbor Test"
        assert commit.author.email == "harbor@example.invalid"


def case_04() -> None:
    from git import Repo

    with tempfile.TemporaryDirectory() as root:
        repo = repo_with_config(root)
        first = commit_file(repo, "history.txt", "one\n", "first")
        second = commit_file(repo, "history.txt", "two\n", "second")
        commits = list(repo.iter_commits())
        assert [item.hexsha for item in commits[:2]] == [second.hexsha, first.hexsha]
        assert repo.commit("HEAD~1").hexsha == first.hexsha
        assert Repo(root).head.commit.hexsha == second.hexsha


def case_05() -> None:
    with tempfile.TemporaryDirectory() as root:
        repo = repo_with_config(root)
        commit_file(repo, "src/module.py", "answer = 42\n", "tree")
        tree = repo.tree("HEAD")
        blob = tree / "src" / "module.py"
        assert tree.type == "tree"
        assert blob.type == "blob"
        assert blob.path == "src/module.py"
        assert blob.data_stream.read() == b"answer = 42\n"
        assert blob.size == len(b"answer = 42\n")


def case_06() -> None:
    with tempfile.TemporaryDirectory() as root:
        repo = repo_with_config(root)
        commit_file(repo, "tracked.txt", "before\n", "tracked")
        Path(root, "tracked.txt").write_text("after\n", encoding="utf-8")
        assert repo.is_dirty() is True
        assert "tracked.txt" in repo.git.diff()
        assert repo.is_dirty(untracked_files=False) is True


def case_07() -> None:
    with tempfile.TemporaryDirectory() as root:
        repo = repo_with_config(root)
        commit_file(repo, "remove.txt", "remove\n", "remove")
        Path(root, "remove.txt").unlink()
        repo.index.remove(["remove.txt"])
        assert list(repo.index.diff(None)) == []
        assert "remove.txt" in repo.git.diff("HEAD")


def case_08() -> None:
    with tempfile.TemporaryDirectory() as root:
        repo = repo_with_config(root)
        main_commit = commit_file(repo, "branch.txt", "main\n", "main")
        feature = repo.create_head("feature")
        assert feature.commit.hexsha == main_commit.hexsha
        feature.checkout()
        feature_commit = commit_file(repo, "branch.txt", "feature\n", "feature")
        assert repo.active_branch.name == "feature"
        assert repo.heads.feature.commit.hexsha == feature_commit.hexsha
        assert [head.name for head in repo.heads] == ["feature", "master"] or [
            head.name for head in repo.heads
        ] == ["master", "feature"]


def case_09() -> None:
    with tempfile.TemporaryDirectory() as root:
        repo = repo_with_config(root)
        commit = commit_file(repo, "tag.txt", "tag\n", "tagged")
        tag = repo.create_tag("v1.0", message="release")
        assert tag.name == "v1.0"
        assert tag.commit.hexsha == commit.hexsha
        assert repo.tags[0].name == "v1.0"


def case_10() -> None:
    with tempfile.TemporaryDirectory() as root:
        repo = repo_with_config(root)
        with repo.config_writer() as writer:
            writer.set_value("core", "filemode", "false")
            writer.set_value("harbor", "mode", "local")
        reader = repo.config_reader()
        assert reader.get("core", "filemode") == "false"
        assert reader.get("harbor", "mode") == "local"
        assert reader.getboolean("core", "filemode") is False


def case_11() -> None:
    from git import Actor

    actor = Actor._from_string("Jane Doe <jane@example.invalid>")
    assert actor.name == "Jane Doe"
    assert actor.email == "jane@example.invalid"
    assert Actor("Jane Doe", "jane@example.invalid") == actor
    assert str(actor) == "Jane Doe"


def case_12() -> None:
    with tempfile.TemporaryDirectory() as root:
        repo = repo_with_config(root)
        commit = commit_file(repo, "command.txt", "command\n", "command")
        assert repo.git.rev_parse("HEAD") == commit.hexsha
        assert commit.hexsha[:7] in repo.git.log("--oneline")
        assert repo.git.status("--short") == ""


def case_13() -> None:
    with tempfile.TemporaryDirectory() as root:
        repo = repo_with_config(root)
        commit = commit_file(repo, "revision.txt", "revision\n", "revision")
        assert repo.rev_parse("HEAD^{commit}").hexsha == commit.hexsha
        assert repo.tree("HEAD").hexsha == commit.tree.hexsha
        assert repo.commit(commit.hexsha).tree.hexsha == commit.tree.hexsha


def case_14() -> None:
    with tempfile.TemporaryDirectory() as root:
        repo = repo_with_config(root)
        base = commit_file(repo, "merge.txt", "base\n", "base")
        feature = repo.create_head("feature")
        feature.checkout()
        head = commit_file(repo, "merge.txt", "feature\n", "feature")
        assert repo.is_ancestor(base, head)
        assert repo.merge_base(base, head)[0].hexsha == base.hexsha


def case_15() -> None:
    from git import Repo

    with tempfile.TemporaryDirectory() as root:
        repo = repo_with_config(root, bare=True)
        assert repo.bare is True
        assert repo.working_tree_dir is None
        assert Repo(root).bare is True
        assert Path(repo.git_dir).is_dir()


def case_16() -> None:
    from git import Repo

    with tempfile.TemporaryDirectory() as parent:
        source = Path(parent, "source")
        destination = Path(parent, "clone")
        source_repo = repo_with_config(str(source))
        commit = commit_file(source_repo, "clone.txt", "cloned\n", "clone")
        cloned = Repo.clone_from(str(source), str(destination))
        assert cloned.head.commit.hexsha == commit.hexsha
        assert (destination / "clone.txt").read_text(encoding="utf-8") == "cloned\n"


def case_17() -> None:
    with tempfile.TemporaryDirectory() as root:
        repo = repo_with_config(root)
        commit_file(repo, "diff.txt", "old\n", "diff")
        Path(root, "diff.txt").write_text("new\n", encoding="utf-8")
        diff = repo.index.diff(None)
        assert len(diff) == 1
        assert diff[0].a_path == "diff.txt"
        assert diff[0].change_type == "M"


def case_18() -> None:
    from git import InvalidGitRepositoryError, NoSuchPathError, Repo

    with tempfile.TemporaryDirectory() as root:
        missing = Path(root, "missing")
        try:
            Repo(str(missing))
        except NoSuchPathError:
            pass
        else:
            raise AssertionError("missing path did not raise NoSuchPathError")
        invalid = Path(root, "invalid")
        invalid.mkdir()
        try:
            Repo(str(invalid))
        except InvalidGitRepositoryError:
            pass
        else:
            raise AssertionError("invalid repository did not raise InvalidGitRepositoryError")


def case_19() -> None:
    from git import Git

    with tempfile.TemporaryDirectory() as root:
        git = Git(root)
        output = git.execute(["git", "--version"])
        assert output.startswith("git version ")
        assert git.version_info[0] >= 2


def case_20() -> None:
    with tempfile.TemporaryDirectory() as root:
        repo = repo_with_config(root)
        commit = commit_file(repo, "stats.txt", "one\n", "stats")
        assert commit.stats.total["files"] == 1
        assert commit.stats.total["insertions"] == 1
        assert commit.stats.total["deletions"] == 0
        assert repo.head.is_valid()


CASES = {f"gitpython-{index:02d}": globals()[f"case_{index:02d}"] for index in range(1, 21)}


def main() -> None:
    case = CASES[sys.argv[1]]
    case()


if __name__ == "__main__":
    main()
