import { lstatSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";

const args = process.argv.slice(2);
const expected = Number(args[args.indexOf("--expected") + 1]);
const reportPath = args.includes("--report") ? args[args.indexOf("--report") + 1] : null;
const reason = args.includes("--reason") ? args[args.indexOf("--reason") + 1] : null;
const trustedExit = args.includes("--runner-exit-code") ? Number(args[args.indexOf("--runner-exit-code") + 1]) : null;
const output = args[args.indexOf("--output") + 1];
const zero = { collected: 0, passed: 0, failed: 0, errors: 0, skipped: 0, todo: 0 };
const modelReasons = new Set([
  "candidate-workspace-rejected",
  "candidate-installation-failed",
  "candidate-call-failed",
]);
function writeResult(result) {
  mkdirSync(output, { recursive: true, mode: 0o700 });
  writeFileSync(`${output}/reward.json`, `${JSON.stringify({ reward: result.reward, test_pass_rate: result.reward }, null, 2)}\n`, { mode: 0o444 });
  writeFileSync(`${output}/grading.json`, `${JSON.stringify({ schema_version: "2.0", metric_contract: "node-test-leaf-pass-rate-v1", ...result })}\n`, { mode: 0o444 });
}
function failure(failureReason, details = []) {
  const modelFailure = modelReasons.has(failureReason);
  writeResult({ valid: modelFailure, reward: 0, expected_total: expected, counts: zero, failure_class: modelFailure ? "model" : "verifier", failure_reason: failureReason, details });
  process.exit(0);
}
if (!Number.isSafeInteger(expected) || expected < 1 || !output) failure("verifier-internal-error");
if (reason) failure(reason);
if (!reportPath) failure("node-report-missing");
let report;
try {
  const metadata = lstatSync(reportPath);
  if (!metadata.isFile() || metadata.size > 8 * 1024 * 1024) failure("node-report-malformed");
  report = JSON.parse(readFileSync(reportPath, "utf8"));
} catch (error) {
  failure("node-report-malformed", [String(error)]);
}
const exactKeys = (object, allowed) => Object.keys(object).every((key) => allowed.includes(key));
if (!report || typeof report !== "object" || Array.isArray(report)) failure("node-report-malformed");
if (!exactKeys(report, ["schema_version", "framework", "report_format", "collected", "tests", "collection_errors", "runner_exit_code"])) failure("node-report-malformed");
if (report.schema_version !== "2.0" || report.report_format !== "node-test-json-v1" || report.framework !== "node:test" || !Number.isSafeInteger(report.collected) || report.collected < 0 || !Array.isArray(report.tests) || !Array.isArray(report.collection_errors) || !Number.isInteger(report.runner_exit_code)) failure("node-report-malformed");
if (report.tests.length !== report.collected) failure("node-report-count-mismatch");
if (trustedExit !== null && trustedExit !== report.runner_exit_code) failure("node-report-exit-mismatch");
const ids = new Set();
const counts = { ...zero };
for (const test of report.tests) {
  if (!test || typeof test !== "object" || Array.isArray(test) || !exactKeys(test, ["schema_version", "test_id", "status", "duration_ms", "details"])) failure("node-report-malformed");
  if (test.schema_version !== "2.0" || typeof test.test_id !== "string" || ids.has(test.test_id)) failure("node-duplicate-test-id");
  ids.add(test.test_id);
  if (!Object.prototype.hasOwnProperty.call(counts, test.status)) failure("node-report-malformed");
  if (typeof test.duration_ms !== "number" || !Number.isFinite(test.duration_ms) || test.duration_ms < 0) failure("node-report-malformed");
  counts[test.status] += 1;
}
for (const error of report.collection_errors) {
  if (!error || typeof error !== "object" || Array.isArray(error) || !exactKeys(error, ["schema_version", "message", "test_id"]) || error.schema_version !== "2.0" || typeof error.message !== "string") failure("node-report-malformed");
}
if (report.collection_errors?.length) failure("node-collection-error");
if (report.collected !== expected) failure("node-collection-mismatch");
const expectedExit = counts.failed || counts.errors ? 1 : 0;
if (report.runner_exit_code !== expectedExit) failure("node-report-exit-mismatch");
counts.collected = report.collected;
writeResult({ valid: true, reward: Math.max(0, Math.min(counts.passed / expected, 1)), expected_total: expected, counts, runner_exit_code: report.runner_exit_code, report });
