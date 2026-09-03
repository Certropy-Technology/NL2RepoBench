#!/usr/bin/env bash
set -euo pipefail

test ! -e /workspace/.git
test ! -e /workspace/upstream
printf 'offline control uses the Oracle workspace under verifier network_mode=none\n'
