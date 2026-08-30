#!/usr/bin/env python3
# ruff: noqa: E501, UP035
"""Private tzlocal contract verifier.

Candidate imports happen only in canonical UID-isolated child processes. This
trusted entrypoint compares their JSON-safe observations with frozen behavior.
"""

from __future__ import annotations

import json
import subprocess
import sys
from typing import Any, Callable

RUNNER = [
    sys.executable,
    "-I",
    "-B",
    "-m",
    "nl2repobench.verification.candidate_runner",
    "--candidate-site",
    "/tmp/candidate-site",
    "script",
]
PREFIX = "NL2REPO_CANDIDATE_RESULT="


def run_child(source: str) -> tuple[bool, Any]:
    try:
        completed = subprocess.run(
            RUNNER,
            input=json.dumps({"source": source}),
            capture_output=True,
            text=True,
            cwd="/workspace",
            timeout=8,
            check=False,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        return False, f"child execution failed: {exc}"
    lines = [line for line in completed.stdout.splitlines() if line.startswith(PREFIX)]
    if not lines:
        return False, f"child returned {completed.returncode}: {completed.stderr[-500:]}"
    try:
        payload = json.loads(lines[-1][len(PREFIX) :])
    except json.JSONDecodeError as exc:
        return False, f"invalid child payload: {exc}"
    if not payload.get("ok"):
        exception = payload.get("exception_type", "candidate exception")
        message = payload.get("exception_message", "candidate scenario failed")
        return False, f"{exception}: {message}"
    return True, payload.get("value")


def expect(source: str, predicate: Callable[[Any], bool]) -> tuple[bool, str]:
    ok, value = run_child(source)
    if not ok:
        return False, str(value)
    try:
        passed = predicate(value)
    except Exception as exc:
        return False, f"predicate failed: {exc}"
    return passed, "unexpected result: " + repr(value)


def equals(expected: Any) -> Callable[[Any], bool]:
    return lambda value: value == expected


def is_true(value: Any) -> bool:
    return value is True


TZ_SETUP = "import os, time\nos.environ['TZ'] = {zone!r}\ntime.tzset()\n"

CASES: list[tuple[str, str, Callable[[Any], bool]]] = [
    (
        "exports",
        "import tzlocal\nresult = tzlocal.__all__",
        equals(["get_localzone", "get_localzone_name", "reload_localzone", "assert_tz_offset"]),
    ),
    (
        "from-imports",
        "from tzlocal import get_localzone, get_localzone_name, reload_localzone, assert_tz_offset\nresult = all(callable(x) for x in (get_localzone, get_localzone_name, reload_localzone, assert_tz_offset))",
        is_true,
    ),
    (
        "metadata-name-version",
        "import importlib.metadata as m\nd = m.distribution('tzlocal')\nresult = (d.metadata['Name'], d.version)",
        equals(["tzlocal", "5.4.5.dev0"]),
    ),
    (
        "metadata-runtime-requires",
        "import importlib.metadata as m\nresult = [r for r in (m.requires('tzlocal') or []) if 'extra ==' not in r]",
        lambda value: value in (["tzdata; platform_system == \"Windows\""], ["tzdata; platform_system == 'Windows'"]),
    ),
    (
        "marker-and-unix-modules",
        "import importlib.resources\nimport tzlocal.unix, tzlocal.utils\nresult = importlib.resources.files('tzlocal').joinpath('py.typed').is_file()",
        is_true,
    ),
    (
        "windows-mapping-module",
        "import tzlocal.windows_tz as w\nresult = ('Belarus Standard Time' in w.win_tz and w.win_tz['Belarus Standard Time'] == 'Europe/Minsk' and 'Europe/Minsk' in w.tz_win)",
        is_true,
    ),
    (
        "public-signatures",
        "import inspect, tzlocal\nresult = [str(inspect.signature(getattr(tzlocal, n))) for n in tzlocal.__all__]",
        equals(["() -> zoneinfo.ZoneInfo", "() -> str", "() -> zoneinfo.ZoneInfo", "(tz, error=True)"]),
    ),
    (
        "env-name-harare",
        TZ_SETUP.format(zone="Africa/Harare") + "import tzlocal\nresult = tzlocal.get_localzone_name()",
        equals("Africa/Harare"),
    ),
    (
        "env-zone-harare",
        TZ_SETUP.format(zone="Africa/Harare") + "import tzlocal\nresult = str(tzlocal.get_localzone())",
        equals("Africa/Harare"),
    ),
    (
        "env-name-berlin",
        TZ_SETUP.format(zone="Europe/Berlin") + "import tzlocal\nresult = tzlocal.get_localzone_name()",
        equals("Europe/Berlin"),
    ),
    (
        "colon-env-name",
        TZ_SETUP.format(zone=":America/New_York") + "import tzlocal\nresult = tzlocal.get_localzone_name()",
        equals("America/New_York"),
    ),
    (
        "colon-env-zone",
        TZ_SETUP.format(zone=":America/New_York") + "import tzlocal\nresult = str(tzlocal.get_localzone())",
        equals("America/New_York"),
    ),
    (
        "absolute-zonefile-name",
        TZ_SETUP.format(zone="/usr/share/zoneinfo/Africa/Harare") + "import tzlocal\nresult = tzlocal.get_localzone_name()",
        equals("Africa/Harare"),
    ),
    (
        "absolute-zonefile-zone",
        TZ_SETUP.format(zone="/usr/share/zoneinfo/Africa/Harare") + "import tzlocal\nresult = str(tzlocal.get_localzone())",
        equals("Africa/Harare"),
    ),
    (
        "invalid-posix-zone-error",
        TZ_SETUP.format(zone="GMT+03:00") + "import zoneinfo, tzlocal\ntry:\n tzlocal.get_localzone()\nexcept zoneinfo.ZoneInfoNotFoundError as e:\n result = ('does not support non-zoneinfo timezones' in str(e))\nelse:\n result = False",
        is_true,
    ),
    (
        "unknown-zone-error",
        TZ_SETUP.format(zone="Not/A-Real-Zone") + "import zoneinfo, tzlocal\ntry:\n tzlocal.get_localzone()\nexcept zoneinfo.ZoneInfoNotFoundError:\n result = True\nelse:\n result = False",
        is_true,
    ),
    (
        "zone-cache",
        TZ_SETUP.format(zone="Africa/Harare") + "import tzlocal\nfirst = tzlocal.get_localzone()\nos.environ['TZ'] = 'Europe/Berlin'\ntime.tzset()\nsecond = tzlocal.get_localzone()\nresult = (str(first), str(second), first is second)",
        equals(["Africa/Harare", "Africa/Harare", True]),
    ),
    (
        "name-cache",
        TZ_SETUP.format(zone="Africa/Harare") + "import tzlocal\nfirst = tzlocal.get_localzone_name()\nos.environ['TZ'] = 'Europe/Berlin'\ntime.tzset()\nsecond = tzlocal.get_localzone_name()\nresult = (first, second)",
        equals(["Africa/Harare", "Africa/Harare"]),
    ),
    (
        "independent-caches",
        TZ_SETUP.format(zone="Africa/Harare") + "import tzlocal\nname = tzlocal.get_localzone_name()\nos.environ['TZ'] = 'Europe/Berlin'\ntime.tzset()\nzone = tzlocal.get_localzone()\nresult = (name, str(zone))",
        equals(["Africa/Harare", "Europe/Berlin"]),
    ),
    (
        "reload-zone",
        TZ_SETUP.format(zone="Africa/Harare") + "import tzlocal\ntzlocal.get_localzone()\nos.environ['TZ'] = 'Europe/Berlin'\ntime.tzset()\nresult = str(tzlocal.reload_localzone())",
        equals("Europe/Berlin"),
    ),
    (
        "reload-name",
        TZ_SETUP.format(zone="Africa/Harare") + "import tzlocal\ntzlocal.get_localzone_name()\nos.environ['TZ'] = 'Europe/Berlin'\ntime.tzset()\ntzlocal.reload_localzone()\nresult = tzlocal.get_localzone_name()",
        equals("Europe/Berlin"),
    ),
    (
        "reload-synchronizes",
        TZ_SETUP.format(zone="Africa/Harare") + "import tzlocal\ntzlocal.get_localzone_name()\nos.environ['TZ'] = 'America/New_York'\ntime.tzset()\nzone = tzlocal.reload_localzone()\nresult = (str(zone), tzlocal.get_localzone_name(), str(tzlocal.get_localzone()))",
        equals(["America/New_York", "America/New_York", "America/New_York"]),
    ),
    (
        "repeated-reload",
        TZ_SETUP.format(zone="Etc/UTC") + "import tzlocal\nresult = (str(tzlocal.reload_localzone()), str(tzlocal.reload_localzone()))",
        equals(["Etc/UTC", "Etc/UTC"]),
    ),
    (
        "zoneinfo-type",
        TZ_SETUP.format(zone="Africa/Harare") + "import zoneinfo, tzlocal\nresult = type(tzlocal.get_localzone()) is zoneinfo.ZoneInfo",
        is_true,
    ),
    (
        "harare-fixed-offset",
        TZ_SETUP.format(zone="Africa/Harare") + "from datetime import datetime\nimport tzlocal\nresult = datetime(2012, 1, 1, 5, tzinfo=tzlocal.get_localzone()).utcoffset().total_seconds()",
        equals(7200.0),
    ),
    (
        "new-york-fixed-offset",
        TZ_SETUP.format(zone="America/New_York") + "from datetime import datetime\nimport tzlocal\nresult = datetime(2021, 10, 1, 12, tzinfo=tzlocal.get_localzone()).utcoffset().total_seconds()",
        equals(-14400.0),
    ),
    (
        "assert-offset-match",
        TZ_SETUP.format(zone="Etc/UTC") + "from zoneinfo import ZoneInfo\nimport tzlocal\nresult = tzlocal.assert_tz_offset(ZoneInfo('Etc/UTC')) is None",
        is_true,
    ),
    (
        "assert-offset-error",
        TZ_SETUP.format(zone="Etc/UTC") + "from zoneinfo import ZoneInfo\nimport tzlocal\ntry:\n tzlocal.assert_tz_offset(ZoneInfo('Pacific/Chatham'))\nexcept ValueError as e:\n result = ('Timezone offset does not match system offset:' in str(e) and '!=' in str(e))\nelse:\n result = False",
        is_true,
    ),
    (
        "assert-offset-warning",
        TZ_SETUP.format(zone="Etc/UTC") + "import warnings\nfrom zoneinfo import ZoneInfo\nimport tzlocal\nwith warnings.catch_warnings(record=True) as seen:\n warnings.simplefilter('always')\n value = tzlocal.assert_tz_offset(ZoneInfo('Pacific/Chatham'), error=False)\nresult = (value is None, len(seen), issubclass(seen[0].category, UserWarning), 'Timezone offset does not match system offset:' in str(seen[0].message))",
        equals([True, 1, True, True]),
    ),
    (
        "lookup-preserves-tz-env",
        TZ_SETUP.format(zone="Africa/Harare") + "import tzlocal\ntzlocal.get_localzone_name(); tzlocal.get_localzone()\nresult = os.environ['TZ']",
        equals("Africa/Harare"),
    ),
]


def main() -> None:
    leaves: list[dict[str, str]] = []
    for leaf_id, source, predicate in CASES:
        passed, message = expect(source, predicate)
        leaf: dict[str, str] = {"id": leaf_id, "status": "passed" if passed else "failed"}
        if not passed:
            leaf["message"] = message
        leaves.append(leaf)
    print(json.dumps({"schema_version": "1.0", "leaves": leaves}, sort_keys=True))


if __name__ == "__main__":
    main()
