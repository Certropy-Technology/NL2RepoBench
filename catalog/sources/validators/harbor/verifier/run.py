"""Private deterministic scenarios for the validators public contract.

Each scenario runs as the unprivileged candidate in an isolated subprocess and
must be derivable from the public instruction. Invalid inputs are checked via
truthiness (bool(ValidationError) is False per the validators contract).
"""

from __future__ import annotations

import json

from nl2repobench.verification.candidate_client import execute_script


def _run(source: str, expected: object) -> tuple[str, object]:
    observed = execute_script(source, timeout_sec=20.0)
    actual: dict[str, object] = {"ok": observed.ok, "value": observed.value}
    if not observed.ok:
        actual["exception_type"] = observed.exception_type
        actual["exception_message"] = observed.exception_message
    return "passed" if actual == expected else "failed", actual


CASES: list[tuple[str, str, object]] = [
    (
        'email_valid_basic',
        "from validators import email\nresult = email('user@example.com')\n",
        {"ok": True, "value": True},
    ),
    (
        'email_valid_subdomain',
        "from validators import email\nresult = email('user@mail.example.com')\n",
        {"ok": True, "value": True},
    ),
    (
        'email_invalid_no_at',
        "from validators import email\nresult = bool(email('userexample.com'))\n",
        {"ok": True, "value": False},
    ),
    (
        'email_invalid_double_at',
        "from validators import email\nresult = bool(email('user@@example.com'))\n",
        {"ok": True, "value": False},
    ),
    (
        'email_invalid_empty',
        "from validators import email\nresult = bool(email(''))\n",
        {"ok": True, "value": False},
    ),
    (
        'url_valid_http',
        "from validators import url\nresult = url('http://example.com')\n",
        {"ok": True, "value": True},
    ),
    (
        'url_valid_https',
        "from validators import url\nresult = url('https://example.com')\n",
        {"ok": True, "value": True},
    ),
    (
        'url_valid_with_path',
        "from validators import url\nresult = url('https://example.com/path/to/page')\n",
        {"ok": True, "value": True},
    ),
    (
        'url_valid_with_query',
        "from validators import url\nresult = url('https://example.com/page?key=value&foo=bar')\n",
        {"ok": True, "value": True},
    ),
    (
        'url_valid_with_fragment',
        "from validators import url\nresult = url('https://example.com/page#section')\n",
        {"ok": True, "value": True},
    ),
    (
        'url_valid_ftp',
        "from validators import url\nresult = url('ftp://ftp.example.com')\n",
        {"ok": True, "value": True},
    ),
    (
        'url_invalid_no_scheme',
        "from validators import url\nresult = bool(url('example.com'))\n",
        {"ok": True, "value": False},
    ),
    (
        'url_invalid_whitespace',
        "from validators import url\nresult = bool(url('http://example.com/path with spaces'))\n",
        {"ok": True, "value": False},
    ),
    (
        'url_invalid_empty',
        "from validators import url\nresult = bool(url(''))\n",
        {"ok": True, "value": False},
    ),
    (
        'domain_valid_basic',
        "from validators import domain\nresult = domain('example.com')\n",
        {"ok": True, "value": True},
    ),
    (
        'domain_valid_subdomain',
        "from validators import domain\nresult = domain('sub.example.com')\n",
        {"ok": True, "value": True},
    ),
    (
        'domain_valid_multi_level',
        "from validators import domain\nresult = domain('deep.sub.example.com')\n",
        {"ok": True, "value": True},
    ),
    (
        'domain_invalid_with_slash',
        "from validators import domain\nresult = bool(domain('example.com/'))\n",
        {"ok": True, "value": False},
    ),
    (
        'domain_invalid_empty',
        "from validators import domain\nresult = bool(domain(''))\n",
        {"ok": True, "value": False},
    ),
    (
        'ipv4_valid_basic',
        "from validators import ipv4\nresult = ipv4('192.168.1.1')\n",
        {"ok": True, "value": True},
    ),
    (
        'ipv4_valid_public',
        "from validators import ipv4\nresult = ipv4('8.8.8.8')\n",
        {"ok": True, "value": True},
    ),
    (
        'ipv4_valid_cidr',
        "from validators import ipv4\nresult = ipv4('192.168.0.0/24')\n",
        {"ok": True, "value": True},
    ),
    (
        'ipv4_valid_localhost',
        "from validators import ipv4\nresult = ipv4('127.0.0.1')\n",
        {"ok": True, "value": True},
    ),
    (
        'ipv4_invalid_high_octet',
        "from validators import ipv4\nresult = bool(ipv4('256.1.1.1'))\n",
        {"ok": True, "value": False},
    ),
    (
        'ipv4_invalid_format',
        "from validators import ipv4\nresult = bool(ipv4('192.168.1'))\n",
        {"ok": True, "value": False},
    ),
    (
        'ipv4_invalid_empty',
        "from validators import ipv4\nresult = bool(ipv4(''))\n",
        {"ok": True, "value": False},
    ),
    (
        'ipv4_private_check_true',
        "from validators import ipv4\nresult = ipv4('192.168.1.1', private=True)\n",
        {"ok": True, "value": True},
    ),
    (
        'ipv4_private_check_false',
        "from validators import ipv4\nresult = bool(ipv4('8.8.8.8', private=True))\n",
        {"ok": True, "value": False},
    ),
    (
        'ipv4_public_check',
        "from validators import ipv4\nresult = ipv4('8.8.8.8', private=False)\n",
        {"ok": True, "value": True},
    ),
    (
        'ipv6_valid_basic',
        "from validators import ipv6\nresult = ipv6('2001:db8::8a2e:370:7334')\n",
        {"ok": True, "value": True},
    ),
    (
        'ipv6_valid_localhost',
        "from validators import ipv6\nresult = ipv6('::1')\n",
        {"ok": True, "value": True},
    ),
    (
        'ipv6_valid_compressed',
        "from validators import ipv6\nresult = ipv6('2001:db8::1')\n",
        {"ok": True, "value": True},
    ),
    (
        'ipv6_valid_ipv4_mapped',
        "from validators import ipv6\nresult = ipv6('::ffff:192.0.2.128')\n",
        {"ok": True, "value": True},
    ),
    (
        'ipv6_valid_cidr',
        "from validators import ipv6\nresult = ipv6('2001:db8::/32')\n",
        {"ok": True, "value": True},
    ),
    (
        'ipv6_invalid_format',
        "from validators import ipv6\nresult = bool(ipv6('gggg::1'))\n",
        {"ok": True, "value": False},
    ),
    (
        'ipv6_invalid_empty',
        "from validators import ipv6\nresult = bool(ipv6(''))\n",
        {"ok": True, "value": False},
    ),
    (
        'uuid_valid_v4',
        "from validators import uuid\nresult = uuid('2bc1c94f-0deb-43e9-92a1-4775189ec9f8')\n",
        {"ok": True, "value": True},
    ),
    (
        'uuid_valid_object',
        'from validators import uuid\nimport uuid as uuid_module\nresult = uuid(uuid_module.uuid4())\n',
        {"ok": True, "value": True},
    ),
    (
        'uuid_invalid_format',
        "from validators import uuid\nresult = bool(uuid('not-a-uuid'))\n",
        {"ok": True, "value": False},
    ),
    (
        'uuid_invalid_empty',
        "from validators import uuid\nresult = bool(uuid(''))\n",
        {"ok": True, "value": False},
    ),
    (
        'mac_valid_colon',
        "from validators import mac_address\nresult = mac_address('01:23:45:67:ab:CD')\n",
        {"ok": True, "value": True},
    ),
    (
        'mac_valid_dash',
        "from validators import mac_address\nresult = mac_address('01-23-45-67-ab-CD')\n",
        {"ok": True, "value": True},
    ),
    (
        'mac_invalid_short',
        "from validators import mac_address\nresult = bool(mac_address('01:23:45:67:ab'))\n",
        {"ok": True, "value": False},
    ),
    (
        'mac_invalid_format',
        "from validators import mac_address\nresult = bool(mac_address('not-a-mac'))\n",
        {"ok": True, "value": False},
    ),
    (
        'mac_invalid_empty',
        "from validators import mac_address\nresult = bool(mac_address(''))\n",
        {"ok": True, "value": False},
    ),
    (
        'iban_valid_de',
        "from validators import iban\nresult = iban('DE29100500001061045672')\n",
        {"ok": True, "value": True},
    ),
    (
        'iban_valid_gb',
        "from validators import iban\nresult = iban('GB82WEST12345698765432')\n",
        {"ok": True, "value": True},
    ),
    (
        'iban_invalid_short',
        "from validators import iban\nresult = bool(iban('DE123'))\n",
        {"ok": True, "value": False},
    ),
    (
        'iban_invalid_checksum',
        "from validators import iban\nresult = bool(iban('DE00100500001061045672'))\n",
        {"ok": True, "value": False},
    ),
    (
        'iban_invalid_empty',
        "from validators import iban\nresult = bool(iban(''))\n",
        {"ok": True, "value": False},
    ),
    (
        'card_valid_luhn',
        "from validators import card_number\nresult = card_number('4242424242424242')\n",
        {"ok": True, "value": True},
    ),
    (
        'card_invalid_luhn',
        "from validators import card_number\nresult = bool(card_number('4242424242424241'))\n",
        {"ok": True, "value": False},
    ),
    (
        'card_invalid_empty',
        "from validators import card_number\nresult = bool(card_number(''))\n",
        {"ok": True, "value": False},
    ),
    (
        'visa_valid',
        "from validators import visa\nresult = visa('4242424242424242')\n",
        {"ok": True, "value": True},
    ),
    (
        'visa_invalid_not_visa',
        "from validators import visa\nresult = bool(visa('5555555555554444'))\n",
        {"ok": True, "value": False},
    ),
    (
        'mastercard_valid',
        "from validators import mastercard\nresult = mastercard('5555555555554444')\n",
        {"ok": True, "value": True},
    ),
    (
        'mastercard_invalid_not_mc',
        "from validators import mastercard\nresult = bool(mastercard('4242424242424242'))\n",
        {"ok": True, "value": False},
    ),
    (
        'amex_valid',
        "from validators import amex\nresult = amex('378282246310005')\n",
        {"ok": True, "value": True},
    ),
    (
        'amex_invalid_not_amex',
        "from validators import amex\nresult = bool(amex('4242424242424242'))\n",
        {"ok": True, "value": False},
    ),
    (
        'discover_valid',
        "from validators import discover\nresult = discover('6011111111111117')\n",
        {"ok": True, "value": True},
    ),
    (
        'discover_invalid',
        "from validators import discover\nresult = bool(discover('4242424242424242'))\n",
        {"ok": True, "value": False},
    ),
    (
        'jcb_valid',
        "from validators import jcb\nresult = jcb('3566002020360505')\n",
        {"ok": True, "value": True},
    ),
    (
        'jcb_invalid',
        "from validators import jcb\nresult = bool(jcb('4242424242424242'))\n",
        {"ok": True, "value": False},
    ),
    (
        'diners_valid',
        "from validators import diners\nresult = diners('3056930009020004')\n",
        {"ok": True, "value": True},
    ),
    (
        'diners_invalid',
        "from validators import diners\nresult = bool(diners('4242424242424242'))\n",
        {"ok": True, "value": False},
    ),
    (
        'unionpay_valid',
        "from validators import unionpay\nresult = unionpay('6200000000000005')\n",
        {"ok": True, "value": True},
    ),
    (
        'unionpay_invalid',
        "from validators import unionpay\nresult = bool(unionpay('4242424242424242'))\n",
        {"ok": True, "value": False},
    ),
    (
        'mir_valid',
        "from validators import mir\nresult = mir('2200123456789019')\n",
        {"ok": True, "value": True},
    ),
    (
        'mir_invalid',
        "from validators import mir\nresult = bool(mir('4242424242424242'))\n",
        {"ok": True, "value": False},
    ),
    (
        'length_valid_min',
        "from validators import length\nresult = length('hello', min_val=3)\n",
        {"ok": True, "value": True},
    ),
    (
        'length_valid_max',
        "from validators import length\nresult = length('hello', max_val=10)\n",
        {"ok": True, "value": True},
    ),
    (
        'length_valid_exact',
        "from validators import length\nresult = length('test', min_val=4, max_val=4)\n",
        {"ok": True, "value": True},
    ),
    (
        'length_invalid_too_short',
        "from validators import length\nresult = bool(length('hi', min_val=3))\n",
        {"ok": True, "value": False},
    ),
    (
        'length_invalid_too_long',
        "from validators import length\nresult = bool(length('very long string', max_val=5))\n",
        {"ok": True, "value": False},
    ),
    (
        'validation_error_bool_false',
        "from validators import email\nresult = bool(email('invalid'))\nvalue = bool(result)\n",
        {"ok": True, "value": False},
    ),
    (
        'validation_error_has_func',
        "from validators import email\nerror = email('invalid')\nresult = hasattr(error, 'func')\n",
        {"ok": True, "value": True},
    ),
]

assert len(CASES) == 76, f"Expected 76 cases, got {len(CASES)}"


def main() -> None:
    leaves: list[dict[str, object]] = []
    for case_id, source, expected in CASES:
        status, actual = _run(source, expected)
        leaf: dict[str, object] = {"id": case_id, "status": status}
        if status == "failed":
            leaf["message"] = json.dumps(actual, ensure_ascii=False, sort_keys=True, default=repr)
        leaves.append(leaf)
    print(json.dumps({"schema_version": "1.0", "leaves": leaves}, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
