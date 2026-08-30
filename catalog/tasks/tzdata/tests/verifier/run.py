from __future__ import annotations

import json

from nl2repobench.verification.candidate_client import execute_script


SCENARIO = r'''
import importlib
import importlib.metadata
import importlib.resources
from datetime import datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError, available_timezones, reset_tzpath

import tzdata


def observe(zone, stamp):
    value = datetime.fromisoformat(stamp).astimezone(ZoneInfo(zone))
    return [
        value.isoformat(),
        value.tzname(),
        int(value.utcoffset().total_seconds()),
        value.fold,
    ]


distribution = importlib.metadata.distribution("tzdata")
package_root = importlib.resources.files("tzdata")
zone_root = importlib.resources.files("tzdata.zoneinfo")
zones = (package_root / "zones").read_text(encoding="utf-8").splitlines()
selected = [
    "UTC",
    "Etc/GMT+5",
    "America/New_York",
    "America/Edmonton",
    "Africa/Casablanca",
    "Africa/El_Aaiun",
    "America/Coyhaique",
    "America/Asuncion",
    "Asia/Kathmandu",
    "Australia/Lord_Howe",
    "Pacific/Chatham",
]
canonical = [
    "Africa/Cairo",
    "America/Los_Angeles",
    "America/New_York",
    "Asia/Seoul",
    "Australia/Perth",
    "Europe/London",
    "Pacific/Kiritimati",
]
aliases = [
    "Asia/Calcutta",
    "Canada/Mountain",
    "Egypt",
    "Hongkong",
    "Mexico/BajaNorte",
    "US/Eastern",
]
packages = [
    "tzdata.zoneinfo",
    "tzdata.zoneinfo.Africa",
    "tzdata.zoneinfo.America",
    "tzdata.zoneinfo.America.Argentina",
    "tzdata.zoneinfo.Asia",
    "tzdata.zoneinfo.Australia",
    "tzdata.zoneinfo.Europe",
    "tzdata.zoneinfo.Pacific",
]

result = {
    "metadata.version": tzdata.__version__,
    "metadata.iana_version": tzdata.IANA_VERSION,
    "metadata.distribution_name": distribution.metadata["Name"],
    "metadata.distribution_version": distribution.version,
    "metadata.requires": distribution.requires,
    "metadata.requires_python": distribution.metadata.get("Requires-Python"),
    "metadata.license": distribution.metadata.get("License"),
    "zones.count": len(zones),
    "zones.unique": len(set(zones)),
    "zones.nonempty": all(bool(zone) for zone in zones),
    "zones.canonical_members": all(zone in zones for zone in canonical),
    "zones.alias_members": all(zone in zones for zone in aliases),
    "zones.recent_members": all(
        zone in zones for zone in ["America/Coyhaique", "America/Nuuk"]
    ),
    "zones.no_posixrules": "posixrules" not in zones
    and not (zone_root / "posixrules").is_file(),
    "resources.ancillary": all(
        (zone_root / name).is_file()
        for name in [
            "iso3166.tab",
            "leapseconds",
            "tzdata.zi",
            "zone.tab",
            "zone1970.tab",
            "zonenow.tab",
        ]
    ),
    "resources.packages": all(
        importlib.import_module(module).__name__ == module for module in packages
    ),
    "resources.selected_tzif": all(
        (zone_root.joinpath(*zone.split("/")).read_bytes()[:5] == b"TZif2")
        for zone in selected
    ),
    "resources.all_manifest_tzif": all(
        zone_root.joinpath(*zone.split("/")).read_bytes()[:4] == b"TZif"
        for zone in zones
    ),
    "resources.tzdata_zi_version": (zone_root / "tzdata.zi")
    .read_text(encoding="utf-8")
    .splitlines()[0],
}

reset_tzpath([])
ZoneInfo.clear_cache()
result["zoneinfo.available_matches_manifest"] = available_timezones() == set(zones)
try:
    ZoneInfo("Mars/Olympus_Mons")
except ZoneInfoNotFoundError:
    result["zoneinfo.invalid_key"] = "ZoneInfoNotFoundError"
else:
    result["zoneinfo.invalid_key"] = "loaded"
result["zoneinfo.keys"] = [ZoneInfo(zone).key for zone in ["UTC", "US/Eastern"]]

checks = {
    "behavior.utc": ("UTC", "2030-07-15T12:00:00+00:00"),
    "behavior.etc_gmt_plus5": ("Etc/GMT+5", "2030-01-15T12:00:00+00:00"),
    "behavior.etc_gmt_minus9": ("Etc/GMT-9", "2030-01-15T12:00:00+00:00"),
    "behavior.new_york_winter": ("America/New_York", "2024-01-15T12:00:00+00:00"),
    "behavior.new_york_summer": ("America/New_York", "2024-07-15T12:00:00+00:00"),
    "behavior.new_york_fold_first": ("America/New_York", "2024-11-03T05:30:00+00:00"),
    "behavior.new_york_fold_second": ("America/New_York", "2024-11-03T06:30:00+00:00"),
    "behavior.london_winter": ("Europe/London", "2024-01-15T12:00:00+00:00"),
    "behavior.london_summer": ("Europe/London", "2024-07-15T12:00:00+00:00"),
    "behavior.kathmandu_1970": ("Asia/Kathmandu", "1970-01-01T00:00:00+00:00"),
    "behavior.kathmandu_current": ("Asia/Kathmandu", "2024-01-15T12:00:00+00:00"),
    "behavior.lord_howe_summer": ("Australia/Lord_Howe", "2024-01-15T12:00:00+00:00"),
    "behavior.lord_howe_winter": ("Australia/Lord_Howe", "2024-07-15T12:00:00+00:00"),
    "behavior.chatham_summer": ("Pacific/Chatham", "2024-01-15T12:00:00+00:00"),
    "behavior.chatham_winter": ("Pacific/Chatham", "2024-07-15T12:00:00+00:00"),
    "behavior.edmonton_before_2026c_switch": ("America/Edmonton", "2026-11-01T07:59:59+00:00"),
    "behavior.edmonton_at_2026c_switch": ("America/Edmonton", "2026-11-01T08:00:00+00:00"),
    "behavior.edmonton_future_winter": ("America/Edmonton", "2030-01-15T12:00:00+00:00"),
    "behavior.edmonton_future_summer": ("America/Edmonton", "2030-07-15T12:00:00+00:00"),
    "behavior.canada_mountain_alias": ("Canada/Mountain", "2030-01-15T12:00:00+00:00"),
    "behavior.casablanca_before_2026c_switch": ("Africa/Casablanca", "2026-09-20T00:59:59+00:00"),
    "behavior.casablanca_at_2026c_switch": ("Africa/Casablanca", "2026-09-20T01:00:00+00:00"),
    "behavior.casablanca_fold_end": ("Africa/Casablanca", "2026-09-20T02:00:00+00:00"),
    "behavior.casablanca_future_winter": ("Africa/Casablanca", "2030-01-15T12:00:00+00:00"),
    "behavior.casablanca_future_summer": ("Africa/Casablanca", "2030-07-15T12:00:00+00:00"),
    "behavior.el_aaiun_at_2026c_switch": ("Africa/El_Aaiun", "2026-09-20T01:00:00+00:00"),
    "behavior.el_aaiun_future": ("Africa/El_Aaiun", "2030-07-15T12:00:00+00:00"),
    "behavior.coyhaique_2024_winter": ("America/Coyhaique", "2024-07-15T12:00:00+00:00"),
    "behavior.coyhaique_future": ("America/Coyhaique", "2030-07-15T12:00:00+00:00"),
    "behavior.asuncion_2024_winter": ("America/Asuncion", "2024-07-15T12:00:00+00:00"),
    "behavior.asuncion_future": ("America/Asuncion", "2030-07-15T12:00:00+00:00"),
}
for key, (zone, stamp) in checks.items():
    result[key] = observe(zone, stamp)
'''


EXPECTED = {
    "metadata.version": "2026.3",
    "metadata.iana_version": "2026c",
    "metadata.distribution_name": "tzdata",
    "metadata.distribution_version": "2026.3",
    "metadata.requires": None,
    "metadata.requires_python": ">=2",
    "metadata.license": "Apache-2.0",
    "zones.count": 598,
    "zones.unique": 598,
    "zones.nonempty": True,
    "zones.canonical_members": True,
    "zones.alias_members": True,
    "zones.recent_members": True,
    "zones.no_posixrules": True,
    "resources.ancillary": True,
    "resources.packages": True,
    "resources.selected_tzif": True,
    "resources.all_manifest_tzif": True,
    "resources.tzdata_zi_version": "# version 2026c",
    "zoneinfo.available_matches_manifest": True,
    "zoneinfo.invalid_key": "ZoneInfoNotFoundError",
    "zoneinfo.keys": ["UTC", "US/Eastern"],
    "behavior.utc": ["2030-07-15T12:00:00+00:00", "UTC", 0, 0],
    "behavior.etc_gmt_plus5": ["2030-01-15T07:00:00-05:00", "-05", -18000, 0],
    "behavior.etc_gmt_minus9": ["2030-01-15T21:00:00+09:00", "+09", 32400, 0],
    "behavior.new_york_winter": ["2024-01-15T07:00:00-05:00", "EST", -18000, 0],
    "behavior.new_york_summer": ["2024-07-15T08:00:00-04:00", "EDT", -14400, 0],
    "behavior.new_york_fold_first": ["2024-11-03T01:30:00-04:00", "EDT", -14400, 0],
    "behavior.new_york_fold_second": ["2024-11-03T01:30:00-05:00", "EST", -18000, 1],
    "behavior.london_winter": ["2024-01-15T12:00:00+00:00", "GMT", 0, 0],
    "behavior.london_summer": ["2024-07-15T13:00:00+01:00", "BST", 3600, 0],
    "behavior.kathmandu_1970": ["1970-01-01T05:30:00+05:30", "+0530", 19800, 0],
    "behavior.kathmandu_current": ["2024-01-15T17:45:00+05:45", "+0545", 20700, 0],
    "behavior.lord_howe_summer": ["2024-01-15T23:00:00+11:00", "+11", 39600, 0],
    "behavior.lord_howe_winter": ["2024-07-15T22:30:00+10:30", "+1030", 37800, 0],
    "behavior.chatham_summer": ["2024-01-16T01:45:00+13:45", "+1345", 49500, 0],
    "behavior.chatham_winter": ["2024-07-16T00:45:00+12:45", "+1245", 45900, 0],
    "behavior.edmonton_before_2026c_switch": ["2026-11-01T01:59:59-06:00", "MDT", -21600, 0],
    "behavior.edmonton_at_2026c_switch": ["2026-11-01T02:00:00-06:00", "CST", -21600, 0],
    "behavior.edmonton_future_winter": ["2030-01-15T06:00:00-06:00", "CST", -21600, 0],
    "behavior.edmonton_future_summer": ["2030-07-15T06:00:00-06:00", "CST", -21600, 0],
    "behavior.canada_mountain_alias": ["2030-01-15T06:00:00-06:00", "CST", -21600, 0],
    "behavior.casablanca_before_2026c_switch": ["2026-09-20T01:59:59+01:00", "+01", 3600, 0],
    "behavior.casablanca_at_2026c_switch": ["2026-09-20T01:00:00+00:00", "+00", 0, 1],
    "behavior.casablanca_fold_end": ["2026-09-20T02:00:00+00:00", "+00", 0, 0],
    "behavior.casablanca_future_winter": ["2030-01-15T12:00:00+00:00", "+00", 0, 0],
    "behavior.casablanca_future_summer": ["2030-07-15T12:00:00+00:00", "+00", 0, 0],
    "behavior.el_aaiun_at_2026c_switch": ["2026-09-20T01:00:00+00:00", "+00", 0, 1],
    "behavior.el_aaiun_future": ["2030-07-15T12:00:00+00:00", "+00", 0, 0],
    "behavior.coyhaique_2024_winter": ["2024-07-15T08:00:00-04:00", "-04", -14400, 0],
    "behavior.coyhaique_future": ["2030-07-15T09:00:00-03:00", "-03", -10800, 0],
    "behavior.asuncion_2024_winter": ["2024-07-15T08:00:00-04:00", "-04", -14400, 0],
    "behavior.asuncion_future": ["2030-07-15T09:00:00-03:00", "-03", -10800, 0],
}


def main() -> None:
    candidate = execute_script(SCENARIO, timeout_sec=60.0)
    if not candidate.ok or not isinstance(candidate.value, dict):
        detail = candidate.exception_message or candidate.exception_type or "invalid response"
        leaves = [
            {"id": leaf_id, "status": "failed", "message": detail[-1000:]}
            for leaf_id in EXPECTED
        ]
    else:
        observed = candidate.value
        leaves = []
        for leaf_id, expected in EXPECTED.items():
            actual = observed.get(leaf_id, "<missing>")
            if actual == expected:
                leaves.append({"id": leaf_id, "status": "passed"})
            else:
                leaves.append(
                    {
                        "id": leaf_id,
                        "status": "failed",
                        "message": f"expected {expected!r}, got {actual!r}"[:1000],
                    }
                )
    print(json.dumps({"schema_version": "1.0", "leaves": leaves}, sort_keys=True))


if __name__ == "__main__":
    main()
