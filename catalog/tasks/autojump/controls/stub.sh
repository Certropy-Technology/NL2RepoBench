#!/usr/bin/env bash
# Stub control: a minimally importable but non-functional autojump repository.
# Collection must still succeed so the frozen denominator stays at 23, while
# every scored behaviour fails.
set -euo pipefail

find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
mkdir -p /workspace/bin /workspace/tools

cat > /workspace/pyproject.toml <<'EOF'
[build-system]
requires = ["setuptools>=70", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "autojump"
version = "22.5.3"
requires-python = ">=3.8"

[tool.setuptools]
packages = ["bin", "tools"]
EOF

touch /workspace/bin/__init__.py /workspace/tools/__init__.py

cat > /workspace/bin/autojump_data.py <<'EOF'
from collections import namedtuple

BACKUP_THRESHOLD = 24 * 60 * 60
Entry = namedtuple("Entry", ["path", "weight"])


def load(config):
    return {}


def save(config, data):
    return None


def dictify(entries):
    return {}


def entriefy(data):
    return iter(())


def load_backup(config):
    return {}


def migrate_osx_xdg_data(config):
    return None
EOF

cat > /workspace/bin/autojump_match.py <<'EOF'
def match_anywhere(needles, haystack, ignore_case=False):
    return iter(())


def match_consecutive(needles, haystack, ignore_case=False):
    return iter(())


def match_fuzzy(needles, haystack, ignore_case=False, threshold=0.6):
    return iter(())
EOF

cat > /workspace/bin/autojump_utils.py <<'EOF'
def is_python2():
    return False


def is_python3():
    return True


def is_linux():
    return False


def is_osx():
    return False


def is_windows():
    return False


def in_bash():
    return False


def is_autojump_sourced():
    return False


def has_uppercase(string):
    return False


def sanitize(directories):
    return []


def surround_quotes(string):
    return ""


def encode_local(string):
    return ""


def unico(string):
    return ""


def first(xs):
    return None


def second(xs):
    return None


def last(xs):
    return None


def take(n, iterable):
    return iter(())


def get_tab_entry_info(entry, separator):
    return (None, None, None)


def get_pwd():
    return ""


def create_dir(path):
    return None


def move_file(src, dst):
    return None


def print_entry(entry):
    return None


def print_local(string):
    return None


def print_tab_menu(needle, tab_entries, separator):
    return None
EOF

cat > /workspace/bin/autojump <<'EOF'
VERSION = "0.0.0"
FUZZY_MATCH_THRESHOLD = 0.6
TAB_ENTRIES_COUNT = 9
TAB_SEPARATOR = "__"


def main(args):
    return 1
EOF

cat > /workspace/install.py <<'EOF'
SUPPORTED_SHELLS = ()


def main():
    return 1
EOF

cat > /workspace/uninstall.py <<'EOF'
def main():
    return 1
EOF
