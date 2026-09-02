import { lstatSync, readFileSync } from "node:fs";

const args = process.argv.slice(2);
const path = args[args.indexOf("--path") + 1];
const expected = {
  candidate_install: "pnpm-pack-offline-v1",
  report_format: "node-test-json-v1",
  runner: "node-test-subprocess-boundary-v1",
  schema_version: "2.0",
  test_root: "/tests/private",
};

if (!path) process.exit(64);
try {
  const metadata = lstatSync(path);
  if (!metadata.isFile() || metadata.size > 4096) process.exit(65);
  const actual = JSON.parse(readFileSync(path, "utf8"));
  if (JSON.stringify(actual) !== JSON.stringify(expected)) process.exit(66);
} catch {
  process.exit(67);
}
