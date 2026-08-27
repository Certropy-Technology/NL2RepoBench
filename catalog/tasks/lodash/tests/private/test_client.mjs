import { spawnSync } from "node:child_process";
import { chmodSync, copyFileSync, mkdirSync } from "node:fs";

const NODE = "/usr/local/bin/node";
const ADAPTER_DIR = "/tmp/lodash-adapter";
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
      "--signal=TERM", "--kill-after=2s", "5s",
      "runuser", "-u", "candidate", "--",
      "/usr/bin/prlimit", "--cpu=10", "--nproc=32", "--nofile=128", "--",
      "env", "-i",
      "PATH=/usr/local/bin:/usr/bin:/bin",
      `HOME=${site}/home`,
      `TMPDIR=${site}/tmp`,
      NODE, "--no-addons", ADAPTER,
    ],
    {
      cwd: site,
      input: `${JSON.stringify(request)}\n`,
      encoding: "utf8",
      maxBuffer: 256 * 1024,
      timeout: 10_000,
    },
  );
  if (result.error) throw result.error;
  let payload;
  try {
    payload = JSON.parse(result.stdout);
  } catch {
    throw new Error(`candidate response malformed: ${result.stdout}`);
  }
  if (!payload.ok) throw new Error(payload.message ?? payload.error ?? "candidate-call-failed");
  return payload.value;
}

export function metadata() {
  return invoke({ operation: "metadata" });
}

export function call(method, ...args) {
  return invoke({ operation: "call", method, args });
}
