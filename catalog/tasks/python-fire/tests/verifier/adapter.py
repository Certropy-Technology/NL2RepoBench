"""Private child adapter for the python-fire deterministic noninteractive slice.

Runs unprivileged with the candidate site on ``sys.path``. It accepts only a
bounded JSON request naming an allowlisted fixture component plus an argv list.
It never accepts Python source, import paths, filesystem paths, callables or
shell commands, and it never starts a REPL or a pager.
"""

import argparse
import io
import json
import os
import sys

FIXTURE_SCHEMA_VERSION = "fire-fixture-v1"


def build_add():
    def add(alpha, beta=2, *rest, gamma=False):
        """Adds numbers.

        Args:
          alpha: The first addend.
          beta: The second addend.
          *rest: Extra addends.
          gamma: Whether to negate the sum.
        """
        total = alpha + beta + sum(rest)
        return -total if gamma else total

    return add


def build_types_echo():
    def echo(value):
        """Reports the parsed type and value of a single argument."""
        return {"type": type(value).__name__, "text": repr(value)}

    return echo


def build_failing():
    def explode(reason="boom"):
        """Always raises a ValueError."""
        raise ValueError(reason)

    return explode


def build_calculator():
    class Calculator:
        """A simple calculator."""

        def __init__(self, offset=0):
            self.offset = offset

        def double(self, value):
            """Doubles a value and adds the offset."""
            return value * 2 + self.offset

        def join(self, *words, separator="-"):
            """Joins words."""
            return separator.join(str(word) for word in words)

        def label(self):
            """Returns the configured offset label."""
            return "offset=%s" % self.offset

    return Calculator


def build_mapping():
    return {
        "value": 7,
        "words": ["alpha", "beta"],
        "nested": {"depth": 2, "name": "café"},
        "upper": build_calculator(),
    }


def build_sequence():
    return [10, 20, 30]


FIXTURES = {
    "add-function": build_add,
    "types-echo": build_types_echo,
    "failing-function": build_failing,
    "calculator-class": build_calculator,
    "mapping": build_mapping,
    "sequence": build_sequence,
}


def normalize(value):
    if value is None or isinstance(value, (bool, int, float, str)):
        return {"kind": type(value).__name__, "value": value}
    if isinstance(value, (list, tuple)):
        return {"kind": type(value).__name__, "value": [normalize(item) for item in value]}
    if isinstance(value, dict):
        return {
            "kind": "dict",
            "value": {str(key): normalize(item) for key, item in sorted(value.items(), key=lambda pair: str(pair[0]))},
        }
    return {"kind": "other", "value": type(value).__name__}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate-site", required=True)
    parser.add_argument("--request", required=True)
    arguments = parser.parse_args()
    # ``python -I`` intentionally ignores inherited PYTHONPATH. Add the
    # compiler-installed candidate dependency site explicitly so runtime
    # dependencies such as termcolor remain isolated from trusted packages.
    sys.path.insert(0, os.environ.get("NL2REPO_CANDIDATE_DEPENDENCIES", "/opt/candidate-dependencies/site"))
    sys.path.insert(0, arguments.candidate_site)
    request = json.loads(arguments.request)
    if request.get("fixture_schema") != FIXTURE_SCHEMA_VERSION:
        raise ValueError("unsupported fixture schema")
    operation = request["operation"]

    if operation == "api":
        import fire

        module = __import__("importlib").import_module("fire.__main__")
        print(
            json.dumps(
                {
                    "ok": True,
                    "value": {
                        "version": fire.__version__,
                        "all": sorted(getattr(fire, "__all__", [])),
                        "callable_fire": callable(fire.Fire),
                        "has_main": callable(getattr(module, "main", None)),
                    },
                },
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            )
        )
        return

    if operation != "invoke":
        raise ValueError("unknown operation")

    argv = list(request.get("argv", []))
    for token in argv:
        if not isinstance(token, str):
            raise ValueError("argv must be strings")
        if token in ("-i", "--interactive", "--"):
            raise ValueError("interactive and separator tokens are outside the scored slice")

    component = FIXTURES[request["fixture"]]()
    import fire

    stdout = io.StringIO()
    stderr = io.StringIO()
    saved = (sys.stdout, sys.stderr)
    sys.stdout, sys.stderr = stdout, stderr
    exit_code = 0
    exception = None
    result = None
    try:
        result = fire.Fire(component, command=argv, name=request.get("name", "tool"))
    except SystemExit as error:
        exit_code = error.code if isinstance(error.code, int) else 1
    except BaseException as error:  # noqa: BLE001 - reported as data, not raised
        exit_code = 1
        exception = type(error).__name__
    finally:
        sys.stdout, sys.stderr = saved

    print(
        json.dumps(
            {
                "ok": True,
                "value": {
                    "exit_code": exit_code,
                    "exception": exception,
                    "result": normalize(result),
                    "stdout": stdout.getvalue(),
                    "stderr": stderr.getvalue(),
                },
            },
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
    )


try:
    main()
except BaseException as error:  # noqa: BLE001 - protocol-level failure report
    print(
        json.dumps(
            {
                "ok": False,
                "exception_type": type(error).__module__ + "." + type(error).__qualname__,
                "exception_message": str(error),
            },
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
    )
