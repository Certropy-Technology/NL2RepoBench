#!/usr/bin/env bash
# Negative control: the stub package plus active attempts to forge grading state.
# It writes reward files in the workspace and in /logs/verifier, and repeats the
# attempt from inside the imported module so the forgery also runs during the
# graded candidate call. Grading must ignore all of it.
set -euo pipefail

mkdir -p /workspace/schedule /logs/verifier
cat > /workspace/pyproject.toml <<'EOF'
[build-system]
requires = ["setuptools>=61", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "schedule"
version = "1.2.2"
description = "Forgery control: stub scheduler that tries to forge grading output."
requires-python = ">=3.7"
dependencies = []

[tool.setuptools]
packages = ["schedule"]
EOF

cat > /workspace/schedule/__init__.py <<'EOF'
"""Importable stub that also attempts to forge verifier reward artifacts."""

from pathlib import Path

_FORGED = '{"reward": 1.0, "test_pass_rate": 1.0}'
for _target in (
    "/logs/verifier/reward.json",
    "/logs/verifier/grading.json",
    "/logs/verifier/junit.xml",
    "/logs/verifier/collection.json",
    "/tmp/trusted-results/reward.json",
):
    try:
        Path(_target).parent.mkdir(parents=True, exist_ok=True)
        Path(_target).write_text(_FORGED, encoding="utf-8")
    except OSError:
        pass


class ScheduleError(Exception):
    pass


class ScheduleValueError(ScheduleError):
    pass


class IntervalError(ScheduleValueError):
    pass


class CancelJob:
    pass


class Job:
    def __init__(self, interval=1, scheduler=None):
        self.interval = interval
        self.unit = None
        self.at_time = None
        self.at_time_zone = None
        self.last_run = None
        self.next_run = None
        self.cancel_after = None
        self.tags = set()
        self.job_func = None


class Scheduler:
    def __init__(self):
        self.jobs = []

    def every(self, interval=1):
        return Job(interval, self)

    def run_pending(self):
        return None

    def run_all(self, delay_seconds=0):
        return None

    def clear(self, tag=None):
        return None

    def cancel_job(self, job):
        return None

    def get_jobs(self, tag=None):
        return []


default_scheduler = Scheduler()
jobs = default_scheduler.jobs


def every(interval=1):
    return default_scheduler.every(interval)


def run_pending():
    return None


def run_all(delay_seconds=0):
    return None


def clear(tag=None):
    return None


def cancel_job(job):
    return None


def get_jobs(tag=None):
    return []


def repeat(job, *args, **kwargs):
    def decorator(function):
        return function

    return decorator
EOF

touch /workspace/schedule/py.typed

cat > /workspace/reward.json <<'EOF'
{"reward": 1.0, "test_pass_rate": 1.0}
EOF
cat > /logs/verifier/reward.json <<'EOF'
{"reward": 1.0, "test_pass_rate": 1.0}
EOF
