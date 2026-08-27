import {spawnSync} from "node:child_process";

const NODE = "/usr/local/bin/node";
const MAX_REQUEST_BYTES = 64 * 1024;
const MAX_RESPONSE_BYTES = 256 * 1024;

const ADAPTER = String.raw`
import {readFileSync} from "node:fs";
import {createRequire} from "node:module";
import {join} from "node:path";
import {pathToFileURL} from "node:url";

const MAX_DEPTH = 8;
const MAX_OBJECT_KEYS = 32;
const MAX_ARRAY_ITEMS = 128;

function emit(payload, code = 0) {
  process.stdout.write(JSON.stringify(payload) + "\n");
  process.exit(code);
}

function fail(message) {
  throw new TypeError(message);
}

function plainObject(value, label) {
  if (!value || typeof value !== "object" || Array.isArray(value)) fail(label + " must be an object");
  return value;
}

function finiteInteger(value, label, minimum = 0) {
  if (!Number.isSafeInteger(value) || value < minimum) fail(label + " must be an integer");
  return value;
}

function build(z, descriptor, depth = 0) {
  plainObject(descriptor, "schema");
  if (depth > MAX_DEPTH) fail("schema depth exceeds limit");
  const type = descriptor.type;
  if (typeof type !== "string") fail("schema type is required");

  if (type === "string") {
    let schema = z.string();
    if (descriptor.minLength !== undefined) schema = schema.min(finiteInteger(descriptor.minLength, "minLength"));
    if (descriptor.maxLength !== undefined) schema = schema.max(finiteInteger(descriptor.maxLength, "maxLength"));
    if (descriptor.length !== undefined) schema = schema.length(finiteInteger(descriptor.length, "length"));
    if (descriptor.email === true) schema = schema.email();
    if (descriptor.trim === true) schema = schema.trim();
    if (descriptor.toLowerCase === true) schema = schema.toLowerCase();
    return schema;
  }
  if (type === "number") {
    let schema = z.number();
    if (descriptor.int === true) schema = schema.int();
    if (descriptor.min !== undefined) {
      if (typeof descriptor.min !== "number" || !Number.isFinite(descriptor.min)) fail("min must be finite");
      schema = schema.min(descriptor.min);
    }
    if (descriptor.max !== undefined) {
      if (typeof descriptor.max !== "number" || !Number.isFinite(descriptor.max)) fail("max must be finite");
      schema = schema.max(descriptor.max);
    }
    if (descriptor.positive === true) schema = schema.positive();
    if (descriptor.nonnegative === true) schema = schema.nonnegative();
    return schema;
  }
  if (type === "boolean") return z.boolean();
  if (type === "literal") {
    const value = descriptor.value;
    if (!(value === null || ["string", "number", "boolean"].includes(typeof value))) fail("literal must be JSON scalar");
    if (typeof value === "number" && !Number.isFinite(value)) fail("literal number must be finite");
    return z.literal(value);
  }
  if (type === "enum") {
    if (!Array.isArray(descriptor.values) || descriptor.values.length < 1 || descriptor.values.length > 32) fail("enum values are invalid");
    if (descriptor.values.some((value) => typeof value !== "string") || new Set(descriptor.values).size !== descriptor.values.length) fail("enum values are invalid");
    return z.enum(descriptor.values);
  }
  if (type === "array") {
    let schema = z.array(build(z, descriptor.item, depth + 1));
    if (descriptor.minLength !== undefined) schema = schema.min(finiteInteger(descriptor.minLength, "minLength"));
    if (descriptor.maxLength !== undefined) schema = schema.max(finiteInteger(descriptor.maxLength, "maxLength"));
    if (descriptor.length !== undefined) schema = schema.length(finiteInteger(descriptor.length, "length"));
    return schema;
  }
  if (type === "object") {
    const properties = plainObject(descriptor.properties, "properties");
    const keys = Object.keys(properties);
    if (keys.length > MAX_OBJECT_KEYS) fail("too many object keys");
    const shape = Object.fromEntries(keys.map((key) => [key, build(z, properties[key], depth + 1)]));
    if (descriptor.unknownKeys === undefined || descriptor.unknownKeys === "strip") return z.object(shape);
    if (descriptor.unknownKeys === "strict") return z.strictObject(shape);
    if (descriptor.unknownKeys === "passthrough") return z.looseObject(shape);
    fail("unknownKeys is invalid");
  }
  if (type === "union") {
    if (!Array.isArray(descriptor.options) || descriptor.options.length < 2 || descriptor.options.length > 16) fail("union options are invalid");
    return z.union(descriptor.options.map((item) => build(z, item, depth + 1)));
  }
  if (type === "optional") return build(z, descriptor.inner, depth + 1).optional();
  if (type === "nullable") return build(z, descriptor.inner, depth + 1).nullable();
  if (type === "default") return build(z, descriptor.inner, depth + 1).default(descriptor.value);
  fail("unsupported schema type");
}

async function loadCandidate() {
  const require = createRequire(pathToFileURL(join(process.cwd(), "package.json")));
  try {
    return require("zod");
  } catch (error) {
    if (error?.code !== "ERR_REQUIRE_ESM" && error?.code !== "ERR_PACKAGE_PATH_NOT_EXPORTED") throw error;
    const packageRoot = join(process.cwd(), "node_modules", "zod");
    const manifest = JSON.parse(readFileSync(join(packageRoot, "package.json"), "utf8"));
    const exports = manifest.exports;
    const entry = typeof exports === "string"
      ? exports
      : exports?.["."]?.import ?? exports?.import ?? manifest.module ?? manifest.main;
    if (typeof entry !== "string" || !entry.startsWith("./") || entry.includes("..")) fail("package has no safe root export");
    return import(pathToFileURL(join(packageRoot, entry)).href);
  }
}

try {
  const request = JSON.parse(process.env.ZOD_REQUEST_JSON ?? "null");
  plainObject(request, "request");
  if (typeof request.id !== "string" || request.id.length < 1 || request.id.length > 128) fail("request id is invalid");
  const candidate = await loadCandidate();
  const z = candidate.z ?? candidate.default ?? candidate;
  if (!z || typeof z !== "object") fail("root z export is unavailable");
  if (request.operation === "inventory") {
    emit({id: request.id, success: true, data: {
      hasNamedZ: typeof candidate.z === "object",
      hasDefaultZAlias: candidate.default === candidate.z,
      constructors: ["string", "number", "boolean", "literal", "enum", "array", "object", "strictObject", "looseObject", "union"]
        .filter((name) => typeof z[name] === "function"),
    }});
  }
  if (request.operation !== undefined && request.operation !== "validate") fail("operation is invalid");
  const schema = build(z, request.schema);
  const result = schema.safeParse(request.value);
  if (result.success) emit({id: request.id, success: true, data: result.data});
  const issues = result.error.issues.map((issue) => ({code: issue.code, path: issue.path, message: issue.message}));
  emit({id: request.id, success: false, issues});
} catch (error) {
  emit({success: false, boundaryError: true, errorType: error?.constructor?.name ?? "Error", message: String(error?.message ?? error).slice(0, 512)}, 1);
}
`;

export function callCandidate(request) {
  const site = process.env.NODE_CANDIDATE_SITE;
  if (!site) throw new Error("candidate site is not configured");
  const encoded = JSON.stringify(request);
  if (Buffer.byteLength(encoded) > MAX_REQUEST_BYTES) throw new Error("candidate request exceeds bound");
  const result = spawnSync(
    "/usr/bin/timeout",
    [
      "--signal=TERM",
      "--kill-after=5s",
      "30s",
      "runuser",
      "-u",
      "candidate",
      "--",
      "/usr/bin/prlimit",
      "--cpu=60",
      "--nproc=4096",
      "--nofile=128",
      "--",
      "env",
      "-i",
      "PATH=/usr/local/bin:/usr/bin:/bin",
      `HOME=${site}/home`,
      `TMPDIR=${site}/tmp`,
      `ZOD_REQUEST_JSON=${encoded}`,
      NODE,
      "--no-addons",
      "--input-type=module",
      "--eval",
      ADAPTER,
    ],
    {cwd: site, encoding: "utf8", maxBuffer: MAX_RESPONSE_BYTES, timeout: 30_000},
  );
  if (result.error) throw result.error;
  let payload;
  try {
    payload = JSON.parse(result.stdout);
  } catch {
    throw new Error(`candidate response malformed: ${result.stdout}`);
  }
  if (result.status !== 0 || payload.boundaryError) {
    throw new Error(`candidate-call-failed: ${payload.message ?? result.stderr}`);
  }
  return payload;
}
