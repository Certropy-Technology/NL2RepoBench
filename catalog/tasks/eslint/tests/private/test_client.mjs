import { chmodSync, copyFileSync } from "node:fs";
import { spawnSync } from "node:child_process";

const candidate = process.env.NODE_CANDIDATE_SITE;
const privateRunner = new URL("./eslint_runner.node", import.meta.url);
const runner = "/tmp/eslint-candidate-runner.mjs";

copyFileSync(privateRunner, runner);
chmodSync(runner, 0o555);

export function call(operation, payload = {}) {
  const result = spawnSync(
    "/usr/sbin/runuser",
    [
      "-u",
      "candidate",
      "--",
      "env",
      "PATH=/usr/local/bin:/usr/bin:/bin",
      `HOME=${candidate}/home`,
      `TMPDIR=${candidate}/tmp`,
      "/usr/local/bin/node",
      "--no-addons",
      runner,
    ],
    {
      cwd: candidate,
      input: `${JSON.stringify({ operation, ...payload })}\n`,
      encoding: "utf8",
      timeout: 30_000,
      maxBuffer: 256 * 1024,
    },
  );
  if (result.error) throw result.error;
  const lines = (result.stdout || "").trim().split(/\r?\n/);
  const response = JSON.parse(lines.at(-1) || "{}");
  if (!response.ok) {
    const error = new Error(response.message || response.error || result.stderr || "candidate call failed");
    error.name = response.exception_type || "CandidateError";
    throw error;
  }
  return response.value;
}
