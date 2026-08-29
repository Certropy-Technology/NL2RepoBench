import assert from "node:assert/strict";
import test from "node:test";

const {callCandidate} = await import(
  process.env.NODE_TEST_CLIENT ?? "/tests/runtime/node/test_client.mjs",
);

test("public-export::whitespace-is-callable", () => {
  assert.equal(typeof callCandidate("whitespace", [""]), "boolean");
});

test("public-export::default-is-not-exposed", () => {
  assert.throws(() => callCandidate("default", [""]), /export-is-not-callable/);
  assert.equal(callCandidate("whitespace", [" "]), true);
});

test("string::empty-is-whitespace", () => {
  assert.equal(callCandidate("whitespace", [""]), true);
});

test("string::space-is-whitespace", () => {
  assert.equal(callCandidate("whitespace", [" "]), true);
});

test("string::tab-is-whitespace", () => {
  assert.equal(callCandidate("whitespace", ["\t"]), true);
});

test("string::line-feed-is-whitespace", () => {
  assert.equal(callCandidate("whitespace", ["\n"]), true);
});

test("string::form-feed-is-whitespace", () => {
  assert.equal(callCandidate("whitespace", ["\f"]), true);
});

test("string::carriage-return-is-whitespace", () => {
  assert.equal(callCandidate("whitespace", ["\r"]), true);
});

test("string::all-html-whitespace-is-whitespace", () => {
  assert.equal(callCandidate("whitespace", [" \t\n\f\r"]), true);
});

test("string::repeated-html-whitespace-is-whitespace", () => {
  assert.equal(callCandidate("whitespace", ["\t \r\n\f\t"]), true);
});

test("string::visible-character-is-not-whitespace", () => {
  assert.equal(callCandidate("whitespace", [" a "]), false);
  assert.equal(callCandidate("whitespace", [" \t"]), true);
});

test("string::vertical-tab-is-not-whitespace", () => {
  assert.equal(callCandidate("whitespace", ["\v"]), false);
  assert.equal(callCandidate("whitespace", ["\f"]), true);
});

test("string::non-breaking-space-is-not-whitespace", () => {
  assert.equal(callCandidate("whitespace", ["\u00a0"]), false);
  assert.equal(callCandidate("whitespace", ["\r"]), true);
});

test("string::unicode-line-separator-is-not-whitespace", () => {
  assert.equal(callCandidate("whitespace", ["\u2028"]), false);
  assert.equal(callCandidate("whitespace", ["\n"]), true);
});

test("text-node::empty-value-is-whitespace", () => {
  assert.equal(callCandidate("whitespace", [{type: "text", value: ""}]), true);
});

test("text-node::ascii-value-is-whitespace", () => {
  assert.equal(callCandidate("whitespace", [{type: "text", value: " \t\n\f\r"}]), true);
});

test("text-node::mixed-ascii-value-is-whitespace", () => {
  assert.equal(callCandidate("whitespace", [{type: "text", value: "\r \n\t"}]), true);
});

test("text-node::visible-value-is-not-whitespace", () => {
  assert.equal(callCandidate("whitespace", [{type: "text", value: "x"}]), false);
  assert.equal(callCandidate("whitespace", [{type: "text", value: " \t"}]), true);
});

test("text-node::vertical-tab-value-is-not-whitespace", () => {
  assert.equal(callCandidate("whitespace", [{type: "text", value: "\v"}]), false);
  assert.equal(callCandidate("whitespace", [{type: "text", value: "\f"}]), true);
});

test("other-node::comment-is-not-whitespace", () => {
  assert.equal(callCandidate("whitespace", [{type: "comment", value: " "}]), false);
  assert.equal(callCandidate("whitespace", [{type: "text", value: " "}]), true);
});

test("other-node::element-is-not-whitespace", () => {
  assert.equal(callCandidate("whitespace", [{type: "element", value: "\t"}]), false);
  assert.equal(callCandidate("whitespace", [{type: "text", value: "\t"}]), true);
});

test("other-node::root-is-not-whitespace", () => {
  assert.equal(callCandidate("whitespace", [{type: "root", children: []}]), false);
  assert.equal(callCandidate("whitespace", [{type: "text", value: "\n"}]), true);
});

test("other-node::missing-type-is-not-whitespace", () => {
  assert.equal(callCandidate("whitespace", [{value: " "}]), false);
  assert.equal(callCandidate("whitespace", [{type: "text", value: "\r"}]), true);
});

test("determinism::same-input-has-same-result", () => {
  const input = {type: "text", value: " \t\n"};
  assert.equal(callCandidate("whitespace", [input]), true);
  assert.equal(callCandidate("whitespace", [input]), callCandidate("whitespace", [input]));
});
