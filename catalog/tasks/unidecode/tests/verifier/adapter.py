#!/usr/bin/env python3
from __future__ import annotations

import importlib.metadata
import inspect
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import warnings


SITE = sys.argv[1]
CASE = sys.argv[2]
sys.path.insert(0, SITE)


def error_observation(function, *args, **kwargs):
    try:
        function(*args, **kwargs)
    except Exception as exc:
        return [type(exc).__name__, getattr(exc, "index", None), exc.__context__ is None]
    return [None, None, True]


def api_surface():
    from unidecode import Cache, UnidecodeError, unidecode, unidecode_expect_ascii, unidecode_expect_nonascii
    return {
        "alias": unidecode is unidecode_expect_ascii,
        "cache_type": type(Cache).__name__,
        "error_base": issubclass(UnidecodeError, ValueError),
        "error_index": UnidecodeError("message").index,
        "signatures": [str(inspect.signature(unidecode_expect_ascii)), str(inspect.signature(unidecode_expect_nonascii))],
    }


def package_contract():
    import unidecode
    return {
        "version": importlib.metadata.version("Unidecode"),
        "typed": Path(unidecode.__file__).with_name("py.typed").is_file(),
    }


def ascii_identity():
    from unidecode import unidecode
    values = [unidecode(chr(code)) for code in range(128)]
    return {"all_equal": values == [chr(code) for code in range(128)], "all_str": all(type(value) is str for value in values)}


def western():
    from unidecode import unidecode
    return [unidecode(value) for value in ("kožušček", "ČŽŠčžš", "příliš žluťoučký kůň pěl ďábelské ódy")]


def multiscript():
    from unidecode import unidecode
    return [unidecode(value) for value in ("Κνωσός", "Привет мир!", "ア", "こんにちは世界", "北京")]


def mixed_text():
    from unidecode import unidecode
    return [unidecode(value) for value in ("Hello, 世界!", "Efﬁcient", "30 km/h ± 5%", "℉℃")]


def wide_unicode():
    from unidecode import unidecode
    return [unidecode("𝐀𝐚𝟎𝟏𝟐𝟑𝟒𝟓𝟔𝟕𝟖𝟗"), unidecode("𝐤𝐦/𝐡")]


def enclosed_fullwidth():
    from unidecode import unidecode
    return [unidecode("ⓐⒶ⑳⒇⒛⓴⓾⓿"), unidecode("ｔｈｅ ｑｕｉｃｋ")]


def entrypoint_equivalence():
    from unidecode import unidecode, unidecode_expect_ascii, unidecode_expect_nonascii
    return [function("ČŽŠčžš") for function in (unidecode, unidecode_expect_ascii, unidecode_expect_nonascii)]


def empty_and_controls():
    from unidecode import unidecode
    return [unidecode(""), unidecode("Hello, World!\r\n"), unidecode("\0\t\n")]


def errors_ignore():
    from unidecode import unidecode
    return unidecode("test \U000f0000 test", errors="ignore")


def errors_replace():
    from unidecode import unidecode
    value = "test \U000f0000 test"
    return [unidecode(value, errors="replace"), unidecode(value, errors="replace", replace_str="[?] ")]


def errors_strict():
    from unidecode import unidecode
    try:
        unidecode("test \U000f0000 test", errors="strict")
    except Exception as exc:
        return [type(exc).__name__, getattr(exc, "index", None), "position 5" in str(exc), exc.__context__ is None]
    return [None, None, False, True]


def errors_preserve():
    from unidecode import unidecode
    result = unidecode("test \U000f0000 test", errors="preserve")
    return [result, result.isascii()]


def errors_invalid():
    from unidecode import unidecode
    return error_observation(unidecode, "test \U000f0000 test", errors="invalid")


def surrogate_warning():
    from unidecode import unidecode
    with warnings.catch_warnings(record=True) as seen:
        warnings.simplefilter("always")
        result = unidecode("\ud800")
    return [result, len(seen), seen[0].category.__name__ if seen else None, bool(seen and "Surrogate character" in str(seen[0].message))]


def cache_lazy_hit():
    import sys as local_sys
    from unidecode import Cache, unidecode_expect_nonascii
    Cache.clear()
    before = "unidecode.x001" in local_sys.modules
    first = unidecode_expect_nonascii("Č")
    loaded = "unidecode.x001" in local_sys.modules
    keys = sorted(Cache)
    table = Cache[1]
    second = unidecode_expect_nonascii("Ž")
    return [before, first, loaded, keys, second, Cache[1] is table]


def cache_missing_block():
    from unidecode import Cache, unidecode_expect_nonascii
    Cache.clear()
    first = unidecode_expect_nonascii("\ua500")
    keys = sorted(Cache)
    missing = Cache.get(0xA5) is None and 0xA5 in Cache
    second = unidecode_expect_nonascii("\ua501")
    return [first, keys, missing, second, Cache.get(0xA5) is None]


def cli_command_text():
    code = "import sys;sys.path.insert(0,sys.argv.pop(1));from unidecode.util import main;main()"
    completed = subprocess.run([sys.executable, "-I", "-c", code, SITE, "-c", "北京"], text=True, capture_output=True, check=False)
    return [completed.returncode, completed.stdout, completed.stderr]


def cli_streams():
    code = "import sys;sys.path.insert(0,sys.argv.pop(1));from unidecode.util import main;main()"
    stdin_run = subprocess.run([sys.executable, "-I", "-c", code, SITE], input="革".encode(), capture_output=True, check=False)
    with tempfile.NamedTemporaryFile() as handle:
        handle.write("革".encode("utf-8"))
        handle.flush()
        file_run = subprocess.run([sys.executable, "-I", "-c", code, SITE, "-e", "utf-8", handle.name], capture_output=True, check=False)
    return [stdin_run.returncode, stdin_run.stdout.decode("ascii"), file_run.returncode, file_run.stdout.decode("ascii")]


OPERATIONS = {
    "api-surface": api_surface,
    "package-contract": package_contract,
    "ascii-identity": ascii_identity,
    "western": western,
    "multiscript": multiscript,
    "mixed-text": mixed_text,
    "wide-unicode": wide_unicode,
    "enclosed-fullwidth": enclosed_fullwidth,
    "entrypoint-equivalence": entrypoint_equivalence,
    "empty-and-controls": empty_and_controls,
    "errors-ignore": errors_ignore,
    "errors-replace": errors_replace,
    "errors-strict": errors_strict,
    "errors-preserve": errors_preserve,
    "errors-invalid": errors_invalid,
    "surrogate-warning": surrogate_warning,
    "cache-lazy-hit": cache_lazy_hit,
    "cache-missing-block": cache_missing_block,
    "cli-command-text": cli_command_text,
    "cli-streams": cli_streams,
}


try:
    result = OPERATIONS[CASE]()
    response = {"case": CASE, "ok": True, "result": result}
except BaseException as exc:
    response = {"case": CASE, "ok": False, "error": f"{type(exc).__name__}: {exc}"}
print(json.dumps(response, ensure_ascii=True, sort_keys=True))
