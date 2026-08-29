from __future__ import annotations

import asyncio
import json
import os
import textwrap
from pathlib import Path
from typing import Any, Callable

from nl2repobench.verification.candidate_client import CandidateCallResult, execute_script


def _run(source: str) -> CandidateCallResult:
    if os.environ.get("JINJA2_LOCAL_CANDIDATE"):
        import subprocess

        candidate_path = os.environ["JINJA2_LOCAL_CANDIDATE"]
        code = (
            "import json,sys;sys.path.insert(0,"
            + repr(candidate_path)
            + ");exec(compile(" + repr(textwrap.dedent(source)) + ",'<scenario>','exec'));print(json.dumps(result))"
        )
        completed = subprocess.run(
            ["python", "-I", "-c", code],
            capture_output=True,
            text=True,
            timeout=20,
            check=False,
        )
        if completed.returncode:
            return CandidateCallResult(False, exception_type="LocalProcessError", exception_message=completed.stderr)
        try:
            return CandidateCallResult(True, value=json.loads(completed.stdout))
        except json.JSONDecodeError as exc:
            return CandidateCallResult(False, exception_type="LocalProtocolError", exception_message=str(exc))
    return execute_script(textwrap.dedent(source), timeout_sec=12)


def _value(source: str, expected: Any) -> bool:
    result = _run(source)
    return result.ok and result.value == expected


def _error(source: str, suffix: str) -> bool:
    result = _run(source)
    return not result.ok and (result.exception_type or "").endswith(suffix)


def _leaf(leaf_id: str, source: str, check: Callable[[CandidateCallResult], bool] | None = None) -> dict[str, str]:
    result = _run(source)
    passed = check(result) if check else result.ok
    leaf: dict[str, str] = {"id": leaf_id, "status": "passed" if passed else "failed"}
    if not passed:
        leaf["message"] = (result.exception_message or repr(result.value))[-500:]
    return leaf


def main() -> None:
    leaves: list[dict[str, str]] = []
    leaves.append(_leaf("exports", """
        import jinja2
        required = ["Environment", "Template", "TemplateSyntaxError", "Undefined", "DictLoader", "select_autoescape"]
        result = all(hasattr(jinja2, name) for name in required) and jinja2.__doc__ is not None
    """, lambda r: r.value is True))
    leaves.append(_leaf("metadata", """
        import importlib.metadata as metadata
        import jinja2
        result = (metadata.version("Jinja2"), jinja2.__package__, hasattr(jinja2, "__version__"))
    """, lambda r: r.value in (["3.2.0.dev", "jinja2", True], ["3.2.0.dev0", "jinja2", True], ["3.1.6", "jinja2", True], ("3.2.0.dev", "jinja2", True), ("3.2.0.dev0", "jinja2", True), ("3.1.6", "jinja2", True))))
    leaves.append(_leaf("basic-render", """
        from jinja2 import Environment
        result = Environment().from_string("Hello {{ name }}!").render(name="Jinja")
    """, lambda r: r.value == "Hello Jinja!"))
    leaves.append(_leaf("expression", """
        from jinja2 import Environment
        result = Environment().from_string("{{ user.name|upper }} {{ items[1] + 2 }} {{ ok and 'yes' or 'no' }}").render(user={"name": "Ada"}, items=[1, 4], ok=True)
    """, lambda r: r.value == "ADA 6 yes"))
    leaves.append(_leaf("escape", """
        from jinja2 import Environment
        result = Environment(autoescape=True).from_string("{{ value }}|{{ value|safe }}").render(value="<b>&")
    """, lambda r: r.value == "&lt;b&gt;&amp;|<b>&"))
    leaves.append(_leaf("trim-blocks", """
        from jinja2 import Environment
        source = "A\\n  {% if ok %}\\n  B\\n  {% endif %}\\nC"
        result = Environment(trim_blocks=True, lstrip_blocks=True).from_string(source).render(ok=True)
    """, lambda r: r.value == "A\n  B\nC"))
    leaves.append(_leaf("if-loop", """
        from jinja2 import Environment
        source = "{% if show %}{% for x in xs %}{{ x }}{% else %}none{% endfor %}{% else %}hidden{% endif %}"
        result = Environment().from_string(source).render(show=True, xs=[1, 2, 3])
    """, lambda r: r.value == "123"))
    leaves.append(_leaf("loop-meta", """
        from jinja2 import Environment
        source = "{% for x in xs %}{{ loop.index }}:{{ loop.first }}:{{ loop.last }}:{{ loop.cycle('a','b') }};{% endfor %}"
        result = Environment().from_string(source).render(xs=["x", "y", "z"])
    """, lambda r: r.value == "1:True:False:a;2:False:False:b;3:False:True:a;"))
    leaves.append(_leaf("set-block", """
        from jinja2 import Environment
        source = "{% set greeting %}Hi {{ name }}{% endset %}{{ greeting|upper }}"
        result = Environment().from_string(source).render(name="Ada")
    """, lambda r: r.value == "HI ADA"))
    leaves.append(_leaf("macro", """
        from jinja2 import Environment
        source = "{% macro input(name, value='') %}<input name='{{ name }}' value='{{ value }}'>{% endmacro %}{{ input('q', 'x') }}"
        result = Environment().from_string(source).render()
    """, lambda r: r.value == "<input name='q' value='x'>"))
    leaves.append(_leaf("call-block", """
        from jinja2 import Environment
        source = "{% macro wrap() %}<b>{{ caller() }}</b>{% endmacro %}{% call wrap() %}inside{% endcall %}"
        result = Environment().from_string(source).render()
    """, lambda r: r.value == "<b>inside</b>"))
    leaves.append(_leaf("filters", """
        from jinja2 import Environment
        source = "{{ words|join(',') }}|{{ words|map('upper')|join('-') }}|{{ words|length }}|{{ missing|default('fallback') }}"
        result = Environment().from_string(source).render(words=["a", "b"])
    """, lambda r: r.value == "a,b|A-B|2|fallback"))
    leaves.append(_leaf("tests", """
        from jinja2 import Environment
        source = "{{ a is defined }} {{ b is undefined }} {{ n is number }} {{ f is callable }}"
        result = Environment().from_string(source).render(a=1, n=2, f=lambda: None)
    """, lambda r: r.value == "True True True True"))
    leaves.append(_leaf("custom-filter", """
        from jinja2 import Environment
        env = Environment()
        env.filters['surround'] = lambda value, left='[', right=']': left + str(value) + right
        result = env.from_string("{{ word|surround('<', '>') }}").render(word="x")
    """, lambda r: r.value == "<x>"))
    leaves.append(_leaf("custom-test", """
        from jinja2 import Environment
        env = Environment()
        env.tests['even'] = lambda value: value % 2 == 0
        result = env.from_string("{% for x in xs if x is even %}{{ x }}{% endfor %}").render(xs=[1, 2, 3, 4])
    """, lambda r: r.value == "24"))
    leaves.append(_leaf("undefined", """
        from jinja2 import Environment, Undefined
        value = Environment().from_string("{{ missing }}").render()
        result = (value, str(Undefined(name='x')))
    """, lambda r: r.value == ["", ""] or r.value == ("", "")))
    leaves.append(_leaf("strict-undefined", """
        from jinja2 import Environment, StrictUndefined
        result = Environment(undefined=StrictUndefined).from_string("{{ missing }}").render()
    """, lambda r: not r.ok and "UndefinedError" in (r.exception_type or "") + (r.exception_message or "")))
    leaves.append(_leaf("chainable-undefined", """
        from jinja2 import ChainableUndefined, Environment
        result = Environment(undefined=ChainableUndefined).from_string("{{ missing.deep.value|default('ok') }}").render()
    """, lambda r: r.value == "ok"))
    leaves.append(_leaf("syntax-error", """
        from jinja2 import Environment
        try:
            Environment().from_string("{% if broken %}").render()
        except Exception as exc:
            result = (type(exc).__name__, getattr(exc, 'lineno', 0) > 0)
        else:
            result = ("none", False)
    """, lambda r: r.value == ["TemplateSyntaxError", True] or r.value == ("TemplateSyntaxError", True)))
    leaves.append(_leaf("environment-options", """
        from jinja2 import Environment
        env = Environment(variable_start_string='[[', variable_end_string=']]')
        env.globals['site'] = 'docs'
        result = env.from_string("[[ site ]]").render()
    """, lambda r: r.value == "docs"))
    leaves.append(_leaf("generate", """
        from jinja2 import Environment
        result = list(Environment().from_string("A{{ x }}B").generate(x=2))
    """, lambda r: r.value == ["A", "2", "B"]))
    leaves.append(_leaf("stream", """
        from jinja2 import Environment
        stream = Environment().from_string("A{{ x }}B").stream(x=2)
        stream.disable_buffering()
        result = list(stream)
    """, lambda r: r.value == ["A", "2", "B"]))
    leaves.append(_leaf("overlay", """
        from jinja2 import Environment
        base = Environment()
        base.globals['x'] = 'base'
        result = (base.overlay().from_string('{{ x }}').render(), base.from_string('{{ x }}').render())
    """, lambda r: r.value == ["base", "base"] or r.value == ("base", "base")))
    leaves.append(_leaf("dict-loader", """
        from jinja2 import DictLoader, Environment
        env = Environment(loader=DictLoader({'hello.txt': 'Hello {{ name }}'}))
        result = (env.get_template('hello.txt').render(name='Ada'), env.list_templates())
    """, lambda r: r.value == ["Hello Ada", ["hello.txt"]] or r.value == ("Hello Ada", ["hello.txt"])))
    leaves.append(_leaf("function-loader", """
        from jinja2 import Environment, FunctionLoader
        def load(name):
            return 'Loaded ' + name if name == 'x' else None
        result = Environment(loader=FunctionLoader(load)).get_template('x').render()
    """, lambda r: r.value == "Loaded x"))
    leaves.append(_leaf("filesystem-loader", """
        import pathlib, tempfile
        from jinja2 import Environment, FileSystemLoader
        root = pathlib.Path(tempfile.mkdtemp())
        (root / 'a.txt').write_text('file {{ value }}', encoding='utf-8')
        env = Environment(loader=FileSystemLoader(str(root)))
        result = (env.get_template('a.txt').render(value='ok'), env.list_templates())
    """, lambda r: r.value == ["file ok", ["a.txt"]] or r.value == ("file ok", ["a.txt"])))
    leaves.append(_leaf("loader-path", """
        from jinja2 import DictLoader, Environment, TemplateNotFound
        env = Environment(loader=DictLoader({'x': 'x'}))
        try:
            env.get_template('../x')
        except Exception as exc:
            result = type(exc).__name__
        else:
            result = 'no-error'
    """, lambda r: r.value == "TemplateNotFound"))
    leaves.append(_leaf("composed-loaders", """
        from jinja2 import ChoiceLoader, DictLoader, Environment, PrefixLoader
        env = Environment(loader=ChoiceLoader([PrefixLoader({'one': DictLoader({'x': '1'})}), DictLoader({'x': '2'})]))
        result = (env.get_template('one/x').render(), env.get_template('x').render())
    """, lambda r: r.value == ["1", "2"] or r.value == ("1", "2")))
    leaves.append(_leaf("bytecode", """
        import tempfile
        from jinja2 import DictLoader, Environment, FileSystemBytecodeCache
        cache = FileSystemBytecodeCache(tempfile.mkdtemp())
        env = Environment(loader=DictLoader({'x': 'cached {{ value }}'}), bytecode_cache=cache)
        first = env.get_template('x').render(value=1)
        env.cache.clear()
        second = env.get_template('x').render(value=1)
        result = (first, second)
    """, lambda r: r.value == ["cached 1", "cached 1"] or r.value == ("cached 1", "cached 1")))
    leaves.append(_leaf("template-metadata", """
        from jinja2 import Environment
        template = Environment().from_string('hello')
        result = (template.render(), template.name, template.filename, callable(template.root_render_func))
    """, lambda r: r.value == ["hello", None, "<template>", True] or r.value == ("hello", None, "<template>", True)))
    leaves.append(_leaf("async-render", """
        import asyncio
        from jinja2 import Environment
        async def main():
            return await Environment(enable_async=True).from_string('{{ value }}').render_async(value='async')
        result = asyncio.run(main())
    """, lambda r: r.value == "async"))
    leaves.append(_leaf("async-generate", """
        import asyncio
        from jinja2 import Environment
        async def main():
            values = []
            async for item in Environment(enable_async=True).from_string('A{{ value }}B').generate_async(value=3):
                values.append(item)
            return values
        result = asyncio.run(main())
    """, lambda r: r.value == ["A", "3", "B"]))
    leaves.append(_leaf("async-filter", """
        import asyncio
        from jinja2 import Environment
        async def upper(value):
            return value.upper()
        async def main():
            env = Environment(enable_async=True)
            env.filters['async_upper'] = upper
            return await env.from_string('{{ value|async_upper }}').render_async(value='ok')
        result = asyncio.run(main())
    """, lambda r: r.value == "OK"))
    leaves.append(_leaf("sandbox-attribute", """
        from jinja2.sandbox import SandboxedEnvironment
        env = SandboxedEnvironment()
        result = env.is_safe_attribute(object(), '__class__', type)
    """, lambda r: r.value is False))
    leaves.append(_leaf("sandbox-call", """
        from jinja2.sandbox import SandboxedEnvironment
        env = SandboxedEnvironment()
        result = env.from_string('{{ value.__class__ }}').render(value=1)
    """, lambda r: r.value == ""))
    leaves.append(_leaf("sandbox-mutable", """
        from jinja2.sandbox import modifies_known_mutable
        result = (modifies_known_mutable([], 'append'), modifies_known_mutable({}, 'clear'), modifies_known_mutable((), 'count'))
    """, lambda r: r.value == [True, True, False] or r.value == (True, True, False)))
    leaves.append(_leaf("meta", """
        from jinja2 import Environment
        from jinja2.meta import find_referenced_templates, find_undeclared_variables
        ast = Environment().parse('{% extends "base.html" %}{{ user.name }}')
        result = (sorted(find_undeclared_variables(ast)), list(find_referenced_templates(ast)))
    """, lambda r: r.value == [["user"], ["base.html"]] or r.value == (["user"], ["base.html"])))
    leaves.append(_leaf("native", """
        from jinja2.nativetypes import NativeEnvironment
        env = NativeEnvironment()
        result = (env.from_string('{{ value }}').render(value=42), env.from_string('{{ a }}{{ b }}').render(a=4, b=2))
    """, lambda r: r.value == [42, 42] or r.value == (42, 42)))
    leaves.append(_leaf("autoescape", """
        from jinja2 import select_autoescape
        callback = select_autoescape(enabled_extensions=('html',), default_for_string=True)
        result = (callback('x.html'), callback('x.txt'), callback(None))
    """, lambda r: r.value == [True, False, True] or r.value == (True, False, True)))
    leaves.append(_leaf("utils", """
        from jinja2 import Environment, clear_caches, is_undefined, pass_environment
        from jinja2.runtime import Undefined
        @pass_environment
        def marker(environment, value):
            return environment is not None and value
        env = Environment()
        env.filters['marker'] = marker
        result = (env.from_string('{{ x|marker }}').render(x='yes'), is_undefined(Undefined(name='x')))
        clear_caches()
    """, lambda r: r.value == ["yes", True] or r.value == ("yes", True)))
    leaves.append(_leaf("inheritance", """
        from jinja2 import DictLoader, Environment
        templates = {'base': 'A{% block body %}base{% endblock %}Z', 'child': '{% extends "base" %}{% block body %}child {{ super() }}{% endblock %}'}
        result = Environment(loader=DictLoader(templates)).get_template('child').render()
    """, lambda r: r.value == "Achild baseZ"))
    leaves.append(_leaf("include-import", """
        from jinja2 import DictLoader, Environment
        templates = {'part': 'P{{ value }}', 'main': '{% include "part" %}|{% import "macros" as m %}{{ m.twice(value) }}', 'macros': '{% macro twice(x) %}{{ x }}{{ x }}{% endmacro %}'}
        result = Environment(loader=DictLoader(templates)).get_template('main').render(value='x')
    """, lambda r: r.value == "Px|xx"))
    leaves.append(_leaf("lexer", """
        from jinja2 import Environment
        tokens = [(token[1], token[2]) for token in Environment().lex('{{ x }}')]
        result = tokens
    """, lambda r: r.value == [["variable_begin", "{{"], ["whitespace", " "], ["name", "x"], ["whitespace", " "], ["variable_end", "}}"]] or r.value == [("variable_begin", "{{"), ("whitespace", " "), ("name", "x"), ("whitespace", " "), ("variable_end", "}}")]))
    leaves.append(_leaf("exceptions", """
        from jinja2 import TemplateNotFound, TemplateSyntaxError, TemplatesNotFound
        result = (issubclass(TemplatesNotFound, TemplateNotFound), issubclass(TemplateSyntaxError, Exception), issubclass(TemplateNotFound, LookupError))
    """, lambda r: r.value == [True, True, True] or r.value == (True, True, True)))
    if len(leaves) != 44:
        raise RuntimeError(f"verifier authoring error: {len(leaves)} leaves")
    print(json.dumps({"schema_version": "1.0", "leaves": leaves}, separators=(",", ":")))


if __name__ == "__main__":
    main()
