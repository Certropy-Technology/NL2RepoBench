#!/usr/bin/env bash
set -euo pipefail
find /workspace -mindepth 1 -maxdepth 1 -exec rm -rf -- {} +
mkdir -p /workspace/pathvalidate
cat > /workspace/pyproject.toml <<'TOML'
[build-system]
requires = ["setuptools==84.0.0"]
build-backend = "setuptools.build_meta"
[project]
name = "pathvalidate"
version = "3.3.1"
TOML
cat > /workspace/pathvalidate/__init__.py <<'PY'
__author__ = "Tsuyoshi Hombashi"
__copyright__ = "Copyright 2016-2025, Tsuyoshi Hombashi"
__email__ = "tsuyoshi.hombashi@gmail.com"
__license__ = "MIT License"
__version__ = "3.3.1"
__all__ = (
    "__author__", "__copyright__", "__email__", "__license__", "__version__",
    "AbstractSanitizer", "AbstractValidator", "Platform", "ascii_symbols",
    "normalize_platform", "replace_ansi_escape", "replace_unprintable_char",
    "unprintable_ascii_chars", "validate_pathtype", "validate_unprintable_char",
    "FileNameSanitizer", "FileNameValidator", "is_valid_filename",
    "sanitize_filename", "validate_filename", "FilePathSanitizer",
    "FilePathValidator", "is_valid_filepath", "sanitize_filepath",
    "validate_filepath", "sanitize_ltsv_label", "validate_ltsv_label",
    "replace_symbol", "validate_symbol", "ErrorReason", "InvalidCharError",
    "InvalidReservedNameError", "NullNameError", "ReservedNameError",
    "ValidationError", "ValidReservedNameError",
)
class AbstractValidator: pass
class AbstractSanitizer: pass
class Platform: pass
ascii_symbols = ()
unprintable_ascii_chars = ()
def normalize_platform(value): return value
def replace_ansi_escape(value, replacement_text=""): return value
def replace_unprintable_char(value, replacement_text=""): return value
def validate_pathtype(value, allow_whitespaces=False, error_msg=None): return None
def validate_unprintable_char(value): return None
class FileNameSanitizer: pass
class FileNameValidator: pass
class FilePathSanitizer: pass
class FilePathValidator: pass
def sanitize_filename(filename, replacement_text="", **kwargs): return filename
def sanitize_filepath(file_path, replacement_text="", **kwargs): return file_path
def validate_filename(filename, **kwargs): return None
def validate_filepath(file_path, **kwargs): return None
def is_valid_filename(filename, **kwargs): return True
def is_valid_filepath(file_path, **kwargs): return True
def sanitize_ltsv_label(label, replacement_text=""): return label
def validate_ltsv_label(label): return None
def replace_symbol(text, replacement_text="", **kwargs): return text
def validate_symbol(text): return None
class ErrorReason: pass
class ValidationError(ValueError): pass
class InvalidCharError(ValidationError): pass
class ReservedNameError(ValidationError): pass
class NullNameError(ValidationError): pass
class ValidReservedNameError(ReservedNameError): pass
class InvalidReservedNameError(ReservedNameError): pass
PY
