#!/usr/bin/env python3
"""custom-json-v1 verifier for arrow datetime library."""
import sys
import json
from nl2repobench.verification.candidate_client import execute_script

# Test scenarios: 90 deterministic scenarios covering arrow API
CASES = [
    ("test_get_iso_string", """
import arrow
result = arrow.get('2024-01-15T12:30:45+00:00')
result = result.isoformat()
""", {"ok": True, "value": "2024-01-15T12:30:45+00:00"}),

    ("test_get_timestamp", """
import arrow
result = arrow.get(1705321845)
result = result.isoformat()
""", {"ok": True, "value": "2024-01-15T12:30:45+00:00"}),

    ("test_get_timestamp_float", """
import arrow
result = arrow.get(1705321845.5)
result = result.isoformat()
""", {"ok": True, "value": "2024-01-15T12:30:45.500000+00:00"}),

    ("test_get_ymd", """
import arrow
result = arrow.get(2024, 1, 15)
result = result.isoformat()
""", {"ok": True, "value": "2024-01-15T00:00:00+00:00"}),

    ("test_format_default", """
import arrow
a = arrow.get('2024-01-15T12:30:45+00:00')
result = a.format()
""", {"ok": True, "value": "2024-01-15 12:30:45+00:00"}),

    ("test_format_custom", """
import arrow
a = arrow.get('2024-01-15T12:30:45+00:00')
result = a.format('YYYY-MM-DD')
""", {"ok": True, "value": "2024-01-15"}),

    ("test_format_time", """
import arrow
a = arrow.get('2024-01-15T12:30:45+00:00')
result = a.format('HH:mm:ss')
""", {"ok": True, "value": "12:30:45"}),

    ("test_shift_days", """
import arrow
a = arrow.get('2024-01-15T12:30:45+00:00')
result = a.shift(days=5).isoformat()
""", {"ok": True, "value": "2024-01-20T12:30:45+00:00"}),

    ("test_shift_hours", """
import arrow
a = arrow.get('2024-01-15T12:30:45+00:00')
result = a.shift(hours=3).isoformat()
""", {"ok": True, "value": "2024-01-15T15:30:45+00:00"}),

    ("test_shift_months", """
import arrow
a = arrow.get('2024-01-15T12:30:45+00:00')
result = a.shift(months=2).isoformat()
""", {"ok": True, "value": "2024-03-15T12:30:45+00:00"}),

    ("test_shift_years", """
import arrow
a = arrow.get('2024-01-15T12:30:45+00:00')
result = a.shift(years=1).isoformat()
""", {"ok": True, "value": "2025-01-15T12:30:45+00:00"}),

    ("test_shift_negative", """
import arrow
a = arrow.get('2024-01-15T12:30:45+00:00')
result = a.shift(days=-3).isoformat()
""", {"ok": True, "value": "2024-01-12T12:30:45+00:00"}),

    ("test_replace_year", """
import arrow
a = arrow.get('2024-01-15T12:30:45+00:00')
result = a.replace(year=2025).isoformat()
""", {"ok": True, "value": "2025-01-15T12:30:45+00:00"}),

    ("test_replace_month", """
import arrow
a = arrow.get('2024-01-15T12:30:45+00:00')
result = a.replace(month=6).isoformat()
""", {"ok": True, "value": "2024-06-15T12:30:45+00:00"}),

    ("test_replace_day", """
import arrow
a = arrow.get('2024-01-15T12:30:45+00:00')
result = a.replace(day=20).isoformat()
""", {"ok": True, "value": "2024-01-20T12:30:45+00:00"}),

    ("test_replace_hour", """
import arrow
a = arrow.get('2024-01-15T12:30:45+00:00')
result = a.replace(hour=18).isoformat()
""", {"ok": True, "value": "2024-01-15T18:30:45+00:00"}),

    ("test_to_timezone", """
import arrow
a = arrow.get('2024-01-15T12:30:45+00:00')
result = a.to('US/Pacific').isoformat()
""", {"ok": True, "value": "2024-01-15T04:30:45-08:00"}),

    ("test_to_utc", """
import arrow
a = arrow.get('2024-01-15T12:30:45-05:00')
result = a.to('UTC').isoformat()
""", {"ok": True, "value": "2024-01-15T17:30:45+00:00"}),

    ("test_floor_hour", """
import arrow
a = arrow.get('2024-01-15T12:34:56+00:00')
result = a.floor('hour').isoformat()
""", {"ok": True, "value": "2024-01-15T12:00:00+00:00"}),

    ("test_floor_day", """
import arrow
a = arrow.get('2024-01-15T12:34:56+00:00')
result = a.floor('day').isoformat()
""", {"ok": True, "value": "2024-01-15T00:00:00+00:00"}),

    ("test_ceil_hour", """
import arrow
a = arrow.get('2024-01-15T12:34:56+00:00')
result = a.ceil('hour').isoformat()
""", {"ok": True, "value": "2024-01-15T12:59:59.999999+00:00"}),

    ("test_ceil_day", """
import arrow
a = arrow.get('2024-01-15T12:34:56+00:00')
result = a.ceil('day').isoformat()
""", {"ok": True, "value": "2024-01-15T23:59:59.999999+00:00"}),

    ("test_timestamp", """
import arrow
a = arrow.get('2024-01-15T12:30:45+00:00')
result = a.timestamp()
""", {"ok": True, "value": 1705321845.0}),

    ("test_humanize_past", """
import arrow
a = arrow.get('2024-01-15T12:30:45+00:00')
b = arrow.get('2024-01-15T14:30:45+00:00')
result = a.humanize(b, only_distance=True)
""", {"ok": True, "value": "2 hours"}),

    ("test_humanize_future", """
import arrow
a = arrow.get('2024-01-15T14:30:45+00:00')
b = arrow.get('2024-01-15T12:30:45+00:00')
result = a.humanize(b, only_distance=True)
""", {"ok": True, "value": "2 hours"}),

    ("test_span_day", """
import arrow
a = arrow.get('2024-01-15T12:30:45+00:00')
start, end = a.span('day')
result = [start.isoformat(), end.isoformat()]
""", {"ok": True, "value": ["2024-01-15T00:00:00+00:00", "2024-01-15T23:59:59.999999+00:00"]}),

    ("test_span_hour", """
import arrow
a = arrow.get('2024-01-15T12:30:45+00:00')
start, end = a.span('hour')
result = [start.isoformat(), end.isoformat()]
""", {"ok": True, "value": ["2024-01-15T12:00:00+00:00", "2024-01-15T12:59:59.999999+00:00"]}),

    ("test_get_string_format", """
import arrow
result = arrow.get('15/01/2024', 'DD/MM/YYYY').isoformat()
""", {"ok": True, "value": "2024-01-15T00:00:00+00:00"}),

    ("test_get_datetime", """
import arrow
from datetime import datetime
dt = datetime(2024, 1, 15, 12, 30, 45)
result = arrow.get(dt).isoformat()
""", {"ok": True, "value": "2024-01-15T12:30:45+00:00"}),

    ("test_get_full_ymdhs", """
import arrow
result = arrow.get(2024, 1, 15, 12, 30, 45).isoformat()
""", {"ok": True, "value": "2024-01-15T12:30:45+00:00"}),

    ("test_format_month_name", """
import arrow
a = arrow.get('2024-01-15T12:30:45+00:00')
result = a.format('MMMM')
""", {"ok": True, "value": "January"}),

    ("test_format_day_of_week", """
import arrow
a = arrow.get('2024-01-15T12:30:45+00:00')
result = a.format('dddd')
""", {"ok": True, "value": "Monday"}),

    ("test_shift_combined", """
import arrow
a = arrow.get('2024-01-15T12:30:45+00:00')
result = a.shift(days=2, hours=3).isoformat()
""", {"ok": True, "value": "2024-01-17T15:30:45+00:00"}),

    ("test_replace_multiple", """
import arrow
a = arrow.get('2024-01-15T12:30:45+00:00')
result = a.replace(year=2025, month=6, day=20).isoformat()
""", {"ok": True, "value": "2025-06-20T12:30:45+00:00"}),

    ("test_floor_minute", """
import arrow
a = arrow.get('2024-01-15T12:34:56+00:00')
result = a.floor('minute').isoformat()
""", {"ok": True, "value": "2024-01-15T12:34:00+00:00"}),

    ("test_ceil_minute", """
import arrow
a = arrow.get('2024-01-15T12:34:56+00:00')
result = a.ceil('minute').isoformat()
""", {"ok": True, "value": "2024-01-15T12:34:59.999999+00:00"}),

    ("test_span_month", """
import arrow
a = arrow.get('2024-01-15T12:30:45+00:00')
start, end = a.span('month')
result = [start.isoformat(), end.isoformat()]
""", {"ok": True, "value": ["2024-01-01T00:00:00+00:00", "2024-01-31T23:59:59.999999+00:00"]}),

    ("test_range_days", """
import arrow
start = arrow.get('2024-01-15T00:00:00+00:00')
end = arrow.get('2024-01-18T00:00:00+00:00')
result = [a.isoformat() for a in arrow.Arrow.range('day', start, end)]
""", {"ok": True, "value": ["2024-01-15T00:00:00+00:00", "2024-01-16T00:00:00+00:00", "2024-01-17T00:00:00+00:00", "2024-01-18T00:00:00+00:00"]}),

    ("test_range_hours", """
import arrow
start = arrow.get('2024-01-15T10:00:00+00:00')
end = arrow.get('2024-01-15T13:00:00+00:00')
result = [a.isoformat() for a in arrow.Arrow.range('hour', start, end)]
""", {"ok": True, "value": ["2024-01-15T10:00:00+00:00", "2024-01-15T11:00:00+00:00", "2024-01-15T12:00:00+00:00", "2024-01-15T13:00:00+00:00"]}),

    ("test_get_with_tzinfo", """
import arrow
result = arrow.get('2024-01-15T12:30:45', tzinfo='US/Eastern').isoformat()
""", {"ok": True, "value": "2024-01-15T12:30:45-05:00"}),

    ("test_shift_weeks", """
import arrow
a = arrow.get('2024-01-15T12:30:45+00:00')
result = a.shift(weeks=2).isoformat()
""", {"ok": True, "value": "2024-01-29T12:30:45+00:00"}),

    ("test_shift_minutes", """
import arrow
a = arrow.get('2024-01-15T12:30:45+00:00')
result = a.shift(minutes=30).isoformat()
""", {"ok": True, "value": "2024-01-15T13:00:45+00:00"}),

    ("test_shift_seconds", """
import arrow
a = arrow.get('2024-01-15T12:30:45+00:00')
result = a.shift(seconds=90).isoformat()
""", {"ok": True, "value": "2024-01-15T12:32:15+00:00"}),

    ("test_replace_minute_second", """
import arrow
a = arrow.get('2024-01-15T12:30:45+00:00')
result = a.replace(minute=0, second=0).isoformat()
""", {"ok": True, "value": "2024-01-15T12:00:00+00:00"}),

    ("test_floor_second", """
import arrow
a = arrow.get('2024-01-15T12:34:56.789+00:00')
result = a.floor('second').isoformat()
""", {"ok": True, "value": "2024-01-15T12:34:56+00:00"}),

    ("test_ceil_second", """
import arrow
a = arrow.get('2024-01-15T12:34:56.789+00:00')
result = a.ceil('second').isoformat()
""", {"ok": True, "value": "2024-01-15T12:34:56.999999+00:00"}),

    ("test_format_year", """
import arrow
a = arrow.get('2024-01-15T12:30:45+00:00')
result = a.format('YYYY')
""", {"ok": True, "value": "2024"}),

    ("test_format_short_month", """
import arrow
a = arrow.get('2024-01-15T12:30:45+00:00')
result = a.format('MMM')
""", {"ok": True, "value": "Jan"}),

    ("test_format_day_of_month", """
import arrow
a = arrow.get('2024-01-15T12:30:45+00:00')
result = a.format('DD')
""", {"ok": True, "value": "15"}),

    ("test_format_12_hour", """
import arrow
a = arrow.get('2024-01-15T14:30:45+00:00')
result = a.format('hh:mm A')
""", {"ok": True, "value": "02:30 PM"}),

    ("test_get_multiple_formats", """
import arrow
result = arrow.get('2024/01/15', ['YYYY-MM-DD', 'YYYY/MM/DD']).isoformat()
""", {"ok": True, "value": "2024-01-15T00:00:00+00:00"}),

    ("test_to_timezone_europe", """
import arrow
a = arrow.get('2024-01-15T12:30:45+00:00')
result = a.to('Europe/London').isoformat()
""", {"ok": True, "value": "2024-01-15T12:30:45+00:00"}),

    ("test_to_timezone_asia", """
import arrow
a = arrow.get('2024-01-15T12:30:45+00:00')
result = a.to('Asia/Tokyo').isoformat()
""", {"ok": True, "value": "2024-01-15T21:30:45+09:00"}),

    ("test_span_year", """
import arrow
a = arrow.get('2024-01-15T12:30:45+00:00')
start, end = a.span('year')
result = [start.isoformat(), end.isoformat()]
""", {"ok": True, "value": ["2024-01-01T00:00:00+00:00", "2024-12-31T23:59:59.999999+00:00"]}),

    ("test_shift_microseconds", """
import arrow
a = arrow.get('2024-01-15T12:30:45+00:00')
result = a.shift(microseconds=500000).isoformat()
""", {"ok": True, "value": "2024-01-15T12:30:45.500000+00:00"}),

    ("test_replace_microsecond", """
import arrow
a = arrow.get('2024-01-15T12:30:45.123456+00:00')
result = a.replace(microsecond=0).isoformat()
""", {"ok": True, "value": "2024-01-15T12:30:45+00:00"}),

    ("test_humanize_granularity", """
import arrow
a = arrow.get('2024-01-15T12:30:45+00:00')
b = arrow.get('2024-01-16T14:30:45+00:00')
result = a.humanize(b, only_distance=True, granularity='day')
""", {"ok": True, "value": "a day"}),

    ("test_get_date_object", """
import arrow
from datetime import date
d = date(2024, 1, 15)
result = arrow.get(d).isoformat()
""", {"ok": True, "value": "2024-01-15T00:00:00+00:00"}),

    ("test_floor_week", """
import arrow
a = arrow.get('2024-01-15T12:30:45+00:00')
result = a.floor('week').isoformat()
""", {"ok": True, "value": "2024-01-15T00:00:00+00:00"}),

    ("test_ceil_week", """
import arrow
a = arrow.get('2024-01-15T12:30:45+00:00')
result = a.ceil('week').isoformat()
""", {"ok": True, "value": "2024-01-21T23:59:59.999999+00:00"}),

    ("test_span_week", """
import arrow
a = arrow.get('2024-01-15T12:30:45+00:00')
start, end = a.span('week')
result = [start.isoformat(), end.isoformat()]
""", {"ok": True, "value": ["2024-01-15T00:00:00+00:00", "2024-01-21T23:59:59.999999+00:00"]}),

    ("test_get_with_tzinfo_object", """
import arrow
from datetime import datetime, timezone
dt = datetime(2024, 1, 15, 12, 30, 45, tzinfo=timezone.utc)
result = arrow.get(dt).isoformat()
""", {"ok": True, "value": "2024-01-15T12:30:45+00:00"}),

    ("test_timestamp_with_microseconds", """
import arrow
a = arrow.get('2024-01-15T12:30:45.500000+00:00')
result = a.timestamp()
""", {"ok": True, "value": 1705321845.5}),

    ("test_format_with_timezone", """
import arrow
a = arrow.get('2024-01-15T12:30:45+00:00')
result = a.format('YYYY-MM-DD HH:mm:ss ZZ')
""", {"ok": True, "value": "2024-01-15 12:30:45 +00:00"}),

    ("test_floor_month", """
import arrow
a = arrow.get('2024-01-15T12:30:45+00:00')
result = a.floor('month').isoformat()
""", {"ok": True, "value": "2024-01-01T00:00:00+00:00"}),

    ("test_ceil_month", """
import arrow
a = arrow.get('2024-01-15T12:30:45+00:00')
result = a.ceil('month').isoformat()
""", {"ok": True, "value": "2024-01-31T23:59:59.999999+00:00"}),

    ("test_shift_negative_hours", """
import arrow
a = arrow.get('2024-01-15T12:30:45+00:00')
result = a.shift(hours=-5).isoformat()
""", {"ok": True, "value": "2024-01-15T07:30:45+00:00"}),

    ("test_shift_negative_months", """
import arrow
a = arrow.get('2024-03-15T12:30:45+00:00')
result = a.shift(months=-2).isoformat()
""", {"ok": True, "value": "2024-01-15T12:30:45+00:00"}),

    ("test_replace_tzinfo", """
import arrow
a = arrow.get('2024-01-15T12:30:45+00:00')
result = a.replace(tzinfo='US/Pacific').isoformat()
""", {"ok": True, "value": "2024-01-15T12:30:45-08:00"}),

    ("test_humanize_minutes", """
import arrow
a = arrow.get('2024-01-15T12:30:45+00:00')
b = arrow.get('2024-01-15T12:45:45+00:00')
result = a.humanize(b, only_distance=True)
""", {"ok": True, "value": "15 minutes"}),

    ("test_humanize_seconds", """
import arrow
a = arrow.get('2024-01-15T12:30:45+00:00')
b = arrow.get('2024-01-15T12:31:30+00:00')
result = a.humanize(b, only_distance=True)
""", {"ok": True, "value": "45 seconds"}),

    ("test_get_naive_then_to", """
import arrow
from datetime import datetime
dt = datetime(2024, 1, 15, 12, 30, 45)
a = arrow.get(dt)
result = a.to('US/Pacific').isoformat()
""", {"ok": True, "value": "2024-01-15T04:30:45-08:00"}),

    ("test_span_quarter", """
import arrow
a = arrow.get('2024-02-15T12:30:45+00:00')
start, end = a.span('quarter')
result = [start.isoformat(), end.isoformat()]
""", {"ok": True, "value": ["2024-01-01T00:00:00+00:00", "2024-03-31T23:59:59.999999+00:00"]}),

    ("test_floor_year", """
import arrow
a = arrow.get('2024-06-15T12:30:45+00:00')
result = a.floor('year').isoformat()
""", {"ok": True, "value": "2024-01-01T00:00:00+00:00"}),

    ("test_ceil_year", """
import arrow
a = arrow.get('2024-06-15T12:30:45+00:00')
result = a.ceil('year').isoformat()
""", {"ok": True, "value": "2024-12-31T23:59:59.999999+00:00"}),

    ("test_format_with_escape", """
import arrow
a = arrow.get('2024-01-15T12:30:45+00:00')
result = a.format('[Year] YYYY')
""", {"ok": True, "value": "Year 2024"}),

    ("test_get_leap_year", """
import arrow
result = arrow.get('2024-02-29T12:30:45+00:00').isoformat()
""", {"ok": True, "value": "2024-02-29T12:30:45+00:00"}),

    ("test_shift_month_boundary", """
import arrow
a = arrow.get('2024-01-31T12:30:45+00:00')
result = a.shift(months=1).isoformat()
""", {"ok": True, "value": "2024-02-29T12:30:45+00:00"}),

    ("test_shift_year_boundary", """
import arrow
a = arrow.get('2024-12-31T12:30:45+00:00')
result = a.shift(days=1).isoformat()
""", {"ok": True, "value": "2025-01-01T12:30:45+00:00"}),

    ("test_get_struct_time", """
import arrow
import time
st = time.strptime('2024-01-15 12:30:45', '%Y-%m-%d %H:%M:%S')
result = arrow.get(st).isoformat()
""", {"ok": True, "value": "2024-01-15T12:30:45+00:00"}),

    ("test_humanize_days", """
import arrow
a = arrow.get('2024-01-15T12:30:45+00:00')
b = arrow.get('2024-01-18T12:30:45+00:00')
result = a.humanize(b, only_distance=True)
""", {"ok": True, "value": "3 days"}),

    ("test_humanize_months", """
import arrow
a = arrow.get('2024-01-15T12:30:45+00:00')
b = arrow.get('2024-03-15T12:30:45+00:00')
result = a.humanize(b, only_distance=True)
""", {"ok": True, "value": "2 months"}),

    ("test_format_iso_basic", """
import arrow
a = arrow.get('2024-01-15T12:30:45+00:00')
result = a.format('YYYYMMDDTHHmmss')
""", {"ok": True, "value": "20240115T123045"}),

    ("test_replace_tzinfo_string", """
import arrow
a = arrow.get('2024-01-15T12:30:45+00:00')
result = a.replace(tzinfo='Europe/Paris').isoformat()
""", {"ok": True, "value": "2024-01-15T12:30:45+01:00"}),

    ("test_floor_quarter", """
import arrow
a = arrow.get('2024-02-15T12:30:45+00:00')
result = a.floor('quarter').isoformat()
""", {"ok": True, "value": "2024-01-01T00:00:00+00:00"}),

    ("test_ceil_quarter", """
import arrow
a = arrow.get('2024-02-15T12:30:45+00:00')
result = a.ceil('quarter').isoformat()
""", {"ok": True, "value": "2024-03-31T23:59:59.999999+00:00"}),

    ("test_shift_quarters", """
import arrow
a = arrow.get('2024-01-15T12:30:45+00:00')
result = a.shift(quarters=2).isoformat()
""", {"ok": True, "value": "2024-07-15T12:30:45+00:00"}),

    ("test_format_full_datetime", """
import arrow
a = arrow.get('2024-01-15T12:30:45+00:00')
result = a.format('dddd, MMMM DD, YYYY [at] HH:mm:ss')
""", {"ok": True, "value": "Monday, January 15, 2024 at 12:30:45"}),

    ("test_get_negative_timestamp", """
import arrow
result = arrow.get(-86400).isoformat()
""", {"ok": True, "value": "1969-12-31T00:00:00+00:00"}),

    ("test_span_minute", """
import arrow
a = arrow.get('2024-01-15T12:30:45+00:00')
start, end = a.span('minute')
result = [start.isoformat(), end.isoformat()]
""", {"ok": True, "value": ["2024-01-15T12:30:00+00:00", "2024-01-15T12:30:59.999999+00:00"]}),
]

def main():
    """Run all test scenarios and output custom-json-v1 format."""
    assert len(CASES) == 90, f"Expected 90 cases, got {len(CASES)}"
    
    leaves = []
    for test_id, script, expected in CASES:
        result = execute_script(script)
        
        if result == expected:
            status = "passed"
        else:
            status = "failed"
        
        leaves.append({"id": test_id, "status": status})
    
    output = {
        "schema_version": "1.0",
        "leaves": leaves
    }
    print(json.dumps(output))
    return 0

if __name__ == "__main__":
    sys.exit(main())
