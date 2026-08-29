from __future__ import annotations

import json

from nl2repobench.verification.candidate_client import execute_script


CASES = [
    (
        "package.version",
        "import isodate\nresult = isodate.__version__ == '0.7.3.dev3+g17cb25eb7'",
    ),
    (
        "date.complete",
        "from datetime import date\nfrom isodate import parse_date\nresult = parse_date('2012-05-29') == date(2012, 5, 29)",
    ),
    (
        "date.reduced",
        "from datetime import date\nfrom isodate import parse_date\nresult = parse_date('2012-05', defaultday=17) == date(2012, 5, 17)",
    ),
    (
        "date.week",
        "from datetime import date\nfrom isodate import parse_date\nresult = parse_date('2012-W01-1') == date(2012, 1, 2)",
    ),
    (
        "date.ordinal",
        "from datetime import date\nfrom isodate import parse_date\nresult = parse_date('2012-060') == date(2012, 2, 29)",
    ),
    (
        "date.invalid",
        "from isodate import ISO8601Error, parse_date\ntry:\n    parse_date('2012-02-30')\nexcept (ISO8601Error, ValueError):\n    result = True\nelse:\n    result = False",
    ),
    (
        "time.extended",
        "from datetime import time\nfrom isodate import parse_time\nresult = parse_time('12:30:45') == time(12, 30, 45)",
    ),
    (
        "time.basic",
        "from datetime import time\nfrom isodate import parse_time\nresult = parse_time('123045') == time(12, 30, 45)",
    ),
    (
        "time.fraction",
        "from datetime import time\nfrom isodate import parse_time\nresult = parse_time('12:30:45.1234569') == time(12, 30, 45, 123456)",
    ),
    (
        "time.comma",
        "from datetime import time\nfrom isodate import parse_time\nresult = parse_time('12:30:45,5') == time(12, 30, 45, 500000)",
    ),
    (
        "time.offset",
        "from datetime import timedelta\nfrom isodate import parse_time\nt = parse_time('12:30:00+0230')\nresult = t.utcoffset() == timedelta(hours=2, minutes=30)",
    ),
    (
        "time.reduced",
        "from datetime import time\nfrom isodate import parse_time\nresult = parse_time('12:30') == time(12, 30)",
    ),
    (
        "time.invalid",
        "from isodate import ISO8601Error, parse_time\ntry:\n    parse_time('12:60:00')\nexcept (ISO8601Error, ValueError):\n    result = True\nelse:\n    result = False",
    ),
    (
        "datetime.aware",
        "from datetime import datetime, timezone\nfrom isodate import parse_datetime\nd = parse_datetime('2012-05-29T12:30:45Z')\nresult = d == datetime(2012, 5, 29, 12, 30, 45, tzinfo=timezone.utc)",
    ),
    (
        "datetime.reduced",
        "from datetime import datetime\nfrom isodate import parse_datetime\nresult = parse_datetime('2012-05-29T12:30') == datetime(2012, 5, 29, 12, 30)",
    ),
    (
        "datetime.invalid",
        "from isodate import ISO8601Error, parse_datetime\ntry:\n    parse_datetime('2012-05-29 12:30')\nexcept ISO8601Error:\n    result = True\nelse:\n    result = False",
    ),
    (
        "duration.timedelta",
        "from datetime import timedelta\nfrom isodate import parse_duration\nresult = parse_duration('P2W') == timedelta(days=14)",
    ),
    (
        "duration.calendar",
        "from isodate import Duration, parse_duration\nd = parse_duration('P1Y2M3DT4H5M6S')\nresult = isinstance(d, Duration) and d.years == 1 and d.months == 2 and d.tdelta.days == 3 and d.tdelta.seconds == 14706",
    ),
    (
        "duration.negative",
        "from datetime import timedelta\nfrom isodate import parse_duration\nresult = parse_duration('-PT1H30M') == -timedelta(hours=1, minutes=30)",
    ),
    (
        "duration.arithmetic",
        "from datetime import timedelta\nfrom isodate import parse_duration\na = parse_duration('P1D') + parse_duration('P2D')\nresult = isinstance(a, timedelta) and a == timedelta(days=3)",
    ),
    (
        "duration.totimedelta",
        "from datetime import date, timedelta\nfrom isodate import parse_duration\nresult = parse_duration('P1M').totimedelta(date(2020, 1, 31)) == timedelta(days=29)",
    ),
    (
        "duration.date-add",
        "from datetime import date\nfrom isodate import parse_duration\nresult = parse_duration('P1M') + date(2020, 1, 31) == date(2020, 2, 29)",
    ),
    (
        "duration.multiply",
        "from datetime import timedelta\nfrom isodate import parse_duration\nd = parse_duration('P2D') * 3\nresult = isinstance(d, timedelta) and d == timedelta(days=6)",
    ),
    (
        "format.date",
        "from datetime import date\nfrom isodate import date_isoformat\nresult = date_isoformat(date(2012, 5, 29)) == '2012-05-29'",
    ),
    (
        "format.time",
        "from datetime import time\nfrom isodate import time_isoformat\nresult = time_isoformat(time(12, 30, 45)) == '12:30:45'",
    ),
    (
        "format.datetime",
        "from datetime import datetime\nfrom isodate import UTC, datetime_isoformat\nresult = datetime_isoformat(datetime(2012, 5, 29, 12, 30, 45, tzinfo=UTC)) == '2012-05-29T12:30:45Z'",
    ),
    (
        "format.duration",
        "from datetime import timedelta\nfrom isodate import duration_isoformat\nresult = duration_isoformat(timedelta(days=2, seconds=3)) == 'P2DT3S'",
    ),
    (
        "format.tz",
        "from datetime import datetime, timedelta, timezone\nfrom isodate import tz_isoformat\nresult = tz_isoformat(datetime(2020, 1, 1, tzinfo=timezone(timedelta(hours=-5)))) == '-05:00'",
    ),
    (
        "format.strftime",
        "from datetime import date\nfrom isodate import strftime\nresult = strftime(date(1899, 12, 31), '%Y-%m-%d') == '1899-12-31'",
    ),
    (
        "tz.utc",
        "from datetime import timedelta\nfrom isodate import UTC, parse_tzinfo\nresult = parse_tzinfo('Z') is UTC and UTC.utcoffset(None) == timedelta(0)",
    ),
    (
        "tz.fixed",
        "from datetime import timedelta\nfrom isodate import FixedOffset\nt = FixedOffset(2, 30, '+02:30')\nresult = t.utcoffset(None) == timedelta(hours=2, minutes=30) and t.tzname(None) == '+02:30'",
    ),
    (
        "tz.parse",
        "from datetime import timedelta\nfrom isodate import parse_tzinfo\nt = parse_tzinfo('-05:30')\nresult = t.utcoffset(None) == -timedelta(hours=5, minutes=30)",
    ),
    (
        "tz.protocol",
        "from isodate import parse_datetime, tz_isoformat\nd = parse_datetime('2020-01-01T00:00:00+01:00')\nresult = tz_isoformat(d) == '+01:00' and d.tzinfo.tzname(d) == '+01:00'",
    ),
    (
        "pickle.duration",
        "import copy\nimport pickle\nfrom isodate import parse_duration\nd = parse_duration('P1Y2M3D')\nresult = pickle.loads(pickle.dumps(d)) == d and copy.deepcopy(d) == d",
    ),
]


def main() -> None:
    leaves = []
    for identifier, source in CASES:
        observed = execute_script(source, timeout_sec=8.0)
        passed = observed.ok and observed.value is True
        leaves.append(
            {
                "id": identifier,
                "status": "passed" if passed else "failed",
                "message": observed.exception_message or "scenario assertion failed",
            }
        )
    print(json.dumps({"schema_version": "1.0", "leaves": leaves}, sort_keys=True))


if __name__ == "__main__":
    main()
