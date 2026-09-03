import json
import subprocess
import sys


bridge, proxy = sys.argv[1:]


def call(operation, args):
    request = json.dumps({"operation": operation, "args": args}, separators=(",", ":"))
    completed = subprocess.run(
        [proxy, bridge], input=request + "\n", text=True,
        capture_output=True, check=False, timeout=8,
    )
    assert completed.returncode == 0, completed.stderr
    lines = completed.stdout.splitlines()
    assert len(lines) == 1, completed.stdout
    response = json.loads(lines[0])
    assert "error_type" not in response, response
    return response["value"]


def expect_error(operation, args):
    request = json.dumps({"operation": operation, "args": args}, separators=(",", ":"))
    completed = subprocess.run(
        [proxy, bridge], input=request + "\n", text=True,
        capture_output=True, check=False, timeout=8,
    )
    assert completed.returncode == 0, completed.stderr
    response = json.loads(completed.stdout)
    assert response.get("error_type") in {"InvalidInput", "CallFailed"}, response


def check_standard_parser_and_next_times():
    value = call("parse_next", ["*/15 * * * *", "2025-03-08T10:07:12Z", [], "UTC"])
    assert value["kind"] == "spec"
    assert value["next"] == "2025-03-08T10:15:00Z"
    assert value["fields"][1] == (1 << 0) | (1 << 15) | (1 << 30) | (1 << 45)

    weekday = call("parse_next", ["0 0 * * 1-5", "2025-03-07T10:00:00Z", [], "UTC"])
    assert weekday["next"] == "2025-03-10T00:00:00Z"

    named = call("parse_next", ["30 9 * JAN,MAR MON-FRI", "2025-01-01T09:29:59Z", [], "UTC"])
    assert named["next"] == "2025-01-01T09:30:00Z"

    expect_error("parse_next", ["0 0 * *", "2025-01-01T00:00:00Z", [], "UTC"])
    expect_error("parse_next", ["0 99 * * *", "2025-01-01T00:00:00Z", [], "UTC"])
    expect_error("parse_next", ["0 0 * * *", "2025-01-01T00:00:00Z", ["unknown"], "UTC"])


def check_descriptors_and_timezones():
    hourly = call("parse_next", ["@hourly", "2025-03-08T10:07:12Z", [], "UTC"])
    assert hourly["next"] == "2025-03-08T11:00:00Z"
    assert hourly["kind"] == "spec"

    every = call("parse_next", ["@every 1m30s", "2025-03-08T10:07:12.123Z", [], "UTC"])
    assert every["kind"] == "constant-delay" and every["delay_ns"] == 90_000_000_000
    assert every["next"] == "2025-03-08T10:08:42Z"

    tokyo = call("parse_next", ["0 9 * * *", "2025-03-08T00:00:00Z", [], "Asia/Tokyo"])
    assert tokyo["next"] == "2025-03-09T09:00:00+09:00"

    ny = call("parse_next", ["CRON_TZ=America/New_York 0 9 * * *", "2025-03-08T13:00:00Z", [], "UTC"])
    assert ny["next"] == "2025-03-08T14:00:00Z"
    assert ny["location"] == "America/New_York"

    expect_error("parse_next", ["@not-a-schedule", "2025-01-01T00:00:00Z", [], "UTC"])
    expect_error("parse_next", ["TZ=No/Such 0 0 * * *", "2025-01-01T00:00:00Z", [], "UTC"])


def check_custom_parser_options():
    seconds = call(
        "parse_next",
        ["*/10 * * * * *", "2025-03-08T10:07:12Z", ["Second", "Minute", "Hour", "Dom", "Month", "Dow", "Descriptor"], "UTC"],
    )
    assert seconds["next"] == "2025-03-08T10:07:20Z"
    assert seconds["fields"][0] == sum(1 << i for i in range(0, 60, 10))

    optional_seconds = call(
        "parse_next",
        ["0 12 * * *", "2025-03-08T10:07:12Z", ["SecondOptional", "Minute", "Hour", "Dom", "Month", "Dow", "Descriptor"], "UTC"],
    )
    assert optional_seconds["next"] == "2025-03-08T12:00:00Z"

    optional_dow = call(
        "parse_next",
        ["0 12 1 *", "2025-03-08T10:07:12Z", ["Minute", "Hour", "Dom", "Month", "DowOptional"], "UTC"],
    )
    assert optional_dow["next"] == "2025-04-01T12:00:00Z"


def check_every_and_cron_entries():
    short = call("every_next", ["250ms", "2025-03-08T10:07:12.900Z"])
    assert short["delay_ns"] == 1_000_000_000 and short["next"] == "2025-03-08T10:07:13Z"
    fractional = call("every_next", ["2.75s", "2025-03-08T10:07:12.900Z"])
    assert fractional["delay_ns"] == 2_000_000_000 and fractional["next"] == "2025-03-08T10:07:14Z"
    expect_error("every_next", ["nonsense", "2025-03-08T10:07:12Z"])

    entries = call("cron_entries", ["Europe/Berlin", ["0 0 * * *", "@hourly"], False])
    assert entries["location"] == "Europe/Berlin"
    assert entries["ids"] == [1, 2] and entries["before"] == 2 and entries["after_remove"] == 1
    assert entries["lookup_valid"] == [True, True, False] and entries["removed"] is True

    seconds = call("cron_entries", ["UTC", ["0 * * * * *"], True])
    assert seconds["ids"] == [1] and seconds["after_remove"] == 0
    expect_error("cron_entries", ["UTC", ["bad spec"], False])


def check_wrappers():
    recovered = call("chain_recover", [])
    assert recovered == {"infos": 0, "errors": 1}

    skipped = call("chain_skip", [])
    assert skipped["count"] == 1 and skipped["infos"] == 1 and skipped["errors"] == 0

    delayed = call("chain_delay", [])
    assert delayed["count"] == 2 and delayed["errors"] == 0


check_standard_parser_and_next_times()
check_descriptors_and_timezones()
check_custom_parser_options()
check_every_and_cron_entries()
check_wrappers()
print(json.dumps({"operation": "public-api", "status": "passed"}, separators=(",", ":")))
