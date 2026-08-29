from __future__ import annotations

import json

from nl2repobench.verification.candidate_client import execute_script


SCENARIO = r'''
import hashlib
import io
import pickle
import tempfile
import sys
import rsa
import rsa.cli
import rsa.pkcs1
import rsa.util
from rsa import common, core, key, pem, pkcs1, pkcs1_v2, prime, randnum, transform

checks = {}
def test(name, fn):
    try:
        fn()
    except BaseException:
        checks[name] = False
    else:
        checks[name] = True

test("root-01", lambda: rsa.__version__ == "4.10-dev0")
test("root-02", lambda: rsa.__all__ == ["newkeys", "encrypt", "decrypt", "sign", "verify", "PublicKey", "PrivateKey", "DecryptionError", "VerificationError", "find_signature_hash", "compute_hash", "sign_hash"])
test("root-03", lambda: rsa.newkeys.__module__ == "rsa.key")
test("root-04", lambda: rsa.encrypt.__module__ == "rsa.pkcs1")
test("root-05", lambda: issubclass(rsa.DecryptionError, rsa.pkcs1.CryptoError) and issubclass(rsa.VerificationError, rsa.pkcs1.CryptoError))

test("transform-01", lambda: transform.bytes2int(b"\x80@\x0f") == 8405007)
test("transform-02", lambda: transform.bytes2int(b"") == 0)
test("transform-03", lambda: transform.int2bytes(0) == b"\x00")
test("transform-04", lambda: transform.int2bytes(255) == b"\xff")
test("transform-05", lambda: transform.int2bytes(255, 4) == b"\x00\x00\x00\xff")
test("transform-06", lambda: transform.int2bytes(1 << 16, 3) == b"\x01\x00\x00")
test("transform-07", lambda: isinstance(transform.bytes2int(bytearray(b"ab")), int))
def transform_negative():
    try: transform.int2bytes(-1)
    except ValueError: return
    raise AssertionError
test("transform-08", transform_negative)
def transform_type():
    try: transform.int2bytes("1")
    except TypeError: return
    raise AssertionError
test("transform-09", transform_type)
def transform_overflow():
    try: transform.int2bytes(256, 1)
    except OverflowError: return
    raise AssertionError
test("transform-10", transform_overflow)

test("common-01", lambda: common.bit_size(1023) == 10)
test("common-02", lambda: common.bit_size(1024) == 11)
test("common-03", lambda: common.bit_size(-1024) == 10)
test("common-04", lambda: common.byte_size(0) == 1)
test("common-05", lambda: common.byte_size((1 << 1024) - 1) == 128)
test("common-06", lambda: common.ceil_div(100, 7) == 15)
test("common-07", lambda: common.extended_gcd(99, 78)[0] == 3)
test("common-08", lambda: common.inverse(7, 4) == 3)
test("common-09", lambda: common.crt([2, 3], [3, 5]) == 8)
def common_bad_inverse():
    try: common.inverse(6, 9)
    except common.NotRelativePrimeError: return
    raise AssertionError
test("common-10", common_bad_inverse)

test("core-01", lambda: core.encrypt_int(42, 3, 101) == 48)
test("core-02", lambda: core.decrypt_int(42, 3, 101) == 46)
test("core-03", lambda: core.encrypt_int(42, 3, 101) == pow(42, 3, 101))
test("core-04", lambda: core.decrypt_int(42, 3, 101) == pow(42, 3, 101))
test("core-05", lambda: core.encrypt_int(0, 3, 101) == 0)
def core_negative():
    try: core.encrypt_int(-1, 3, 101)
    except ValueError: return
    raise AssertionError
test("core-06", core_negative)
def core_overflow():
    try: core.encrypt_int(101, 3, 101)
    except OverflowError: return
    raise AssertionError
test("core-07", core_overflow)
def core_type():
    try: core.encrypt_int("1", 3, 101)
    except TypeError: return
    raise AssertionError
test("core-08", core_type)
test("core-09", lambda: core.decrypt_int(0, 3, 101) == 0)
test("core-10", lambda: core.encrypt_int(100, 1, 101) == 100)

pub, priv = key.newkeys(512)
message = b"rsa verifier message"
test("key-01", lambda: isinstance(pub, key.PublicKey) and isinstance(priv, key.PrivateKey))
test("key-02", lambda: pub.n == priv.n and pub.e == priv.e)
test("key-03", lambda: pub["n"] == pub.n and pub["e"] == pub.e)
test("key-04", lambda: priv["n"] == priv.n and priv["d"] == priv.d)
test("key-05", lambda: pub == key.PublicKey(pub.n, pub.e))
test("key-06", lambda: hash(pub) == hash(key.PublicKey(pub.n, pub.e)))
test("key-07", lambda: "PublicKey" in repr(pub) and "PrivateKey" in repr(priv))
test("key-08", lambda: priv.exp1 == priv.d % (priv.p - 1))
test("key-09", lambda: priv.exp2 == priv.d % (priv.q - 1))
test("key-10", lambda: priv.coef == common.inverse(priv.q, priv.p))
test("key-11", lambda: key.PublicKey.load_pkcs1(pub.save_pkcs1("DER"), "DER") == pub)
test("key-12", lambda: key.PrivateKey.load_pkcs1(priv.save_pkcs1("DER"), "DER") == priv)
test("key-13", lambda: key.PublicKey.load_pkcs1(pub.save_pkcs1("PEM"), "PEM") == pub)
test("key-14", lambda: key.PrivateKey.load_pkcs1(priv.save_pkcs1("PEM"), "PEM") == priv)
test("key-15", lambda: pickle.loads(pickle.dumps(pub)) == pub)
test("key-16", lambda: pickle.loads(pickle.dumps(priv)) == priv)
test("key-17", lambda: isinstance(priv.rs, list) and priv.rs[:2] == [priv.p, priv.q])
test("key-18", lambda: isinstance(priv.ds, list) and isinstance(priv.ts, list))
test("key-19", lambda: key.PrivateKey.load_pkcs1(priv.save_pkcs1()).n == priv.n)
def key_bad_format():
    try: pub.save_pkcs1("UNKNOWN")
    except ValueError: return
    raise AssertionError
test("key-20", key_bad_format)

test("pkcs1-01", lambda: pkcs1.decrypt(pkcs1.encrypt(message, pub), priv) == message)
test("pkcs1-02", lambda: len(pkcs1.encrypt(message, pub)) == common.byte_size(pub.n))
test("pkcs1-03", lambda: pkcs1.encrypt(message, pub) != pkcs1.encrypt(message, pub))
test("pkcs1-04", lambda: pkcs1.compute_hash(message, "SHA-256") == hashlib.sha256(message).digest())
test("pkcs1-05", lambda: pkcs1.compute_hash(message, "SHA-1") == hashlib.sha1(message).digest())
test("pkcs1-06", lambda: pkcs1.compute_hash(message, "SHA3-256") == hashlib.sha3_256(message).digest())
signature = pkcs1.sign(message, priv, "SHA-256")
test("pkcs1-07", lambda: pkcs1.verify(message, signature, pub) == "SHA-256")
test("pkcs1-08", lambda: pkcs1.find_signature_hash(signature, pub) == "SHA-256")
test("pkcs1-09", lambda: pkcs1.sign_hash(hashlib.sha256(message).digest(), priv, "SHA-256") == signature)
def pkcs1_bad_verify():
    try: pkcs1.verify(b"other", signature, pub)
    except pkcs1.VerificationError: return
    raise AssertionError
test("pkcs1-10", pkcs1_bad_verify)
def pkcs1_bad_decrypt():
    try: pkcs1.decrypt(b"bad", priv)
    except pkcs1.DecryptionError: return
    raise AssertionError
test("pkcs1-11", pkcs1_bad_decrypt)
test("pkcs1-12", lambda: pkcs1.decrypt(pkcs1.encrypt(b"", pub), priv) == b"")
test("pkcs1-13", lambda: pkcs1.verify(message, pkcs1.sign(message, priv, "SHA-1"), pub) == "SHA-1")
test("pkcs1-14", lambda: pkcs1.verify(message, pkcs1.sign(message, priv, "SHA-224"), pub) == "SHA-224")
test("pkcs1-15", lambda: pkcs1.verify(message, pkcs1.sign(message, priv, "SHA3-256"), pub) == "SHA3-256")
test("pkcs1-16", lambda: list(pkcs1.yield_fixedblocks(io.BytesIO(b"abcde"), 2)) == [b"ab", b"cd", b"e"])
test("pkcs1-17", lambda: pkcs1_v2.mgf1(b"seed", 20) == hashlib.sha1(b"seed" + (0).to_bytes(4, "big")).digest())
test("pkcs1-18", lambda: len(pkcs1_v2.mgf1(b"seed", 37, "SHA-256")) == 37)
def pkcs1_bad_hash():
    try: pkcs1_v2.mgf1(b"x", 1, "NOPE")
    except ValueError: return
    raise AssertionError
test("pkcs1-19", pkcs1_bad_hash)
def pkcs1_bad_length():
    try: pkcs1_v2.mgf1(b"x", 2 ** 50)
    except OverflowError: return
    raise AssertionError
test("pkcs1-20", pkcs1_bad_length)

test("prime-01", lambda: prime.is_prime(2))
test("prime-02", lambda: prime.is_prime(41))
test("prime-03", lambda: not prime.is_prime(1))
test("prime-04", lambda: not prime.is_prime(42))
test("prime-05", lambda: not prime.is_prime(-7))
test("prime-06", lambda: prime.gcd(48, 180) == 12)
test("prime-07", lambda: prime.are_relatively_prime(2, 3) and not prime.are_relatively_prime(2, 4))
test("prime-08", lambda: prime.get_primality_testing_rounds(512) == 7)
test("prime-09", lambda: prime.get_primality_testing_rounds(1024) == 4)
test("prime-10", lambda: prime.get_primality_testing_rounds(1536) == 3)

test("pem-01", lambda: pem._markers("RSA PUBLIC KEY") == (b"-----BEGIN RSA PUBLIC KEY-----", b"-----END RSA PUBLIC KEY-----"))
test("pem-02", lambda: pem._markers(b"RSA PRIVATE KEY")[0].startswith(b"-----BEGIN"))
test("pem-03", lambda: pem.load_pem(pem.save_pem(b"abc", "TEST"), "TEST") == b"abc")
test("pem-04", lambda: pem.load_pem("-----BEGIN TEST-----\nYWJj\n-----END TEST-----\n", "TEST") == b"abc")
test("pem-05", lambda: key.PublicKey.load_pkcs1(pub.save_pkcs1(), "PEM") == pub)
test("pem-06", lambda: key.PrivateKey.load_pkcs1(priv.save_pkcs1(), "PEM") == priv)
test("pem-07", lambda: len(pem.save_pem(b"x" * 100, "TEST").splitlines()[1]) == 64)
test("pem-08", lambda: pem.save_pem(b"", "EMPTY").endswith(b"-----END EMPTY-----\n"))
def pem_missing():
    try: pem.load_pem(b"no marker", "TEST")
    except ValueError: return
    raise AssertionError
test("pem-09", pem_missing)
test("pem-10", lambda: pem.load_pem(b"prefix\n-----BEGIN TEST-----\nComment: x\nYWJj\n-----END TEST-----\nsuffix", "TEST") == b"abc")

test("cli-01", lambda: rsa.cli.keygen.__name__ == "keygen")
test("cli-02", lambda: isinstance(rsa.cli.encrypt, rsa.cli.EncryptOperation) and callable(rsa.cli.encrypt))
test("cli-03", lambda: isinstance(rsa.cli.decrypt, rsa.cli.DecryptOperation) and callable(rsa.cli.decrypt))
test("cli-04", lambda: isinstance(rsa.cli.sign, rsa.cli.SignOperation) and callable(rsa.cli.sign))
test("cli-05", lambda: rsa.util.private_to_public.__name__ == "private_to_public")

result = checks
'''


def main() -> None:
    result = execute_script(SCENARIO, timeout_sec=180.0)
    checks = result.value if result.ok and isinstance(result.value, dict) else {}
    groups = (("root", 5), ("transform", 10), ("common", 10), ("core", 10), ("key", 20), ("pkcs1", 20), ("prime", 10), ("pem", 10), ("cli", 5))
    leaves = []
    for prefix, count in groups:
        for index in range(1, count + 1):
            leaf = f"{prefix}-{index:02d}"
            leaves.append({"id": leaf, "status": "passed" if checks.get(leaf) is True else "failed"})
    print(json.dumps({"schema_version": "1.0", "leaves": leaves}, separators=(",", ":")))


if __name__ == "__main__":
    main()
