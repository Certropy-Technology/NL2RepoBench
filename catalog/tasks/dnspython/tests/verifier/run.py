"""Private deterministic child-side verifier for the dnspython task."""

from __future__ import annotations

import json
import os
import subprocess
import sys


SCENARIOS: tuple[tuple[str, str], ...] = (
    ("name-presentation", """
import dns.name
n = dns.name.from_text('WWW.Example.COM.')
assert str(n) == 'WWW.Example.COM.'
assert n.labels == (b'WWW', b'Example', b'COM', b'')
assert n.is_absolute()
"""),
    ("name-relations", """
import dns.name
origin = dns.name.from_text('example.com.')
child = dns.name.from_text('www.example.com.')
assert str(child.relativize(origin)) == 'www'
assert str(dns.name.from_text('www.').derelativize(origin)) == 'www.'
assert child.is_subdomain(origin)
assert origin.is_superdomain(child)
"""),
    ("name-wire-roundtrip", """
import dns.name
n = dns.name.from_text('a\\032b.example.')
wire = n.to_wire()
decoded, offset = dns.name.from_wire(wire + b'next', 0)
assert decoded == n
assert offset == len(wire)
assert n.to_digestable() == wire.lower()
"""),
    ("type-and-class-symbols", """
import dns.rdatatype, dns.rdataclass
assert dns.rdatatype.from_text('a') == 1
assert dns.rdatatype.to_text(28) == 'AAAA'
assert dns.rdatatype.RdataType.make('MX') == 15
assert dns.rdataclass.from_text('in') == 1
assert dns.rdataclass.to_text(1) == 'IN'
try:
    dns.rdatatype.from_text('not-a-type')
except dns.rdatatype.UnknownRdatatype:
    pass
else:
    raise AssertionError('unknown type accepted')
"""),
    ("ttl-conversion", """
import dns.ttl
assert dns.ttl.from_text('1h30m') == 5400
assert dns.ttl.from_text('2W') == 1209600
assert dns.ttl.make('1h') == 3600
try:
    dns.ttl.from_text('-1')
except dns.ttl.BadTTL:
    pass
else:
    raise AssertionError('negative TTL accepted')
"""),
    ("ipv4-conversion", """
import dns.ipv4
packed = dns.ipv4.inet_aton('192.0.2.1')
assert packed == b'\\xc0\\x00\\x02\\x01'
assert dns.ipv4.inet_ntoa(packed) == '192.0.2.1'
"""),
    ("ipv6-conversion", """
import dns.ipv6
packed = dns.ipv6.inet_aton('2001:db8::1')
assert len(packed) == 16
assert dns.ipv6.inet_ntoa(packed) == '2001:db8::1'
"""),
    ("rrset-a-records", """
import dns.rrset
rr = dns.rrset.from_text('example.com.', 300, 'IN', 'A', '192.0.2.2', '192.0.2.1')
assert str(rr.name) == 'example.com.'
assert rr.ttl == 300 and rr.rdclass == 1 and rr.rdtype == 1
assert sorted(str(item) for item in rr) == ['192.0.2.1', '192.0.2.2']
assert len(rr) == 2
"""),
    ("rdataset-deduplication", """
import dns.rdataset
rd = dns.rdataset.from_text('IN', 'A', 120, '192.0.2.1', '192.0.2.1')
assert rd.ttl == 120 and rd.rdclass == 1 and rd.rdtype == 1
assert len(rd) == 1
assert str(next(iter(rd))) == '192.0.2.1'
"""),
    ("zone-relative-lookup", """
import dns.zone
text = '''$ORIGIN example.com.
@ 3600 IN SOA ns.example.com. hostmaster.example.com. 1 3600 600 86400 300
@ 3600 IN NS ns.example.com.
@ 300 IN A 192.0.2.10
www IN CNAME @
'''
zone = dns.zone.from_text(text)
assert str(zone.origin) == 'example.com.'
assert sorted(str(key) for key in zone.nodes) == ['@', 'www']
assert str(zone.find_rdataset('example.com.', 'A')[0]) == '192.0.2.10'
"""),
    ("zone-absolute-owners", """
import dns.zone
text = '''$ORIGIN example.com.
@ 3600 IN SOA ns.example.com. hostmaster.example.com. 1 3600 600 86400 300
@ 3600 IN NS ns.example.com.
www 300 IN A 192.0.2.20
'''
zone = dns.zone.from_text(text, relativize=False)
assert str(zone.find_rdataset('www.example.com.', 'A')[0]) == '192.0.2.20'
assert 'www.example.com.' in {str(key) for key in zone.nodes}
"""),
    ("query-message", """
import dns.flags, dns.message, dns.rdatatype
query = dns.message.make_query('example.com.', dns.rdatatype.A)
query.id = 0x1234
assert len(query.question) == 1
assert str(query.question[0].name) == 'example.com.'
assert query.question[0].rdtype == dns.rdatatype.A
assert query.flags & dns.flags.RD
"""),
    ("message-wire-roundtrip", """
import dns.message, dns.rdatatype
query = dns.message.make_query('example.com.', dns.rdatatype.A)
query.id = 7
wire = query.to_wire()
decoded = dns.message.from_wire(wire)
assert decoded.id == 7
assert len(decoded.question) == 1
assert str(decoded.question[0].name) == 'example.com.'
assert decoded.question[0].rdtype == dns.rdatatype.A
"""),
    ("flags-conversion", """
import dns.flags
value = dns.flags.from_text('QR RD RA')
assert value == dns.flags.QR | dns.flags.RD | dns.flags.RA
assert dns.flags.to_text(value) == 'QR RD RA'
"""),
    ("tokenizer-comments", """
import dns.tokenizer
tokenizer = dns.tokenizer.Tokenizer('www.example. 300 IN A 192.0.2.1 ; ignored\\n')
values = []
while True:
    token = tokenizer.get()
    if token.is_eof():
        break
    if not token.is_eol():
        values.append(token.value)
assert values == ['www.example.', '300', 'IN', 'A', '192.0.2.1']
"""),
    ("wire-parser", """
import dns.wire
parser = dns.wire.Parser(b'\\x01\\x02\\x03\\x04abc')
assert parser.get_uint16() == 0x0102
assert parser.get_uint16() == 0x0304
assert parser.get_bytes(3) == b'abc'
assert parser.remaining() == 0
"""),
    ("reverse-name", """
import dns.reversename
reverse = dns.reversename.from_address('192.0.2.1')
assert str(reverse) == '1.2.0.192.in-addr.arpa.'
assert dns.reversename.to_address(reverse) == '192.0.2.1'
"""),
    ("dynamic-update", """
import dns.update
update = dns.update.Update('example.com.')
update.add('www', 300, 'A', '192.0.2.1')
assert len(update.authority) == 1
assert str(update.authority[0].name) == 'www'
assert update.authority[0].ttl == 300
assert update.authority[0].rdtype == 1
"""),
    ("keyring-and-edns-option", """
import dns.edns, dns.name, dns.tsigkeyring
keyring = dns.tsigkeyring.from_text({'key.example.': 'c2VjcmV0'})
assert keyring[dns.name.from_text('key.example.')] == b'secret'
option = dns.edns.GenericOption(65000, b'abc')
assert option.otype == 65000 and option.to_wire() == b'abc'
"""),
    ("package-version-metadata", """
import dns, dns.version
assert dns.__version__ == '2.9.0dev0'
assert dns.version.version == dns.__version__
assert dns.__path__
"""),
)


def _run_child(body: str, root: str, candidate_root: str) -> tuple[bool, str]:
    bootstrap = (
        "import sys; "
        f"sys.path.insert(0, {root!r}); "
        f"sys.path.insert(0, {candidate_root!r});\n" + body
    )
    command = [sys.executable, "-I", "-c", bootstrap]
    if os.environ.get("DNSTEST_LOCAL") != "1":
        command = ["runuser", "-u", "candidate", "--", *command]
    try:
        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=12,
            check=False,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        return False, str(exc)
    if completed.returncode == 0:
        return True, ""
    detail = (completed.stderr or completed.stdout).strip().replace("\n", " ")
    return False, detail[-500:]


def main() -> None:
    root = os.environ.get("DNSTEST_ROOT", "/tmp/candidate-site")
    candidate_root = os.environ.get("DNSTEST_CANDIDATE_ROOT", "/tmp/candidate")
    leaves = []
    for scenario_id, body in SCENARIOS:
        passed, message = _run_child(body, root, candidate_root)
        leaf = {"id": scenario_id, "status": "passed" if passed else "failed"}
        if message:
            leaf["message"] = message
        leaves.append(leaf)
    print(json.dumps({"schema_version": "1.0", "leaves": leaves}, sort_keys=True))


if __name__ == "__main__":
    main()
