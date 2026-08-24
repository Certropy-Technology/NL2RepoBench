import asyncio

import httpx
import pytest


def response_for(request: httpx.Request) -> httpx.Response:
    if request.url.path == "/redirect":
        return httpx.Response(302, headers={"location": "/final"})
    if request.url.path == "/final":
        return httpx.Response(200, json={"path": str(request.url)})
    if request.url.path == "/set-cookie":
        return httpx.Response(200, headers={"set-cookie": "session=abc"})
    if request.url.path == "/echo":
        return httpx.Response(200, json={"method": request.method, "url": str(request.url), "headers": dict(request.headers), "content": request.content.decode()})
    return httpx.Response(200, text="hello")


def client(transport=None, **kwargs):
    return httpx.Client(transport=transport or httpx.MockTransport(response_for), **kwargs)


def test_sync_get_response():
    with client() as http:
        response = http.get("https://example.test/")
    assert (response.status_code, response.text) == (200, "hello")


def test_sync_post_content():
    with client() as http:
        response = http.post("https://example.test/echo", content="payload")
    assert response.json()["content"] == "payload"


def test_sync_post_json():
    with client() as http:
        response = http.post("https://example.test/echo", json={"a": 1})
    assert response.json()["content"] == '{"a":1}'


def test_sync_request_method_and_url():
    with client() as http:
        response = http.request("PUT", "https://example.test/echo")
    assert response.json()["method"] == "PUT"
    assert response.json()["url"] == "https://example.test/echo"


def test_sync_headers_merge():
    with client(headers={"X-Client": "one"}) as http:
        response = http.get("https://example.test/echo", headers={"X-Request": "two"})
    headers = response.json()["headers"]
    assert headers["x-client"] == "one"
    assert headers["x-request"] == "two"


def test_sync_query_parameters():
    with client(params={"a": "b"}) as http:
        response = http.get("https://example.test/echo", params={"c": "d"})
    assert response.json()["url"] == "https://example.test/echo?a=b&c=d"


def test_sync_cookie_send():
    with client(cookies={"session": "abc"}) as http:
        response = http.get("https://example.test/echo")
    assert response.json()["headers"]["cookie"] == "session=abc"


def test_sync_cookie_persistence():
    with client() as http:
        http.get("https://example.test/set-cookie")
        response = http.get("https://example.test/echo")
    assert response.json()["headers"]["cookie"] == "session=abc"


def test_sync_redirect_following():
    with client(follow_redirects=True) as http:
        response = http.get("https://example.test/redirect")
    assert response.status_code == 200
    assert response.json()["path"] == "https://example.test/final"


def test_sync_redirect_disabled():
    with client() as http:
        response = http.get("https://example.test/redirect")
    assert (response.status_code, response.headers["location"]) == (302, "/final")


def test_sync_basic_auth():
    with client() as http:
        response = http.get("https://example.test/echo", auth=("user", "pass"))
    assert response.json()["headers"]["authorization"] == "Basic dXNlcjpwYXNz"


def test_sync_event_hooks():
    events = []
    def on_request(request):
        events.append(("request", request.method))
    def on_response(response):
        events.append(("response", response.status_code))
    with client(event_hooks={"request": [on_request], "response": [on_response]}) as http:
        http.get("https://example.test/")
    assert events == [("request", "GET"), ("response", 200)]


def test_sync_stream_response():
    def stream_response(request):
        return httpx.Response(200, content=b"one\ntwo\n")
    with client(httpx.MockTransport(stream_response)) as http:
        with http.stream("GET", "https://example.test/") as response:
            assert list(response.iter_lines()) == ["one", "two"]


def test_sync_raise_for_status():
    def missing(request):
        return httpx.Response(404)
    with client(httpx.MockTransport(missing)) as http:
        response = http.get("https://example.test/")
    with pytest.raises(httpx.HTTPStatusError):
        response.raise_for_status()


def test_sync_client_close():
    http = client()
    http.close()
    assert http.is_closed
    with pytest.raises(RuntimeError):
        http.get("https://example.test/")


def test_sync_custom_mount():
    def mounted(request):
        return httpx.Response(201, text="mounted")
    with client(mounts={"https://special.test": httpx.MockTransport(mounted)}) as http:
        response = http.get("https://special.test/")
    assert (response.status_code, response.text) == (201, "mounted")


def test_async_get_response():
    async def run():
        async with httpx.AsyncClient(transport=httpx.MockTransport(response_for)) as http:
            return await http.get("https://example.test/")
    response = asyncio.run(run())
    assert (response.status_code, response.text) == (200, "hello")


def test_async_post_json():
    async def run():
        async with httpx.AsyncClient(transport=httpx.MockTransport(response_for)) as http:
            return await http.post("https://example.test/echo", json={"a": 1})
    assert asyncio.run(run()).json()["content"] == '{"a":1}'


def test_async_stream_response():
    async def run():
        async with httpx.AsyncClient(transport=httpx.MockTransport(response_for)) as http:
            async with http.stream("GET", "https://example.test/") as response:
                return [line async for line in response.aiter_lines()]
    assert asyncio.run(run()) == ["hello"]


def test_async_custom_mount():
    async def mounted(request):
        return httpx.Response(202, text="mounted")
    async def run():
        mounts = {"https://special.test": httpx.MockTransport(mounted)}
        async with httpx.AsyncClient(transport=httpx.MockTransport(response_for), mounts=mounts) as http:
            return await http.get("https://special.test/")
    response = asyncio.run(run())
    assert (response.status_code, response.text) == (202, "mounted")


def test_async_event_hooks():
    events = []
    async def on_request(request):
        events.append(("request", request.method))
    async def on_response(response):
        events.append(("response", response.status_code))
    async def run():
        async with httpx.AsyncClient(transport=httpx.MockTransport(response_for), event_hooks={"request": [on_request], "response": [on_response]}) as http:
            await http.get("https://example.test/")
    asyncio.run(run())
    assert events == [("request", "GET"), ("response", 200)]


def test_async_redirect_following():
    async def run():
        async with httpx.AsyncClient(transport=httpx.MockTransport(response_for), follow_redirects=True) as http:
            return await http.get("https://example.test/redirect")
    response = asyncio.run(run())
    assert response.json()["path"] == "https://example.test/final"


def test_async_client_close():
    async def run():
        http = httpx.AsyncClient(transport=httpx.MockTransport(response_for))
        await http.aclose()
        return http.is_closed
    assert asyncio.run(run())


def test_async_raise_for_status():
    async def missing(request):
        return httpx.Response(404)
    async def run():
        async with httpx.AsyncClient(transport=httpx.MockTransport(missing)) as http:
            response = await http.get("https://example.test/")
        with pytest.raises(httpx.HTTPStatusError):
            response.raise_for_status()
    asyncio.run(run())
