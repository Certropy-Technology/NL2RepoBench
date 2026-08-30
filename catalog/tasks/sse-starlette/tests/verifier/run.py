from __future__ import annotations

import json

from nl2repobench.verification.candidate_client import execute_script


def check(case_id: str, source: str, expected: object) -> dict[str, object]:
    observed = execute_script(source, timeout_sec=25.0)
    actual: dict[str, object] = {"ok": observed.ok, "value": observed.value}
    if not observed.ok:
        actual["exception_type"] = observed.exception_type
        actual["exception_message"] = observed.exception_message
    return {
        "id": case_id,
        "status": "passed" if actual == expected else "failed",
        **({} if actual == expected else {"message": json.dumps(actual, sort_keys=True)}),
    }


CASES: list[tuple[str, str, object]] = [
    (
        "exports-version",
        "import sse_starlette as s; result = [s.__version__, sorted(s.__all__), s.EventSourceResponse.__name__]",
        {"ok": True, "value": ["3.4.8", ["EventSourceResponse", "JSONServerSentEvent", "ServerSentEvent"], "EventSourceResponse"]},
    ),
    (
        "event-basic",
        "from sse_starlette.event import ServerSentEvent; result = ServerSentEvent('hello', event='update', id='7', retry=5000).encode().decode()",
        {"ok": True, "value": "id: 7\r\nevent: update\r\ndata: hello\r\nretry: 5000\r\n\r\n"},
    ),
    (
        "event-multiline",
        "from sse_starlette.event import ServerSentEvent; result = ServerSentEvent('a\\nb\\rc', comment='x\\ny', sep='\\n').encode().decode()",
        {"ok": True, "value": ": x\n: y\ndata: a\ndata: b\ndata: c\n\n"},
    ),
    (
        "event-sanitize",
        "from sse_starlette.event import ServerSentEvent; result = ServerSentEvent('v', event='e\\r\\nx', id='i\\n\\ny').encode().decode()",
        {"ok": True, "value": "id: iy\r\nevent: ex\r\ndata: v\r\n\r\n"},
    ),
    (
        "event-comment-only",
        "from sse_starlette.event import ServerSentEvent; result = ServerSentEvent(comment='ping').encode()",
        {"ok": True, "value": "b': ping\\r\\n\\r\\n'"},
    ),
    (
        "event-retry-type",
        "from sse_starlette.event import ServerSentEvent; ServerSentEvent('x', retry='bad').encode()",
        {"ok": False, "value": None, "exception_type": "builtins.TypeError", "exception_message": "retry argument must be int"},
    ),
    (
        "json-event",
        "from sse_starlette.event import JSONServerSentEvent; result = JSONServerSentEvent({'text':'café','n':2}, event='json').encode().decode()",
        {"ok": True, "value": 'event: json\r\ndata: {"text":"café","n":2}\r\n\r\n'},
    ),
    (
        "ensure-memoryview",
        "from sse_starlette.event import ensure_bytes; result = ensure_bytes(memoryview(b'raw'), '\\n')",
        {"ok": True, "value": "b'raw'"},
    ),
    (
        "ensure-dict-separator",
        "from sse_starlette.event import ensure_bytes; value={'data':'x'}; result=[ensure_bytes(value, '\\n').decode(), value]",
        {"ok": True, "value": ["data: x\n\n", {"data": "x", "sep": "\n"}]},
    ),
    (
        "ensure-other",
        "from sse_starlette.event import ensure_bytes; result = ensure_bytes(42, '\\r')",
        {"ok": True, "value": "b'data: 42\\r\\r'"},
    ),
    (
        "response-default-headers",
        "from sse_starlette.sse import EventSourceResponse; r=EventSourceResponse([], ping=0); result=dict((k.decode(),v.decode()) for k,v in r.raw_headers)",
        {"ok": True, "value": {"cache-control": "no-store", "connection": "keep-alive", "x-accel-buffering": "no", "content-type": "text/event-stream; charset=utf-8"}},
    ),
    (
        "response-header-precedence",
        "from sse_starlette.sse import EventSourceResponse; r=EventSourceResponse([], headers={'cache-control':'no-cache','connection':'close','x-accel-buffering':'yes','x-custom':'ok'}); result=dict((k.decode(),v.decode()) for k,v in r.raw_headers)",
        {"ok": True, "value": {"cache-control": "no-cache", "connection": "keep-alive", "x-accel-buffering": "no", "x-custom": "ok", "content-type": "text/event-stream; charset=utf-8"}},
    ),
    (
        "response-separator-validation",
        "from sse_starlette.sse import EventSourceResponse; EventSourceResponse([], sep='bad')",
        {"ok": False, "value": None, "exception_type": "builtins.ValueError", "exception_message": "sep must be one of: \\r\\n, \\r, \\n, got: bad"},
    ),
    (
        "response-grace-validation",
        "from sse_starlette.sse import EventSourceResponse; EventSourceResponse([], shutdown_grace_period=-1)",
        {"ok": False, "value": None, "exception_type": "builtins.ValueError", "exception_message": "shutdown_grace_period must be >= 0"},
    ),
    (
        "ping-validation",
        "from sse_starlette.sse import EventSourceResponse; r=EventSourceResponse([], ping=1); r.ping_interval='x'",
        {"ok": False, "value": None, "exception_type": "builtins.TypeError", "exception_message": "ping interval must be int"},
    ),
    (
        "ping-negative",
        "from sse_starlette.sse import EventSourceResponse; r=EventSourceResponse([], ping=1); r.ping_interval=-1",
        {"ok": False, "value": None, "exception_type": "builtins.ValueError", "exception_message": "ping interval must be greater than 0"},
    ),
    (
        "compression-disabled",
        "from sse_starlette.sse import EventSourceResponse; EventSourceResponse([]).enable_compression()",
        {"ok": False, "value": None, "exception_type": "builtins.NotImplementedError", "exception_message": "Compression is not supported for SSE streams."},
    ),
    (
        "stream-async",
        """import anyio
from sse_starlette.sse import EventSourceResponse
async def main():
 out=[]
 async def gen():
  yield 'a'
  yield {'data':'b','event':'e'}
 async def send(message): out.append(message)
 await EventSourceResponse(gen(), ping=0)._stream_response(send)
 return [[m['type'], m.get('status'), m.get('body',b'').decode(), m.get('more_body')] for m in out]
result=anyio.run(main)""",
        {"ok": True, "value": [["http.response.start", 200, "", None], ["http.response.body", None, "data: a\r\n\r\n", True], ["http.response.body", None, "event: e\r\ndata: b\r\n\r\n", True], ["http.response.body", None, "", False]]},
    ),
    (
        "stream-sync",
        """import anyio
from sse_starlette.sse import EventSourceResponse
async def main():
 out=[]
 async def send(message): out.append(message)
 await EventSourceResponse([1,2], ping=0)._stream_response(send)
 return [m.get('body',b'').decode() for m in out]
result=anyio.run(main)""",
        {"ok": True, "value": ["", "data: 1\r\n\r\n", "data: 2\r\n\r\n", ""]},
    ),
    (
        "websocket-denial",
        """import anyio
from sse_starlette.sse import EventSourceResponse
async def main():
 out=[]
 async def send(message): out.append(message)
 async def receive(): return {'type':'http.disconnect'}
 await EventSourceResponse([], ping=0)({'type':'websocket'}, receive, send)
 return [m['type'] for m in out]
result=anyio.run(main)""",
        {"ok": True, "value": ["websocket.http.response.start"]},
    ),
    (
        "send-timeout",
        """import anyio
from sse_starlette.sse import EventSourceResponse
async def main():
 async def send(message): await anyio.sleep(0.05)
 try: await EventSourceResponse(['x'], ping=0, send_timeout=0.001)._stream_response(send)
 except BaseException as exc: return [type(exc).__name__, str(exc)]
result=anyio.run(main)""",
        {"ok": True, "value": ["SendTimeoutError", ""]},
    ),
    (
        "ping-factory",
        """import anyio
from sse_starlette.event import ServerSentEvent
from sse_starlette.sse import EventSourceResponse
async def main():
 out=[]
 async def send(message): out.append(message); response.active=False
 response=EventSourceResponse([], ping=0, ping_message_factory=lambda: ServerSentEvent(comment='tick'))
 await response._ping(send)
 return out[0]['body'].decode()
result=anyio.run(main)""",
        {"ok": True, "value": ": tick\r\n\r\n"},
    ),
    (
        "background-task",
        """import anyio
from starlette.background import BackgroundTask
from sse_starlette.sse import EventSourceResponse
async def main():
 state=[]
 async def bg(): state.append('done')
 async def send(message): pass
 async def receive(): return {'type':'http.disconnect'}
 await EventSourceResponse([], ping=0, background=BackgroundTask(bg))({'type':'http'}, receive, send)
 return state
result=anyio.run(main)""",
        {"ok": True, "value": ["done"]},
    ),
    (
        "disconnect-callback",
        """import anyio
from sse_starlette.sse import EventSourceResponse
async def main():
 state=[]
 async def cb(message): state.append(message['type'])
 async def receive(): return {'type':'http.disconnect'}
 r=EventSourceResponse([], ping=0, client_close_handler_callable=cb)
 await r._listen_for_disconnect(receive)
 return [r.active,state]
result=anyio.run(main)""",
        {"ok": True, "value": [False, ["http.disconnect"]]},
    ),
    (
        "shutdown-event",
        """import anyio
from sse_starlette.sse import AppStatus, EventSourceResponse
async def main():
 AppStatus.should_exit=True
 event=anyio.Event()
 async def gen():
  while not event.is_set():
   yield 'x'
   await anyio.sleep(0)
  yield 'bye'
 async def send(message): pass
 async def receive(): await anyio.sleep(100)
 await EventSourceResponse(gen(), ping=0, shutdown_event=event, shutdown_grace_period=0.01)({'type':'http'}, receive, send)
 return event.is_set()
result=anyio.run(main)""",
        {"ok": True, "value": True},
    ),
    (
        "websocket-wrapper",
        """import anyio
from sse_starlette.sse import _wrap_websocket_denial_send
async def main():
 out=[]
 async def send(message): out.append(message)
 wrapped=_wrap_websocket_denial_send(send)
 await wrapped({'type':'http.response.start','status':204})
 await wrapped({'type':'http.response.body','body':b'x'})
 await wrapped({'type':'other'})
 return [m['type'] for m in out]
result=anyio.run(main)""",
        {"ok": True, "value": ["websocket.http.response.start", "websocket.http.response.body", "other"]},
    ),
    (
        "metadata-version",
        "import importlib.metadata; result=importlib.metadata.version('sse-starlette')",
        {"ok": True, "value": "3.4.8"},
    ),
    (
        "import-without-uvicorn",
        "import sse_starlette.event, sse_starlette.sse; result=True",
        {"ok": True, "value": True},
    ),
]


def main() -> None:
    leaves = [check(case_id, source, expected) for case_id, source, expected in CASES]
    print(json.dumps({"schema_version": "1.0", "leaves": leaves}, sort_keys=True))


if __name__ == "__main__":
    main()
