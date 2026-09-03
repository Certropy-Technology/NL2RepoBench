#!/usr/bin/env bash
set -euo pipefail

readonly WHEEL="/solution/orjson-3.12.0-cp312-cp312-manylinux_2_34_x86_64.whl"
readonly WHEEL_SHA256="144297495446ae65a0e69ef24864e357c74375401357c36e942977b971cec36b"
readonly WHEEL_SIZE="295539"

test -f "$WHEEL"
test "$(stat -c '%s' "$WHEEL")" = "$WHEEL_SIZE"
printf '%s  %s\n' "$WHEEL_SHA256" "$WHEEL" | sha256sum --check --strict
rm -rf /workspace/*
python -m pip install --no-deps --no-index --target /workspace "$WHEEL"
cat > /workspace/pyproject.toml <<'TOML'
[build-system]
requires = []
build-backend = "setuptools.build_meta:__legacy__"

[project]
name = "orjson"
version = "3.12.0"

[tool.setuptools]
packages = ["orjson"]

[tool.setuptools.package-data]
orjson = ["*.so", "*.pyi", "py.typed"]
TOML
python - <<'PY'
import orjson
assert orjson.__version__ == "3.12.0"
assert orjson.loads(orjson.dumps({"ok": True})) == {"ok": True}
PY
echo "restored orjson 3.12.0 from digest-verified reference wheel"
