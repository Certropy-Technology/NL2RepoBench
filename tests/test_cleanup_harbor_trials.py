from __future__ import annotations

from pathlib import Path

from nl2repobench.harbor_cleanup import project_for_trial, trial_dirs


def test_trial_dirs_are_limited_to_jobs_tree(tmp_path: Path) -> None:
    first = tmp_path / "task" / "harbor__ABC123"
    second = tmp_path / "task" / "harbor__XYZ789"
    first.mkdir(parents=True)
    second.mkdir(parents=True)
    (first / "lock.json").write_text("{}", encoding="utf-8")
    (second / "result.json").write_text("{}", encoding="utf-8")
    assert trial_dirs(tmp_path) == (first,)


def test_project_name_is_exact_and_fail_closed() -> None:
    assert project_for_trial(Path("harbor__ABC123")) == "harbor__abc123__env"
    assert project_for_trial(Path("bad name")) is None
