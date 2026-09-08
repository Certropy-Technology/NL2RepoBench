"""Private deterministic scenarios for the python-dateutil public contract.

Each scenario runs as the unprivileged candidate in an isolated subprocess and
must be derivable from the public instruction (https://github.com/dateutil/dateutil,
v2.9.0.post0, immutable revision 48bd1af97e71baf8e96fce5b663d589caac8f147). The
candidate runner executes the script and reads the ``result`` binding.
"""

from __future__ import annotations

import json

from nl2repobench.verification.candidate_client import execute_script


def _run(source: str, expected: object) -> tuple[str, object]:
    observed = execute_script(source, timeout_sec=20.0)
    actual: dict[str, object] = {"ok": observed.ok, "value": observed.value}
    if not observed.ok:
        actual["exception_type"] = observed.exception_type
        actual["exception_message"] = observed.exception_message
    return "passed" if actual == expected else "failed", actual


CASES: list[tuple[str, str, object]] = [
    (
        "relativedelta-add-years",
        "from datetime import datetime\nfrom dateutil.relativedelta import relativedelta\ndt = datetime(2020, 1, 1, 12, 0, 0)\nresult = dt + relativedelta(years=1)",
        {"ok": True, "value": "2021-01-01T12:00:00"},
    ),
    (
        "relativedelta-add-months",
        "from datetime import datetime\nfrom dateutil.relativedelta import relativedelta\ndt = datetime(2020, 1, 31, 12, 0, 0)\nresult = dt + relativedelta(months=1)",
        {"ok": True, "value": "2020-02-29T12:00:00"},
    ),
    (
        "relativedelta-diff",
        "from datetime import datetime\nfrom dateutil.relativedelta import relativedelta\ndt1 = datetime(2020, 3, 15, 10, 30, 0)\ndt2 = datetime(2019, 1, 10, 8, 15, 0)\nrd = relativedelta(dt1, dt2)\nresult = [rd.years, rd.months]",
        {"ok": True, "value": [1, 2]},
    ),
    (
        "relativedelta-weekday-mo",
        "from datetime import datetime\nfrom dateutil.relativedelta import relativedelta, MO\ndt = datetime(2020, 1, 1, 12, 0, 0)\nresult = dt + relativedelta(weekday=MO)",
        {"ok": True, "value": "2020-01-06T12:00:00"},
    ),
    (
        "relativedelta-combined",
        "from datetime import datetime\nfrom dateutil.relativedelta import relativedelta\ndt = datetime(2020, 1, 1, 12, 0, 0)\nresult = dt + relativedelta(years=1, months=2, days=3)",
        {"ok": True, "value": "2021-03-04T12:00:00"},
    ),
    (
        "parse-iso-date",
        "from dateutil import parser\nresult = parser.parse(\"2020-01-15\")",
        {"ok": True, "value": "2020-01-15T00:00:00"},
    ),
    (
        "parse-iso-datetime",
        "from dateutil import parser\nresult = parser.parse(\"2020-01-15T14:30:00\")",
        {"ok": True, "value": "2020-01-15T14:30:00"},
    ),
    (
        "parse-fuzzy",
        "from dateutil import parser\nresult = parser.parse(\"Today is 2020-01-15\", fuzzy=True)",
        {"ok": True, "value": "2020-01-15T00:00:00"},
    ),
    (
        "parse-dayfirst",
        "from dateutil import parser\nresult = parser.parse(\"15/01/2020\", dayfirst=True)",
        {"ok": True, "value": "2020-01-15T00:00:00"},
    ),
    (
        "parse-error",
        "from dateutil import parser\ntry:\n    result = parser.parse(\"not a date\")\nexcept parser.ParserError:\n    result = \"ParserError\"",
        {"ok": True, "value": "ParserError"},
    ),
    (
        "rrule-daily-count",
        "from datetime import datetime\nfrom dateutil import rrule\nstart = datetime(2020, 1, 1, 9, 0, 0)\nresult = list(rrule.rrule(rrule.DAILY, count=3, dtstart=start))",
        {"ok": True, "value": ["2020-01-01T09:00:00", "2020-01-02T09:00:00", "2020-01-03T09:00:00"]},
    ),
    (
        "rrule-weekly",
        "from datetime import datetime\nfrom dateutil import rrule\nstart = datetime(2020, 1, 1, 9, 0, 0)\nresult = list(rrule.rrule(rrule.WEEKLY, count=2, dtstart=start))",
        {"ok": True, "value": ["2020-01-01T09:00:00", "2020-01-08T09:00:00"]},
    ),
    (
        "rrule-byweekday-mo",
        "from datetime import datetime\nfrom dateutil import rrule\nstart = datetime(2020, 1, 1, 9, 0, 0)\nresult = list(rrule.rrule(rrule.WEEKLY, count=3, byweekday=rrule.MO, dtstart=start))",
        {"ok": True, "value": ["2020-01-06T09:00:00", "2020-01-13T09:00:00", "2020-01-20T09:00:00"]},
    ),
    (
        "rrule-until",
        "from datetime import datetime\nfrom dateutil import rrule\nstart = datetime(2020, 1, 1, 9, 0, 0)\nuntil = datetime(2020, 1, 3, 9, 0, 0)\nresult = list(rrule.rrule(rrule.DAILY, dtstart=start, until=until))",
        {"ok": True, "value": ["2020-01-01T09:00:00", "2020-01-02T09:00:00", "2020-01-03T09:00:00"]},
    ),
    (
        "rrule-interval",
        "from datetime import datetime\nfrom dateutil import rrule\nstart = datetime(2020, 1, 1, 9, 0, 0)\nresult = list(rrule.rrule(rrule.DAILY, count=3, interval=2, dtstart=start))",
        {"ok": True, "value": ["2020-01-01T09:00:00", "2020-01-03T09:00:00", "2020-01-05T09:00:00"]},
    ),
    (
        "easter-2020",
        "from dateutil import easter\nresult = easter.easter(2020)",
        {"ok": True, "value": "2020-04-12"},
    ),
    (
        "easter-2021",
        "from dateutil import easter\nresult = easter.easter(2021)",
        {"ok": True, "value": "2021-04-04"},
    ),
    (
        "easter-method-julian",
        "from dateutil import easter\nresult = easter.easter(2020, method=easter.EASTER_JULIAN)",
        {"ok": True, "value": "2020-04-06"},
    ),
    (
        "easter-method-orthodox",
        "from dateutil import easter\nresult = easter.easter(2020, method=easter.EASTER_ORTHODOX)",
        {"ok": True, "value": "2020-04-19"},
    ),
    (
        "tz-datetime-utcoffset",
        "from datetime import datetime, timedelta\nfrom dateutil import tz\ndt = datetime(2020, 1, 1, 12, 0, 0, tzinfo=tz.tzoffset(None, timedelta(hours=5)))\nresult = dt.utcoffset()",
        {"ok": True, "value": {"seconds": 18000.0}},
    ),
    (
        "tz-datetime-tzname",
        "from datetime import datetime\nfrom dateutil import tz\ndt = datetime(2020, 1, 1, 12, 0, 0, tzinfo=tz.UTC)\nresult = dt.tzname()",
        {"ok": True, "value": "UTC"},
    ),
    (
        "tz-aware-comparison",
        "from datetime import datetime\nfrom dateutil import tz\ndt1 = datetime(2020, 1, 1, 12, 0, 0, tzinfo=tz.UTC)\ndt2 = datetime(2020, 1, 1, 12, 0, 0, tzinfo=tz.UTC)\nresult = dt1 == dt2",
        {"ok": True, "value": True},
    ),
    (
        "tz-tzoffset-name",
        "from dateutil import tz\nfrom datetime import timedelta\ntzinfo = tz.tzoffset(\"EST\", timedelta(hours=-5))\nresult = tzinfo.tzname(None)",
        {"ok": True, "value": "EST"},
    ),
]


def main() -> None:
    assert len(CASES) == 23, f"Expected 23 test cases, got {len(CASES)}"
    
    leaves: list[dict[str, object]] = []
    for case_id, source, expected in CASES:
        status, actual = _run(source, expected)
        leaf: dict[str, object] = {"id": case_id, "status": status}
        if status == "failed":
            leaf["message"] = json.dumps(actual, ensure_ascii=False, sort_keys=True)
        leaves.append(leaf)
    print(json.dumps({"schema_version": "1.0", "leaves": leaves}, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
