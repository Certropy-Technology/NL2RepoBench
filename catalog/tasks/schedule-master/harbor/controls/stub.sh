#!/usr/bin/env bash
# Negative control: a packaging-complete but non-functional `schedule` package.
# It must install cleanly and import, so the low score is attributable to missing
# behaviour rather than to an installation or collection failure.
set -euo pipefail

mkdir -p /workspace/schedule
cat > /workspace/pyproject.toml <<'EOF'
[build-system]
requires = ["setuptools>=61", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "schedule"
version = "1.2.2"
description = "Stub control: importable but non-functional scheduler."
requires-python = ">=3.7"
dependencies = []

[tool.setuptools]
packages = ["schedule"]
EOF

cat > /workspace/schedule/__init__.py <<'EOF'
"""Importable stub: public names exist, no scheduling behaviour is implemented."""


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

    @property
    def next_run(self):
        return None

    @property
    def idle_seconds(self):
        return None


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


def next_run():
    return None


def idle_seconds():
    return None


def repeat(job, *args, **kwargs):
    def decorator(function):
        return function

    return decorator
EOF

touch /workspace/schedule/py.typed
