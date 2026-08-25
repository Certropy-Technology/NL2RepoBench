from __future__ import annotations

import datetime
import importlib.metadata
import json
import os
import sys
import time
from collections.abc import Callable
from typing import Any


CANDIDATE_SITE = os.environ.get(
    "NL2REPO_FREEZEGUN_CANDIDATE_SITE", "/tmp/candidate-site"
)
DEPENDENCY_SITE = os.environ.get(
    "NL2REPO_CANDIDATE_DEPENDENCIES", "/opt/candidate-dependencies/site"
)
for site in (DEPENDENCY_SITE, CANDIDATE_SITE):
    if site not in sys.path:
        sys.path.insert(0, site)

import freezegun
from freezegun import freeze_time


def iso(value: datetime.date | datetime.datetime) -> str:
    return value.isoformat()


def error_name(callable_: Callable[..., Any], *args: Any, **kwargs: Any) -> str | None:
    try:
        callable_(*args, **kwargs)
    except Exception as exc:
        return type(exc).__name__
    return None


def package_surface() -> dict[str, Any]:
    return {
        "distribution_version": importlib.metadata.version("freezegun"),
        "module_version": freezegun.__version__,
        "exports": sorted(freezegun.__all__),
        "freeze_time_callable": callable(freezegun.freeze_time),
    }


def string_context() -> dict[str, Any]:
    with freeze_time("2042-03-04 05:06:07.123456"):
        return {
            "now": iso(datetime.datetime.now()),
            "utcnow": iso(datetime.datetime.utcnow()),
            "today": iso(datetime.date.today()),
            "time": time.time(),
            "time_ns": time.time_ns(),
        }


def date_input() -> dict[str, str]:
    with freeze_time(datetime.date(2031, 7, 8)):
        return {
            "now": iso(datetime.datetime.now()),
            "today": iso(datetime.date.today()),
        }


def datetime_input() -> dict[str, str]:
    target = datetime.datetime(2031, 7, 8, 9, 10, 11, 120000)
    with freeze_time(target):
        return {
            "now": iso(datetime.datetime.now()),
            "utcnow": iso(datetime.datetime.utcnow()),
        }


def date_datetime_operations() -> dict[str, Any]:
    real_date = datetime.date
    real_datetime = datetime.datetime
    with freeze_time("2040-02-28 23:30:00"):
        today = datetime.date.today()
        now = datetime.datetime.now()
        return {
            "date_isinstance": isinstance(today, real_date),
            "datetime_isinstance": isinstance(now, real_datetime),
            "tomorrow": iso(today + datetime.timedelta(days=1)),
            "later": iso(now + datetime.timedelta(minutes=90)),
            "combined": iso(datetime.datetime.combine(today, datetime.time(4, 5, 6))),
        }


def time_functions() -> dict[str, Any]:
    with freeze_time("2001-02-03 04:05:06"):
        return {
            "gmtime": list(time.gmtime()),
            "localtime": list(time.localtime()),
            "strftime": time.strftime("%Y-%m-%d %H:%M:%S"),
        }


def epoch_time() -> dict[str, Any]:
    with freeze_time("1970-01-01 00:00:00.000001"):
        return {
            "time": time.time(),
            "time_ns": time.time_ns(),
            "utcnow": iso(datetime.datetime.utcnow()),
        }


def tz_offset_hours() -> dict[str, str]:
    with freeze_time("2042-03-04 05:06:07", tz_offset=-4):
        return {
            "now": iso(datetime.datetime.now()),
            "utcnow": iso(datetime.datetime.utcnow()),
            "today": iso(datetime.date.today()),
        }


def tz_offset_timedelta() -> dict[str, str]:
    offset = datetime.timedelta(hours=5, minutes=30)
    with freeze_time("2042-03-04 20:00:00", tz_offset=offset):
        return {
            "now": iso(datetime.datetime.now()),
            "utcnow": iso(datetime.datetime.utcnow()),
            "today": iso(datetime.date.today()),
        }


def aware_datetime() -> dict[str, str]:
    east_two = datetime.timezone(datetime.timedelta(hours=2), name="EAST2")
    west_seven = datetime.timezone(datetime.timedelta(hours=-7), name="WEST7")
    with freeze_time("2042-03-04 05:06:07"):
        return {
            "east": iso(datetime.datetime.now(east_two)),
            "west": iso(datetime.datetime.now(west_seven)),
        }


def tick_numeric() -> dict[str, Any]:
    with freeze_time("2030-01-02 03:04:05") as frozen:
        before = iso(datetime.datetime.now())
        returned = frozen.tick(2.5)
        return {
            "before": before,
            "returned": iso(returned),
            "after": iso(datetime.datetime.now()),
            "timestamp": time.time(),
        }


def tick_timedelta() -> dict[str, str]:
    with freeze_time("2030-01-02 03:04:05") as frozen:
        returned = frozen.tick(datetime.timedelta(days=2, seconds=3, microseconds=4))
        return {
            "returned": iso(returned),
            "after": iso(datetime.datetime.now()),
        }


def tick_date_boundary() -> dict[str, str]:
    with freeze_time("2030-12-31 23:59:59") as frozen:
        frozen.tick(2)
        return {
            "now": iso(datetime.datetime.now()),
            "today": iso(datetime.date.today()),
        }


def auto_tick() -> list[str]:
    with freeze_time("2030-01-02 03:04:05", auto_tick_seconds=15):
        return [iso(datetime.datetime.now()) for _ in range(3)]


def move_to_string() -> dict[str, str]:
    with freeze_time("2030-01-02 03:04:05") as frozen:
        frozen.move_to("2044-05-06 07:08:09.100000")
        return {
            "now": iso(datetime.datetime.now()),
            "today": iso(datetime.date.today()),
        }


def move_to_date() -> str:
    with freeze_time("2030-01-02") as frozen:
        frozen.move_to(datetime.date(2044, 5, 6))
        return iso(datetime.datetime.now())


def move_to_datetime() -> str:
    with freeze_time("2030-01-02") as frozen:
        frozen.move_to(datetime.datetime(2044, 5, 6, 7, 8, 9, 100000))
        return iso(datetime.datetime.now())


def nested_contexts() -> list[str]:
    with freeze_time("2030-01-02 03:04:05"):
        outer_before = iso(datetime.datetime.now())
        with freeze_time("2040-06-07 08:09:10"):
            inner = iso(datetime.datetime.now())
        outer_after = iso(datetime.datetime.now())
    return [outer_before, inner, outer_after]


def context_restoration() -> dict[str, Any]:
    original_datetime = datetime.datetime
    original_date = datetime.date
    original_time = time.time
    with freeze_time("2030-01-02 03:04:05"):
        inside = {
            "datetime_patched": datetime.datetime is not original_datetime,
            "date_patched": datetime.date is not original_date,
            "time_patched": time.time is not original_time,
            "now": iso(datetime.datetime.now()),
        }
    return {
        "inside": inside,
        "datetime_restored": datetime.datetime is original_datetime,
        "date_restored": datetime.date is original_date,
        "time_restored": time.time is original_time,
        "fixed_constructor": iso(datetime.datetime(2000, 1, 2, 3, 4, 5)),
    }


def explicit_start_stop() -> dict[str, Any]:
    original_datetime = datetime.datetime
    original_date = datetime.date
    original_time = time.time
    freezer = freeze_time("2030-01-02 03:04:05")
    factory = freezer.start()
    try:
        active = {
            "now": iso(datetime.datetime.now()),
            "factory": iso(factory()),
        }
    finally:
        freezer.stop()
    return {
        "active": active,
        "datetime_restored": datetime.datetime is original_datetime,
        "date_restored": datetime.date is original_date,
        "time_restored": time.time is original_time,
    }


def decorator_function() -> dict[str, Any]:
    def original(label: str) -> dict[str, str]:
        return {
            "label": label,
            "now": iso(datetime.datetime.now()),
            "today": iso(datetime.date.today()),
        }

    decorated = freeze_time("2035-04-05 06:07:08")(original)
    return {
        "result": decorated("kept"),
        "name": decorated.__name__,
        "wrapped": decorated.__wrapped__ is original,
    }


def decorator_as_arg() -> dict[str, Any]:
    @freeze_time("2035-04-05 06:07:08", as_arg=True)
    def decorated(frozen: Any, label: str) -> dict[str, str]:
        before = iso(datetime.datetime.now())
        frozen.tick(2)
        return {
            "label": label,
            "before": before,
            "after": iso(datetime.datetime.now()),
        }

    return decorated(label="kept")


def decorator_as_kwarg() -> dict[str, Any]:
    @freeze_time("2035-04-05 06:07:08", as_kwarg="clock")
    def decorated(label: str, clock: Any = None) -> dict[str, str]:
        before = iso(datetime.datetime.now())
        clock.move_to("2040-01-02 03:04:05")
        return {
            "label": label,
            "before": before,
            "after": iso(datetime.datetime.now()),
        }

    return decorated("kept")


def invalid_input() -> dict[str, str | None]:
    return {
        "integer": error_name(freeze_time, 42),
        "object": error_name(freeze_time, object()),
    }


OPERATION_NAMES = (
    "package_surface",
    "string_context",
    "date_input",
    "datetime_input",
    "date_datetime_operations",
    "time_functions",
    "epoch_time",
    "tz_offset_hours",
    "tz_offset_timedelta",
    "aware_datetime",
    "tick_numeric",
    "tick_timedelta",
    "tick_date_boundary",
    "auto_tick",
    "move_to_string",
    "move_to_date",
    "move_to_datetime",
    "nested_contexts",
    "context_restoration",
    "explicit_start_stop",
    "decorator_function",
    "decorator_as_arg",
    "decorator_as_kwarg",
    "invalid_input",
)
OPERATIONS: dict[str, Callable[[], Any]] = {
    name: globals()[name] for name in OPERATION_NAMES
}


def main() -> None:
    operation = sys.argv[1]
    try:
        if operation == "__all__":
            result = {name: OPERATIONS[name]() for name in OPERATION_NAMES}
        else:
            result = OPERATIONS[operation]()
        response = {"id": operation, "ok": True, "result": result}
    except Exception as exc:
        response = {
            "id": operation,
            "ok": False,
            "error": {"type": type(exc).__name__, "message": str(exc)},
        }
    print(json.dumps(response, ensure_ascii=True, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
