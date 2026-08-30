"""Record evidence that the verifier cannot establish a public connection."""

from __future__ import annotations

import argparse
import json
import os
import socket
from pathlib import Path

PROBES = (("pypi.org", 443), ("1.1.1.1", 443))
MAX_ROUTE_TABLE_BYTES = 64 * 1024
MAX_RECEIPT_BYTES = 128 * 1024


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


def _bounded_text(path: Path, max_bytes: int) -> str:
    with path.open("rb") as handle:
        data = handle.read(max_bytes + 1)
    if len(data) > max_bytes:
        raise ValueError(f"network receipt source exceeds {max_bytes} bytes: {path}")
    return data.decode("utf-8")


def build_receipt(
    probes: dict[str, bool],
    *,
    namespace_path: Path = Path("/proc/self/ns/net"),
    route_path: Path = Path("/proc/net/route"),
) -> dict[str, object]:
    """Build a bounded network receipt or raise an internal verifier error."""

    namespace = os.readlink(namespace_path)
    if len(namespace.encode("utf-8")) > 4096:
        raise ValueError("network namespace identifier exceeds size limit")
    return {
        "schema_version": "1.0",
        "probes": probes,
        "public_network_available": any(probes.values()),
        "network_namespace": namespace,
        "route_table": _bounded_text(route_path, MAX_ROUTE_TABLE_BYTES),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        probes = probe_public_network()
        receipt = build_receipt(probes)
        data = json.dumps(receipt, indent=2, sort_keys=True) + "\n"
        if len(data.encode("utf-8")) > MAX_RECEIPT_BYTES:
            raise ValueError("network receipt exceeds size limit")
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(data, encoding="utf-8")
    except (OSError, UnicodeError, ValueError):
        raise SystemExit(70) from None
    raise SystemExit(1 if receipt["public_network_available"] else 0)


if __name__ == "__main__":
    main()
