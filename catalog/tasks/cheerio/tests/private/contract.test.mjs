import assert from "node:assert/strict";
import test from "node:test";
import { call, failure, query } from "./test_client.mjs";

const fruits = '<ul id="fruits"><li class="apple">Apple</li><li class="orange">Orange</li><li class="pear" data-count="3">Pear</li></ul>';
const outer = (html, selector, steps = [], extra = {}) => query(html, selector, { kind: "outerHTMLs" }, steps, extra);

test("package metadata is scripts-stripped and runtime-only", () => {
  const value = call({ operation: "metadata" });
  assert.equal(value.name, "cheerio");
  assert.equal(value.version, "1.2.0");
  assert.equal(value.type, "module");
  assert.equal(value.scripts, null);
  assert.deepEqual(value.devDependencies, []);
  assert.equal(value.rootLoad, true);
  assert.equal(value.slimLoad, true);
  assert.deepEqual(value.utilityNames, ["camelCase", "cssCase", "isHtml"]);
});

test("document loading inserts html head and body", () => {
  assert.equal(query("<title>T</title><p>Hello</p>", "body", { kind: "documentHtml" }), "<html><head><title>T</title></head><body><p>Hello</p></body></html>");
});

test("fragment loading suppresses document wrappers", () => {
  assert.equal(query("<li>A</li><li>B</li>", "li", { kind: "documentHtml" }, [], { isDocument: false }), "<li>A</li><li>B</li>");
});

test("empty input produces an empty document body", () => {
  assert.equal(query("", "body", { kind: "documentHtml" }), "<html><head></head><body></body></html>");
});

test("text decodes entities and preserves Unicode", () => {
  assert.equal(query("<p>Caf&eacute; &amp; 東京 😀</p>", "p", { kind: "text" }), "Café & 東京 😀");
});

test("tag id and class selectors preserve document order", () => {
  assert.deepEqual(outer(fruits, "#fruits > li.pear, #fruits > li.apple"), [
    '<li class="apple">Apple</li>', '<li class="pear" data-count="3">Pear</li>'
  ]);
});

test("descendant and child combinators are distinct", () => {
  const html = '<section><div><span>A</span></div><span>B</span></section>';
  assert.equal(query(html, "section span", { kind: "length" }), 2);
  assert.equal(query(html, "section > span", { kind: "text" }), "B");
});

test("attribute selectors support exact and prefix matching", () => {
  const html = '<a href="https://a.test">A</a><a href="/local">B</a><a>C</a>';
  assert.equal(query(html, 'a[href^="https://"]', { kind: "text" }), "A");
  assert.equal(query(html, 'a[href="/local"]', { kind: "text" }), "B");
});

test("structural and content pseudos select expected elements", () => {
  assert.equal(query(fruits, "li:nth-child(2)", { kind: "text" }), "Orange");
  assert.equal(query(fruits, 'li:contains("Pear")', { kind: "text" }), "Pear");
});

test("malformed table markup receives HTML tree correction", () => {
  const html = "<table><tr><td>A</td></tr></table>";
  assert.equal(query(html, "table", { kind: "html" }), "<tbody><tr><td>A</td></tr></tbody>");
});

test("script and style text participates in textContent", () => {
  assert.equal(query("<div>A<style>.x{}</style><script>go()</script>B</div>", "div", { kind: "text" }), "A.x{}go()B");
});

test("XML mode preserves case and self-closing syntax", () => {
  const value = query('<Root><Item ID="x"/></Root>', "Item", { kind: "documentXml" }, [], { options: { xmlMode: true } });
  assert.equal(value, '<Root><Item ID="x"/></Root>');
});

test("attr reads one attribute or the first element attribute map", () => {
  assert.equal(query(fruits, ".pear", { kind: "attr", name: "data-count" }), "3");
  assert.deepEqual(query(fruits, ".pear", { kind: "attrs" }), { class: "pear", "data-count": "3" });
});

test("attr map sets and null removes attributes on every match", () => {
  const steps = [{ method: "attr", args: [{ title: "fruit", class: null }] }];
  assert.deepEqual(outer(fruits, "li", steps), [
    '<li title="fruit">Apple</li>', '<li title="fruit">Orange</li>', '<li data-count="3" title="fruit">Pear</li>'
  ]);
});

test("prop exposes outerHTML innerHTML and textContent", () => {
  assert.equal(query("<div><b>A</b>B</div>", "div", { kind: "prop", name: "outerHTML" }), "<div><b>A</b>B</div>");
  assert.equal(query("<div><b>A</b>B</div>", "div", { kind: "prop", name: "innerHTML" }), "<b>A</b>B");
  assert.equal(query("<div><b>A</b>B</div>", "div", { kind: "prop", name: "textContent" }), "AB");
});

test("class methods add remove toggle and inspect tokens", () => {
  const steps = [
    { method: "addClass", args: ["fresh ripe"] },
    { method: "removeClass", args: ["pear"] },
    { method: "toggleClass", args: ["ripe"] }
  ];
  assert.equal(query(fruits, ".pear", { kind: "attr", name: "class" }, steps), "fresh");
  assert.equal(query(fruits, ".pear", { kind: "hasClass", name: "pear" }), true);
});

test("css parses and updates inline style declarations", () => {
  const html = '<div style="color: red; width: 10px"></div>';
  assert.equal(query(html, "div", { kind: "css", name: "color" }), "red");
  assert.equal(query(html, "div", { kind: "attr", name: "style" }, [{ method: "css", args: [{ color: "blue", height: "2px" }] }]), "color: blue; width: 10px; height: 2px;");
});

test("val reads inputs and selected options", () => {
  assert.equal(query('<input value="hello">', "input", { kind: "val" }), "hello");
  const html = '<select><option value="a">A</option><option value="b" selected>B</option></select>';
  assert.equal(query(html, "select", { kind: "val" }), "b");
});

test("find searches descendants of the current selection", () => {
  assert.equal(query(fruits, "#fruits", { kind: "text" }, [{ method: "find", args: [".orange"] }]), "Orange");
});

test("parent parents and closest traverse ancestors", () => {
  const html = '<main><section class="box"><p><em>X</em></p></section></main>';
  assert.equal(query(html, "em", { kind: "prop", name: "tagName" }, [{ method: "parent", args: [] }]), "P");
  assert.equal(query(html, "em", { kind: "length" }, [{ method: "parents", args: ["main, section"] }]), 2);
  assert.equal(query(html, "em", { kind: "attr", name: "class" }, [{ method: "closest", args: [".box"] }]), "box");
});

test("next prev and siblings preserve sibling order", () => {
  assert.equal(query(fruits, ".orange", { kind: "text" }, [{ method: "next", args: [] }]), "Pear");
  assert.equal(query(fruits, ".orange", { kind: "text" }, [{ method: "prev", args: [] }]), "Apple");
  assert.equal(query(fruits, ".orange", { kind: "text" }, [{ method: "siblings", args: [] }]), "ApplePear");
});

test("children excludes text while contents includes it", () => {
  const html = '<div>A<span>B</span><!-- C --></div>';
  assert.equal(query(html, "div", { kind: "length" }, [{ method: "children", args: [] }]), 1);
  assert.equal(query(html, "div", { kind: "length" }, [{ method: "contents", args: [] }]), 3);
});

test("filter not is and has use CSS selectors", () => {
  assert.equal(query(fruits, "li", { kind: "text" }, [{ method: "filter", args: [".apple, .pear"] }]), "ApplePear");
  assert.equal(query(fruits, "li", { kind: "text" }, [{ method: "not", args: [".orange"] }]), "ApplePear");
  assert.equal(query(fruits, ".pear", { kind: "is", selector: "li[data-count]" }), true);
  assert.equal(query('<div><b>X</b></div><div>Y</div>', "div", { kind: "length" }, [{ method: "has", args: ["b"] }]), 1);
});

test("first last eq and slice operate on selection order", () => {
  assert.equal(query(fruits, "li", { kind: "text" }, [{ method: "first", args: [] }]), "Apple");
  assert.equal(query(fruits, "li", { kind: "text" }, [{ method: "last", args: [] }]), "Pear");
  assert.equal(query(fruits, "li", { kind: "text" }, [{ method: "eq", args: [-2] }]), "Orange");
  assert.equal(query(fruits, "li", { kind: "text" }, [{ method: "slice", args: [1, 3] }]), "OrangePear");
});

test("end returns the previous selection in a chain", () => {
  const steps = [{ method: "find", args: ["li"] }, { method: "first", args: [] }, { method: "end", args: [] }];
  assert.equal(query(fruits, "#fruits", { kind: "length" }, steps), 3);
});

test("append and prepend insert parsed HTML for each target", () => {
  const steps = [{ method: "prepend", args: ["<i>A</i>"] }, { method: "append", args: ["<b>B</b>"] }];
  assert.equal(query("<div>X</div>", "div", { kind: "html" }, steps), "<i>A</i>X<b>B</b>");
});

test("before and after insert siblings around a selection", () => {
  const steps = [{ method: "before", args: ["<i>A</i>"] }, { method: "after", args: ["<b>B</b>"] }, { method: "parent", args: [] }];
  assert.equal(query("<div><span>X</span></div>", "span", { kind: "html" }, steps), "<i>A</i><span>X</span><b>B</b>");
});

test("remove detaches matches and empty removes children", () => {
  const removed = [{ method: "remove", args: [] }, { method: "end", args: [] }, { method: "parent", args: [] }];
  assert.equal(query("<div><i>A</i><b>B</b></div>", "i", { kind: "documentHtml" }, removed), "<html><head></head><body><div><b>B</b></div></body></html>");
  assert.equal(query("<div><i>A</i></div>", "div", { kind: "html" }, [{ method: "empty", args: [] }]), "");
});

test("html and text setters replace element contents", () => {
  assert.equal(query("<p>old</p>", "p", { kind: "html" }, [{ method: "html", args: ["<b>new</b>"] }]), "<b>new</b>");
  assert.equal(query("<p><b>old</b></p>", "p", { kind: "html" }, [{ method: "text", args: ["<new>"] }]), "&lt;new&gt;");
});

test("wrap and unwrap change the surrounding structure", () => {
  const wrapped = [{ method: "wrap", args: ["<section class=box></section>"] }, { method: "parent", args: [] }];
  assert.equal(query("<div><span>X</span></div>", "span", { kind: "outerHTML" }, wrapped), '<section class="box"><span>X</span></section>');
  const unwrapped = [{ method: "unwrap", args: [] }, { method: "parent", args: [] }];
  assert.equal(query("<main><section><span>X</span></section></main>", "span", { kind: "prop", name: "tagName" }, unwrapped), "MAIN");
});

test("clone creates an independent serialized copy", () => {
  const steps = [{ method: "clone", args: [] }, { method: "attr", args: ["id", "copy"] }];
  assert.equal(query('<div id="original"><b>X</b></div>', "div", { kind: "outerHTML" }, steps), '<div id="copy"><b>X</b></div>');
});

test("document html serializes a doctype and comments", () => {
  const html = '<!doctype html><!--top--><p>X</p>';
  assert.equal(query(html, "p", { kind: "documentHtml" }), '<!DOCTYPE html><!--top--><html><head></head><body><p>X</p></body></html>');
});

test("document text concatenates all descendant text", () => {
  assert.equal(query("<h1>A</h1><p>B <em>C</em></p>", "p", { kind: "documentText" }), "AB C");
});

test("extract maps selectors to text and attributes", () => {
  const map = { title: "h1", links: [{ selector: "a", value: "href" }] };
  assert.deepEqual(query('<h1>Docs</h1><a href="/a">A</a><a href="/b">B</a>', "body", { kind: "extract", map }), {
    title: "Docs", links: ["/a", "/b"]
  });
});

test("serialize encodes successful form controls", () => {
  const html = '<form><input name="q" value="a b"><input type="checkbox" name="yes" checked><input disabled name="no" value="x"></form>';
  assert.equal(query(html, "form", { kind: "serialize" }), "q=a+b&yes=on");
});

test("serializeArray preserves successful control order", () => {
  const html = '<form><input name="a" value="1"><textarea name="b">two</textarea></form>';
  assert.deepEqual(query(html, "form", { kind: "serializeArray" }), [{ name: "a", value: "1" }, { name: "b", value: "two" }]);
});

test("camelCase converts CSS names", () => {
  assert.equal(call({ operation: "utils", method: "camelCase", value: "border-top-left-radius" }), "borderTopLeftRadius");
});

test("cssCase converts JavaScript style names", () => {
  assert.equal(call({ operation: "utils", method: "cssCase", value: "WebkitLineClamp" }), "-webkit-line-clamp");
});

test("isHtml recognizes markup and rejects plain selectors", () => {
  assert.equal(call({ operation: "utils", method: "isHtml", value: "<div>x</div>" }), true);
  assert.equal(call({ operation: "utils", method: "isHtml", value: "div.item" }), false);
});

test("slim entry supports local HTML parsing and selectors", () => {
  assert.equal(query("<root><item>A</item><item>B</item></root>", "item", { kind: "text" }, [], { slim: true, isDocument: false }), "AB");
});

test("an empty selection has zero length and undefined getters", () => {
  assert.equal(query(fruits, ".missing", { kind: "length" }), 0);
  assert.equal(query(fruits, ".missing", { kind: "html" }), null);
});

test("invalid CSS selectors report a candidate error", () => {
  const result = failure({ operation: "query", html: fruits, selector: "li[", result: { kind: "length" } });
  assert.equal(result.error, "candidate-call-failed");
  assert.match(result.message, /expected name|attribute selector|unmatched|selector/i);
});

test("HTML option xmlMode uses htmlparser2 semantics", () => {
  const html = '<root><Item checked=""><Child/></Item></root>';
  assert.equal(query(html, "Item", { kind: "outerHTML" }, [], { options: { xmlMode: true } }), '<Item checked=""><Child/></Item>');
});

test("lower-case HTML property tagName is uppercase", () => {
  assert.equal(query("<article></article>", "article", { kind: "prop", name: "tagName" }), "ARTICLE");
});

test("boolean properties follow HTML attribute presence", () => {
  assert.equal(query('<input checked><input>', "input", { kind: "prop", name: "checked" }, [{ method: "first", args: [] }]), true);
  assert.equal(query('<input checked><input>', "input", { kind: "prop", name: "checked" }, [{ method: "last", args: [] }]), false);
});

test("attribute removal accepts whitespace-separated names", () => {
  const steps = [{ method: "removeAttr", args: ["id title"] }];
  assert.equal(query('<p id="x" title="y" class="z">A</p>', "p", { kind: "outerHTML" }, steps), '<p class="z">A</p>');
});

test("multiple select val returns selected values in order", () => {
  const html = '<select multiple><option value="a" selected>A</option><option>B</option><option value="c" selected>C</option></select>';
  assert.deepEqual(query(html, "select", { kind: "val" }), ["A", "C"]);
});

test("setting val updates matching selected options", () => {
  const html = '<select multiple><option value="a">A</option><option value="b">B</option><option value="c">C</option></select>';
  const steps = [{ method: "val", args: [["a", "c"]] }, { method: "children", args: ["option:selected"] }];
  assert.deepEqual(outer(html, "select", steps), ['<option value="a" selected="">A</option>', '<option value="c" selected="">C</option>']);
});

test("wrapInner encloses existing contents", () => {
  const steps = [{ method: "wrapInner", args: ["<strong></strong>"] }];
  assert.equal(query("<p>A<em>B</em></p>", "p", { kind: "html" }, steps), "<strong>A<em>B</em></strong>");
});

test("negative eq outside range returns an empty selection", () => {
  assert.equal(query(fruits, "li", { kind: "length" }, [{ method: "eq", args: [-4] }]), 0);
});

test("fragment parser preserves adjacent top-level nodes", () => {
  assert.deepEqual(outer("text<b>B</b><!--c--><i>I</i>", "b, i", [], { isDocument: false }), ["<b>B</b>", "<i>I</i>"]);
});
