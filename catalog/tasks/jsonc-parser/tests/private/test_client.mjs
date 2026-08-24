import { spawnSync } from "node:child_process";
import { chmodSync, copyFileSync, mkdirSync } from "node:fs";

const NODE = "/usr/local/bin/node";
const ADAPTER_DIR = "/tmp/jsonc-adapter";
const ADAPTER = `${ADAPTER_DIR}/candidate_adapter.mjs`;
mkdirSync(ADAPTER_DIR, { recursive: true, mode: 0o555 });
copyFileSync("/tests/private/candidate_adapter.source", ADAPTER);
chmodSync(ADAPTER, 0o555);
chmodSync(ADAPTER_DIR, 0o555);

function invoke(request) {
  const site = process.env.NODE_CANDIDATE_SITE;
  if (!site) throw new Error("candidate site is not configured");
  const result = spawnSync(
    "/usr/bin/timeout",
    [
      "--signal=TERM", "--kill-after=5s", "30s",
      "runuser", "-u", "candidate", "--",
      "/usr/bin/prlimit", "--cpu=60", "--nproc=32", "--nofile=128", "--",
      "env", "-i",
      "PATH=/usr/local/bin:/usr/bin:/bin",
      `HOME=${site}/home`,
      `TMPDIR=${site}/tmp`,
      "JSONC_ADAPTER_MODE=1",
      NODE, "--no-addons", ADAPTER,
    ],
    {
      cwd: site,
      input: `${JSON.stringify(request)}\n`,
      encoding: "utf8",
      maxBuffer: 256 * 1024,
      timeout: 30_000,
    },
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

export function callJsonc(operation, request) {
  const payload = invoke({ operation, ...request });
  if (!payload.ok) {
    throw new Error(`${payload.exception_type ?? "Error"}: ${payload.message ?? payload.error}`);
  }
  return payload.result;
}

export function callJsoncFailure(operation, request) {
  const payload = invoke({ operation, ...request });
  if (payload.ok) throw new Error("candidate call unexpectedly succeeded");
  return payload;
}
