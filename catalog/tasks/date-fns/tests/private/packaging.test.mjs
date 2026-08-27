import assert from "node:assert/strict";
import test from "node:test";
import { packageManifest } from "./test_client.mjs";

test("package identity and ESM root export", () => {
  const manifest = packageManifest();
  assert.equal(manifest.name, "date-fns");
  assert.equal(manifest.version, "4.4.0");
  assert.equal(manifest.type, "module");
  assert.ok(manifest.root, "the package root must be exported");
});
