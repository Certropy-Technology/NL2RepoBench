from __future__ import annotations

import contextvars

from nl2repobench.harbor_runner_safety import reset_contextvar_safely


def test_contextvar_reset_falls_back_in_a_different_context() -> None:
    variable: contextvars.ContextVar[tuple[str, ...]] = contextvars.ContextVar(
        "test_overlay", default=()
    )
    token = variable.set(("overlay",))
    other_context = contextvars.copy_context()

    other_context.run(reset_contextvar_safely, variable, token, ())

    # The fallback is installed in the context that performed finalization.
    assert other_context.get(variable) == ()
    # The creating context retains its own value and can safely be restored by
    # its owner; the helper never mutates a different Context object.
    assert variable.get() == ("overlay",)
    variable.reset(token)


def test_same_context_reset_uses_the_original_token() -> None:
    variable: contextvars.ContextVar[tuple[str, ...]] = contextvars.ContextVar(
        "test_overlay_same", default=()
    )
    token = variable.set(("overlay",))
    reset_contextvar_safely(variable, token, ())
    assert variable.get() == ()
