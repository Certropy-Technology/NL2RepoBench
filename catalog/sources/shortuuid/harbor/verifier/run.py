"""Private deterministic scenarios for the shortuuid public contract.

Each scenario runs as the unprivileged candidate in an isolated subprocess and
must be derivable from the public instruction (https://github.com/skorokithakis/shortuuid,
v1.0.13, immutable revision 16374d288c796faa2aee5789ed649c3ed7cdd9be). The
candidate runner executes the script and reads the ``result`` binding.
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
        "generation-default",
        "import shortuuid\ns = shortuuid.uuid()\nresult = [type(s).__name__, s.isalnum(), 20 < len(s) < 24]",
        {"ok": True, "value": ["str", True, True]},
    ),
    (
        "generation-named",
        "import shortuuid\na = shortuuid.uuid('http://www.example.com/')\nb = shortuuid.uuid('HTTP://www.example.com/')\nc = shortuuid.uuid('example.com/')\nresult = [len(a), len(b), len(c)]",
        {"ok": True, "value": [22, 22, 22]},
    ),
    (
        "encoding-known-uuid",
        "from uuid import UUID\nimport shortuuid\nu = UUID('{3b1f8b40-222c-4a6e-b77e-779d5a94e21c}')\nresult = shortuuid.encode(u)",
        {"ok": True, "value": "CXc85b4rqinB7s5J52TRYb"},
    ),
    (
        "decoding-known-id",
        "from uuid import UUID\nimport shortuuid\nu = UUID('{3b1f8b40-222c-4a6e-b77e-779d5a94e21c}')\nresult = shortuuid.decode('CXc85b4rqinB7s5J52TRYb') == u",
        {"ok": True, "value": True},
    ),
    (
        "alphabet",
        "import shortuuid\nsu = shortuuid.ShortUUID()\nalphabet = '01'\nsu.set_alphabet(alphabet)\nresult = [su.get_alphabet() == alphabet, set(su.uuid()) == set('01'), 116 < len(su.uuid()) < 140]",
        {"ok": True, "value": [True, True, True]},
    ),
    (
        "alphabet-invalid",
        "import shortuuid\nsu = shortuuid.ShortUUID()\nr = []\ntry:\n    su.set_alphabet('1')\nexcept ValueError:\n    r.append('ValueError')\ntry:\n    su.set_alphabet('1111111')\nexcept ValueError:\n    r.append('ValueError')\nresult = r",
        {"ok": True, "value": ["ValueError", "ValueError"]},
    ),
    (
        "constructor-invalid",
        "import shortuuid\nr = []\ntry:\n    shortuuid.ShortUUID('0')\nexcept ValueError:\n    r.append('ValueError')\nresult = r",
        {"ok": True, "value": ["ValueError"]},
    ),
    (
        "random-length",
        "import shortuuid\nresult = [len(shortuuid.random()), all(len(shortuuid.random(i)) == i for i in range(1, 100))]",
        {"ok": True, "value": [22, True]},
    ),
    (
        "class-uuid",
        "import shortuuid\nsu = shortuuid.ShortUUID()\ns = su.uuid()\nresult = [20 < len(s) < 24, len(su.uuid('http://www.example.com/')) == 22]",
        {"ok": True, "value": [True, True]},
    ),
    (
        "class-encoding-decoding",
        "from uuid import uuid4\nimport shortuuid\nsu = shortuuid.ShortUUID()\nu = uuid4()\nresult = [u == su.decode(su.encode(u)), su.encode(su.decode(su.encode(u))) == su.encode(u)]",
        {"ok": True, "value": [True, True]},
    ),
    (
        "encoded-length",
        "import string\nimport shortuuid\nsu1 = shortuuid.ShortUUID()\nsu2 = shortuuid.ShortUUID(string.ascii_uppercase + string.ascii_lowercase + string.digits + '+/')\nsu3 = shortuuid.ShortUUID('01')\nresult = [su1.encoded_length(), su2.encoded_length(), su3.encoded_length(), su1.encoded_length(num_bytes=8)]",
        {"ok": True, "value": [22, 22, 128, 11]},
    ),
    (
        "padding",
        "from uuid import UUID, uuid4\nimport shortuuid\nsu = shortuuid.ShortUUID()\nran = su.encode(uuid4())\nsmall = su.encode(UUID(int=0))\nresult = [len(ran) == len(small), su.decode(small) == UUID(int=0), su.decode(ran) == su.decode(ran)]",
        {"ok": True, "value": [True, True, True]},
    ),
    (
        "consistency-length",
        "from uuid import uuid4\nfrom collections import defaultdict\nimport shortuuid\nsu = shortuuid.ShortUUID()\nuid_lengths = defaultdict(int)\nfor _ in range(200):\n    r = uuid4()\n    uid_lengths[len(su.encode(r))] += 1\nresult = [len(uid_lengths) == 1, sum(uid_lengths.values()) == 200]",
        {"ok": True, "value": [True, True]},
    ),
    (
        "encode-invalid",
        "import shortuuid\nsu = shortuuid.ShortUUID()\nr = []\nfor bad in ([], {}, 42, 42.0):\n    try:\n        su.encode(bad)\n    except ValueError:\n        r.append('ValueError')\nresult = len(r)",
        {"ok": True, "value": 4},
    ),
    (
        "decode-invalid",
        "import shortuuid\nsu = shortuuid.ShortUUID()\nr = []\nfor bad in ([], {}, (2,), 42):\n    try:\n        su.decode(bad)\n    except ValueError:\n        r.append('ValueError')\nresult = len(r)",
        {"ok": True, "value": 4},
    ),
    (
        "cli-generate",
        "import shortuuid.cli as c\nfrom unittest.mock import patch\nwith patch('shortuuid.cli.print') as mp:\n    c.cli([])\n    out = mp.call_args[0][0]\nresult = [len(out), out.isalnum()]",
        {"ok": True, "value": [22, True]},
    ),
    (
        "cli-encode",
        "import shortuuid.cli as c\nfrom unittest.mock import patch\nwith patch('shortuuid.cli.print') as mp:\n    c.cli(['encode', '3b1f8b40-222c-4a6e-b77e-779d5a94e21c'])\nresult = mp.call_args[0][0]",
        {"ok": True, "value": "CXc85b4rqinB7s5J52TRYb"},
    ),
    (
        "cli-decode",
        "import shortuuid.cli as c\nfrom unittest.mock import patch\nwith patch('shortuuid.cli.print') as mp:\n    c.cli(['decode', 'CXc85b4rqinB7s5J52TRYb'])\nresult = mp.call_args[0][0]",
        {"ok": True, "value": "3b1f8b40-222c-4a6e-b77e-779d5a94e21c"},
    ),
    (
        "roundtrip",
        "from uuid import uuid4\nimport shortuuid\nsu = shortuuid.ShortUUID()\nu = uuid4()\ns = su.encode(u)\nresult = [su.decode(s) == u, len(s) == su.encoded_length()]",
        {"ok": True, "value": [True, True]},
    ),
]


def main() -> None:
    leaves: list[dict[str, object]] = []
    for case_id, source, expected in CASES:
        status, actual = _run(source, expected)
        leaf: dict[str, object] = {"id": case_id, "status": status}
        if status == "failed":
            leaf["message"] = json.dumps(actual, ensure_ascii=False, sort_keys=True)
        leaves.append(leaf)
    print(json.dumps({"schema_version": "1.0", "leaves": leaves}, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
