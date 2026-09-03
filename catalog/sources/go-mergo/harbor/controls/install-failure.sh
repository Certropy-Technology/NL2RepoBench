#!/usr/bin/env bash
set -euo pipefail
printf '%s\n' 'not a go module' > go.mod
: > go.sum
