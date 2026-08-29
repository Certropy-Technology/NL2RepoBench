from __future__ import annotations

import json
import os
import sys
from typing import Any


def _load_candidate() -> None:
    paths = [os.environ.get("NL2REPO_PROBE_SITE"), "/tmp/candidate-site", "/opt/candidate-dependencies/site"]
    for path in reversed([p for p in paths if p]):
        sys.path.insert(0, path)


def _token(token: Any) -> list[Any]:
    return [token.type, token.tag, token.nesting, token.attrs, token.level, token.content, token.markup]


def case_metadata() -> Any:
    import markdown_it
    from markdown_it import MarkdownIt

    md = MarkdownIt("commonmark")
    return [markdown_it.__version__, list(markdown_it.__all__), repr(md), dict(md.options)]


def case_render_basic() -> Any:
    from markdown_it import MarkdownIt

    return MarkdownIt("commonmark").render("# Hello\n\nThis is **bold** and [link](https://example.com).\n")


def case_render_blocks() -> Any:
    from markdown_it import MarkdownIt

    return MarkdownIt("commonmark").render(
        "> quote\n\n- one\n- two\n\n```python\nprint(1)\n```\n"
    )


def case_render_inline() -> Any:
    from markdown_it import MarkdownIt

    return MarkdownIt("commonmark").renderInline("a *b* `c` & d")


def case_render_security() -> Any:
    from markdown_it import MarkdownIt

    md = MarkdownIt("commonmark", {"html": False, "breaks": True, "typographer": True})
    return md.render('a\nb\n\n<span>x</span>\n\n"Hi" -- ok...')


def case_render_table() -> Any:
    from markdown_it import MarkdownIt

    return MarkdownIt("default").render("~~x~~\n\n| a | b |\n|---|---|\n| c | d |\n")


def case_parse_inline() -> Any:
    from markdown_it import MarkdownIt

    return [_token(token) for token in MarkdownIt("commonmark").parseInline("a *b* [c](d)")[0].children]


def case_parse_tokens() -> Any:
    from markdown_it import MarkdownIt

    return [_token(token) for token in MarkdownIt("commonmark").parse("## Hi\n\ntext")]


def case_token_api() -> Any:
    from markdown_it.token import Token

    token = Token("text", "", 0, attrs={"class": "a"}, content="x")
    token.attrJoin("class", "b")
    copied = token.copy(content="y")
    restored = Token.from_dict({"type": "text", "tag": "", "nesting": 0, "attrs": None, "content": "ok"})
    return {
        "attrs": token.attrItems(),
        "missing": token.attrGet("missing"),
        "index": token.attrIndex("class"),
        "copy": [copied.content, token.content],
        "dict": Token("text", "", 0, attrs=None, content="hi").as_dict(),
        "restored": [restored.type, restored.attrs, restored.content],
    }


def case_token_nested() -> Any:
    from markdown_it import MarkdownIt

    tokens = MarkdownIt("commonmark").parseInline("**bold**")[0].children
    assert tokens is not None
    return [token.as_dict(as_upstream=False) for token in tokens]


def case_tree_api() -> Any:
    from markdown_it import MarkdownIt
    from markdown_it.tree import SyntaxTreeNode

    root = SyntaxTreeNode(MarkdownIt("commonmark").parse("Hello **world**"))
    return {
        "repr": repr(root),
        "type": root.type,
        "children": [[child.type, child.content, len(child.children)] for child in root.children],
        "tokens": [token.type for token in root.to_tokens()],
        "walk": [[node.type, None if node.is_root else node.level] for node in root.walk(include_self=True)],
    }


def case_tree_mutation() -> Any:
    from markdown_it import MarkdownIt
    from markdown_it.tree import SyntaxTreeNode

    root = SyntaxTreeNode(MarkdownIt("commonmark").parse("a"))
    child = root.children[0]
    return [root.is_root, child.parent is root, child.is_nested, child.siblings[0].type]


def case_presets() -> Any:
    from markdown_it import MarkdownIt

    source = "# h\n\n*x*"
    return [MarkdownIt("zero").render(source), MarkdownIt("commonmark").render(source)]


def case_options_mapping() -> Any:
    from markdown_it import MarkdownIt

    md = MarkdownIt("commonmark")
    md.options.maxNesting = 7
    md.options.xhtmlOut = False
    return [md.options.maxNesting, md.options.xhtmlOut, str(md.options), md["renderer"] is md.renderer]


def case_ruler() -> Any:
    from markdown_it import MarkdownIt

    md = MarkdownIt("commonmark")
    before = md.get_active_rules()
    md.disable("emphasis")
    disabled = md.render("*x*")
    md.enable("emphasis")
    enabled = md.render("*x*")
    return [
        len(before["core"]),
        len(before["block"]),
        len(before["inline"]),
        disabled,
        enabled,
        "emphasis" in md.get_active_rules()["inline"],
    ]


def case_plugin() -> Any:
    from markdown_it import MarkdownIt

    def plugin(md: Any) -> None:
        def uppercase(state: Any) -> None:
            for token in state.tokens:
                if token.type == "inline" and token.children:
                    for child in token.children:
                        if child.type == "text":
                            child.content = child.content.upper()

        md.core.ruler.push("uppercase", uppercase)

    return MarkdownIt("commonmark").use(plugin).render("hello *world*")


def case_link_methods() -> Any:
    from markdown_it import MarkdownIt

    md = MarkdownIt("commonmark")
    return [
        md.validateLink("javascript:alert(1)"),
        md.validateLink("https://example.com/a b"),
        md.normalizeLink("https://example.com/α β"),
        md.normalizeLinkText("https://example.com/α β"),
    ]


def case_reference_links() -> Any:
    from markdown_it import MarkdownIt

    env: dict[str, Any] = {}
    result = MarkdownIt("commonmark").render("[x][id]\n\n[id]: /url \"Title\"\n", env)
    return [result, env]


def case_helpers() -> Any:
    from markdown_it.common.utils import unescapeAll

    return [unescapeAll(r"&amp; &copy; &#x1F4AC; \\ \* \a"), unescapeAll("&#0; &#x110000;")]


def case_renderer_override() -> Any:
    from markdown_it import MarkdownIt
    from markdown_it.renderer import RendererHTML

    class Renderer(RendererHTML):
        def text(self, tokens: Any, idx: int, options: Any, env: Any) -> str:
            return "[" + super().text(tokens, idx, options, env) + "]"

    return MarkdownIt("commonmark", renderer_cls=Renderer).render("hello")


def case_input_errors() -> Any:
    from markdown_it import MarkdownIt

    md = MarkdownIt("commonmark")
    errors: list[str] = []
    for action in (lambda: md.parse(1), lambda: md.render("x", []), lambda: MarkdownIt("missing")):
        try:
            action()
        except Exception as exc:
            errors.append(type(exc).__name__)
    return errors


def case_custom_config() -> Any:
    from markdown_it import MarkdownIt

    options = dict(MarkdownIt("commonmark").options)
    options["html"] = False
    config = {"options": options, "components": {"inline": {"rules": ["text"]}}}
    md = MarkdownIt(config)
    return [md.render("*x* <b>y</b>"), md.get_active_rules()]


def case_state_access() -> Any:
    from markdown_it import MarkdownIt

    md = MarkdownIt("commonmark")
    return [
        md["inline"].__class__.__name__,
        md["block"].__class__.__name__,
        md["core"].__class__.__name__,
        md["renderer"].__class__.__name__,
        sorted(md.get_all_rules()),
    ]


def case_cli_parser() -> Any:
    from markdown_it.cli.parse import parse_args

    args = parse_args(["--stdin"])
    batch = parse_args(["README.md", "README.footer.md"])
    return [args.stdin, args.filenames, batch.stdin, batch.filenames]


CASES = {
    name.removeprefix("case_"): value
    for name, value in globals().items()
    if name.startswith("case_")
}


def main() -> None:
    _load_candidate()
    case = sys.argv[1]
    value = CASES[case]()
    print(json.dumps({"case": case, "value": value}, ensure_ascii=False, sort_keys=True, default=str))


if __name__ == "__main__":
    main()
