import { spawnSync } from "node:child_process";

const site = process.env.NODE_CANDIDATE_SITE;
if (!site) throw new Error("NODE_CANDIDATE_SITE is required");

export function call(exportName, args = []) {
  const child = spawnSync(
    "/usr/sbin/runuser",
    [
      "-u", "candidate", "--", "env",
      "PATH=/usr/local/bin:/usr/bin:/bin",
      "NODE_ALLOWED_PACKAGE=pg-connection-string",
      "/usr/local/bin/node", "/tests/runtime/node/candidate_runner.mjs",
    ],
    {
      cwd: site,
      input: JSON.stringify({ package: "pg-connection-string", export: exportName, args }),
      encoding: "utf8",
      timeout: 10_000,
      maxBuffer: 256 * 1024,
    },
  );
  if (child.error) return { ok: false, error: "adapter-failed", message: child.error.message };
  try {
    return JSON.parse(child.stdout);
  } catch {
    return { ok: false, error: "adapter-failed", message: String(child.stderr).slice(0, 1024) };
  }
}

export function value(exportName, args = []) {
  const result = call(exportName, args);
  if (!result.ok) throw new Error(`${result.error}: ${result.message ?? ""}`);
  return result.value;
}
