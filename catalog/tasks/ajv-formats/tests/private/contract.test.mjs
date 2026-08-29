import assert from "node:assert/strict";
import test from "node:test";
import {callCandidate} from "./test_client.mjs";

let sequence = 0;
const request = (operation, fields = {}) => callCandidate({id: `case-${++sequence}`, operation, ...fields});
const check = (format, value, fields = {}) => request("validate", {schema: {type: "string", format}, value, ...fields}).data;

test("package metadata and public format table", () => {
  const result = request("inventory");
  assert.deepEqual(result.data, {
    name: "ajv-formats", version: "3.0.1", main: "dist/index.js",
    formats: ["date", "time", "date-time", "iso-time", "iso-date-time", "duration", "uri", "uri-reference", "uri-template", "url", "email", "hostname", "ipv4", "ipv6", "regex", "uuid", "json-pointer", "json-pointer-uri-fragment", "relative-json-pointer", "byte", "int32", "int64", "float", "double", "password", "binary"],
    hasGet: true,
  });
});

test("default plugin registers every format", () => {
  assert.equal(check("date", "2024-02-29").valid, true);
  assert.equal(check("uuid", "550e8400-e29b-41d4-a716-446655440000").valid, true);
});

test("selected format list registers only requested names", () => {
  assert.equal(check("date", "2024-01-01", {options: ["date"]}).valid, true);
  assert.throws(() => check("email", "a@example.com", {options: ["date"]}), /unknown format/i);
});

test("get returns full and fast definitions", () => {
  const full = request("get", {name: "date"}).data;
  const fast = request("get", {name: "date", mode: "fast"}).data;
  assert.equal(full.name, "date");
  assert.equal(fast.mode, "fast");
  assert.equal(full.hasCompare, true);
  assert.equal(fast.hasCompare, true);
});

test("get rejects unknown format", () => {
  assert.throws(() => request("get", {name: "not-a-format"}), /Unknown format/);
});

test("full date validates ranges and leap years", () => {
  assert.equal(check("date", "2016-02-29").valid, true);
  assert.equal(check("date", "2017-02-29").valid, false);
  assert.equal(check("date", "2020-09-35").valid, false);
});

test("fast date keeps structural shape without full range validation", () => {
  assert.equal(check("date", "2020-09-35", {options: {mode: "fast", formats: ["date"]}}).valid, true);
  assert.equal(check("date", "2020-09", {options: {mode: "fast", formats: ["date"]}}).valid, false);
});

test("time requires a timezone and handles leap seconds", () => {
  assert.equal(check("time", "17:27:38Z").valid, true);
  assert.equal(check("time", "17:27:38").valid, false);
  assert.equal(check("time", "23:59:60Z").valid, true);
});

test("ISO time accepts an optional timezone", () => {
  assert.equal(check("iso-time", "17:27:38").valid, true);
  assert.equal(check("iso-time", "17:27").valid, false);
});

test("date-time requires a valid date and timezone", () => {
  assert.equal(check("date-time", "2016-02-29T00:00:00Z").valid, true);
  assert.equal(check("date-time", "2017-02-29T00:00:00Z").valid, false);
  assert.equal(check("date-time", "2020-01-01T00:00:00").valid, false);
});

test("ISO date-time permits a space and absent timezone", () => {
  assert.equal(check("iso-date-time", "2020-01-01 00:00:00").valid, true);
  assert.equal(check("iso-date-time", "2020-01-01T00:00").valid, false);
});

test("duration validates RFC3339 duration forms", () => {
  assert.equal(check("duration", "P3Y6M4DT12H30M5S").valid, true);
  assert.equal(check("duration", "P").valid, false);
  assert.equal(check("duration", "3 days").valid, false);
});

test("URI formats distinguish absolute and relative references", () => {
  assert.equal(check("uri", "https://example.com/a?q=1").valid, true);
  assert.equal(check("uri", "/relative/path").valid, false);
  assert.equal(check("uri-reference", "/relative/path#part").valid, true);
});

test("URI templates validate expressions", () => {
  assert.equal(check("uri-template", "https://example.com/{user}").valid, true);
  assert.equal(check("uri-template", "https://example.com/{").valid, false);
});

test("email and hostname formats validate ordinary syntax", () => {
  assert.equal(check("email", "a@example.com").valid, true);
  assert.equal(check("email", "not-an-email").valid, false);
  assert.equal(check("hostname", "api.example.com").valid, true);
  assert.equal(check("hostname", "-bad.example").valid, false);
});

test("IPv4 and IPv6 formats validate address ranges", () => {
  assert.equal(check("ipv4", "192.168.1.10").valid, true);
  assert.equal(check("ipv4", "256.1.1.1").valid, false);
  assert.equal(check("ipv6", "2001:db8::1").valid, true);
  assert.equal(check("ipv6", "not-ipv6").valid, false);
});

test("regex and UUID formats validate JavaScript and RFC shapes", () => {
  assert.equal(check("regex", "^[a-z]+$").valid, true);
  assert.equal(check("regex", "[").valid, false);
  assert.equal(check("uuid", "550e8400-e29b-41d4-a716-446655440000").valid, true);
  assert.equal(check("uuid", "550e8400-e29b-41d4-a716-44665544000z").valid, false);
});

test("JSON pointer formats preserve escaping rules", () => {
  assert.equal(check("json-pointer", "/a~1b/~0c").valid, true);
  assert.equal(check("json-pointer", "/bad~2escape").valid, false);
  assert.equal(check("relative-json-pointer", "1/foo").valid, true);
  assert.equal(check("relative-json-pointer", "01/foo").valid, false);
});

test("byte and OpenAPI numeric formats enforce their domains", () => {
  assert.equal(check("byte", "SGVsbG8=").valid, true);
  assert.equal(check("byte", "not base64!").valid, false);
  assert.equal(request("validate", {schema: {type: "number", format: "int32"}, value: 2147483647}).data.valid, true);
  assert.equal(request("validate", {schema: {type: "number", format: "int32"}, value: 2147483648}).data.valid, false);
});

test("int64, float, double, password, and binary formats are available", () => {
  assert.equal(request("validate", {schema: {type: "number", format: "int64"}, value: 9007199254740991}).data.valid, true);
  assert.equal(request("validate", {schema: {type: "number", format: "float"}, value: 1.25}).data.valid, true);
  assert.equal(check("password", "anything").valid, true);
  assert.equal(check("binary", "raw payload").valid, true);
});

test("format validators reject values with the wrong JSON type", () => {
  const result = request("validate", {schema: {type: "string", format: "date"}, value: 42});
  assert.equal(result.data.valid, false);
  assert.equal(result.data.errors[0].keyword, "type");
});

test("formatMinimum and formatMaximum compare inclusive dates", () => {
  const schema = {type: "string", format: "date", formatMinimum: "2020-01-01", formatMaximum: "2020-12-31"};
  assert.equal(request("validate", {schema, value: "2020-01-01"}).data.valid, true);
  assert.equal(request("validate", {schema, value: "2021-01-01"}).data.valid, false);
});

test("exclusive format limits reject equal values", () => {
  const schema = {type: "string", format: "date", formatExclusiveMinimum: "2020-01-01", formatExclusiveMaximum: "2020-12-31"};
  assert.equal(request("validate", {schema, value: "2020-01-02"}).data.valid, true);
  assert.equal(request("validate", {schema, value: "2020-01-01"}).data.valid, false);
});

test("format limits pass through non-string data", () => {
  const schema = {type: "number", format: "date", formatMaximum: "2020-12-31"};
  assert.equal(request("validate", {schema, value: 7}).data.valid, true);
});

test("comparison keywords require a format", () => {
  const result = request("compile-error", {schema: {type: "string", formatMaximum: "2020-12-31"}});
  assert.equal(result.data.compiled, false);
});

test("keywords can be disabled", () => {
  const schema = {type: "string", format: "date", formatMaximum: "2020-01-01"};
  const result = request("compile-error", {schema, options: {keywords: false}});
  assert.equal(result.data.compiled, false);
});

test("full default options include comparison keywords", () => {
  const schema = {type: "string", format: "date", formatMaximum: "2020-01-01"};
  assert.equal(request("validate", {schema, value: "2021-01-01"}).data.valid, false);
});
