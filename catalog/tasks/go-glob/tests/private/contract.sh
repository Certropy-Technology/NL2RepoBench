#!/usr/bin/env bash
set -euo pipefail
bridge="$1"
proxy="$2"
python3 -I - "$bridge" "$proxy" <<'PY'
import json
import subprocess
import sys

bridge, proxy = sys.argv[1:]
cases = [
    ("match", ["abc", "", "abc"], {"ok": True, "matched": True}),
    ("match", ["abc", "", "xabc"], {"ok": True, "matched": False}),
    ("match", ["*", "", "anything"], {"ok": True, "matched": True}),
    ("match", ["a?c", "", "abc"], {"ok": True, "matched": True}),
    ("match", ["a?c", "", "ac"], {"ok": True, "matched": False}),
    ("match", ["a*c", "", "a123c"], {"ok": True, "matched": True}),
    ("match", ["*.example.*", ".", "api.example.com"], {"ok": True, "matched": True}),
    ("match", ["*.example.*", ".", "api.deep.example.com"], {"ok": True, "matched": False}),
    ("match", ["**.example.**", ".", "api.deep.example.com"], {"ok": True, "matched": True}),
    ("match", ["a.?.c", ".", "a.b.c"], {"ok": True, "matched": True}),
    ("match", ["a.?.c", ".", "a.bb.c"], {"ok": True, "matched": False}),
    ("match", ["[a-c]at", "", "bat"], {"ok": True, "matched": True}),
    ("match", ["[!a-c]at", "", "fat"], {"ok": True, "matched": True}),
    ("match", ["[abc]at", "", "dat"], {"ok": True, "matched": False}),
    ("match", ["{cat,dog}", "", "dog"], {"ok": True, "matched": True}),
    ("match", ["{cat,dog}", "", "cow"], {"ok": True, "matched": False}),
    ("match", ["{a,ab}c", "", "abc"], {"ok": True, "matched": True}),
    ("match", ["{a,}", "", ""], {"ok": True, "matched": True}),
    ("match", ["{a,{b,c}}", "", "c"], {"ok": True, "matched": True}),
    ("match", ["\\*", "", "*"], {"ok": True, "matched": True}),
    ("match", ["test,pattern", "", "test,pattern"], {"ok": True, "matched": True}),
    ("match", ["*ä", "", "åä"], {"ok": True, "matched": True}),
    ("match", ["a/**/b", "/", "a/x/y/b"], {"ok": True, "matched": True}),
    ("match_info", ["api.*.com", ".", "api.x.com"], {"ok": True, "matched": True, "pattern": "api.*.com", "separators": "."}),
    ("must_match", ["{cat,dog}", "", "cat"], {"matched": True}),
    ("separator_ownership", ["*", "/", "a/b"], {"ok": True, "matched": False, "separators": "#"}),
    ("quote", ["*a?[x]{y}\\"], "\\*a\\?\\[x\\]\\{y\\}\\\\"),
    ("compile_error", ["{a,b"], {"ok": False, "error": "glob: syntax error at 4: unclosed `{`", "reason": "unclosed `{`", "offset": 4}),
    ("compile_error", ["[abc"], {"ok": False, "error": "glob: syntax error at 4: unexpected end of input", "reason": "unexpected end of input", "offset": 4}),
    ("compile_error", ["[c-a]"], {"ok": False, "error": "glob: syntax error at 5: range hi character is less than lo", "reason": "range hi character is less than lo", "offset": 5}),
    ("compile_error", ["a\\"], {"ok": False, "error": "glob: syntax error at 2: trailing backslash", "reason": "trailing backslash", "offset": 2}),
    ("unknown", [], None),
]

requests = [json.dumps({"operation": op, "args": args}, ensure_ascii=False) for op, args, _ in cases]
try:
    completed = subprocess.run(
        [proxy, bridge], input=("\n".join(requests) + "\n").encode("utf-8"),
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=25,
        check=False,
    )
except (OSError, subprocess.TimeoutExpired):
    print(json.dumps({"schema_version": "1.0", "leaves": [{"id": "contract::public-api", "status": "failed", "message": "candidate-call-failed"}]}))
    raise SystemExit(1)

passed = completed.returncode == 0
if passed:
    lines = completed.stdout.decode("utf-8", "replace").splitlines()
    if len(lines) != len(cases):
        passed = False
    else:
        for index, (line, (_, _, expected)) in enumerate(zip(lines, cases)):
            try:
                response = json.loads(line)
            except json.JSONDecodeError:
                passed = False
                break
            if expected is None:
                if response.get("error_type") != "InvalidInput":
                    passed = False
                    break
                continue
            if "value" not in response or response["value"] != expected:
                print("case", index, "got", response.get("value"), "want", expected, file=sys.stderr)
                passed = False
                break

report = {
    "schema_version": "1.0",
    "framework": "go",
    "report_format": "go-test-json-v1",
    "collected": 1,
    "tests": [{"test_id": "contract::public-api", "status": "passed" if passed else "failed", "duration_ms": 0}],
    "collection_errors": [],
    "runner_exit_code": 0 if passed else 1,
}
print(json.dumps(report, sort_keys=True))
raise SystemExit(0 if passed else 1)
PY
