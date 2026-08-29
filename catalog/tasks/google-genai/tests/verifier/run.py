from __future__ import annotations

import json
import textwrap
from collections.abc import Callable
from typing import Any

from nl2repobench.verification.candidate_client import execute_script

LeafCheck = tuple[str, str, Any | Callable[[Any], bool]]
leaves: list[dict[str, str]] = []


def add_leaf(leaf_id: str, passed: bool, message: str = "") -> None:
    leaf = {"id": leaf_id, "status": "passed" if passed else "failed"}
    if not passed:
        leaf["message"] = message[-2000:] or "observation did not match contract"
    leaves.append(leaf)


def run_group(source: str, checks: list[LeafCheck]) -> None:
    result = execute_script(textwrap.dedent(source), timeout_sec=15.0)
    if not result.ok or not isinstance(result.value, dict):
        detail = f"{result.exception_type}: {result.exception_message}"
        for leaf_id, _, _ in checks:
            add_leaf(leaf_id, False, detail)
        return
    for leaf_id, key, expected in checks:
        actual = result.value.get(key, object())
        try:
            passed = expected(actual) if callable(expected) else actual == expected
        except Exception as exc:
            passed = False
            actual = f"predicate error: {type(exc).__name__}: {exc}; actual={actual!r}"
        add_leaf(leaf_id, passed, f"expected={expected!r}; actual={actual!r}")


run_group(
    """
    import importlib.metadata
    import google.genai as genai
    from google.genai import errors, types
    result = {
        "metadata": importlib.metadata.version("google-genai"),
        "exports": all(hasattr(genai, name) for name in ("Client", "types", "errors")),
        "type_exports": all(hasattr(types, name) for name in (
            "Part", "Content", "UserContent", "ModelContent",
            "GenerateContentResponse", "HttpOptions",
        )),
    }
    """,
    [
        ("pkg.metadata", "metadata", "2.20.0"),
        ("pkg.root-exports", "exports", True),
        ("pkg.type-exports", "type_exports", True),
    ],
)

run_group(
    """
    from google.genai import types

    def dump(value):
        return value.model_dump(mode="json", exclude_none=True)

    result = {
        "text": dump(types.Part.from_text(text="hello")),
        "bytes": dump(types.Part.from_bytes(data=b"abc", mime_type="text/plain")),
        "uri": dump(types.Part.from_uri(file_uri="gs://bucket/cat.png")),
        "call": dump(types.Part.from_function_call(name="sum", args={"x": 2})),
        "response": dump(types.Part.from_function_response(name="sum", response={"result": 3})),
        "code": dump(types.Part.from_executable_code(
            code="print(1)", language=types.Language.PYTHON
        )),
        "code_result": dump(types.Part.from_code_execution_result(
            outcome=types.Outcome.OUTCOME_OK, output="1\\n"
        )),
        "ctor_string": dump(types.Part("hello")),
        "enum": types.HarmCategory("harm_category_hate_speech").value,
    }
    try:
        types.Part({"text": "a"}, text="b")
    except Exception as exc:
        result["ctor_conflict"] = [type(exc).__name__, str(exc)]
    """,
    [
        ("part.from-text", "text", {"text": "hello"}),
        ("part.from-bytes", "bytes", {"inline_data": {"data": "YWJj", "mime_type": "text/plain"}}),
        (
            "part.from-uri",
            "uri",
            {"file_data": {"file_uri": "gs://bucket/cat.png", "mime_type": "image/png"}},
        ),
        ("part.from-function-call", "call", {"function_call": {"args": {"x": 2}, "name": "sum"}}),
        (
            "part.from-function-response",
            "response",
            {"function_response": {"name": "sum", "response": {"result": 3}}},
        ),
        (
            "part.from-executable-code",
            "code",
            {"executable_code": {"code": "print(1)", "language": "PYTHON"}},
        ),
        (
            "part.from-code-result",
            "code_result",
            {"code_execution_result": {"outcome": "OUTCOME_OK", "output": "1\n"}},
        ),
        ("part.positional-string", "ctor_string", {"text": "hello"}),
        (
            "part.positional-keyword-conflict",
            "ctor_conflict",
            [
                "ValueError",
                "Positional and keyword arguments can not be combined when initializing a Part.",
            ],
        ),
        ("types.case-insensitive-enum", "enum", "HARM_CATEGORY_HATE_SPEECH"),
    ],
)

run_group(
    """
    from google.genai import _transformers as t
    from google.genai import types

    def dump(value):
        return value.model_dump(mode="json", exclude_none=True)

    result = {
        "user": dump(types.UserContent("hello")),
        "model": dump(types.ModelContent([{"text": "hi"}])),
        "part": dump(t.t_part("hello")),
        "parts": [dump(x) for x in t.t_parts(["a", {"text": "b"}])],
        "content": dump(t.t_content("hello")),
        "contents": [dump(x) for x in t.t_contents([
            "a",
            types.Part.from_function_call(name="f", args={}),
            types.Part.from_function_response(name="f", response={"x": 1}),
            "b",
        ])],
    }
    for key, function in (("bad_part", t.t_part), ("bad_content", t.t_content)):
        try:
            function(5)
        except Exception as exc:
            result[key] = [type(exc).__name__, str(exc)]
    """,
    [
        ("content.user-role", "user", {"parts": [{"text": "hello"}], "role": "user"}),
        ("content.model-role", "model", {"parts": [{"text": "hi"}], "role": "model"}),
        ("transform.part", "part", {"text": "hello"}),
        ("transform.parts", "parts", [{"text": "a"}, {"text": "b"}]),
        ("transform.content", "content", {"parts": [{"text": "hello"}], "role": "user"}),
        (
            "transform.contents-grouping",
            "contents",
            [
                {"parts": [{"text": "a"}], "role": "user"},
                {"parts": [{"function_call": {"args": {}, "name": "f"}}], "role": "model"},
                {
                    "parts": [
                        {"function_response": {"name": "f", "response": {"x": 1}}},
                        {"text": "b"},
                    ],
                    "role": "user",
                },
            ],
        ),
        (
            "transform.part-invalid",
            "bad_part",
            ["ValueError", "Unsupported content part type: <class 'int'>"],
        ),
        (
            "transform.content-invalid",
            "bad_content",
            ["ValueError", "Unsupported content part type: <class 'int'>"],
        ),
    ],
)

run_group(
    """
    from google.genai import _api_client, _common, types

    result = {
        "joins": [
            _api_client.join_url_path("https://x.test/base/", "/v1"),
            _api_client.join_url_path("https://x.test/base", "v1"),
            _api_client.join_url_path("https://x.test/", ""),
        ],
    }
    headers = {"x": "1"}
    _api_client.populate_server_timeout_header(headers, 1.4)
    result["timeout_round"] = headers
    headers = {"X-Server-Timeout": "9"}
    _api_client.populate_server_timeout_header(headers, 1.6)
    result["timeout_keep"] = headers
    base = types.HttpOptions(base_url="a", headers={"A": "1", "B": "2"}, timeout=1000)
    patch = types.HttpOptions(headers={"B": "3", "C": "4"}, api_version="v1")
    merged = _api_client.patch_http_options(base, patch)
    result["patch"] = {
        "base_url": merged.base_url,
        "api_version": merged.api_version,
        "timeout": merged.timeout,
        "headers": {key: merged.headers[key] for key in ("A", "B", "C")},
        "inputs_unchanged": (
            base.headers == {"A": "1", "B": "2"}
            and patch.headers == {"B": "3", "C": "4"}
        ),
    }
    target = {"A": {"b": 1}, "C": 2}
    _common.recursive_dict_update(target, {"a": {"D": 3}, "c": 4})
    result["recursive"] = target
    result["align"] = _common.align_key_case(
        {"camelCase": {"InnerKey": 1}},
        {"CAMEL_CASE": {"inner_key": 2, "new": 3}},
    )
    """,
    [
        (
            "client.join-url",
            "joins",
            ["https://x.test/base/v1", "https://x.test/base/v1", "https://x.test/"],
        ),
        ("client.timeout-rounding", "timeout_round", {"x": "1", "X-Server-Timeout": "2"}),
        ("client.timeout-preserve", "timeout_keep", {"X-Server-Timeout": "9"}),
        (
            "client.patch-options",
            "patch",
            {
                "base_url": "a",
                "api_version": "v1",
                "timeout": 1000,
                "headers": {"A": "1", "B": "3", "C": "4"},
                "inputs_unchanged": True,
            },
        ),
        ("common.recursive-update", "recursive", {"A": {"b": 1, "D": 3}, "C": 4}),
        ("common.align-key-case", "align", {"camelCase": {"InnerKey": 2, "new": 3}}),
    ],
)

run_group(
    """
    import pickle
    from google.genai import errors

    nested = errors.APIError(None, {"error": {"code": 400, "message": "bad", "status": "INVALID"}})
    outside = errors.APIError(None, {"code": 401, "message": "outside", "status": "NO"})
    rebuilt = pickle.loads(pickle.dumps(nested))
    result = {
        "parse": [
            nested.code, nested.message, nested.status,
            outside.code, outside.message, outside.status,
        ],
        "pickle": [
            type(rebuilt).__name__, rebuilt.code, rebuilt.message,
            rebuilt.status, str(rebuilt),
        ],
    }
    for key, code in (("client", 400), ("server", 500)):
        try:
            errors.APIError.raise_error(code, {"error": {"message": "boom"}}, None)
        except Exception as exc:
            result[key] = [type(exc).__name__, exc.code, exc.message]
    """,
    [
        ("errors.payload-parsing", "parse", [400, "bad", "INVALID", 401, "outside", "NO"]),
        ("errors.client-subclass", "client", ["ClientError", 400, "boom"]),
        ("errors.server-subclass", "server", ["ServerError", 500, "boom"]),
        (
            "errors.pickle-roundtrip",
            "pickle",
            [
                "APIError",
                400,
                "bad",
                "INVALID",
                "400 INVALID. {'error': {'code': 400, 'message': 'bad', 'status': 'INVALID'}}",
            ],
        ),
    ],
)

run_group(
    """
    from google.genai import types

    def dump(value):
        return value.model_dump(mode="json", exclude_none=True)

    response = types.GenerateContentResponse(candidates=[{
        "content": {"role": "model", "parts": [{"text": "A"}, {"text": "B"}]}
    }])
    called = types.GenerateContentResponse(candidates=[{
        "content": {"parts": [{"function_call": {"name": "f", "args": {"x": 1}}}]}
    }])
    empty = types.GenerateContentResponse()
    result = {
        "text_parts": [response.text, [dump(x) for x in response.parts]],
        "calls": [dump(x) for x in called.function_calls],
        "empty": [empty.text, empty.parts, empty.function_calls],
    }
    """,
    [
        ("response.text-and-parts", "text_parts", ["AB", [{"text": "A"}, {"text": "B"}]]),
        ("response.function-calls", "calls", [{"args": {"x": 1}, "name": "f"}]),
        ("response.empty-accessors", "empty", [None, None, None]),
    ],
)

run_group(
    """
    from google.genai import chats, types

    history = [
        {"role": "user", "parts": [{"text": "u1"}]},
        {"role": "model", "parts": [{"text": "m1"}]},
        {"role": "user", "parts": [{"text": "u2"}]},
        {"role": "model", "parts": []},
    ]
    chat = chats.Chat(modules=object(), model="gemini-test", history=history)
    dump = lambda values: [x.model_dump(mode="json", exclude_none=True) for x in values]
    comprehensive = dump(chat.get_history())
    curated = dump(chat.get_history(curated=True))
    chat.record_history(
        types.UserContent("u3"), [types.ModelContent("m3")], is_valid=True
    )
    result = {
        "curation": [len(comprehensive), comprehensive, len(curated), curated],
        "record": dump(chat.get_history(curated=True))[-2:],
    }
    """,
    [
        (
            "chat.curated-history",
            "curation",
            [
                4,
                [
                    {"role": "user", "parts": [{"text": "u1"}]},
                    {"role": "model", "parts": [{"text": "m1"}]},
                    {"role": "user", "parts": [{"text": "u2"}]},
                    {"role": "model", "parts": []},
                ],
                2,
                [
                    {"role": "user", "parts": [{"text": "u1"}]},
                    {"role": "model", "parts": [{"text": "m1"}]},
                ],
            ],
        ),
        (
            "chat.record-history",
            "record",
            [
                {"role": "user", "parts": [{"text": "u3"}]},
                {"role": "model", "parts": [{"text": "m3"}]},
            ],
        ),
    ],
)

run_group(
    """
    import asyncio
    from types import SimpleNamespace
    from google.genai.pagers import AsyncPager, Pager

    second = SimpleNamespace(models=["m3"], next_page_token=None, sdk_http_response="http2")
    calls = []
    def request(*, config):
        calls.append(dict(config))
        return second
    config = {"page_size": 2, "nested": {"x": 1}}
    first = SimpleNamespace(models=["m1", "m2"], next_page_token="next", sdk_http_response="http1")
    pager = Pager("models", request, first, config)
    config["nested"]["x"] = 9
    iterated = list(pager)
    try:
        pager.next_page()
    except Exception as exc:
        exhausted = [type(exc).__name__, str(exc)]

    async def observe_async():
        async def async_request(*, config):
            return SimpleNamespace(models=["a2"], next_page_token=None, sdk_http_response=None)
        value = AsyncPager("models", async_request, SimpleNamespace(
            models=["a1"], next_page_token="n", sdk_http_response=None
        ), {"page_size": 1})
        return [item async for item in value]

    result = {
        "properties": [
            pager.name, pager.page_size, pager.sdk_http_response,
            calls, pager.config["nested"],
        ],
        "iteration": iterated,
        "exhausted": exhausted,
        "async": asyncio.run(observe_async()),
    }
    """,
    [
        (
            "pager.properties-and-copy",
            "properties",
            [
                "models",
                2,
                "http2",
                [{"page_size": 2, "nested": {"x": 1}, "page_token": "next"}],
                {"x": 1},
            ],
        ),
        ("pager.sync-iteration", "iteration", ["m1", "m2", "m3"]),
        ("pager.exhaustion", "exhausted", ["IndexError", "No more pages to fetch."]),
        ("pager.async-iteration", "async", ["a1", "a2"]),
    ],
)

assert len(leaves) == 40, len(leaves)
print(json.dumps({"schema_version": "1.0", "leaves": leaves}, sort_keys=True))
