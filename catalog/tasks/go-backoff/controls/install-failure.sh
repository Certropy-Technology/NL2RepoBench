#!/usr/bin/env bash
set -euo pipefail
rm -rf go.mod go.sum vendor backoff.go
printf broken > broken.txt
