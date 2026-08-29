#!/usr/bin/env bash
set -euo pipefail

find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
cat > /workspace/pyproject.toml <<'EOF'
[build-system]
requires = []
build-backend = "backend"
backend-path = ["."]

[project]
name = "mypy_extensions"
version = "1.2.0.dev0"
EOF
cat > /workspace/backend.py <<'EOF'
import base64
from pathlib import Path
import zipfile


def build_wheel(wheel_directory, config_settings=None, metadata_directory=None):
    wheel = Path(wheel_directory) / "mypy_extensions-1.2.0.dev0-py3-none-any.whl"
    module = Path(__file__).with_name("mypy_extensions.py").read_bytes()
    metadata = b"Metadata-Version: 2.1\nName: mypy_extensions\nVersion: 1.2.0.dev0\n\n"
    wheel_meta = b"Wheel-Version: 1.0\nGenerator: control\nRoot-Is-Purelib: true\nTag: py3-none-any\n"
    files = {
        "mypy_extensions.py": module,
        "mypy_extensions-1.2.0.dev0.dist-info/METADATA": metadata,
        "mypy_extensions-1.2.0.dev0.dist-info/WHEEL": wheel_meta,
    }
    records = []
    with zipfile.ZipFile(wheel, "w") as archive:
        for name, data in files.items():
            archive.writestr(name, data)
            digest = base64.urlsafe_b64encode(__import__("hashlib").sha256(data).digest()).rstrip(b"=").decode()
            records.append(f"{name},sha256={digest},{len(data)}")
        record = "mypy_extensions-1.2.0.dev0.dist-info/RECORD"
        records.append(f"{record},,")
        archive.writestr(record, "\n".join(records) + "\n")
    return wheel.name
EOF
cat > /workspace/mypy_extensions.py <<'EOF'
def _missing(*args, **kwargs):
    raise NotImplementedError("control stub")

Arg = DefaultArg = NamedArg = DefaultNamedArg = VarArg = KwArg = _missing
TypedDict = trait = mypyc_attr = _missing

class _Missing:
    def __class_getitem__(cls, item):
        raise NotImplementedError("control stub")

FlexibleAlias = _Missing()
i64 = i32 = i16 = u8 = _Missing
EOF
