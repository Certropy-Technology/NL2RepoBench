import assert from "node:assert/strict";
import test from "node:test";
import { call } from "./test_client.mjs";

test("exports the documented CommonJS API", () => {
  const result = call("apiSurface");
  assert.deepEqual(result.keys, ["ESLint", "Linter", "RuleTester", "SourceCode", "loadESLint"]);
  assert.deepEqual(result.types, {
    Linter: "function",
    loadESLint: "function",
    ESLint: "function",
    RuleTester: "function",
    SourceCode: "function",
  });
  assert.equal(result.ruleTesterConstructible, true);
});

test("reports version 10.9.0 and loadESLint resolves to ESLint", () => {
  const result = call("apiSurface");
  assert.equal(result.eslintVersion, "10.9.0");
  assert.equal(result.linterVersion, "10.9.0");
  assert.equal(result.loadIdentity, true);
});

test("Linter.verify reports eqeqeq with stable location data", () => {
  const messages = call("verify", {
    code: "const answer = value == 42;",
    config: [{ languageOptions: { ecmaVersion: 2024 }, rules: { eqeqeq: "error" } }],
    filename: "input.js",
  });
  assert.deepEqual(messages, [{
    ruleId: "eqeqeq",
    severity: 2,
    message: "Expected '===' and instead saw '=='.",
    line: 1,
    column: 22,
    endLine: 1,
    endColumn: 24,
    messageId: "unexpected",
  }]);
});

test("Linter.verify orders no-unused-vars and no-undef diagnostics", () => {
  const messages = call("verify", {
    code: "function greet(name) { const unused = 1; return missing + name; }",
    config: [{
      languageOptions: { ecmaVersion: 2024 },
      rules: { "no-unused-vars": "warn", "no-undef": "error" },
    }],
    filename: "input.js",
  });
  assert.deepEqual(messages.map(({ ruleId, severity, line, column, messageId }) => ({
    ruleId, severity, line, column, messageId,
  })), [
    { ruleId: "no-unused-vars", severity: 1, line: 1, column: 10, messageId: "unusedVar" },
    { ruleId: "no-unused-vars", severity: 1, line: 1, column: 30, messageId: "unusedVar" },
    { ruleId: "no-undef", severity: 2, line: 1, column: 49, messageId: "undef" },
  ]);
});

test("Linter.verify returns a parsing diagnostic for invalid source", () => {
  const messages = call("verify", {
    code: "const = 1;",
    config: [{ languageOptions: { ecmaVersion: 2024 } }],
    filename: "bad.js",
  });
  assert.deepEqual(messages, [{
    ruleId: null,
    severity: 2,
    message: "Parsing error: Unexpected token =",
    line: 1,
    column: 7,
  }]);
});

test("used eslint-disable directives suppress the selected rule", () => {
  const messages = call("verify", {
    code: "/* eslint-disable eqeqeq */\nif (a == b) {}",
    config: [{
      languageOptions: { globals: { a: "readonly", b: "readonly" } },
      linterOptions: { reportUnusedDisableDirectives: "error" },
      rules: { eqeqeq: "error", "no-undef": "error" },
    }],
    filename: "input.js",
  });
  assert.deepEqual(messages, []);
});

test("unused eslint-disable directives are reported at configured severity", () => {
  const messages = call("verify", {
    code: "/* eslint-disable eqeqeq */\nconst x = 1;",
    config: [{ linterOptions: { reportUnusedDisableDirectives: "warn" }, rules: { eqeqeq: "error" } }],
    filename: "input.js",
  });
  assert.equal(messages.length, 1);
  assert.deepEqual(messages[0], {
    ruleId: null,
    severity: 1,
    message: "Unused eslint-disable directive (no problems were reported from 'eqeqeq').",
    line: 1,
    column: 1,
  });
});

test("languageOptions globals prevent no-undef while other rules still run", () => {
  const messages = call("verify", {
    code: "window.alert(value);",
    config: [{
      languageOptions: { globals: { window: "readonly", value: "readonly" } },
      rules: { "no-undef": 2, "no-alert": 1, eqeqeq: 0 },
    }],
    filename: "browser.js",
  });
  assert.deepEqual(messages.map(({ ruleId, severity, messageId }) => ({ ruleId, severity, messageId })), [
    { ruleId: "no-alert", severity: 1, messageId: "unexpected" },
  ]);
});

test("modern optional chaining and nullish coalescing parse under ecmaVersion 2024", () => {
  const messages = call("verify", {
    code: "const value = input?.items?.[0] ?? 0;",
    config: [{
      languageOptions: { ecmaVersion: 2024, globals: { input: "readonly" } },
      rules: { "no-undef": "error" },
    }],
    filename: "modern.js",
  });
  assert.deepEqual(messages, []);
});

test("verifyAndFix applies quotes and semi fixes until stable", () => {
  const result = call("verifyAndFix", {
    code: "const message = \"hello\"\n",
    config: [{ rules: { quotes: ["error", "single"], semi: ["error", "always"] } }],
    filename: "input.js",
  });
  assert.equal(result.fixed, true);
  assert.equal(result.output, "const message = 'hello';\n");
  assert.deepEqual(result.messages, []);
});

test("getSourceCode exposes text, lines and first token", () => {
  const result = call("sourceSnapshot", {
    code: "// head\nconst total = 1 + 2;\n",
    config: [{ languageOptions: { ecmaVersion: 2024 } }],
    filename: "input.js",
    index: 14,
    loc: { line: 2, column: 6 },
  });
  assert.equal(result.text, "// head\nconst total = 1 + 2;\n");
  assert.deepEqual(result.lines, ["// head", "const total = 1 + 2;", ""]);
  assert.equal(result.getText, result.text);
  assert.equal(result.firstToken, "const");
  assert.equal(result.isSourceCode, true);
});

test("getSourceCode converts locations and returns comments", () => {
  const result = call("sourceSnapshot", {
    code: "// head\nconst total = 1 + 2;\n",
    config: [{ languageOptions: { ecmaVersion: 2024 } }],
    filename: "input.js",
    index: 14,
    loc: { line: 2, column: 6 },
  });
  assert.deepEqual(result.loc, { line: 2, column: 6 });
  assert.equal(result.reverseIndex, 14);
  assert.deepEqual(result.comments, [{
    type: "Line",
    value: " head",
    loc: { start: { line: 1, column: 0 }, end: { line: 1, column: 7 } },
  }]);
});

test("SourceCode.splitLines recognizes CRLF, LF and CR", () => {
  assert.deepEqual(call("splitLines", { text: "a\r\nb\nc\r" }), ["a", "b", "c", ""]);
});

test("ESLint.lintText returns ordered counts and diagnostics", () => {
  const result = call("lintText", {
    options: {
      overrideConfigFile: true,
      overrideConfig: [{ rules: { eqeqeq: "error", "no-unused-vars": "warn" } }],
    },
    code: "const unused = 1; if (value == 1) {}",
    lintOptions: { filePath: "input.js", warnIgnored: false },
  });
  assert.deepEqual({
    filePath: result.filePath,
    errorCount: result.errorCount,
    warningCount: result.warningCount,
    fixableErrorCount: result.fixableErrorCount,
    fixableWarningCount: result.fixableWarningCount,
    output: result.output,
  }, {
    filePath: "input.js",
    errorCount: 1,
    warningCount: 1,
    fixableErrorCount: 0,
    fixableWarningCount: 0,
    output: null,
  });
  assert.deepEqual(result.messages.map(({ ruleId, severity, column }) => ({ ruleId, severity, column })), [
    { ruleId: "no-unused-vars", severity: 1, column: 7 },
    { ruleId: "eqeqeq", severity: 2, column: 29 },
  ]);
});

test("ESLint.lintText with fix returns output and removes fixed messages", () => {
  const result = call("lintText", {
    options: {
      fix: true,
      overrideConfigFile: true,
      overrideConfig: [{ rules: { semi: ["error", "always"] } }],
    },
    code: "const x = 1\n",
    lintOptions: { filePath: "fix.js" },
  });
  assert.equal(result.errorCount, 0);
  assert.equal(result.warningCount, 0);
  assert.deepEqual(result.messages, []);
  assert.equal(result.output, "const x = 1;\n");
});

test("eslint/config defineConfig flattens config arguments", () => {
  const result = call("configHelpers", {
    configs: [
      { rules: { eqeqeq: "error" } },
      { files: ["**/*.js"], rules: { semi: "warn" } },
    ],
    ignores: ["dist/**"],
    name: "build output",
  });
  assert.deepEqual(result.keys, ["defineConfig", "globalIgnores", "includeIgnoreFile"]);
  assert.deepEqual(result.types, {
    defineConfig: "function",
    globalIgnores: "function",
    includeIgnoreFile: "function",
  });
  assert.deepEqual(result.defined, [
    { rules: { eqeqeq: "error" } },
    { files: ["**/*.js"], rules: { semi: "warn" } },
  ]);
});

test("eslint/config globalIgnores creates a named global ignore config", () => {
  const result = call("configHelpers", {
    configs: [{}],
    ignores: ["dist/**", "coverage/**"],
    name: "generated output",
  });
  assert.deepEqual(result.ignored, {
    name: "generated output",
    ignores: ["dist/**", "coverage/**"],
  });
});

test("use-at-your-own-risk exposes the frozen built-in rule map", () => {
  const result = call("builtinRule", { ruleName: "eqeqeq" });
  assert.deepEqual(result.keys, ["builtinRules", "shouldUseFlatConfig"]);
  assert.equal(result.size, 292);
  assert.equal(result.exists, true);
});

test("the eqeqeq built-in rule exposes stable metadata", () => {
  const result = call("builtinRule", { ruleName: "eqeqeq" });
  assert.deepEqual(result.meta, {
    type: "suggestion",
    fixable: "code",
    messages: {
      unexpected: "Expected '{{expectedOperator}}' and instead saw '{{actualOperator}}'.",
      replaceOperator: "Use '{{expectedOperator}}' instead of '{{actualOperator}}'.",
    },
  });
});
