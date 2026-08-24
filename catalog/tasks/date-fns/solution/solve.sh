#!/usr/bin/env bash
set -euo pipefail

cat > package.json <<'JSON'
{
  "name": "date-fns",
  "version": "4.4.0",
  "type": "module",
  "exports": {
    ".": {
      "import": "./index.js",
      "default": "./index.js"
    }
  }
}
JSON
cat > package-lock.json <<'JSON'
{
  "name": "date-fns",
  "version": "4.4.0",
  "lockfileVersion": 3,
  "requires": true,
  "packages": {
    "": {
      "name": "date-fns",
      "version": "4.4.0",
      "type": "module",
      "exports": {
        ".": {
          "import": "./index.js",
          "default": "./index.js"
        }
      }
    }
  }
}
JSON
cat > index.js <<'JS'
const asDate = (value) => new Date(value);
const valid = (value) => !Number.isNaN(value.getTime());
const startOfDay = (value) => { const date = asDate(value); date.setUTCHours(0, 0, 0, 0); return date; };
const daysInMonth = (year, month) => new Date(Date.UTC(year, month + 1, 0)).getUTCDate();
const isoWeekParts = (value) => {
  const date = startOfDay(value);
  const day = date.getUTCDay() || 7;
  date.setUTCDate(date.getUTCDate() + 4 - day);
  const year = date.getUTCFullYear();
  const first = new Date(Date.UTC(year, 0, 1));
  return { year, week: Math.ceil((((date - first) / 86400000) + 1) / 7) };
};

export function addDays(value, amount) { const date = asDate(value); date.setUTCDate(date.getUTCDate() + amount); return date; }
export function addMonths(value, amount) { const date = asDate(value); const day = date.getUTCDate(); date.setUTCDate(1); date.setUTCMonth(date.getUTCMonth() + amount); date.setUTCDate(Math.min(day, daysInMonth(date.getUTCFullYear(), date.getUTCMonth()))); return date; }
export function setHours(value, hours) { const date = asDate(value); date.setUTCHours(hours); return date; }
export function differenceInCalendarDays(left, right) { const a = startOfDay(left); const b = startOfDay(right); return Math.round((a - b) / 86400000); }
export function eachDayOfInterval(interval, options = {}) { const start = startOfDay(interval.start); const end = startOfDay(interval.end); const rawStep = options.step ?? 1; if (!rawStep || !Number.isFinite(rawStep)) return []; const reverse = rawStep < 0; const step = Math.abs(rawStep); const direction = start <= end ? 1 : -1; const out = []; for (let date = new Date(start); direction > 0 ? date <= end : date >= end; date.setUTCDate(date.getUTCDate() + direction * step)) out.push(new Date(date)); return reverse ? out.reverse() : out; }
export function startOfWeek(value, options = {}) { const date = startOfDay(value); const weekStartsOn = options.weekStartsOn ?? 0; const distance = (date.getUTCDay() - weekStartsOn + 7) % 7; date.setUTCDate(date.getUTCDate() - distance); return date; }
export function endOfMonth(value) { const date = asDate(value); date.setUTCMonth(date.getUTCMonth() + 1, 0); date.setUTCHours(23, 59, 59, 999); return date; }
export function formatISO(value, options = {}) { const date = asDate(value); if (!valid(date)) throw new RangeError("Invalid time value"); const extended = options.format !== "basic"; const datePart = extended ? date.toISOString().slice(0, 10) : date.toISOString().slice(0, 10).replaceAll("-", ""); const timePart = extended ? date.toISOString().slice(11, 19) : date.toISOString().slice(11, 19).replaceAll(":", ""); const zone = "Z"; if (options.representation === "date") return datePart; if (options.representation === "time") return `${timePart}${zone}`; return `${datePart}T${timePart}${zone}`; }
export function formatRFC3339(value, options = {}) { const date = asDate(value); if (!valid(date)) throw new RangeError("Invalid time value"); const digits = options.fractionDigits ?? 0; const base = date.toISOString().slice(0, 19); const fraction = digits ? `.${date.toISOString().slice(20, 20 + digits)}` : ""; return `${base}${fraction}Z`; }
export function parseISO(value) { if (typeof value === "string") { const week = value.match(/^([+-]?\d{4,})-?W(\d{2})-?(\d)?$/i); if (week) { const year = Number(week[1]); const day = Number(week[3] ?? 1); const jan4 = new Date(Date.UTC(year, 0, 4)); const monday = new Date(jan4); monday.setUTCDate(4 - (jan4.getUTCDay() || 7) + 1); monday.setUTCDate(monday.getUTCDate() + (Number(week[2]) - 1) * 7 + day - 1); return monday; } } return asDate(value); }
export function getISOWeek(value) { return isoWeekParts(value).week; }
export function isWeekend(value) { const date = asDate(value); return valid(date) && (date.getUTCDay() === 0 || date.getUTCDay() === 6); }
export function isLeapYear(value) { const year = asDate(value).getUTCFullYear(); return year % 4 === 0 && (year % 100 !== 0 || year % 400 === 0); }
export function isWithinInterval(value, interval) { const time = asDate(value).getTime(); return time >= asDate(interval.start).getTime() && time <= asDate(interval.end).getTime(); }
export function min(values) { return values.map(asDate).filter(valid).sort((a, b) => a - b)[0] ?? new Date(NaN); }
export function max(values) { return values.map(asDate).filter(valid).sort((a, b) => b - a)[0] ?? new Date(NaN); }
JS
