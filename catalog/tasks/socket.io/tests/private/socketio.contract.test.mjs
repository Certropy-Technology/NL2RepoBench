import assert from "node:assert/strict";
import test from "node:test";

import { runScenario } from "./test_client.mjs";

test("package root exports the three public runtime classes", () => {
  const result = runScenario("exports");
  assert.deepEqual(result.keys, ["Namespace", "Server", "Socket"]);
  assert.deepEqual(result.types, { Server: "function", Namespace: "function", Socket: "function" });
});

test("default namespace connects, emits events, and acknowledges client events", () => {
  const result = runScenario("basic");
  assert.equal(result.connectedType, 0);
  assert.equal(result.connectedNamespace, "/");
  assert.deepEqual(result.welcome, ["welcome", { connected: true }]);
  assert.equal(result.ackValue, "hello");
  assert.equal(result.ackHasId, true);
});

test("namespace middleware accepts auth and returns connect errors", () => {
  const result = runScenario("namespaceMiddleware");
  assert.equal(result.accepted, true);
  assert.deepEqual(result.ready, ["ready", "/admin"]);
  assert.equal(result.rejectedType, 4);
  assert.equal(result.rejectedMessage, "forbidden");
});

test("room broadcasts target joined sockets only", () => {
  const result = runScenario("rooms");
  assert.equal(result.value, 42);
  assert.equal(result.redReceived, false);
  assert.ok(result.rooms.includes("blue"));
});

test("socket.broadcast excludes the sending socket", () => {
  const result = runScenario("broadcast");
  assert.equal(result.value, "peer-only");
  assert.equal(result.senderReceived, false);
});

test("room inventory and bulk join/leave APIs stay consistent", () => {
  const result = runScenario("socketInventory");
  assert.deepEqual(result, { fetched: 2, ids: 2, joined: 2, left: 0, roomsAreSets: true });
});

test("server-to-client acknowledgements return the client value", () => {
  const result = runScenario("serverAck");
  assert.deepEqual(result.question, ["question", 21]);
  assert.deepEqual(result.callback, { error: null, value: "answer" });
});

test("socket timeout reports a missing acknowledgement", () => {
  const result = runScenario("ackTimeout");
  assert.equal(result.timedOut, true);
  assert.match(result.message, /operation has timed out/i);
});

test("disconnectSockets closes matching clients and updates inventory", () => {
  const result = runScenario("disconnectSockets");
  assert.equal(result.reason, "server namespace disconnect");
  assert.equal(result.remaining, 0);
});

test("regular-expression parent namespaces create matching children only", () => {
  const result = runScenario("dynamicNamespace");
  assert.equal(result.allowed, 0);
  assert.equal(result.tenant, "/tenant-42");
  assert.equal(result.denied, 4);
  assert.match(result.deniedMessage, /invalid namespace/i);
});

test("custom Engine.IO paths are honored", () => {
  const result = runScenario("customPath");
  assert.equal(result.connected, 0);
  assert.equal(result.configuredPath, "/realtime");
  assert.equal(result.wrongPathStatus, 404);
  assert.equal(result.listening, true);
});

test("server close invokes its callback and closes the HTTP listener", () => {
  const result = runScenario("closeLifecycle");
  assert.deepEqual(result, { callbacks: 1, listening: false, sockets: 0 });
});
