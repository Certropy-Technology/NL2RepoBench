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
import { closeSync, openSync } from "node:fs";

function boundedHang() {
  const sentinel = "/tmp/candidate-site/tmp/date-fns-timeout-once";
  try {
    closeSync(openSync(sentinel, "wx"));
  } catch {
    throw new Error("timeout control follow-up call");
  }
  for (;;) {}
}

export const addDays = boundedHang;
export const addMonths = boundedHang;
export const setHours = boundedHang;
export const differenceInCalendarDays = boundedHang;
export const eachDayOfInterval = boundedHang;
export const startOfWeek = boundedHang;
export const endOfMonth = boundedHang;
export const parseISO = boundedHang;
export const formatISO = boundedHang;
export const formatRFC3339 = boundedHang;
export const getISOWeek = boundedHang;
export const isWeekend = boundedHang;
export const isLeapYear = boundedHang;
export const isWithinInterval = boundedHang;
export const min = boundedHang;
export const max = boundedHang;
EOF
cat > /workspace/package-lock.json <<'EOF'
{"name":"date-fns","version":"4.4.0","lockfileVersion":3,"requires":true,"packages":{"":{"name":"date-fns","version":"4.4.0"}}}
EOF
