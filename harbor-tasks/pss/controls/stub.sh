#!/usr/bin/env bash
# Stub control: a minimally importable but non-functional pss repository.
# Collection must still succeed so the frozen denominator stays at 46, while
# every scored behaviour fails.
set -euo pipefail

find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
mkdir -p /workspace/psslib

cat > /workspace/pyproject.toml <<'EOF'
[build-system]
requires = ["setuptools>=70", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "pss"
version = "1.45"
description = "Stub control build of the pss source search toolkit."
requires-python = ">=3.8"

[tool.setuptools]
packages = ["psslib"]
EOF

cat > /workspace/psslib/__init__.py <<'EOF'
from .driver import pss_run

__version__ = "1.45"
EOF

cat > /workspace/psslib/matchresult.py <<'EOF'
from collections import namedtuple

MatchResult = namedtuple("MatchResult", ["matching_lineno", "matching_column_ranges"])
EOF

cat > /workspace/psslib/outputformatter.py <<'EOF'
class OutputFormatter:
    def start_matches_in_file(self, filename):
        return None

    def end_matches_in_file(self, filename):
        return None

    def matching_line(self, matchresult, filename):
        return None

    def context_line(self, line, lineno, filename):
        return None

    def context_separator(self):
        return None

    def binary_file_matches(self, msg):
        return None

    def found_filename(self, filename):
        return None
EOF

cat > /workspace/psslib/contentmatcher.py <<'EOF'
from .matchresult import MatchResult


class ContentMatcher:
    def __init__(
        self,
        pattern,
        ignore_case=False,
        invert_match=False,
        whole_words=False,
        literal_pattern=False,
        max_match_count=0,
    ):
        self.pattern = pattern

    def match_file(self, fileobj, max_match_count=0):
        return iter(())

    def matcher(self, line):
        return iter(())

    def inverted_matcher(self, line):
        return iter(())
EOF

cat > /workspace/psslib/filefinder.py <<'EOF'
class FileFinder:
    def __init__(
        self,
        roots,
        recurse=True,
        ignore_dirs=[],
        find_only_text_files=False,
        search_extensions=[],
        ignore_extensions=[],
        search_patterns=[],
        ignore_patterns=[],
        filter_include_patterns=[],
        filter_exclude_patterns=[],
    ):
        self.roots = roots

    def files(self):
        return iter(())
EOF

cat > /workspace/psslib/utils.py <<'EOF'
def tostring(b):
    return ""


def istextfile(fileobj, blocksize=512):
    return False


def decode_colorama_color(color_str):
    return None
EOF

cat > /workspace/psslib/defaultpssoutputformatter.py <<'EOF'
from .outputformatter import OutputFormatter


class DefaultPssOutputFormatter(OutputFormatter):
    def __init__(self, *args, **kwargs):
        return None
EOF

cat > /workspace/psslib/driver.py <<'EOF'
TYPE_EXTENSION_MAP = {}
IGNORED_DIRS = set()


class PssOnlyFindFilesOption:
    FIND_FILES = "FIND_FILES"
    FIND_FILES_MATCHING_PATTERN = "FIND_FILES_MATCHING_PATTERN"
    FIND_FILES_NOT_MATCHING_PATTERN = "FIND_FILES_NOT_MATCHING_PATTERN"


def pss_run(
    roots,
    pattern=None,
    output_formatter=None,
    only_find_files=False,
    only_find_files_option=PssOnlyFindFilesOption.FIND_FILES,
    search_all_types=False,
    search_all_files_and_dirs=False,
    add_ignored_dirs=[],
    remove_ignored_dirs=[],
    recurse=True,
    textonly=False,
    include_types=[],
    exclude_types=[],
    include_patterns=[],
    exclude_patterns=[],
    ignore_case=False,
    smart_case=False,
    invert_match=False,
    whole_words=False,
    literal_pattern=False,
    max_match_count=0,
    do_colors=False,
    match_color_str=None,
    filename_color_str=None,
    lineno_color_str=None,
    do_break=True,
    do_heading=True,
    prefix_filename_to_file_matches=True,
    show_column_of_first_match=False,
    ncontext_before=0,
    ncontext_after=0,
    **kwargs
):
    return False
EOF

cat > /workspace/psslib/pss.py <<'EOF'
class PssOptionParser:
    def __init__(self, *args, **kwargs):
        return None

    def parse_args(self, args=None):
        return (None, [])


def parse_cmdline(cmdline_list):
    return (None, [])


def main(argv=None, output_formatter=None):
    return 1
EOF

cat > /workspace/setup.py <<'EOF'
from setuptools import setup

setup()
EOF
