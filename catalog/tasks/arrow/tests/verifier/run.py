"""Private JSON verifier for Arrow's deterministic public contract."""

# Scenario source strings are intentionally kept inline for auditability.
# ruff: noqa: E501

from __future__ import annotations

import json

from nl2repobench.verification.candidate_client import execute_script


def _run(source: str, expected: object) -> dict[str, object]:
    observed = execute_script(source, timeout_sec=20.0)
    actual: dict[str, object] = {"ok": observed.ok, "value": observed.value}
    if not observed.ok:
        actual["exception_type"] = observed.exception_type
        actual["exception_message"] = observed.exception_message
    return {"status": "passed" if actual == expected else "failed", "actual": actual}


CASES: list[tuple[str, str, object]] = [
    (
        "metadata",
        "import arrow\nresult=[arrow.__version__, list(arrow.__all__)]",
        {"ok": True, "value": ["1.4.0", ["__version__", "get", "now", "utcnow", "Arrow", "ArrowFactory", "FORMAT_ATOM", "FORMAT_COOKIE", "FORMAT_RFC822", "FORMAT_RFC850", "FORMAT_RFC1036", "FORMAT_RFC1123", "FORMAT_RFC2822", "FORMAT_RFC3339", "FORMAT_RFC3339_STRICT", "FORMAT_RSS", "FORMAT_W3C", "ParserError"]]},
    ),
    (
        "init-and-repr",
        "import arrow\nresult=repr(arrow.Arrow(2020,1,2,3,4,5,tzinfo='US/Pacific'))",
        {"ok": True, "value": "<Arrow [2020-01-02T03:04:05-08:00]>"},
    ),
    (
        "str-and-properties",
        "import arrow\na=arrow.Arrow(2020,1,2,3,4,5,tzinfo='UTC')\nresult=[str(a),a.year,a.month,a.day,a.tzname(),a.fold]",
        {"ok": True, "value": ["2020-01-02T03:04:05+00:00", 2020, 1, 2, "UTC", 0]},
    ),
    (
        "get-iso",
        "import arrow\nresult=repr(arrow.get('2020-01-02T03:04:05+02:00'))",
        {"ok": True, "value": "<Arrow [2020-01-02T03:04:05+02:00]>"},
    ),
    (
        "get-date",
        "import arrow\nfrom datetime import date\nresult=repr(arrow.get(date(2020,1,2)))",
        {"ok": True, "value": "<Arrow [2020-01-02T00:00:00+00:00]>"},
    ),
    (
        "get-timestamp",
        "import arrow\nresult=repr(arrow.get(0))",
        {"ok": True, "value": "<Arrow [1970-01-01T00:00:00+00:00]>"},
    ),
    (
        "format-default",
        "import arrow\nresult=arrow.get('2020-01-02T03:04:05.123456+02:00').format()",
        {"ok": True, "value": "2020-01-02 03:04:05+02:00"},
    ),
    (
        "format-tokens",
        "import arrow\nresult=arrow.get('2020-01-02T03:04:05.123456+02:00').format('YYYY YY MMMM MMM MM M DDDD DDD DD D HH H hh h mm m ss s SSS Z ZZ ZZZ X x dddd ddd d A a')",
        {"ok": True, "value": "2020 20 January Jan 01 1 002 2 02 2 03 3 03 3 04 4 05 5 123 +0200 +02:00 UTC+02:00 1577927045.123456 1577927045123456 Thursday Thu 4 AM am"},
    ),
    (
        "format-literal",
        "import arrow\nresult=arrow.get('2020-01-02T03:04:05+00:00').format('[Today] YYYY')",
        {"ok": True, "value": "Today 2020"},
    ),
    (
        "timezone-conversion",
        "import arrow\nresult=arrow.get('2020-01-02T03:04:05+00:00').to('US/Pacific').format('YYYY-MM-DD HH:mm ZZ')",
        {"ok": True, "value": "2020-01-01 19:04 -08:00"},
    ),
    (
        "fixed-offset",
        "import arrow\nresult=arrow.get('2020-01-02T03:04:05+00:00').to('+05:30').format('YYYY-MM-DD HH:mm ZZ')",
        {"ok": True, "value": "2020-01-02 08:34 +05:30"},
    ),
    (
        "shift-days",
        "import arrow\nresult=arrow.get('2020-01-31').shift(days=1).format('YYYY-MM-DD')",
        {"ok": True, "value": "2020-02-01"},
    ),
    (
        "shift-month-clamp",
        "import arrow\nresult=arrow.get('2020-01-31').shift(months=1).format('YYYY-MM-DD')",
        {"ok": True, "value": "2020-02-29"},
    ),
    (
        "replace",
        "import arrow\nresult=arrow.get('2020-01-02').replace(day=5).format('YYYY-MM-DD')",
        {"ok": True, "value": "2020-01-05"},
    ),
    (
        "clone",
        "import arrow\nresult=arrow.get('2020-01-02').clone() == arrow.get('2020-01-02')",
        {"ok": True, "value": True},
    ),
    (
        "naive-and-datetime",
        "import arrow\na=arrow.get('2020-01-02T03:04:05+02:00')\nresult=[a.naive.isoformat(),a.datetime.isoformat()]",
        {"ok": True, "value": ["2020-01-02T03:04:05", "2020-01-02T03:04:05+02:00"]},
    ),
    (
        "timestamp",
        "import arrow\nresult=arrow.get('2020-01-02T03:04:05+00:00').timestamp()",
        {"ok": True, "value": 1577934245.0},
    ),
    (
        "timedelta-addition",
        "import arrow\nfrom datetime import timedelta\nresult=(arrow.get('2020-01-02')+timedelta(days=2)).format('YYYY-MM-DD')",
        {"ok": True, "value": "2020-01-04"},
    ),
    (
        "arrow-subtraction",
        "import arrow\nresult=(arrow.get('2020-01-04')-arrow.get('2020-01-02')).total_seconds()",
        {"ok": True, "value": 172800.0},
    ),
    (
        "fromdate",
        "import arrow\nfrom datetime import date\nresult=repr(arrow.Arrow.fromdate(date(2020,1,2)))",
        {"ok": True, "value": "<Arrow [2020-01-02T00:00:00+00:00]>"},
    ),
    (
        "fromordinal",
        "import arrow\nresult=repr(arrow.Arrow.fromordinal(737426))",
        {"ok": True, "value": "<Arrow [2020-01-02T00:00:00+00:00]>"},
    ),
    (
        "strptime",
        "import arrow\nresult=repr(arrow.Arrow.strptime('2020-01-02','%Y-%m-%d'))",
        {"ok": True, "value": "<Arrow [2020-01-02T00:00:00+00:00]>"},
    ),
    (
        "get-format",
        "import arrow\nresult=repr(arrow.get('2020/01/02', 'YYYY/MM/DD'))",
        {"ok": True, "value": "<Arrow [2020-01-02T00:00:00+00:00]>"},
    ),
    (
        "get-format-list",
        "import arrow\nresult=repr(arrow.get('02 Jan 2020', ['YYYY/MM/DD','DD MMM YYYY']))",
        {"ok": True, "value": "<Arrow [2020-01-02T00:00:00+00:00]>"},
    ),
    (
        "parser-iso",
        "from arrow.parser import DateTimeParser\nresult=DateTimeParser().parse_iso('2020-01-02T03:04:05Z').isoformat()",
        {"ok": True, "value": "2020-01-02T03:04:05+00:00"},
    ),
    (
        "parser-format",
        "from arrow.parser import DateTimeParser\nresult=DateTimeParser().parse('2020/01/02','YYYY/MM/DD').isoformat()",
        {"ok": True, "value": "2020-01-02T00:00:00"},
    ),
    (
        "parser-error",
        "from arrow.parser import DateTimeParser\ntry:\n DateTimeParser().parse('bad','YYYY')\nexcept Exception as exc:\n result=[type(exc).__name__,str(exc)]",
        {"ok": True, "value": ["ParserMatchError", "Failed to match 'YYYY' when parsing 'bad'."]},
    ),
    (
        "normalize-whitespace",
        "import arrow\nresult=repr(arrow.get('2020-01-02   03:04:05', normalize_whitespace=True))",
        {"ok": True, "value": "<Arrow [2020-01-02T03:04:05+00:00]>"},
    ),
    (
        "factory-class",
        "import arrow\nfrom arrow.api import factory\nresult=type(factory(arrow.Arrow)).__name__",
        {"ok": True, "value": "ArrowFactory"},
    ),
    (
        "factory-get",
        "import arrow\nfrom arrow.api import factory\nresult=factory(arrow.Arrow).get('2020-01-02').format('YYYY-MM-DD')",
        {"ok": True, "value": "2020-01-02"},
    ),
    (
        "locale-french",
        "from arrow.locales import get_locale\nresult=get_locale('fr').describe('day',1)",
        {"ok": True, "value": "dans un jour"},
    ),
    (
        "locale-month",
        "from arrow.locales import get_locale\nresult=get_locale('en_us').month_name(1)",
        {"ok": True, "value": "January"},
    ),
    (
        "humanize-past",
        "import arrow\nresult=arrow.get('2020-01-01').humanize(arrow.get('2020-01-02'))",
        {"ok": True, "value": "a day ago"},
    ),
    (
        "humanize-future",
        "import arrow\nresult=arrow.get('2020-01-02').humanize(arrow.get('2020-01-01'))",
        {"ok": True, "value": "in a day"},
    ),
    (
        "dehumanize",
        "import arrow\nresult=arrow.get('2020-01-01').dehumanize('in 2 days').format('YYYY-MM-DD')",
        {"ok": True, "value": "2020-01-03"},
    ),
    (
        "floor",
        "import arrow\nresult=arrow.get('2020-01-02T03:04:05').floor('hour').format('YYYY-MM-DD HH:mm:ss')",
        {"ok": True, "value": "2020-01-02 03:00:00"},
    ),
    (
        "ceil",
        "import arrow\nresult=arrow.get('2020-01-02T03:04:05').ceil('hour').format('YYYY-MM-DD HH:mm:ss')",
        {"ok": True, "value": "2020-01-02 03:59:59"},
    ),
    (
        "span",
        "import arrow\na,b=arrow.get('2020-01-02T03:04:05').span('hour')\nresult=[a.format('YYYY-MM-DD HH:mm:ss'),b.format('YYYY-MM-DD HH:mm:ss')]",
        {"ok": True, "value": ["2020-01-02 03:00:00", "2020-01-02 03:59:59"]},
    ),
    (
        "range",
        "import arrow\nresult=[x.format('HH:mm') for x in arrow.Arrow.range('hour',arrow.get('2020-01-02T00:00'),arrow.get('2020-01-02T03:00'))]",
        {"ok": True, "value": ["00:00", "01:00", "02:00", "03:00"]},
    ),
    (
        "interval",
        "import arrow\nresult=[[x.format('HH:mm') for x in pair] for pair in arrow.Arrow.interval('hour',arrow.get('2020-01-02T00:00'),arrow.get('2020-01-02T03:00'),interval=2)]",
        {"ok": True, "value": [["00:00", "01:59"], ["02:00", "03:59"]]},
    ),
    (
        "util-helpers",
        "from arrow.util import is_timestamp,iso_to_gregorian\nresult=[is_timestamp(1.5),iso_to_gregorian(2020,1,3).isoformat()]",
        {"ok": True, "value": [True, "2020-01-01"]},
    ),
    (
        "constants",
        "from arrow.constants import DEFAULT_LOCALE\nresult=DEFAULT_LOCALE",
        {"ok": True, "value": "en-us"},
    ),
    (
        "instant-equality",
        "import arrow\nresult=arrow.get('2020-01-02T00:00+00:00') == arrow.get('2020-01-01T19:00-05:00')",
        {"ok": True, "value": True},
    ),
    (
        "json",
        "import arrow\nresult=arrow.get('2020-01-02T03:04:05+00:00').for_json()",
        {"ok": True, "value": "2020-01-02T03:04:05+00:00"},
    ),
    (
        "utcfromtimestamp",
        "import arrow\nresult=repr(arrow.Arrow.utcfromtimestamp(0))",
        {"ok": True, "value": "<Arrow [1970-01-01T00:00:00+00:00]>"},
    ),
    (
        "fromdatetime",
        "import arrow\nfrom datetime import datetime,timezone\nresult=repr(arrow.Arrow.fromdatetime(datetime(2020,1,2,3,4,5,tzinfo=timezone.utc)))",
        {"ok": True, "value": "<Arrow [2020-01-02T03:04:05+00:00]>"},
    ),
    (
        "datetime-protocol",
        "import arrow\nresult=[arrow.get('2020-01-02').toordinal(),arrow.get('2020-01-02').isocalendar().week]",
        {"ok": True, "value": [737426, 1]},
    ),
    (
        "invalid-input",
        "import arrow\ntry:\n arrow.get(None)\nexcept Exception as exc:\n result=[type(exc).__name__,str(exc)]",
        {"ok": True, "value": ["TypeError", "Cannot parse argument of type None."]},
    ),
]


def main() -> None:
    leaves: list[dict[str, object]] = []
    for case_id, source, expected in CASES:
        outcome = _run(source, expected)
        leaf: dict[str, object] = {"id": case_id, "status": outcome["status"]}
        if outcome["status"] == "failed":
            leaf["message"] = json.dumps(outcome["actual"], ensure_ascii=False, sort_keys=True)
        leaves.append(leaf)
    print(json.dumps({"schema_version": "1.0", "leaves": leaves}, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
