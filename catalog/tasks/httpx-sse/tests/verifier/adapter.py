from __future__ import annotations

import argparse
import asyncio
import json
import sys
from typing import Any, Iterator

sys.path[:0] = ["/tmp/candidate-site", "/opt/candidate-dependencies/site"]

import httpx


def exc_name(exc: BaseException) -> str:
    return f"{type(exc).__module__}.{type(exc).__qualname__}"


class SyncBody(httpx.SyncByteStream):
    def __init__(self, chunks: list[bytes]) -> None:
        self.chunks = chunks

    def __iter__(self) -> Iterator[bytes]:
        yield from self.chunks


class AsyncBody(httpx.AsyncByteStream):
    def __init__(self, chunks: list[bytes]) -> None:
        self.chunks = chunks

    async def __aiter__(self) -> Any:
        for chunk in self.chunks:
            yield chunk


def sync_response(text: str, *, content_type: str = "text/event-stream") -> Any:
    import httpx

    return httpx.Response(
        200,
        headers={"content-type": content_type},
        stream=SyncBody([text.encode("utf-8")]),
    )


async def exercise(scenario: str) -> Any:
    import httpx
    from httpx_sse import (
        EventSource,
        SSEError,
        ServerSentEvent,
        aconnect_sse,
        connect_sse,
    )

    if scenario == "exports":
        import httpx_sse

        return {
            "version": httpx_sse.__version__,
            "all": list(httpx_sse.__all__),
            "symbols": all(hasattr(httpx_sse, name) for name in httpx_sse.__all__),
        }
    if scenario == "sse-default":
        event = ServerSentEvent()
        return {"event": event.event, "data": event.data, "id": event.id, "retry": event.retry}
    if scenario == "sse-fields":
        event = ServerSentEvent(event="update", data="payload", id="evt-7", retry=2500)
        return {"event": event.event, "data": event.data, "id": event.id, "retry": event.retry}
    if scenario == "sse-json":
        return ServerSentEvent(data='{"items": [1, 2], "ok": true}').json()
    if scenario == "sse-repr":
        return repr(ServerSentEvent(event="update", data="payload", id="evt-7", retry=2500))
    if scenario == "multiline":
        events = list(EventSource(sync_response("data: one\ndata: two\n\n")).iter_sse())
        return [[event.event, event.data, event.id, event.retry] for event in events]
    if scenario == "line-endings":
        events = list(EventSource(sync_response("event: x\rdata: y\r\r\ndata: z\r\n\r\n")).iter_sse())
        return [[event.event, event.data] for event in events]
    if scenario == "chunk-boundary":
        response = httpx.Response(
            200,
            headers={"content-type": "text/event-stream"},
            stream=SyncBody([b"data: hel", b"lo\r", b"\n", b"\r\n"]),
        )
        return [[event.event, event.data] for event in EventSource(response).iter_sse()]
    if scenario == "flush":
        response = httpx.Response(
            200,
            headers={"content-type": "text/event-stream"},
            stream=SyncBody([b"data: partial"]),
        )
        return [[event.event, event.data] for event in EventSource(response).iter_sse()]
    if scenario == "comment-unknown":
        events = list(EventSource(sync_response(": comment\nsomething: ignored\n\n")).iter_sse())
        return len(events)
    if scenario == "id-retry":
        text = "id: first\nretry: 1500\ndata: one\n\ndata: two\n\n"
        events = list(EventSource(sync_response(text)).iter_sse())
        return [[event.data, event.id, event.retry] for event in events]
    if scenario == "nul-id":
        events = list(EventSource(sync_response("id: bad\0id\ndata: ok\n\n")).iter_sse())
        return [[event.data, event.id] for event in events]
    if scenario == "invalid-retry":
        events = list(EventSource(sync_response("retry: nope\n\n")).iter_sse())
        return len(events)
    if scenario == "data-spacing":
        text = "data:no-space\ndata: one-space\ndata:  two-spaces\n\n"
        events = list(EventSource(sync_response(text)).iter_sse())
        return events[0].data
    if scenario == "empty-dispatch":
        text = "event: empty\n\n"
        events = list(EventSource(sync_response(text)).iter_sse())
        return [[event.event, event.data] for event in events]
    if scenario == "unicode-separator":
        text = 'data: {"text":"Hello\u2028World"}\n\n'
        events = list(EventSource(sync_response(text)).iter_sse())
        return events[0].json()
    if scenario == "response-identity":
        response = sync_response("data: x\n\n")
        return EventSource(response).response is response
    if scenario == "content-type-parameter":
        event = list(EventSource(sync_response("data: x\n\n", content_type="text/event-stream; charset=utf-8")).iter_sse())[0]
        return event.data
    if scenario == "wrong-content-type":
        try:
            list(EventSource(sync_response("data: x\n\n", content_type="application/json")).iter_sse())
        except Exception as exc:
            return exc_name(exc), isinstance(exc, SSEError), isinstance(exc, httpx.TransportError)
        return None
    if scenario == "connect-headers":
        seen: dict[str, Any] = {}

        def handler(request: httpx.Request) -> httpx.Response:
            seen.update({"method": request.method, "path": request.url.path, "accept": request.headers.get("accept"), "cache": request.headers.get("cache-control")})
            return httpx.Response(200, headers={"content-type": "text/event-stream"}, text="data: connected\n\n")

        with httpx.Client(transport=httpx.MockTransport(handler)) as client:
            with connect_sse(client, "POST", "http://testserver/events", headers={"X-Test": "yes"}) as source:
                data = [event.data for event in source.iter_sse()]
        return {"seen": seen, "data": data}
    if scenario == "connect-method-forwarding":
        seen: dict[str, Any] = {}

        def handler(request: httpx.Request) -> httpx.Response:
            seen["method"] = request.method
            seen["url"] = str(request.url)
            return httpx.Response(200, headers={"content-type": "text/event-stream"}, text="data: ok\n\n")

        with httpx.Client(transport=httpx.MockTransport(handler)) as client:
            with connect_sse(client, "PUT", "http://testserver/a?x=1", content=b"body") as source:
                data = [event.data for event in source.iter_sse()]
        return {"seen": seen, "data": data}
    if scenario == "connect-custom-header-overrides":
        seen: dict[str, str | None] = {}

        def handler(request: httpx.Request) -> httpx.Response:
            seen["accept"] = request.headers.get("accept")
            seen["cache"] = request.headers.get("cache-control")
            return httpx.Response(200, headers={"content-type": "text/event-stream"}, text="data: ok\n\n")

        with httpx.Client(transport=httpx.MockTransport(handler)) as client:
            with connect_sse(client, "GET", "http://testserver", headers={"Accept": "application/json", "Cache-Control": "max-age=10"}):
                pass
        return seen
    if scenario == "async-iteration":
        response = httpx.Response(
            200,
            headers={"content-type": "text/event-stream"},
            stream=AsyncBody([b"data: async\n", b"data: value\n", b"\n"]),
        )
        events = [event async for event in EventSource(response).aiter_sse()]
        return [[event.event, event.data] for event in events]
    if scenario == "async-connect":
        seen: dict[str, str | None] = {}

        def handler(request: httpx.Request) -> httpx.Response:
            seen["accept"] = request.headers.get("accept")
            seen["cache"] = request.headers.get("cache-control")
            return httpx.Response(200, headers={"content-type": "text/event-stream"}, text="data: async-connected\n\n")

        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            async with aconnect_sse(client, "GET", "http://testserver/sse") as source:
                data = [event.data async for event in source.aiter_sse()]
        return {"seen": seen, "data": data}
    if scenario == "async-flush":
        response = httpx.Response(
            200,
            headers={"content-type": "text/event-stream"},
            stream=AsyncBody([b"data: async-partial"]),
        )
        events = [event async for event in EventSource(response).aiter_sse()]
        return [[event.event, event.data] for event in events]
    if scenario == "async-error":
        response = httpx.Response(
            200,
            headers={"content-type": "application/octet-stream"},
            stream=AsyncBody([b"data: no\n\n"]),
        )
        try:
            [event async for event in EventSource(response).aiter_sse()]
        except Exception as exc:
            return exc_name(exc)
        return None
    raise ValueError(f"unknown scenario: {scenario}")


async def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate-site", required=True)
    parser.add_argument("--scenario", required=True)
    args = parser.parse_args()
    if args.candidate_site != "/tmp/candidate-site":
        raise ValueError("unexpected candidate site")
    sys.path.insert(0, args.candidate_site)
    try:
        value = await exercise(args.scenario)
        print(json.dumps({"ok": True, "value": value}, sort_keys=True))
    except BaseException as exc:
        print(json.dumps({"ok": False, "exception_type": exc_name(exc), "exception_message": str(exc)}, sort_keys=True))


if __name__ == "__main__":
    asyncio.run(main())
