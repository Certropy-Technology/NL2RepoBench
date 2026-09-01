"""Run trusted Go contract assertions while proxying candidate calls safely."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import tempfile
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--script", type=Path, required=True)
    parser.add_argument("--bridge", type=Path, required=True)
    parser.add_argument("--proxy", type=Path, required=True)
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix="nl2repo-go-contract-") as temp:
        proxy = Path(temp) / "bridge-proxy"
        proxy.write_text(
            "#!/usr/bin/python3\n"
            "import runpy, sys\n"
            f"sys.argv = [{str(args.proxy)!r}, *sys.argv[1:]]\n"
            f"runpy.run_path({str(args.proxy)!r}, run_name='__main__')\n",
            encoding="utf-8",
        )
        os.chmod(proxy, 0o555)
        result = subprocess.run(
            ["/bin/bash", str(args.script), str(args.bridge), str(proxy)],
            capture_output=True,
            text=True,
            check=False,
            timeout=35.0,
        )
        print(result.stdout, end="")
        print(result.stderr, end="", file=sys.stderr)
        if result.returncode != 0 and not result.stderr:
            print(
                f"Go contract exited {result.returncode} without diagnostics",
                file=sys.stderr,
            )
        return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
