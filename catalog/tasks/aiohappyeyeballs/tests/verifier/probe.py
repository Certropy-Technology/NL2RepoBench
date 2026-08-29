from __future__ import annotations

import asyncio
import importlib.metadata
import json
import socket
import sys
from pathlib import Path
from typing import Any


sys.path.insert(0, "/tmp/candidate-site")


def _record(family: int, host: str, port: int, *, flow: int = 0, scope: int = 0) -> tuple[Any, ...]:
    address: tuple[Any, ...] = (host, port, flow, scope) if family == socket.AF_INET6 else (host, port)
    return (family, socket.SOCK_STREAM, socket.IPPROTO_TCP, "", address)


def _json_value(value: Any) -> Any:
    if isinstance(value, tuple):
        return [_json_value(item) for item in value]
    if isinstance(value, list):
        return [_json_value(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _json_value(item) for key, item in value.items()}
    return value


async def _loopback_connection(module: Any, *, fallback: bool = False, delay: float | None = None, local: bool = False, factory: bool = False) -> dict[str, Any]:
    received = asyncio.Event()

    async def handler(reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        await reader.readexactly(1)
        received.set()
        writer.close()
        await writer.wait_closed()

    server = await asyncio.start_server(handler, "127.0.0.1", 0)
    port = server.sockets[0].getsockname()[1]
    addresses = [_record(socket.AF_INET, "127.0.0.1", port)]
    if fallback:
        temporary = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        temporary.bind(("127.0.0.1", 0))
        refused_port = temporary.getsockname()[1]
        temporary.close()
        addresses.insert(0, _record(socket.AF_INET, "127.0.0.1", refused_port))
    seen: list[int] = []

    def socket_factory(addr_info: Any) -> socket.socket:
        seen.append(addr_info[0])
        family, type_, proto, _, _ = addr_info
        return socket.socket(family=family, type=type_, proto=proto)

    kwargs: dict[str, Any] = {}
    if delay is not None:
        kwargs["happy_eyeballs_delay"] = delay
    if local:
        kwargs["local_addr_infos"] = [_record(socket.AF_INET, "127.0.0.1", 0)]
    if factory:
        kwargs["socket_factory"] = socket_factory
    try:
        client = await module.start_connection(addresses, **kwargs)
        try:
            peer = client.getpeername()
            bound = client.getsockname()
            await asyncio.get_running_loop().sock_sendall(client, b"x")
            await asyncio.wait_for(received.wait(), timeout=1.0)
        finally:
            client.close()
        return {
            "peer": [peer[0], peer[1]],
            "bound_host": bound[0],
            "bound_port_positive": bound[1] > 0,
            "factory_families": seen,
        }
    finally:
        server.close()
        await server.wait_closed()


async def _main(request: dict[str, Any]) -> Any:
    import aiohappyeyeballs as module

    operation = request["operation"]
    if operation == "exports":
        return {"all": list(module.__all__), "version": module.__version__, "typed": (Path(module.__file__).parent / "py.typed").is_file()}
    if operation == "metadata":
        return {"name": importlib.metadata.metadata("aiohappyeyeballs")["Name"], "version": importlib.metadata.version("aiohappyeyeballs"), "requires": importlib.metadata.requires("aiohappyeyeballs") or []}
    if operation == "addr-to":
        return _json_value(module.addr_to_addr_infos(request["addr"]))
    if operation == "pop":
        values = [_record(*item) for item in request["records"]]
        module.pop_addr_infos_interleave(values, request.get("interleave"))
        return _json_value(values)
    if operation == "remove":
        values = [_record(*item) for item in request["records"]]
        try:
            module.remove_addr_infos(values, tuple(request["addr"]))
        except ValueError as error:
            return {"error": type(error).__name__, "contains": "not found" in str(error)}
        return _json_value(values)
    if operation == "start-empty":
        try:
            await module.start_connection([])
        except ValueError as error:
            return {"error": type(error).__name__, "contains": "must not be empty" in str(error)}
        return {"error": None}
    if operation == "start-loopback":
        return await _loopback_connection(module)
    if operation == "start-fallback":
        return await _loopback_connection(module, fallback=True)
    if operation == "start-happy":
        return await _loopback_connection(module, fallback=True, delay=0.01)
    if operation == "start-local":
        return await _loopback_connection(module, local=True)
    if operation == "start-factory":
        return await _loopback_connection(module, factory=True)
    raise KeyError(f"unknown operation: {operation}")


request = json.loads(sys.stdin.read())
try:
    response = {"ok": True, "value": asyncio.run(_main(request))}
except BaseException as error:
    response = {"ok": False, "error": f"{type(error).__name__}: {error}"}
print(json.dumps(response, sort_keys=True, separators=(",", ":")))
