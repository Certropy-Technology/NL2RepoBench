#!/usr/bin/env bash
set -euo pipefail
bash "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/stub-packages.sh"
(sleep 60) &
printf 'background_pid=%s\n' "$!"
