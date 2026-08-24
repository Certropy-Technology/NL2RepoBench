// Hidden scored slice for `fast-glob` 4.0.0 (revision
// 467b65a79ed1b84fd9fd18966deda8a4e57b8e0e).
//
// Every assertion crosses the bounded JSON child boundary in
// `candidate_runner.mjs`, so the scored slice is restricted to directly
// callable, JSON-serializable exports: `glob`, `globSync`, `generateTasks`,
// `isDynamicPattern`, `escapePath`, `convertPathToPattern`.
//
// Deliberately out of scope (documented in blocked.md / handoff.md):
// `globStream` (ReadableStream cannot cross JSON), the `posix`/`win32`
// namespace objects (not directly callable), `objectMode`/`stats` (Dirent and
// Stats have no defined JSON contract), the `fs` adapter (functions),
// `signal` (AbortSignal), and the upstream internal Mocha unit tests.
import assert from "node:assert/strict";
import { mkdirSync, writeFileSync } from "node:fs";
import { join } from "node:path";
import test from "node:test";

const { callCandidate } = await import(
  process.env.NODE_TEST_CLIENT ?? "/tests/runtime/node/test_client.mjs"
);

// Bounded fixture protocol: the trusted test process materializes a fixed,
// world-readable tree inside its own cwd (the candidate site) and always passes
// an explicit absolute `cwd` option. The candidate child never inherits an
// implicit working directory, and no fixture escapes the site.
const FIXTURES = join(process.cwd(), "glob-fixtures");
for (const directory of [".directory", "first", "first/nested", "second", "third/library"]) {
  mkdirSync(join(FIXTURES, directory), { recursive: true, mode: 0o755 });
}
for (const file of [
  ".file",
  ".directory/file.md",
  "file.md",
  "first/file.md",
  "first/nested/file.md",
  "second/file.md",
  "third/library/a.js",
  "third/library/b.ts",
]) {
  writeFileSync(join(FIXTURES, file), "content\n", { mode: 0o644 });
}

// The library does not guarantee result ordering; upstream sorts before
// asserting and this adapter does the same.
const sorted = (value) => [...value].sort();
const globAsync = (patterns, options) => sorted(callCandidate("glob", [patterns, { cwd: FIXTURES, ...options }]));
const globSync = (patterns, options) => sorted(callCandidate("globSync", [patterns, { cwd: FIXTURES, ...options }]));

test("glob resolves a shallow wildcard to files only", () => {
  assert.deepEqual(globAsync("*"), ["file.md"]);
});

test("globSync matches glob for a shallow wildcard", () => {
  assert.deepEqual(globSync("*"), ["file.md"]);
});

test("glob traverses recursively with globstar", () => {
  assert.deepEqual(globAsync("**/*.md"), [
    "file.md",
    "first/file.md",
    "first/nested/file.md",
    "second/file.md",
  ]);
});

test("globSync traverses recursively with globstar", () => {
  assert.deepEqual(globSync("**/*.md"), [
    "file.md",
    "first/file.md",
    "first/nested/file.md",
    "second/file.md",
  ]);
});

test("glob accepts an array of patterns and de-duplicates results", () => {
  assert.deepEqual(globAsync(["first/*.md", "first/*.md", "second/*.md"]), [
    "first/file.md",
    "second/file.md",
  ]);
});

test("glob collapses identical patterns even when unique is disabled", () => {
  // Verified against the frozen revision: identical patterns are merged into a
  // single task before traversal, so unique:false yields no duplicate entries.
  assert.deepEqual(globAsync(["first/*.md", "first/*.md"], { unique: false }), [
    "first/file.md",
  ]);
});

test("glob excludes dot entries by default", () => {
  assert.deepEqual(globAsync("**/*"), [
    "file.md",
    "first/file.md",
    "first/nested/file.md",
    "second/file.md",
    "third/library/a.js",
    "third/library/b.ts",
  ]);
});

test("glob includes dot entries when dot is enabled", () => {
  assert.ok(globAsync("**/*", { dot: true }).includes(".file"));
  assert.ok(globAsync("**/*", { dot: true }).includes(".directory/file.md"));
});

test("glob returns directories when onlyDirectories is enabled", () => {
  assert.deepEqual(globAsync("*", { onlyDirectories: true }), ["first", "second", "third"]);
});

test("glob marks directories with a trailing separator", () => {
  assert.deepEqual(globAsync("*", { onlyDirectories: true, markDirectories: true }), [
    "first/",
    "second/",
    "third/",
  ]);
});

test("glob returns both files and directories when onlyFiles is disabled", () => {
  assert.deepEqual(globAsync("*", { onlyFiles: false }), [
    "file.md",
    "first",
    "second",
    "third",
  ]);
});

test("glob returns absolute paths with posix separators", () => {
  assert.deepEqual(globAsync("file.md", { absolute: true }), [`${FIXTURES}/file.md`]);
});

test("glob applies the ignore option", () => {
  assert.deepEqual(globAsync("**/*.md", { ignore: ["first/**"] }), ["file.md", "second/file.md"]);
});

test("glob limits traversal with deep", () => {
  assert.deepEqual(globAsync("**/*.md", { deep: 1 }), ["file.md"]);
});

test("glob expands brace patterns", () => {
  assert.deepEqual(globAsync("third/library/*.{js,ts}"), [
    "third/library/a.js",
    "third/library/b.ts",
  ]);
});

test("glob disables brace expansion on request", () => {
  assert.deepEqual(globAsync("third/library/*.{js,ts}", { braceExpansion: false }), []);
});

test("glob matches base names when baseNameMatch is enabled", () => {
  assert.deepEqual(globAsync("*.ts", { baseNameMatch: true }), ["third/library/b.ts"]);
});

test("glob is case sensitive by default", () => {
  assert.deepEqual(globAsync("FILE.md"), []);
});

test("glob ignores case when caseSensitiveMatch is disabled", () => {
  assert.deepEqual(globAsync("FILE.md", { caseSensitiveMatch: false }), ["file.md"]);
});

test("glob returns an empty array for a non-matching static pattern", () => {
  assert.deepEqual(globAsync("missing.md"), []);
});

test("glob resolves a static pattern without wildcards", () => {
  assert.deepEqual(globAsync("first/file.md"), ["first/file.md"]);
});

test("glob suppresses errors for a missing cwd when suppressErrors is enabled", () => {
  assert.deepEqual(
    sorted(callCandidate("glob", ["**/*", { cwd: join(FIXTURES, "absent"), suppressErrors: true }])),
    [],
  );
});

test("isDynamicPattern detects wildcards", () => {
  assert.equal(callCandidate("isDynamicPattern", ["*.md"]), true);
  assert.equal(callCandidate("isDynamicPattern", ["**/file.md"]), true);
});

test("isDynamicPattern reports static patterns", () => {
  assert.equal(callCandidate("isDynamicPattern", ["file.md"]), false);
  assert.equal(callCandidate("isDynamicPattern", ["first/file.md"]), false);
});

test("isDynamicPattern honours braceExpansion:false", () => {
  assert.equal(callCandidate("isDynamicPattern", ["{a,b}.md"]), true);
  assert.equal(callCandidate("isDynamicPattern", ["{a,b}.md", { braceExpansion: false }]), false);
});

test("escapePath escapes glob metacharacters", () => {
  assert.equal(callCandidate("escapePath", ["!abc"]), "\\!abc");
  assert.equal(callCandidate("escapePath", ["a(b)c"]), "a\\(b\\)c");
});

test("escapePath leaves plain paths unchanged", () => {
  assert.equal(callCandidate("escapePath", ["first/file.md"]), "first/file.md");
});

test("convertPathToPattern escapes glob metacharacters in a path", () => {
  assert.equal(callCandidate("convertPathToPattern", ["a(b)c"]), "a\\(b\\)c");
});

test("convertPathToPattern normalizes a posix path", () => {
  assert.equal(callCandidate("convertPathToPattern", ["first/file.md"]), "first/file.md");
});

test("generateTasks reports a single task for one dynamic pattern", () => {
  const tasks = callCandidate("generateTasks", ["**/*.md", { cwd: FIXTURES }]);
  assert.equal(tasks.length, 1);
  assert.equal(tasks[0].dynamic, true);
  assert.equal(tasks[0].base, ".");
  assert.deepEqual(tasks[0].patterns, ["**/*.md"]);
  assert.deepEqual(tasks[0].positive, ["**/*.md"]);
  assert.deepEqual(tasks[0].negative, []);
});

test("generateTasks separates tasks by base directory", () => {
  const tasks = callCandidate("generateTasks", [["first/*.md", "second/*.md"], { cwd: FIXTURES }]);
  assert.deepEqual(sorted(tasks.map((task) => task.base)), ["first", "second"]);
});

test("generateTasks records negative patterns", () => {
  const tasks = callCandidate("generateTasks", [["**/*.md", "!first/**"], { cwd: FIXTURES }]);
  assert.equal(tasks.length, 1);
  assert.deepEqual(tasks[0].negative, ["first/**"]);
});

test("generateTasks marks a static pattern as non-dynamic", () => {
  const tasks = callCandidate("generateTasks", ["file.md", { cwd: FIXTURES }]);
  assert.equal(tasks.length, 1);
  assert.equal(tasks[0].dynamic, false);
});

test("glob rejects a non-string pattern", () => {
  assert.throws(() => callCandidate("glob", [[42], { cwd: FIXTURES }]), /candidate-call-failed/);
});

test("globSync rejects a non-string pattern", () => {
  assert.throws(() => callCandidate("globSync", [[42], { cwd: FIXTURES }]), /candidate-call-failed/);
});

test("glob returns an empty array for a missing cwd even without error suppression", () => {
  // Verified against the frozen revision: a non-existent cwd is reported as an
  // empty result set rather than a rejection, independent of suppressErrors.
  assert.deepEqual(
    sorted(callCandidate("glob", ["**/*", { cwd: join(FIXTURES, "absent"), suppressErrors: false }])),
    [],
  );
});
