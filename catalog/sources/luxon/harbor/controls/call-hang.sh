#!/usr/bin/env bash
set -euo pipefail

mkdir -p "$PWD"
printf '%s\n' '{"name":"luxon","version":"3.7.2","type":"commonjs","main":"index.js","license":"MIT","files":["index.js"]}' > "$PWD/package.json"
printf '%s\n' '{"name":"luxon","version":"3.7.2","lockfileVersion":3,"requires":true,"packages":{"":{"name":"luxon","version":"3.7.2","license":"MIT"}}}' > "$PWD/package-lock.json"
printf '%s\n' \
  'class DateTime { static fromISO() { throw new Error("stub"); } static fromObject() { for (;;) {} } static fromMillis() { throw new Error("stub"); } }' \
  'class Placeholder {}' \
  'module.exports = { VERSION: "3.7.2", DateTime, Duration: Placeholder, Interval: Placeholder, Info: Placeholder, Zone: Placeholder, FixedOffsetZone: Placeholder, IANAZone: Placeholder, InvalidZone: Placeholder, SystemZone: Placeholder, Settings: Placeholder };' \
  > "$PWD/index.js"
