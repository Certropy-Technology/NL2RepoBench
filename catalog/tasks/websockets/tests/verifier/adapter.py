from __future__ import annotations

import asyncio
import json
import secrets
import sys
from contextlib import suppress
from pathlib import Path
from typing import Any
from unittest.mock import patch


def type_name(exc: BaseException) -> str:
    return f"{type(exc).__module__}.{type(exc).__qualname__}"


def parse_frame(data: bytes, mask: bool) -> Any:
    from websockets.frames import Frame
    from websockets.streams import StreamReader

    reader = StreamReader()
    reader.feed_data(data)
    reader.feed_eof()
    parser = Frame.parse(reader.read_exact, mask=mask)
    try:
        while True:
            next(parser)
    except StopIteration as stop:
        return stop.value


async def async_scenario(name: str) -> Any:
    from websockets.asyncio.messages import Assembler
    from websockets.frames import CONT, TEXT, Frame, Opcode

    if name == "assembler-fragments":
        assembler = Assembler()
        assembler.frames.put(Frame(TEXT, b"he", False))
        assembler.frames.put(Frame(CONT, b"llo", True))
        return await assembler.get()
    if name == "assembler-binary-decode":
        assembler = Assembler()
        assembler.frames.put(Frame(Opcode.BINARY, b"42", True))
        return await assembler.get(True)
    if name == "assembler-concurrency":
        assembler = Assembler()
        first_get = asyncio.create_task(assembler.get())
        await asyncio.sleep(0)
        try:
            await assembler.get()
        except Exception as exc:
            return type_name(exc)
        finally:
            first_get.cancel()
            with suppress(asyncio.CancelledError):
                await first_get
        return None
    raise ValueError(f"unknown async scenario: {name}")


def scenario(name: str) -> Any:
    from websockets.datastructures import Headers
    from websockets.exceptions import InvalidHeaderValue, InvalidURI, ProtocolError
    from websockets.frames import Close, Frame, Opcode
    from websockets.protocol import Protocol, Side
    from websockets.uri import parse_uri

    if name == "package-identity":
        import websockets

        return [
            websockets.__version__,
            "py.typed" in {p.name for p in Path(websockets.__path__[0]).iterdir()},
        ]
    if name == "root-exports":
        import websockets

        required = {
            "Headers",
            "MultipleValuesError",
            "Frame",
            "Close",
            "CloseCode",
            "Opcode",
            "Protocol",
            "Side",
            "State",
            "InvalidURI",
            "InvalidHeaderValue",
            "ProtocolError",
            "ConcurrencyError",
        }
        return [
            all(hasattr(websockets, item) for item in required),
            required.issubset(set(websockets.__all__)),
        ]
    if name == "headers-init":
        first = Headers({"Connection": "Upgrade"}, Server="websockets")
        second = Headers(first)
        return [list(first.raw_items()), second == first]
    if name == "headers-lookup":
        headers = Headers([("Server", "websockets")])
        return [headers["server"], "server" in headers, headers.get_all("SERVER"), len(headers)]
    if name == "headers-duplicates":
        headers = Headers([("X-Test", "one"), ("x-test", "two")])
        try:
            headers["X-Test"]
        except Exception as exc:
            return [type_name(exc), headers.get_all("x-test")]
        return None
    if name == "headers-mutation":
        headers = Headers([("A", "1"), ("B", "2")])
        headers["a"] = "3"
        del headers["A"]
        return [list(headers.raw_items()), headers.get_all("a"), len(headers)]
    if name == "headers-serialize":
        headers = Headers(connection="Upgrade", server="websockets")
        return [str(headers), headers.serialize().decode("latin-1"), repr(headers)]
    if name == "headers-invalid":
        headers = Headers()
        try:
            headers["X"] = "bad\r\nvalue"
        except Exception as exc:
            return type_name(exc)
        return None
    if name == "headers-copy":
        original = Headers(X="one")
        copy = original.copy()
        copy["Y"] = "two"
        return [list(original.raw_items()), list(copy.raw_items()), original == copy]
    if name == "uri-basic":
        uri = parse_uri("ws://EXAMPLE.com/chat?room=1")
        return [
            uri.secure,
            uri.host,
            uri.port,
            uri.path,
            uri.query,
            uri.resource_name,
            uri.user_info,
        ]
    if name == "uri-secure-userinfo":
        uri = parse_uri("wss://alice:secret@example.com:8443/x")
        return [uri.secure, uri.port, uri.user_info, uri.resource_name]
    if name == "uri-idna":
        uri = parse_uri("ws://例え.テスト/路径?q=值")
        return [uri.host, uri.path, uri.query]
    if name == "uri-invalid-scheme":
        try:
            parse_uri("http://example.com")
        except Exception as exc:
            return [type_name(exc), str(exc)]
        return None
    if name == "uri-invalid-fragment":
        try:
            parse_uri("ws://example.com/#fragment")
        except Exception as exc:
            return type_name(exc)
        return None
    if name == "frame-text":
        frame = Frame(Opcode.TEXT, b"hi")
        return [str(frame), frame.serialize(mask=False).hex(), frame.check()]
    if name == "frame-masked":
        frame = Frame(Opcode.TEXT, b"hi")
        with patch.object(secrets, "token_bytes", return_value=b"abcd"):
            wire = frame.serialize(mask=True)
        return wire.hex()
    if name == "frame-long":
        frame = Frame(Opcode.BINARY, b"x" * 126)
        wire = frame.serialize(mask=False)
        return [wire[:4].hex(), len(wire)]
    if name == "frame-parse":
        frame = parse_frame(bytes.fromhex("81026869"), mask=False)
        return [frame.opcode.name, frame.data.decode(), frame.fin, frame.rsv1]
    if name == "frame-invalid":
        try:
            Frame(Opcode.TEXT, b"x", rsv1=True).check()
        except Exception as exc:
            return type_name(exc)
        return None
    if name == "close-roundtrip":
        close = Close(1000, "bye")
        parsed = Close.parse(close.serialize())
        return [parsed.code, parsed.reason, str(parsed), close.serialize().hex()]
    if name == "close-invalid":
        try:
            Close.parse(bytes.fromhex("03ed"))
        except Exception as exc:
            return type_name(exc)
        return None
    if name == "exception-contract":
        from websockets.exceptions import (
            ConcurrencyError,
            InvalidHeaderValue,
            InvalidURI,
            ProtocolError,
            WebSocketException,
        )

        return [
            issubclass(InvalidURI, WebSocketException),
            issubclass(InvalidHeaderValue, WebSocketException),
            issubclass(ProtocolError, WebSocketException),
            issubclass(ConcurrencyError, RuntimeError),
        ]
    if name == "protocol-receive":
        protocol = Protocol(Side.SERVER)
        with patch.object(secrets, "token_bytes", return_value=b"abcd"):
            wire = Frame(Opcode.TEXT, b"hi").serialize(mask=True)
        protocol.receive_data(wire)
        event = protocol.events_received()[0]
        return [event.opcode.name, event.data.decode(), event.fin, protocol.state.name]
    if name == "protocol-send":
        protocol = Protocol(Side.SERVER)
        protocol.send_binary(b"\x00\x01")
        return [item.hex() for item in protocol.data_to_send()]
    if name == "protocol-close":
        protocol = Protocol(Side.SERVER)
        protocol.send_close(1000, "bye")
        return [item.hex() for item in protocol.data_to_send()] + [
            protocol.state.name,
            protocol.close_expected(),
        ]
    if name.startswith("assembler-"):
        return asyncio.run(async_scenario(name))
    raise ValueError(f"unknown scenario: {name}")


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate-site", required=True)
    parser.add_argument("--scenario", required=True)
    args = parser.parse_args()
    if str(Path(args.candidate_site).resolve()) != "/tmp/candidate-site":
        raise ValueError("candidate site is unavailable")
    sys.path.insert(0, args.candidate_site)
    try:
        value = scenario(args.scenario)
        print(json.dumps({"ok": True, "value": value}, default=str, sort_keys=True))
    except BaseException as exc:
        print(
            json.dumps(
                {"ok": False, "exception_type": type_name(exc), "exception_message": str(exc)},
                sort_keys=True,
            )
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
