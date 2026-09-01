import { spawnSync } from "node:child_process";

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

const runtime = "/opt/nl2repobench-runtime";
const python = "/usr/local/bin/python3";
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
  "fixed-test-pass-rate-v1",
  "--output",
  output,
];
if (report) pythonArgs.push("--report", report);
if (runnerExit !== null) pythonArgs.push("--runner-exit-code", runnerExit);
if (reason) pythonArgs.push("--reason", reason);

const result = spawnSync(python, pythonArgs, {
  stdio: "inherit",
  env: {
    PATH: "/usr/bin:/bin",
    HOME: "/nonexistent",
    PYTHONDONTWRITEBYTECODE: "1",
  },
  timeout: 120_000,
});
process.exit(result.error ? 70 : result.status ?? 70);
