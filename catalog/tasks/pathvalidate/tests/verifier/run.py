#!/usr/bin/env python3
"""Private pathvalidate contract executed through isolated candidate subprocesses."""

from __future__ import annotations

import json
import os
import sys
import textwrap
from dataclasses import dataclass


@dataclass(frozen=True)
class Scenario:
    leaf_id: str
    source: str


def scenario(leaf_id: str, source: str) -> Scenario:
    return Scenario(leaf_id, textwrap.dedent(source).strip() + "\n")


SCENARIOS = (
    scenario(
        "api-surface",
        """
        import pathvalidate as p
        expected = (
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
        assert tuple(p.__all__) == expected
        assert all(hasattr(p, name) for name in expected)
        result = True
        """,
    ),
    scenario(
        "module-metadata",
        """
        import pathvalidate as p
        assert p.__version__ == "3.3.1"
        assert p.__author__ == "Tsuyoshi Hombashi"
        assert p.__license__ == "MIT License"
        assert p.__email__ == "tsuyoshi.hombashi@gmail.com"
        result = True
        """,
    ),
    scenario(
        "core-signatures",
        """
        import inspect
        import pathvalidate as p
        assert list(inspect.signature(p.sanitize_filename).parameters) == [
            "filename", "replacement_text", "platform", "max_len", "fs_encoding",
            "check_reserved", "null_value_handler", "reserved_name_handler",
            "additional_reserved_names", "validate_after_sanitize",
        ]
        assert list(inspect.signature(p.validate_filename).parameters) == [
            "filename", "platform", "min_len", "max_len", "fs_encoding",
            "check_reserved", "additional_reserved_names",
        ]
        assert list(inspect.signature(p.sanitize_filepath).parameters) == [
            "file_path", "replacement_text", "platform", "max_len", "fs_encoding",
            "check_reserved", "null_value_handler", "reserved_name_handler",
            "additional_reserved_names", "normalize", "validate_after_sanitize",
        ]
        assert list(inspect.signature(p.validate_filepath).parameters) == [
            "file_path", "platform", "min_len", "max_len", "fs_encoding",
            "check_reserved", "additional_reserved_names",
        ]
        result = True
        """,
    ),
    scenario(
        "platform-enum",
        """
        from pathvalidate import Platform
        assert [(x.name, x.value) for x in Platform] == [
            ("POSIX", "POSIX"), ("UNIVERSAL", "universal"), ("LINUX", "Linux"),
            ("WINDOWS", "Windows"), ("MACOS", "macOS"),
        ]
        result = True
        """,
    ),
    scenario(
        "normalize-platform",
        """
        from pathvalidate import Platform, normalize_platform
        assert normalize_platform(None) is Platform.UNIVERSAL
        assert normalize_platform("") is Platform.UNIVERSAL
        assert normalize_platform("universal") is Platform.UNIVERSAL
        assert normalize_platform("POSIX") is Platform.POSIX
        assert normalize_platform("linux") is Platform.LINUX
        assert normalize_platform("win32") is Platform.WINDOWS
        assert normalize_platform("Windows") is Platform.WINDOWS
        assert normalize_platform("darwin") is Platform.MACOS
        assert normalize_platform(Platform.LINUX) is Platform.LINUX
        result = True
        """,
    ),
    scenario(
        "ascii-constants",
        """
        import string
        from pathvalidate import ascii_symbols, unprintable_ascii_chars
        assert isinstance(ascii_symbols, tuple) and isinstance(unprintable_ascii_chars, tuple)
        assert all(len(x) == 1 for x in ascii_symbols + unprintable_ascii_chars)
        assert set(unprintable_ascii_chars).isdisjoint(string.printable)
        assert "/" in ascii_symbols and ":" in ascii_symbols and "A" not in ascii_symbols
        result = True
        """,
    ),
    scenario(
        "ansi-escape-replacement",
        """
        from pathvalidate import replace_ansi_escape
        assert replace_ansi_escape("A\\x1b[31mred\\x1b[0mB") == "AredB"
        assert replace_ansi_escape("x\\x1b[2Jy", "-") == "x-y"
        try:
            replace_ansi_escape(None)
        except TypeError as exc:
            assert str(exc) == "text must be a string"
        else:
            raise AssertionError("TypeError not raised")
        result = True
        """,
    ),
    scenario(
        "unprintable-character-helpers",
        """
        from pathvalidate import InvalidCharError, replace_unprintable_char, validate_unprintable_char
        assert replace_unprintable_char("a\\x00b\\x07c") == "abc"
        assert replace_unprintable_char("a\\x00b", "_") == "a_b"
        validate_unprintable_char("plain text")
        try:
            validate_unprintable_char("a\\x00b")
        except InvalidCharError as exc:
            assert exc.reason.name == "INVALID_CHARACTER"
        else:
            raise AssertionError("InvalidCharError not raised")
        result = True
        """,
    ),
    scenario(
        "path-type-validation",
        """
        from pathlib import Path
        from pathvalidate import ErrorReason, ValidationError, validate_pathtype
        validate_pathtype("name")
        validate_pathtype(Path("name"))
        validate_pathtype("   ", allow_whitespaces=True)
        for value in (None, "", "   "):
            try:
                validate_pathtype(value)
            except ValidationError as exc:
                assert exc.reason is ErrorReason.NULL_NAME
            else:
                raise AssertionError(value)
        try:
            validate_pathtype(123)
        except TypeError as exc:
            assert "text must be a string" in str(exc)
        else:
            raise AssertionError("TypeError not raised")
        result = True
        """,
    ),
    scenario(
        "sanitize-filename-universal",
        """
        from pathvalidate import sanitize_filename
        assert sanitize_filename('fi:l*e/p"a?t>h|.t<xt') == "filepath.txt"
        assert sanitize_filename("_a*b:c<d>e%f/(g)h+i_0.txt") == "_abcde%f(g)h+i_0.txt"
        assert sanitize_filename("normal.txt") == "normal.txt"
        result = True
        """,
    ),
    scenario(
        "sanitize-filename-replacement",
        """
        from pathvalidate import sanitize_filename
        assert sanitize_filename("a:b*c?.txt", "_") == "a_b_c_.txt"
        assert sanitize_filename("a/b", "--", platform="linux") == "a--b"
        assert sanitize_filename("a:b", "-", platform="windows") == "a-b"
        result = True
        """,
    ),
    scenario(
        "sanitize-filename-pathlike",
        """
        from pathlib import Path
        from pathvalidate import sanitize_filename
        value = sanitize_filename(Path("a:b.txt"), platform="windows")
        assert value == Path("ab.txt")
        assert isinstance(value, Path)
        result = True
        """,
    ),
    scenario(
        "sanitize-filename-multibyte",
        """
        from pathvalidate import sanitize_filename
        assert sanitize_filename("あい/うえお.txt") == "あいうえお.txt"
        assert sanitize_filename("属/性.txt", "-") == "属-性.txt"
        result = True
        """,
    ),
    scenario(
        "sanitize-filename-byte-truncation",
        """
        from pathvalidate import sanitize_filename
        assert sanitize_filename("abcdef", max_len=4, fs_encoding="utf-8") == "abcd"
        assert sanitize_filename("あいう", max_len=7, fs_encoding="utf-8") == "あい"
        assert sanitize_filename("abc", max_len=None) == "abc"
        result = True
        """,
    ),
    scenario(
        "sanitize-filename-windows-boundaries",
        """
        from pathvalidate import sanitize_filename
        assert sanitize_filename(" leading.txt", platform="windows") == "leading.txt"
        assert sanitize_filename("trailing. ", platform="windows") == "trailing"
        assert sanitize_filename("...", platform="windows") == ""
        assert sanitize_filename(".", platform="windows") == "."
        assert sanitize_filename("..", platform="windows") == ".."
        result = True
        """,
    ),
    scenario(
        "sanitize-filename-reserved-default",
        """
        from pathvalidate import sanitize_filename
        assert sanitize_filename("CON", platform="windows") == "CON_"
        assert sanitize_filename("con.txt", platform="windows") == "con_.txt"
        assert sanitize_filename("NUL", platform="universal") == "NUL_"
        assert sanitize_filename("CON", platform="linux") == "CON"
        result = True
        """,
    ),
    scenario(
        "sanitize-filename-reserved-handlers",
        """
        from pathvalidate import sanitize_filename
        from pathvalidate.handler import ReservedNameHandler, raise_error
        assert sanitize_filename("CON", platform="windows", reserved_name_handler=ReservedNameHandler.add_leading_underscore) == "_CON"
        assert sanitize_filename("CON", platform="windows", reserved_name_handler=ReservedNameHandler.as_is) == "CON"
        try:
            sanitize_filename("CON", platform="windows", reserved_name_handler=raise_error)
        except Exception as exc:
            assert exc.reason.name == "RESERVED_NAME"
        else:
            raise AssertionError("reserved error not raised")
        result = True
        """,
    ),
    scenario(
        "sanitize-filename-additional-reserved",
        """
        from pathvalidate import sanitize_filename
        assert sanitize_filename("secret.txt", additional_reserved_names=["secret"]) == "secret_.txt"
        assert sanitize_filename("SECRET.TXT", additional_reserved_names=["secret"]) == "SECRET_.TXT"
        assert sanitize_filename("other.txt", additional_reserved_names=["secret"]) == "other.txt"
        result = True
        """,
    ),
    scenario(
        "sanitize-filename-null-handlers",
        """
        from pathvalidate import ErrorReason, sanitize_filename
        from pathvalidate.handler import NullValueHandler, raise_error
        assert sanitize_filename(None, null_value_handler=NullValueHandler.return_null_string) == ""
        stamp = sanitize_filename("", null_value_handler=NullValueHandler.return_timestamp)
        assert isinstance(stamp, str) and float(stamp) > 0
        try:
            sanitize_filename("?", null_value_handler=raise_error)
        except Exception as exc:
            assert exc.reason is ErrorReason.NULL_NAME
        else:
            raise AssertionError("null error not raised")
        result = True
        """,
    ),
    scenario(
        "validate-filename-valid",
        """
        from pathvalidate import validate_filename
        for platform in (None, "universal", "linux", "windows", "macos", "posix"):
            validate_filename("report-2025.txt", platform=platform)
        validate_filename("a:b", platform="linux")
        validate_filename("CON", platform="linux")
        result = True
        """,
    ),
    scenario(
        "validate-filename-invalid-character",
        """
        from pathvalidate import ErrorReason, InvalidCharError, Platform, validate_filename
        try:
            validate_filename("a?b", platform="windows")
        except InvalidCharError as exc:
            assert exc.reason is ErrorReason.INVALID_CHARACTER
            assert exc.platform is Platform.WINDOWS
            assert exc.as_slog()["value"] == "a?b"
        else:
            raise AssertionError("InvalidCharError not raised")
        result = True
        """,
    ),
    scenario(
        "validate-filename-absolute-path",
        """
        from pathvalidate import ErrorReason, validate_filename
        for value in ("/tmp/name", "C:/tmp/name"):
            try:
                validate_filename(value, platform="universal")
            except Exception as exc:
                assert exc.reason is ErrorReason.FOUND_ABS_PATH
                assert "expected a filename" in str(exc)
            else:
                raise AssertionError(value)
        result = True
        """,
    ),
    scenario(
        "validate-filename-reserved-error",
        """
        from pathvalidate import ErrorReason, Platform, ReservedNameError, validate_filename
        try:
            validate_filename("con.txt", platform="windows")
        except ReservedNameError as exc:
            assert exc.reason is ErrorReason.RESERVED_NAME
            assert exc.platform is Platform.WINDOWS
            assert exc.reserved_name.casefold() == "con"
            assert exc.reusable_name is False
        else:
            raise AssertionError("ReservedNameError not raised")
        result = True
        """,
    ),
    scenario(
        "validate-filename-length",
        """
        from pathvalidate import ErrorReason, validate_filename
        try:
            validate_filename("éé", max_len=3, fs_encoding="utf-8")
        except Exception as exc:
            assert exc.reason is ErrorReason.INVALID_LENGTH
            assert exc.byte_count == 4
            assert exc.fs_encoding == "utf-8"
            assert "expected<=3 bytes" in str(exc)
        else:
            raise AssertionError("length error not raised")
        try:
            validate_filename("a", min_len=2)
        except Exception as exc:
            assert exc.reason is ErrorReason.INVALID_LENGTH
        else:
            raise AssertionError("minimum error not raised")
        result = True
        """,
    ),
    scenario(
        "is-valid-filename",
        """
        from pathvalidate import is_valid_filename
        assert is_valid_filename("report.txt") is True
        assert is_valid_filename("a?b", platform="windows") is False
        assert is_valid_filename("CON", platform="windows") is False
        assert is_valid_filename("CON", platform="windows", check_reserved=False) is True
        assert is_valid_filename("x" * 300, max_len=None) is False
        assert is_valid_filename("x" * 200, max_len=None) is True
        result = True
        """,
    ),
    scenario(
        "filename-validator-properties",
        """
        from pathvalidate import FileNameValidator, Platform
        validator = FileNameValidator(min_len=2, max_len=12, fs_encoding="utf-8", platform="windows", additional_reserved_names=["abc"])
        assert validator.min_len == 2
        assert validator.max_len == 12
        assert validator.platform is Platform.WINDOWS
        assert "ABC" in validator.reserved_keywords
        assert "CON" in validator.reserved_keywords
        result = True
        """,
    ),
    scenario(
        "filename-sanitizer-properties",
        """
        from pathvalidate import FileNameSanitizer, Platform
        sanitizer = FileNameSanitizer(max_len=20, fs_encoding="utf-8", platform="linux", additional_reserved_names=["abc"])
        assert sanitizer.max_len == 20
        assert sanitizer.platform is Platform.LINUX
        assert sanitizer.sanitize("a/b", "_") == "a_b"
        assert sanitizer.sanitize("abc") == "abc_"
        result = True
        """,
    ),
    scenario(
        "sanitize-filepath-universal",
        """
        from pathvalidate import sanitize_filepath
        assert sanitize_filepath('fi:l*e/p"a?t>h|.t<xt') == "file/path.txt"
        assert sanitize_filepath("dir/a:b?.txt", "_") == "dir/a_b_.txt"
        assert sanitize_filepath("dir//sub/../name.txt") == "dir/name.txt"
        result = True
        """,
    ),
    scenario(
        "sanitize-filepath-windows",
        """
        from pathvalidate import sanitize_filepath
        assert sanitize_filepath(r"C:\\A?B\\CON\\name.txt", platform="windows") == r"C:\\AB\\CON_\\name.txt"
        assert sanitize_filepath(r"dir/a:b.txt", "_", platform="windows") == r"dir\\a_b.txt"
        result = True
        """,
    ),
    scenario(
        "sanitize-filepath-posix",
        """
        from pathvalidate import sanitize_filepath
        assert sanitize_filepath("dir/a:b*c?.txt", platform="linux") == "dir/a:b*c?.txt"
        assert sanitize_filepath("dir/a\\x00b.txt", "_", platform="linux") == "dir/a_b.txt"
        result = True
        """,
    ),
    scenario(
        "sanitize-filepath-normalize",
        """
        from pathvalidate import sanitize_filepath
        assert sanitize_filepath("a/./b/../c", platform="linux", normalize=True) == "a/c"
        assert sanitize_filepath("a/./b/../c", platform="linux", normalize=False) == "a/./b/../c"
        result = True
        """,
    ),
    scenario(
        "sanitize-filepath-pathlike",
        """
        from pathlib import Path
        from pathvalidate import sanitize_filepath
        value = sanitize_filepath(Path("dir/a:b.txt"), platform="universal")
        assert value == Path("dir/ab.txt")
        assert isinstance(value, Path)
        result = True
        """,
    ),
    scenario(
        "sanitize-filepath-reserved",
        """
        from pathvalidate import sanitize_filepath
        assert sanitize_filepath("CON/file.txt", platform="windows") == r"CON_\\file.txt"
        assert sanitize_filepath("dir/NUL.txt", platform="universal") == "dir/NUL_.txt"
        assert sanitize_filepath("secret/file", additional_reserved_names=["secret"]) == "secret_/file"
        result = True
        """,
    ),
    scenario(
        "sanitize-filepath-null",
        """
        from pathvalidate import ErrorReason, sanitize_filepath
        from pathvalidate.handler import NullValueHandler, raise_error
        assert sanitize_filepath(None, null_value_handler=NullValueHandler.return_null_string) == ""
        stamp = sanitize_filepath("", null_value_handler=NullValueHandler.return_timestamp)
        assert float(stamp) > 0
        try:
            sanitize_filepath("?", null_value_handler=raise_error)
        except Exception as exc:
            assert exc.reason is ErrorReason.NULL_NAME
        else:
            raise AssertionError("null error not raised")
        result = True
        """,
    ),
    scenario(
        "validate-filepath-valid",
        """
        from pathvalidate import validate_filepath
        validate_filepath("dir/report.txt", platform="linux")
        validate_filepath("/var/tmp/report.txt", platform="linux")
        validate_filepath(r"C:\\Temp\\report.txt", platform="windows")
        validate_filepath("dir/report.txt", platform="universal")
        result = True
        """,
    ),
    scenario(
        "validate-filepath-invalid-character",
        """
        from pathvalidate import ErrorReason, InvalidCharError, validate_filepath
        try:
            validate_filepath("dir/a?b.txt", platform="windows")
        except InvalidCharError as exc:
            assert exc.reason is ErrorReason.INVALID_CHARACTER
            assert exc.as_slog()["value"] == "a?b.txt"
        else:
            raise AssertionError("InvalidCharError not raised")
        try:
            validate_filepath("dir/a\\x00b", platform="linux")
        except InvalidCharError:
            pass
        else:
            raise AssertionError("unprintable error not raised")
        result = True
        """,
    ),
    scenario(
        "validate-filepath-platform-absolute",
        """
        from pathvalidate import ErrorReason, validate_filepath
        for value, platform in (("/tmp/name", "windows"), (r"C:\\tmp\\name", "linux")):
            try:
                validate_filepath(value, platform=platform)
            except Exception as exc:
                assert exc.reason is ErrorReason.MALFORMED_ABS_PATH
                assert "invalid absolute file path" in str(exc)
            else:
                raise AssertionError((value, platform))
        result = True
        """,
    ),
    scenario(
        "validate-filepath-length",
        """
        from pathvalidate import ErrorReason, validate_filepath
        try:
            validate_filepath("dir/éé", platform="linux", max_len=6, fs_encoding="utf-8")
        except Exception as exc:
            assert exc.reason is ErrorReason.INVALID_LENGTH
            assert exc.byte_count == 8
            assert "expected<=6 bytes" in str(exc)
        else:
            raise AssertionError("length error not raised")
        result = True
        """,
    ),
    scenario(
        "is-valid-filepath",
        """
        from pathvalidate import is_valid_filepath
        assert is_valid_filepath("dir/report.txt", platform="linux") is True
        assert is_valid_filepath("dir/a?b", platform="windows") is False
        assert is_valid_filepath("/tmp/name", platform="windows") is False
        assert is_valid_filepath("x" * 300, platform="windows", max_len=None) is False
        result = True
        """,
    ),
    scenario(
        "filepath-validator-properties",
        """
        from pathvalidate import FilePathValidator, Platform
        validator = FilePathValidator(min_len=2, max_len=40, fs_encoding="utf-8", platform="linux", additional_reserved_names=["abc"])
        assert validator.min_len == 2
        assert validator.max_len == 40
        assert validator.platform is Platform.LINUX
        assert "ABC" in validator.reserved_keywords
        result = True
        """,
    ),
    scenario(
        "filepath-sanitizer-properties",
        """
        from pathvalidate import FilePathSanitizer, Platform
        sanitizer = FilePathSanitizer(max_len=40, fs_encoding="utf-8", platform="windows", normalize=False)
        assert sanitizer.max_len == 40
        assert sanitizer.platform is Platform.WINDOWS
        assert sanitizer.sanitize("dir/a:b", "_") == r"dir\\a_b"
        result = True
        """,
    ),
    scenario(
        "ltsv-labels",
        """
        from pathvalidate import ErrorReason, sanitize_ltsv_label, validate_ltsv_label
        assert sanitize_ltsv_label("host:name value", "_") == "host_name_value"
        assert sanitize_ltsv_label("A-z_9.-") == "A-z_9.-"
        validate_ltsv_label("host_name-1.2")
        try:
            validate_ltsv_label("host:name")
        except Exception as exc:
            assert exc.reason is ErrorReason.INVALID_CHARACTER
        else:
            raise AssertionError("label error not raised")
        result = True
        """,
    ),
    scenario(
        "replace-symbol-basic",
        """
        from pathvalidate import replace_symbol
        assert replace_symbol("A+B=C!") == "ABC"
        assert replace_symbol("A+B=C!", "_") == "A_B_C_"
        assert replace_symbol("日本語+ABC") == "日本語ABC"
        result = True
        """,
    ),
    scenario(
        "replace-symbol-options",
        """
        from pathvalidate import replace_symbol
        assert replace_symbol("A++B==C", "_", is_replace_consecutive_chars=True) == "A_B_C"
        assert replace_symbol("++A++", "_", is_replace_consecutive_chars=True, is_strip=True) == "A"
        assert replace_symbol("A+B-C", "_", exclude_symbols=["+"]) == "A+B_C"
        result = True
        """,
    ),
    scenario(
        "validate-symbol",
        """
        from pathvalidate import ErrorReason, validate_symbol
        validate_symbol("Alpha123日本語")
        try:
            validate_symbol("Alpha+Beta")
        except Exception as exc:
            assert exc.reason is ErrorReason.INVALID_CHARACTER
            assert "+" in str(exc)
        else:
            raise AssertionError("symbol error not raised")
        result = True
        """,
    ),
    scenario(
        "error-reason-metadata",
        """
        from pathvalidate import ErrorReason
        expected = {
            "NULL_NAME": ("PV1001", "the value must not be an empty string"),
            "RESERVED_NAME": ("PV1002", "found a reserved name by a platform"),
            "INVALID_CHARACTER": ("PV1100", "invalid characters found"),
            "INVALID_LENGTH": ("PV1101", "found an invalid string length"),
            "FOUND_ABS_PATH": ("PV1200", "found an absolute path where must be a relative path"),
            "MALFORMED_ABS_PATH": ("PV1201", "found a malformed absolute path"),
            "INVALID_AFTER_SANITIZE": ("PV2000", "found invalid value after sanitizing"),
        }
        assert {x.name: (x.code, x.description) for x in ErrorReason} == expected
        assert str(ErrorReason.INVALID_CHARACTER) == "[PV1100] invalid characters found"
        result = True
        """,
    ),
    scenario(
        "validation-error-structure",
        """
        from pathvalidate import ErrorReason, Platform, ValidationError
        exc = ValidationError(
            reason=ErrorReason.INVALID_CHARACTER, platform=Platform.UNIVERSAL,
            description="bad name", fs_encoding="utf-8", byte_count=7, value="a?b",
        )
        assert exc.reason is ErrorReason.INVALID_CHARACTER
        assert exc.platform is Platform.UNIVERSAL
        assert exc.description == "bad name"
        assert exc.fs_encoding == "utf-8" and exc.byte_count == 7
        assert exc.as_slog() == {
            "code": "PV1100", "description": "bad name", "platform": "universal",
            "fs_encoding": "utf-8", "byte_count": "7", "value": "a?b",
        }
        text = str(exc)
        assert text.startswith("[PV1100] invalid characters found: platform=universal")
        assert "platform=universal" in text and "value='a?b'" in text
        result = True
        """,
    ),
    scenario(
        "exception-hierarchy",
        """
        from pathvalidate import (
            InvalidCharError, InvalidReservedNameError, NullNameError, ReservedNameError,
            ValidationError, ValidReservedNameError,
        )
        assert issubclass(ValidationError, ValueError)
        assert issubclass(InvalidCharError, ValidationError)
        assert issubclass(ReservedNameError, ValidationError)
        assert issubclass(NullNameError, ValidationError)
        assert issubclass(ValidReservedNameError, ReservedNameError)
        assert issubclass(InvalidReservedNameError, ReservedNameError)
        result = True
        """,
    ),
    scenario(
        "reserved-name-handlers",
        """
        from pathvalidate import ErrorReason, ReservedNameError
        from pathvalidate.handler import ReservedNameHandler
        exc = ReservedNameError(reason=ErrorReason.RESERVED_NAME, reserved_name="CON", reusable_name=False)
        assert ReservedNameHandler.add_leading_underscore(exc) == "_CON"
        assert ReservedNameHandler.add_trailing_underscore(exc) == "CON_"
        assert ReservedNameHandler.as_is(exc) == "CON"
        reusable = ReservedNameError(reason=ErrorReason.RESERVED_NAME, reserved_name=".", reusable_name=True)
        assert ReservedNameHandler.add_leading_underscore(reusable) == "."
        assert ReservedNameHandler.add_trailing_underscore(reusable) == "."
        result = True
        """,
    ),
    scenario(
        "argparse-adapters-success",
        """
        from pathvalidate.argparse import (
            sanitize_filename_arg, sanitize_filepath_arg, validate_filename_arg,
            validate_filepath_arg,
        )
        assert validate_filename_arg("report.txt") == "report.txt"
        assert validate_filepath_arg("dir/report.txt") == "dir/report.txt"
        assert sanitize_filename_arg("a:b.txt") == "ab.txt"
        assert sanitize_filepath_arg("dir/a:b.txt") == "dir/a:b.txt"
        assert validate_filename_arg("") == ""
        result = True
        """,
    ),
    scenario(
        "argparse-adapters-errors",
        """
        from argparse import ArgumentTypeError
        from pathvalidate.argparse import validate_filename_arg, validate_filepath_arg
        for function, value in ((validate_filename_arg, "a?b"), (validate_filepath_arg, "dir/a\\x00b")):
            try:
                function(value)
            except ArgumentTypeError as exc:
                assert "PV1100" in str(exc)
            else:
                raise AssertionError(function.__name__)
        result = True
        """,
    ),
    scenario(
        "click-adapters-success",
        """
        from pathvalidate.click import (
            sanitize_filename_arg, sanitize_filepath_arg, validate_filename_arg,
            validate_filepath_arg,
        )
        assert validate_filename_arg(None, None, "report.txt") == "report.txt"
        assert validate_filepath_arg(None, None, "dir/report.txt") == "dir/report.txt"
        assert sanitize_filename_arg(None, None, "a:b.txt") == "ab.txt"
        assert sanitize_filepath_arg(None, None, "dir/a:b.txt") == "dir/ab.txt"
        assert validate_filename_arg(None, None, "") == ""
        result = True
        """,
    ),
    scenario(
        "click-adapters-errors",
        """
        import click
        from pathvalidate.click import validate_filename_arg, validate_filepath_arg
        for function, value in ((validate_filename_arg, "a?b"), (validate_filepath_arg, "dir/a?b")):
            try:
                function(None, None, value)
            except click.BadParameter as exc:
                assert "PV1100" in str(exc)
            else:
                raise AssertionError(function.__name__)
        result = True
        """,
    ),
    scenario(
        "deprecated-check-reserved-flag",
        """
        import warnings
        from pathvalidate import sanitize_filename, sanitize_filepath
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            assert sanitize_filename("CON", platform="windows", check_reserved=False) == "CON"
            assert sanitize_filepath("CON/file", platform="windows", check_reserved=False) == r"CON\\file"
        assert len(caught) == 2
        assert all(item.category is DeprecationWarning for item in caught)
        result = True
        """,
    ),
)


def _direct_self_check() -> int:
    checkout = os.environ.get("PATHVALIDATE_DIRECT_CHECKOUT")
    if not checkout:
        return -1
    sys.path.insert(0, checkout)
    failures: list[dict[str, str]] = []
    for item in SCENARIOS:
        namespace: dict[str, object] = {"__name__": "__main__"}
        try:
            exec(compile(item.source, f"<{item.leaf_id}>", "exec"), namespace)
            if namespace.get("result") is not True:
                raise AssertionError("scenario did not return True")
        except BaseException as exc:
            failures.append({"id": item.leaf_id, "error": f"{type(exc).__name__}: {exc}"})
    print(json.dumps({"total": len(SCENARIOS), "failures": failures}, sort_keys=True))
    return 1 if failures else 0


def main() -> int:
    direct = _direct_self_check()
    if direct >= 0:
        return direct

    from nl2repobench.verification.candidate_client import execute_script

    leaves: list[dict[str, str]] = []
    for item in SCENARIOS:
        observed = execute_script(item.source, timeout_sec=1.0)
        if observed.ok and observed.value is True:
            leaves.append({"id": item.leaf_id, "status": "passed"})
            continue
        detail = observed.exception_message or repr(observed.value)
        leaves.append(
            {
                "id": item.leaf_id,
                "status": "failed",
                "message": f"{observed.exception_type or 'Mismatch'}: {detail}"[:1000],
            }
        )
    print(json.dumps({"schema_version": "1.0", "leaves": leaves}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
