from __future__ import annotations

import argparse
import hashlib
import json
import os
import resource
import sys
from pathlib import Path
from typing import Any, Callable

RESULT_PREFIX = "NL2REPO_PYNACL_RESULT="


def _limits() -> None:
    resource.setrlimit(resource.RLIMIT_AS, (768 * 1024 * 1024,) * 2)
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
    resource.setrlimit(resource.RLIMIT_CPU, (10, 10))
    resource.setrlimit(resource.RLIMIT_FSIZE, (1024 * 1024,) * 2)
    resource.setrlimit(resource.RLIMIT_NOFILE, (64, 64))
    resource.setrlimit(resource.RLIMIT_NPROC, (32, 32))


def _hex(value: bytes) -> str:
    return value.hex()


def _error(action: Callable[[], Any]) -> dict[str, Any]:
    try:
        action()
    except BaseException as exc:
        return {
            "message": str(exc),
            "type": f"{type(exc).__module__}.{type(exc).__qualname__}",
        }
    return {"message": None, "type": None}


def _tamper(value: bytes) -> bytes:
    return value[:-1] + bytes([value[-1] ^ 1])


def exercise(name: str) -> Any:
    from nacl import encoding, exceptions, hash as nacl_hash, hashlib as nacl_hashlib
    from nacl import pwhash
    from nacl.public import Box, PrivateKey, PublicKey, SealedBox
    from nacl.secret import Aead, SecretBox
    from nacl.signing import SigningKey, VerifyKey
    from nacl.utils import EncryptedMessage, random, randombytes_deterministic

    key = bytes(range(32))
    nonce = bytes(range(24))
    other_key = bytes(range(32, 64))
    message = b"PyNaCl deterministic contract"

    if name == "metadata-imports":
        import nacl

        package = Path(nacl.__file__).resolve().parent
        return {
            "all": sorted(nacl.__all__),
            "py_typed": (package / "py.typed").is_file(),
            "version": nacl.__version__,
        }

    if name == "encoding-raw":
        return {
            "decode": _hex(encoding.RawEncoder.decode(b"raw\x00bytes")),
            "encode": _hex(encoding.RawEncoder.encode(b"raw\x00bytes")),
        }

    if name == "encoding-hex-base16":
        return {
            "base16": encoding.Base16Encoder.encode(b"Ab\x00").decode(),
            "base16_roundtrip": _hex(
                encoding.Base16Encoder.decode(encoding.Base16Encoder.encode(b"Ab\x00"))
            ),
            "hex": encoding.HexEncoder.encode(b"Ab\x00").decode(),
            "hex_roundtrip": _hex(
                encoding.HexEncoder.decode(encoding.HexEncoder.encode(b"Ab\x00"))
            ),
        }

    if name == "encoding-base32-base64":
        return {
            "base32": encoding.Base32Encoder.encode(b"encode me").decode(),
            "base32_roundtrip": _hex(
                encoding.Base32Encoder.decode(
                    encoding.Base32Encoder.encode(b"encode me")
                )
            ),
            "base64": encoding.Base64Encoder.encode(b"encode me").decode(),
            "base64_roundtrip": _hex(
                encoding.Base64Encoder.decode(
                    encoding.Base64Encoder.encode(b"encode me")
                )
            ),
        }

    if name == "encoding-urlsafe-errors":
        encoded = encoding.URLSafeBase64Encoder.encode(b"\xfb\xff\xef")
        return {
            "encoded": encoded.decode(),
            "invalid_hex": _error(lambda: encoding.HexEncoder.decode(b"xyz")),
            "roundtrip": _hex(encoding.URLSafeBase64Encoder.decode(encoded)),
        }

    if name == "utils-deterministic-random":
        seed = bytes(range(32))
        return {
            "hex": _hex(randombytes_deterministic(48, seed)),
            "hex_encoder": randombytes_deterministic(
                16, seed, encoding.HexEncoder
            ).decode(),
            "invalid_seed": _error(lambda: randombytes_deterministic(8, b"short")),
        }

    if name == "utils-random-shape":
        first = random(17)
        second = random(17)
        return {
            "different": first != second,
            "first_len": len(first),
            "second_len": len(second),
            "types": [type(first).__name__, type(second).__name__],
        }

    if name == "exceptions-hierarchy-ensure":
        return {
            "bad_signature_crypto": issubclass(
                exceptions.BadSignatureError, exceptions.CryptoError
            ),
            "ensure_failure": _error(
                lambda: exceptions.ensure(False, "nope", ValueError)
            ),
            "ensure_success": exceptions.ensure(True, "unused", ValueError),
            "value_error_builtin": issubclass(exceptions.ValueError, ValueError),
        }

    if name == "secretbox-constants-key":
        box = SecretBox(key)
        return {
            "bytes": _hex(bytes(box)),
            "key_size": SecretBox.KEY_SIZE,
            "macbytes": SecretBox.MACBYTES,
            "nonce_size": SecretBox.NONCE_SIZE,
            "str": str(box),
        }

    if name == "secretbox-key-validation":
        return {
            "hex_key": _hex(bytes(SecretBox(key.hex().encode(), encoding.HexEncoder))),
            "short": _error(lambda: SecretBox(b"x")),
            "wrong_type": _error(lambda: SecretBox("x")),
        }

    if name == "secretbox-deterministic":
        box = SecretBox(key)
        encrypted = box.encrypt(message, nonce)
        return {
            "ciphertext": _hex(encrypted.ciphertext),
            "combined": _hex(bytes(encrypted)),
            "decrypt_combined": box.decrypt(encrypted).decode(),
            "decrypt_detached": box.decrypt(encrypted.ciphertext, nonce).decode(),
            "nonce": _hex(encrypted.nonce),
            "type": type(encrypted).__name__,
        }

    if name == "secretbox-encoded":
        box = SecretBox(key)
        encrypted = box.encrypt(b"encoded", nonce, encoding.Base64Encoder)
        return {
            "combined": bytes(encrypted).decode(),
            "decrypt": box.decrypt(encrypted, encoder=encoding.Base64Encoder).decode(),
            "nonce": encrypted.nonce.decode(),
        }

    if name == "secretbox-random-nonce":
        encrypted = SecretBox(key).encrypt(b"random nonce")
        return {
            "ciphertext_len": len(encrypted.ciphertext),
            "combined_len": len(encrypted),
            "nonce_len": len(encrypted.nonce),
            "roundtrip": SecretBox(key).decrypt(encrypted).decode(),
        }

    if name == "secretbox-errors":
        box = SecretBox(key)
        encrypted = bytes(box.encrypt(message, nonce))
        return {
            "bad_nonce": _error(lambda: box.encrypt(message, b"short")),
            "tamper": _error(lambda: box.decrypt(_tamper(encrypted))),
            "wrong_key": _error(lambda: SecretBox(other_key).decrypt(encrypted)),
        }

    if name == "aead-constants-key":
        box = Aead(key)
        return {
            "bytes": _hex(bytes(box)),
            "key_size": Aead.KEY_SIZE,
            "macbytes": Aead.MACBYTES,
            "nonce_size": Aead.NONCE_SIZE,
            "str": str(box),
        }

    if name == "aead-deterministic":
        box = Aead(key)
        encrypted = box.encrypt(message, b"header", nonce)
        return {
            "ciphertext": _hex(encrypted.ciphertext),
            "combined": _hex(bytes(encrypted)),
            "decrypt_combined": box.decrypt(encrypted, b"header").decode(),
            "decrypt_detached": box.decrypt(
                encrypted.ciphertext, b"header", nonce
            ).decode(),
            "nonce": _hex(encrypted.nonce),
        }

    if name == "aead-encoded":
        box = Aead(key)
        encrypted = box.encrypt(b"encoded", b"aad", nonce, encoding.HexEncoder)
        return {
            "combined": bytes(encrypted).decode(),
            "decrypt": box.decrypt(
                encrypted, b"aad", encoder=encoding.HexEncoder
            ).decode(),
            "nonce": encrypted.nonce.decode(),
        }

    if name == "aead-random-nonce":
        encrypted = Aead(key).encrypt(b"random nonce", b"aad")
        return {
            "ciphertext_len": len(encrypted.ciphertext),
            "combined_len": len(encrypted),
            "nonce_len": len(encrypted.nonce),
            "roundtrip": Aead(key).decrypt(encrypted, b"aad").decode(),
        }

    if name == "aead-errors":
        box = Aead(key)
        encrypted = bytes(box.encrypt(message, b"right", nonce))
        return {
            "bad_aad": _error(lambda: box.decrypt(encrypted, b"wrong")),
            "bad_nonce": _error(lambda: box.encrypt(message, b"", b"short")),
            "short_key": _error(lambda: Aead(b"x")),
            "tamper": _error(lambda: box.decrypt(_tamper(encrypted), b"right")),
        }

    if name == "public-private-from-seed":
        private = PrivateKey.from_seed(key)
        return {
            "private": _hex(bytes(private)),
            "public": _hex(bytes(private.public_key)),
            "seed_size": PrivateKey.SEED_SIZE,
            "size": PrivateKey.SIZE,
        }

    if name == "public-key-encoding-equality":
        private = PrivateKey.from_seed(key)
        public = PublicKey(bytes(private.public_key).hex().encode(), encoding.HexEncoder)
        duplicate = PublicKey(bytes(public))
        return {
            "encoded": public.encode(encoding.Base64Encoder).decode(),
            "equal": public == duplicate,
            "hash_equal": hash(public) == hash(duplicate),
            "not_bytes": public != bytes(public),
            "size": PublicKey.SIZE,
        }

    if name == "public-key-validation":
        return {
            "private_seed_short": _error(lambda: PrivateKey.from_seed(b"short")),
            "private_short": _error(lambda: PrivateKey(b"short")),
            "public_short": _error(lambda: PublicKey(b"short")),
        }

    if name == "box-shared-key":
        alice = PrivateKey.from_seed(key)
        bob = PrivateKey.from_seed(other_key)
        first = Box(alice, bob.public_key)
        second = Box(bob, alice.public_key)
        return {
            "bytes": _hex(bytes(first)),
            "equal": first.shared_key() == second.shared_key(),
            "length": len(first.shared_key()),
        }

    if name == "box-deterministic":
        alice = PrivateKey.from_seed(key)
        bob = PrivateKey.from_seed(other_key)
        sender = Box(alice, bob.public_key)
        receiver = Box(bob, alice.public_key)
        encrypted = sender.encrypt(message, nonce)
        return {
            "ciphertext": _hex(encrypted.ciphertext),
            "combined": _hex(bytes(encrypted)),
            "decrypt_combined": receiver.decrypt(encrypted).decode(),
            "decrypt_detached": receiver.decrypt(
                encrypted.ciphertext, nonce
            ).decode(),
            "nonce": _hex(encrypted.nonce),
        }

    if name == "box-decode-encoded":
        alice = PrivateKey.from_seed(key)
        bob = PrivateKey.from_seed(other_key)
        original = Box(alice, bob.public_key)
        restored = Box.decode(original.encode(encoding.HexEncoder), encoding.HexEncoder)
        encrypted = original.encrypt(b"decoded", nonce, encoding.HexEncoder)
        return {
            "decrypt": restored.decrypt(
                encrypted, encoder=encoding.HexEncoder
            ).decode(),
            "equal_key": bytes(restored) == bytes(original),
            "str": str(original),
        }

    if name == "box-errors":
        alice = PrivateKey.from_seed(key)
        bob = PrivateKey.from_seed(other_key)
        box = Box(alice, bob.public_key)
        encrypted = bytes(box.encrypt(message, nonce))
        return {
            "bad_ctor": _error(lambda: Box(alice, b"not-key")),
            "bad_nonce": _error(lambda: box.encrypt(message, b"short")),
            "tamper": _error(lambda: Box(bob, alice.public_key).decrypt(_tamper(encrypted))),
        }

    if name == "sealedbox-roundtrip":
        recipient = PrivateKey.from_seed(key)
        sender = SealedBox(recipient.public_key)
        receiver = SealedBox(recipient)
        first = sender.encrypt(message)
        second = sender.encrypt(message)
        return {
            "bytes": _hex(bytes(sender)),
            "decrypt": receiver.decrypt(first).decode(),
            "different": first != second,
            "length": len(first),
        }

    if name == "sealedbox-encoded-errors":
        recipient = PrivateKey.from_seed(key)
        sender = SealedBox(recipient.public_key)
        receiver = SealedBox(recipient)
        encoded = sender.encrypt(b"sealed", encoding.Base64Encoder)
        return {
            "decrypt": receiver.decrypt(encoded, encoding.Base64Encoder).decode(),
            "public_decrypt": _error(lambda: sender.decrypt(encoded, encoding.Base64Encoder)),
            "tamper": _error(lambda: receiver.decrypt(_tamper(encoding.Base64Encoder.decode(encoded)))),
        }

    if name == "signing-seed-keys":
        signing = SigningKey(key)
        return {
            "seed": _hex(bytes(signing)),
            "str": str(signing),
            "verify": _hex(bytes(signing.verify_key)),
        }

    if name == "signing-encoding-equality":
        signing = SigningKey(key.hex().encode(), encoding.HexEncoder)
        duplicate = SigningKey(bytes(signing))
        verify = VerifyKey(
            bytes(signing.verify_key).hex().encode(), encoding.HexEncoder
        )
        return {
            "equal": signing == duplicate,
            "hash_equal": hash(signing) == hash(duplicate),
            "verify_equal": verify == signing.verify_key,
            "verify_hash_equal": hash(verify) == hash(signing.verify_key),
        }

    if name == "signing-combined":
        signing = SigningKey(key)
        signed = signing.sign(message)
        return {
            "combined": _hex(bytes(signed)),
            "message": _hex(signed.message),
            "signature": _hex(signed.signature),
            "type": type(signed).__name__,
            "verify": signing.verify_key.verify(signed).decode(),
        }

    if name == "signing-detached-encoded":
        signing = SigningKey(key)
        raw_signed = signing.sign(message)
        encoded = signing.sign(message, encoding.Base64Encoder)
        return {
            "message": encoded.message.decode(),
            "signature": encoded.signature.decode(),
            "verify_combined": signing.verify_key.verify(
                encoded, encoder=encoding.Base64Encoder
            ).decode(),
            "verify_detached": signing.verify_key.verify(
                raw_signed.message, raw_signed.signature
            ).decode(),
        }

    if name == "signing-errors":
        signing = SigningKey(key)
        signed = signing.sign(message)
        return {
            "bad_signature": _error(
                lambda: signing.verify_key.verify(message, _tamper(signed.signature))
            ),
            "short_seed": _error(lambda: SigningKey(b"short")),
            "short_signature": _error(
                lambda: signing.verify_key.verify(message, b"short")
            ),
            "short_verify_key": _error(lambda: VerifyKey(b"short")),
        }

    if name == "signing-curve-conversion":
        signing = SigningKey(key)
        private = signing.to_curve25519_private_key()
        public = signing.verify_key.to_curve25519_public_key()
        return {
            "private": _hex(bytes(private)),
            "public": _hex(bytes(public)),
            "public_matches": private.public_key == public,
        }

    if name == "hash-sha":
        return {
            "sha256": nacl_hash.sha256(message).decode(),
            "sha256_raw": _hex(nacl_hash.sha256(message, encoding.RawEncoder)),
            "sha512": nacl_hash.sha512(message).decode(),
        }

    if name == "hash-blake2b":
        return {
            "default": nacl_hash.blake2b(message).decode(),
            "keyed": nacl_hash.blake2b(
                message,
                digest_size=32,
                key=b"key",
                salt=b"salt",
                person=b"person",
            ).decode(),
            "raw_length": len(
                nacl_hash.blake2b(message, digest_size=17, encoder=encoding.RawEncoder)
            ),
        }

    if name == "hash-siphash":
        sip_key = bytes(range(nacl_hash.SIPHASH_KEYBYTES))
        return {
            "available_x": nacl_hash.SIPHASHX_AVAILABLE,
            "siphash24": nacl_hash.siphash24(message, sip_key).decode(),
            "siphash24_raw": _hex(
                nacl_hash.siphash24(message, sip_key, encoding.RawEncoder)
            ),
            "siphashx24": nacl_hash.siphashx24(
                message, bytes(range(nacl_hash.SIPHASHX_KEYBYTES))
            ).decode(),
        }

    if name == "hash-errors":
        return {
            "blake_size": _error(lambda: nacl_hash.blake2b(message, digest_size=1)),
            "sip_key": _error(lambda: nacl_hash.siphash24(message, b"short")),
        }

    if name == "hashlib-basic":
        value = nacl_hashlib.blake2b(message, digest_size=32)
        return {
            "block_size": value.block_size,
            "digest": _hex(value.digest()),
            "digest_size": value.digest_size,
            "hexdigest": value.hexdigest(),
            "name": value.name,
        }

    if name == "hashlib-incremental":
        value = nacl_hashlib.blake2b(digest_size=32, key=b"key")
        value.update(b"PyNaCl ")
        first = value.hexdigest()
        value.update(b"deterministic contract")
        return {
            "before": first,
            "final": value.hexdigest(),
            "stdlib_equal": value.digest()
            == hashlib.blake2b(message, digest_size=32, key=b"key").digest(),
        }

    if name == "hashlib-copy":
        value = nacl_hashlib.blake2b(b"prefix", digest_size=20)
        duplicate = value.copy()
        value.update(b"-one")
        duplicate.update(b"-two")
        return {
            "different": value.hexdigest() != duplicate.hexdigest(),
            "first": value.hexdigest(),
            "second": duplicate.hexdigest(),
        }

    if name == "hashlib-errors":
        value = nacl_hashlib.blake2b()
        return {
            "digest_size": _error(lambda: nacl_hashlib.blake2b(digest_size=1)),
            "pickle": _error(lambda: value.__reduce__()),
        }

    if name == "pwhash-constants":
        return {
            "alg": pwhash.argon2id.ALG,
            "bytes_min": pwhash.argon2id.BYTES_MIN,
            "memlimit_min": pwhash.argon2id.MEMLIMIT_MIN,
            "opslimit_min": pwhash.argon2id.OPSLIMIT_MIN,
            "passwd_min": pwhash.argon2id.PASSWD_MIN,
            "saltbytes": pwhash.argon2id.SALTBYTES,
            "strprefix": pwhash.argon2id.STRPREFIX.decode(),
        }

    if name == "pwhash-kdf":
        salt = bytes(range(pwhash.argon2id.SALTBYTES))
        derived = pwhash.argon2id.kdf(
            32,
            b"correct horse battery staple",
            salt,
            opslimit=pwhash.argon2id.OPSLIMIT_MIN,
            memlimit=pwhash.argon2id.MEMLIMIT_MIN,
        )
        return {"derived": _hex(derived), "length": len(derived)}

    if name == "pwhash-kdf-encoded":
        salt = bytes(range(pwhash.argon2id.SALTBYTES))
        derived = pwhash.argon2id.kdf(
            24,
            b"password",
            salt,
            opslimit=pwhash.argon2id.OPSLIMIT_MIN,
            memlimit=pwhash.argon2id.MEMLIMIT_MIN,
            encoder=encoding.HexEncoder,
        )
        return {"derived": derived.decode(), "length": len(derived)}

    if name == "pwhash-string-verify":
        encoded = pwhash.argon2id.str(
            b"password",
            opslimit=pwhash.argon2id.OPSLIMIT_MIN,
            memlimit=pwhash.argon2id.MEMLIMIT_MIN,
        )
        return {
            "generic_verify": pwhash.verify(encoded, b"password"),
            "length": len(encoded),
            "prefix": encoded.startswith(pwhash.argon2id.STRPREFIX),
            "verify": pwhash.argon2id.verify(encoded, b"password"),
            "wrong": _error(lambda: pwhash.argon2id.verify(encoded, b"wrong")),
        }

    if name == "pwhash-errors":
        salt = bytes(range(pwhash.argon2id.SALTBYTES))
        return {
            "bad_prefix": _error(lambda: pwhash.verify(b"not-a-hash", b"password")),
            "short_output": _error(
                lambda: pwhash.argon2id.kdf(
                    1,
                    b"password",
                    salt,
                    opslimit=pwhash.argon2id.OPSLIMIT_MIN,
                    memlimit=pwhash.argon2id.MEMLIMIT_MIN,
                )
            ),
            "short_salt": _error(
                lambda: pwhash.argon2id.kdf(
                    32,
                    b"password",
                    b"short",
                    opslimit=pwhash.argon2id.OPSLIMIT_MIN,
                    memlimit=pwhash.argon2id.MEMLIMIT_MIN,
                )
            ),
        }

    if name == "generated-key-shapes":
        private = PrivateKey.generate()
        signing = SigningKey.generate()
        return {
            "private_len": len(bytes(private)),
            "public_len": len(bytes(private.public_key)),
            "signing_len": len(bytes(signing)),
            "verify_len": len(bytes(signing.verify_key)),
        }

    if name == "encrypted-message-bytes":
        encrypted = SecretBox(key).encrypt(message, nonce)
        return {
            "bytes_subclass": isinstance(encrypted, bytes),
            "ciphertext_suffix": bytes(encrypted).endswith(encrypted.ciphertext),
            "nonce_prefix": bytes(encrypted).startswith(encrypted.nonce),
            "type": EncryptedMessage.__name__,
        }

    raise ValueError(f"unknown scenario: {name}")


SCENARIOS = (
    "metadata-imports",
    "encoding-raw",
    "encoding-hex-base16",
    "encoding-base32-base64",
    "encoding-urlsafe-errors",
    "utils-deterministic-random",
    "utils-random-shape",
    "exceptions-hierarchy-ensure",
    "secretbox-constants-key",
    "secretbox-key-validation",
    "secretbox-deterministic",
    "secretbox-encoded",
    "secretbox-random-nonce",
    "secretbox-errors",
    "aead-constants-key",
    "aead-deterministic",
    "aead-encoded",
    "aead-random-nonce",
    "aead-errors",
    "public-private-from-seed",
    "public-key-encoding-equality",
    "public-key-validation",
    "box-shared-key",
    "box-deterministic",
    "box-decode-encoded",
    "box-errors",
    "sealedbox-roundtrip",
    "sealedbox-encoded-errors",
    "signing-seed-keys",
    "signing-encoding-equality",
    "signing-combined",
    "signing-detached-encoded",
    "signing-errors",
    "signing-curve-conversion",
    "hash-sha",
    "hash-blake2b",
    "hash-siphash",
    "hash-errors",
    "hashlib-basic",
    "hashlib-incremental",
    "hashlib-copy",
    "hashlib-errors",
    "pwhash-constants",
    "pwhash-kdf",
    "pwhash-kdf-encoded",
    "pwhash-string-verify",
    "pwhash-errors",
    "generated-key-shapes",
    "encrypted-message-bytes",
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate-site", required=True)
    parser.add_argument("--scenario")
    parser.add_argument("--all", action="store_true")
    args = parser.parse_args()
    _limits()
    candidate_site = Path(args.candidate_site).resolve()
    if candidate_site != Path("/tmp/candidate-site") and os.environ.get(
        "NL2REPO_AUTHORING_REFERENCE"
    ) != "1":
        raise ValueError("candidate site is unavailable")
    sys.path.insert(0, str(candidate_site))
    sys.path.insert(1, "/opt/candidate-dependencies/site")
    try:
        if args.all:
            value = {scenario: exercise(scenario) for scenario in SCENARIOS}
        elif args.scenario in SCENARIOS:
            value = exercise(args.scenario)
        else:
            raise ValueError("a known scenario is required")
        payload: dict[str, Any] = {"ok": True, "value": value}
    except BaseException as exc:
        payload = {
            "exception_message": str(exc),
            "exception_type": f"{type(exc).__module__}.{type(exc).__qualname__}",
            "ok": False,
        }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    os.write(1, RESULT_PREFIX.encode() + encoded + b"\n")


if __name__ == "__main__":
    main()
