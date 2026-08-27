import { copyFileSync, chmodSync, rmSync } from "node:fs";
import { spawnSync } from "node:child_process";

const site = process.env.NODE_CANDIDATE_SITE;
if (!site) throw new Error("candidate site is not configured");

export function runScenario(scenario, input = {}) {
  const runner = `/tmp/socketio-scenario-runner-${process.pid}-${Date.now()}.mjs`;
  copyFileSync("/tests/private/scenario_runner.txt", runner);
  chmodSync(runner, 0o555);
  try {
    const result = spawnSync(
      "/usr/bin/timeout",
      [
        "--signal=TERM",
        "--kill-after=3s",
        "12s",
        "runuser",
        "-u",
        "candidate",
        "--",
        "/usr/bin/prlimit",
        "--cpu=12",
        "--nproc=32",
        "--nofile=128",
        "--",
        "env",
        "-i",
        "PATH=/usr/local/bin:/usr/bin:/bin",
        `HOME=${site}/home`,
        `TMPDIR=${site}/tmp`,
        `NODE_CANDIDATE_SITE=${site}`,
        "/usr/local/bin/node",
        "--no-addons",
        runner,
      ],
      {
        cwd: site,
        input: `${JSON.stringify({ scenario, input })}\n`,
        encoding: "utf8",
        maxBuffer: 256 * 1024,
        timeout: 12_000,
      },
    );
    if (result.error) throw result.error;
    if (result.status !== 0) {
      throw new Error(`candidate-call-failed (${result.status}): ${result.stderr}`);
    }
    const lines = result.stdout.trim().split(/\r?\n/).reverse();
    for (const line of lines) {
      try {
        const payload = JSON.parse(line);
        if (payload?.nl2repo_socketio_result !== true) continue;
        if (!payload.ok) throw new Error(payload.error ?? "candidate-call-failed");
        return payload.value;
      } catch (error) {
        if (error instanceof SyntaxError) continue;
        throw error;
      }
    }
    throw new Error(`candidate-call-failed: no bounded result (${result.stderr})`);
  } finally {
    rmSync(runner, { force: true });
  }
}
