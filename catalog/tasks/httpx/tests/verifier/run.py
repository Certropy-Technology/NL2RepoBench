"""Emit the fixed MockTransport slice as the custom-json-v1 verifier report."""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

EXPECTED_TOTAL = 24
TESTS = Path("/tests/verifier/tests/test_mocktransport_slice.py")


def main() -> int:
    candidate = Path("/workspace").resolve()
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))
    with tempfile.TemporaryDirectory(prefix="httpx-verifier-") as temporary:
        junit = Path(temporary) / "junit.xml"
        command = [
            sys.executable,
            "-m",
            "pytest",
            "-q",
            "-o",
            "addopts=",
            str(TESTS),
            f"--junitxml={junit}",
        ]
        environment = os.environ.copy()
        environment["PYTHONPATH"] = os.pathsep.join(
            ["/tmp/candidate-site", str(candidate), "/opt/candidate-dependencies/site", environment.get("PYTHONPATH", "")]
        )
        result = subprocess.run(command, cwd=candidate, env=environment, capture_output=True, text=True, timeout=180.0)
        leaves: list[dict[str, str]] = []
        if junit.is_file():
            root = ET.parse(junit).getroot()
            for case in root.iter("testcase"):
                status = "passed"
                if case.find("skipped") is not None:
                    status = "skipped"
                elif case.find("failure") is not None or case.find("error") is not None:
                    status = "failed"
                leaves.append({"id": case.attrib.get("classname", "") + "::" + case.attrib.get("name", ""), "status": status})
        if len(leaves) != EXPECTED_TOTAL or len({leaf["id"] for leaf in leaves}) != EXPECTED_TOTAL:
            leaves = [{"id": f"mocktransport-{index:02d}", "status": "failed"} for index in range(EXPECTED_TOTAL)]
        if result.returncode not in (0, 1):
            leaves = [{"id": leaf["id"], "status": "failed"} for leaf in leaves]
        print(json.dumps({"schema_version": "1.0", "leaves": leaves}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
