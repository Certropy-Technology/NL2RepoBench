import json
import os
import subprocess
import sys


CASES = [
    ("parser-basic", "from dateutil import parser; from datetime import datetime; ok = parser.parse('2024-07-14 09:30') == datetime(2024, 7, 14, 9, 30)"),
    ("parser-fuzzy", "from dateutil import parser; from datetime import datetime; ok = parser.parse('Today is January 1, 2040 at 5:30 pm', fuzzy=True) == datetime(2040, 1, 1, 17, 30)"),
    ("parser-options", "from dateutil import parser; from datetime import datetime; ok = parser.parse('03/04/05', dayfirst=True, yearfirst=False) == datetime(2005, 4, 3)"),
    ("parser-error", "from dateutil import parser; ok = False\ntry:\n parser.parse('not a date')\nexcept parser.ParserError:\n ok = True"),
    ("isoparse-aware", "from dateutil import parser; from datetime import timedelta; ok = parser.isoparse('2024-03-01T12:34:56+02:30').utcoffset() == timedelta(hours=2, minutes=30)"),
    ("isoparse-week-date", "from dateutil import parser; from datetime import datetime; ok = parser.isoparse('2024-W01-1') == datetime(2024, 1, 1)"),
    ("relativedelta-month-end", "from dateutil.relativedelta import relativedelta; from datetime import date; ok = date(2023, 1, 31) + relativedelta(months=1) == date(2023, 2, 28)"),
    ("relativedelta-normalized", "from dateutil.relativedelta import relativedelta; ok = relativedelta(days=1.5, hours=2).normalized() == relativedelta(days=1, hours=14)"),
    ("relativedelta-weekday", "from dateutil.relativedelta import relativedelta, MO; from datetime import date; ok = date(2024, 5, 1) + relativedelta(weekday=MO(+1)) == date(2024, 5, 6)"),
    ("relativedelta-subtract", "from dateutil.relativedelta import relativedelta; from datetime import date; ok = date(2024, 3, 31) + relativedelta(months=-1) == date(2024, 2, 29)"),
    ("easter-western", "from dateutil import easter; from datetime import date; ok = easter.easter(2024, 3) == date(2024, 3, 31)"),
    ("easter-orthodox", "from dateutil import easter; from datetime import date; ok = easter.easter(2024, 2) == date(2024, 5, 5)"),
    ("rrule-daily", "from dateutil.rrule import rrule, DAILY; from datetime import datetime; ok = list(rrule(DAILY, count=3, dtstart=datetime(2024, 1, 1))) == [datetime(2024, 1, 1), datetime(2024, 1, 2), datetime(2024, 1, 3)]"),
    ("rrule-interval", "from dateutil.rrule import rrule, WEEKLY; from datetime import datetime; ok = [x.day for x in rrule(WEEKLY, interval=2, count=3, dtstart=datetime(2024, 1, 1))] == [1, 15, 29]"),
    ("rrule-byweekday", "from dateutil.rrule import rrule, MONTHLY, MO; from datetime import datetime; ok = [x.day for x in rrule(MONTHLY, byweekday=MO, count=3, dtstart=datetime(2024, 1, 1))] == [1, 8, 15]"),
    ("rrule-monthday", "from dateutil.rrule import rrule, MONTHLY; from datetime import datetime; ok = [x.day for x in rrule(MONTHLY, bymonthday=31, count=4, dtstart=datetime(2024, 1, 1))] == [31, 31, 31, 31]"),
    ("rrulestr", "from dateutil.rrule import rrulestr; from datetime import datetime; ok = list(rrulestr('DTSTART:20240101T090000\\nRRULE:FREQ=WEEKLY;COUNT=2')) == [datetime(2024, 1, 1, 9), datetime(2024, 1, 8, 9)]"),
    ("rruleset-exdate", "from dateutil.rrule import rrule, rruleset, DAILY; from datetime import datetime; s=rruleset(); s.rrule(rrule(DAILY, count=3, dtstart=datetime(2024, 1, 1))); s.exdate(datetime(2024, 1, 2)); ok = list(s) == [datetime(2024, 1, 1), datetime(2024, 1, 3)]"),
    ("tz-fixed-offset", "from dateutil import tz; from datetime import datetime, timedelta; z=tz.tzoffset('IST', 19800); ok = z.tzname(None) == 'IST' and z.utcoffset(datetime(2024, 1, 1)) == timedelta(hours=5, minutes=30)"),
    ("tz-named-zone", "from dateutil import tz; from datetime import datetime, timedelta; z=tz.gettz('America/New_York'); ok = datetime(2024, 1, 1, tzinfo=z).utcoffset() == -timedelta(hours=5)"),
    ("tz-ambiguous", "from dateutil import tz; from datetime import datetime; z=tz.gettz('America/New_York'); ok = tz.datetime_ambiguous(datetime(2021, 11, 7, 1, 30, tzinfo=z))"),
    ("tz-imaginary", "from dateutil import tz; from datetime import datetime; z=tz.gettz('America/New_York'); d=datetime(2021, 3, 14, 2, 30, tzinfo=z); ok = not tz.datetime_exists(d) and tz.resolve_imaginary(d).hour == 3"),
    ("tz-enfold", "from dateutil import tz; from datetime import datetime; z=tz.gettz('America/New_York'); ok = tz.enfold(datetime(2021, 11, 7, 1, 30, tzinfo=z)).fold == 1"),
]


def run_case(code):
    bootstrap = "import sys; sys.path[:0] = ['/tmp/candidate-site', '/opt/candidate-dependencies/site']; " + code + "; print(json.dumps({'ok': bool(ok)}))"
    try:
        result = subprocess.run(
            [sys.executable, '-I', '-B', '-c', 'import json; ' + bootstrap],
            cwd='/workspace', capture_output=True, text=True, timeout=8,
            env={'PATH': os.environ.get('PATH', ''), 'TZ': 'UTC'}, check=False,
        )
    except subprocess.TimeoutExpired:
        return False, 'child timeout'
    if result.returncode != 0:
        return False, result.stderr[-500:]
    try:
        payload = json.loads(result.stdout.strip().splitlines()[-1])
    except (IndexError, json.JSONDecodeError):
        return False, 'child produced no JSON result'
    return bool(payload.get('ok')), '' if payload.get('ok') else 'behavior assertion failed'


def main():
    leaves = []
    for case_id, code in CASES:
        ok, message = run_case(code)
        leaves.append({'id': case_id, 'status': 'passed' if ok else 'failed', 'message': message})
    print(json.dumps({'schema_version': '1.0', 'leaves': leaves}, sort_keys=True))


if __name__ == '__main__':
    main()
