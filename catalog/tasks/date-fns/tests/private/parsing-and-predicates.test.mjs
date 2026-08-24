import assert from "node:assert/strict";
import test from "node:test";
import { callCandidate } from "./test_client.mjs";

test("formatISO emits extended complete UTC text", () => {
  assert.equal(callCandidate("formatISO", ["2019-03-03T19:00:52.123Z"]), "2019-03-03T19:00:52Z");
});
test("formatISO emits a basic date representation", () => {
  assert.equal(callCandidate("formatISO", ["2019-03-03T19:00:52.123Z", { format: "basic", representation: "date" }]), "20190303");
});
test("formatISO emits a time representation", () => {
  assert.equal(callCandidate("formatISO", ["2019-03-03T19:00:52.123Z", { representation: "time" }]), "19:00:52Z");
});
test("formatRFC3339 keeps requested fractions", () => {
  assert.equal(callCandidate("formatRFC3339", ["2019-03-03T19:00:52.123Z", { fractionDigits: 3 }]), "2019-03-03T19:00:52.123Z");
});
test("parseISO accepts an ISO week date", () => {
  assert.equal(callCandidate("parseISO", ["2014-W02-7"]), "2014-01-12T00:00:00.000Z");
});
test("parseISO returns an invalid date for an invalid month", () => {
  assert.equal(callCandidate("parseISO", ["2014-00"]), null);
});
test("getISOWeek handles the first day of a year", () => {
  assert.equal(callCandidate("getISOWeek", ["2016-01-01T00:00:00.000Z"]), 53);
});
test("isWeekend identifies Sunday and Monday", () => {
  assert.deepEqual([callCandidate("isWeekend", ["2024-08-18T15:00:00.000Z"]), callCandidate("isWeekend", ["2024-08-19T15:00:00.000Z"])], [true, false]);
});
test("isLeapYear distinguishes leap years", () => {
  assert.deepEqual([callCandidate("isLeapYear", ["2020-01-01T00:00:00.000Z"]), callCandidate("isLeapYear", ["2019-01-01T00:00:00.000Z"])], [true, false]);
});
test("isWithinInterval includes both endpoints", () => {
  assert.equal(callCandidate("isWithinInterval", ["2020-01-05T00:00:00.000Z", { start: "2020-01-01T00:00:00.000Z", end: "2020-01-05T00:00:00.000Z" }]), true);
});
