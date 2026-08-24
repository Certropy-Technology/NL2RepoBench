import { spawnSync } from "node:child_process";
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";

const NODE = process.execPath;
const ADAPTER = fileURLToPath(new URL("./koa_adapter", import.meta.url));
const ADAPTER_SOURCE = readFileSync(ADAPTER, "utf8");

export function callKoa(operation, payload = {}) {
  const site = process.env.NODE_CANDIDATE_SITE;
  if (!site) throw new Error("candidate site is not configured");
  const result = spawnSync(
    "/usr/bin/timeout",
    ["--signal=TERM", "--kill-after=5s", "30s", "runuser", "-u", "candidate", "--",
      "/usr/bin/prlimit", "--cpu=60", "--nproc=32", "--nofile=128", "--",
      "env", "-i", `PATH=/usr/local/bin:/usr/bin:/bin`, `HOME=${site}/home`,
      `TMPDIR=${site}/tmp`, "NODE_OPTIONS=", NODE, "--no-addons", "--input-type=module",
      "-e", ADAPTER_SOURCE],
    {
      cwd: site,
      input: `${JSON.stringify({ operation, payload })}\n`,
      encoding: "utf8",
      maxBuffer: 256 * 1024,
      timeout: 30_000,
    },
  );
  if (result.error) throw result.error;
  if (result.status !== 0) throw new Error(`adapter exited ${result.status}: ${result.stderr}`);
  let response;
  try {
    response = JSON.parse(result.stdout);
  } catch {
    throw new Error(`adapter response malformed: ${result.stdout}`);
  }
  if (!response.ok) throw new Error(response.error ?? "adapter-call-failed");
  return response.value;
}

