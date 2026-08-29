import {spawnSync} from "node:child_process";

async function runCandidateBridge() {
  const {createRequire} = await import("node:module");
  const {readFileSync} = await import("node:fs");
  const {join} = await import("node:path");
  const {pathToFileURL} = await import("node:url");
  const request = JSON.parse(readFileSync(0, "utf8"));
  if (!request || request.package !== "lines-and-columns") {
    throw new Error("package-not-allowlisted");
  }
  const require = createRequire(pathToFileURL(`${process.cwd()}/package.json`));
  const cjs = require(request.package);
  const packageRoot = join(process.cwd(), "node_modules", request.package);
  const packageManifest = JSON.parse(readFileSync(join(packageRoot, "package.json"), "utf8"));
  const importEntry = packageManifest.exports?.import ?? packageManifest.exports?.["."]?.import;
  if (typeof importEntry !== "string" || !importEntry.startsWith("./") || importEntry.includes("..")) {
    throw new Error("package-has-no-safe-import-entry");
  }
  const esm = await import(pathToFileURL(join(packageRoot, importEntry)).href);
  if (request.operation === "inventory") {
    process.stdout.write(JSON.stringify({
      cjsClass: typeof cjs.LinesAndColumns,
      esmClass: typeof esm.LinesAndColumns,
      cjsDefaultAbsent: cjs.default === undefined,
      effectiveUid: process.getuid(),
      effectiveGid: process.getgid(),
    }));
  } else if (request.operation === "location") {
    const [string, index] = request.args;
    process.stdout.write(JSON.stringify(new esm.LinesAndColumns(string).locationForIndex(index)));
  } else if (request.operation === "index") {
    const [string, location] = request.args;
    process.stdout.write(JSON.stringify(new cjs.LinesAndColumns(string).indexForLocation(location)));
  } else {
    throw new Error("operation-not-allowlisted");
  }
}

const bridge = `(${runCandidateBridge.toString()})().catch((error) => {\n`
  + `  process.stderr.write(String(error?.stack ?? error));\n`
  + `  process.exitCode = 1;\n`
  + `});`;

export function callCandidate(operation, args = []) {
  const result = spawnSync(process.execPath, ["--no-addons", "--input-type=module", "--eval", bridge], {
    cwd: process.env.NODE_CANDIDATE_SITE,
    input: JSON.stringify({package: "lines-and-columns", operation, args}),
    encoding: "utf8",
    timeout: 30000,
    maxBuffer: 262144,
    uid: 10001,
    gid: 10001,
    env: {
      PATH: "/usr/local/bin:/usr/bin:/bin",
      HOME: `${process.env.NODE_CANDIDATE_SITE}/.home`,
      TMPDIR: `${process.env.NODE_CANDIDATE_SITE}/.tmp`,
    },
  });
  if (result.error || result.status !== 0) {
    throw new Error(`candidate-call-failed: ${result.stderr || result.error}`);
  }
  try {
    return JSON.parse(result.stdout);
  } catch {
    throw new Error("candidate-call-failed: malformed response");
  }
}
