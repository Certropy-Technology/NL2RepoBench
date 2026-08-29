from __future__ import annotations

import json
import textwrap

from nl2repobench.verification.candidate_client import execute_script, metadata_requires


def _script(body: str) -> str:
    return textwrap.dedent(body).strip() + "\n"


def _probe(body: str, timeout_sec: float = 45.0) -> tuple[bool, str]:
    result = execute_script(_script(body), timeout_sec=timeout_sec)
    if result.ok and result.value is True:
        return True, ""
    if result.exception_type:
        return False, f"{result.exception_type}: {result.exception_message or ''}".strip()
    return False, f"scenario returned {result.value!r}"


def _metadata_probe() -> tuple[bool, str]:
    result = metadata_requires("pyOpenSSL")
    if not result.ok:
        return False, f"{result.exception_type}: {result.exception_message or ''}".strip()
    requirements = result.value or []
    valid = any(
        isinstance(item, str)
        and item.casefold().startswith("cryptography")
        and ">=49.0.0" in item
        and "<51" in item
        for item in requirements
    )
    return valid, f"Requires-Dist={requirements!r}" if not valid else ""


SCENARIOS: tuple[tuple[str, str | None], ...] = (
    (
        "root-exports",
        """
        import OpenSSL

        names = {
            "__author__", "__copyright__", "__email__", "__license__",
            "__summary__", "__title__", "__uri__", "__version__",
        }
        assert OpenSSL.__version__ == "26.4.0"
        assert {"SSL", "crypto", *names}.issubset(set(OpenSSL.__all__))
        assert all(isinstance(getattr(OpenSSL, name), str) for name in names)
        assert OpenSSL.SSL is not None and OpenSSL.crypto is not None
        result = True
        """,
    ),
    (
        "crypto-exports",
        """
        from OpenSSL import crypto

        required = {
            "FILETYPE_PEM", "FILETYPE_ASN1", "FILETYPE_TEXT", "TYPE_RSA",
            "TYPE_DSA", "Error", "PKey", "X509Name", "X509", "X509Store",
            "X509StoreContext", "X509StoreContextError", "X509StoreFlags",
            "load_certificate", "dump_certificate", "load_privatekey",
            "dump_privatekey", "load_publickey", "dump_publickey",
            "get_elliptic_curve", "get_elliptic_curves",
        }
        assert required.issubset(set(crypto.__all__))
        assert (crypto.FILETYPE_PEM, crypto.FILETYPE_ASN1, crypto.FILETYPE_TEXT) == (1, 2, 65535)
        assert all(isinstance(getattr(crypto, name), type) for name in ("PKey", "X509", "X509Name"))
        result = True
        """,
    ),
    ("metadata-requires", None),
    (
        "pkey-empty",
        """
        from OpenSSL import crypto

        key = crypto.PKey()
        assert key.type() == 0
        assert key.bits() == 0
        try:
            key.check()
        except TypeError:
            pass
        else:
            raise AssertionError("empty key check must fail")
        result = True
        """,
    ),
    (
        "pkey-rsa",
        """
        from OpenSSL import crypto

        key = crypto.PKey()
        assert key.generate_key(crypto.TYPE_RSA, 2048) is None
        assert key.type() == crypto.TYPE_RSA
        assert key.bits() == 2048
        assert key.check() is True
        result = True
        """,
    ),
    (
        "pkey-invalid",
        """
        from OpenSSL import crypto

        key = crypto.PKey()
        try:
            key.generate_key(999999, 1024)
        except crypto.Error:
            pass
        else:
            raise AssertionError("unsupported key type must raise Error")
        key.generate_key(crypto.TYPE_RSA, 2048)
        public = crypto.load_publickey(crypto.FILETYPE_ASN1, crypto.dump_publickey(crypto.FILETYPE_ASN1, key))
        try:
            public.check()
        except TypeError:
            pass
        else:
            raise AssertionError("public key check must raise TypeError")
        result = True
        """,
    ),
    (
        "pkey-cryptography-roundtrip",
        """
        from cryptography.hazmat.primitives.asymmetric import rsa
        from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
        from OpenSSL import crypto

        private = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        wrapped = crypto.PKey.from_cryptography_key(private)
        assert wrapped.bits() == 2048
        assert type(wrapped.to_cryptography_key()).__name__ == "RSAPrivateKey"
        public = private.public_key()
        public_wrapped = crypto.PKey.from_cryptography_key(public)
        assert public_wrapped.bits() == 2048
        assert type(public_wrapped.to_cryptography_key()).__name__ == "RSAPublicKey"
        assert public_wrapped.to_cryptography_key().public_bytes(Encoding.DER, PublicFormat.SubjectPublicKeyInfo) == public.public_bytes(Encoding.DER, PublicFormat.SubjectPublicKeyInfo)
        result = True
        """,
    ),
    (
        "x509-name",
        """
        from OpenSSL import crypto

        name = crypto.X509().get_subject()
        assert name.CN is None
        name.CN = "example.test"
        name.O = "Example Org"
        name.C = "US"
        assert name.commonName == "example.test"
        assert name.organizationName == "Example Org"
        assert name.countryName == "US"
        assert name.ST is None
        assert name.get_components() == [(b"CN", b"example.test"), (b"O", b"Example Org"), (b"C", b"US")]
        assert isinstance(name.hash(), int)
        assert name.der()
        assert repr(name).startswith("<X509Name object '")
        try:
            name.unknown_component = "x"
        except AttributeError:
            pass
        else:
            raise AssertionError("unknown X509Name attributes must fail")
        result = True
        """,
    ),
    (
        "x509-name-copy",
        """
        from OpenSSL import crypto

        original = crypto.X509().get_subject()
        original.CN = "before"
        original.O = "Org"
        copied = crypto.X509Name(original)
        assert copied == original
        copied.CN = "after"
        assert copied.CN == "after"
        assert original.CN == "before"
        assert original.O == copied.O == "Org"
        result = True
        """,
    ),
    (
        "x509-fields",
        """
        from OpenSSL import crypto

        key = crypto.PKey()
        key.generate_key(crypto.TYPE_RSA, 2048)
        cert = crypto.X509()
        assert cert.set_version(2) is None
        assert cert.get_version() == 2
        assert cert.set_serial_number(123456) is None
        assert cert.get_serial_number() == 123456
        subject = cert.get_subject()
        subject.CN = "fields.example"
        issuer = cert.get_issuer()
        issuer.O = "Issuer"
        assert cert.set_subject(subject) is None
        assert cert.set_issuer(issuer) is None
        assert cert.set_pubkey(key) is None
        assert cert.get_subject().CN == "fields.example"
        assert cert.get_issuer().O == "Issuer"
        assert cert.get_pubkey().bits() == 2048
        try:
            cert.set_pubkey(object())
        except TypeError:
            pass
        else:
            raise AssertionError("incompatible public key must fail")
        result = True
        """,
    ),
    (
        "x509-sign-serialize",
        """
        from OpenSSL import crypto

        key = crypto.PKey()
        key.generate_key(crypto.TYPE_RSA, 2048)
        cert = crypto.X509()
        cert.set_version(2)
        cert.set_serial_number(7)
        subject = cert.get_subject()
        subject.CN = "signed.example"
        cert.set_issuer(subject)
        cert.set_subject(subject)
        cert.set_pubkey(key)
        cert.gmtime_adj_notBefore(0)
        cert.gmtime_adj_notAfter(3600)
        assert cert.sign(key, "sha256") is None
        pem = crypto.dump_certificate(crypto.FILETYPE_PEM, cert)
        der = crypto.dump_certificate(crypto.FILETYPE_ASN1, cert)
        assert pem.startswith(b"-----BEGIN CERTIFICATE-----")
        assert der and len(der) < len(pem)
        loaded = crypto.load_certificate(crypto.FILETYPE_ASN1, der)
        assert crypto.dump_certificate(crypto.FILETYPE_ASN1, loaded) == der
        assert loaded.get_serial_number() == 7
        assert loaded.get_subject().CN == "signed.example"
        result = True
        """,
    ),
    (
        "key-serialize",
        """
        from OpenSSL import crypto

        key = crypto.PKey()
        key.generate_key(crypto.TYPE_RSA, 2048)
        private_pem = crypto.dump_privatekey(crypto.FILETYPE_PEM, key)
        private_der = crypto.dump_privatekey(crypto.FILETYPE_ASN1, key)
        public_pem = crypto.dump_publickey(crypto.FILETYPE_PEM, key)
        public_der = crypto.dump_publickey(crypto.FILETYPE_ASN1, key)
        assert private_pem.startswith(b"-----BEGIN") and public_pem.startswith(b"-----BEGIN")
        assert private_der and public_der
        assert crypto.load_privatekey(crypto.FILETYPE_ASN1, private_der).bits() == 2048
        loaded_public = crypto.load_publickey(crypto.FILETYPE_ASN1, public_der)
        assert loaded_public.bits() == 2048
        try:
            loaded_public.check()
        except TypeError:
            pass
        else:
            raise AssertionError("loaded public key must remain public-only")
        result = True
        """,
    ),
    (
        "invalid-loads",
        """
        from OpenSSL import crypto

        for loader in (
            lambda: crypto.load_certificate(crypto.FILETYPE_ASN1, b"not-a-cert"),
            lambda: crypto.load_privatekey(crypto.FILETYPE_ASN1, b"not-a-key"),
            lambda: crypto.load_publickey(crypto.FILETYPE_ASN1, b"not-a-key"),
        ):
            try:
                loader()
            except crypto.Error:
                pass
            else:
                raise AssertionError("invalid encoded data must raise crypto.Error")
        result = True
        """,
    ),
    (
        "x509-cryptography-bridge",
        """
        import datetime
        from cryptography import x509
        from cryptography.hazmat.primitives import hashes, serialization
        from cryptography.hazmat.primitives.asymmetric import rsa
        from cryptography.x509.oid import NameOID
        from OpenSSL import crypto

        key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "bridge.example")])
        cert = x509.CertificateBuilder().subject_name(name).issuer_name(name).public_key(key.public_key()).serial_number(19).not_valid_before(datetime.datetime(2020, 1, 1, tzinfo=datetime.timezone.utc)).not_valid_after(datetime.datetime(2099, 1, 1, tzinfo=datetime.timezone.utc)).sign(key, hashes.SHA256())
        wrapped = crypto.X509.from_cryptography(cert)
        assert wrapped.get_subject().CN == "bridge.example"
        assert wrapped.to_cryptography().public_bytes(serialization.Encoding.DER) == cert.public_bytes(serialization.Encoding.DER)
        result = True
        """,
    ),
    (
        "store-context",
        """
        from OpenSSL import crypto

        key = crypto.PKey()
        key.generate_key(crypto.TYPE_RSA, 2048)
        cert = crypto.X509()
        cert.set_version(2)
        cert.set_serial_number(31)
        subject = cert.get_subject()
        subject.CN = "trusted.example"
        cert.set_issuer(subject)
        cert.set_pubkey(key)
        cert.gmtime_adj_notBefore(0)
        cert.gmtime_adj_notAfter(3600)
        cert.sign(key, "sha256")
        store = crypto.X509Store()
        assert store.add_cert(cert) is None
        context = crypto.X509StoreContext(store, cert)
        assert context.verify_certificate() is None
        chain = context.get_verified_chain()
        assert len(chain) == 1 and chain[0].get_serial_number() == 31
        result = True
        """,
    ),
    (
        "elliptic-curves",
        """
        from OpenSSL import crypto

        curve = crypto.get_elliptic_curve("prime256v1")
        curves = crypto.get_elliptic_curves()
        assert curve.name == "prime256v1"
        assert repr(curve) == "<Curve 'prime256v1'>"
        assert curve in curves
        assert isinstance(curves, set) and len(curves) > 1
        result = True
        """,
    ),
    (
        "ssl-exports",
        """
        from OpenSSL import SSL

        names = {
            "TLS_METHOD", "TLS_CLIENT_METHOD", "TLS_SERVER_METHOD", "SSLv23_METHOD",
            "VERIFY_NONE", "VERIFY_PEER", "MODE_RELEASE_BUFFERS", "OP_NO_SSLv2",
            "SENT_SHUTDOWN", "OPENSSL_VERSION", "OPENSSL_VERSION_NUMBER",
            "SSLEAY_VERSION", "Error", "WantReadError", "WantWriteError",
            "ZeroReturnError", "SysCallError", "Session", "Context", "Connection",
            "OpenSSL_version",
        }
        assert names - {"OpenSSL_version"} <= set(SSL.__all__)
        assert hasattr(SSL, "OpenSSL_version")
        assert all(isinstance(getattr(SSL, name), int) for name in ("TLS_METHOD", "VERIFY_NONE", "VERIFY_PEER", "OPENSSL_VERSION_NUMBER"))
        assert isinstance(SSL.OpenSSL_version(SSL.SSLEAY_VERSION), bytes)
        assert isinstance(SSL.OPENSSL_VERSION, int)
        result = True
        """,
    ),
    (
        "ssl-context",
        """
        from OpenSSL import SSL

        context = SSL.Context(SSL.TLS_METHOD)
        assert context.get_verify_mode() == SSL.VERIFY_NONE
        assert context.set_verify(SSL.VERIFY_PEER, None) is None
        assert context.get_verify_mode() == SSL.VERIFY_PEER
        assert context.set_verify_depth(5) is None
        assert context.get_verify_depth() == 5
        marker = {"local": True}
        assert context.set_app_data(marker) is None
        assert context.get_app_data() == marker
        assert context.set_cipher_list(b"DEFAULT") is None
        assert context.set_min_proto_version(0) is None
        assert context.set_max_proto_version(0) is None
        result = True
        """,
    ),
    (
        "ssl-context-validation",
        """
        from OpenSSL import SSL

        try:
            SSL.Context("TLS")
        except TypeError:
            pass
        else:
            raise AssertionError("non-integer method must fail")
        try:
            SSL.Context(987654321)
        except ValueError:
            pass
        else:
            raise AssertionError("unknown method must fail")
        context = SSL.Context(SSL.TLS_METHOD)
        try:
            context.set_cipher_list(123)
        except TypeError:
            pass
        else:
            raise AssertionError("non-bytes cipher expression must fail")
        result = True
        """,
    ),
    (
        "ssl-cipher-connection",
        """
        from OpenSSL import SSL

        context = SSL.Context(SSL.TLS_METHOD)
        context.set_cipher_list(b"DEFAULT")
        connection = SSL.Connection(context, None)
        assert connection.get_context() is context
        assert connection.pending() == 0
        ciphers = connection.get_cipher_list()
        assert isinstance(ciphers, list) and ciphers
        connection.set_tlsext_host_name(b"example.test")
        assert connection.get_servername() == b"example.test"
        try:
            connection.set_tlsext_host_name(b"bad\\x00name")
        except TypeError:
            pass
        else:
            raise AssertionError("NUL hostname must fail")
        result = True
        """,
    ),
    (
        "ssl-memory-handshake",
        """
        from OpenSSL import SSL

        connection = SSL.Connection(SSL.Context(SSL.TLS_CLIENT_METHOD), None)
        connection.set_connect_state()
        try:
            connection.do_handshake()
        except SSL.WantReadError:
            pass
        else:
            raise AssertionError("memory handshake without peer must want read")
        assert connection.want_read() == 1
        result = True
        """,
    ),
    (
        "ssl-context-options",
        """
        from OpenSSL import SSL

        context = SSL.Context(SSL.TLS_METHOD)
        options = context.set_options(SSL.OP_NO_SSLv2)
        assert isinstance(options, int) and options != 0
        mode = context.set_mode(SSL.MODE_RELEASE_BUFFERS)
        assert isinstance(mode, int) and mode != 0
        result = True
        """,
    ),
    (
        "ssl-connection-options",
        """
        from OpenSSL import SSL

        connection = SSL.Connection(SSL.Context(SSL.TLS_METHOD), None)
        options = connection.set_options(SSL.OP_NO_SSLv2)
        assert isinstance(options, int) and options != 0
        assert connection.set_app_data("connection-data") is None
        assert connection.get_app_data() == "connection-data"
        assert connection.get_shutdown() == 0
        assert connection.set_shutdown(SSL.SENT_SHUTDOWN) is None
        assert connection.get_shutdown() & SSL.SENT_SHUTDOWN
        result = True
        """,
    ),
    (
        "rand-surface",
        """
        from OpenSSL import rand

        assert isinstance(rand.status(), int)
        assert rand.add(b"bounded-seed", 0) is None
        try:
            rand.add("not-bytes", 0)
        except TypeError:
            pass
        else:
            raise AssertionError("rand.add must reject text")
        try:
            rand.add(b"bytes", 0.5)
        except TypeError:
            pass
        else:
            raise AssertionError("rand.add must reject non-integer entropy")
        result = True
        """,
    ),
    (
        "debug-module",
        """
        import OpenSSL.debug as debug

        assert isinstance(debug._env_info, str)
        assert "pyOpenSSL: 26.4.0" in debug._env_info
        assert "cryptography:" in debug._env_info
        assert "Python version:" in debug._env_info
        result = True
        """,
    ),
)


def main() -> None:
    leaves: list[dict[str, object]] = []
    for leaf_id, body in SCENARIOS:
        if body is None:
            passed, detail = _metadata_probe()
        else:
            passed, detail = _probe(body)
        leaf: dict[str, object] = {"id": leaf_id, "status": "passed" if passed else "failed"}
        if detail:
            leaf["message"] = detail[:2000]
        leaves.append(leaf)
    print(json.dumps({"schema_version": "1.0", "leaves": leaves}, sort_keys=True))


if __name__ == "__main__":
    main()
