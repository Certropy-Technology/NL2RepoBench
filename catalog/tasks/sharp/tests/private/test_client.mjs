import { spawnSync } from "node:child_process";
import { chmodSync, chownSync, copyFileSync, existsSync, mkdirSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const NODE = "/usr/local/bin/node";
const SCRIPT_DIR = dirname(fileURLToPath(import.meta.url));

function ensureAdapter(site) {
  const target = join(site, ".sharp-candidate-adapter.mjs");
  if (!existsSync(target)) {
    copyFileSync(join(SCRIPT_DIR, "candidate_adapter.txt"), target);
    chownSync(target, 10001, 10001);
    chmodSync(target, 0o500);
  }
  mkdirSync(join(site, "home"), { recursive: true });
  mkdirSync(join(site, "tmp"), { recursive: true });
  return target;
}

export function callSharp(operation, input = undefined, extra = {}) {
  const site = process.env.NODE_CANDIDATE_SITE;
  if (!site) throw new Error("candidate site is not configured");
  const adapter = ensureAdapter(site);
  const request = { operation, ...extra };
  if (input !== undefined) request.input = input;
  const result = spawnSync(
    "/usr/bin/timeout",
    [
      "--signal=TERM", "--kill-after=5s", "30s",
      "runuser", "-u", "candidate", "--",
      "/usr/bin/prlimit", "--cpu=60", "--nproc=4096", "--nofile=128", "--",
      "env", "-i",
      "PATH=/usr/local/bin:/usr/bin:/bin",
      `HOME=${site}/home`,
      `TMPDIR=${site}/tmp`,
      "NODE_ALLOWED_PACKAGE=sharp",
      NODE, adapter,
    ],
    {
      cwd: site,
      input: `${JSON.stringify(request)}\n`,
      encoding: "utf8",
      maxBuffer: 512 * 1024,
      timeout: 30_000,
    },
  );
  if (result.error) throw result.error;
  let payload;
  try {
    payload = JSON.parse(result.stdout);
  } catch {
    throw new Error(
      `candidate response malformed: status=${result.status} signal=${result.signal ?? ""} `
      + `stdout=${result.stdout} stderr=${result.stderr}`,
    );
  }
  return { ...payload, returncode: result.status };
}

export function sharpValue(operation, input = undefined, extra = {}) {
  const result = callSharp(operation, input, extra);
  if (!result.ok) throw new Error(`${result.exception_type ?? "Error"}: ${result.message ?? result.error}`);
  return result.value;
}
