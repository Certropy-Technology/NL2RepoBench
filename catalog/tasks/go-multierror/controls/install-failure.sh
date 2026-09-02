#!/usr/bin/env bash
set -euo pipefail
printf '%s\n' 'not a Go module' > go.mod
: > go.sum
