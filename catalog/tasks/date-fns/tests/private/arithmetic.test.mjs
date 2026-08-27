import assert from "node:assert/strict";
import test from "node:test";
import { callCandidate } from "./test_client.mjs";

test("addDays crosses a leap-day boundary", () => {
  assert.equal(callCandidate("addDays", ["2020-02-28T15:30:00.000Z", 2]), "2020-03-01T15:30:00.000Z");
});

test("addDays accepts a negative amount", () => {
  assert.equal(callCandidate("addDays", ["2021-01-01T00:00:00.000Z", -1]), "2020-12-31T00:00:00.000Z");
});

test("addMonths clamps at the end of a common-year February", () => {
  assert.equal(callCandidate("addMonths", ["2021-01-31T12:00:00.000Z", 1]), "2021-02-28T12:00:00.000Z");
});

test("addMonths preserves leap day when available", () => {
  assert.equal(callCandidate("addMonths", ["2020-01-31T12:00:00.000Z", 1]), "2020-02-29T12:00:00.000Z");
});

test("setHours replaces the UTC hour", () => {
  assert.equal(callCandidate("setHours", ["2024-05-06T03:04:05.006Z", 22]), "2024-05-06T22:04:05.006Z");
});

test("differenceInCalendarDays ignores time of day", () => {
  assert.equal(callCandidate("differenceInCalendarDays", ["2024-03-02T00:01:00.000Z", "2024-03-01T23:59:00.000Z"]), 1);
});

test("differenceInCalendarDays preserves sign", () => {
  assert.equal(callCandidate("differenceInCalendarDays", ["2024-03-01T23:59:00.000Z", "2024-03-03T00:01:00.000Z"]), -2);
});

test("eachDayOfInterval includes both endpoints", () => {
  assert.deepEqual(callCandidate("eachDayOfInterval", [{ start: "2024-01-01T13:00:00.000Z", end: "2024-01-03T08:00:00.000Z" }]), [
    "2024-01-01T00:00:00.000Z",
    "2024-01-02T00:00:00.000Z",
    "2024-01-03T00:00:00.000Z",
  ]);
});

test("eachDayOfInterval honors a positive step", () => {
  assert.deepEqual(callCandidate("eachDayOfInterval", [{ start: "2024-01-01", end: "2024-01-06" }, { step: 2 }]), [
    "2024-01-01T00:00:00.000Z",
    "2024-01-03T00:00:00.000Z",
    "2024-01-05T00:00:00.000Z",
  ]);
});

test("eachDayOfInterval reverses output for a negative step", () => {
  assert.deepEqual(callCandidate("eachDayOfInterval", [{ start: "2024-01-01", end: "2024-01-05" }, { step: -2 }]), [
    "2024-01-05T00:00:00.000Z",
    "2024-01-03T00:00:00.000Z",
    "2024-01-01T00:00:00.000Z",
  ]);
});

test("eachDayOfInterval returns an empty array for step zero", () => {
  assert.deepEqual(callCandidate("eachDayOfInterval", [{ start: "2024-01-01", end: "2024-01-05" }, { step: 0 }]), []);
});

test("startOfWeek defaults to Sunday", () => {
  assert.equal(callCandidate("startOfWeek", ["2024-01-03T16:45:00.000Z"]), "2023-12-31T00:00:00.000Z");
});

test("startOfWeek accepts Monday as the first day", () => {
  assert.equal(callCandidate("startOfWeek", ["2024-01-03T16:45:00.000Z", { weekStartsOn: 1 }]), "2024-01-01T00:00:00.000Z");
});

test("endOfMonth returns the final millisecond of a leap February", () => {
  assert.equal(callCandidate("endOfMonth", ["2024-02-10T12:00:00.000Z"]), "2024-02-29T23:59:59.999Z");
});

test("min selects the earliest instant", () => {
  assert.equal(callCandidate("min", [["2020-04-03T00:00:00.000Z", "2019-12-31T23:59:59.000Z", 1577836800000]]), "2019-12-31T23:59:59.000Z");
});

test("max selects the latest instant", () => {
  assert.equal(callCandidate("max", [["2020-04-03T00:00:00.000Z", "2019-12-31T23:59:59.000Z", 1577836800000]]), "2020-04-03T00:00:00.000Z");
});

test("min returns an invalid date for an empty array", () => {
  assert.equal(callCandidate("min", [[]]), null);
});

test("max returns an invalid date for an empty array", () => {
  assert.equal(callCandidate("max", [[]]), null);
});

test("min and max propagate an invalid member", () => {
  assert.equal(callCandidate("min", [["2024-01-01", "not-a-date"]]), null);
  assert.equal(callCandidate("max", [["2024-01-01", "not-a-date"]]), null);
});
