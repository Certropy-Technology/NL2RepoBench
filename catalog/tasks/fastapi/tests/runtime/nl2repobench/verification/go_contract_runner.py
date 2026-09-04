"""Run trusted Go contract assertions while proxying candidate calls safely."""

from __future__ import annotations

import argparse
import os
import shlex
import subprocess
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
            "#!/bin/sh\n"
            "exec /usr/bin/python3 "
            f"{shlex.quote(str(args.proxy))} "
            '"$1"\n',
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
        print(result.stderr, end="", file=__import__("sys").stderr)
        if result.returncode != 0 and not result.stderr:
            print(
                f"Go contract exited {result.returncode} without diagnostics",
                file=__import__("sys").stderr,
            )
        return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
