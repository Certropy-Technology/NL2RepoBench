#!/usr/bin/env bash
set -euo pipefail
(sleep 60) &
printf 'background_pid=%s\n' "$!"
