import { chmodSync, copyFileSync, mkdirSync } from "node:fs";
import { spawnSync } from "node:child_process";

const NODE = "/usr/local/bin/node";
const ADAPTER_DIR = "/tmp/cheerio-adapter";
const ADAPTER = `${ADAPTER_DIR}/candidate_adapter.mjs`;
const ADAPTER_SOURCE = "/tests/private/candidate_adapter.source";

function invoke(request) {
  const site = process.env.NODE_CANDIDATE_SITE;
  if (!site) throw new Error("candidate site is not configured");
  mkdirSync(ADAPTER_DIR, { recursive: true, mode: 0o755 });
  copyFileSync(ADAPTER_SOURCE, ADAPTER);
  chmodSync(ADAPTER, 0o555);
  const input = `${JSON.stringify(request)}\n`;
  if (Buffer.byteLength(input) > 64 * 1024) throw new Error("request exceeds the boundary");
  const result = spawnSync(
    "/usr/bin/timeout",
    [
      "--signal=TERM", "--kill-after=5s", "30s",
      "runuser", "-u", "candidate", "--",
      "/usr/bin/prlimit", "--cpu=60", "--nproc=32", "--nofile=128", "--",
      "env", "-i",
      "PATH=/usr/local/bin:/usr/bin:/bin",
      `HOME=${site}/home`, `TMPDIR=${site}/tmp`,
      "LC_ALL=C.UTF-8", "TERM=dumb", "CI=true", "FORCE_COLOR=0",
      NODE, "--no-addons", ADAPTER
    ],
    { cwd: site, input, encoding: "utf8", maxBuffer: 256 * 1024, timeout: 35_000 }
  );
  if (result.error) throw result.error;
  let payload;
  try {
    payload = JSON.parse(result.stdout);
  } catch {
    throw new Error(`candidate response malformed: ${result.stdout}`);
  }
  return payload;
}

export function call(request) {
  const response = invoke(request);
  if (!response.ok) throw new Error(`${response.exception_type ?? "Error"}: ${response.message ?? response.error}`);
  return response.value;
}

export function failure(request) {
  const response = invoke(request);
  if (response.ok) throw new Error("candidate call unexpectedly succeeded");
  return response;
}

export const query = (html, selector, result, steps = [], extra = {}) => call({
  operation: "query", html, selector, result, steps, ...extra
});
