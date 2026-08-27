#!/usr/bin/env bash
set -euo pipefail

mkdir -p /workspace
cat > /workspace/package.json <<'EOF'
{
  "name": "date-fns",
  "version": "4.4.0",
  "type": "module",
  "exports": ".\/index.js"
}
EOF
cat > /workspace/index.js <<'EOF'
const placeholder = () => null;
export const addDays = placeholder;
export const addMonths = placeholder;
export const setHours = placeholder;
export const differenceInCalendarDays = placeholder;
export const eachDayOfInterval = placeholder;
export const startOfWeek = placeholder;
export const endOfMonth = placeholder;
export const parseISO = placeholder;
export const formatISO = placeholder;
export const formatRFC3339 = placeholder;
export const getISOWeek = placeholder;
export const isWeekend = placeholder;
export const isLeapYear = placeholder;
export const isWithinInterval = placeholder;
export const min = placeholder;
export const max = placeholder;
EOF
cat > /workspace/package-lock.json <<'EOF'
{"name":"date-fns","version":"4.4.0","lockfileVersion":3,"requires":true,"packages":{"":{"name":"date-fns","version":"4.4.0"}}}
EOF
