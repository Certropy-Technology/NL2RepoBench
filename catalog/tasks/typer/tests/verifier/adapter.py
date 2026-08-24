"""Private child adapter for the typer deterministic noninteractive CLI slice.

Runs unprivileged with the candidate site on ``sys.path``. It accepts only a
bounded JSON request naming an allowlisted fixture plus an argv list and
optional stdin text. Every Python callback, annotation, enum, ``Typer``
application and ``CliRunner`` object is constructed *inside this child* from
the allowlisted fixture table below; no callable, import path, filesystem path
or Python source ever crosses the JSON boundary. The child returns a bounded
JSON-safe observation of the invocation.
"""

import argparse
import enum
import json
import os
import sys
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple

FIXTURE_SCHEMA_VERSION = "typer-fixture-v1"


def build_scalars():
    """Single command exercising scalar argument/option conversion."""
    import typer

    app = typer.Typer(add_completion=False)

    @app.command()
    def main(
        name: str,
        count: int = 1,
        ratio: float = 0.5,
        flag: bool = False,
    ):
        """Echoes converted scalar values.

        Args are converted by typer before this callback runs.
        """
        typer.echo("name=%s type=%s" % (name, type(name).__name__))
        typer.echo("count=%s type=%s" % (count, type(count).__name__))
        typer.echo("ratio=%s type=%s" % (ratio, type(ratio).__name__))
        typer.echo("flag=%s type=%s" % (flag, type(flag).__name__))

    return app


def build_required():
    """Single command with a required option and an env-var option."""
    import typer

    app = typer.Typer(add_completion=False)

    @app.command()
    def main(
        token: str = typer.Option(..., "--token", help="Required token."),
        region: str = typer.Option("local", "--region", envvar="SLICE_REGION"),
    ):
        typer.echo("token=%s region=%s" % (token, region))

    return app


class Level(str, enum.Enum):
    low = "low"
    high = "high"


def build_enum():
    """Single command converting an enum choice back into a Python member."""
    import typer

    app = typer.Typer(add_completion=False)

    @app.command()
    def main(level: Level = Level.low):
        typer.echo("level=%s member=%s type=%s" % (level.value, level.name, type(level).__name__))

    return app


def build_containers():
    """Single command exercising list, fixed tuple and optional values."""
    import typer

    app = typer.Typer(add_completion=False)

    @app.command()
    def main(
        tag: List[str] = typer.Option([], "--tag"),
        pair: Tuple[str, int] = typer.Option(("none", 0), "--pair"),
        note: Optional[str] = typer.Option(None, "--note"),
    ):
        typer.echo("tag=%s type=%s" % (list(tag), type(tag).__name__))
        typer.echo("pair=%s types=%s" % (list(pair), [type(item).__name__ for item in pair]))
        typer.echo("note=%s type=%s" % (note, type(note).__name__))

    return app


def build_richtypes():
    """Single command converting UUID, datetime and Path values."""
    import typer

    app = typer.Typer(add_completion=False)

    @app.command()
    def main(
        identifier: uuid.UUID = typer.Option(..., "--id"),
        when: datetime = typer.Option(..., "--when"),
        target: Path = typer.Option(..., "--target"),
    ):
        typer.echo("id=%s type=%s" % (identifier, type(identifier).__name__))
        typer.echo("when=%s type=%s" % (when.isoformat(), type(when).__name__))
        typer.echo("target=%s type=%s" % (target.as_posix(), type(target).__name__))

    return app


def build_group():
    """Multi-command application with a group callback and result state."""
    import typer

    app = typer.Typer(add_completion=False)
    state = {"verbose": False}

    @app.callback()
    def root(verbose: bool = typer.Option(False, "--verbose")):
        """Root group callback."""
        state["verbose"] = verbose

    @app.command()
    def add(alpha: int, beta: int = 2):
        """Adds two integers."""
        typer.echo("sum=%s verbose=%s" % (alpha + beta, state["verbose"]))

    @app.command(name="join-words")
    def join_words(words: List[str], separator: str = typer.Option("-", "--separator")):
        """Joins words."""
        typer.echo(separator.join(words))

    return app


def build_nested():
    """Nested sub-application registered with add_typer."""
    import typer

    app = typer.Typer(add_completion=False)
    child = typer.Typer(add_completion=False)

    @child.command()
    def show(value: int):
        """Shows a doubled value."""
        typer.echo("doubled=%s" % (value * 2))

    app.add_typer(child, name="items", help="Item commands.")

    @app.command()
    def version():
        """Prints a fixed version string."""
        typer.echo("slice-1")

    return app


def build_streams():
    """Single command exercising prompt input, stderr and styled output."""
    import typer

    app = typer.Typer(add_completion=False)

    @app.command()
    def main(
        label: str = typer.Option(..., "--label", prompt="Label"),
        fail: bool = typer.Option(False, "--fail"),
    ):
        typer.echo("label=%s" % label)
        typer.echo("warned", err=True)
        typer.echo(typer.style("styled", fg=typer.colors.GREEN))
        if fail:
            raise typer.Exit(code=3)

    return app


def build_failing():
    """Single command that raises an ordinary Python exception."""
    import typer

    app = typer.Typer(add_completion=False)

    @app.command()
    def main(reason: str = typer.Option("boom", "--reason")):
        raise ValueError(reason)

    return app


FIXTURES = {
    "scalars": build_scalars,
    "required": build_required,
    "enum": build_enum,
    "containers": build_containers,
    "richtypes": build_richtypes,
    "group": build_group,
    "nested": build_nested,
    "streams": build_streams,
    "failing": build_failing,
}

# Only these environment names may be set per invocation, and only to strings.
ALLOWED_ENV = ("SLICE_REGION",)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate-site", required=True)
    parser.add_argument("--request", required=True)
    arguments = parser.parse_args()
    # ``python -I`` intentionally ignores inherited PYTHONPATH. Add the
    # compiler-installed candidate dependency site explicitly so runtime
    # dependencies such as rich and shellingham stay isolated from trusted
    # packages.
    sys.path.insert(0, os.environ.get("NL2REPO_CANDIDATE_DEPENDENCIES", "/opt/candidate-dependencies/site"))
    sys.path.insert(0, arguments.candidate_site)
    request = json.loads(arguments.request)
    if request.get("fixture_schema") != FIXTURE_SCHEMA_VERSION:
        raise ValueError("unsupported fixture schema")
    operation = request["operation"]

    if operation == "api":
        import typer
        import typer.testing

        module = __import__("importlib").import_module("typer.cli")
        names = ("Typer", "Option", "Argument", "Context", "Exit", "Abort", "echo", "secho", "style", "run")
        return {
            "version": typer.__version__,
            "exports": {name: callable(getattr(typer, name, None)) for name in names},
            "has_cli_main": callable(getattr(module, "main", None)),
            "runner": callable(getattr(typer.testing.CliRunner, "invoke", None)),
        }

    if operation != "invoke":
        raise ValueError("unknown operation")

    argv = list(request.get("argv", []))
    for token in argv:
        if not isinstance(token, str):
            raise ValueError("argv must be strings")
    stdin_text = request.get("input")
    if stdin_text is not None and not isinstance(stdin_text, str):
        raise ValueError("input must be a string")
    env = {}
    for key, value in sorted((request.get("env") or {}).items()):
        if key not in ALLOWED_ENV or not isinstance(value, str):
            raise ValueError("environment name is outside the scored slice")
        env[key] = value

    import typer.testing

    app = FIXTURES[request["fixture"]]()
    runner = typer.testing.CliRunner()
    result = runner.invoke(app, argv, input=stdin_text, env=env or None, catch_exceptions=True)
    exception = result.exception
    return {
        "exit_code": result.exit_code,
        "exception": None if exception is None else type(exception).__name__,
        "stdout": result.stdout,
        "stderr": result.stderr,
    }


try:
    print(
        json.dumps(
            {"ok": True, "value": main()},
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
    )
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
