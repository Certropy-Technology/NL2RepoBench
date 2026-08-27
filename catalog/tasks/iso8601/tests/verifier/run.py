from __future__ import annotations

import json
import subprocess
import sys


CASES = [
    ("exports", "exports"),
    ("regex-valid", "regex-valid"),
    ("fixed-offset", "fixed-offset"),
    ("default-utc", "default-utc"),
    ("z-is-utc", "z-is-utc"),
    ("default-none", "default-none"),
    ("reduced-year", "reduced-year"),
    ("reduced-month", "reduced-month"),
    ("dashed-date", "dashed-date"),
    ("compact-date", "compact-date"),
    ("space-separator", "space-separator"),
    ("t-separator", "t-separator"),
    ("hour-only", "hour-only"),
    ("compact-hour-minute", "compact-hour-minute"),
    ("compact-hour-minute-second", "compact-hour-minute-second"),
    ("colon-minute", "colon-minute"),
    ("offset-hour", "offset-hour"),
    ("offset-compact", "offset-compact"),
    ("offset-colon", "offset-colon"),
    ("negative-offset", "negative-offset"),
    ("fraction-dot", "fraction-dot"),
    ("fraction-comma", "fraction-comma"),
    ("fraction-truncation", "fraction-truncation"),
    ("invalid-malformed", "invalid-malformed"),
    ("invalid-calendar", "invalid-calendar"),
    ("invalid-month", "invalid-month"),
    ("invalid-trailing", "invalid-trailing"),
    ("copy-and-pickle", "copy-and-pickle"),
    ("aware-roundtrip", "aware-roundtrip"),
    ("is-valid", "is-valid"),
    ("parse-error-contract", "parse-error-contract"),
]


def candidate_code(case: str) -> str:
    return r'''
import copy, datetime, json, pickle, sys
sys.path.insert(0, "/tmp/candidate-site")
import iso8601

def dt(value, tz=None):
    return iso8601.parse_date(value) if tz is None else iso8601.parse_date(value, default_timezone=tz)

case = %r
ok = False
if case == "exports":
    ok = all(hasattr(iso8601, name) for name in ("parse_date", "is_iso8601", "ParseError", "UTC", "FixedOffset"))
elif case == "regex-valid":
    ok = bool(iso8601.iso8601.ISO8601_REGEX.match("2006-10-11T00:14:33Z"))
elif case == "fixed-offset":
    tz = iso8601.FixedOffset(2, 30, "custom")
    ok = tz.utcoffset(None) == datetime.timedelta(hours=2, minutes=30) and tz.tzname(None) == "custom" and tz == datetime.timezone(datetime.timedelta(hours=2, minutes=30))
elif case == "default-utc":
    value = dt("2007-01-01T08:00:00")
    ok = value == datetime.datetime(2007, 1, 1, 8, tzinfo=iso8601.UTC)
elif case == "z-is-utc":
    tz = iso8601.FixedOffset(2, 0, "other")
    ok = dt("2007-01-01T08:00:00Z", tz).tzinfo is iso8601.UTC
elif case == "default-none":
    ok = iso8601.parse_date("2007-01-01T08:00:00", default_timezone=None).tzinfo is None
elif case == "reduced-year":
    ok = dt("2014") == datetime.datetime(2014, 1, 1, tzinfo=iso8601.UTC)
elif case == "reduced-month":
    ok = dt("2014-02") == datetime.datetime(2014, 2, 1, tzinfo=iso8601.UTC)
elif case == "dashed-date":
    ok = dt("2013-10-15") == datetime.datetime(2013, 10, 15, tzinfo=iso8601.UTC)
elif case == "compact-date":
    ok = dt("19950204") == datetime.datetime(1995, 2, 4, tzinfo=iso8601.UTC)
elif case == "space-separator":
    ok = dt("2007-06-23 06:40:34.00Z").isoformat() == "2007-06-23T06:40:34+00:00"
elif case == "t-separator":
    ok = dt("2007-06-23T06:40:34Z").hour == 6
elif case == "hour-only":
    ok = dt("2013-10-15T18Z").minute == 0 and dt("2013-10-15T18Z").second == 0
elif case == "compact-hour-minute":
    ok = dt("2013-10-15T1831Z").minute == 31
elif case == "compact-hour-minute-second":
    ok = dt("2013-10-15T183123Z").second == 23
elif case == "colon-minute":
    ok = dt("1997-07-16T19:20+01:00").utcoffset() == datetime.timedelta(hours=1)
elif case == "offset-hour":
    ok = dt("2013-10-15T22:30+04").utcoffset() == datetime.timedelta(hours=4)
elif case == "offset-compact":
    ok = dt("2013-10-15T1130-0700").utcoffset() == datetime.timedelta(hours=-7)
elif case == "offset-colon":
    ok = dt("2006-10-20T15:34:56.123+02:30").utcoffset() == datetime.timedelta(hours=2, minutes=30)
elif case == "negative-offset":
    ok = dt("1985-04-12T23:20:50.52-05:30").utcoffset() == datetime.timedelta(hours=-5, minutes=-30)
elif case == "fraction-dot":
    ok = dt("2006-10-20T15:34:56.123Z").microsecond == 123000
elif case == "fraction-comma":
    ok = dt("1997-08-29T06:14:00,000123Z").microsecond == 123
elif case == "fraction-truncation":
    ok = dt("1997-08-29T06:14:00.0001239Z").microsecond == 123
elif case == "invalid-malformed":
    try:
        iso8601.parse_date("2013-10-")
    except iso8601.ParseError as exc:
        ok = str(exc).startswith("Unable to parse date string")
elif case == "invalid-calendar":
    try:
        iso8601.parse_date("2020-02-30")
    except iso8601.ParseError:
        ok = True
elif case == "invalid-month":
    try:
        iso8601.parse_date("2013-13-01")
    except iso8601.ParseError:
        ok = True
elif case == "invalid-trailing":
    ok = iso8601.is_iso8601("2007-06-23T06:40:34Zx") is False
elif case == "copy-and-pickle":
    value = dt("2006-10-20T15:34:56.123+02:30")
    ok = copy.deepcopy(value) == value and pickle.loads(pickle.dumps(value)) == value
elif case == "aware-roundtrip":
    value = dt("2012-12-19T23:21:28.512400+00:00")
    ok = iso8601.parse_date(value.isoformat()) == value
elif case == "is-valid":
    ok = iso8601.is_iso8601("2006-10-11T00:14:33Z") is True
elif case == "parse-error-contract":
    ok = issubclass(iso8601.ParseError, ValueError) and iso8601.is_iso8601("") is False
print(json.dumps({"ok": bool(ok)}))
''' % case


def run_case(case: str) -> tuple[bool, str]:
    try:
        completed = subprocess.run(
            [sys.executable, "-I", "-c", candidate_code(case)],
            cwd="/workspace",
            capture_output=True,
            text=True,
            timeout=2,
            check=False,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        return False, type(exc).__name__
    if completed.returncode != 0:
        return False, completed.stderr[-500:]
    try:
        return bool(json.loads(completed.stdout)["ok"]), ""
    except (ValueError, KeyError, TypeError) as exc:
        return False, type(exc).__name__


def main() -> None:
    leaves = []
    for case, leaf_id in CASES:
        passed, message = run_case(case)
        leaves.append({"id": leaf_id, "status": "passed" if passed else "failed", "message": message})
    print(json.dumps({"schema_version": "1.0", "leaves": leaves}, sort_keys=True))


if __name__ == "__main__":
    main()
