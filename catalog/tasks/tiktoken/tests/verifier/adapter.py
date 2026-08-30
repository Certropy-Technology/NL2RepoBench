from __future__ import annotations

import argparse
import base64
import json
import os
import pickle
import tempfile
from pathlib import Path
from typing import Any


def exc_name(exc: BaseException) -> str:
    return f"{type(exc).__module__}.{type(exc).__qualname__}"


def fixture() -> Any:
    import tiktoken

    ranks = {bytes([i]): i for i in range(256)}
    ranks.update({b"he": 256, b"ll": 257, b"hell": 258, b"hello": 259})
    return tiktoken.Encoding(
        "fixture",
        pat_str=r"[A-Za-z]+|\s+|[^A-Za-z\s]+",
        mergeable_ranks=ranks,
        special_tokens={"<|end|>": 300},
    )


def run_scenario(name: str) -> Any:
    import tiktoken
    from tiktoken import load

    if name == "exports":
        return {
            "encoding": tiktoken.Encoding.__name__,
            "model": callable(tiktoken.encoding_for_model),
            "get": callable(tiktoken.get_encoding),
            "names": callable(tiktoken.list_encoding_names),
        }
    if name == "encoding_repr":
        enc = fixture()
        return {"repr": repr(enc), "max": enc.max_token_value, "n_vocab": enc.n_vocab}
    if name == "bpe_merge":
        enc = fixture()
        tokens = enc.encode("hello", disallowed_special=())
        return {"tokens": tokens, "text": enc.decode(tokens), "bytes": enc.decode_bytes(tokens).decode()}
    if name == "special_guard":
        enc = fixture()
        try:
            enc.encode("<|end|>")
        except Exception as exc:
            blocked = exc_name(exc)
        else:
            blocked = None
        return {"blocked": blocked, "allowed": enc.encode("<|end|>", allowed_special="all")}
    if name == "single_token":
        enc = fixture()
        try:
            enc.encode_single_token("missing")
        except Exception as exc:
            missing = exc_name(exc)
        else:
            missing = None
        return {"known": enc.encode_single_token("hello"), "missing": missing}
    if name == "decode_errors":
        enc = tiktoken.Encoding("bytes", pat_str=r".+", mergeable_ranks={bytes([i]): i for i in range(256)}, special_tokens={})
        replacement = enc.decode([255])
        try:
            enc.decode([255], errors="strict")
        except Exception as exc:
            strict = exc_name(exc)
        else:
            strict = None
        return {"replacement": replacement, "strict": strict}
    if name == "offsets":
        enc = fixture()
        tokens = enc.encode("hello world", disallowed_special=())
        text, offsets = enc.decode_with_offsets(tokens)
        return {"tokens": tokens, "text": text, "offsets": offsets}
    if name == "batch_order":
        enc = fixture()
        values = ["hello", "world", "hello world"]
        encoded = enc.encode_batch(values, num_threads=2)
        return {"encoded": encoded, "decoded": enc.decode_batch(encoded, num_threads=2)}
    if name == "surrogate_replace":
        enc = fixture()
        return enc.encode("\ud83d") == enc.encode("�")
    if name == "pickle":
        enc = fixture()
        restored = pickle.loads(pickle.dumps(enc))
        return {"repr": repr(restored), "same": restored.decode(restored.encode("hello", disallowed_special=())) == "hello"}
    if name == "explicit_vocab":
        try:
            tiktoken.Encoding("bad", pat_str=r".+", mergeable_ranks={b"a": 0}, special_tokens={b"bad": 1}, explicit_n_vocab=3)  # type: ignore[arg-type]
        except Exception as exc:
            return exc_name(exc)
        return None
    if name == "registry_names":
        return tiktoken.list_encoding_names()
    if name == "model_exact":
        from tiktoken.model import encoding_name_for_model

        return encoding_name_for_model("gpt-4")
    if name == "model_prefix":
        from tiktoken.model import encoding_name_for_model

        return encoding_name_for_model("gpt-4-2024-06-01")
    if name == "model_unknown":
        from tiktoken.model import encoding_name_for_model

        try:
            encoding_name_for_model("not-a-model")
        except Exception as exc:
            return exc_name(exc)
        return None
    if name == "load_bpe":
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "vocab.tiktoken"
            path.write_bytes(b"YQ== 0\nYg== 1\n")
            return {key.decode(): value for key, value in load.load_tiktoken_bpe(str(path)).items()}
    if name == "load_hash_mismatch":
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "vocab.tiktoken"
            path.write_bytes(b"YQ== 0\n")
            try:
                load.load_tiktoken_bpe(str(path), expected_hash="0" * 64)
            except Exception as exc:
                return exc_name(exc)
            return None
    if name == "dump_bpe":
        import sys
        import types

        class BlobFile:
            def __init__(self, path: str, mode: str):
                self.handle = open(path, mode)

            def __enter__(self):
                return self.handle

            def __exit__(self, *args: Any) -> None:
                self.handle.close()

        fake_blobfile = types.ModuleType("blobfile")
        fake_blobfile.BlobFile = BlobFile  # type: ignore[attr-defined]
        sys.modules["blobfile"] = fake_blobfile
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "dump.tiktoken"
            load.dump_tiktoken_bpe({b"b": 2, b"a": 0, b"ab": 1}, str(path))
            return path.read_bytes().decode()
    if name == "data_gym_local":
        rank_to_byte = [b for b in range(256) if chr(b).isprintable() and chr(b) != " "]
        mapping = {chr(b): b for b in rank_to_byte}
        n = 0
        for b in range(256):
            if b not in rank_to_byte:
                rank_to_byte.append(b)
                mapping[chr(256 + n)] = b
                n += 1
        encoded = {key: rank for rank, key in enumerate(mapping)}
        with tempfile.TemporaryDirectory() as directory:
            vocab = Path(directory) / "vocab.bpe"
            encoder = Path(directory) / "encoder.json"
            vocab.write_text("#version: 0.2\n", encoding="utf-8")
            encoder.write_text(json.dumps(encoded), encoding="utf-8")
            result = load.data_gym_to_mergeable_bpe_ranks(str(vocab), str(encoder))
            return {"size": len(result), "zero": result[b"\x00"], "space": result[b" "]}
    if name == "educational_bpe":
        from tiktoken._educational import bpe_encode

        ranks = {bytes([i]): i for i in range(256)}
        ranks.update({b"ab": 256, b"abc": 257})
        return bpe_encode(ranks, b"abc", visualise=None)
    if name == "educational_train":
        from tiktoken._educational import bpe_train

        ranks = bpe_train("abababab", 257, r".+", visualise=None)
        return {"size": len(ranks), "new": ranks[b"ab"]}
    if name == "educational_wrapper":
        from tiktoken._educational import SimpleBytePairEncoding

        ranks = {bytes([i]): i for i in range(256)}
        ranks.update({b"ab": 256})
        enc = SimpleBytePairEncoding(pat_str=r".+", mergeable_ranks=ranks)
        return {"tokens": enc.encode("ab", visualise=None), "text": enc.decode([256])}
    if name == "unknown_encoding":
        try:
            tiktoken.get_encoding("does-not-exist")
        except Exception as exc:
            return exc_name(exc)
        return None
    if name == "offline_local_loader":
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "data"
            path.write_bytes(b"offline")
            return load.read_file(str(path)).decode()
    raise ValueError(f"unknown scenario {name}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate-site", required=True)
    parser.add_argument("--dependency-site", required=True)
    parser.add_argument("--scenario", required=True)
    args = parser.parse_args()
    if os.path.realpath(args.candidate_site) != "/tmp/candidate-site":
        raise ValueError("candidate site is unavailable")
    import sys

    sys.path.insert(0, args.candidate_site)
    sys.path.insert(1, args.dependency_site)
    try:
        value = run_scenario(args.scenario)
        result = {"ok": True, "value": value}
    except BaseException as exc:
        result = {"ok": False, "exception_type": exc_name(exc), "exception_message": str(exc)}
    print(json.dumps(result, ensure_ascii=False, sort_keys=True, default=repr))


if __name__ == "__main__":
    main()
