#!/usr/bin/env bash
set -euo pipefail
test "${npm_config_offline:-true}" = true
