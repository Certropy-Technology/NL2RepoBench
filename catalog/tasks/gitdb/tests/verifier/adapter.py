#!/usr/bin/env python3
"""Child-side scenarios for the documented deterministic GitDB API."""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import tempfile
import traceback
import zlib
import sys
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
        raise AssertionError(f"{message}: expected {exc_type.__name__}, got {type(exc).__name__}") from exc
    raise AssertionError(f"{message}: expected {exc_type.__name__}")


def make_stream(type_: bytes = b"blob", payload: bytes = b"hello"):
    from gitdb import IStream

    return IStream(type_, len(payload), io.BytesIO(payload))


def api_surface() -> None:
    import gitdb
    from gitdb.base import IStream, OInfo, OStream
    from gitdb.db.git import GitDB
    from gitdb.db.loose import LooseObjectDB
    from gitdb.db.mem import MemoryDB
    from gitdb.stream import Sha1Writer

    required = {
        "OInfo": OInfo,
        "OStream": OStream,
        "IStream": IStream,
        "MemoryDB": MemoryDB,
        "LooseObjectDB": LooseObjectDB,
        "GitDB": GitDB,
        "Sha1Writer": Sha1Writer,
    }
    check(all(getattr(gitdb, name) is value for name, value in required.items()), "root re-export identity changed")
    check(isinstance(gitdb.__version__, str) and gitdb.__version__, "version metadata is absent")
    check(gitdb.fun.type_to_type_id_map[b"blob"] == 3, "type map missing blob")
    check(gitdb.fun.type_id_to_type_map[3] == b"blob", "inverse type map missing blob")


def object_records() -> None:
    from gitdb.base import ODeltaPackInfo, ODeltaPackStream, OInfo, OPackInfo, OPackStream, OStream

    sha = b"x" * 20
    info = OInfo(sha, b"blob", 3)
    check(tuple(info) == (sha, b"blob", 3), "OInfo tuple contents failed")
    check(info.binsha == sha and info.hexsha == b"78" * 20 and info.type_id == 3 and info.size == 3, "OInfo properties failed")
    pack = OPackInfo(17, 3, 4)
    delta = ODeltaPackInfo(18, 6, 5, 9)
    check(pack.pack_offset == 17 and pack.type == b"blob" and pack.type_id == 3, "OPackInfo properties failed")
    check(delta.delta_info == 9 and delta.type == "OFS_DELTA", "ODeltaPackInfo properties failed")
    check(OStream(sha, b"blob", 3, io.BytesIO(b"abc")).read() == b"abc", "OStream read failed")
    check(OPackStream(1, 3, 3, io.BytesIO(b"abc")).read(2) == b"ab", "OPackStream read failed")
    check(ODeltaPackStream(1, 6, 3, 2, io.BytesIO(b"abc")).read() == b"abc", "ODeltaPackStream read failed")


def istream_mutation() -> None:
    from gitdb import IStream

    stream = IStream(b"tree", 4, io.BytesIO(b"data"))
    check(stream.binsha is None and stream.type == b"tree" and stream.size == 4, "IStream initial fields failed")
    stream.binsha = b"a" * 20
    stream.type = b"blob"
    stream.size = 3
    stream.error = ValueError("marker")
    check(stream.hexsha == b"61" * 20 and stream.read() == b"data", "IStream read/hex failed")
    check(stream.type == b"blob" and stream.size == 3 and isinstance(stream.error, ValueError), "IStream mutation failed")


def sha_writers() -> None:
    from gitdb.stream import FlexibleSha1Writer, NullStream, Sha1Writer, ZippedStoreShaWriter

    writer = Sha1Writer()
    check(writer.write(b"abc") == 3, "Sha1Writer byte count failed")
    check(writer.sha() == hashlib.sha1(b"abc").digest(), "Sha1Writer digest failed")
    check(writer.sha(as_hex=True) == hashlib.sha1(b"abc").hexdigest(), "Sha1Writer hex digest failed")
    forwarded: list[bytes] = []
    flexible = FlexibleSha1Writer(forwarded.append)
    flexible.write(b"data")
    check(forwarded == [b"data"] and flexible.sha() == hashlib.sha1(b"data").digest(), "FlexibleSha1Writer failed")
    zipped = ZippedStoreShaWriter()
    zipped.write(b"repeat" * 20)
    zipped.close()
    zipped.seek(0)
    check(zlib.decompress(zipped.getvalue()) == b"repeat" * 20, "ZippedStoreShaWriter compression failed")
    check(NullStream().write(b"x") == 1, "NullStream write failed")


def object_helpers() -> None:
    from gitdb.fun import loose_object_header, loose_object_header_info, stream_copy, write_object
    from gitdb.util import bin_to_hex, hex_to_bin

    payload = b"payload"
    header = loose_object_header(b"blob", len(payload))
    check(
        header == b"blob 7\0" and loose_object_header_info(zlib.compress(header + payload)) == (b"blob", 7),
        "header helpers failed",
    )
    output = io.BytesIO()
    write_object(b"blob", len(payload), io.BytesIO(payload).read, output.write)
    check(output.getvalue() == header + payload, "write_object failed")
    copied = io.BytesIO()
    check(stream_copy(io.BytesIO(b"abcdef").read, copied.write, 4, 2) == 4, "stream_copy count failed")
    check(copied.getvalue() == b"abcd", "stream_copy bytes failed")
    digest = hashlib.sha1(b"value").digest()
    check(hex_to_bin(bin_to_hex(digest)) == digest, "hex conversion round trip failed")


def memory_store_read() -> None:
    from gitdb import MemoryDB

    db = MemoryDB()
    stored = db.store(make_stream(b"blob", b"hello"))
    expected = hashlib.sha1(b"blob 5\0hello").digest()
    check(stored.binsha == expected and db.has_object(expected), "MemoryDB store SHA failed")
    info = db.info(expected)
    check(info.binsha == expected and info.type == b"blob" and info.size == 5, "MemoryDB info failed")
    check(db.stream(expected).read() == b"hello", "MemoryDB stream content failed")
    check(db.stream(expected).read(2) == b"he" and db.stream(expected).read() == b"hello", "MemoryDB streams do not rewind")


def memory_idempotency() -> None:
    from gitdb import MemoryDB

    db = MemoryDB()
    first = db.store(make_stream(b"commit", b"same"))
    second = db.store(make_stream(b"commit", b"same"))
    check(first.binsha == second.binsha and db.size() == 1, "MemoryDB duplicate storage changed object set")
    check(tuple(db.sha_iter()) == (first.binsha,), "MemoryDB SHA iteration failed")


def memory_stream_copy() -> None:
    from gitdb import LooseObjectDB, MemoryDB

    with tempfile.TemporaryDirectory(prefix="gitdb-memory-copy-") as temporary:
        source, target = MemoryDB(), LooseObjectDB(temporary)
        first = source.store(make_stream(b"blob", b"a"))
        second = source.store(make_stream(b"tree", b"b"))
        check(source.stream_copy((first.binsha, second.binsha), target) == 2, "MemoryDB first copy failed")
        check(target.size() == 2 and target.stream(second.binsha).read() == b"b", "MemoryDB copied data failed")
        check(source.stream_copy((first.binsha, second.binsha), target) == 0, "MemoryDB duplicate copy was not skipped")


def memory_errors() -> None:
    from gitdb import MemoryDB
    from gitdb.exc import BadObject, UnsupportedOperation

    db = MemoryDB()
    expect(BadObject, lambda: db.stream(b"z" * 20), "unknown MemoryDB object accepted")
    expect(UnsupportedOperation, lambda: db.set_ostream(None), "MemoryDB accepted output stream")


def loose_store_layout() -> None:
    from gitdb import LooseObjectDB

    with tempfile.TemporaryDirectory(prefix="gitdb-loose-") as temporary:
        root = Path(temporary)
        db = LooseObjectDB(root)
        stored = db.store(make_stream(b"blob", b"local"))
        relative = db.object_path(stored.hexsha)
        path = root / relative.decode()
        check(relative == stored.hexsha[:2] + b"/" + stored.hexsha[2:], "loose object relative path failed")
        check(path.is_file() and zlib.decompress(path.read_bytes()) == b"blob 5\0local", "loose bytes failed")
        check(db.readable_db_object_path(stored.hexsha) == str(path), "readable loose path failed")


def loose_reopen_read() -> None:
    from gitdb import LooseObjectDB

    with tempfile.TemporaryDirectory(prefix="gitdb-loose-") as temporary:
        first = LooseObjectDB(temporary)
        stored = first.store(make_stream(b"tree", b"reopen"))
        second = LooseObjectDB(temporary)
        check(second.has_object(stored.binsha), "reopened loose DB missed object")
        check(second.info(stored.binsha).type == b"tree" and second.info(stored.binsha).size == 6, "reopened loose info failed")
        check(second.stream(stored.binsha).read() == b"reopen", "reopened loose stream failed")


def loose_partial_lookup() -> None:
    from gitdb import LooseObjectDB

    with tempfile.TemporaryDirectory(prefix="gitdb-loose-") as temporary:
        db = LooseObjectDB(temporary)
        one = db.store(make_stream(b"blob", b"one"))
        two = db.store(make_stream(b"blob", b"two"))
        ordered = tuple(db.sha_iter())
        check(set(ordered) == {one.binsha, two.binsha} and len(ordered) == 2, "loose SHA iteration failed")
        prefix = one.hexsha[:12]
        check(db.partial_to_complete_sha_hex(prefix) == one.binsha, "unique byte prefix lookup failed")
        check(db.partial_to_complete_sha_hex(prefix.decode()) == one.binsha, "unique text prefix lookup failed")


def loose_errors() -> None:
    from gitdb import LooseObjectDB
    from gitdb.exc import AmbiguousObjectName, BadObject

    with tempfile.TemporaryDirectory(prefix="gitdb-loose-") as temporary:
        db = LooseObjectDB(temporary)
        first = db.store(make_stream(b"blob", b"first"))
        db.store(make_stream(b"blob", b"second"))
        expect(BadObject, lambda: db.readable_db_object_path(b"0" * 40), "missing loose path accepted")
        expect(BadObject, lambda: db.partial_to_complete_sha_hex(b"dead"), "missing prefix accepted")
        # Two first-nibble matches are not guaranteed; locate an actual ambiguous prefix deterministically.
        prefixes = {}
        for index in range(512):
            item = db.store(make_stream(b"blob", f"item-{index}".encode()))
            prefixes.setdefault(item.hexsha[:1], []).append(item)
        ambiguous = next(prefix for prefix, values in sorted(prefixes.items()) if len(values) > 1)
        expect(AmbiguousObjectName, lambda: db.partial_to_complete_sha_hex(ambiguous), "ambiguous prefix accepted")
        check(db.has_object(first.binsha), "existing object disappeared during ambiguity probe")


def gitdb_composition() -> None:
    from gitdb import GitDB
    from gitdb.exc import InvalidDBRoot

    with tempfile.TemporaryDirectory(prefix="gitdb-git-") as temporary:
        root = Path(temporary) / "objects"
        expect(InvalidDBRoot, lambda: GitDB(root).size(), "missing GitDB root accepted")
        root.mkdir()
        db = GitDB(root)
        stored = db.store(make_stream(b"blob", b"gitdb"))
        check(db.size() == 1 and db.has_object(stored.binsha), "GitDB store/delegation failed")
        check(db.stream(stored.binsha).read() == b"gitdb", "GitDB stream failed")
        check((root / stored.hexsha[:2].decode() / stored.hexsha[2:].decode()).is_file(), "GitDB did not use loose layout")


def cross_database_projection() -> None:
    from gitdb import LooseObjectDB, MemoryDB

    with tempfile.TemporaryDirectory(prefix="gitdb-cross-") as temporary:
        memory = MemoryDB()
        loose = LooseObjectDB(temporary)
        source = memory.store(make_stream(b"tag", b"copy"))
        check(memory.stream_copy((source.binsha,), loose) == 1, "memory-to-loose copy failed")
        check(loose.stream(source.binsha).read() == b"copy", "cross-database bytes failed")
        check(memory.stream_copy((source.binsha,), loose) == 0, "cross-database duplicate was not skipped")


def deterministic_projection() -> None:
    from gitdb import MemoryDB

    def snapshot():
        db = MemoryDB()
        a = db.store(make_stream(b"blob", b"alpha"))
        b = db.store(make_stream(b"tree", b"beta"))
        return {"sha": [a.hexsha.decode(), b.hexsha.decode()], "objects": sorted(item.hex() for item in db.sha_iter()), "contents": [db.stream(a.binsha).read().decode(), db.stream(b.binsha).read().decode()]}

    check(snapshot() == snapshot(), "fresh deterministic projection changed")


SCENARIOS = {
    "api_surface": api_surface,
    "object_records": object_records,
    "istream_mutation": istream_mutation,
    "sha_writers": sha_writers,
    "object_helpers": object_helpers,
    "memory_store_read": memory_store_read,
    "memory_idempotency": memory_idempotency,
    "memory_stream_copy": memory_stream_copy,
    "memory_errors": memory_errors,
    "loose_store_layout": loose_store_layout,
    "loose_reopen_read": loose_reopen_read,
    "loose_partial_lookup": loose_partial_lookup,
    "loose_errors": loose_errors,
    "gitdb_composition": gitdb_composition,
    "cross_database_projection": cross_database_projection,
    "deterministic_projection": deterministic_projection,
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scenario", choices=sorted(SCENARIOS), required=True)
    parser.add_argument("--candidate-site", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    dependency_site = os.environ.get("NL2REPO_CANDIDATE_DEPENDENCIES", "")
    if dependency_site:
        sys.path.insert(0, dependency_site)
    sys.path.insert(0, args.candidate_site)
    verdict = {"scenario": args.scenario, "status": "failed"}
    try:
        SCENARIOS[args.scenario]()
    except BaseException:
        verdict["message"] = traceback.format_exc(limit=12)[-2400:]
    else:
        verdict["status"] = "passed"
    args.output.write_text(json.dumps(verdict, sort_keys=True), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
