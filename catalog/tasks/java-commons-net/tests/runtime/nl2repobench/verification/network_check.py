"""Record evidence that the verifier cannot establish a public connection."""

from __future__ import annotations

import argparse
import json
import os
import socket
from pathlib import Path

PROBES = (("pypi.org", 443), ("1.1.1.1", 443))


def probe_public_network(timeout_sec: float = 1.0) -> dict[str, bool]:
    results: dict[str, bool] = {}
    for host, port in PROBES:
        key = f"{host}:{port}"
        try:
            with socket.create_connection((host, port), timeout=timeout_sec):
                results[key] = True
        except OSError:
            results[key] = False
    return results


def public_network_available(
    timeout_sec: float = 1.0,
) -> bool:
    return any(probe_public_network(timeout_sec).values())


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    probes = probe_public_network()
    available = any(probes.values())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "probes": probes,
                "public_network_available": available,
                "network_namespace": os.readlink("/proc/self/ns/net"),
                "route_table": Path("/proc/net/route").read_text(encoding="utf-8"),
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    raise SystemExit(1 if available else 0)


if __name__ == "__main__":
    main()
