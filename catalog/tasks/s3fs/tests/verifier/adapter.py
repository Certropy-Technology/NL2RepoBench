from __future__ import annotations

import argparse
import asyncio
import importlib.metadata
import json
import os
import resource
import sys
from pathlib import Path
from typing import Any

RESULT_PREFIX = "NL2REPO_S3FS_RESULT="


def _limits() -> None:
    resource.setrlimit(resource.RLIMIT_AS, (512 * 1024 * 1024, 512 * 1024 * 1024))
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
    resource.setrlimit(resource.RLIMIT_CPU, (12, 12))
    resource.setrlimit(resource.RLIMIT_FSIZE, (1024 * 1024, 1024 * 1024))
    resource.setrlimit(resource.RLIMIT_NOFILE, (64, 64))
    resource.setrlimit(resource.RLIMIT_NPROC, (32, 32))


def _error(action: Any) -> dict[str, Any]:
    try:
        action()
    except BaseException as exc:
        return {"type": f"{type(exc).__module__}.{type(exc).__qualname__}", "message": str(exc)}
    return {"type": None, "message": None}


async def _error_async(action: Any) -> dict[str, Any]:
    try:
        await action()
    except BaseException as exc:
        return {"type": f"{type(exc).__module__}.{type(exc).__qualname__}", "message": str(exc)}
    return {"type": None, "message": None}


class Body:
    def __init__(self, data: bytes):
        self.data = data
        self.closed = False

    async def read(self, size: int = -1) -> bytes:
        if size is None or size < 0:
            out, self.data = self.data, b""
        else:
            out, self.data = self.data[:size], self.data[size:]
        return out

    def close(self) -> None:
        self.closed = True


def _fake_call(responses: dict[str, Any], calls: list[dict[str, Any]]):
    async def call(method: str, *args: Any, **kwargs: Any) -> Any:
        calls.append({"method": method, "kwargs": kwargs})
        value = responses.get(method, {})
        if callable(value):
            value = value(method, kwargs)
        return value

    return call


def _call_sync(responses: dict[str, Any], calls: list[dict[str, Any]], method: str, kwargs: dict[str, Any]) -> Any:
    calls.append({"method": method, "kwargs": kwargs})
    value = responses.get(method, {})
    return value(method, kwargs) if callable(value) else value


def _fs():
    from s3fs import S3FileSystem

    return S3FileSystem(skip_instance_cache=True, anon=True)


def exercise(name: str) -> Any:
    import s3fs
    from botocore.exceptions import ClientError
    from s3fs import S3FileSystem, S3Map, add_retryable_error, set_custom_error_handler
    from s3fs.core import calculate_chunksize, version_id_kw
    from s3fs.errors import translate_boto_error
    from s3fs.utils import SSEParams, title_case

    if name == "exports-and-metadata":
        return {
            "exports": sorted(name for name in ("S3FileSystem", "S3File", "S3Map", "add_retryable_error", "set_custom_error_handler") if hasattr(s3fs, name)),
            "version": s3fs.__version__,
            "distribution": importlib.metadata.version("s3fs"),
            "module": s3fs.S3FileSystem.__module__,
        }

    if name == "constructor-options":
        fs = S3FileSystem(skip_instance_cache=True, anon=True, endpoint_url="http://example.invalid", default_block_size=123, default_cache_type="none", version_aware=True, requester_pays=True, max_concurrency=3, fixed_upload_size=True, local_expiry_check=True)
        return {"anon": fs.anon, "endpoint": fs.endpoint_url, "block": fs.default_block_size, "cache": fs.default_cache_type, "version_aware": fs.version_aware, "requester_pays": fs.requester_pays, "req_kw": fs.req_kw, "protocol": list(fs.protocol), "concurrency": fs.max_concurrency, "fixed": fs.fixed_upload_size, "expiry": fs.local_expiry_check}

    if name == "constructor-validation":
        return {
            "key_conflict": _error(lambda: S3FileSystem(key="k", username="u")),
            "secret_conflict": _error(lambda: S3FileSystem(secret="s", password="p")),
            "bad_concurrency": _error(lambda: S3FileSystem(max_concurrency=0)),
            "aliases": (lambda fs: [fs.key, fs.secret])(S3FileSystem(username="u", password="p", skip_instance_cache=True)),
        }

    if name == "split-paths":
        plain = S3FileSystem(skip_instance_cache=True, anon=True)
        aware = S3FileSystem(skip_instance_cache=True, anon=True, version_aware=True)
        return {"plain": [plain.split_path(x) for x in ["s3://bucket/key", "s3a://bucket/key/", "bucket"]], "aware_version": aware.split_path("s3://bucket/key?versionId=v1"), "plain_version": plain.split_path("bucket/key?versionId=v1"), "access_point": aware.split_path("arn:aws:s3:us-east-1:123456789012:accesspoint/ap/key")}

    if name == "chunking-and-version-helper":
        return {"chunks": [calculate_chunksize(x) for x in [0, 1, 50 * 2**20, 50 * 2**20 + 1]], "large": calculate_chunksize(5 * 2**40), "version_ids": [version_id_kw(None), version_id_kw(""), version_id_kw("v1")]}

    if name == "utils-serialization":
        return {"title": [title_case(x) for x in ["content_type", "etag", "x_amz_meta_foo", ""]], "sse": SSEParams(server_side_encryption="AES256", sse_kms_key_id="kid").to_kwargs(), "empty_sse": SSEParams().to_kwargs()}

    if name == "error-translation":
        original = ClientError({"Error": {"Code": "NoSuchKey", "Message": "missing"}}, "GetObject")
        translated = translate_boto_error(original)
        unknown = translate_boto_error(ClientError({"Error": {"Code": "Weird", "Message": "bad"}}, "GetObject"))
        return {"known": {"type": type(translated).__name__, "message": str(translated), "cause": translated.__cause__ is original}, "unknown": {"type": type(unknown).__name__, "errno": unknown.errno}}

    if name == "retry-configuration":
        import s3fs.core as core
        class CustomError(Exception):
            pass
        before = len(core.S3_RETRYABLE_ERRORS)
        handler = lambda exc: isinstance(exc, CustomError)
        add_retryable_error(CustomError)
        set_custom_error_handler(handler)
        return {"grew": len(core.S3_RETRYABLE_ERRORS) == before + 1, "registered": CustomError in core.S3_RETRYABLE_ERRORS, "handler": core.CUSTOM_ERROR_HANDLER is handler}

    if name == "root-and-cache":
        fs = _fs()
        fs.dircache[""] = [{"name": "bucket", "type": "directory"}]
        return {"root": fs.exists(""), "before": list(fs.dircache), "after": (fs.invalidate_cache(), list(fs.dircache))}

    if name == "cached-listing":
        fs = _fs()
        fs.dircache["bucket"] = [{"name": "bucket/z", "type": "file", "size": 2}, {"name": "bucket/a", "type": "file", "size": 1}]
        return {"names": fs.ls("bucket"), "detail": fs.ls("bucket", detail=True), "cached": fs.ls("bucket")}

    if name == "fake-info":
        fs = _fs()
        calls: list[dict[str, Any]] = []
        fs._call_s3 = _fake_call({"head_object": {"ContentLength": 7, "ETag": '"abc"', "ContentType": "text/plain", "StorageClass": "STANDARD"}}, calls)
        return {"info": fs.info("bucket/key"), "call": calls}

    if name == "fake-exists":
        fs = _fs()
        calls: list[dict[str, Any]] = []
        fs._call_s3 = _fake_call({"head_object": {"ContentLength": 1}, "head_bucket": {}}, calls)
        return {"object": fs.exists("bucket/key"), "bucket": fs.exists("bucket"), "calls": [call["method"] for call in calls]}

    if name == "pipe-file":
        fs = _fs()
        calls: list[dict[str, Any]] = []
        fs._call_s3 = _fake_call({"put_object": {"ETag": "etag"}}, calls)
        result = fs.pipe_file("bucket/key.txt", b"abc")
        return {"result": result, "method": calls[0]["method"], "bucket": calls[0]["kwargs"]["Bucket"], "key": calls[0]["kwargs"]["Key"], "body": calls[0]["kwargs"]["Body"].decode()}

    if name == "buffered-read":
        fs = _fs()
        calls: list[dict[str, Any]] = []
        body = Body(b"abcdef")
        fs._call_s3 = _fake_call({"get_object": {"Body": body, "ETag": '"etag"', "ContentLength": 6}, "head_object": {"ContentLength": 6, "ETag": '"etag"'}}, calls)
        file = fs.open("bucket/key", "rb", size=6, cache_type="none")
        value = file.read()
        file.close()
        return {"value": value.decode(), "range": calls[0]["kwargs"].get("Range"), "closed": body.closed}

    if name == "buffered-write":
        fs = _fs()
        calls: list[dict[str, Any]] = []
        response = {"put_object": {"ETag": "etag"}}
        fs._call_s3 = _fake_call(response, calls)
        fs.call_s3 = lambda method, *args, **kwargs: _call_sync(response, calls, method, kwargs)
        file = fs.open("bucket/key", "wb")
        written = file.write(b"hello")
        file.close()
        return {"written": written, "method": calls[0]["method"], "body": calls[0]["kwargs"]["Body"].decode(), "bucket": calls[0]["kwargs"]["Bucket"], "key": calls[0]["kwargs"]["Key"]}

    if name == "async-stream":
        async def run() -> Any:
            fs = _fs()
            body = Body(b"stream-data")
            fs._call_s3 = _fake_call({"get_object": {"Body": body, "ResponseMetadata": {"HTTPHeaders": {"content-length": "11"}}}}, [])
            stream = await fs.open_async("bucket/key", "rb")
            first = await stream.read(6)
            second = await stream.read()
            return {"first": first.decode(), "second": second.decode(), "loc": stream.loc, "size": stream.size}
        return asyncio.run(run())

    if name == "open-validation":
        async def run() -> Any:
            fs = _fs()
            return {"text": await _error_async(lambda: fs.open_async("bucket/key", "r")), "compression": await _error_async(lambda: fs.open_async("bucket/key", "rb", compression="gzip"))}
        return asyncio.run(run())

    if name == "mapping-factory":
        fs = _fs()
        mapping = S3Map("bucket/prefix", fs)
        return {"class": type(mapping).__name__, "root": mapping.root, "fs_class": type(mapping.fs).__name__, "check": mapping.check, "create": mapping.create}

    if name == "requester-pays":
        fs = S3FileSystem(skip_instance_cache=True, anon=True, requester_pays=True)
        file = fs.open("bucket/key", "wb")
        value = {"fs": fs.req_kw, "file": file.req_kw, "requester": file._request_payer_kw}
        file.discard()
        file.closed = True
        return value

    if name == "cache-invalidation":
        fs = _fs()
        fs.dircache = {"": [], "bucket": [], "bucket/dir": [], "bucket/dir/file": []}
        fs.invalidate_cache("bucket/dir/file")
        return {"remaining": sorted(fs.dircache)}

    raise ValueError(f"unknown scenario: {name}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate-site", required=True)
    parser.add_argument("--scenario", required=True)
    args = parser.parse_args()
    _limits()
    sys.path.insert(0, str(Path(args.candidate_site).resolve()))
    dependencies = os.environ.get("NL2REPO_CANDIDATE_DEPENDENCIES")
    if dependencies:
        sys.path.append(str(Path(dependencies).resolve()))
    try:
        value = exercise(args.scenario)
        result = {"ok": True, "value": value}
    except BaseException as exc:
        result = {"ok": False, "exception_type": f"{type(exc).__module__}.{type(exc).__qualname__}", "exception_message": str(exc)}
    print(RESULT_PREFIX + json.dumps(result, default=lambda value: sorted(value) if isinstance(value, set) else repr(value), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
