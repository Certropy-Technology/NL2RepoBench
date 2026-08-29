import { spawnSync } from "node:child_process";
import { Buffer } from "node:buffer";
import { createRequire } from "node:module";
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join, resolve } from "node:path";

const adapter = fileURLToPath(import.meta.url);
const maxMessage = 4096;

const site = resolve(process.env.NODE_CANDIDATE_SITE ?? "");
if (!site) process.exit(64);

function requireCandidate(root) {
  root = resolve(root);
  const packageRoot = `${root}/node_modules/json-parse-even-better-errors`;
  const manifest = JSON.parse(readFileSync(`${packageRoot}/package.json`, "utf8"));
  if (manifest.name !== "json-parse-even-better-errors") throw new Error("wrong package name");
  return createRequire(`${root}/package.json`)(packageRoot);
}

function decode(value) {
  if (!value || typeof value !== "object" || Array.isArray(value)) return value;
  if (value.type === "buffer") return Buffer.from(value.base64, "base64");
  if (value.type === "undefined") return undefined;
  if (value.type === "empty-array") return [];
  if (value.type === "map") return new Map();
  if (value.type === "date") return new Date(0);
  if (Object.hasOwn(value, "value")) return value.value;
  return value.value;
}

function reviverFor(name) {
  if (name === "deleteSecret") return (key, value) => key === "secret" ? undefined : value;
  if (name === "doubleNumbers") return (key, value) => typeof value === "number" ? value * 2 : value;
  return undefined;
}

function encode(value) {
  if (value === undefined) return { type: "undefined" };
  if (value === null || typeof value !== "object") return value;
  return {
    json: JSON.stringify(value),
    indent: value[Symbol.for("indent")],
    newline: value[Symbol.for("newline")],
  };
}

function handle(request) {
  const parseJson = requireCandidate(site);
  const raw = decode(request.value);
  const reviver = reviverFor(request.reviver);
  if (request.operation === "parse" || request.operation === "noExceptions") {
    const value = request.operation === "parse"
      ? parseJson(raw, reviver, request.context)
      : parseJson.noExceptions(raw, reviver);
    return encode(value);
  }
  if (request.operation === "class") {
    const error = new Error(request.errorMessage ?? "native");
    const parsed = new parseJson.JSONParseError(error, request.text ?? "sample", request.context);
    return {
      isSyntaxError: parsed instanceof SyntaxError,
      name: parsed.name,
      code: parsed.code,
      position: parsed.position,
      message: parsed.message,
      sameError: parsed.systemError === error,
      tag: parsed[Symbol.toStringTag],
    };
  }
  throw new Error("unknown operation");
}

if (process.argv[1] === adapter) {
  let input = "";
  process.stdin.setEncoding("utf8");
  process.stdin.on("data", (chunk) => { input += chunk; });
  process.stdin.on("end", () => {
    try {
      process.stdout.write(JSON.stringify({ ok: true, value: handle(JSON.parse(input)) }) + "\n");
    } catch (error) {
      process.stdout.write(JSON.stringify({
        ok: false,
        error_type: error?.constructor?.name ?? "Error",
        name: error?.name ?? "Error",
        code: error?.code,
        position: error?.position,
        message: String(error?.message ?? error).slice(0, 4096),
        systemError: error?.systemError?.constructor?.name,
      }) + "\n");
      process.exitCode = 1;
    }
  });
}

export function request(operation, value, options = {}) {
  const payload = JSON.stringify({ operation, value, ...options });
  if (Buffer.byteLength(payload) > 65536) throw new Error("request exceeds bound");
  const result = spawnSync(process.execPath, ["--no-addons", adapter], {
    input: `${payload}\n`,
    cwd: process.env.NODE_CANDIDATE_SITE,
    env: {
      PATH: "/usr/local/bin:/usr/bin:/bin",
      HOME: "/tmp",
      NODE_CANDIDATE_SITE: site,
      NODE_TEST_CLIENT: undefined,
      NODE_OPTIONS: undefined,
      NODE_PATH: undefined,
    },
    encoding: "utf8",
    timeout: 5000,
    maxBuffer: 262144,
  });
  const line = (result.stdout ?? "").trim().split(/\r?\n/).at(-1) ?? "";
  if (result.error && !line) throw result.error;
  if (Buffer.byteLength(line) > 262144) throw new Error("response exceeds bound");
  const response = JSON.parse(line);
  if (!response.ok) {
    const error = new Error(String(response.message ?? "candidate error").slice(0, maxMessage));
    Object.assign(error, response);
    throw error;
  }
  return response.value;
}
