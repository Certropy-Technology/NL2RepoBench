"""Safety patches and entrypoint for the pinned Harbor runner.

Harbor 0.21.0 stores per-phase environment overlays in ``ContextVar``
instances.  Under Python 3.14, cancellation during an upstream/API failure can
unwind the context manager in a different asyncio context.  A direct
``ContextVar.reset(token)`` then raises ``ValueError`` and prevents Docker
environment cleanup, leaving the intentionally long-lived ``sleep infinity``
environment container orphaned.

This module is loaded only by the repository's Harbor entrypoint.  It does not
change Harbor scoring or retry classification; it makes cleanup best-effort and
idempotent when the runner is already unwinding after cancellation.
"""

from __future__ import annotations

import contextvars
from collections.abc import Callable, Generator
from contextlib import contextmanager
from typing import Any, TypeVar

T = TypeVar("T")


def reset_contextvar_safely(
    variable: contextvars.ContextVar[T],
    token: contextvars.Token[T],
    fallback: T,
) -> None:
    """Reset a context variable, restoring a fallback after context migration.

    ``ContextVar.reset`` is strict about token ownership.  During cancellation
    the token may belong to the task context that created it while finalization
    executes in another context.  Setting the known previous value in the
    current context is the only safe fallback; it prevents overlay leakage and
    lets the caller continue to Docker cleanup.
    """

    try:
        variable.reset(token)
    except ValueError:
        variable.set(fallback)


def _safe_scoped_exec_env(self: Any, env: dict[str, str]) -> Generator[None, None, None]:
    variable = self._exec_env_overlays
    previous = variable.get()
    token = variable.set((*previous, dict(env)))
    try:
        yield
    finally:
        reset_contextvar_safely(variable, token, previous)


def _safe_scoped_output_callback(
    self: Any, callback: Callable[..., Any] | None
) -> Generator[None, None, None]:
    if callback is None:
        yield
        return
    variable = self._output_callbacks
    previous = variable.get()
    token = variable.set((*previous, callback))
    try:
        yield
    finally:
        reset_contextvar_safely(variable, token, previous)


def install_harbor_cleanup_patch() -> None:
    """Install the idempotent Harbor context-cleanup patch before CLI startup."""

    from harbor.environments import base  # type: ignore[import-not-found]

    marker = "_nl2repo_cleanup_patch_installed"
    if getattr(base.BaseEnvironment, marker, False):
        return
    base.BaseEnvironment.scoped_exec_env = contextmanager(_safe_scoped_exec_env)
    base.BaseEnvironment.scoped_output_callback = contextmanager(_safe_scoped_output_callback)
    setattr(base.BaseEnvironment, marker, True)


def main() -> None:
    """Patch Harbor, then execute the normal pinned Harbor Typer application."""

    install_harbor_cleanup_patch()
    from harbor.cli.main import app  # type: ignore[import-not-found]

    app()


if __name__ == "__main__":  # pragma: no cover - exercised in Harbor image
    main()
