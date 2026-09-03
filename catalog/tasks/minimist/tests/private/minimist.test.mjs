import assert from "node:assert/strict";
import test from "node:test";
import { exportProbe, parse, prototypeProbe } from "./test_client.mjs";

test("package root exports a working CommonJS parser function", () => {
  assert.deepEqual(exportProbe(), { type: "function" });
  assert.deepEqual(parse([]), { _: [] });
});

test("empty arguments create an empty positional list", () => {
  assert.deepEqual(parse([]), { _: [] });
});

test("long flags capture following values and positionals", () => {
  assert.deepEqual(parse(["--host", "localhost", "file"]), { _: ["file"], host: "localhost" });
});

test("long equals values and numeric conversion", () => {
  assert.deepEqual(parse(["--port=8080", "--ratio", "1.5", "--hex", "0x10"]), {
    _: [],
    port: 8080,
    ratio: 1.5,
    hex: 16,
  });
});

test("long negation and a bare flag", () => {
  assert.deepEqual(parse(["--no-color", "--verbose"]), { _: [], color: false, verbose: true });
});

test("repeated non-boolean values retain encounter order", () => {
  assert.deepEqual(parse(["--tag", "a", "--tag", "b", "--tag=c"]), { _: [], tag: ["a", "b", "c"] });
});

test("short flags group and final short flag captures a following value", () => {
  assert.deepEqual(parse(["-cats", "meow"]), { _: [], c: true, a: true, t: true, s: "meow" });
});

test("short flags accept numeric and attached values", () => {
  assert.deepEqual(parse(["-n123", "-I/path", "-s=value"]), {
    _: [],
    n: 123,
    I: "/path",
    s: "value",
  });
});

test("plain numeric positionals use JavaScript number conversion", () => {
  assert.deepEqual(parse(["123", "+3.5", "4e2", "text"]), { _: [123, 3.5, 400, "text"] });
});

test("string options preserve numeric text and empty values", () => {
  assert.deepEqual(parse(["--id", "000123", "--empty"], { string: ["id", "empty"] }), {
    _: [],
    id: "000123",
    empty: "",
  });
});

test("declared booleans initialize and consume literal false", () => {
  assert.deepEqual(parse(["--verbose", "false", "rest"], {
    boolean: ["verbose", "quiet"],
    default: { verbose: true },
  }), { _: ["rest"], verbose: false, quiet: false });
});

test("all-long-boolean mode leaves a following positional", () => {
  assert.deepEqual(parse(["--flag", "value", "--other"], { boolean: true }), {
    _: ["value"],
    flag: true,
    other: true,
  });
});

test("aliases mirror assigned values", () => {
  assert.deepEqual(parse(["-v", "42"], { alias: { verbose: "v" } }), {
    _: [],
    v: 42,
    verbose: 42,
  });
});

test("string declarations apply through aliases", () => {
  assert.deepEqual(parse(["--verbose", "0007"], {
    alias: { verbose: "v" },
    string: "verbose",
  }), { _: [], verbose: "0007", v: "0007" });
});

test("defaults apply only to absent keys and mirror aliases", () => {
  assert.deepEqual(parse(["--port", "42"], {
    alias: { port: "p" },
    default: { port: 80, host: "localhost" },
  }), { _: [], port: 42, p: 42, host: "localhost" });
});

test("dotted flags and defaults create nested plain objects", () => {
  assert.deepEqual(parse(["--db.port", "5432"], {
    alias: { "db.port": "database.port" },
    default: { "db.host": "localhost" },
  }), {
    _: [],
    db: { port: 5432, host: "localhost" },
    database: { port: 5432 },
  });
});

test("trailing arguments join positionals by default", () => {
  assert.deepEqual(parse(["--name", "n", "--", "--not-a-flag", "2"]), {
    _: ["--not-a-flag", "2"],
    name: "n",
  });
});

test("trailing arguments can be retained under the double-dash key", () => {
  assert.deepEqual(parse(["--name", "n", "--", "--not-a-flag", "2"], { "--": true }), {
    _: [],
    name: "n",
    "--": ["--not-a-flag", "2"],
  });
});

test("stopEarly preserves later tokens without flag parsing", () => {
  assert.deepEqual(parse(["--name", "n", "first", "2", "--later"], { stopEarly: true }), {
    _: ["first", "2", "--later"],
    name: "n",
  });
});

test("prototype-shaped keys do not pollute global prototypes", () => {
  assert.deepEqual(prototypeProbe([
    "--__proto__.polluted", "yes",
    "--constructor.prototype.polluted", "yes",
  ]), {
    result: { _: [] },
    objectPrototypeSafe: true,
    functionPrototypeSafe: true,
    stringPrototypeSafe: true,
  });
});
