import { readFileSync } from "node:fs";
import { createRequire } from "node:module";
import { join } from "node:path";
import { pathToFileURL } from "node:url";

const MAX_REQUEST_BYTES = 64 * 1024;
const MAX_RESPONSE_BYTES = 256 * 1024;
const NAME_PATTERN = /^[A-Za-z0-9_.@/-]{1,128}$/;

function emit(payload, code = 0) {
  const encoded = JSON.stringify(payload);
  if (Buffer.byteLength(encoded) > MAX_RESPONSE_BYTES) {
    process.stderr.write("candidate response exceeds the bound\n");
    process.exit(70);
  }
  process.stdout.write(`${encoded}\n`);
  process.exit(code);
}

function request() {
  const data = readFileSync(0);
  if (data.byteLength > MAX_REQUEST_BYTES) {
    emit({ ok: false, error: "request-too-large" }, 64);
  }
  let payload;
  try {
    payload = JSON.parse(data.toString("utf8"));
  } catch {
    emit({ ok: false, error: "malformed-json" }, 64);
  }
  if (!payload || typeof payload !== "object" || Array.isArray(payload)) {
    emit({ ok: false, error: "request-must-be-object" }, 64);
  }
  const packageName = payload.package;
  const exportName = payload.export;
  if (typeof packageName !== "string" || !NAME_PATTERN.test(packageName)) {
    emit({ ok: false, error: "package-name-not-allowlisted" }, 64);
  }
  if (typeof exportName !== "string" || !NAME_PATTERN.test(exportName)) {
    emit({ ok: false, error: "export-name-not-allowlisted" }, 64);
  }
  if (process.env.NODE_ALLOWED_PACKAGE && packageName !== process.env.NODE_ALLOWED_PACKAGE) {
    emit({ ok: false, error: "package-name-not-allowlisted" }, 64);
  }
  return { packageName, exportName, args: payload.args ?? [] };
}

async function main() {
  const { packageName, exportName, args } = request();
  if (!Array.isArray(args) || args.length > 32) {
    emit({ ok: false, error: "args-not-allowlisted" }, 64);
  }
  try {
    const require = createRequire(pathToFileURL(`${process.cwd()}/package.json`));
    let candidate;
    try {
      candidate = require(packageName);
    } catch (error) {
      if (error?.code !== "ERR_REQUIRE_ESM" && error?.code !== "ERR_PACKAGE_PATH_NOT_EXPORTED") throw error;
      const packageRoot = join(process.cwd(), "node_modules", packageName);
      const packageManifest = JSON.parse(readFileSync(join(packageRoot, "package.json"), "utf8"));
      const exports = packageManifest.exports;
      const rootExport = exports?.["."];
      const entry = typeof exports === "string"
        ? exports
        : typeof rootExport === "string"
          ? rootExport
          : rootExport?.import ?? exports?.import ?? packageManifest.module ?? packageManifest.main;
      if (typeof entry !== "string" || !entry.startsWith("./") || entry.includes("..")) {
        throw new Error("allowlisted package has no safe ESM entry");
      }
      candidate = await import(pathToFileURL(join(packageRoot, entry)).href);
    }
    const segments = exportName.split(".");
    if (segments.some((segment) => (
      !segment
      || segment === "__proto__"
      || segment === "prototype"
      || segment === "constructor"
    ))) {
      emit({ ok: false, error: "export-name-not-allowlisted" }, 64);
    }
    let value = candidate;
    for (const segment of segments) {
      if (
        value === null
        || (typeof value !== "object" && typeof value !== "function")
        || !Object.prototype.hasOwnProperty.call(value, segment)
      ) {
        emit({ ok: false, error: "export-is-not-callable" }, 65);
      }
      value = value[segment];
    }
    if (typeof value !== "function") {
      emit({ ok: false, error: "export-is-not-callable" }, 65);
    }
    const result = await value(...args);
    emit({ ok: true, value: result, args });
  } catch (error) {
    emit({
      ok: false,
      error: "candidate-call-failed",
      exception_type: error?.constructor?.name ?? "Error",
      message: String(error?.message ?? error),
    }, 1);
  }
}

await main();
