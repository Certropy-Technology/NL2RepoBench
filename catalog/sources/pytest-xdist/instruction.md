# Project Description

Create a complete, installable Python distribution named `pytest-xdist` from
an empty workspace. It must provide the `xdist` pytest plugin and work with
pytest 9 on CPython 3.12 in a network-isolated runtime. Use the standard
library plus the declared `execnet` dependency; the implementation does not
need native code.

## Natural Language Instruction

Create the installable `pytest-xdist` distribution from an empty workspace.
Implement the `xdist` pytest plugin, plugin entry points, worker identity
fixtures, option parsing, local `popen` execution, scheduler classes, and
hook specifications described below. Preserve pytest-compatible collection,
exit statuses, worker reports, deterministic scheduling, and the explicit
offline boundary. External SSH/socket transports and interactive-only behavior
are not required for the local contract.

## Task Scope

`pytest-xdist` extends pytest with distributed and subprocess test execution.
The main user interface is the installed `xdist` plugin: pytest discovers it
through the `pytest11` entry point, adds distribution options, starts workers,
balances tests, and exposes worker identity to tests and fixtures.

The implementation must be usable from an empty repository after installation.
It must not require a network connection, source checkout, environment-specific
absolute paths, or an SSH server during ordinary local execution.

## Supports

- Provide an installable project named `pytest-xdist`, supporting Python 3.9+
  and pytest 7+; the evaluator uses CPython 3.12 and pytest 9.
- Use a setuptools build backend with a reproducible version. Runtime metadata
  must declare `execnet>=2.1` and `pytest>=7.0.0`; the optional extras are
  `testing` (`filelock`), `psutil` (`psutil>=3.0`), and `setproctitle`
  (`setproctitle`).
- Register `xdist.plugin` as the `xdist` pytest11 entry point and register
  `xdist.looponfail` for the legacy loop-on-fail entry point.
- Export from `xdist`: `__version__`, `get_xdist_worker_id`,
  `is_xdist_controller`, `is_xdist_master`, and `is_xdist_worker`.
- Keep ordinary runs offline. `-n0` or no distribution option must run tests in
  the controller process; `-n1`, `-n2`, and `--tx=popen` must create the
  requested subprocess workers and return pytest's normal exit status.

## Project Directory Structure

```text
workspace/
├── pyproject.toml
├── src/
│   └── xdist/
│       ├── __init__.py
│       ├── plugin.py
│       ├── newhooks.py
│       ├── workermanage.py
│       └── scheduler/
│           ├── __init__.py
│           ├── each.py
│           ├── load.py
│           └── worksteal.py
└── README.rst
```

Register the plugin through the `pytest11` entry point in `pyproject.toml`.
The module tree must match the public import paths below. Optional extras may
remain optional; do not put evaluator or upstream test files in the generated
workspace.

## API Usage Guide

### `xdist.plugin.parse_numprocesses`

Import path: `xdist.plugin.parse_numprocesses`.

Signature: `parse_numprocesses(value: str) -> int | Literal["auto", "logical"]`.
Return an integer for a decimal worker count and preserve `"auto"` and
`"logical"`. Invalid integer text raises `ValueError`.

### `xdist.plugin.parse_ramp_duration`

Import path: `xdist.plugin.parse_ramp_duration`.

Signature: `parse_ramp_duration(value: str) -> float`.
Accept a non-negative finite number with an optional `s`, `m`, or `h` suffix;
the default unit is seconds. Whitespace around the value is ignored. Return
seconds as a float. Empty values, negative values, unknown units, non-numeric
text, and non-finite values raise `pytest.UsageError`.

### Worker identity helpers

Import paths: `xdist.is_xdist_worker`, `xdist.is_xdist_controller`,
`xdist.is_xdist_master`, and `xdist.get_xdist_worker_id`.

Signatures: `is_xdist_worker(request_or_session) -> bool`,
`is_xdist_controller(request_or_session) -> bool`,
`is_xdist_master(request_or_session) -> bool`, and
`get_xdist_worker_id(request_or_session) -> str`.
The argument is pytest's `request` fixture or `session` object. In a worker,
the helpers inspect `request_or_session.config.workerinput`: worker is true,
controller is false, and the worker id is a name such as `gw0`. In a
controller, worker is false, controller is true only when distribution is
active, master is the compatibility alias, and the id is `"master"`. Do not
infer identity from the machine hostname.

### `worker_id` and `testrun_uid` fixtures

The plugin provides `worker_id` and `testrun_uid` pytest fixtures. A local run
returns `worker_id == "master"`; a distributed run returns a stable worker name
such as `gw0` in each worker. `--testrunuid VALUE` makes every worker return
that exact value. Without it, one non-empty identifier is generated for the
run and exposed as `PYTEST_XDIST_TESTRUNUID`.

### Pytest options and distribution

The plugin adds `-n/--numprocesses`, `--maxprocesses`, `--max-worker-restart`,
`--ramp`, `--dist`, `--tx`, `--px`, `-d`, `--rsyncdir`, `--rsyncignore`,
`--testrunuid`, and `--maxschedchunk`. `--dist` accepts `each`, `load`,
`loadscope`, `loadfile`, `loadgroup`, `worksteal`, and `no`. `-n N` is the
short form for `--dist=load --tx=N*popen`; `-d` is the short form for load
distribution. `-n0` disables distribution even if another distribution option
was supplied.

The scheduler must collect the same node ids on every worker, distribute each
test exactly according to the selected mode, report failures/skips/import
errors with pytest-compatible statuses, and finish cleanly when a worker
exits. `--collect-only` must collect without starting a distributed session.
`--pdb` is incompatible with distributed execution and must be reported as a
pytest usage error rather than silently running workers.

### `xdist.newhooks`

Import path: `xdist.newhooks`. Declare the hook specifications
`pytest_xdist_setupnodes`, `pytest_xdist_newgateway`, `pytest_xdist_rsyncstart`,
`pytest_xdist_rsyncfinish`, `pytest_xdist_getremotemodule`,
`pytest_configure_node`, `pytest_testnodeready`, `pytest_testnodedown`,
`pytest_xdist_node_collection_finished`, `pytest_xdist_make_scheduler`,
`pytest_xdist_auto_num_workers`, and `pytest_handlecrashitem` so other pytest
plugins can implement them. Preserve their documented positional arguments
and optional return values.

### `xdist.workermanage` and schedulers

The public support modules must expose the worker-management and scheduler
classes used by the plugin, including `NodeManager`, `HostRSync`,
`WorkerController`, `EachScheduling`, `LoadScheduling`,
`LoadScopeScheduling`, `LoadFileScheduling`, `LoadGroupScheduling`, and
`WorkStealingScheduling`. Their methods must maintain pending/completed test
state, avoid duplicate scheduling, and tolerate worker removal. Local `popen`
workers are required; SSH and socket transports may be represented as clear
usage errors when no configured transport is available.

## Implementation Notes

Use a subprocess boundary for workers: the controller communicates through
execnet and workers execute pytest in their own interpreter. Preserve pytest's
plugin hook ordering and attach `node`, `worker_id`, and `testrun_uid` to
reports generated by workers. The `workerinput` mapping should include the
worker id, worker count, test-run uid, and controller argv where applicable.

Do not hard-code the host CPU count or make test ordering depend on wall-clock
time. Keep collection deterministic and preserve pytest exit codes. A normal
single-process run must not import optional `psutil`, `filelock`, or
`setproctitle` unless the corresponding feature is used.

## Examples

```python
from xdist.plugin import parse_numprocesses
parse_numprocesses("2")  # 2
parse_numprocesses("auto")  # "auto"
```

```bash
pytest -n0 tests
pytest -n1 --dist=load tests
```

```python
def test_identity(worker_id, testrun_uid):
    assert worker_id
    assert testrun_uid
```

## Error Handling and Boundary Conditions

- Invalid process counts, ramp durations, and incompatible `--pdb` usage must
  raise pytest usage errors rather than silently changing modes.
- `-n0` runs in the controller process; distributed modes must not duplicate a
  test node id and must tolerate a worker exiting during a run.
- Collection-only mode must not start workers. Local no-network execution must
  not attempt SSH, socket, DNS, registry, or external service access.
- Worker identity comes from pytest configuration, not machine hostname or a
  mutable global counter.
