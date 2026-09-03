from __future__ import annotations

import json
import textwrap
from typing import Any

from nl2repobench.verification.candidate_client import execute_script


SCENARIOS: tuple[tuple[str, str, Any], ...] = (
    (
        "metadata-version",
        "import importlib.metadata as m; result = m.version('pendulum')",
        "3.2.0",
    ),
    (
        "root-types",
        "import pendulum; result = [x.__name__ for x in (pendulum.Date, pendulum.Time, pendulum.DateTime, pendulum.Duration, pendulum.Interval)]",
        ["Date", "Time", "DateTime", "Duration", "Interval"],
    ),
    (
        "weekday-constants",
        "import pendulum; result = [int(x) for x in (pendulum.MONDAY, pendulum.TUESDAY, pendulum.WEDNESDAY, pendulum.THURSDAY, pendulum.FRIDAY, pendulum.SATURDAY, pendulum.SUNDAY)]",
        [0, 1, 2, 3, 4, 5, 6],
    ),
    (
        "datetime-default-utc",
        "import pendulum; d=pendulum.datetime(2024,2,29,12,30,4,5000); result=[d.to_iso8601_string(),d.timezone_name,d.is_utc()]",
        ["2024-02-29T12:30:04.005000Z", "UTC", True],
    ),
    (
        "datetime-naive",
        "import pendulum; d=pendulum.naive(2024,1,2,3,4,5,6); result=[d.to_datetime_string(),d.timezone_name,d.tzinfo is None]",
        ["2024-01-02 03:04:05", None, True],
    ),
    (
        "datetime-properties",
        "import pendulum; d=pendulum.datetime(1970,1,1,1,30,tz='Europe/Paris'); result=[d.int_timestamp,d.offset,d.offset_hours,d.is_dst()]",
        [1800, 3600, 1.0, False],
    ),
    (
        "timezone-conversion",
        "import pendulum; d=pendulum.datetime(2024,7,1,12,tz='Europe/Paris').in_timezone('UTC'); result=[d.to_iso8601_string(),d.timezone_name]",
        ["2024-07-01T10:00:00Z", "UTC"],
    ),
    (
        "dst-skipped-normalization",
        "import pendulum; d=pendulum.datetime(2013,3,31,2,30,tz='Europe/Paris'); result=d.to_iso8601_string()",
        "2013-03-31T03:30:00+02:00",
    ),
    (
        "dst-repeated-folds",
        "import pendulum; result=[pendulum.datetime(2013,10,27,2,30,tz='Europe/Paris',fold=f).offset for f in (0,1)]",
        [7200, 3600],
    ),
    (
        "dst-nonexistent-error",
        "import pendulum\ntry:\n pendulum.datetime(2013,3,31,2,30,tz='Europe/Paris',raise_on_unknown_times=True)\nexcept Exception as e:\n result=type(e).__module__+'.'+type(e).__name__",
        "pendulum.tz.exceptions.NonExistingTime",
    ),
    (
        "dst-ambiguous-error",
        "import pendulum\ntry:\n pendulum.datetime(2013,10,27,2,30,tz='Europe/Paris',raise_on_unknown_times=True)\nexcept Exception as e:\n result=type(e).__module__+'.'+type(e).__name__",
        "pendulum.tz.exceptions.AmbiguousTime",
    ),
    (
        "date-month-clamp",
        "import pendulum; d=pendulum.date(2024,1,31).add(months=1); result=d.to_date_string()",
        "2024-02-29",
    ),
    (
        "date-subtract",
        "import pendulum; d=pendulum.date(2024,3,1).subtract(days=2); result=d.to_date_string()",
        "2024-02-28",
    ),
    (
        "date-start-end-year",
        "import pendulum; d=pendulum.date(2024,5,6); result=[d.start_of('year').to_date_string(),d.end_of('year').to_date_string()]",
        ["2024-01-01", "2024-12-31"],
    ),
    (
        "datetime-start-end-day",
        "import pendulum; d=pendulum.datetime(2024,5,6,12,34,56,789); result=[d.start_of('day').to_iso8601_string(),d.end_of('day').to_iso8601_string()]",
        ["2024-05-06T00:00:00Z", "2024-05-06T23:59:59.999999Z"],
    ),
    (
        "datetime-next-monday",
        "import pendulum; d=pendulum.datetime(2024,5,8,14,30); result=d.next(pendulum.MONDAY,keep_time=True).to_iso8601_string()",
        "2024-05-13T14:30:00Z",
    ),
    (
        "datetime-previous-day",
        "import pendulum; d=pendulum.datetime(2024,5,8,14,30); result=d.previous(keep_time=False).to_iso8601_string()",
        "2024-05-01T00:00:00Z",
    ),
    (
        "time-add-wrap",
        "import pendulum; t=pendulum.time(23,30).add(hours=2); result=str(t)",
        "01:30:00",
    ),
    (
        "time-diff",
        "import pendulum; result=pendulum.time(10,15).diff(pendulum.time(8,0),abs=False).in_minutes()",
        -135,
    ),
    (
        "duration-components",
        "import pendulum; d=pendulum.duration(years=1,months=2,weeks=1,days=3,hours=4,minutes=5,seconds=6,microseconds=7); result=[d.years,d.months,d.weeks,d.remaining_days,d.hours,d.minutes,d.remaining_seconds,d.microseconds]",
        [1, 2, 1, 3, 4, 5, 6, 7],
    ),
    (
        "duration-totals",
        "import pendulum; d=pendulum.duration(days=2,hours=12,minutes=30); result=[d.total_hours(),d.total_minutes(),d.in_seconds()]",
        [60.5, 3630.0, 217800],
    ),
    (
        "duration-arithmetic",
        "import pendulum; d=(pendulum.duration(days=3)+pendulum.duration(hours=12))*2; result=[d.in_hours(),str(d)]",
        [168, "1 week"],
    ),
    (
        "interval-properties",
        "import pendulum; a=pendulum.datetime(2024,1,1); b=pendulum.datetime(2024,1,10,12); i=pendulum.interval(a,b); result=[i.start.to_date_string(),i.end.to_datetime_string(),i.in_days(),i.hours]",
        ["2024-01-01", "2024-01-10 12:00:00", 9, 12],
    ),
    (
        "interval-containment",
        "import pendulum; i=pendulum.interval(pendulum.datetime(2024,1,1),pendulum.datetime(2024,1,3)); result=[pendulum.datetime(2024,1,d) in i for d in (1,2,3,4)]",
        [True, True, True, False],
    ),
    (
        "interval-range",
        "import pendulum; i=pendulum.interval(pendulum.datetime(2024,1,1),pendulum.datetime(2024,1,7)); result=[x.to_date_string() for x in i.range('days',2)]",
        ["2024-01-01", "2024-01-03", "2024-01-05", "2024-01-07"],
    ),
    (
        "parse-datetime",
        "import pendulum; d=pendulum.parse('2024-02-29T23:45:01.250+02:30'); result=[type(d).__name__,d.to_iso8601_string()]",
        ["DateTime", "2024-02-29T23:45:01.250000+02:30"],
    ),
    (
        "parse-exact-date",
        "import pendulum; d=pendulum.parse('2024-02-29',exact=True); result=[type(d).__name__,d.to_date_string()]",
        ["Date", "2024-02-29"],
    ),
    (
        "parse-exact-time",
        "import pendulum; d=pendulum.parse('23:45:01.25',exact=True); result=[type(d).__name__,str(d).split('.')[0]]",
        ["Time", "23:45:01"],
    ),
    (
        "parse-duration",
        "import pendulum; d=pendulum.parse('P1Y2M3DT4H5M6S'); result=[type(d).__name__,d.years,d.months,d.remaining_days,d.hours,d.minutes,d.remaining_seconds]",
        ["Duration", 1, 2, 3, 4, 5, 6],
    ),
    (
        "parse-interval",
        "import pendulum; i=pendulum.parse('2024-01-01T00:00:00Z/2024-01-03T12:00:00Z'); result=[type(i).__name__,i.in_hours()]",
        ["Interval", 60],
    ),
    (
        "from-format",
        "import pendulum; d=pendulum.from_format('31/12/2024 23:59','DD/MM/YYYY HH:mm',tz='Europe/Paris'); result=d.to_iso8601_string()",
        "2024-12-31T23:59:00+01:00",
    ),
    (
        "format-tokens",
        "import pendulum; d=pendulum.datetime(2024,2,3,4,5,6,789000,tz='Europe/Paris'); result=d.format('YYYY-MM-DD [at] HH:mm:ss.SSSSSS ZZ')",
        "2024-02-03 at 04:05:06.789000 +0100",
    ),
    (
        "format-french",
        "import pendulum; d=pendulum.datetime(2024,7,14); result=d.format('dddd D MMMM YYYY',locale='fr')",
        "dimanche 14 juillet 2024",
    ),
    (
        "ukrainian-locale-name",
        "import pendulum; result=pendulum.datetime(2026,4,3,1,2,5).format('dddd D MMMM YYYY',locale='uk')",
        "пʼятницю 3 квітня 2026",
    ),
    (
        "human-difference",
        "import pendulum; a=pendulum.datetime(2024,1,1); b=a.add(days=2,hours=3); result=b.diff_for_humans(a,absolute=True,locale='en')",
        "2 days",
    ),
    (
        "duration-french-words",
        "import pendulum; result=pendulum.duration(days=2,hours=3).in_words(locale='fr')",
        "2 jours 3 heures",
    ),
    (
        "fixed-timezone",
        "import pendulum; z=pendulum.fixed_timezone(19800); d=pendulum.datetime(2024,1,1,tz=z); result=[z.name,d.to_iso8601_string(),d.offset]",
        ["+05:30", "2024-01-01T00:00:00+05:30", 19800],
    ),
    (
        "timezone-membership",
        "import pendulum; zones=pendulum.timezones(); result=[isinstance(zones,tuple) or isinstance(zones,set),'Europe/Paris' in zones,'America/New_York' in zones,len(zones)>500]",
        [True, True, True, True],
    ),
    (
        "timestamp-construction",
        "import pendulum; d=pendulum.from_timestamp(0,'America/New_York'); result=[d.to_iso8601_string(),d.int_timestamp]",
        ["1969-12-31T19:00:00-05:00", 0],
    ),
    (
        "stdlib-instance",
        "import datetime,pendulum; d=pendulum.instance(datetime.datetime(2024,1,2,3,4,5)); result=[type(d).__name__,d.to_iso8601_string()]",
        ["DateTime", "2024-01-02T03:04:05Z"],
    ),
    (
        "rfc-strings",
        "import pendulum; d=pendulum.datetime(2024,1,2,3,4,5); result=[d.to_rfc3339_string(),d.to_rfc2822_string(),d.to_cookie_string()]",
        ["2024-01-02T03:04:05+00:00", "Tue, 02 Jan 2024 03:04:05 +0000", "Tuesday, 02-Jan-2024 03:04:05 UTC"],
    ),
    (
        "invalid-timezone",
        "import pendulum\ntry:\n pendulum.timezone('Not/A_Zone')\nexcept Exception as e:\n result=type(e).__module__+'.'+type(e).__name__",
        "pendulum.tz.exceptions.InvalidTimezone",
    ),
    (
        "invalid-parse",
        "import pendulum\ntry:\n pendulum.parse('definitely not a date',strict=True)\nexcept Exception as e:\n result=type(e).__module__+'.'+type(e).__name__",
        "pendulum.parsing.exceptions.ParserError",
    ),
    (
        "invalid-calendar-date",
        "import pendulum\ntry:\n pendulum.date(2023,2,29)\nexcept Exception as e:\n result=type(e).__module__+'.'+type(e).__name__",
        "builtins.ValueError",
    ),
    (
        "invalid-locale",
        "import pendulum\ntry:\n pendulum.set_locale('not-a-locale')\nexcept Exception as e:\n result=type(e).__module__+'.'+type(e).__name__",
        "builtins.ValueError",
    ),
    (
        "time-travel",
        "import pendulum; target=pendulum.datetime(2030,5,6,7,8,9); before=pendulum.now().year\nwith pendulum.travel_to(target,freeze=True):\n inside=pendulum.now('UTC').to_iso8601_string()\nresult=[inside,pendulum.now().year==before]",
        ["2030-05-06T07:08:09Z", True],
    ),
    (
        "pickle-roundtrip",
        "import pickle,pendulum; d=pendulum.datetime(2024,2,29,12,30,tz='Europe/Paris'); x=pickle.loads(pickle.dumps(d)); result=[type(x).__name__,x.to_iso8601_string(),x==d]",
        ["DateTime", "2024-02-29T12:30:00+01:00", True],
    ),
)


def main() -> int:
    leaves: list[dict[str, str]] = []
    for scenario_id, source, expected in SCENARIOS:
        response = execute_script(textwrap.dedent(source), timeout_sec=10.0)
        actual = response.value if response.ok else response.exception_type
        passed = response.ok and actual == expected
        message = ""
        if not passed:
            message = json.dumps(
                {
                    "actual": actual,
                    "exception_message": response.exception_message,
                    "expected": expected,
                },
                ensure_ascii=False,
                sort_keys=True,
            )[:2000]
        leaves.append(
            {
                "id": f"pendulum/{scenario_id}",
                "message": message,
                "status": "passed" if passed else "failed",
            }
        )
    print(json.dumps({"schema_version": "1.0", "leaves": leaves}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
