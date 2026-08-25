from __future__ import annotations

import json
import os
from pathlib import Path
import pwd
import shutil
import subprocess
import sys


EXPECTED = {
    "package_identity": {
        "version": "1.17.0",
        "flags": [False, True, True],
        "types": [["str"], ["int"], ["type"], "str", "bytes"],
        "maxsize": 9223372036854775807,
        "package_path": [],
    },
    "byte_literals": {
        "b_hex": "ff",
        "u": "hi \u0439",
        "unichr": "\u1234",
        "int2byte": "03",
        "int2byte_error": "error",
        "byte2int": 3,
        "byte2int_empty_error": "IndexError",
        "indexbytes": 108,
        "iterbytes": [104, 105],
    },
    "ensure_conversions": {
        "binary_from_text": "f09f9880",
        "binary_identity": True,
        "str_from_binary": "\U0001f600",
        "str_identity": True,
        "text_from_binary": "\U0001f600",
        "text_identity": True,
        "ignore": "",
        "strict_error": "UnicodeEncodeError",
        "type_errors": ["TypeError", "TypeError", "TypeError"],
    },
    "io_aliases": {
        "text": "hello",
        "binary": "68656c6c6f",
        "types": ["StringIO", "BytesIO"],
        "wrong_write": "TypeError",
    },
    "dictionary_helpers": {
        "iterkeys": ["a", "b", "c"],
        "itervalues": [1, 2, 3],
        "iteritems": [["a", 1], ["b", 2], ["c", 3]],
        "views": [["a", "b", "c"], [1, 2, 3], [["a", 1], ["b", 2], ["c", 3]]],
        "iterlists": [["a", [1, 2]]],
        "kwargs": {"marker": 42},
    },
    "function_accessors": {
        "defaults": [3],
        "code_name": "sample",
        "globals_name": "__main__",
        "closure": [42],
        "method_function": "method",
        "method_self_class": "Holder",
        "unbound_name": "method",
        "missing_method_error": "AttributeError",
    },
    "iterator_helpers": {
        "alias": True,
        "values": [1, 2],
        "exhausted": "StopIteration",
        "portable": 13,
        "callable": [True, False, True, False],
    },
    "method_constructors": {
        "bound_type": "method",
        "bound_value": 17,
        "bound_self": True,
        "unbound_value": 17,
        "unbound_error": "TypeError",
    },
    "exec_namespaces": {
        "first": 42,
        "global_y": 42,
        "global_has_x": False,
        "local_x": 12,
        "local_has_y": False,
    },
    "print_function": {
        "normal": "Hello, person!\n",
        "custom": "aXb!",
        "flushed": True,
        "errors": ["TypeError", "TypeError"],
    },
    "exception_helpers": {
        "reraise": ["ValueError", "original", True],
        "raise_from": {
            "type": "RuntimeError",
            "message": "outer",
            "cause_is_none": True,
            "context_preserved": True,
            "suppressed": True,
        },
    },
    "with_metaclass_helper": {
        "meta": "Meta",
        "bases": ["Base"],
        "mro": ["Built", "Base", "object"],
        "prepared_type": "mappingproxy",
        "prepared_values": ["Meta", ["Base"]],
        "marker": 7,
    },
    "add_metaclass_helper": {
        "meta": "Meta",
        "bases": ["Base"],
        "doc": "kept doc",
        "qualname_suffix": True,
        "slots": ["value"],
        "slot_value": 9,
        "dict_error": "AttributeError",
        "attributes": ["meta", "base"],
    },
    "unicode_decorator": {"str": "hello", "bytes": "68656c6c6f", "class": "Value"},
    "wraps_helper": {
        "name": "original",
        "doc": "original doc",
        "marker": 43,
        "settings": {"original": 1, "wrapper": 2},
        "wrapped_identity": True,
        "call": 42,
        "missing_error": "AttributeError",
    },
    "unittest_aliases": {
        "success": True,
        "count_error": "AssertionError",
        "regex_error": "AssertionError",
        "not_regex_error": "AssertionError",
    },
    "moves_modules": {
        "module_names": [
            "builtins",
            "pickle",
            "collections.abc",
            "configparser",
            "html.parser",
            "queue",
        ],
        "classes": ["ConfigParser", "Queue"],
        "dir_entries": True,
    },
    "moves_iterables": {
        "filter": [1, 3, 5],
        "filterfalse": [0, 3, 6],
        "map": [1, 2, 3],
        "range": [2, 3, 4],
        "reduce": 6,
        "zip": [[0, 2], [1, 3]],
        "zip_longest": [[0, 0], [1, None]],
    },
    "urllib_moves": {
        "parsed": ["https", "example.test", "/a", "x=1"],
        "joined": "https://example.test/b",
        "quoted": "a%20b/",
        "module_aliases": [False, False, True, True],
        "types": ["URLError", "Request", "addinfourl", "RobotFileParser"],
    },
    "custom_moves": {
        "module": ["json", 2],
        "attribute": ["JSONDecoder", 3],
        "removed": [False, False],
        "missing_error": "AttributeError",
    },
    "import_protocol": {
        "parse_identity": True,
        "parse_name": "six.moves.urllib_parse",
        "queue_name": "queue",
        "spec_names": ["six.moves.urllib_parse", "six.moves.urllib_parse", "six.moves.queue"],
        "paths": [[], []],
    },
}


def candidate_command(adapter: Path) -> list[str]:
    command = [
        "env",
        "PYTHONNOUSERSITE=1",
        "PYTHONDONTWRITEBYTECODE=1",
        "/usr/local/bin/python" if Path("/usr/local/bin/python").is_file() else sys.executable,
        "-I",
        str(adapter),
    ]
    if os.geteuid() == 0:
        try:
            pwd.getpwnam("candidate")
        except KeyError:
            pass
        else:
            command = ["runuser", "-u", "candidate", "--", *command]
    return command


def run_candidate() -> tuple[dict[str, object], str]:
    source = Path(__file__).with_name("adapter.py")
    adapter = Path(os.environ.get("NL2REPO_SIX_ADAPTER_COPY", "/tmp/six-contract-adapter.py"))
    adapter.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, adapter)
    adapter.chmod(0o444)
    requests = [
        {"id": name, "operation": name}
        for name in EXPECTED
    ]
    payload = "".join(json.dumps(item, sort_keys=True) + "\n" for item in requests)
    environment = os.environ.copy()
    local_site = environment.get("NL2REPO_SIX_CANDIDATE_SITE")
    if local_site:
        environment["NL2REPO_SIX_CANDIDATE_SITE"] = local_site
    try:
        completed = subprocess.run(
            candidate_command(adapter),
            input=payload,
            text=True,
            capture_output=True,
            timeout=45,
            check=False,
            env=environment,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        return {}, type(exc).__name__
    responses = {}
    for line in completed.stdout.splitlines():
        try:
            response = json.loads(line)
        except json.JSONDecodeError:
            continue
        if (
            isinstance(response, dict)
            and response.get("id") in EXPECTED
            and response.get("id") not in responses
        ):
            responses[response["id"]] = response
    diagnostic = f"candidate-exit={completed.returncode}; stderr={completed.stderr[-1000:]}"
    return responses, diagnostic


def main() -> None:
    responses, diagnostic = run_candidate()
    leaves = []
    for name, expected in EXPECTED.items():
        response = responses.get(name)
        passed = (
            isinstance(response, dict)
            and response.get("ok") is True
            and response.get("result") == expected
        )
        leaves.append(
            {
                "id": f"six-contract::{name}",
                "status": "passed" if passed else "failed",
                "message": "" if passed else diagnostic,
            }
        )
    print(json.dumps({"schema_version": "1.0", "leaves": leaves}, sort_keys=True))


if __name__ == "__main__":
    main()
