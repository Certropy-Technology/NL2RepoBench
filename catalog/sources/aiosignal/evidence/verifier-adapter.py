from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
from typing import Any


def type_name(exc: BaseException) -> str:
    return f"{type(exc).__module__}.{type(exc).__qualname__}"


async def exercise(scenario: str) -> Any:
    from aiosignal import Signal

    if scenario == "empty-frozen":
        signal = Signal("owner")
        before = (len(signal), signal.frozen)
        signal.freeze()
        return {"before": list(before), "after": [len(signal), signal.frozen]}

    if scenario == "positional-forwarding":
        seen: list[list[Any]] = []

        async def receiver(number: int, text: str) -> None:
            seen.append([number, text])

        signal = Signal(object())
        signal.append(receiver)
        signal.freeze()
        result = await signal.send(42, "ok")
        return {"seen": seen, "result": result}

    if scenario == "keyword-forwarding":
        seen: list[dict[str, Any]] = []

        async def receiver(**kwargs: Any) -> None:
            seen.append(kwargs)

        signal = Signal(None)
        signal.append(receiver)
        signal.freeze()
        await signal.send(alpha=1, beta="two")
        return seen

    if scenario == "order-and-mixed-forwarding":
        seen: list[list[Any]] = []

        async def first(*args: Any, **kwargs: Any) -> None:
            seen.append(["first", list(args), kwargs])

        async def second(*args: Any, **kwargs: Any) -> None:
            seen.append(["second", list(args), kwargs])

        signal = Signal("x")
        signal.extend([first, second])
        signal.freeze()
        await signal.send("a", "b", flag=True)
        return seen

    if scenario == "reject-non-callable":
        signal = Signal(None)
        signal.append(True)  # type: ignore[arg-type]
        signal.freeze()
        try:
            await signal.send()
        except Exception as exc:
            return type_name(exc)
        return None

    if scenario == "reject-non-awaitable":
        signal = Signal(None)
        signal.append(lambda: None)  # type: ignore[arg-type]
        signal.freeze()
        try:
            await signal.send()
        except Exception as exc:
            return type_name(exc)
        return None

    if scenario in {"append-after-freeze", "set-after-freeze", "delete-after-freeze"}:
        signal = Signal(None)
        signal.append(lambda: None)  # type: ignore[arg-type]
        signal.freeze()
        try:
            if scenario == "append-after-freeze":
                signal.append(lambda: None)  # type: ignore[arg-type]
            elif scenario == "set-after-freeze":
                signal[0] = lambda: None  # type: ignore[assignment]
            else:
                del signal[0]
        except Exception as exc:
            return {"error": type_name(exc), "length": len(signal)}
        return {"error": None, "length": len(signal)}

    if scenario == "send-before-freeze":
        called = False

        async def receiver() -> None:
            nonlocal called
            called = True

        signal = Signal(None)
        signal.append(receiver)
        try:
            await signal.send()
        except Exception as exc:
            return {"error": type_name(exc), "called": called}
        return {"error": None, "called": called}

    if scenario == "decorator-registration":
        seen: list[str] = []
        signal = Signal(None)

        @signal
        async def receiver() -> None:
            seen.append("called")

        signal.freeze()
        await signal.send()
        return {"same": receiver in signal, "seen": seen}

    if scenario == "repr":
        class Owner:
            def __repr__(self) -> str:
                return "<Owner>"

        signal = Signal(Owner())
        signal.append(lambda: None)  # type: ignore[arg-type]
        return repr(signal)

    if scenario == "stop-on-error":
        seen: list[str] = []

        async def failing() -> None:
            seen.append("before-error")
            raise ValueError("boom")

        async def after() -> None:
            seen.append("after")

        signal = Signal(None)
        signal.extend([failing, after])
        signal.freeze()
        try:
            await signal.send()
        except Exception as exc:
            return {"error": type_name(exc), "seen": seen}
        return {"error": None, "seen": seen}

    raise ValueError("unknown scenario")


async def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate-site", required=True)
    parser.add_argument("--scenario", required=True)
    args = parser.parse_args()
    if os.path.realpath(args.candidate_site) != "/tmp/candidate-site":
        raise ValueError("candidate site is unavailable")
    sys.path.insert(0, args.candidate_site)
    print(json.dumps({"ok": True, "value": await exercise(args.scenario)}, sort_keys=True))


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except BaseException as exc:
        print(json.dumps({"ok": False, "exception_type": type_name(exc), "exception_message": str(exc)}, sort_keys=True))
