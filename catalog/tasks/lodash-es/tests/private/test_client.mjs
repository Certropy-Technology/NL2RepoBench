import { spawnSync } from "node:child_process";

const RUNNER = "/tests/runtime/node/candidate_runner.mjs";
const MAX_REQUEST_BYTES = 64 * 1024;

function request(exportName, args) {
  const site = process.env.NODE_CANDIDATE_SITE;
  if (!site) throw new Error("candidate site is not configured");
  const input = JSON.stringify({ package: "lodash-es", export: exportName, args });
  if (Buffer.byteLength(input) > MAX_REQUEST_BYTES) throw new Error("request exceeds bound");
  const result = spawnSync(
    "/usr/bin/timeout",
    ["--signal=TERM", "--kill-after=5s", "30s", "runuser", "-u", "candidate", "--",
      "/usr/bin/prlimit", "--cpu=60", "--nproc=32", "--nofile=128", "--",
      "env", "-i", "PATH=/usr/local/bin:/usr/bin:/bin", `HOME=${site}/home`,
      `TMPDIR=${site}/tmp`, "NODE_ALLOWED_PACKAGE=lodash-es", "/usr/local/bin/node",
      "--no-addons", RUNNER],
    { cwd: site, input: `${input}\n`, encoding: "utf8", maxBuffer: 256 * 1024, timeout: 35_000 },
  );
  if (result.error) throw result.error;
  let response;
  try {
    response = JSON.parse(result.stdout);
  } catch {
    throw new Error("candidate response was not JSON");
  }
  if (!response?.ok) throw new Error(response?.message ?? response?.error ?? "candidate-call-failed");
  return response;
}

export function call(exportName, ...args) {
  return request(exportName, args).value;
}

export function callWithArgs(exportName, ...args) {
  return request(exportName, args);
}
