import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";

const candidateSite = process.env.NODE_CANDIDATE_SITE;
const MAX_RESPONSE_BYTES = 256 * 1024;
const CALL_TIMEOUT_MS = 2_000;

if (!candidateSite) throw new Error("NODE_CANDIDATE_SITE is required");

const childProgram = String.raw`
const fs = require("node:fs");
const payload = JSON.parse(fs.readFileSync(0, "utf8"));
const parse = require("minimist");
if (payload.operation === "export-probe") {
  process.stdout.write(JSON.stringify({type: typeof parse}) + "\n");
} else {
  const result = parse(payload.args, payload.options);
  if (payload.operation === "prototype-probe") {
    process.stdout.write(JSON.stringify({
      result,
      objectPrototypeSafe: ({}).polluted === undefined,
      functionPrototypeSafe: (function () {}).polluted === undefined,
      stringPrototypeSafe: "text".polluted === undefined,
    }) + "\n");
  } else {
    process.stdout.write(JSON.stringify(result) + "\n");
  }
}
`;

function invoke(operation, args = [], options = {}) {
  const result = spawnSync(
    "/usr/sbin/runuser",
    ["-u", "candidate", "--", "/usr/local/bin/node", "--no-addons", "-e", childProgram],
    {
      cwd: candidateSite,
      env: {
        PATH: "/usr/local/bin:/usr/bin:/bin",
        HOME: `${candidateSite}/home`,
        TMPDIR: `${candidateSite}/tmp`,
      },
      input: JSON.stringify({ operation, args, options }),
      encoding: "utf8",
      timeout: CALL_TIMEOUT_MS,
      maxBuffer: MAX_RESPONSE_BYTES,
    },
  );
  if (result.error) throw new Error(`candidate call failed: ${result.error.message}`);
  if (result.status !== 0) throw new Error(`candidate call exited with ${result.status}`);
  if (Buffer.byteLength(result.stdout) > MAX_RESPONSE_BYTES) {
    throw new Error("candidate response exceeds the bound");
  }
  try {
    return JSON.parse(result.stdout);
  } catch {
    throw new Error("candidate response is not JSON");
  }
}

export function parse(args, options) {
  assert.ok(Array.isArray(args));
  return invoke("parse", args, options ?? {});
}

export function prototypeProbe(args, options) {
  return invoke("prototype-probe", args, options ?? {});
}

export function exportProbe() {
  return invoke("export-probe");
}
