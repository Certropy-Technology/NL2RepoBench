import { spawnSync } from "node:child_process";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const child = join(dirname(fileURLToPath(import.meta.url)), "candidate_child.runner");

export function call(request, timeout = 12_000) {
  const result = spawnSync(process.execPath, ["--no-addons", child], {
    cwd: process.env.NODE_CANDIDATE_SITE,
    env: {
      PATH: "/usr/local/bin:/usr/bin:/bin",
      HOME: join(process.env.NODE_CANDIDATE_SITE, "home"),
      TMPDIR: join(process.env.NODE_CANDIDATE_SITE, "tmp"),
    },
    input: `${JSON.stringify(request)}\n`,
    encoding: "utf8",
    timeout,
    maxBuffer: 256 * 1024,
  });
  if (result.error) throw result.error;
  let payload;
  try { payload = JSON.parse(result.stdout); }
  catch { throw new Error(`malformed candidate response: ${result.stderr}`); }
  if (!payload.ok) throw new Error(`${payload.exceptionType ?? "Error"}: ${payload.message ?? payload.error}`);
  return payload.value;
}

export function session(source, bytes, steps, extra = {}) {
  return call({ op: "session", source, bytes, steps, ...extra });
}
