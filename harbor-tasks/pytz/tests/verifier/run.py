from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


CASES = [
    ({"op": "metadata"}, {"version": "2026.3.post1", "olson": "2026c", "utc_identity": True, "has_us_eastern": True, "timezone_count_min": 500}),
    ({"op": "offset", "zone": "UTC", "local": "2024-01-15T12:00:00"}, {"offset_seconds": 0}),
    ({"op": "offset", "zone": "US/Eastern", "local": "2024-07-01T12:00:00"}, {"offset_seconds": -14400}),
    ({"op": "offset", "zone": "US/Eastern", "local": "2024-01-15T12:00:00"}, {"offset_seconds": -18000}),
    ({"op": "offset", "zone": "Europe/London", "local": "2024-07-01T12:00:00"}, {"offset_seconds": 3600}),
    ({"op": "offset", "zone": "Asia/Tokyo", "local": "2024-01-15T12:00:00"}, {"offset_seconds": 32400}),
    ({"op": "localize", "zone": "US/Eastern", "local": "2024-06-01T12:00:00"}, {"offset_seconds": -14400}),
    ({"op": "localize", "zone": "US/Eastern", "local": "2024-11-03T01:30:00", "is_dst": True}, {"offset_seconds": -14400}),
    ({"op": "localize", "zone": "US/Eastern", "local": "2024-11-03T01:30:00", "is_dst": False}, {"offset_seconds": -18000}),
    ({"op": "localize", "zone": "US/Eastern", "local": "2024-11-03T01:30:00", "is_dst": None}, {"error": "AmbiguousTimeError"}),
    ({"op": "localize", "zone": "US/Eastern", "local": "2024-03-10T02:30:00", "is_dst": None}, {"error": "NonExistentTimeError"}),
    ({"op": "normalize", "zone": "US/Eastern", "local": "2024-11-03T01:30:00", "is_dst": True, "hours": 1}, {"offset_seconds": -18000}),
    ({"op": "convert", "source": "US/Eastern", "target": "UTC", "local": "2024-07-01T12:00:00"}, {"offset_seconds": 0, "iso": "2024-07-01T16:00:00+00:00"}),
    ({"op": "fixed", "minutes": 330}, {"zone": "pytz.FixedOffset(330)", "offset_seconds": 19800, "cached": True}),
    ({"op": "unknown", "zone": "Mars/Phobos"}, {"error": "UnknownTimeZoneError"}),
]


def matches(actual: object, expected: dict[str, object]) -> bool:
    if not isinstance(actual, dict):
        return False
    if "timezone_count_min" in expected:
        return actual.get("timezone_count", 0) >= expected["timezone_count_min"] and all(
            actual.get(key) == value for key, value in expected.items() if key != "timezone_count_min"
        )
    return all(actual.get(key) == value for key, value in expected.items())


def main() -> None:
    client = Path("/tests/verifier/client.py")
    site = Path("/tmp/candidate-site")
    leaves = []
    for index, (request, expected) in enumerate(CASES, start=1):
        try:
            completed = subprocess.run(
                [sys.executable, "-I", "-S", str(client), "--site", str(site)],
                input=json.dumps(request),
                text=True,
                capture_output=True,
                timeout=10,
                check=False,
            )
            response = json.loads(completed.stdout.strip()) if completed.returncode == 0 else {}
            passed = bool(response.get("ok")) and matches(response.get("value"), expected)
        except (OSError, subprocess.SubprocessError, json.JSONDecodeError):
            passed = False
        leaves.append({"id": f"pytz-case-{index:02d}", "status": "passed" if passed else "failed"})
    print(json.dumps({"schema_version": "1.0", "leaves": leaves}, sort_keys=True))


if __name__ == "__main__":
    main()
