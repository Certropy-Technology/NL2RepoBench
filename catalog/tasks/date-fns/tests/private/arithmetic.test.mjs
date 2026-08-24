import assert from "node:assert/strict";
import test from "node:test";
import { callCandidate } from "./test_client.mjs";

test("addDays crosses a leap day", () => {
  assert.equal(callCandidate("addDays", ["2020-02-28T00:00:00.000Z", 2]), "2020-03-01T00:00:00.000Z");
});
test("addMonths clamps the destination month", () => {
  assert.equal(callCandidate("addMonths", ["2021-01-31T00:00:00.000Z", 1]), "2021-02-28T00:00:00.000Z");
});
test("setHours preserves the other fields", () => {
  assert.equal(callCandidate("setHours", ["2020-01-01T12:34:56.000Z", 3]), "2020-01-01T03:34:56.000Z");
});
test("differenceInCalendarDays ignores time of day", () => {
  assert.equal(callCandidate("differenceInCalendarDays", ["2020-03-01T00:00:00.000Z", "2020-02-28T23:00:00.000Z"]), 2);
});
test("eachDayOfInterval steps forward inclusively", () => {
  assert.deepEqual(callCandidate("eachDayOfInterval", [{ start: "2020-01-01T12:00:00.000Z", end: "2020-01-05T12:00:00.000Z" }, { step: 2 }]), ["2020-01-01T00:00:00.000Z", "2020-01-03T00:00:00.000Z", "2020-01-05T00:00:00.000Z"]);
});
test("eachDayOfInterval supports reverse intervals", () => {
  assert.deepEqual(callCandidate("eachDayOfInterval", [{ start: "2020-01-05T12:00:00.000Z", end: "2020-01-01T12:00:00.000Z" }, { step: 2 }]), ["2020-01-05T00:00:00.000Z", "2020-01-03T00:00:00.000Z", "2020-01-01T00:00:00.000Z"]);
});
test("eachDayOfInterval reverses with a negative step", () => {
  assert.deepEqual(callCandidate("eachDayOfInterval", [{ start: "2020-01-01T12:00:00.000Z", end: "2020-01-05T12:00:00.000Z" }, { step: -2 }]), ["2020-01-05T00:00:00.000Z", "2020-01-03T00:00:00.000Z", "2020-01-01T00:00:00.000Z"]);
});
test("startOfWeek honors Monday", () => {
  assert.equal(callCandidate("startOfWeek", ["2014-09-02T11:55:00.000Z", { weekStartsOn: 1 }]), "2014-09-01T00:00:00.000Z");
});
test("endOfMonth returns the final millisecond", () => {
  assert.equal(callCandidate("endOfMonth", ["2020-02-11T11:00:00.000Z"]), "2020-02-29T23:59:59.999Z");
});
test("min selects the earliest date", () => {
  assert.equal(callCandidate("min", [["2020-01-03T00:00:00.000Z", "2020-01-01T00:00:00.000Z", "2020-01-02T00:00:00.000Z"]]), "2020-01-01T00:00:00.000Z");
});
test("max selects the latest date", () => {
  assert.equal(callCandidate("max", [["2020-01-03T00:00:00.000Z", "2020-01-01T00:00:00.000Z", "2020-01-02T00:00:00.000Z"]]), "2020-01-03T00:00:00.000Z");
});
