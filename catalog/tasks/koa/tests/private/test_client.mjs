import { spawnSync } from "node:child_process";
import { readFileSync } from "node:fs";

const NODE = process.env.KOA_NODE ?? process.execPath;
const RUNNER_SOURCE = readFileSync(new URL("./koa_runner.fixture", import.meta.url), "utf8");

export function callScenario(name) {
  const site = process.env.NODE_CANDIDATE_SITE;
  if (!site) throw new Error("candidate site is not configured");
  const command = process.env.KOA_TEST_DIRECT === "1"
    ? [NODE, "--input-type=module", "--eval", RUNNER_SOURCE]
    : ["/usr/bin/timeout", "--signal=TERM", "--kill-after=5s", "30s", "runuser", "-u", "candidate", "--",
        "/usr/bin/prlimit", "--cpu=60", "--nproc=4096", "--nofile=128", "--",
        "env", "-i", "PATH=/usr/local/bin:/usr/bin:/bin", `HOME=${site}/home`,
        `TMPDIR=${site}/tmp`, `NODE_CANDIDATE_SITE=${site}`, NODE, "--input-type=module", "--eval", RUNNER_SOURCE];
  const [executable, ...args] = command;
  const result = spawnSync(
    executable,
    args,
    { cwd: site, input: `${JSON.stringify({ name })}\n`, encoding: "utf8", maxBuffer: 256 * 1024, timeout: 30_000 },
  );
  if (result.error) throw result.error;
  if (result.status !== 0) throw new Error(`candidate scenario failed: ${result.stderr || result.stdout}`);
  try { return JSON.parse(result.stdout); } catch { throw new Error(`malformed scenario response: ${result.stdout}`); }
}
