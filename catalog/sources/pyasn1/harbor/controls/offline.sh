#!/usr/bin/env bash
set -euo pipefail
test ! -e /proc/net/route || ! grep -qv '^Iface' /proc/net/route
