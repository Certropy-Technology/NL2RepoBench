import { createRequire } from "node:module";
import { resolve } from "node:path";
import { test } from "node:test";
import assert from "node:assert/strict";

const site = resolve(process.env.NODE_CANDIDATE_SITE ?? process.cwd());
const require = createRequire(`${site}/package.json`);
const eslint = require("eslint");

test("main export exposes the measured constructors", () => {
  assert.deepEqual(Object.keys(eslint).sort(), [
    "ESLint",
    "Linter",
    "RuleTester",
    "SourceCode",
    "loadESLint",
  ]);
  for (const name of ["ESLint", "Linter", "RuleTester", "SourceCode", "loadESLint"]) {
    assert.equal(typeof eslint[name], "function", name);
  }
});

test("version fields and loadESLint are stable", async () => {
  assert.equal(eslint.ESLint.version, "10.9.0");
  assert.equal(eslint.Linter.version, "10.9.0");
  assert.equal(await eslint.loadESLint(), eslint.ESLint);
});

test("Linter verifies eqeqeq with exact diagnostic details", () => {
  const messages = new eslint.Linter().verify("value == 42", { rules: { eqeqeq: "error" } });
  assert.equal(messages.length, 1);
  assert.deepEqual(
    {
      ruleId: messages[0].ruleId,
      severity: messages[0].severity,
      message: messages[0].message,
      line: messages[0].line,
      column: messages[0].column,
      messageId: messages[0].messageId,
      endLine: messages[0].endLine,
      endColumn: messages[0].endColumn,
    },
    {
      ruleId: "eqeqeq",
      severity: 2,
      message: "Expected '===' and instead saw '=='.",
      line: 1,
      column: 7,
      messageId: "unexpected",
      endLine: 1,
      endColumn: 9,
    },
  );
});

test("no-unused-vars reports the binding location and messageId", () => {
  const [message] = new eslint.Linter().verify(
    "const unused = 1;",
    { rules: { "no-unused-vars": "error" } },
  );
  assert.equal(message.ruleId, "no-unused-vars");
  assert.equal(message.messageId, "unusedVar");
  assert.equal(message.message, "'unused' is assigned a value but never used.");
  assert.deepEqual(
    { line: message.line, column: message.column, endLine: message.endLine, endColumn: message.endColumn },
    { line: 1, column: 7, endLine: 1, endColumn: 13 },
  );
});

test("no-undef honors readonly globals", () => {
  const linter = new eslint.Linter();
  assert.equal(linter.verify("console.log(missing);", { rules: { "no-undef": "error" } }).length, 2);
  const messages = linter.verify(
    "console.log(missing);",
    { languageOptions: { globals: { console: "readonly" } }, rules: { "no-undef": "error" } },
  );
  assert.deepEqual(messages.map((message) => message.message), ["'missing' is not defined."]);
});

test("no-alert reports alert calls", () => {
  const [message] = new eslint.Linter().verify("alert('x');", { rules: { "no-alert": "error" } });
  assert.equal(message.ruleId, "no-alert");
  assert.equal(message.message, "Unexpected alert.");
  assert.equal(message.messageId, "unexpected");
});

test("verifyAndFix applies quotes and semi fixes to stability", () => {
  const result = new eslint.Linter().verifyAndFix(
    'const message = "hello"\n',
    { rules: { quotes: ["error", "single"], semi: ["error", "always"] } },
  );
  assert.equal(result.fixed, true);
  assert.equal(result.output, "const message = 'hello';\n");
  assert.deepEqual(result.messages, []);
});

test("modern optional chaining and nullish coalescing parse in ECMAScript 2024", () => {
  const messages = new eslint.Linter().verify(
    "const value = object?.field ?? fallback;",
    { languageOptions: { ecmaVersion: 2024 }, rules: {} },
  );
  assert.deepEqual(messages, []);
});

test("invalid source returns a parsing diagnostic", () => {
  const [message] = new eslint.Linter().verify("const = 1;", { rules: {} });
  assert.equal(message.ruleId, null);
  assert.equal(message.message, "Parsing error: Unexpected token =");
  assert.equal(message.line, 1);
  assert.equal(message.column, 7);
});

test("used eslint-disable directives suppress the selected rule", () => {
  const messages = new eslint.Linter().verify(
    "/* eslint-disable no-alert */\nalert('x');",
    { rules: { "no-alert": "error" } },
  );
  assert.deepEqual(messages, []);
});

test("unused disable directives are reported with configured severity", () => {
  const [message] = new eslint.Linter().verify(
    "/* eslint-disable no-alert */\nconst value = 1;",
    {
      linterOptions: { reportUnusedDisableDirectives: "error" },
      rules: { "no-alert": "error" },
    },
  );
  assert.equal(message.ruleId, null);
  assert.equal(message.severity, 2);
  assert.match(message.message, /Unused eslint-disable directive/);
  assert.match(message.message, /no-alert/);
});

test("getSourceCode exposes text, lines, locations, and comments", () => {
  const linter = new eslint.Linter();
  const source = "// hello\nconst value = 1;\n";
  assert.deepEqual(linter.verify(source, { rules: {} }), []);
  const code = linter.getSourceCode();
  assert.equal(code.text, source);
  assert.deepEqual(code.lines, ["// hello", "const value = 1;", ""]);
  assert.equal(code.getLocFromIndex(9).line, 2);
  assert.equal(code.getIndexFromLoc({ line: 2, column: 0 }), 9);
  assert.deepEqual(code.getAllComments().map((comment) => ({ type: comment.type, value: comment.value })), [
    { type: "Line", value: " hello" },
  ]);
});

test("SourceCode.splitLines handles CRLF, LF, CR, and trailing empties", () => {
  assert.deepEqual(eslint.SourceCode.splitLines("a\r\nb\nc\r"), ["a", "b", "c", ""]);
});

test("SourceCode token helpers return the parsed source structure", () => {
  const linter = new eslint.Linter();
  linter.verify("const value = 1;", { rules: {} });
  const code = linter.getSourceCode();
  assert.equal(code.getText(), "const value = 1;");
  assert.equal(code.getFirstToken(code.ast).value, "const");
  assert.equal(code.getText(code.ast), "const value = 1;");
});

test("ESLint.lintText returns final counts without fixes", async () => {
  const [result] = await new eslint.ESLint({
    overrideConfigFile: true,
    overrideConfig: [{ rules: { eqeqeq: "error" } }],
  }).lintText("value == 42", { filePath: "sample.js" });
  assert.match(result.filePath, /(?:^|[\\/])sample\.js$/);
  assert.equal(result.errorCount, 1);
  assert.equal(result.warningCount, 0);
  assert.equal(result.fixableErrorCount, 0);
  assert.equal(result.messages[0].ruleId, "eqeqeq");
});

test("ESLint.lintText returns fixed output and final counts", async () => {
  const [result] = await new eslint.ESLint({
    overrideConfigFile: true,
    overrideConfig: [{ rules: { quotes: ["error", "single"], semi: ["error", "always"] } }],
    fix: true,
  }).lintText('const message = "hello"\n', { filePath: "sample.js" });
  assert.equal(result.errorCount, 0);
  assert.equal(result.warningCount, 0);
  assert.deepEqual(result.messages, []);
  assert.equal(result.output, "const message = 'hello';\n");
});

test("config helpers preserve flat config order and values", () => {
  const config = require("eslint/config");
  assert.deepEqual(config.defineConfig({ files: ["**/*.js"], rules: { eqeqeq: "error" } }), [
    { files: ["**/*.js"], rules: { eqeqeq: "error" } },
  ]);
  assert.deepEqual(config.defineConfig({ rules: { semi: "error" } }, { rules: { quotes: "error" } }), [
    { rules: { semi: "error" } },
    { rules: { quotes: "error" } },
  ]);
  assert.deepEqual(config.globalIgnores(["dist/**"], "generated"), { ignores: ["dist/**"], name: "generated" });
});

test("use-at-your-own-risk exposes the frozen builtin rule metadata", () => {
  const risky = require("eslint/use-at-your-own-risk");
  assert.equal(typeof risky.shouldUseFlatConfig, "function");
  assert.equal(risky.builtinRules instanceof Map, true);
  assert.equal(risky.builtinRules.size, 292);
  const eqeqeq = risky.builtinRules.get("eqeqeq");
  assert.equal(eqeqeq.meta.type, "suggestion");
  assert.equal(eqeqeq.meta.fixable, "code");
  assert.equal(eqeqeq.meta.messages.unexpected, "Expected '{{expectedOperator}}' and instead saw '{{actualOperator}}'.");
});

test("documented package subpaths and package metadata are loadable", () => {
  const packageJson = require("eslint/package.json");
  assert.equal(packageJson.name, "eslint");
  assert.equal(packageJson.version, "10.9.0");
  assert.equal(typeof require("eslint/config").defineConfig, "function");
  assert.equal(typeof require("eslint/use-at-your-own-risk").builtinRules, "object");
});

test("diagnostics are deterministic and ordered by source location", () => {
  const messages = new eslint.Linter().verify(
    "missing == other;\nalert('x');",
    {
      languageOptions: { globals: { alert: "readonly" } },
      rules: { eqeqeq: "error", "no-undef": "error", "no-alert": "warn" },
    },
  );
  assert.deepEqual(messages.map(({ ruleId, line, column }) => ({ ruleId, line, column })), [
    { ruleId: "no-undef", line: 1, column: 1 },
    { ruleId: "eqeqeq", line: 1, column: 9 },
    { ruleId: "no-undef", line: 1, column: 12 },
    { ruleId: "no-alert", line: 2, column: 1 },
  ]);
});
