import assert from "node:assert/strict";
import { test } from "node:test";
import { callKoa } from "./test_client.mjs";

test("application defaults are stable", () => {
  assert.deepEqual(callKoa("app-json"), { subdomainOffset: 2, proxy: false, env: "development" });
});

test("application options are retained", () => {
  assert.deepEqual(callKoa("app-json", { options: { env: "test", proxy: true, subdomainOffset: 3 } }),
    { subdomainOffset: 3, proxy: true, env: "test" });
});

test("use rejects non-functions", () => {
  assert.deepEqual(callKoa("use-error"), { ok: true, name: "TypeError", message: "middleware must be a function!" });
});

test("middleware composes before and after in order", () => {
  const result = callKoa("http", { steps: [
    { kind: "record", value: "one" }, { kind: "record", value: "two" },
    { kind: "body", value: "ok" },
  ] });
  assert.equal(result.status, 200);
  assert.equal(result.body, "ok");
});

test("string body selects text content type", () => {
  const result = callKoa("http", { steps: [{ kind: "body", value: "hello" }] });
  assert.equal(result.status, 200);
  assert.equal(result.body, "hello");
  assert.match(result.headers["content-type"], /^text\/plain/);
});

test("object body is JSON encoded", () => {
  const result = callKoa("http", { steps: [{ kind: "body", value: { answer: 42, ok: true } }] });
  assert.equal(result.status, 200);
  assert.deepEqual(JSON.parse(result.body), { answer: 42, ok: true });
  assert.match(result.headers["content-type"], /json/);
});

test("status and response headers are applied", () => {
  const result = callKoa("http", { steps: [
    { kind: "status", value: 201 }, { kind: "header", name: "X-Test", value: "yes" },
    { kind: "body", value: "created" },
  ] });
  assert.equal(result.status, 201);
  assert.equal(result.headers["x-test"], "yes");
  assert.equal(result.body, "created");
});

test("null body produces an empty response", () => {
  const result = callKoa("http", { steps: [{ kind: "body", value: null }] });
  assert.equal(result.status, 204);
  assert.equal(result.body, "");
});

test("request accessors expose path and query", () => {
  const result = callKoa("http", { steps: [{ kind: "request-info" }], request: {
    path: "/users?active=1&tag=a&tag=b", headers: { Host: "api.example.test", Accept: "application/json" },
  } });
  const body = JSON.parse(result.body);
  assert.equal(body.path, "/users");
  assert.equal(body.querystring, "active=1&tag=a&tag=b");
  assert.deepEqual(body.query, { active: "1", tag: ["a", "b"] });
  assert.equal(body.hostname, "api.example.test");
});

test("proxy headers and subdomains are honored", () => {
  const result = callKoa("http", { options: { proxy: true, subdomainOffset: 2 }, steps: [{ kind: "request-info" }], request: {
    path: "/", headers: { Host: "ignored.test", "X-Forwarded-Host": "a.b.example.com", "X-Forwarded-Proto": "https", "X-Forwarded-For": "1.1.1.1, 2.2.2.2" },
  } });
  const body = JSON.parse(result.body);
  assert.equal(body.protocol, "https");
  assert.equal(body.secure, true);
  assert.equal(body.ip, "1.1.1.1");
  assert.deepEqual(body.ips, ["1.1.1.1", "2.2.2.2"]);
  assert.deepEqual(body.subdomains, ["b", "a"]);
});

test("accept negotiation is available on context", () => {
  const result = callKoa("http", { steps: [{ kind: "accepts" }], request: {
    headers: { Accept: "text/html, application/json;q=0.5" },
  } });
  assert.deepEqual(JSON.parse(result.body), { html: "html", json: "json" });
});

test("redirect sets location and a response body", () => {
  const result = callKoa("http", { steps: [{ kind: "redirect", url: "/login" }], request: {
    headers: { Accept: "text/plain" },
  } });
  assert.equal(result.status, 302);
  assert.equal(result.headers.location, "/login");
  assert.match(result.body, /Redirecting to \/login\./);
});

test("http errors use their status and exposed message", () => {
  const result = callKoa("http", { steps: [{ kind: "throw", status: 400, message: "bad input" }] });
  assert.equal(result.status, 400);
  assert.equal(result.body, "bad input");
});

test("cookies set a Set-Cookie header", () => {
  const result = callKoa("http", { steps: [{ kind: "cookie", name: "sid", value: "abc" }] });
  assert.equal(result.status, 404);
  assert.match(result.headers["set-cookie"][0], /^sid=abc;/);
});

test("async local storage exposes current context", () => {
  const result = callKoa("http", { options: { asyncLocalStorage: true }, steps: [{ kind: "current-context" }] });
  assert.deepEqual(JSON.parse(result.body), { same: true });
});

test("HEAD requests omit the body", () => {
  const result = callKoa("http", { steps: [{ kind: "body", value: "hello" }], request: { method: "HEAD" } });
  assert.equal(result.status, 200);
  assert.equal(result.body, "");
});

test("append combines repeated response headers", () => {
  const result = callKoa("http", { steps: [
    { kind: "header", name: "X-List", value: "one" },
    { kind: "append", name: "X-List", value: "two" },
    { kind: "body", value: "ok" },
  ] });
  assert.equal(result.headers["x-list"], "one, two");
});

