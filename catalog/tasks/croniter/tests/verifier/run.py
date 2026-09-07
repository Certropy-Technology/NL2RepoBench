"""Private deterministic scenarios for the croniter public contract.

Each scenario runs as the unprivileged candidate in an isolated subprocess and
must be derivable from the public instruction (https://github.com/kiorky/croniter,
v6.2.4, immutable revision 9181ba7de0a91512cb77d537b7e23631ffe4f7e8). The
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
        "basic-import",
        "from croniter import croniter\nresult = [type(croniter).__name__, callable(croniter)]",
        {"ok": True, "value": ["type", True]},
    ),
    (
        "simple-next-iteration",
        "from croniter import croniter\nfrom datetime import datetime\nbase = datetime(2010, 1, 25, 4, 46)\niter = croniter('*/5 * * * *', base)\nn1 = iter.get_next(datetime)\nn2 = iter.get_next(datetime)\nresult = [n1.year, n1.month, n1.day, n1.hour, n1.minute, n2.minute]",
        {"ok": True, "value": [2010, 1, 25, 4, 50, 55]},
    ),
    (
        "backward-iteration",
        "from croniter import croniter\nfrom datetime import datetime\nbase = datetime(2010, 8, 25, 10, 0)\nitr = croniter('0 0 1 * *', base)\np1 = itr.get_prev(datetime)\np2 = itr.get_prev(datetime)\nresult = [p1.month, p1.day, p2.month, p2.day]",
        {"ok": True, "value": [8, 1, 7, 1]},
    ),
    (
        "validation-valid",
        "from croniter import croniter\nresult = [croniter.is_valid('0 0 1 * *'), croniter.is_valid('*/15 * * * *'), croniter.is_valid('0 9 * * MON-FRI')]",
        {"ok": True, "value": [True, True, True]},
    ),
    (
        "validation-invalid",
        "from croniter import croniter\nresult = [croniter.is_valid('0 wrong_value 1 * *'), croniter.is_valid('60 * * * *'), croniter.is_valid('not a cron')]",
        {"ok": True, "value": [False, False, False]},
    ),
    (
        "validation-strict-mode",
        "from croniter import croniter\nresult = [croniter.is_valid('0 0 31 2 *'), croniter.is_valid('0 0 31 2 *', strict=True)]",
        {"ok": True, "value": [True, False]},
    ),
    (
        "return-type-float",
        "from croniter import croniter\nfrom datetime import datetime\nbase = datetime(2010, 1, 1, 0, 0)\niter = croniter('0 0 * * *', base, ret_type=float)\nn = iter.get_next()\nresult = [type(n).__name__, n > 1262304000]",
        {"ok": True, "value": ["float", True]},
    ),
    (
        "get-current",
        "from croniter import croniter\nfrom datetime import datetime\nbase = datetime(2010, 1, 1, 0, 0)\niter = croniter('0 0 * * *', base)\niter.get_next(datetime)\nc = iter.get_current(datetime)\nresult = [c.year, c.month, c.day]",
        {"ok": True, "value": [2010, 1, 2]},
    ),
    (
        "set-current",
        "from croniter import croniter\nfrom datetime import datetime\nbase = datetime(2010, 1, 1, 0, 0)\niter = croniter('0 0 * * *', base)\niter.set_current(datetime(2020, 6, 15, 0, 0))\nn = iter.get_next(datetime)\nresult = [n.year, n.month, n.day]",
        {"ok": True, "value": [2020, 6, 16]},
    ),
    (
        "match-method",
        "from croniter import croniter\nfrom datetime import datetime\nresult = [croniter.match('*/5 * * * *', datetime(2024, 1, 1, 10, 30)), croniter.match('*/5 * * * *', datetime(2024, 1, 1, 10, 31))]",
        {"ok": True, "value": [True, False]},
    ),
    (
        "croniter-range",
        "from croniter import croniter_range\nfrom datetime import datetime\nstart = datetime(2024, 1, 1, 9, 0)\nstop = datetime(2024, 1, 1, 9, 30)\nresults = list(croniter_range(start, stop, '*/10 * * * *'))\nresult = [len(results), results[0].minute if results else None, results[-1].minute if results else None]",
        {"ok": True, "value": [4, 0, 30]},
    ),
    (
        "six-field-with-seconds",
        "from croniter import croniter\nfrom datetime import datetime\nbase = datetime(2010, 1, 1, 0, 0, 0)\niter = croniter('30 */5 * * * *', base)\nn = iter.get_next(datetime)\nresult = [n.minute, n.second]",
        {"ok": True, "value": [0, 30]},
    ),
    (
        "exception-bad-cron",
        "from croniter import croniter, CroniterBadCronError\nfrom datetime import datetime\ntry:\n    croniter('invalid cron', datetime.now())\n    result = 'no_exception'\nexcept CroniterBadCronError:\n    result = 'CroniterBadCronError'",
        {"ok": True, "value": "CroniterBadCronError"},
    ),
    (
        "expand-method",
        "from croniter import croniter\nexp = croniter.expand('*/15 * * * *')\nresult = [type(exp).__name__, len(exp), 0 in exp[0], 15 in exp[0], 30 in exp[0], 45 in exp[0]]",
        {"ok": True, "value": ["tuple", 5, True, True, True, True]},
    ),
    (
        "month-weekday-names",
        "from croniter import croniter\nfrom datetime import datetime\nbase = datetime(2024, 1, 1, 9, 0)\niter = croniter('0 9 * JAN-MAR MON-FRI', base)\nn1 = iter.get_next(datetime)\nresult = [n1.month <= 3, n1.weekday() < 5]",
        {"ok": True, "value": [True, True]},
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
