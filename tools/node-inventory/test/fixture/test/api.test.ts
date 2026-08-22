import { test } from "node:test";
import assert from "node:assert/strict";
import { parse } from "../src/index.js";
test("parse trims input", () => assert.equal(parse(" value "), "value"));
test("parse rejects empty strict input", () =>
  assert.throws(() => parse("", { strict: true })));
