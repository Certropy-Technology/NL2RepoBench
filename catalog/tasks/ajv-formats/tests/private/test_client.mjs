import {spawnSync} from "node:child_process";

const NODE = "/usr/local/bin/node";
const MAX_REQUEST_BYTES = 64 * 1024;
const MAX_RESPONSE_BYTES = 256 * 1024;

const ADAPTER = String.raw`
const {createRequire} = require("node:module");
const {readFileSync} = require("node:fs");
const {join} = require("node:path");

function fail(message) { throw new TypeError(message); }
function object(value, label) {
  if (!value || typeof value !== "object" || Array.isArray(value)) fail(label + " must be an object");
  return value;
}
function emit(value, code = 0) {
  process.stdout.write(JSON.stringify(value) + "\n");
  process.exit(code);
}
function load(name) {
  const require = createRequire(join(process.cwd(), "package.json"));
  return require(name);
}
try {
  const request = object(JSON.parse(process.env.AJV_FORMATS_REQUEST_JSON ?? "null"), "request");
  if (typeof request.id !== "string" || request.id.length < 1 || request.id.length > 128) fail("invalid request id");
  const AjvModule = load("ajv");
  const Ajv = AjvModule.default ?? AjvModule;
  const pluginModule = load("ajv-formats");
  const addFormats = pluginModule.default ?? pluginModule;
  if (typeof Ajv !== "function" || typeof addFormats !== "function") fail("package exports are unavailable");
  if (request.operation === "inventory") {
    const manifest = JSON.parse(readFileSync(join(process.cwd(), "node_modules", "ajv-formats", "package.json"), "utf8"));
    const names = ["date", "time", "date-time", "iso-time", "iso-date-time", "duration", "uri", "uri-reference", "uri-template", "url", "email", "hostname", "ipv4", "ipv6", "regex", "uuid", "json-pointer", "json-pointer-uri-fragment", "relative-json-pointer", "byte", "int32", "int64", "float", "double", "password", "binary"];
    emit({id: request.id, success: true, data: {name: manifest.name, version: manifest.version, main: manifest.main, formats: names, hasGet: typeof addFormats.get === "function"}});
  }
  if (!["validate", "get", "compile-error"].includes(request.operation)) fail("unsupported operation");
  if (request.operation === "get") {
    const definition = addFormats.get(request.name, request.mode ?? "full");
    emit({id: request.id, success: true, data: {name: request.name, mode: request.mode ?? "full", definitionType: definition instanceof RegExp ? "regexp" : typeof definition, hasCompare: Boolean(definition && typeof definition === "object" && typeof definition.compare === "function"), validateType: definition instanceof RegExp ? "regexp" : typeof definition?.validate}});
  }
  const ajv = new Ajv({allErrors: true, strictTypes: false, validateFormats: request.validateFormats ?? true});
  const options = request.options;
  if (Array.isArray(options)) addFormats(ajv, options);
  else addFormats(ajv, options ?? {keywords: true});
  let compiled;
  try {
    compiled = ajv.compile(object(request.schema, "schema"));
  } catch (error) {
    if (request.operation === "compile-error") emit({id: request.id, success: true, data: {compiled: false, message: String(error?.message ?? error).slice(0, 512)}});
    throw error;
  }
  if (request.operation === "compile-error") emit({id: request.id, success: true, data: {compiled: true}});
  const valid = compiled(request.value);
  emit({id: request.id, success: true, data: {valid, errors: compiled.errors ? compiled.errors.map((error) => ({keyword: error.keyword, instancePath: error.instancePath, params: error.params})) : null}});
} catch (error) {
  emit({success: false, boundaryError: true, message: String(error?.message ?? error).slice(0, 512)}, 1);
}
`;

export function callCandidate(request) {
  const site = process.env.NODE_CANDIDATE_SITE;
  if (!site) throw new Error("candidate site is not configured");
  const encoded = JSON.stringify(request);
  if (Buffer.byteLength(encoded) > MAX_REQUEST_BYTES) throw new Error("request exceeds bound");
  const result = spawnSync("/usr/bin/timeout", [
    "--signal=TERM", "--kill-after=5s", "30s", "runuser", "-u", "candidate", "--",
    "/usr/bin/prlimit", "--cpu=60", "--nproc=4096", "--nofile=128", "--",
    "env", "-i", "PATH=/usr/local/bin:/usr/bin:/bin", `HOME=${site}/home`, `TMPDIR=${site}/tmp`,
    `AJV_FORMATS_REQUEST_JSON=${encoded}`, NODE, "--no-addons", "--eval", ADAPTER,
  ], {cwd: site, encoding: "utf8", maxBuffer: MAX_RESPONSE_BYTES, timeout: 30_000});
  if (result.error) throw result.error;
  let payload;
  try { payload = JSON.parse(result.stdout); } catch { throw new Error(`malformed response: ${result.stdout}`); }
  if (result.status !== 0 || payload.boundaryError) throw new Error(`candidate-call-failed: ${payload.message ?? result.stderr}`);
  return payload;
}
