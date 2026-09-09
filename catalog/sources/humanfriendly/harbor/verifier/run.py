#!/usr/bin/env python3
"""
Custom JSON v1 verifier for humanfriendly package.
Tests format_size, parse_size, format_timespan, parse_timespan, format_number,
format_length, parse_length, pluralize, concatenate, coerce_boolean, round_number, format_table.
"""
import json
import sys
from nl2repobench.verification.candidate_client import execute_script

CASES = [
    # format_size tests (13)
    ("format_size_0", "from humanfriendly import format_size\nresult = format_size(0)", {"ok": True, "value": "0 bytes"}),
    ("format_size_1", "from humanfriendly import format_size\nresult = format_size(1)", {"ok": True, "value": "1 byte"}),
    ("format_size_5", "from humanfriendly import format_size\nresult = format_size(5)", {"ok": True, "value": "5 bytes"}),
    ("format_size_1000", "from humanfriendly import format_size\nresult = format_size(1000)", {"ok": True, "value": "1 KB"}),
    ("format_size_1024", "from humanfriendly import format_size\nresult = format_size(1024)", {"ok": True, "value": "1.02 KB"}),
    ("format_size_1024_binary", "from humanfriendly import format_size\nresult = format_size(1024, binary=True)", {"ok": True, "value": "1 KiB"}),
    ("format_size_1000_3_mul_4", "from humanfriendly import format_size\nresult = format_size(1000 ** 3 * 4)", {"ok": True, "value": "4 GB"}),
    ("format_size_megabytes", "from humanfriendly import format_size\nresult = format_size(1000000)", {"ok": True, "value": "1 MB"}),
    ("format_size_gigabytes", "from humanfriendly import format_size\nresult = format_size(5000000000)", {"ok": True, "value": "5 GB"}),
    ("format_size_terabytes", "from humanfriendly import format_size\nresult = format_size(2000000000000)", {"ok": True, "value": "2 TB"}),
    ("format_size_keep_width", "from humanfriendly import format_size\nresult = format_size(1500, keep_width=True)", {"ok": True, "value": "1.50 KB"}),
    ("format_size_binary_mib", "from humanfriendly import format_size\nresult = format_size(1024**2, binary=True)", {"ok": True, "value": "1 MiB"}),
    ("format_size_large", "from humanfriendly import format_size\nresult = format_size(123456789)", {"ok": True, "value": "123.46 MB"}),
    
    # parse_size tests (11)
    ("parse_size_0_bytes", "from humanfriendly import parse_size\nresult = parse_size('0 bytes')", {"ok": True, "value": 0}),
    ("parse_size_1_byte", "from humanfriendly import parse_size\nresult = parse_size('1 byte')", {"ok": True, "value": 1}),
    ("parse_size_5_KB", "from humanfriendly import parse_size\nresult = parse_size('5 KB')", {"ok": True, "value": 5000}),
    ("parse_size_1_MB", "from humanfriendly import parse_size\nresult = parse_size('1 MB')", {"ok": True, "value": 1000000}),
    ("parse_size_2_GB", "from humanfriendly import parse_size\nresult = parse_size('2 GB')", {"ok": True, "value": 2000000000}),
    ("parse_size_1_TB", "from humanfriendly import parse_size\nresult = parse_size('1 TB')", {"ok": True, "value": 1000000000000}),
    ("parse_size_1_KiB_binary", "from humanfriendly import parse_size\nresult = parse_size('1 KiB', binary=True)", {"ok": True, "value": 1024}),
    ("parse_size_1_MiB_binary", "from humanfriendly import parse_size\nresult = parse_size('1 MiB', binary=True)", {"ok": True, "value": 1048576}),
    ("parse_size_decimal_kb", "from humanfriendly import parse_size\nresult = parse_size('1.5 KB')", {"ok": True, "value": 1500}),
    ("parse_size_no_space", "from humanfriendly import parse_size\nresult = parse_size('5KB')", {"ok": True, "value": 5000}),
    ("parse_size_invalid", "from humanfriendly import parse_size, InvalidSize\ntry:\n    result = parse_size('invalid')\nexcept InvalidSize:\n    result = 'InvalidSize'", {"ok": True, "value": "InvalidSize"}),
    
    # format_timespan tests (13)
    ("format_timespan_0", "from humanfriendly import format_timespan\nresult = format_timespan(0)", {"ok": True, "value": "0 seconds"}),
    ("format_timespan_1", "from humanfriendly import format_timespan\nresult = format_timespan(1)", {"ok": True, "value": "1 second"}),
    ("format_timespan_60", "from humanfriendly import format_timespan\nresult = format_timespan(60)", {"ok": True, "value": "1 minute"}),
    ("format_timespan_3600", "from humanfriendly import format_timespan\nresult = format_timespan(3600)", {"ok": True, "value": "1 hour"}),
    ("format_timespan_86400", "from humanfriendly import format_timespan\nresult = format_timespan(86400)", {"ok": True, "value": "1 day"}),
    ("format_timespan_90", "from humanfriendly import format_timespan\nresult = format_timespan(90)", {"ok": True, "value": "1 minute and 30 seconds"}),
    ("format_timespan_3661", "from humanfriendly import format_timespan\nresult = format_timespan(3661)", {"ok": True, "value": "1 hour, 1 minute and 1 second"}),
    ("format_timespan_detailed", "from humanfriendly import format_timespan\nresult = format_timespan(3661, detailed=True)", {"ok": True, "value": "1 hour, 1 minute and 1 second"}),
    ("format_timespan_max_units", "from humanfriendly import format_timespan\nresult = format_timespan(90061, max_units=2)", {"ok": True, "value": "1 day and 1 hour"}),
    ("format_timespan_float", "from humanfriendly import format_timespan\nresult = format_timespan(1.5)", {"ok": True, "value": "1.5 seconds"}),
    ("format_timespan_week", "from humanfriendly import format_timespan\nresult = format_timespan(604800)", {"ok": True, "value": "1 week"}),
    ("format_timespan_complex", "from humanfriendly import format_timespan\nresult = format_timespan(93784)", {"ok": True, "value": "1 day, 2 hours and 3 minutes"}),
    ("format_timespan_max_units_1", "from humanfriendly import format_timespan\nresult = format_timespan(7265, max_units=1)", {"ok": True, "value": "2 hours"}),
    
    # parse_timespan tests (11)
    ("parse_timespan_0_seconds", "from humanfriendly import parse_timespan\nresult = parse_timespan('0 seconds')", {"ok": True, "value": 0.0}),
    ("parse_timespan_1_second", "from humanfriendly import parse_timespan\nresult = parse_timespan('1 second')", {"ok": True, "value": 1.0}),
    ("parse_timespan_5_minutes", "from humanfriendly import parse_timespan\nresult = parse_timespan('5 minutes')", {"ok": True, "value": 300.0}),
    ("parse_timespan_1_hour", "from humanfriendly import parse_timespan\nresult = parse_timespan('1 hour')", {"ok": True, "value": 3600.0}),
    ("parse_timespan_2_days", "from humanfriendly import parse_timespan\nresult = parse_timespan('2 days')", {"ok": True, "value": 172800.0}),
    ("parse_timespan_1_week", "from humanfriendly import parse_timespan\nresult = parse_timespan('1 week')", {"ok": True, "value": 604800.0}),
    ("parse_timespan_complex", "from humanfriendly import parse_timespan\nresult = parse_timespan('90 minutes')", {"ok": True, "value": 5400.0}),
    ("parse_timespan_abbreviation_m", "from humanfriendly import parse_timespan\nresult = parse_timespan('5m')", {"ok": True, "value": 300.0}),
    ("parse_timespan_abbreviation_h", "from humanfriendly import parse_timespan\nresult = parse_timespan('2h')", {"ok": True, "value": 7200.0}),
    ("parse_timespan_abbreviation_s", "from humanfriendly import parse_timespan\nresult = parse_timespan('30s')", {"ok": True, "value": 30.0}),
    ("parse_timespan_invalid", "from humanfriendly import parse_timespan, InvalidTimespan\ntry:\n    result = parse_timespan('invalid')\nexcept InvalidTimespan:\n    result = 'InvalidTimespan'", {"ok": True, "value": "InvalidTimespan"}),
    
    # format_number tests (7)
    ("format_number_0", "from humanfriendly import format_number\nresult = format_number(0)", {"ok": True, "value": "0"}),
    ("format_number_1234", "from humanfriendly import format_number\nresult = format_number(1234)", {"ok": True, "value": "1,234"}),
    ("format_number_1234567", "from humanfriendly import format_number\nresult = format_number(1234567)", {"ok": True, "value": "1,234,567"}),
    ("format_number_float", "from humanfriendly import format_number\nresult = format_number(1234.56)", {"ok": True, "value": "1,234.56"}),
    ("format_number_decimals", "from humanfriendly import format_number\nresult = format_number(1234.567, num_decimals=3)", {"ok": True, "value": "1,234.567"}),
    ("format_number_large", "from humanfriendly import format_number\nresult = format_number(9876543210)", {"ok": True, "value": "9,876,543,210"}),
    ("format_number_decimals_0", "from humanfriendly import format_number\nresult = format_number(1234.567, num_decimals=0)", {"ok": True, "value": "1,234"}),
    
    # format_length tests (6)
    ("format_length_0", "from humanfriendly import format_length\nresult = format_length(0)", {"ok": True, "value": "0 metres"}),
    ("format_length_1", "from humanfriendly import format_length\nresult = format_length(1)", {"ok": True, "value": "1 metre"}),
    ("format_length_0_5", "from humanfriendly import format_length\nresult = format_length(0.5)", {"ok": True, "value": "50 cm"}),
    ("format_length_1000", "from humanfriendly import format_length\nresult = format_length(1000)", {"ok": True, "value": "1 km"}),
    ("format_length_0_01", "from humanfriendly import format_length\nresult = format_length(0.01)", {"ok": True, "value": "1 cm"}),
    ("format_length_0_001", "from humanfriendly import format_length\nresult = format_length(0.001)", {"ok": True, "value": "1 mm"}),
    
    # parse_length tests (6)
    ("parse_length_1_metre", "from humanfriendly import parse_length\nresult = parse_length('1 metre')", {"ok": True, "value": 1.0}),
    ("parse_length_5_km", "from humanfriendly import parse_length\nresult = parse_length('5 km')", {"ok": True, "value": 5000.0}),
    ("parse_length_100_cm", "from humanfriendly import parse_length\nresult = parse_length('100 cm')", {"ok": True, "value": 1.0}),
    ("parse_length_500_mm", "from humanfriendly import parse_length\nresult = parse_length('500 mm')", {"ok": True, "value": 0.5}),
    ("parse_length_metres_plural", "from humanfriendly import parse_length\nresult = parse_length('2 metres')", {"ok": True, "value": 2.0}),
    ("parse_length_invalid", "from humanfriendly import parse_length, InvalidLength\ntry:\n    result = parse_length('invalid')\nexcept InvalidLength:\n    result = 'InvalidLength'", {"ok": True, "value": "InvalidLength"}),
    
    # pluralize tests (8)
    ("pluralize_0", "from humanfriendly.text import pluralize\nresult = pluralize(0, 'item')", {"ok": True, "value": "0 items"}),
    ("pluralize_1", "from humanfriendly.text import pluralize\nresult = pluralize(1, 'item')", {"ok": True, "value": "1 item"}),
    ("pluralize_2", "from humanfriendly.text import pluralize\nresult = pluralize(2, 'item')", {"ok": True, "value": "2 items"}),
    ("pluralize_1_5", "from humanfriendly.text import pluralize\nresult = pluralize(1.5, 'item')", {"ok": True, "value": "1.5 items"}),
    ("pluralize_custom_plural", "from humanfriendly.text import pluralize\nresult = pluralize(2, 'box', 'boxes')", {"ok": True, "value": "2 boxes"}),
    ("pluralize_custom_1", "from humanfriendly.text import pluralize\nresult = pluralize(1, 'box', 'boxes')", {"ok": True, "value": "1 box"}),
    ("pluralize_float_1_0", "from humanfriendly.text import pluralize\nresult = pluralize(1.0, 'item')", {"ok": True, "value": "1.0 item"}),
    ("pluralize_negative", "from humanfriendly.text import pluralize\nresult = pluralize(-1, 'item')", {"ok": True, "value": "-1 items"}),
    
    # concatenate tests (5)
    ("concatenate_empty", "from humanfriendly.text import concatenate\nresult = concatenate([])", {"ok": True, "value": ""}),
    ("concatenate_one", "from humanfriendly.text import concatenate\nresult = concatenate(['apple'])", {"ok": True, "value": "apple"}),
    ("concatenate_two", "from humanfriendly.text import concatenate\nresult = concatenate(['apple', 'banana'])", {"ok": True, "value": "apple and banana"}),
    ("concatenate_three", "from humanfriendly.text import concatenate\nresult = concatenate(['apple', 'banana', 'cherry'])", {"ok": True, "value": "apple, banana and cherry"}),
    ("concatenate_four", "from humanfriendly.text import concatenate\nresult = concatenate(['a', 'b', 'c', 'd'])", {"ok": True, "value": "a, b, c and d"}),
    
    # coerce_boolean tests (11)
    ("coerce_boolean_true_str", "from humanfriendly import coerce_boolean\nresult = coerce_boolean('true')", {"ok": True, "value": True}),
    ("coerce_boolean_false_str", "from humanfriendly import coerce_boolean\nresult = coerce_boolean('false')", {"ok": True, "value": False}),
    ("coerce_boolean_yes", "from humanfriendly import coerce_boolean\nresult = coerce_boolean('yes')", {"ok": True, "value": True}),
    ("coerce_boolean_no", "from humanfriendly import coerce_boolean\nresult = coerce_boolean('no')", {"ok": True, "value": False}),
    ("coerce_boolean_1_str", "from humanfriendly import coerce_boolean\nresult = coerce_boolean('1')", {"ok": True, "value": True}),
    ("coerce_boolean_0_str", "from humanfriendly import coerce_boolean\nresult = coerce_boolean('0')", {"ok": True, "value": False}),
    ("coerce_boolean_on", "from humanfriendly import coerce_boolean\nresult = coerce_boolean('on')", {"ok": True, "value": True}),
    ("coerce_boolean_off", "from humanfriendly import coerce_boolean\nresult = coerce_boolean('off')", {"ok": True, "value": False}),
    ("coerce_boolean_int_1", "from humanfriendly import coerce_boolean\nresult = coerce_boolean(1)", {"ok": True, "value": True}),
    ("coerce_boolean_empty", "from humanfriendly import coerce_boolean\nresult = coerce_boolean('')", {"ok": True, "value": False}),
    ("coerce_boolean_invalid", "from humanfriendly import coerce_boolean\ntry:\n    result = coerce_boolean('maybe')\nexcept ValueError:\n    result = 'ValueError'", {"ok": True, "value": "ValueError"}),
    
    # round_number tests (6)
    ("round_number_1234", "from humanfriendly import round_number\nresult = round_number(1234)", {"ok": True, "value": "1234"}),
    ("round_number_1234_56", "from humanfriendly import round_number\nresult = round_number(1234.56)", {"ok": True, "value": "1234.56"}),
    ("round_number_0_1234", "from humanfriendly import round_number\nresult = round_number(0.1234)", {"ok": True, "value": "0.12"}),
    ("round_number_keep_width", "from humanfriendly import round_number\nresult = round_number(1.5, keep_width=True)", {"ok": True, "value": "1.50"}),
    ("round_number_0", "from humanfriendly import round_number\nresult = round_number(0)", {"ok": True, "value": "0"}),
    ("round_number_large", "from humanfriendly import round_number\nresult = round_number(9876543.21)", {"ok": True, "value": "9876543.21"}),
    
    # format_table tests (3)
    ("format_table_simple", "from humanfriendly.tables import format_pretty_table\nresult = format_pretty_table([['Name', 'Age'], ['Alice', '30'], ['Bob', '25']])", {"ok": True, "value": "---------------\n| Name  | Age |\n| Alice | 30  |\n| Bob   | 25  |\n---------------"}),
    ("format_table_single_row", "from humanfriendly.tables import format_pretty_table\nresult = format_pretty_table([['Header'], ['Value']])", {"ok": True, "value": "----------\n| Header |\n| Value  |\n----------"}),
    ("format_table_wide", "from humanfriendly.tables import format_pretty_table\nresult = format_pretty_table([['A', 'B', 'C'], ['1', '2', '3'], ['4', '5', '6']])", {"ok": True, "value": "-------------\n| A | B | C |\n| 1 | 2 | 3 |\n| 4 | 5 | 6 |\n-------------"}),
]

assert len(CASES) == 100

def main():
    leaves = []
    for test_id, script, expected in CASES:
        result = execute_script(script)
        status = "passed" if result == expected else "failed"
        leaves.append({"id": test_id, "status": status})
    
    output = {
        "schema_version": "1.0",
        "leaves": leaves
    }
    print(json.dumps(output))

if __name__ == "__main__":
    main()
