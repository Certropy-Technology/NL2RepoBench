#!/usr/bin/env python3
"""Create task-local Node negative-control bundles from one compiled task."""

from __future__ import annotations

import argparse
import os
import shutil
from pathlib import Path

CONTROL_SCRIPTS = {
    "stub": """#!/usr/bin/env bash
set -euo pipefail
cat > package.json <<'JSON'
{"name":"canonicalize","version":"1.0.0","type":"module","exports":{".":{"import":"./index.mjs"}}}
JSON
cat > index.mjs <<'JS'
export default () => '{}';
JS
""",
    "forgery": """#!/usr/bin/env bash
set -euo pipefail
mkdir -p tests /logs/verifier
printf 'forged' > reward.json
printf 'forged' > grading.json
cat > package.json <<'JSON'
{"name":"canonicalize","version":"1.0.0","type":"module","exports":{".":{"import":"./index.mjs"}}}
JSON
cat > index.mjs <<'JS'
export default (value) => JSON.stringify(value);
JS
""",
    "install-script": """#!/usr/bin/env bash
set -euo pipefail
cat > package.json <<'JSON'
{"name":"canonicalize","version":"1.0.0","type":"module","scripts":{"postinstall":"echo forbidden"},
 "exports":{".":{"import":"./index.mjs"}}}
JSON
cat > index.mjs <<'JS'
export default (value) => JSON.stringify(value);
JS
""",
    "loader-hook": """#!/usr/bin/env bash
set -euo pipefail
cat > package.json <<'JSON'
{"name":"canonicalize","version":"1.0.0","type":"module","exports":{".":{"import":"./index.mjs"}}}
JSON
cat > index.mjs <<'JS'
export default (value) => JSON.stringify(value);
JS
printf 'NODE_OPTIONS=--loader=./evil.mjs' > node-options.txt
""",
    "hang": """#!/usr/bin/env bash
set -euo pipefail
cat > package.json <<'JSON'
{"name":"canonicalize","version":"1.0.0","type":"module","exports":{".":{"import":"./index.mjs"}}}
JSON
cat > index.mjs <<'JS'
export default () => { while (true) {} };
JS
""",
    "offline": """#!/usr/bin/env bash
set -euo pipefail
cat > package.json <<'JSON'
{"name":"canonicalize","version":"1.0.0","type":"module","exports":{".":{"import":"./index.mjs"}}}
JSON
cat > index.mjs <<'JS'
export default async () => fetch('https://example.invalid/should-be-blocked');
JS
""",
}

CONTROL_LOCK = """cat > package-lock.json <<'JSON'
{"name":"canonicalize","version":"1.0.0","lockfileVersion":3,"requires":true,"packages":{"":{"name":"canonicalize","version":"1.0.0","type":"module"}}}
JSON
"""


def prepare(bundle: Path, output: Path, kinds: tuple[str, ...]) -> tuple[Path, ...]:
    if not bundle.is_dir() or bundle.is_symlink():
        raise ValueError(f"compiled Node bundle must be a regular directory: {bundle}")
    output.mkdir(parents=True, exist_ok=True)
    results: list[Path] = []
    for kind in kinds:
        if kind not in CONTROL_SCRIPTS:
            raise ValueError(f"unknown Node control: {kind}")
        target = output / f"{bundle.name}-{kind}"
        if target.exists() or target.is_symlink():
            raise ValueError(f"control output already exists: {target}")
        shutil.copytree(bundle, target, symlinks=False)
        solve = target / "solution/solve.sh"
        script = CONTROL_SCRIPTS[kind]
        solve.write_text(
            script if kind == "empty" else CONTROL_LOCK + script,
            encoding="utf-8",
        )
        os.chmod(solve, 0o755)
        results.append(target)
    return tuple(results)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("bundle", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--kind", action="append", choices=sorted(CONTROL_SCRIPTS))
    args = parser.parse_args()
    kinds = tuple(args.kind or CONTROL_SCRIPTS)
    try:
        outputs = prepare(args.bundle, args.output, kinds)
    except (OSError, ValueError) as exc:
        print(f"Node control preparation failed: {exc}")
        return 1
    for path in outputs:
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
