import { spawnSync } from "node:child_process";
import { dirname, join } from "node:path";
import { existsSync } from "node:fs";
import { fileURLToPath } from "node:url";

// Node is responsible only for transport. The trusted Python runtime owns
// report normalization, canonical LeafReport construction, and evaluation.
const args = process.argv.slice(2);
const value = (name) => args[args.indexOf(name) + 1];
const expected = value("--expected");
const report = args.includes("--report") ? value("--report") : null;
const reason = args.includes("--reason") ? value("--reason") : null;
const runnerExit = args.includes("--runner-exit-code") ? value("--runner-exit-code") : null;
const output = value("--output");
if (!expected || !output) process.exit(64);

const bundledRuntime = "/opt/nl2repobench-runtime";
const sourceRuntime = join(dirname(fileURLToPath(import.meta.url)), "../../..");
const runtime = process.env.NL2REPO_RUNTIME
  ?? (existsSync(join(bundledRuntime, "nl2repobench/__init__.py")) ? bundledRuntime : sourceRuntime);
const pythonCandidates = [
  process.env.NL2REPO_PYTHON,
  process.env.VIRTUAL_ENV ? join(process.env.VIRTUAL_ENV, "bin/python") : null,
  "/usr/local/bin/python",
  "/usr/local/bin/python3",
  "/usr/bin/python3",
].filter(Boolean);
const python = pythonCandidates.find((candidate) => existsSync(candidate)) ?? "/usr/bin/python3";
const pythonCode = [
  "import sys",
  `sys.path.insert(0, ${JSON.stringify(runtime)})`,
  "from nl2repobench.verification.cli import main",
  "main()",
].join("; ");
const pythonArgs = [
  "-I",
  "-c",
  pythonCode,
  "--runtime",
  "node",
  "--expected",
  expected,
  "--metric-contract",
  "node-test-leaf-pass-rate-v1",
  "--output",
  output,
];
if (report) pythonArgs.push("--report", report);
if (runnerExit !== null) pythonArgs.push("--runner-exit-code", runnerExit);
if (reason) pythonArgs.push("--reason", reason);

const result = spawnSync(python, pythonArgs, {
  stdio: "inherit",
  timeout: 120_000,
});
process.exit(result.error ? 70 : result.status ?? 70);
