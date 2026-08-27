import assert from "node:assert/strict";
import test from "node:test";
import { callCandidate, callCandidateResult } from "./test_client.mjs";

test("parseISO parses an extended calendar date", () => {
  assert.equal(callCandidate("parseISO", ["2014-02-11"]), "2014-02-11T00:00:00.000Z");
});

test("parseISO parses a compact calendar date", () => {
  assert.equal(callCandidate("parseISO", ["20140211"]), "2014-02-11T00:00:00.000Z");
});

test("parseISO normalizes a numeric offset", () => {
  assert.equal(callCandidate("parseISO", ["2014-02-11T11:30:30+05:30"]), "2014-02-11T06:00:30.000Z");
});

test("parseISO parses an ISO week date", () => {
  assert.equal(callCandidate("parseISO", ["2014-W02-7"]), "2014-01-12T00:00:00.000Z");
});

test("parseISO returns an invalid date for an impossible date", () => {
  assert.equal(callCandidate("parseISO", ["2023-02-29"]), null);
});

test("formatISO defaults to extended complete form", () => {
  assert.equal(callCandidate("formatISO", ["2019-09-18T19:00:52.123Z"]), "2019-09-18T19:00:52Z");
});

test("formatISO supports basic date representation", () => {
  assert.equal(callCandidate("formatISO", ["2019-09-18T19:00:52.123Z", { format: "basic", representation: "date" }]), "20190918");
});

test("formatISO supports time-only representation", () => {
  assert.equal(callCandidate("formatISO", ["2019-09-18T19:00:52.123Z", { representation: "time" }]), "19:00:52Z");
});

test("formatISO rejects an invalid date", () => {
  const result = callCandidateResult("formatISO", ["not-a-date"]);
  assert.equal(result.ok, false);
  assert.equal(result.exception_type, "RangeError");
});

test("formatRFC3339 defaults to whole seconds", () => {
  assert.equal(callCandidate("formatRFC3339", ["2019-09-18T19:00:52.234Z"]), "2019-09-18T19:00:52Z");
});

test("formatRFC3339 supports three fractional digits", () => {
  assert.equal(callCandidate("formatRFC3339", ["2019-09-18T19:00:52.234Z", { fractionDigits: 3 }]), "2019-09-18T19:00:52.234Z");
});

test("formatRFC3339 rejects an invalid date", () => {
  const result = callCandidateResult("formatRFC3339", ["not-a-date"]);
  assert.equal(result.ok, false);
  assert.equal(result.exception_type, "RangeError");
});

test("getISOWeek handles an ISO week-year boundary", () => {
  assert.equal(callCandidate("getISOWeek", ["2005-01-02T12:00:00.000Z"]), 53);
});

test("isWeekend distinguishes weekends from weekdays", () => {
  assert.equal(callCandidate("isWeekend", ["2024-06-08"]), true);
  assert.equal(callCandidate("isWeekend", ["2024-06-09"]), true);
  assert.equal(callCandidate("isWeekend", ["2024-06-10"]), false);
});

test("isWeekend returns false for an invalid date", () => {
  assert.equal(callCandidate("isWeekend", ["not-a-date"]), false);
});

test("isLeapYear implements Gregorian century rules", () => {
  assert.equal(callCandidate("isLeapYear", ["2000-06-01"]), true);
  assert.equal(callCandidate("isLeapYear", ["1900-06-01"]), false);
  assert.equal(callCandidate("isLeapYear", ["2024-06-01"]), true);
  assert.equal(callCandidate("isLeapYear", ["2023-06-01"]), false);
});

test("isWithinInterval includes both endpoints", () => {
  const interval = { start: "2024-01-01T00:00:00.000Z", end: "2024-01-31T23:59:59.999Z" };
  assert.equal(callCandidate("isWithinInterval", [interval.start, interval]), true);
  assert.equal(callCandidate("isWithinInterval", [interval.end, interval]), true);
});

test("isWithinInterval normalizes reversed endpoints", () => {
  assert.equal(callCandidate("isWithinInterval", ["2024-01-15", { start: "2024-01-31", end: "2024-01-01" }]), true);
});

test("isWithinInterval returns false for an invalid date", () => {
  assert.equal(callCandidate("isWithinInterval", ["not-a-date", { start: "2024-01-01", end: "2024-01-31" }]), false);
});
