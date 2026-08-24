#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--site", required=True)
    args = parser.parse_args()
    sys.path.insert(0, args.site)
    import pytz

    request = json.load(sys.stdin)
    op = request["op"]
    if op == "metadata":
        value = {"version": pytz.__version__, "olson": pytz.OLSON_VERSION, "utc_identity": pytz.timezone("UTC") is pytz.utc, "has_us_eastern": "US/Eastern" in pytz.all_timezones_set, "timezone_count": len(pytz.all_timezones)}
    elif op == "offset":
        zone = pytz.timezone(request["zone"])
        local = zone.localize(dt.datetime.fromisoformat(request["local"]))
        value = {"iso": local.isoformat(), "offset_seconds": int(local.utcoffset().total_seconds()), "tzname": local.tzname()}
    elif op == "localize":
        zone = pytz.timezone(request["zone"])
        try:
            local = zone.localize(dt.datetime.fromisoformat(request["local"]), is_dst=request.get("is_dst", False))
            value = {"iso": local.isoformat(), "offset_seconds": int(local.utcoffset().total_seconds())}
        except Exception as exc:
            value = {"error": type(exc).__name__}
    elif op == "normalize":
        zone = pytz.timezone(request["zone"])
        local = zone.localize(dt.datetime.fromisoformat(request["local"]), is_dst=request["is_dst"])
        normalized = zone.normalize(local + dt.timedelta(hours=request["hours"]))
        value = {"iso": normalized.isoformat(), "offset_seconds": int(normalized.utcoffset().total_seconds())}
    elif op == "convert":
        source = pytz.timezone(request["source"])
        target = pytz.timezone(request["target"])
        converted = source.localize(dt.datetime.fromisoformat(request["local"])).astimezone(target)
        value = {"iso": converted.isoformat(), "offset_seconds": int(converted.utcoffset().total_seconds())}
    elif op == "fixed":
        fixed = pytz.FixedOffset(request["minutes"])
        value = {"zone": str(fixed), "offset_seconds": int(fixed.utcoffset(None).total_seconds()), "cached": fixed is pytz.FixedOffset(request["minutes"])}
    elif op == "unknown":
        try:
            pytz.timezone(request["zone"])
            value = {"error": "missing"}
        except Exception as exc:
            value = {"error": type(exc).__name__}
    else:
        raise ValueError(f"unknown operation: {op}")
    print(json.dumps({"ok": True, "value": value}, sort_keys=True))

if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(json.dumps({"ok": False, "error": type(exc).__name__, "message": str(exc)}, sort_keys=True))
        raise SystemExit(0)
