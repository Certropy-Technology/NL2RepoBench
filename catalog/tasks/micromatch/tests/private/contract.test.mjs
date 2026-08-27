import assert from "node:assert/strict";
import test from "node:test";

const {
  callCandidate,
  callbackTrace,
  inspectSurface,
  parseSummary,
  runMatcher,
  runRegex,
  scanSummary,
} = await import(process.env.NODE_TEST_CLIENT ?? "/tests/private/test_client.mjs");

test("exports the CommonJS callable and documented method aliases", () => {
  const surface = inspectSurface();
  assert.equal(surface.callableDefault, true);
  assert.deepEqual(surface.aliases, { match: true, any: true });
  assert.ok(Object.values(surface.types).every(type => type === "function"));
});

test("match filters a list with one pattern", () => {
  assert.deepEqual(callCandidate("match", [["a.js", "a.txt", "b.js"], "*.js"]), ["a.js", "b.js"]);
});

test("match normalizes a scalar list", () => {
  assert.deepEqual(callCandidate("match", ["a.js", "*.js"]), ["a.js"]);
});

test("match preserves pattern-group then input order", () => {
  assert.deepEqual(callCandidate("match", [["a.js", "a.txt", "b.md"], ["*.md", "*.js"]]), ["b.md", "a.js"]);
});

test("match removes duplicate inputs and duplicate matches", () => {
  assert.deepEqual(callCandidate("match", [["a.js", "a.js", "b.js"], ["*.js", "a.*"]]), ["a.js", "b.js"]);
});

test("match applies negative patterns", () => {
  assert.deepEqual(callCandidate("match", [["a.js", "a.test.js", "b.js"], ["*.js", "!*.test.js"]]), ["a.js", "b.js"]);
});

test("match with only negative patterns starts from all inputs", () => {
  assert.deepEqual(callCandidate("match", [["a.js", "a.txt", "b.js"], "!*.txt"]), ["a.js", "b.js"]);
});

test("a later positive pattern can re-include an omitted input", () => {
  assert.deepEqual(callCandidate("match", [["a.js", "b.js"], ["*.js", "!a.js", "a.js"]]), ["a.js", "b.js"]);
});

test("wildcards exclude leading dots by default", () => {
  assert.deepEqual(callCandidate("match", [[".gitignore", "a.js"], "*"]), ["a.js"]);
});

test("dot includes leading-dot names", () => {
  assert.deepEqual(callCandidate("match", [[".gitignore", "a.js"], "*", { dot: true }]), [".gitignore", "a.js"]);
});

test("nocase enables case-insensitive matching", () => {
  assert.deepEqual(callCandidate("match", [["A.JS", "a.txt"], "*.js", { nocase: true }]), ["A.JS"]);
});

test("basename matches the final path segment", () => {
  assert.deepEqual(callCandidate("match", [["src/a.js", "src/a.txt"], "*.js", { basename: true }]), ["src/a.js"]);
});

test("matchBase aliases basename matching", () => {
  assert.deepEqual(callCandidate("match", [["src/a.js", "src/a.txt"], "*.js", { matchBase: true }]), ["src/a.js"]);
});

test("noext disables extglob syntax", () => {
  assert.deepEqual(callCandidate("match", [["a.js", "a.txt"], "*.@(js|md)", { noext: true }]), []);
});

test("nonegate treats a leading exclamation mark literally", () => {
  assert.deepEqual(callCandidate("match", [["!a.js", "a.js"], "!a.js", { nonegate: true }]), ["!a.js"]);
});

test("noglobstar treats a double star as ordinary stars", () => {
  assert.deepEqual(callCandidate("match", [["a/b.js", "a/x/b.js"], "a/**/b.js", { noglobstar: true }]), ["a/x/b.js"]);
});

test("nobrace disables brace alternation", () => {
  assert.deepEqual(callCandidate("match", [["a.js", "b.js"], "{a,b}.js", { nobrace: true }]), []);
});

test("nonull returns an unmatched pattern", () => {
  assert.deepEqual(callCandidate("match", [["a.js"], "*.md", { nonull: true }]), ["*.md"]);
});

test("nullglob aliases nonull fallback behavior", () => {
  assert.deepEqual(callCandidate("match", [[], "foo\\*bar", { nullglob: true, unescape: true }]), ["foo*bar"]);
});

test("unescape removes escapes from a returned nonull pattern", () => {
  assert.deepEqual(callCandidate("match", [[], "foo\\*bar", { nonull: true, unescape: true }]), ["foo*bar"]);
});

test("ignore removes otherwise matching inputs", () => {
  assert.deepEqual(callCandidate("match", [["a.js", "a.test.js"], "*.js", { ignore: "*.test.js" }]), ["a.js"]);
});

test("ignore accepts an array of patterns", () => {
  assert.deepEqual(callCandidate("match", [["a.js", "a.test.js", "a.spec.js"], "*.js", { ignore: ["*.test.js", "*.spec.js"] }]), ["a.js"]);
});

test("globstar spans zero or multiple path segments", () => {
  assert.deepEqual(callCandidate("match", [["a/b.js", "a/x/b.js"], "a/**/b.js"]), ["a/b.js", "a/x/b.js"]);
});

test("extglobs support alternatives", () => {
  assert.deepEqual(callCandidate("match", [["a.js", "a.txt", "a.md"], "a.@(js|md)"]), ["a.js", "a.md"]);
});

test("question mark matches exactly one non-separator character", () => {
  assert.deepEqual(callCandidate("match", [["a1.js", "a12.js", "a/.js"], "a?.js"]), ["a1.js"]);
});

test("bracket character classes constrain one character", () => {
  assert.deepEqual(callCandidate("match", [["a1", "ab", "aB"], "a[a-z]"]), ["ab"]);
});

test("POSIX character classes are supported", () => {
  assert.deepEqual(callCandidate("match", [["a1", "aa"], "a[[:digit:]]"]), ["a1"]);
});

test("matcher returns a reusable predicate", () => {
  assert.deepEqual(runMatcher("*.js", {}, ["a.js", "a.txt", ".a.js"]), [true, false, false]);
});

test("matcher forwards options", () => {
  assert.deepEqual(runMatcher("*.js", { nocase: true }, ["A.JS", "A.TXT"]), [true, false]);
});

test("isMatch accepts an array of patterns", () => {
  assert.equal(callCandidate("isMatch", ["src/a.js", ["*.txt", "**/*.js"]]), true);
});

test("isMatch returns false when no pattern matches", () => {
  assert.equal(callCandidate("isMatch", ["a.txt", ["*.js", "*.md"]]), false);
});

test("any behaves as the isMatch alias", () => {
  assert.equal(callCandidate("any", ["a.txt", ["*.js", "*.txt"]]), true);
});

test("not returns inputs excluded by all patterns", () => {
  assert.deepEqual(callCandidate("not", [["a.js", "a.txt", "b.js"], ["*.js", "b.*"]]), ["a.txt"]);
});

test("not preserves unmatched input order", () => {
  assert.deepEqual(callCandidate("not", [["b.txt", "a.txt"], "*.js"]), ["b.txt", "a.txt"]);
});

test("contains supports a glob fragment", () => {
  assert.equal(callCandidate("contains", ["aa/bb/cc", "*b"]), true);
});

test("contains detects a literal substring after a dot-slash prefix", () => {
  assert.equal(callCandidate("contains", ["./aa/bb", "aa/b"]), true);
});

test("contains returns false for empty strings and dot-slash", () => {
  assert.equal(callCandidate("contains", ["./", "*"]), false);
});

test("contains accepts an array of candidate patterns", () => {
  assert.equal(callCandidate("contains", ["foo/bar.js", ["*.txt", "bar.*"]]), true);
});

test("contains rejects a non-string input", () => {
  assert.throws(() => callCandidate("contains", [[], "*"]), /TypeError: Expected a string/);
});

test("matchKeys filters only own top-level keys", () => {
  assert.deepEqual(callCandidate("matchKeys", [{ aa: 1, ab: 2, ba: 3 }, "a*"]), { aa: 1, ab: 2 });
});

test("matchKeys rejects a non-object first argument", () => {
  assert.throws(() => callCandidate("matchKeys", [[], "*"]), /Expected the first argument to be an object/);
});

test("some returns true when one item matches one pattern", () => {
  assert.equal(callCandidate("some", [["a.js", "b.txt"], ["*.md", "*.txt"]]), true);
});

test("some returns false when no item matches", () => {
  assert.equal(callCandidate("some", [["a.js", "b.txt"], "*.md"]), false);
});

test("every returns true when all items match every pattern", () => {
  assert.equal(callCandidate("every", [["a.js", "b.js"], ["*.js"]]), true);
});

test("every evaluates negative patterns as predicates", () => {
  assert.equal(callCandidate("every", [["a.js", "b.js"], ["*.js", "!a.js"]]), false);
});

test("all returns true when one string matches every pattern", () => {
  assert.equal(callCandidate("all", ["foo.js", ["*.js", "f*", "!bar*"]]), true);
});

test("all returns false when any pattern rejects the string", () => {
  assert.equal(callCandidate("all", ["foo.js", ["*.js", "!foo.js"]]), false);
});

test("all rejects a non-string input", () => {
  assert.throws(() => callCandidate("all", [[], "*"]), /TypeError: Expected a string/);
});

test("capture returns wildcard and group captures", () => {
  assert.deepEqual(callCandidate("capture", ["src/*/(*).js", "src/lib/file.js"]), ["lib", "file", "file"]);
});

test("capture returns undefined for a non-match", () => {
  assert.equal(callCandidate("capture", ["src/*.js", "test/a.js"]), undefined);
});

test("makeRe returns a regex with matching glob behavior", () => {
  assert.deepEqual(runRegex("*.js", {}, ["a.js", "a.txt"]), [true, false]);
});

test("makeRe excludes leading-dot basenames by default", () => {
  assert.deepEqual(runRegex("*.js", {}, ["a.js", ".a.js"]), [true, false]);
});

test("scan exposes stable prefix, base, glob, and classification fields", () => {
  assert.deepEqual(scanSummary("!src/**/a*.js"), {
    input: "!src/**/a*.js",
    prefix: "!",
    base: "src",
    glob: "**/a*.js",
    isGlob: true,
    isGlobstar: false,
    isExtglob: false,
    negated: true,
  });
});

test("parse expands braces before returning parse states", () => {
  assert.deepEqual(parseSummary("{a,b}/*.js"), [{
    input: "(a|b)/*.js",
    output: "(a|b)\\/(?!\\.)(?=.)[^/]*?\\.js",
    negated: false,
    prefix: "",
  }]);
});

test("parse accepts an array and preserves pattern order", () => {
  const states = parseSummary(["*.js", "!a*"]);
  assert.deepEqual(states.map(state => [state.input, state.negated, state.prefix]), [
    ["*.js", false, ""],
    ["!a*", true, ""],
  ]);
});

test("braces compiles alternatives without expanding them", () => {
  assert.deepEqual(callCandidate("braces", ["foo/{a,b}/bar"]), ["foo/(a|b)/bar"]);
});

test("braces expands alternatives when requested", () => {
  assert.deepEqual(callCandidate("braces", ["foo/{a,b}/bar", { expand: true }]), ["foo/a/bar", "foo/b/bar"]);
});

test("braces honors nobrace", () => {
  assert.deepEqual(callCandidate("braces", ["foo/{a,b}", { nobrace: true }]), ["foo/{a,b}"]);
});

test("braces returns an unchanged pattern when no complete braces exist", () => {
  assert.deepEqual(callCandidate("braces", ["foo/{a"]), ["foo/{a"]);
});

test("braces rejects a non-string pattern", () => {
  assert.throws(() => callCandidate("braces", [[], {}]), /TypeError: Expected a string/);
});

test("braceExpand expands numeric ranges", () => {
  assert.deepEqual(callCandidate("braceExpand", ["file{1..3}.js"]), ["file1.js", "file2.js", "file3.js"]);
});

test("braceExpand rejects a non-string pattern", () => {
  assert.throws(() => callCandidate("braceExpand", [[], {}]), /TypeError: Expected a string/);
});

test("hasBraces detects a complete brace pair", () => {
  assert.equal(callCandidate("hasBraces", ["a/{b,c}"]), true);
});

test("hasBraces rejects an incomplete brace pair", () => {
  assert.equal(callCandidate("hasBraces", ["a/{b"]), false);
});

test("failglob throws when the result is empty", () => {
  assert.throws(() => callCandidate("match", [["a.js"], "*.md", { failglob: true }]), /No matches found/);
});

test("matching callbacks receive deterministic result states", () => {
  assert.deepEqual(callbackTrace(["a.js", "a.txt"], ["*", "!*.txt"], {}), {
    value: ["a.js"],
    events: {
      result: [
        ["*", "a.js", "a.js", true],
        ["*", "a.txt", "a.txt", true],
        ["!*.txt", "a.js", "a.js", true],
        ["!*.txt", "a.txt", "a.txt", false],
      ],
      match: [
        ["*", "a.js", "a.js", true],
        ["*", "a.txt", "a.txt", true],
        ["!*.txt", "a.js", "a.js", true],
      ],
      ignore: [],
    },
  });
});

test("onIgnore receives matcher state for ignored results", () => {
  assert.deepEqual(callbackTrace(["a.js", "a.test.js"], "*.js", { ignore: "*.test.js" }), {
    value: ["a.js"],
    events: {
      result: [
        ["*.js", "a.js", "a.js", true],
        ["*.js", "a.test.js", "a.test.js", true],
      ],
      match: [
        ["*.js", "a.js", "a.js", true],
      ],
      ignore: [["*.js", "a.test.js", "a.test.js", true]],
    },
  });
});
