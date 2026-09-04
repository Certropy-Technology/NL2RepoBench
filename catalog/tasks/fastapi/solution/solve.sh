#!/usr/bin/env bash
set -euo pipefail

readonly ARCHIVE=/solution/source.tar
readonly EXPECTED=93b5db4f6487b38ff1acfbbd66d8a775654fc7014da277240916efe5bae66d06
printf '%s  %s\n' "$EXPECTED" "$ARCHIVE" | sha256sum --check --strict
find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
tar -xf "$ARCHIVE" -C /workspace
test "$(grep -E '^__version__ = ' /workspace/fastapi/__init__.py)" = '__version__ = "0.141.1"'
printf 'restored FastAPI revision 50113da16fec53b66b80d75e80a89296de4fa5a5\n'
