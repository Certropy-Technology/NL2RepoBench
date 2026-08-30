from __future__ import annotations

import json

from nl2repobench.verification.candidate_client import execute_script


CASES: list[tuple[str, str, object]] = [
    ("exports", "import websocket\nresult = [websocket.__version__, websocket.ABNF.OPCODE_TEXT, websocket.ABNF.OPCODE_BINARY, websocket.STATUS_NORMAL, hasattr(websocket, 'WebSocket'), hasattr(websocket, 'WebSocketApp'), hasattr(websocket, 'create_connection')]", {"ok": True, "value": ["1.9.0", 1, 2, 1000, True, True, True]}),
    ("parse-ws", "from websocket._url import parse_url\nresult = list(parse_url('ws://example.com/chat'))", {"ok": True, "value": ["example.com", 80, "/chat", False]}),
    ("parse-wss-query", "from websocket._url import parse_url\nresult = list(parse_url('wss://[2001:db8::1]:8443/path?q=1'))", {"ok": True, "value": ["2001:db8::1", 8443, "/path?q=1", True]}),
    ("parse-invalid-scheme", "from websocket._url import parse_url\nparse_url('http://example.com')", {"ok": False, "value": None, "exception_type": "builtins.ValueError", "exception_message": "scheme http is invalid"}),
    ("parse-invalid-host", "from websocket._url import parse_url\nparse_url('ws:///path')", {"ok": False, "value": None, "exception_type": "builtins.ValueError", "exception_message": "hostname is invalid"}),
    ("proxy-explicit", "from websocket._url import get_proxy_info\nresult = list(get_proxy_info('example.com', False, 'proxy.local', 3128, ('u', 'p')))" , {"ok": True, "value": ["proxy.local", 3128, ["u", "p"]]}),
    ("proxy-no-port", "from websocket._url import get_proxy_info\nget_proxy_info('example.com', False, 'proxy.local', 0)", {"ok": False, "value": None, "exception_type": "websocket._exceptions.WebSocketProxyException", "exception_message": "Cannot use port 0 when proxy_host specified"}),
    ("proxy-no-proxy", "from websocket._url import get_proxy_info\nresult = list(get_proxy_info('api.example.com', False, 'proxy.local', 3128, None, ['example.com']))", {"ok": True, "value": [None, 0, None]}),
    ("proxy-env", "import os\nos.environ['HTTP_PROXY'] = 'http://user:p%40ss@proxy.local:8080'\nos.environ.pop('NO_PROXY', None)\nos.environ.pop('no_proxy', None)\nfrom websocket._url import get_proxy_info\nresult = list(get_proxy_info('not-listed.invalid', False))", {"ok": True, "value": ["proxy.local", 8080, ["user", "p@ss"]]}),
    ("mask-known", "from websocket._abnf import ABNF\nresult = ABNF.mask(b'1234', b'hello').hex()", {"ok": True, "value": "59575f585e"}),
    ("frame-unmasked", "from websocket._abnf import ABNF\nf = ABNF(1, 0, 0, 0, ABNF.OPCODE_TEXT, 0, 'hello')\nresult = f.format().hex()", {"ok": True, "value": "810568656c6c6f"}),
    ("frame-masked", "from websocket._abnf import ABNF\nf = ABNF(1, 0, 0, 0, ABNF.OPCODE_TEXT, 1, b'hello')\nf.get_mask_key = lambda n: b'1234'\nresult = f.format().hex()", {"ok": True, "value": "81853132333459575f585e"}),
    ("frame-lengths", "from websocket._abnf import ABNF\nresult = [ABNF(1, 0, 0, 0, 2, 0, b'a' * n).format()[:4].hex() for n in (125, 126, 65536)]", {"ok": True, "value": ["827d6161", "827e007e", "827f0000"]}),
    ("invalid-ping", "from websocket._abnf import ABNF\nABNF(0, 0, 0, 0, ABNF.OPCODE_PING, 0, b'x').validate()", {"ok": False, "value": None, "exception_type": "websocket._exceptions.WebSocketProtocolException", "exception_message": "Invalid ping frame."}),
    ("invalid-close", "from websocket._abnf import ABNF\nABNF(1, 0, 0, 0, ABNF.OPCODE_CLOSE, 0, bytes.fromhex('03ed')).validate()", {"ok": False, "value": None, "exception_type": "websocket._exceptions.WebSocketProtocolException", "exception_message": "('Invalid close opcode %r', 1005)"}),
    ("frame-buffer", "from websocket._abnf import ABNF, frame_buffer\nchunks = [b'\\x81', b'\\x05he', b'llo']\ndef recv(n):\n    return chunks.pop(0)\nf = frame_buffer(recv, False).recv_frame()\nresult = [f.fin, f.opcode, f.data.decode(), f.mask_value]", {"ok": True, "value": [1, 1, "hello", 0]}),
    ("continuous-frame", "from websocket._abnf import ABNF, continuous_frame\nframes = [ABNF(0, 0, 0, 0, 1, 0, b'hel'), ABNF(1, 0, 0, 0, 0, 0, b'lo')]\nc = continuous_frame(False, False)\nfor frame in frames:\n    c.validate(frame)\n    c.add(frame)\nlast = frames[-1]\nresult = [c.is_fire(last), c.extract(last)[0], last.data.decode()]", {"ok": True, "value": [1, 1, "hello"]}),
    ("cookiejar", "from websocket._cookiejar import SimpleCookieJar\nj = SimpleCookieJar()\nj.add('sid=abc; Domain=Example.COM')\nj.add('theme=dark; Domain=.example.com')\nresult = [j.get('example.com'), j.get('api.example.com'), j.get('other.com')]", {"ok": True, "value": ["sid=abc; theme=dark", "sid=abc; theme=dark", ""]}),
    ("cookiejar-set", "from websocket._cookiejar import SimpleCookieJar\nj = SimpleCookieJar()\nj.set('sid=abc; Domain=example.com')\nresult = j.get('example.com')", {"ok": True, "value": "sid=abc"}),
    ("handshake-headers", "from websocket._handshake import _get_handshake_headers\nopts = {'header': {'Sec-WebSocket-Key': 'fixed-key', 'X-Test': 'yes'}, 'subprotocols': ['chat', 'superchat'], 'cookie': 'client=1'}\nresult = list(_get_handshake_headers('/chat?x=1', 'ws://example.com/chat', 'example.com', 80, opts)[0])", {"ok": True, "value": ["GET /chat?x=1 HTTP/1.1", "Upgrade: websocket", "Host: example.com", "Origin: http://example.com", "Sec-WebSocket-Version: 13", "Connection: Upgrade", "Sec-WebSocket-Protocol: chat,superchat", "Sec-WebSocket-Key: fixed-key", "X-Test: yes", "Cookie: client=1", "", ""]}),
    ("handshake-validate-ok", "import base64, hashlib\nfrom websocket._handshake import _validate\nkey = 'dGhlIHNhbXBsZSBub25jZQ=='\naccept = base64.b64encode(hashlib.sha1((key + '258EAFA5-E914-47DA-95CA-C5AB0DC85B11').encode()).digest()).decode()\nresult = list(_validate({'upgrade': 'websocket', 'connection': 'keep-alive, Upgrade', 'sec-websocket-accept': accept, 'sec-websocket-protocol': 'CHAT'}, key, ['chat']))", {"ok": True, "value": [True, "chat"]}),
    ("handshake-validate-bad", "from websocket._handshake import _validate\nresult = list(_validate({'upgrade': 'websocket', 'connection': 'upgrade'}, 'x', None))", {"ok": True, "value": [False, None]}),
    ("sockopt-state", "from websocket._socket import sock_opt\ns = sock_opt(None, None)\ns.timeout = 3.5\nresult = [s.sockopt, s.sslopt, s.timeout]", {"ok": True, "value": [[], {}, 3.5]}),
    ("default-timeout", "import websocket\nwebsocket.setdefaulttimeout(7)\na = websocket.getdefaulttimeout()\nwebsocket.setdefaulttimeout(None)\nresult = [a, websocket.getdefaulttimeout()]", {"ok": True, "value": [7, None]}),
    ("websocket-state", "import websocket\nws = websocket.WebSocket(enable_multithread=False, skip_utf8_validation=True)\nws.settimeout(2)\nresult = [ws.gettimeout(), ws.connected, ws.frame_buffer.skip_utf8_validation, type(ws.lock).__name__, type(ws.readlock).__name__]", {"ok": True, "value": [2, False, True, "NoLock", "NoLock"]}),
    ("websocket-fileno-error", "import websocket\nwebsocket.WebSocket().fileno()", {"ok": False, "value": None, "exception_type": "websocket._exceptions.WebSocketException", "exception_message": "Connection not established"}),
    ("app-state", "import websocket\napp = websocket.WebSocketApp('ws://example.com', header={'X-Test': 'yes'}, cookie='a=1', subprotocols=['chat'])\nresult = [app.url, app.header, app.cookie, app.subprotocols, app.keep_running, app.sock, app.has_errored, app.has_done_teardown]", {"ok": True, "value": ["ws://example.com", {"X-Test": "yes"}, "a=1", ["chat"], False, None, False, False]}),
    ("app-close-inactive", "import websocket\napp = websocket.WebSocketApp('ws://example.com')\napp.close()\nresult = [app.has_done_teardown, app.sock]", {"ok": True, "value": [False, None]}),
    ("exception-status", "from websocket._exceptions import WebSocketBadStatusException\ne = WebSocketBadStatusException('bad', 503, 'Service Unavailable', {'x': 'y'}, b'no')\nresult = [str(e), e.status_code, e.resp_headers, repr(e.resp_body)]", {"ok": True, "value": ["bad", 503, {"x": "y"}, "b'no'"]}),
    ("utf8", "from websocket._utils import validate_utf8\nresult = [validate_utf8(b'hello'), validate_utf8(b'\\xff')]", {"ok": True, "value": [True, False]}),
]


def _run(source: str, expected: object) -> dict[str, object]:
    observed = execute_script(source, timeout_sec=20.0)
    actual: dict[str, object] = {"ok": observed.ok, "value": observed.value}
    if not observed.ok:
        actual["exception_type"] = observed.exception_type
        actual["exception_message"] = observed.exception_message
    return {"status": "passed" if actual == expected else "failed", "actual": actual}


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
