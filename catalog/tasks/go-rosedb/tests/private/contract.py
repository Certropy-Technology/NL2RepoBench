import json
import subprocess
import sys


bridge, proxy = sys.argv[1:]


def call(operation):
    request = json.dumps({"operation": operation, "args": []}, separators=(",", ":"))
    completed = subprocess.run(
        [proxy, bridge], input=request + "\n", text=True,
        capture_output=True, check=False, timeout=8,
    )
    if completed.returncode != 0:
        raise AssertionError(f"bridge exit {completed.returncode}: {completed.stderr}")
    lines = completed.stdout.splitlines()
    if len(lines) != 1:
        raise AssertionError(f"expected one response, got {completed.stdout!r}")
    response = json.loads(lines[0])
    if "error_type" in response:
        raise AssertionError(f"bridge error: {response}")
    expected = operation + "-ok"
    if response.get("value") != expected:
        raise AssertionError(f"{operation}: expected {expected!r}, got {response!r}")


for operation in ("basic", "batch", "iterator", "ttl", "scans", "watch"):
    call(operation)

print(json.dumps({"operation": "public-api", "status": "passed"}, separators=(",", ":")))
