#!/usr/bin/env python3
"""Child-side deterministic adapter for the public httpcore contract."""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import traceback
from pathlib import Path


def check(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def expect(exc_type: type[BaseException], function, message: str) -> None:
    try:
        function()
    except exc_type:
        return
    except BaseException as exc:
        raise AssertionError(
            f"{message}: expected {exc_type.__name__}, got {type(exc).__name__}"
        ) from exc
    raise AssertionError(f"{message}: expected {exc_type.__name__}")


def response_buffer() -> list[bytes]:
    return [
        b"HTTP/1.1 200 OK\r\n",
        b"Content-Type: text/plain\r\n",
        b"Content-Length: 13\r\n",
        b"\r\n",
        b"Hello, world!",
    ]


def api_surface() -> None:
    import httpcore

    names = (
        "URL", "Origin", "Proxy", "Request", "Response", "ConnectionPool",
        "HTTP11Connection", "HTTP2Connection", "AsyncConnectionPool",
        "AsyncHTTP11Connection", "MockStream", "MockBackend", "AsyncMockStream",
        "AsyncMockBackend", "NetworkStream", "AsyncNetworkStream", "ConnectError",
        "RemoteProtocolError", "default_ssl_context",
    )
    check(all(hasattr(httpcore, name) for name in names), "root exports incomplete")
    check(httpcore.__version__ == "1.0.9", "version metadata changed")
    from httpcore._sync.interfaces import RequestInterface
    from httpcore._async.interfaces import AsyncRequestInterface

    check(hasattr(RequestInterface, "request"), "sync interface missing request")
    check(hasattr(AsyncRequestInterface, "request"), "async interface missing request")


def url_origin_proxy() -> None:
    import httpcore

    url = httpcore.URL("https://example.com:8443/path?q=1")
    check(url.scheme == b"https" and url.host == b"example.com", "URL parse failed")
    check(url.port == 8443 and url.target == b"/path?q=1", "URL target failed")
    check(bytes(url) == b"https://example.com:8443/path?q=1", "URL bytes failed")
    check(str(url.origin) == "https://example.com:8443", "origin conversion failed")
    check(httpcore.URL("https://example.com").origin.port == 443, "default port failed")
    expect(TypeError, lambda: httpcore.URL("https://example.com/\N{WHITE SMILING FACE}"), "unicode URL accepted")
    proxy = httpcore.Proxy("http://proxy.local:8080", auth=("user", "pass"))
    check(proxy.url.host == b"proxy.local" and proxy.auth == (b"user", b"pass"), "proxy parse failed")
    check(proxy.headers[0] == (b"Proxy-Authorization", b"Basic dXNlcjpwYXNz"), "proxy auth header failed")


def request_model() -> None:
    import httpcore

    request = httpcore.Request(
        "POST", "https://example.com/items", headers={"X-Test": "yes"},
        content=b"abc", extensions={"target": b"/override"},
    )
    check(request.method == b"POST" and request.url.target == b"/override", "request fields failed")
    check(request.headers == [(b"X-Test", b"yes")], "header normalization failed")
    check(list(request.stream) == [b"abc"], "request stream failed")
    check(repr(request) == "<Request [b'POST']>", "request repr failed")
    expect(TypeError, lambda: httpcore.Request(1, "https://example.com"), "invalid method accepted")
    expect(TypeError, lambda: httpcore.Request("GET", "https://example.com", headers=1), "invalid headers accepted")


def response_buffered() -> None:
    import httpcore

    response = httpcore.Response(201, headers={"Content-Type": "text/plain"}, content=b"created")
    check(response.status == 201 and response.headers == [(b"Content-Type", b"text/plain")], "response fields failed")
    check(response.read() == b"created" and response.content == b"created", "buffered response failed")
    check(repr(response) == "<Response [201]>", "response repr failed")
    check(response.extensions == {}, "response extensions default failed")


def response_sync_stream() -> None:
    import httpcore

    response = httpcore.Response(200, content=(part for part in (b"a", b"b")))
    check(list(response.iter_stream()) == [b"a", b"b"], "sync stream chunks failed")
    expect(RuntimeError, lambda: response.content, "stream content became available")
    expect(RuntimeError, lambda: list(response.iter_stream()), "stream was reusable")


async def response_async_stream() -> None:
    import httpcore

    async def parts():
        yield b"x"
        yield b"y"

    response = httpcore.Response(200, content=parts())
    chunks = [chunk async for chunk in response.aiter_stream()]
    check(chunks == [b"x", b"y"], "async stream chunks failed")
    expect(RuntimeError, lambda: response.content, "async stream content became available")
    try:
        await response.aread()
    except RuntimeError:
        pass
    else:
        raise AssertionError("async stream was reusable")


def mock_stream() -> None:
    import httpcore

    stream = httpcore.MockStream([b"one", b"two"])
    check(stream.read(3) == b"one" and stream.read(3) == b"two", "mock reads failed")
    check(stream.read(3) == b"", "mock EOF failed")
    stream.write(b"request-bytes")
    check(stream.get_extra_info("unknown") is None, "mock extra info failed")
    check(repr(stream) == "<httpcore.MockStream>", "mock stream repr failed")


def http11_basic() -> None:
    import httpcore

    origin = httpcore.Origin(b"https", b"example.com", 443)
    with httpcore.HTTP11Connection(origin=origin, stream=httpcore.MockStream(response_buffer())) as conn:
        response = conn.request("GET", "https://example.com/")
        check(response.status == 200 and response.content == b"Hello, world!", "HTTP/1.1 response failed")
        check(conn.is_idle() and conn.is_available() and not conn.is_closed(), "connection state failed")


def http11_post_body() -> None:
    import httpcore

    stream = httpcore.MockStream(response_buffer())
    with httpcore.HTTP11Connection(
        origin=httpcore.Origin(b"http", b"example.com", 80), stream=stream
    ) as conn:
        response = conn.request("POST", "http://example.com/submit", content=b"payload")
        check(response.content == b"Hello, world!", "POST response failed")


def http11_interim() -> None:
    import httpcore

    stream = httpcore.MockStream([
        b"HTTP/1.1 100 Continue\r\n", b"\r\n", b"HTTP/1.1 200 OK\r\n",
        b"Content-Length: 2\r\n", b"\r\n", b"ok",
    ])
    with httpcore.HTTP11Connection(
        origin=httpcore.Origin(b"https", b"example.com", 443), stream=stream
    ) as conn:
        response = conn.request("GET", "https://example.com/", headers={"Expect": "continue"})
        check(response.status == 200 and response.content == b"ok", "interim response handling failed")


def http11_upgrade() -> None:
    import httpcore

    stream = httpcore.MockStream([
        b"HTTP/1.1 101 Switching Protocols\r\n", b"Connection: upgrade\r\n",
        b"Upgrade: custom\r\n", b"\r\n", b"tail",
    ])
    with httpcore.HTTP11Connection(
        origin=httpcore.Origin(b"wss", b"example.com", 443), stream=stream
    ) as conn:
        with conn.stream("GET", "wss://example.com/", headers={"Connection": "upgrade", "Upgrade": "custom"}) as response:
            check(response.status == 101, "upgrade status failed")
            check(response.extensions["network_stream"].read(10) == b"tail", "upgrade stream failed")


def http11_errors() -> None:
    import httpcore

    bad = httpcore.MockStream([b"not HTTP", b""])
    with httpcore.HTTP11Connection(
        origin=httpcore.Origin(b"https", b"example.com", 443), stream=bad
    ) as conn:
        expect(httpcore.RemoteProtocolError, lambda: conn.request("GET", "https://example.com/"), "malformed response accepted")
        check(conn.is_closed() and not conn.is_available(), "failed connection remained reusable")
    def illegal_request() -> None:
        with httpcore.HTTP11Connection(
            origin=httpcore.Origin(b"https", b"example.com", 443),
            stream=httpcore.MockStream(response_buffer()),
        ) as conn:
            conn.request("GET", "https://example.com/", headers={"X": "\0"})

    expect(httpcore.LocalProtocolError, illegal_request, "illegal header accepted")


def http11_lifecycle() -> None:
    import httpcore

    stream = httpcore.MockStream(response_buffer())
    conn = httpcore.HTTP11Connection(origin=httpcore.Origin(b"https", b"example.com", 443), stream=stream)
    with conn.stream("GET", "https://example.com/"):
        expect(httpcore.ConnectionNotAvailable, lambda: conn.request("GET", "https://example.com/"), "concurrent request accepted")
    check(conn.is_closed(), "unread response did not close connection")
    expect(RuntimeError, lambda: conn.request("GET", "https://other.example/"), "wrong origin accepted")


def pool_keepalive() -> None:
    import httpcore

    with httpcore.ConnectionPool(network_backend=httpcore.MockBackend(response_buffer() * 2), max_keepalive_connections=1) as pool:
        first = pool.request("GET", "https://example.com/")
        second = pool.request("GET", "https://example.com/")
        check(first.content == second.content == b"Hello, world!", "pool response failed")
        check(len(pool.connections) == 1 and "Request Count: 2" in repr(pool.connections[0]), "pool did not reuse connection")


def pool_close_header() -> None:
    import httpcore

    with httpcore.ConnectionPool(network_backend=httpcore.MockBackend(response_buffer())) as pool:
        response = pool.request("GET", "https://example.com/", headers={"Connection": "close"})
        check(response.content == b"Hello, world!" and pool.connections == [], "close header retained connection")


def pool_trace() -> None:
    import httpcore

    events: list[str] = []
    with httpcore.ConnectionPool(network_backend=httpcore.MockBackend(response_buffer())) as pool:
        response = pool.request("GET", "http://example.com/", extensions={"trace": lambda name, kwargs: events.append(name)})
        check(response.status == 200, "trace request failed")
    check(events[:2] == ["connection.connect_tcp.started", "connection.connect_tcp.complete"], "trace start events failed")
    check("http11.receive_response_body.complete" in events, "trace body event missing")


async def async_http11_basic() -> None:
    import httpcore

    async with httpcore.AsyncHTTP11Connection(
        origin=httpcore.Origin(b"https", b"example.com", 443), stream=httpcore.AsyncMockStream(response_buffer())
    ) as conn:
        response = await conn.request("GET", "https://example.com/")
        check(response.status == 200 and response.content == b"Hello, world!", "async HTTP/1.1 failed")
        check(conn.is_idle() and conn.is_available(), "async connection state failed")


async def async_http11_interim() -> None:
    import httpcore

    stream = httpcore.AsyncMockStream([
        b"HTTP/1.1 103 Early Hints\r\n", b"Link: </a.css>\r\n", b"\r\n",
        b"HTTP/1.1 200 OK\r\n", b"Content-Length: 2\r\n", b"\r\n", b"ok",
    ])
    async with httpcore.AsyncHTTP11Connection(
        origin=httpcore.Origin(b"https", b"example.com", 443), stream=stream
    ) as conn:
        response = await conn.request("GET", "https://example.com/")
        check(response.status == 200 and response.content == b"ok", "async interim failed")


async def async_pool_keepalive() -> None:
    import httpcore

    async with httpcore.AsyncConnectionPool(
        network_backend=httpcore.AsyncMockBackend(response_buffer() * 2), max_keepalive_connections=1
    ) as pool:
        first = await pool.request("GET", "https://example.com/")
        second = await pool.request("GET", "https://example.com/")
        check(first.content == second.content == b"Hello, world!", "async pool response failed")
        check(len(pool.connections) == 1 and "Request Count: 2" in repr(pool.connections[0]), "async pool reuse failed")


async def async_trace() -> None:
    import httpcore

    events: list[str] = []

    async def trace(name, kwargs):
        events.append(name)

    async with httpcore.AsyncConnectionPool(network_backend=httpcore.AsyncMockBackend(response_buffer())) as pool:
        response = await pool.request("GET", "http://example.com/", extensions={"trace": trace})
        check(response.status == 200, "async trace request failed")
    check(events[:2] == ["connection.connect_tcp.started", "connection.connect_tcp.complete"], "async trace start failed")
    check("http11.receive_response_body.complete" in events, "async trace body missing")


def http2_basic() -> None:
    import hpack
    import hyperframe.frame
    import httpcore

    stream = httpcore.MockBackend(
        [
            hyperframe.frame.SettingsFrame().serialize(),
            hyperframe.frame.HeadersFrame(stream_id=1, data=hpack.Encoder().encode([(b":status", b"200")]), flags=["END_HEADERS"]).serialize(),
            hyperframe.frame.DataFrame(stream_id=1, data=b"h2", flags=["END_STREAM"]).serialize(),
        ],
        http2=True,
    )
    with httpcore.ConnectionPool(network_backend=stream) as pool:
        response = pool.request("GET", "https://example.com/")
        check(response.status == 200 and response.content == b"h2", "HTTP/2 response failed")
        check("HTTP/2" in repr(pool.connections[0]), "HTTP/2 connection not retained")


def interfaces() -> None:
    import httpcore

    sync = httpcore.ConnectionPool(network_backend=httpcore.MockBackend(response_buffer()))
    async_pool = httpcore.AsyncConnectionPool(network_backend=httpcore.AsyncMockBackend(response_buffer()))
    check(hasattr(sync, "handle_request"), "sync request interface failed")
    check(hasattr(async_pool, "handle_async_request"), "async request interface failed")
    sync.close()
    asyncio.run(async_pool.aclose())


def exception_contracts() -> None:
    import httpcore

    check(issubclass(httpcore.ConnectError, httpcore.NetworkError), "ConnectError hierarchy changed")
    check(issubclass(httpcore.RemoteProtocolError, httpcore.ProtocolError), "RemoteProtocolError hierarchy changed")
    check(issubclass(httpcore.PoolTimeout, httpcore.TimeoutException), "PoolTimeout hierarchy changed")
    check(issubclass(httpcore.WriteTimeout, httpcore.TimeoutException), "WriteTimeout hierarchy changed")


def deterministic_projection() -> None:
    import httpcore

    def snapshot():
        return {
            "url": repr(httpcore.URL("https://example.com/path?q=1")),
            "request": repr(httpcore.Request("GET", "https://example.com/")),
            "response": repr(httpcore.Response(204)),
            "origin": str(httpcore.URL("https://example.com/").origin),
        }

    check(snapshot() == snapshot(), "model projection changed between fresh values")


SCENARIOS = {
    "api-surface": api_surface,
    "url-origin-proxy": url_origin_proxy,
    "request-model": request_model,
    "response-buffered": response_buffered,
    "response-sync-stream": response_sync_stream,
    "response-async-stream": response_async_stream,
    "mock-stream": mock_stream,
    "http11-basic": http11_basic,
    "http11-post-body": http11_post_body,
    "http11-interim": http11_interim,
    "http11-upgrade": http11_upgrade,
    "http11-errors": http11_errors,
    "http11-lifecycle": http11_lifecycle,
    "pool-keepalive": pool_keepalive,
    "pool-close-header": pool_close_header,
    "pool-trace": pool_trace,
    "async-http11-basic": async_http11_basic,
    "async-http11-interim": async_http11_interim,
    "async-pool-keepalive": async_pool_keepalive,
    "async-trace": async_trace,
    "http2-basic": http2_basic,
    "interfaces": interfaces,
    "exception-contracts": exception_contracts,
    "deterministic-projection": deterministic_projection,
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scenario", choices=sorted(SCENARIOS), required=True)
    parser.add_argument("--candidate-site", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    import sys

    dependency_site = os.environ.get("NL2REPO_CANDIDATE_DEPENDENCIES")
    if dependency_site:
        sys.path.insert(0, dependency_site)
    sys.path.insert(0, args.candidate_site)
    verdict = {"scenario": args.scenario, "status": "failed"}
    try:
        result = SCENARIOS[args.scenario]()
        if asyncio.iscoroutine(result):
            asyncio.run(result)
    except BaseException:
        verdict["message"] = traceback.format_exc(limit=10)[-2400:]
    else:
        verdict["status"] = "passed"
    args.output.write_text(json.dumps(verdict, sort_keys=True), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
