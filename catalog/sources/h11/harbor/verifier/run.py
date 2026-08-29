from __future__ import annotations

import json

from nl2repobench.verification.candidate_client import execute_script


def _run(source: str, expected: object) -> dict[str, object]:
    observed = execute_script(source, timeout_sec=20.0)
    actual = {"ok": observed.ok, "value": observed.value}
    if not observed.ok:
        actual["exception_type"] = observed.exception_type
        actual["exception_message"] = observed.exception_message
    return {"status": "passed" if actual == expected else "failed", "actual": actual}


CASES: list[tuple[str, str, object]] = [
    (
        "exports-and-version",
        "import h11\nresult = [h11.__version__, repr(h11.CLIENT), repr(h11.SERVER), repr(h11.NEED_DATA), repr(h11.PAUSED)]",
        {"ok": True, "value": ["0.16.0+dev", "CLIENT", "SERVER", "NEED_DATA", "PAUSED"]},
    ),
    (
        "request-event",
        "from h11 import Request\nr = Request(method='GET', target='/', headers=[('Host', 'example.org'), ('X-Test', 'value')])\nresult = {'method': r.method.decode(), 'target': r.target.decode(), 'headers': [[a.decode(), b.decode()] for a,b in r.headers], 'raw': [[a.decode(), b.decode()] for a,b in r.headers.raw_items()], 'version': r.http_version.decode()}",
        {"ok": True, "value": {"method": "GET", "target": "/", "headers": [["host", "example.org"], ["x-test", "value"]], "raw": [["Host", "example.org"], ["X-Test", "value"]], "version": "1.1"}},
    ),
    (
        "response-and-body-events",
        "from h11 import Response, InformationalResponse, Data, EndOfMessage, ConnectionClosed\nr = Response(status_code=200, headers=[('Content-Length', '2')], reason='OK')\ni = InformationalResponse(status_code=100, headers=[])\nd = Data(b'ab', chunk_start=True, chunk_end=True)\ne = EndOfMessage(headers=[('X-Trailer', 'yes')])\nresult = [r.status_code, r.reason.decode(), i.status_code, d.data.decode(), d.chunk_start, d.chunk_end, [[a.decode(), b.decode()] for a,b in e.headers], repr(ConnectionClosed())]",
        {"ok": True, "value": [200, "OK", 100, "ab", True, True, [["x-trailer", "yes"]], "ConnectionClosed()"]},
    ),
    (
        "header-normalization",
        "from h11._headers import normalize_and_validate, get_comma_header, set_comma_header\nh = normalize_and_validate([('X-Test', 'v'), ('Connection', 'Keep-Alive, close')])\nh = set_comma_header(h, b'connection', [b'upgrade', b'close'])\nresult = {'items': [[a.decode(), b.decode()] for a,b in h], 'raw': [[a.decode(), b.decode()] for a,b in h.raw_items()], 'comma': [x.decode() for x in get_comma_header(h, b'connection')]}",
        {"ok": True, "value": {"items": [["x-test", "v"], ["connection", "upgrade"], ["connection", "close"]], "raw": [["X-Test", "v"], ["Connection", "upgrade"], ["Connection", "close"]], "comma": ["upgrade", "close"]}},
    ),
    (
        "header-validation",
        "from h11 import Request\nRequest(method='GET', target='/', headers=[('Host', 'x'), ('Content-Length', '1'), ('content-length', '2')])",
        {"ok": False, "value": None, "exception_type": "h11._util.LocalProtocolError", "exception_message": "conflicting Content-Length headers"},
    ),
    (
        "request-wire",
        "import h11\nc = h11.Connection(h11.CLIENT)\nresult = c.send(h11.Request(method='GET', target='/x', headers=[('Host', 'example.org'), ('X-A', 'b')])).decode('ascii')",
        {"ok": True, "value": "GET /x HTTP/1.1\r\nHost: example.org\r\nX-A: b\r\n\r\n"},
    ),
    (
        "response-wire",
        "import h11\nc = h11.Connection(h11.SERVER)\nc.receive_data(b'GET / HTTP/1.1\\r\\nHost: x\\r\\n\\r\\n')\nc.next_event()\nresult = [c.send(h11.Response(status_code=200, headers=[('Content-Length', '3')], reason='OK')).decode('ascii'), c.send(h11.Data(b'abc')).decode('ascii'), c.send(h11.EndOfMessage()).decode('ascii')]",
        {"ok": True, "value": ["HTTP/1.1 200 OK\r\nContent-Length: 3\r\n\r\n", "abc", ""]},
    ),
    (
        "receive-request",
        "import h11\nc = h11.Connection(h11.SERVER)\nc.receive_data(b'GET / HTTP/1.1\\r\\nHost: x\\r\\n\\r\\n')\na = c.next_event()\nb = c.next_event()\nresult = [type(a).__name__, a.method.decode(), a.target.decode(), type(b).__name__, repr(c.our_state), repr(c.their_state)]",
        {"ok": True, "value": ["Request", "GET", "/", "EndOfMessage", "SEND_RESPONSE", "DONE"]},
    ),
    (
        "receive-response",
        "import h11\nc = h11.Connection(h11.CLIENT)\nc.send(h11.Request(method='GET', target='/', headers=[('Host', 'x')]))\nc.receive_data(b'HTTP/1.1 200 OK\\r\\nContent-Length: 3\\r\\n\\r\\nabc')\na = c.next_event(); b = c.next_event(); d = c.next_event()\nresult = [type(a).__name__, a.status_code, type(b).__name__, b.data.decode(), type(d).__name__]",
        {"ok": True, "value": ["Response", 200, "Data", "abc", "EndOfMessage"]},
    ),
    (
        "chunked-wire",
        "import h11\nc = h11.Connection(h11.CLIENT)\nreq = h11.Request(method='POST', target='/', headers=[('Host', 'x'), ('Transfer-Encoding', 'chunked')])\nresult = [c.send(req).decode('ascii'), c.send(h11.Data(b'abc')).decode('ascii'), c.send(h11.EndOfMessage()).decode('ascii')]",
        {"ok": True, "value": ["POST / HTTP/1.1\r\nHost: x\r\nTransfer-Encoding: chunked\r\n\r\n", "3\r\nabc\r\n", "0\r\n\r\n"]},
    ),
    (
        "chunked-parse",
        "import h11\nc = h11.Connection(h11.SERVER)\nc.receive_data(b'POST / HTTP/1.1\\r\\nHost: x\\r\\nTransfer-Encoding: chunked\\r\\n\\r\\n3\\r\\nabc\\r\\n0\\r\\n\\r\\n')\na=c.next_event(); b=c.next_event(); d=c.next_event(); result=[type(a).__name__, type(b).__name__, b.data.decode(), b.chunk_start, b.chunk_end, type(d).__name__]",
        {"ok": True, "value": ["Request", "Data", "abc", True, True, "EndOfMessage"]},
    ),
    (
        "client-lifecycle",
        "import h11\nc = h11.Connection(h11.CLIENT)\nc.send(h11.Request(method='GET', target='/', headers=[('Host','x')]))\nc.send(h11.EndOfMessage())\nresult = [repr(c.our_state), repr(c.their_state), c.states == {h11.CLIENT: h11.DONE, h11.SERVER: h11.IDLE}]",
        {"ok": True, "value": ["DONE", "SEND_RESPONSE", False]},
    ),
    (
        "server-lifecycle",
        "import h11\nc = h11.Connection(h11.SERVER)\nc.receive_data(b'GET / HTTP/1.1\\r\\nHost: x\\r\\n\\r\\n')\nc.next_event(); c.next_event(); c.send(h11.Response(status_code=204, headers=[])); c.send(h11.EndOfMessage())\nresult = [repr(c.our_state), repr(c.their_state)]",
        {"ok": True, "value": ["DONE", "DONE"]},
    ),
    (
        "need-data",
        "import h11\nc = h11.Connection(h11.SERVER)\nc.receive_data(b'GET / HTTP/1.1\\r\\n')\nresult = [repr(c.next_event()), repr(c.our_state), repr(c.their_state)]",
        {"ok": True, "value": ["NEED_DATA", "IDLE", "IDLE"]},
    ),
    (
        "paused-flow-control",
        "import h11\nc = h11.Connection(h11.SERVER)\nc.receive_data(b'GET / HTTP/1.1\\r\\nHost: x\\r\\n\\r\\n')\nc.next_event(); c.next_event(); c.send(h11.Response(status_code=204, headers=[])); c.send(h11.EndOfMessage()); c.receive_data(b'GET /two HTTP/1.1\\r\\nHost: x\\r\\n\\r\\n')\nresult = repr(c.next_event())",
        {"ok": True, "value": "PAUSED"},
    ),
    (
        "eof-close",
        "import h11\nc = h11.Connection(h11.CLIENT)\nc.receive_data(b'')\nresult = [repr(c.next_event()), repr(c.next_event()), repr(c.their_state)]",
        {"ok": True, "value": ["ConnectionClosed()", "ConnectionClosed()", "CLOSED"]},
    ),
    (
        "protocol-error",
        "import h11\nc = h11.Connection(h11.SERVER)\nc.receive_data(b'GET / HTTP/1.1\\r\\n\\r\\n')\nc.next_event()",
        {"ok": False, "value": None, "exception_type": "h11._util.RemoteProtocolError", "exception_message": "Missing mandatory Host: header"},
    ),
    (
        "automatic-chunked-response",
        "import h11\nc = h11.Connection(h11.SERVER)\nc.receive_data(b'GET / HTTP/1.1\\r\\nHost: x\\r\\n\\r\\n'); c.next_event(); c.next_event()\nresult = c.send(h11.Response(status_code=200, headers=[])).decode('ascii')",
        {"ok": True, "value": "HTTP/1.1 200 \r\nTransfer-Encoding: chunked\r\n\r\n"},
    ),
    (
        "head-framing",
        "import h11\nc = h11.Connection(h11.SERVER)\nc.receive_data(b'HEAD / HTTP/1.1\\r\\nHost: x\\r\\n\\r\\n'); c.next_event(); c.next_event()\nresult = [c.send(h11.Response(status_code=200, headers=[])).decode('ascii'), c.send(h11.EndOfMessage()).decode('ascii')]",
        {"ok": True, "value": ["HTTP/1.1 200 \r\nTransfer-Encoding: chunked\r\n\r\n", ""]},
    ),
    (
        "http10-close-delimited",
        "import h11\nc = h11.Connection(h11.SERVER)\nc.receive_data(b'GET / HTTP/1.0\\r\\n\\r\\n'); c.next_event(); c.next_event()\nresult = [c.send(h11.Response(status_code=200, headers=[])).decode('ascii'), repr(c.our_state), repr(c.their_state)]",
        {"ok": True, "value": ["HTTP/1.1 200 \r\nConnection: close\r\n\r\n", "SEND_BODY", "MUST_CLOSE"]},
    ),
    (
        "passthrough-writes",
        "import h11\nc = h11.Connection(h11.CLIENT)\nc.send(h11.Request(method='POST', target='/', headers=[('Host','x'), ('Content-Length','2')]))\nd=h11.Data(bytearray(b'ab')); parts=c.send_with_data_passthrough(d)\nresult=[len(parts), parts[0].decode('ascii'), parts[0] is d.data]",
        {"ok": True, "value": [1, "ab", True]},
    ),
    (
        "bytesify-and-sentinels",
        "from h11._util import bytesify\nimport h11\nresult = [bytesify('abc').decode(), bytesify(bytearray(b'de')).decode(), repr(h11.CLIENT), repr(h11.DONE)]",
        {"ok": True, "value": ["abc", "de", "CLIENT", "DONE"]},
    ),
    (
        "module-exports",
        "import h11\nfrom h11._events import Request\nresult = [Request.__module__, 'Connection' in h11.__all__, 'Request' in h11.__all__, 'RemoteProtocolError' in h11.__all__]",
        {"ok": True, "value": ["h11._events", True, True, True]},
    ),
    (
        "repeat-determinism",
        "import h11\ndef run():\n c=h11.Connection(h11.CLIENT); return c.send(h11.Request(method='GET', target='/', headers=[('Host','x')])).decode('ascii')\nresult = [run(), run(), run()]",
        {"ok": True, "value": ["GET / HTTP/1.1\r\nHost: x\r\n\r\n"] * 3},
    ),
]


def main() -> None:
    leaves = []
    for case_id, source, expected in CASES:
        outcome = _run(source, expected)
        leaf = {"id": case_id, "status": outcome["status"]}
        if outcome["status"] == "failed":
            leaf["message"] = json.dumps(outcome["actual"], sort_keys=True)
        leaves.append(leaf)
    print(json.dumps({"schema_version": "1.0", "leaves": leaves}, sort_keys=True))


if __name__ == "__main__":
    main()
