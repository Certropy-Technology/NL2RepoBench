import { spawnSync } from "node:child_process";
import { readFileSync } from "node:fs";

const NODE = process.env.NODE_CANDIDATE_NODE ?? "/usr/local/bin/node";
const ADAPTER = process.env.NODE_CANDIDATE_ADAPTER ?? "/tests/private/candidate_adapter.js.txt";
const ADAPTER_SOURCE = readFileSync(ADAPTER, "utf8");

function runCandidate(input) {
  const site = process.env.NODE_CANDIDATE_SITE;
  if (!site) throw new Error("candidate site is not configured");
  const result = spawnSync(
    "/usr/bin/timeout",
    [
      "--signal=TERM", "--kill-after=5s", "30s", "runuser", "-u", "candidate", "--",
      "/usr/bin/prlimit", "--cpu=60", "--nproc=32", "--nofile=128", "--", "env", "-i",
      "PATH=/usr/local/bin:/usr/bin:/bin", `HOME=${site}/home`, `TMPDIR=${site}/tmp`,
      "NODE_ALLOWED_PACKAGE=micromatch", NODE, "--no-addons", "--input-type=module", "--eval",
      ADAPTER_SOURCE,
    ],
    {
      cwd: site,
      input: `${JSON.stringify(input)}\n`,
      encoding: "utf8",
      maxBuffer: 256 * 1024,
      timeout: 30_000,
    },
  );
  if (result.error) throw result.error;
  let payload;
  try {
    payload = JSON.parse(result.stdout);
  } catch {
    throw new Error(`candidate response malformed: ${result.stdout}`);
  }
  if (!payload.ok) {
    throw new Error(
      `${payload.exception_type ?? "Error"}: ${payload.message ?? payload.error ?? "candidate-call-failed"}`,
    );
  }
  return payload.value;
}

export function callCandidate(exportName, args) {
  return runCandidate({ operation: "call", exportName, args });
}

export function inspectSurface() {
  return runCandidate({ operation: "surface", args: [] });
}

export function runMatcher(pattern, options, inputs) {
  return runCandidate({ operation: "matcher", args: [pattern, options, inputs] });
}

export function runRegex(pattern, options, inputs) {
  return runCandidate({ operation: "regex", args: [pattern, options, inputs] });
}

export function scanSummary(pattern, options) {
  const args = options === undefined ? [pattern] : [pattern, options];
  return runCandidate({ operation: "scan-summary", args });
}

export function parseSummary(patterns, options) {
  const args = options === undefined ? [patterns] : [patterns, options];
  return runCandidate({ operation: "parse-summary", args });
}

export function callbackTrace(list, patterns, options) {
  return runCandidate({ operation: "callbacks", args: [list, patterns, options] });
}
