from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

from nl2repobench.verification.candidate_client import (
    CandidateCallResult,
    execute_script,
    metadata_requires,
)


def scenario(source: str, timeout: float = 35.0) -> CandidateCallResult:
    return execute_script(source, timeout_sec=timeout)


def pytest_script(
    body: str, args: tuple[str, ...] = (), conftest: str | None = None
) -> str:
    encoded_body = json.dumps(body)
    encoded_args = json.dumps(list(args))
    encoded_conftest = "None" if conftest is None else json.dumps(conftest)
    return f"""
import json, os, pathlib, subprocess, sys, tempfile
body = {encoded_body}
args = {encoded_args}
conftest = {encoded_conftest}
with tempfile.TemporaryDirectory(prefix='xdist-contract-') as directory:
    root = pathlib.Path(directory)
    (root / 'test_sample.py').write_text(body, encoding='utf-8')
    if conftest is not None:
        (root / 'conftest.py').write_text(conftest, encoding='utf-8')
    env = os.environ.copy()
    env['PYTHONPATH'] = '/tmp/candidate-site:/opt/candidate-dependencies/site'
    env.pop('PYTEST_DISABLE_PLUGIN_AUTOLOAD', None)
    env.pop('PYTEST_ADDOPTS', None)
    completed = subprocess.run(
        [sys.executable, '-m', 'pytest', '-q', *args, 'test_sample.py'],
        cwd=root, env=env, capture_output=True, text=True, timeout=30,
    )
    result = [completed.returncode, completed.stdout[-6000:], completed.stderr[-2000:]]
"""


def successful_pytest(result: CandidateCallResult, needle: str | None = None) -> bool:
    if not result.ok or not isinstance(result.value, list) or len(result.value) != 3:
        return False
    code, stdout, stderr = result.value
    return code == 0 and (needle is None or needle in stdout or needle in stderr)


def main() -> None:
    leaves: list[dict[str, str]] = []

    def check(identifier: str, passed: bool, message: str = "") -> None:
        leaves.append(
            {
                "id": f"pytest-xdist::{identifier}",
                "status": "passed" if passed else "failed",
                "message": message[-2000:],
            }
        )

    metadata = metadata_requires("pytest-xdist")
    check(
        "packaging-surface",
        metadata.ok
        and metadata.value
        == [
            "execnet>=2.1",
            "pytest>=7.0.0",
            'filelock; extra == "testing"',
            'psutil>=3.0; extra == "psutil"',
            'setproctitle; extra == "setproctitle"',
        ]
        and scenario(
            "import xdist\nresult = [bool(xdist.__version__), sorted(xdist.__all__)]"
        ).value
        == [
            True,
            [
                "__version__",
                "get_xdist_worker_id",
                "is_xdist_controller",
                "is_xdist_master",
                "is_xdist_worker",
            ],
        ],
    )
    parsed = scenario(
        "from xdist.plugin import parse_numprocesses\nresult = [parse_numprocesses('3'), parse_numprocesses('auto'), parse_numprocesses('logical')]"
    )
    check("parse-numprocesses", parsed.ok and parsed.value == [3, "auto", "logical"])
    ramp = scenario(
        "from xdist.plugin import parse_ramp_duration\nresult = [parse_ramp_duration('10'), parse_ramp_duration('0.5s'), parse_ramp_duration('2m'), parse_ramp_duration('1h')]"
    )
    check("parse-ramp-valid", ramp.ok and ramp.value == [10.0, 0.5, 120.0, 3600.0])
    invalid = scenario(
        "from xdist.plugin import parse_ramp_duration\nresult = []\nfor value in ('', '-1', '1d', 'soon', 'nan'):\n try:\n  parse_ramp_duration(value)\n except Exception as exc:\n  result.append(type(exc).__module__ + '.' + type(exc).__qualname__)"
    )
    check(
        "parse-ramp-invalid",
        invalid.ok and invalid.value == ["pytest.UsageError"] * 5,
    )
    identity = scenario(
        "import os\nfrom xdist.plugin import is_xdist_controller, is_xdist_master, is_xdist_worker\nresult = []\nclass C: pass\nc = C(); c.config = C(); c.config.option = C(); c.config.option.dist = 'no'\nresult = [is_xdist_worker(c), is_xdist_controller(c), is_xdist_master(c)]"
    )
    check("identity-helper", identity.ok and identity.value == [False, False, False])
    local = scenario(
        pytest_script(
            """
def test_identity(worker_id, testrun_uid, request):
    import xdist
    assert worker_id == "master"
    assert testrun_uid
    assert not xdist.is_xdist_worker(request)
    assert not xdist.is_xdist_controller(request)
    assert not xdist.is_xdist_master(request)
    assert xdist.get_xdist_worker_id(request) == "master"
"""
        )
    )
    check("local-fixtures", successful_pytest(local, "1 passed"), str(local))
    distributed = scenario(
        pytest_script(
            """
import pytest
@pytest.mark.parametrize("value", range(4))
def test_worker_identity(value, worker_id, testrun_uid, request):
    import xdist
    assert worker_id.startswith("gw")
    assert testrun_uid == "fixed-run"
    assert xdist.is_xdist_worker(request)
    assert not xdist.is_xdist_controller(request)
    assert xdist.get_xdist_worker_id(request) == worker_id
""",
            ("-n2", "--testrunuid=fixed-run"),
        )
    )
    check("distributed-fixtures", successful_pytest(distributed, "4 passed"), str(distributed))
    simple = scenario(
        pytest_script(
            "def test_one():\n    assert 2 + 2 == 4\n",
            ("-n1",),
        )
    )
    check("distributed-pass", successful_pytest(simple, "1 passed"), str(simple))
    outcomes = scenario(
        pytest_script(
            """
import pytest
def test_ok():
    assert True
def test_skip():
    pytest.skip("expected")
""",
            ("-n2", "--dist=load"),
        )
    )
    check("distributed-outcomes", successful_pytest(outcomes, "1 passed, 1 skipped"), str(outcomes))
    modes = True
    mode_messages = []
    for mode in ("each", "load", "loadscope", "loadfile", "loadgroup", "worksteal"):
        marker = "\nimport pytest\npytestmark = pytest.mark.xdist_group('one')\n" if mode == "loadgroup" else ""
        result = scenario(
            pytest_script(
                marker + "\ndef test_a():\n    assert True\n\ndef test_b():\n    assert True\n",
                ("-n2", f"--dist={mode}"),
            )
        )
        ok = successful_pytest(result, "passed")
        modes = modes and ok
        if not ok:
            mode_messages.append(f"{mode}: {result}")
    check("distribution-modes", modes, "; ".join(mode_messages))
    hook = scenario(
        pytest_script(
            "def test_one():\n    pass\n",
            ("-n1", "--tx=popen"),
            conftest="""
def pytest_configure_node(node):
    node.workerinput["left"] = 40
    node.workerinput["right"] = 2
def pytest_configure(config):
    if hasattr(config, "workerinput"):
        config.workeroutput["total"] = config.workerinput["left"] + config.workerinput["right"]
def pytest_testnodedown(node, error):
    node.config.total = node.workeroutput["total"]
def pytest_terminal_summary(terminalreporter):
    if not hasattr(terminalreporter.config, "workerinput"):
        assert terminalreporter.config.total == 42
""",
        )
    )
    check("hook-data-exchange", successful_pytest(hook, "1 passed"), str(hook))
    collect_only = scenario(
        pytest_script(
            "def test_a():\n    pass\n\ndef test_b():\n    pass\n",
            ("-n1", "--collect-only"),
        )
    )
    check(
        "collect-only",
        successful_pytest(collect_only, "2 tests collected")
        and "created:" not in str(collect_only.value),
        str(collect_only),
    )
    pdb = scenario(
        pytest_script("def test_one():\n    pass\n", ("-n1", "--pdb"))
    )
    check(
        "pdb-incompatibility",
        pdb.ok
        and isinstance(pdb.value, list)
        and pdb.value[0] != 0
        and "incompatible" in (pdb.value[1] + pdb.value[2]),
        str(pdb),
    )
    scheduler = scenario(
        "from xdist.scheduler import EachScheduling, LoadScheduling, LoadScopeScheduling, LoadFileScheduling, LoadGroupScheduling, WorkStealingScheduling\nresult = [c.__name__ for c in (EachScheduling, LoadScheduling, LoadScopeScheduling, LoadFileScheduling, LoadGroupScheduling, WorkStealingScheduling)]"
    )
    check(
        "scheduler-exports",
        scheduler.ok
        and scheduler.value
        == [
            "EachScheduling",
            "LoadScheduling",
            "LoadScopeScheduling",
            "LoadFileScheduling",
            "LoadGroupScheduling",
            "WorkStealingScheduling",
        ],
    )
    print(json.dumps({"schema_version": "1.0", "leaves": leaves}, sort_keys=True))


if __name__ == "__main__":
    main()
