#!/usr/bin/env bash
set -euo pipefail
printf '%s\n' 'this is not a Go module' > go.mod
: > go.sum
