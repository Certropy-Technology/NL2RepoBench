import {spawnSync} from "node:child_process";
import {readFileSync} from "node:fs";
import {join} from "node:path";
import {pathToFileURL} from "node:url";

const NODE = "/usr/local/bin/node";
const MAX_REQUEST_BYTES = 64 * 1024;
const MAX_RESPONSE_BYTES = 256 * 1024;
const ADAPTER = String.raw`
import {readFileSync} from "node:fs";
import {join} from "node:path";
import {pathToFileURL} from "node:url";

function emit(payload, code = 0) {
  process.stdout.write(JSON.stringify(payload) + "\n");
  process.exit(code);
}

function fail(message) {
  throw new TypeError(message);
}

function object(value, label) {
  if (!value || typeof value !== "object" || Array.isArray(value)) fail(label + " must be an object");
  return value;
}

function string(value, label) {
  if (typeof value !== "string") fail(label + " must be a string");
  return value;
}

async function loadPackage() {
  const site = process.env.NODE_CANDIDATE_SITE;
  const root = join(site, "node_modules", "leven");
  const manifest = JSON.parse(readFileSync(join(root, "package.json"), "utf8"));
  const entry = typeof manifest.exports === "string" ? manifest.exports : manifest.main;
  if (typeof entry !== "string" || !entry.startsWith("./") || entry.includes("..")) fail("unsafe package entry");
  return {manifest, module: await import(pathToFileURL(join(root, entry)).href)};
}

try {
  const request = object(JSON.parse(process.env.LEVEN_REQUEST_JSON ?? "null"), "request");
  if (typeof request.id !== "string" || request.id.length < 1 || request.id.length > 128) fail("request id is invalid");
  const {manifest, module} = await loadPackage();
  if (request.operation === "metadata") {
    emit({id: request.id, data: {
      name: manifest.name,
      version: manifest.version,
      type: manifest.type,
      hasDefault: typeof module.default === "function",
      hasClosestMatch: typeof module.closestMatch === "function",
    }});
  }
  if (request.operation === "leven") {
    string(request.first, "first");
    string(request.second, "second");
    emit({id: request.id, data: module.default(request.first, request.second, request.options)});
  }
  if (request.operation === "closestMatch") {
    string(request.target, "target");
    if (!Array.isArray(request.candidates)) fail("candidates must be an array");
    for (const candidate of request.candidates) string(candidate, "candidate");
    emit({id: request.id, data: module.closestMatch(request.target, request.candidates, request.options)});
  }
  fail("unknown operation");
} catch (error) {
  emit({boundaryError: true, errorType: error?.constructor?.name ?? "Error", message: String(error?.message ?? error).slice(0, 512)}, 1);
}
`;

let sequence = 0;
export function callCandidate(request) {
  const site = process.env.NODE_CANDIDATE_SITE;
  if (!site) throw new Error("candidate site is not configured");
  const encoded = JSON.stringify({...request, id: `request-${++sequence}`});
  if (Buffer.byteLength(encoded) > MAX_REQUEST_BYTES) throw new Error("candidate request exceeds bound");
  const result = spawnSync(
    "/usr/bin/timeout",
    ["--signal=TERM", "--kill-after=5s", "30s", "runuser", "-u", "candidate", "--", "/usr/bin/prlimit", "--cpu=60", "--nproc=4096", "--nofile=128", "--", "env", "-i", "PATH=/usr/local/bin:/usr/bin:/bin", `HOME=${site}/home`, `TMPDIR=${site}/tmp`, `NODE_CANDIDATE_SITE=${site}`, `LEVEN_REQUEST_JSON=${encoded}`, NODE, "--no-addons", "--input-type=module", "--eval", ADAPTER],
    {cwd: site, encoding: "utf8", maxBuffer: MAX_RESPONSE_BYTES, timeout: 30_000},
  );
  if (result.error) throw result.error;
  let payload;
  try {
    payload = JSON.parse(result.stdout);
  } catch {
    throw new Error(`candidate response malformed: ${result.stdout}`);
  }
  if (result.status !== 0 || payload.boundaryError) throw new Error(`candidate-call-failed: ${payload.message ?? result.stderr}`);
  return payload;
}

export function distance(first, second, options) {
  return callCandidate({operation: "leven", first, second, options}).data;
}

export function closest(target, candidates, options) {
  return callCandidate({operation: "closestMatch", target, candidates, options}).data;
}
