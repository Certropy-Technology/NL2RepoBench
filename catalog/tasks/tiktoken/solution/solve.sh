#!/usr/bin/env bash
set -euo pipefail

work=/workspace
script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
rm -rf "$work"/* "$work"/.[!.]* "$work"/..?* 2>/dev/null || true
mkdir -p "$work"
git clone --no-tags https://github.com/openai/tiktoken "$work/source"
git -C "$work/source" fetch --no-tags --depth=1 origin 4e71bbe0c078468e00fefbf94b39849389f346e5
git -C "$work/source" checkout --detach 4e71bbe0c078468e00fefbf94b39849389f346e5
test "$(git -C "$work/source" rev-parse HEAD)" = "4e71bbe0c078468e00fefbf94b39849389f346e5"
test "$(git -C "$work/source" archive --format=tar --prefix=tiktoken/ HEAD | sha256sum | cut -d' ' -f1)" = "80736cfc1a7cf9c87e530f3cf4cc7b536a3261208ded244138872b130b9f41d7"
cp -a "$work/source/." "$work/"
cp "$script_dir/fallback.py" "$work/tiktoken/_tiktoken.py"
cat > "$work/setup.py" <<'PY'
from setuptools import setup

setup(
    name="tiktoken",
    version="0.14.0",
    packages=["tiktoken", "tiktoken_ext"],
    package_data={"tiktoken": ["py.typed"]},
    install_requires=["regex", "requests"],
    zip_safe=False,
)
PY
rm -f "$work/pyproject.toml"
rm -rf "$work/source"
python -m pip install --no-deps --no-build-isolation "$work"
