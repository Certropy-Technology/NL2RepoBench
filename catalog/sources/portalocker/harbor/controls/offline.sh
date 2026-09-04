#!/usr/bin/env bash
set -euo pipefail
python -I -m nl2repobench.verification.network_check --output /logs/verifier/network.json
