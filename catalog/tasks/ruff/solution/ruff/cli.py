from __future__ import annotations

from pathlib import Path
import subprocess
import sys


def main() -> int:
    binary = Path(__file__).with_name("_ruff_bin")
    return subprocess.call([str(binary), *sys.argv[1:]])
