"""Private deterministic scenarios for the dateparser public contract.

Each scenario runs as the unprivileged candidate in an isolated subprocess and
must be derivable from the public instruction (https://github.com/scrapinghub/dateparser,
v1.4.3, immutable revision 9ce60b1958f1b285886bcfbb743f6419feacfc92). The
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
    # Basic ISO date parsing
    (
        "iso-date-basic",
        "import dateparser\ndt = dateparser.parse('2024-01-15')\nresult = [dt.year, dt.month, dt.day]",
        {"ok": True, "value": [2024, 1, 15]},
    ),
    (
        "iso-datetime-basic",
        "import dateparser\ndt = dateparser.parse('2024-01-15T14:30:00')\nresult = [dt.year, dt.month, dt.day, dt.hour, dt.minute]",
        {"ok": True, "value": [2024, 1, 15, 14, 30]},
    ),
    (
        "iso-date-method",
        "import dateparser\nfrom datetime import date\ndt = dateparser.parse('2024-01-15')\nresult = [type(dt.date()).__name__, dt.date() == date(2024, 1, 15)]",
        {"ok": True, "value": ["date", True]},
    ),
    (
        "iso-isoformat",
        "import dateparser\ndt = dateparser.parse('2024-01-15')\nresult = dt.isoformat().startswith('2024-01-15T00:00:00')",
        {"ok": True, "value": True},
    ),
    
    # Unparseable input returns None
    (
        "unparseable-text",
        "import dateparser\nresult = dateparser.parse('not a date')",
        {"ok": True, "value": None},
    ),
    (
        "unparseable-empty",
        "import dateparser\nresult = dateparser.parse('')",
        {"ok": True, "value": None},
    ),
    (
        "unparseable-whitespace",
        "import dateparser\nresult = dateparser.parse('   ')",
        {"ok": True, "value": None},
    ),
    (
        "unparseable-gibberish",
        "import dateparser\nresult = dateparser.parse('xyz123abc')",
        {"ok": True, "value": None},
    ),
    
    # Relative dates with RELATIVE_BASE
    (
        "relative-tomorrow",
        "import dateparser\nfrom datetime import datetime\nbase = datetime(2024, 1, 15, 12, 0, 0)\ndt = dateparser.parse('tomorrow', settings={'RELATIVE_BASE': base})\nresult = [dt.year, dt.month, dt.day]",
        {"ok": True, "value": [2024, 1, 16]},
    ),
    (
        "relative-yesterday",
        "import dateparser\nfrom datetime import datetime\nbase = datetime(2024, 1, 15, 12, 0, 0)\ndt = dateparser.parse('yesterday', settings={'RELATIVE_BASE': base})\nresult = [dt.year, dt.month, dt.day]",
        {"ok": True, "value": [2024, 1, 14]},
    ),
    (
        "relative-today",
        "import dateparser\nfrom datetime import datetime\nbase = datetime(2024, 1, 15, 12, 0, 0)\ndt = dateparser.parse('today', settings={'RELATIVE_BASE': base})\nresult = [dt.year, dt.month, dt.day]",
        {"ok": True, "value": [2024, 1, 15]},
    ),
    (
        "relative-days-ago",
        "import dateparser\nfrom datetime import datetime\nbase = datetime(2024, 1, 15, 12, 0, 0)\ndt = dateparser.parse('3 days ago', settings={'RELATIVE_BASE': base})\nresult = [dt.year, dt.month, dt.day]",
        {"ok": True, "value": [2024, 1, 12]},
    ),
    (
        "relative-days-future",
        "import dateparser\nfrom datetime import datetime\nbase = datetime(2024, 1, 15, 12, 0, 0)\ndt = dateparser.parse('in 5 days', settings={'RELATIVE_BASE': base})\nresult = [dt.year, dt.month, dt.day]",
        {"ok": True, "value": [2024, 1, 20]},
    ),
    
    # DATE_ORDER settings
    (
        "date-order-mdy",
        "import dateparser\ndt = dateparser.parse('01/15/2024', settings={'DATE_ORDER': 'MDY'})\nresult = [dt.month, dt.day, dt.year]",
        {"ok": True, "value": [1, 15, 2024]},
    ),
    (
        "date-order-dmy",
        "import dateparser\ndt = dateparser.parse('15/01/2024', settings={'DATE_ORDER': 'DMY'})\nresult = [dt.day, dt.month, dt.year]",
        {"ok": True, "value": [15, 1, 2024]},
    ),
    (
        "date-order-ymd",
        "import dateparser\ndt = dateparser.parse('2024/01/15', settings={'DATE_ORDER': 'YMD'})\nresult = [dt.year, dt.month, dt.day]",
        {"ok": True, "value": [2024, 1, 15]},
    ),
    
    # Common date formats
    (
        "format-month-name-long",
        "import dateparser\ndt = dateparser.parse('January 15, 2024')\nresult = [dt.year, dt.month, dt.day]",
        {"ok": True, "value": [2024, 1, 15]},
    ),
    (
        "format-month-name-short",
        "import dateparser\ndt = dateparser.parse('Jan 15, 2024')\nresult = [dt.year, dt.month, dt.day]",
        {"ok": True, "value": [2024, 1, 15]},
    ),
    (
        "format-day-month-year",
        "import dateparser\ndt = dateparser.parse('15 Jan 2024')\nresult = [dt.day, dt.month, dt.year]",
        {"ok": True, "value": [15, 1, 2024]},
    ),
    
    # Timestamp parsing
    (
        "timestamp-seconds",
        "import dateparser\ndt = dateparser.parse('1705334400')\nresult = dt is not None",
        {"ok": True, "value": True},
    ),
    (
        "timestamp-with-time",
        "import dateparser\ndt = dateparser.parse('1705334400')\nresult = [dt.year >= 2024, dt.month >= 1]",
        {"ok": True, "value": [True, True]},
    ),
    
    # DateDataParser class
    (
        "datadataparser-basic",
        "from dateparser import DateDataParser\nparser = DateDataParser()\ndata = parser.get_date_data('2024-01-15')\nresult = [type(data).__name__ == 'DateData', hasattr(data, 'date_obj')]",
        {"ok": True, "value": [True, True]},
    ),
    (
        "datadataparser-date-obj",
        "from dateparser import DateDataParser\nparser = DateDataParser()\ndata = parser.get_date_data('2024-01-15')\ndt = data['date_obj'] if data else None\nresult = [dt.year, dt.month, dt.day] if dt else None",
        {"ok": True, "value": [2024, 1, 15]},
    ),
    (
        "datadataparser-settings",
        "from dateparser import DateDataParser\nparser = DateDataParser(settings={'DATE_ORDER': 'DMY'})\ndata = parser.get_date_data('15/01/2024')\ndt = data['date_obj'] if data else None\nresult = [dt.day, dt.month] if dt else None",
        {"ok": True, "value": [15, 1]},
    ),
    (
        "datadataparser-none",
        "from dateparser import DateDataParser\nparser = DateDataParser()\ndata = parser.get_date_data('not a date')\nresult = data.date_obj",
        {"ok": True, "value": None},
    ),
    
    # More relative expressions
    (
        "relative-weeks-ago",
        "import dateparser\nfrom datetime import datetime\nbase = datetime(2024, 1, 15, 12, 0, 0)\ndt = dateparser.parse('2 weeks ago', settings={'RELATIVE_BASE': base})\nresult = [dt.year, dt.month, dt.day]",
        {"ok": True, "value": [2024, 1, 1]},
    ),
    (
        "relative-months-ago",
        "import dateparser\nfrom datetime import datetime\nbase = datetime(2024, 2, 15, 12, 0, 0)\ndt = dateparser.parse('1 month ago', settings={'RELATIVE_BASE': base})\nresult = [dt.year, dt.month, dt.day]",
        {"ok": True, "value": [2024, 1, 15]},
    ),
    (
        "relative-hours-ago",
        "import dateparser\nfrom datetime import datetime\nbase = datetime(2024, 1, 15, 15, 0, 0)\ndt = dateparser.parse('3 hours ago', settings={'RELATIVE_BASE': base})\nresult = [dt.year, dt.month, dt.day, dt.hour]",
        {"ok": True, "value": [2024, 1, 15, 12]},
    ),
    
    # Different date separators
    (
        "separator-hyphen",
        "import dateparser\ndt = dateparser.parse('2024-01-15')\nresult = [dt.year, dt.month, dt.day]",
        {"ok": True, "value": [2024, 1, 15]},
    ),
    (
        "separator-slash",
        "import dateparser\ndt = dateparser.parse('2024/01/15')\nresult = [dt.year, dt.month, dt.day]",
        {"ok": True, "value": [2024, 1, 15]},
    ),
    (
        "separator-dot",
        "import dateparser\ndt = dateparser.parse('2024.01.15')\nresult = [dt.year, dt.month, dt.day]",
        {"ok": True, "value": [2024, 1, 15]},
    ),
    
    # Year variations
    (
        "year-two-digit",
        "import dateparser\ndt = dateparser.parse('01/15/24', settings={'DATE_ORDER': 'MDY'})\nresult = dt is not None",
        {"ok": True, "value": True},
    ),
    (
        "year-four-digit",
        "import dateparser\ndt = dateparser.parse('01/15/2024', settings={'DATE_ORDER': 'MDY'})\nresult = [dt.year, dt.month, dt.day]",
        {"ok": True, "value": [2024, 1, 15]},
    ),
    
    # Edge cases
    (
        "date-leap-year",
        "import dateparser\ndt = dateparser.parse('2024-02-29')\nresult = [dt.year, dt.month, dt.day]",
        {"ok": True, "value": [2024, 2, 29]},
    ),
    (
        "date-end-of-year",
        "import dateparser\ndt = dateparser.parse('2024-12-31')\nresult = [dt.year, dt.month, dt.day]",
        {"ok": True, "value": [2024, 12, 31]},
    ),
    (
        "date-start-of-year",
        "import dateparser\ndt = dateparser.parse('2024-01-01')\nresult = [dt.year, dt.month, dt.day]",
        {"ok": True, "value": [2024, 1, 1]},
    ),
    
    # Time components
    (
        "time-hours-minutes",
        "import dateparser\ndt = dateparser.parse('2024-01-15 14:30')\nresult = [dt.hour, dt.minute]",
        {"ok": True, "value": [14, 30]},
    ),
    (
        "time-hours-minutes-seconds",
        "import dateparser\ndt = dateparser.parse('2024-01-15 14:30:45')\nresult = [dt.hour, dt.minute, dt.second]",
        {"ok": True, "value": [14, 30, 45]},
    ),
    (
        "time-midnight",
        "import dateparser\ndt = dateparser.parse('2024-01-15 00:00:00')\nresult = [dt.hour, dt.minute, dt.second]",
        {"ok": True, "value": [0, 0, 0]},
    ),
    
    # More natural language
    (
        "natural-now",
        "import dateparser\nfrom datetime import datetime\nbase = datetime(2024, 1, 15, 12, 0, 0)\ndt = dateparser.parse('now', settings={'RELATIVE_BASE': base})\nresult = dt is not None",
        {"ok": True, "value": True},
    ),
    
    # Settings validation - REQUIRE_PARTS
    (
        "settings-require-parts-valid",
        "import dateparser\ndt = dateparser.parse('2024-01-15', settings={'REQUIRE_PARTS': ['day', 'month', 'year']})\nresult = [dt.year, dt.month, dt.day]",
        {"ok": True, "value": [2024, 1, 15]},
    ),
    (
        "settings-require-parts-missing",
        "import dateparser\ndt = dateparser.parse('January 2024', settings={'REQUIRE_PARTS': ['day', 'month', 'year']})\nresult = dt",
        {"ok": True, "value": None},
    ),
    (
        "settings-require-parts-invalid",
        "import dateparser\nfrom dateparser.conf import SettingValidationError\ntry:\n    dt = dateparser.parse('2024-01-15', settings={'REQUIRE_PARTS': ['invalid']})\n    result = 'no-error'\nexcept SettingValidationError:\n    result = 'SettingValidationError'\nexcept ValueError:\n    result = 'ValueError'",
        {"ok": True, "value": "SettingValidationError"},
    ),
    
    # Multiple date formats
    (
        "format-long-month-day-year",
        "import dateparser\ndt = dateparser.parse('December 25, 2024')\nresult = [dt.month, dt.day]",
        {"ok": True, "value": [12, 25]},
    ),
    (
        "format-short-month-day-year",
        "import dateparser\ndt = dateparser.parse('Dec 25, 2024')\nresult = [dt.month, dt.day]",
        {"ok": True, "value": [12, 25]},
    ),
    
    # ISO with timezone indicator
    (
        "iso-with-z",
        "import dateparser\ndt = dateparser.parse('2024-01-15T14:30:00Z')\nresult = [dt.year, dt.month, dt.day, dt.hour, dt.minute]",
        {"ok": True, "value": [2024, 1, 15, 14, 30]},
    ),
    
    # Partial dates (year/month only)
    (
        "partial-year-month",
        "import dateparser\nfrom datetime import datetime\ndt = dateparser.parse('January 2024', settings={'RELATIVE_BASE': datetime(2024, 6, 1)})\nresult = [dt.year, dt.month, dt.day]",
        {"ok": True, "value": [2024, 1, 1]},
    ),
    (
        "partial-year-only",
        "import dateparser\ndt = dateparser.parse('2024')\nresult = dt is not None",
        {"ok": True, "value": True},
    ),
    
    # More relative dates
    (
        "relative-next-week",
        "import dateparser\nfrom datetime import datetime\nbase = datetime(2024, 1, 15, 12, 0, 0)\ndt = dateparser.parse('in 1 week', settings={'RELATIVE_BASE': base})\nresult = [dt.year, dt.month, dt.day]",
        {"ok": True, "value": [2024, 1, 22]},
    ),
    (
        "relative-last-month",
        "import dateparser\nfrom datetime import datetime\nbase = datetime(2024, 3, 15, 12, 0, 0)\ndt = dateparser.parse('2 months ago', settings={'RELATIVE_BASE': base})\nresult = [dt.year, dt.month, dt.day]",
        {"ok": True, "value": [2024, 1, 15]},
    ),
    
    # Day of week
    (
        "format-day-name",
        "import dateparser\nfrom datetime import datetime\nbase = datetime(2024, 1, 15, 12, 0, 0)\ndt = dateparser.parse('Monday', settings={'RELATIVE_BASE': base})\nresult = dt is not None",
        {"ok": True, "value": True},
    ),
    
    # Date with spaces
    (
        "format-spaces",
        "import dateparser\ndt = dateparser.parse('15   January   2024')\nresult = [dt.day, dt.month, dt.year]",
        {"ok": True, "value": [15, 1, 2024]},
    ),
    
    # Zero-padded dates
    (
        "format-zero-pad",
        "import dateparser\ndt = dateparser.parse('2024-01-05')\nresult = [dt.month, dt.day]",
        {"ok": True, "value": [1, 5]},
    ),
    (
        "format-no-zero-pad",
        "import dateparser\ndt = dateparser.parse('2024-1-5')\nresult = [dt.month, dt.day]",
        {"ok": True, "value": [1, 5]},
    ),
    
    # Return type verification
    (
        "return-type-datetime",
        "import dateparser\nfrom datetime import datetime\ndt = dateparser.parse('2024-01-15')\nresult = isinstance(dt, datetime)",
        {"ok": True, "value": True},
    ),
    (
        "return-none-type",
        "import dateparser\ndt = dateparser.parse('invalid')\nresult = dt is None",
        {"ok": True, "value": True},
    ),
    
    # Package version
    (
        "package-version",
        "import dateparser\nresult = hasattr(dateparser, '__version__')",
        {"ok": True, "value": True},
    ),
    
    # Additional date formats
    (
        "format-day-month",
        "import dateparser\ndt = dateparser.parse('15 January', settings={'RELATIVE_BASE': __import__('datetime').datetime(2024, 1, 1)})\nresult = [dt.day, dt.month]",
        {"ok": True, "value": [15, 1]},
    ),
    
    # Minutes and hours in relative
    (
        "relative-minutes",
        "import dateparser\nfrom datetime import datetime\nbase = datetime(2024, 1, 15, 12, 30, 0)\ndt = dateparser.parse('10 minutes ago', settings={'RELATIVE_BASE': base})\nresult = [dt.hour, dt.minute]",
        {"ok": True, "value": [12, 20]},
    ),
    
    # Different years
    (
        "year-2023",
        "import dateparser\ndt = dateparser.parse('2023-06-15')\nresult = [dt.year, dt.month, dt.day]",
        {"ok": True, "value": [2023, 6, 15]},
    ),
    (
        "year-2025",
        "import dateparser\ndt = dateparser.parse('2025-11-20')\nresult = [dt.year, dt.month, dt.day]",
        {"ok": True, "value": [2025, 11, 20]},
    ),
    
    # Compact ISO format
    (
        "iso-compact",
        "import dateparser\ndt = dateparser.parse('20240115')\nresult = dt is None",
        {"ok": True, "value": True},
    ),
    
    # More edge month/day combinations
    (
        "date-feb-28",
        "import dateparser\ndt = dateparser.parse('2024-02-28')\nresult = [dt.month, dt.day]",
        {"ok": True, "value": [2, 28]},
    ),
    (
        "date-apr-30",
        "import dateparser\ndt = dateparser.parse('2024-04-30')\nresult = [dt.month, dt.day]",
        {"ok": True, "value": [4, 30]},
    ),
    
    # Case sensitivity
    (
        "format-lowercase-month",
        "import dateparser\ndt = dateparser.parse('january 15, 2024')\nresult = [dt.month, dt.day]",
        {"ok": True, "value": [1, 15]},
    ),
    (
        "format-uppercase-month",
        "import dateparser\ndt = dateparser.parse('JANUARY 15, 2024')\nresult = [dt.month, dt.day]",
        {"ok": True, "value": [1, 15]},
    ),
    (
        "relative-in-hours",
        "import dateparser\nfrom datetime import datetime\nbase = datetime(2024, 1, 15, 10, 0, 0)\ndt = dateparser.parse('in 2 hours', settings={'RELATIVE_BASE': base})\nresult = [dt.hour]",
        {"ok": True, "value": [12]},
    ),
    (
        "format-month-year-word",
        "import dateparser\ndt = dateparser.parse('Feb 2024')\nresult = [dt.month, dt.year]",
        {"ok": True, "value": [2, 2024]},
    ),
    (
        "date-july-fourth",
        "import dateparser\ndt = dateparser.parse('July 4, 2024')\nresult = [dt.month, dt.day, dt.year]",
        {"ok": True, "value": [7, 4, 2024]},
    ),
    (
        "relative-year-ago",
        "import dateparser\nfrom datetime import datetime\nbase = datetime(2024, 6, 15, 12, 0, 0)\ndt = dateparser.parse('1 year ago', settings={'RELATIVE_BASE': base})\nresult = [dt.year, dt.month, dt.day]",
        {"ok": True, "value": [2023, 6, 15]},
    ),
]


def main() -> None:
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
