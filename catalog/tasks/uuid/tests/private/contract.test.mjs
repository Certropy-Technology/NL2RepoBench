import assert from "node:assert/strict";
import test from "node:test";

import { callUuid } from "./test_client.mjs";

const RANDOM_HEX = "00112233445566778899aabbccddeeff";
const NODE_HEX = "010203040506";
const TIMESTAMP = Date.UTC(2020, 0, 2, 3, 4, 5, 678);

test("validate recognizes canonical UUIDs and rejects malformed forms", () => {
  assert.equal(callUuid("validate", "0F5ABCD1-C194-47F3-905B-2DF7263A084B"), true);
  assert.equal(callUuid("validate", null), false);
  assert.equal(callUuid("validate", "00000000000000000000000000000000"), false);
  assert.equal(callUuid("validate", "00000000-0000-9000-8000-000000000000"), false);
});

test("version reports the UUID version nibble including NIL and MAX", () => {
  assert.equal(callUuid("version", "00000000-0000-0000-0000-000000000000"), 0);
  assert.equal(callUuid("version", "ffffffff-ffff-ffff-ffff-ffffffffffff"), 15);
  assert.equal(callUuid("version", "0f5abcd1-c194-47f3-905b-2df7263a084b"), 4);
});

test("parse returns network-order bytes and stringify reverses them", () => {
  const uuid = "0f5abcd1-c194-47f3-905b-2df7263a084b";
  assert.equal(callUuid("parse", uuid), "0f5abcd1c19447f3905b2df7263a084b");
  assert.equal(callUuid("stringify", "0f5ABCD1c19447F3905B2dF7263A084B"), uuid);
});

test("v3 produces the deterministic DNS namespace result", () => {
  assert.equal(
    callUuid("v3", {
      name: "www.example.com",
      namespace: "6ba7b810-9dad-11d1-80b4-00c04fd430c8",
    }),
    "5df41881-3aed-3515-88a7-2f4a814cf09e",
  );
});

test("v5 produces the deterministic URL namespace result", () => {
  assert.equal(
    callUuid("v5", {
      name: "www.example.com",
      namespace: "6ba7b811-9dad-11d1-80b4-00c04fd430c8",
    }),
    "b63cdfa4-3df9-568e-97ae-006c5b8fd652",
  );
});

test("v4 masks explicit random bytes as version four and RFC variant", () => {
  assert.equal(
    callUuid("v4", { random_hex: RANDOM_HEX }),
    "00112233-4455-4677-8899-aabbccddeeff",
  );
});

test("v1 uses explicit timestamp, sequence, node, and random fields", () => {
  assert.equal(
    callUuid("v1", {
      msecs: TIMESTAMP,
      nsecs: 42,
      clockseq: 0x1234,
      node_hex: NODE_HEX,
      random_hex: RANDOM_HEX,
    }),
    "896e350a-2d0c-11ea-9234-010203040506",
  );
});

test("v6 reorders explicit version one fields and preserves timestamp order", () => {
  const options = {
    msecs: TIMESTAMP,
    nsecs: 42,
    clockseq: 0x1234,
    node_hex: NODE_HEX,
    random_hex: RANDOM_HEX,
  };
  assert.equal(callUuid("v6", options), "1ea2d0c8-96e3-650a-9234-010203040506");
  assert.ok(callUuid("v6", { ...options, msecs: TIMESTAMP + 1 }) > callUuid("v6", options));
});

test("v7 uses explicit timestamp, sequence, and random fields", () => {
  assert.equal(
    callUuid("v7", {
      msecs: TIMESTAMP,
      seq: 0x12345678,
      random_hex: RANDOM_HEX,
    }),
    "016f6435-cf2e-7123-9159-e2bbccddeeff",
  );
});

test("v1ToV6 and v6ToV1 are inverse field reorderings", () => {
  const v1 = "896e350a-2d0c-11ea-9234-010203040506";
  const v6 = "1ea2d0c8-96e3-650a-9234-010203040506";
  assert.equal(callUuid("v1ToV6", v1), v6);
  assert.equal(callUuid("v6ToV1", v6), v1);
});

test("invalid namespace input preserves the documented error boundary", () => {
  assert.throws(
    () => callUuid("v5", { name: "example", namespace: "not-a-uuid" }),
    /candidate-call-failed/,
  );
});
