import { spawnSync } from "node:child_process";

const RUNNER = "/tests/runtime/node/candidate_runner.mjs";
const NODE = "/usr/local/bin/node";
const PACKAGE = "date-fns";

function runNode(args, input = undefined) {
  const site = process.env.NODE_CANDIDATE_SITE;
  if (!site) throw new Error("candidate site is not configured");
  const result = spawnSync(
    "/usr/bin/timeout",
    [
      "--signal=TERM",
      "--kill-after=5s",
      "30s",
      "runuser",
      "-u",
      "candidate",
      "--",
      "/usr/bin/prlimit",
      "--cpu=30",
      "--nproc=32",
      "--nofile=128",
      "--",
      "env",
      "-i",
      "PATH=/usr/local/bin:/usr/bin:/bin",
      `HOME=${site}/home`,
      `TMPDIR=${site}/tmp`,
      "TERM=dumb",
      "CI=true",
      "FORCE_COLOR=0",
      "LC_ALL=C.UTF-8",
      "TZ=UTC",
      `NODE_ALLOWED_PACKAGE=${PACKAGE}`,
      NODE,
      "--no-addons",
      ...args,
    ],
    {
      cwd: site,
      input,
      encoding: "utf8",
      maxBuffer: 256 * 1024,
      timeout: 35_000,
    },
  );
  if (result.error) throw result.error;
  return result;
}

export function callCandidateResult(exportName, args) {
  const request = JSON.stringify({ package: PACKAGE, export: exportName, args });
  if (Buffer.byteLength(request) > 64 * 1024) throw new Error("request is too large");
  const result = runNode([RUNNER], `${request}\n`);
  let payload;
  try {
    payload = JSON.parse(result.stdout);
  } catch {
    throw new Error("candidate response is malformed");
  }
  return payload;
}

export function callCandidate(exportName, args) {
  const payload = callCandidateResult(exportName, args);
  if (!payload.ok) throw new Error(payload.error ?? "candidate-call-failed");
  return payload.value;
}

export function packageManifest() {
  const source = [
    'import { readFileSync } from "node:fs";',
    'const p = JSON.parse(readFileSync("./node_modules/date-fns/package.json", "utf8"));',
    'const root = typeof p.exports === "string" ? p.exports : p.exports?.["."];',
    'process.stdout.write(JSON.stringify({name:p.name,version:p.version,type:p.type,root}) + "\\n");',
  ].join("");
  const result = runNode(["--input-type=module", "-e", source]);
  if (result.status !== 0) throw new Error("candidate package metadata is unavailable");
  return JSON.parse(result.stdout);
}
