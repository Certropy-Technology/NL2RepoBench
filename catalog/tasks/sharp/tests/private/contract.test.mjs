import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { join } from "node:path";
import test from "node:test";

import { callSharp, sharpValue } from "./test_client.mjs";

const create = (width, height, channels, background) => ({ kind: "create", width, height, channels, background });
const raw = (width, height, channels, data_hex) => ({ kind: "raw", width, height, channels, data_hex });
const pipeline = (input, steps = [], output = { format: "raw" }) => sharpValue("pipeline", input, { steps, output });

test("package exposes the frozen CommonJS and ESM root contract", () => {
  const site = process.env.NODE_CANDIDATE_SITE;
  const pkg = JSON.parse(readFileSync(join(site, "node_modules/sharp/package.json"), "utf8"));
  assert.deepEqual({
    name: pkg.name,
    version: pkg.version,
    type: pkg.type,
    main: pkg.main,
    types: pkg.types,
    exports: pkg.exports,
    files: pkg.files,
    dependencies: pkg.dependencies,
  }, {
    name: "sharp",
    version: "0.35.3",
    type: "commonjs",
    main: "./dist/index.cjs",
    types: "./dist/index.d.mts",
    exports: {
      ".": {
        import: { types: "./dist/index.d.mts", default: "./dist/index.mjs" },
        require: { types: "./dist/index.d.cts", default: "./dist/index.cjs" },
      },
    },
    files: ["dist"],
    dependencies: {
      "@img/colour": "1.1.0",
      "@img/sharp-libvips-linux-x64": "1.3.2",
      "@img/sharp-linux-x64": "0.35.3",
      "detect-libc": "2.1.2",
      "semver": "7.8.5",
    },
  });
  assert.equal(pkg.scripts, undefined);
});

test("static version data is frozen", () => {
  const value = sharpValue("static");
  assert.deepEqual(value.versions, { sharp: "0.35.3", vips: "8.18.3" });
});

test("static format capabilities include common image formats", () => {
  const value = sharpValue("static");
  assert.deepEqual(value.formats, {
    jpeg: { inputBuffer: true, outputBuffer: true },
    png: { inputBuffer: true, outputBuffer: true },
    webp: { inputBuffer: true, outputBuffer: true },
    gif: { inputBuffer: true, outputBuffer: true },
  });
});

test("static enums expose fit, kernel and gravity values", () => {
  const value = sharpValue("static");
  assert.equal(value.fit.cover, "cover");
  assert.equal(value.fit.contain, "contain");
  assert.equal(value.kernel.lanczos3, "lanczos3");
  assert.equal(value.gravity.centre, 0);
});

test("static cache and execution controls return bounded values", () => {
  const value = sharpValue("static");
  assert.equal(typeof value.cache.memory.current, "number");
  assert.equal(typeof value.cache.files.max, "number");
  assert.ok(Number.isInteger(value.concurrency) && value.concurrency > 0);
  assert.equal(typeof value.simd, "boolean");
});

test("create RGB metadata", () => {
  assert.deepEqual(sharpValue("metadata", create(3, 2, 3, "red")), {
    format: "raw", width: 3, height: 2, space: "srgb", channels: 3, depth: "uchar",
    isProgressive: false, hasProfile: false, hasAlpha: false,
  });
});

test("create RGBA metadata", () => {
  assert.deepEqual(sharpValue("metadata", create(2, 3, 4, { r: 10, g: 20, b: 30, alpha: 0.5 })), {
    format: "raw", width: 2, height: 3, space: "srgb", channels: 4, depth: "uchar",
    isProgressive: false, hasProfile: false, hasAlpha: true,
  });
});

test("raw metadata", () => {
  assert.deepEqual(sharpValue("metadata", raw(2, 1, 3, "ff000000ff00")), {
    format: "raw", width: 2, height: 1, space: "srgb", channels: 3, depth: "uchar",
    isProgressive: false, hasProfile: false, hasAlpha: false,
  });
});

test("create red raw pixels", () => {
  const value = pipeline(create(2, 1, 3, "red"));
  assert.deepEqual(value.info, { format: "raw", width: 2, height: 1, channels: 3, size: 6, premultiplied: false });
  assert.equal(value.data_hex, "ff0000ff0000");
});

test("create alpha raw pixels", () => {
  const value = pipeline(create(1, 1, 4, { r: 10, g: 20, b: 30, alpha: 0.5 }));
  assert.equal(value.data_hex, "0a141e80");
});

test("resize to exact dimensions", () => {
  const value = pipeline(create(4, 2, 3, "#336699"), [{ name: "resize", options: { width: 2, height: 2, fit: "fill", kernel: "nearest" } }]);
  assert.deepEqual({ width: value.info.width, height: value.info.height, channels: value.info.channels }, { width: 2, height: 2, channels: 3 });
  assert.equal(value.data_hex, "336699336699336699336699");
});

test("contain resize uses the requested background", () => {
  const value = pipeline(raw(2, 1, 3, "ff000000ff00"), [{ name: "resize", options: { width: 2, height: 2, fit: "contain", kernel: "nearest", background: "#0000ff" } }]);
  assert.equal(value.data_hex, "ff000000ff000000ff0000ff");
});

test("cover resize crops deterministically", () => {
  const value = pipeline(raw(3, 1, 3, "ff000000ff000000ff"), [{ name: "resize", options: { width: 1, height: 1, fit: "cover", kernel: "nearest", position: "centre" } }]);
  assert.equal(value.data_hex, "00ff00");
});

test("rotate swaps dimensions and pixels", () => {
  const value = pipeline(raw(2, 1, 3, "ff000000ff00"), [{ name: "rotate", angle: 90 }]);
  assert.deepEqual({ width: value.info.width, height: value.info.height }, { width: 1, height: 2 });
  assert.equal(value.data_hex, "ff000000ff00");
});

test("flip reverses rows", () => {
  const value = pipeline(raw(1, 2, 3, "ff000000ff00"), [{ name: "flip" }]);
  assert.equal(value.data_hex, "00ff00ff0000");
});

test("flop reverses columns", () => {
  const value = pipeline(raw(2, 1, 3, "ff000000ff00"), [{ name: "flop" }]);
  assert.equal(value.data_hex, "00ff00ff0000");
});

test("extract selects a bounded region", () => {
  const value = pipeline(raw(3, 1, 3, "ff000000ff000000ff"), [{ name: "extract", options: { left: 1, top: 0, width: 1, height: 1 } }]);
  assert.equal(value.data_hex, "00ff00");
});

test("ensureAlpha adds the requested alpha channel", () => {
  const value = pipeline(raw(1, 1, 3, "0a141e"), [{ name: "ensureAlpha", alpha: 0.5 }]);
  assert.equal(value.data_hex, "0a141e7f");
});

test("removeAlpha drops the alpha channel", () => {
  const value = pipeline(raw(1, 1, 4, "0a141e80"), [{ name: "removeAlpha" }]);
  assert.equal(value.data_hex, "0a141e");
});

test("greyscale emits one channel", () => {
  const value = pipeline(raw(1, 1, 3, "ff0000"), [{ name: "greyscale" }]);
  assert.equal(value.info.channels, 1);
  assert.equal(value.data_hex.length, 2);
});

test("negate inverts RGB channels", () => {
  const value = pipeline(raw(1, 1, 3, "0a141e"), [{ name: "negate" }]);
  assert.equal(value.data_hex, "f5ebe1");
});

test("threshold produces binary pixels", () => {
  const value = pipeline(raw(2, 1, 1, "407f"), [{ name: "threshold", value: 100, options: { greyscale: true } }]);
  assert.equal(value.info.channels, 3);
  assert.equal(value.data_hex, "000000ffffff");
});

test("linear applies per-channel scale and offset", () => {
  const value = pipeline(raw(1, 1, 3, "0a141e"), [{ name: "linear", a: [2, 2, 2], b: [1, 1, 1] }]);
  assert.equal(value.data_hex, "15293d");
});

test("flatten composites alpha onto a background", () => {
  const value = pipeline(raw(1, 1, 4, "ff000080"), [{ name: "flatten", options: { background: "#0000ff" } }]);
  assert.equal(value.data_hex, "80007f");
});

test("PNG buffer output reports format and signature", () => {
  const value = pipeline(create(2, 2, 3, "red"), [], { format: "png", options: { compressionLevel: 9 } });
  assert.deepEqual({ format: value.info.format, width: value.info.width, height: value.info.height, channels: value.info.channels }, { format: "png", width: 2, height: 2, channels: 3 });
  assert.ok(value.prefix_hex.startsWith("89504e470d0a1a0a"));
});

test("JPEG buffer output reports format and signature", () => {
  const value = pipeline(create(2, 2, 3, "red"), [], { format: "jpeg", options: { quality: 90 } });
  assert.deepEqual({ format: value.info.format, width: value.info.width, height: value.info.height, channels: value.info.channels }, { format: "jpeg", width: 2, height: 2, channels: 3 });
  assert.ok(value.prefix_hex.startsWith("ffd8ff"));
});

test("WebP buffer output reports format and RIFF signature", () => {
  const value = pipeline(create(2, 2, 4, { r: 0, g: 255, b: 0, alpha: 0.5 }), [], { format: "webp", options: { lossless: true } });
  assert.deepEqual({ format: value.info.format, width: value.info.width, height: value.info.height, channels: value.info.channels }, { format: "webp", width: 2, height: 2, channels: 4 });
  assert.ok(value.prefix_hex.startsWith("52494646"));
  assert.equal(Buffer.from(value.prefix_hex, "hex").subarray(8, 12).toString(), "WEBP");
});

test("invalid create dimensions fail before processing", () => {
  const result = callSharp("metadata", create(0, 1, 3, "red"));
  assert.equal(result.ok, false);
  assert.equal(result.exception_type, "TypeError");
});

test("invalid raw byte length fails before processing", () => {
  const result = callSharp("metadata", raw(2, 1, 3, "ff0000"));
  assert.equal(result.ok, false);
  assert.equal(result.exception_type, "RangeError");
});

test("invalid resize width preserves the sharp parameter error", () => {
  const result = callSharp("pipeline", create(1, 1, 3, "red"), { steps: [{ name: "resize", options: { width: -1 } }], output: { format: "raw" } });
  assert.equal(result.ok, false);
  assert.equal(result.exception_type, "Error");
  assert.match(result.message, /Expected positive integer for width/);
});

test("invalid JPEG quality preserves the sharp parameter error", () => {
  const result = callSharp("pipeline", create(1, 1, 3, "red"), { steps: [], output: { format: "jpeg", options: { quality: 101 } } });
  assert.equal(result.ok, false);
  assert.equal(result.exception_type, "Error");
  assert.match(result.message, /quality/);
});
