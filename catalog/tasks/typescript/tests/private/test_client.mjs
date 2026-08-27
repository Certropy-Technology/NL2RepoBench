import { chmodSync, copyFileSync, mkdirSync } from "node:fs";
import { spawnSync } from "node:child_process";
import { join } from "node:path";
import { fileURLToPath } from "node:url";

const candidateSite = process.env.NODE_CANDIDATE_SITE;
if (!candidateSite) throw new Error("NODE_CANDIDATE_SITE is required");

const runtimeDir = "/tmp/nl2repobench-typescript-adapter";
const adapter = join(runtimeDir, "adapter.mjs");
mkdirSync(runtimeDir, { recursive: true, mode: 0o755 });
copyFileSync(fileURLToPath(new URL("./candidate_adapter.txt", import.meta.url)), adapter);
chmodSync(runtimeDir, 0o555);
chmodSync(adapter, 0o555);

export function callCandidate(payload, timeoutMs = 10_000) {
  const result = spawnSync(
    "/usr/sbin/runuser",
    [
      "-u", "candidate", "--",
      "env",
      "PATH=/usr/local/bin:/usr/bin:/bin",
      `HOME=${join(candidateSite, "home")}`,
      `TMPDIR=${join(candidateSite, "tmp")}`,
      "NODE_OPTIONS=",
      "NODE_PATH=",
      "/usr/local/bin/node",
      "--no-addons",
      adapter,
    ],
    {
      cwd: candidateSite,
      input: `${JSON.stringify(payload)}\n`,
      encoding: "utf8",
      timeout: timeoutMs,
      maxBuffer: 1024 * 1024,
      env: { PATH: "/usr/local/bin:/usr/bin:/bin" },
    },
  );
  if (result.error) throw result.error;
  if (result.status !== 0) {
    throw new Error(`candidate adapter exited ${result.status}: ${(result.stderr || result.stdout).slice(0, 4096)}`);
  }
  const lines = result.stdout.trim().split(/\r?\n/);
  if (lines.length !== 1) throw new Error("candidate adapter emitted non-protocol output");
  const response = JSON.parse(lines[0]);
  if (response?.ok !== true) throw new Error(`candidate adapter rejected request: ${JSON.stringify(response)}`);
  return response.value;
}
