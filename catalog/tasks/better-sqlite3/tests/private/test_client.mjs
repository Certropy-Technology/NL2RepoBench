import { spawnSync } from "node:child_process";

const NODE = "/usr/local/bin/node";
const RUNNER = "/tests/runtime/node/candidate_runner.mjs";

export function callScenario(name) {
  const site = process.env.NODE_CANDIDATE_SITE;
  if (!site) throw new Error("candidate site is not configured");
  const result = spawnSync(
    "/usr/bin/timeout",
    ["--signal=TERM", "--kill-after=5s", "30s", "runuser", "-u", "candidate", "--", "/usr/bin/prlimit", "--cpu=60", "--nproc=32", "--nofile=128", "--", "env", "-i", `PATH=/usr/local/bin:/usr/bin:/bin`, `HOME=${site}/home`, `TMPDIR=${site}/tmp`, "NODE_ALLOWED_PACKAGE=better-sqlite3", NODE, "--no-addons", RUNNER],
    { cwd: site, input: `${JSON.stringify({ package: "better-sqlite3", export: "runScenario", args: [name] })}\n`, encoding: "utf8", maxBuffer: 256 * 1024, timeout: 5_000 },
  );
  if (result.error) throw result.error;
  let payload;
  try { payload = JSON.parse(result.stdout); } catch (_) { throw new Error(`malformed candidate response: ${result.stdout}`); }
  if (!payload.ok) throw new Error(payload.message ?? payload.error ?? "candidate-call-failed");
  return payload.value;
}
