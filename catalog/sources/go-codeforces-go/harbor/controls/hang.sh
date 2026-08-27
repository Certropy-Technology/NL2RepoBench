#!/usr/bin/env bash
set -euo pipefail
/controls/stub.sh
python3 - <<'PY'
from pathlib import Path

path = Path("copypasta/bitset.go")
text = path.read_text(encoding="utf-8")
text = text.replace("package copypasta\n", "package copypasta\n\nimport \"time\"\n")
path.write_text(text.replace("func (Bitset) String() string { return \"\" }", "func (Bitset) String() string { time.Sleep(60 * time.Second); return \"\" }"), encoding="utf-8")
PY
