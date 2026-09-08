#!/usr/bin/env bash
set -euo pipefail

# Stub control: minimal API surface, low expected score

WORKSPACE="/workspace"
mkdir -p "${WORKSPACE}/colorama"

cat > "${WORKSPACE}/pyproject.toml" << 'PYPROJ'
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "colorama"
version = "0.4.6"
description = "Stub colorama"
PYPROJ

cat > "${WORKSPACE}/colorama/__init__.py" << 'PY'
__version__ = "0.4.6"

class AnsiFore:
    BLACK = ""
    RED = ""
    GREEN = ""
    YELLOW = ""
    BLUE = ""
    MAGENTA = ""
    CYAN = ""
    WHITE = ""
    RESET = ""
    LIGHTBLACK_EX = ""
    LIGHTRED_EX = ""
    LIGHTGREEN_EX = ""
    LIGHTYELLOW_EX = ""
    LIGHTBLUE_EX = ""
    LIGHTMAGENTA_EX = ""
    LIGHTCYAN_EX = ""
    LIGHTWHITE_EX = ""

class AnsiBack:
    BLACK = ""
    RED = ""
    GREEN = ""
    YELLOW = ""
    BLUE = ""
    MAGENTA = ""
    CYAN = ""
    WHITE = ""
    RESET = ""
    LIGHTBLACK_EX = ""
    LIGHTRED_EX = ""
    LIGHTGREEN_EX = ""
    LIGHTYELLOW_EX = ""
    LIGHTBLUE_EX = ""
    LIGHTMAGENTA_EX = ""
    LIGHTCYAN_EX = ""
    LIGHTWHITE_EX = ""

class AnsiStyle:
    BRIGHT = ""
    DIM = ""
    NORMAL = ""
    RESET_ALL = ""

class AnsiCursor:
    @staticmethod
    def UP(n=1):
        return ""
    @staticmethod
    def DOWN(n=1):
        return ""
    @staticmethod
    def FORWARD(n=1):
        return ""
    @staticmethod
    def BACK(n=1):
        return ""
    @staticmethod
    def POS(x=1, y=1):
        return ""

Fore = AnsiFore()
Back = AnsiBack()
Style = AnsiStyle()
Cursor = AnsiCursor()

def init(autoreset=False, convert=None, strip=None, wrap=True):
    pass

def deinit():
    pass

def reinit():
    pass

def just_fix_windows_console():
    pass

def colorama_text(*args, **kwargs):
    pass

class AnsiToWin32:
    pass
PY
