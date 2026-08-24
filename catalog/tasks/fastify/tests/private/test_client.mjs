import { spawnSync } from "node:child_process";
import { readFileSync, writeFileSync } from "node:fs";

const entry = `
const fastify = require("fastify");

function responseShape(response) {
  return {
    statusCode: response.statusCode,
    headers: response.headers,
    body: response.body,
    json: response.headers["content-type"]?.includes("json") ? response.json() : null,
  };
}

async function main(input) {
  const app = fastify({ logger: false });
  let result;
  switch (input.op) {
    case "basic":
      app.get("/hello", async () => ({ hello: "world" }));
      result = responseShape(await app.inject({ method: "GET", url: "/hello" }));
      break;
    case "params":
      app.get("/users/:id", (request) => ({ id: request.params.id, query: request.query }));
      result = responseShape(await app.inject({ method: "GET", url: "/users/42?active=true" }));
      break;
    case "post":
      app.post("/echo", (request) => ({ body: request.body, contentType: request.headers["content-type"] }));
      result = responseShape(await app.inject({
        method: "POST",
        url: "/echo",
        headers: { "content-type": "application/json" },
        payload: { message: "héllo", count: 2 },
      }));
      break;
    case "methods":
      app.route({ method: "PUT", url: "/items/:id", handler: (request, reply) => reply.code(202).send({ id: request.params.id, method: request.raw.method }) });
      app.delete("/items/:id", (request, reply) => reply.code(204).send());
      result = {
        put: responseShape(await app.inject({ method: "PUT", url: "/items/a" })),
        del: responseShape(await app.inject({ method: "DELETE", url: "/items/a" })),
      };
      break;
    case "precedence":
      app.get("/files/*", () => ({ route: "wildcard" }));
      app.get("/files/:name", (request) => ({ route: "param", name: request.params.name }));
      app.get("/files/readme", () => ({ route: "static" }));
      result = {
        static: responseShape(await app.inject({ method: "GET", url: "/files/readme" })),
        param: responseShape(await app.inject({ method: "GET", url: "/files/notes" })),
        wildcard: responseShape(await app.inject({ method: "GET", url: "/files/a/b" })),
      };
      break;
    case "hooks": {
      const events = [];
      for (const name of ["onRequest", "preParsing", "preValidation", "preHandler"]) {
        app.addHook(name, async () => { events.push(name); });
      }
      app.addHook("onSend", async () => { events.push("onSend"); });
      app.addHook("onResponse", async () => { events.push("onResponse"); });
      app.get("/hooked", async () => { events.push("handler"); return { ok: true }; });
      const response = await app.inject({ method: "GET", url: "/hooked" });
      result = { response: responseShape(response), events };
      break;
    }
    case "schema": {
      app.get("/search", {
        schema: { querystring: { type: "object", required: ["q"], properties: { q: { type: "string", minLength: 3 } }, additionalProperties: false } },
      }, (request) => ({ q: request.query.q }));
      result = {
        valid: responseShape(await app.inject({ method: "GET", url: "/search?q=fastify" })),
        invalid: responseShape(await app.inject({ method: "GET", url: "/search?q=x" })),
      };
      break;
    }
    case "response-schema":
      app.get("/typed", { schema: { response: { 200: { type: "object", required: ["ok"], properties: { ok: { type: "boolean" } } } } } }, () => ({ ok: true, ignored: "removed" }));
      result = responseShape(await app.inject({ method: "GET", url: "/typed" }));
      break;
    case "error":
      app.setErrorHandler((error, request, reply) => reply.code(418).send({ handled: true, message: error.message }));
      app.get("/boom", async () => { throw new Error("boom"); });
      result = responseShape(await app.inject({ method: "GET", url: "/boom" }));
      break;
    case "not-found":
      app.setNotFoundHandler((request, reply) => reply.code(404).send({ missing: request.url }));
      result = responseShape(await app.inject({ method: "GET", url: "/missing" }));
      break;
    case "plugin":
      app.get("/root", () => ({ scope: "root" }));
      await app.register(async (instance, options) => {
        instance.addHook("preHandler", async (request) => { request.pluginSeen = true; });
        instance.get("/item", (request) => ({ scope: options.scope, pluginSeen: request.pluginSeen }));
      }, { prefix: "/v1", scope: "child" });
      result = {
        child: responseShape(await app.inject({ method: "GET", url: "/v1/item" })),
        root: responseShape(await app.inject({ method: "GET", url: "/root" })),
      };
      break;
    case "lifecycle":
      app.get("/ready", () => ({ ready: true }));
      result = { hasRoute: app.hasRoute({ method: "GET", url: "/ready" }) };
      await app.ready();
      result.response = responseShape(await app.inject({ method: "GET", url: "/ready" }));
      break;
    default:
      throw new Error("unknown operation: " + input.op);
  }
  await app.close();
  return result;
}

let input;
try { input = JSON.parse(process.argv[2]); } catch (error) { process.stdout.write(JSON.stringify({ ok: false, message: error.message })); process.exit(1); }
main(input).then((value) => process.stdout.write(JSON.stringify({ ok: true, value }) + "\\n"), (error) => process.stdout.write(JSON.stringify({ ok: false, type: error.constructor?.name, message: error.message }) + "\\n"));
`;

export function call(input, { expectError = false } = {}) {
  const site = process.env.NODE_CANDIDATE_SITE;
  if (!site) throw new Error("candidate site is not configured");
  const entryPath = `${site}/.task-candidate-entry.cjs`;
  writeFileSync(entryPath, entry, { mode: 0o444 });
  const candidateAvailable = !process.env.NODE_FORCE_DIRECT && readFileSync("/etc/passwd", "utf8").includes("\ncandidate:");
  const command = candidateAvailable ? "/usr/sbin/runuser" : process.execPath;
  const commandArgs = candidateAvailable
    ? ["-u", "candidate", "--", "env", "-i", "PATH=/usr/local/bin:/usr/bin:/bin", `HOME=${site}/home`, `TMPDIR=${site}/tmp`, process.execPath, entryPath, JSON.stringify(input)]
    : [entryPath, JSON.stringify(input)];
  const result = spawnSync(
    "/usr/bin/timeout",
    ["--signal=TERM", "--kill-after=5s", "30s", command, ...commandArgs],
    { cwd: site, env: { PATH: "/usr/local/bin:/usr/bin:/bin", HOME: `${site}/home`, TMPDIR: `${site}/tmp`, NODE_OPTIONS: "" }, encoding: "utf8", timeout: 30_000, maxBuffer: 256 * 1024 },
  );
  if (result.error) throw result.error;
  let response;
  try { response = JSON.parse(result.stdout); } catch { throw new Error(`malformed candidate response (exit ${result.status}): ${result.stdout} ${result.stderr}`); }
  if (expectError) return response;
  if (!response.ok) throw new Error(`${response.type ?? "candidate-call-failed"}: ${response.message}`);
  return response.value;
}
