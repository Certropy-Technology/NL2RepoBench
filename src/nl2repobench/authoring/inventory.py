"""Static source and test inventory for evidence-first task authoring.

The scanner intentionally parses source text without importing or executing a
candidate package.  Its output is a deterministic structural inventory used
to prioritize review and build a test-to-behavior graph; it is not a semantic
oracle and must never be treated as proof that an API behaves correctly.
"""

from __future__ import annotations

import ast
import hashlib
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, cast


class InventoryError(ValueError):
    """Raised when a source root cannot be scanned safely."""


_DYNAMIC_CALLS = frozenset({"eval", "exec", "getattr", "setattr", "__import__", "compile"})
_RISKY_IMPORT_PREFIXES = (
    "ctypes",
    "cffi",
    "subprocess",
    "socket",
    "requests",
    "httpx",
    "boto",
    "selenium",
    "playwright",
)


@dataclass(frozen=True)
class ApiSymbol:
    """One statically discovered module export or callable."""

    module: str
    name: str
    qualified_name: str
    kind: str
    signature: str | None
    line: int
    end_line: int
    public: bool
    exported: bool
    decorators: tuple[str, ...] = ()


@dataclass(frozen=True)
class ImportEdge:
    """One import edge discovered without resolving candidate code."""

    module: str
    imported: str
    line: int
    relative_level: int = 0


@dataclass(frozen=True)
class TestReference:
    """A test definition and the names it references syntactically."""

    module: str
    name: str
    line: int
    end_line: int
    decorators: tuple[str, ...]
    referenced_names: tuple[str, ...]
    assertion_kinds: tuple[str, ...]


@dataclass(frozen=True)
class InventoryMetrics:
    """Bounded source-size and structural counters."""

    implementation_loc: int
    test_loc: int
    python_files: int
    test_files: int
    public_symbol_count: int
    test_count: int
    import_count: int


@dataclass(frozen=True)
class ApiInventory:
    """Deterministic JSON-serializable inventory produced by the scanner."""

    language: str
    source_root: str
    source_digest: str
    scanner_identity: str
    symbols: tuple[ApiSymbol, ...]
    imports: tuple[ImportEdge, ...]
    tests: tuple[TestReference, ...]
    cli_entries: tuple[str, ...]
    risk_flags: tuple[str, ...]
    syntax_diagnostics: tuple[str, ...]
    metrics: InventoryMetrics
    completeness: dict[str, bool]

    def to_dict(self) -> dict[str, Any]:
        """Return stable JSON data with tuple fields converted recursively."""

        return cast(
            dict[str, Any],
            json.loads(json.dumps(asdict(self), ensure_ascii=False, sort_keys=True)),
        )

    def to_json(self) -> bytes:
        """Serialize the inventory canonically for content-addressed storage."""

        return (
            json.dumps(
                self.to_dict(),
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            )
            + "\n"
        ).encode("utf-8")


def scan_python_source(root: Path) -> ApiInventory:
    """Scan Python source and tests below ``root`` without importing them."""

    resolved_root = root.resolve()
    if not resolved_root.is_dir() or root.is_symlink():
        raise InventoryError(f"source root must be a regular directory: {root}")

    files = tuple(sorted(resolved_root.rglob("*.py")))
    if not files:
        raise InventoryError(f"no Python files found below {root}")

    symbols: list[ApiSymbol] = []
    imports: list[ImportEdge] = []
    tests: list[TestReference] = []
    risk_flags: set[str] = set()
    diagnostics: list[str] = []
    cli_entries = _read_python_cli_entries(resolved_root)
    implementation_loc = 0
    test_loc = 0
    test_file_count = 0
    source_has_dynamic = False
    source_has_unresolved_syntax = False

    for path in files:
        relative = path.relative_to(resolved_root)
        is_test = _is_test_path(relative)
        if is_test:
            test_file_count += 1
        text = _read_text(path)
        lines = _non_comment_lines(text)
        if is_test:
            test_loc += lines
        else:
            implementation_loc += lines
        module = _module_name(relative)
        try:
            tree = ast.parse(text, filename=str(relative))
        except SyntaxError as exc:
            source_has_unresolved_syntax = True
            diagnostics.append(f"{relative}:{exc.lineno or 0}:{exc.offset or 0}: {exc.msg}")
            continue

        exported_names = _explicit_exports(tree)
        visitor = _InventoryVisitor(module, is_test=is_test, exported_names=exported_names)
        visitor.visit(tree)
        symbols.extend(visitor.symbols)
        imports.extend(visitor.imports)
        tests.extend(visitor.tests)
        risk_flags.update(visitor.risk_flags)
        source_has_dynamic = source_has_dynamic or visitor.dynamic_seen

    digest = _digest_files(resolved_root, files)
    public_count = sum(1 for symbol in symbols if symbol.public)
    return ApiInventory(
        language="python",
        source_root=str(resolved_root),
        source_digest=digest,
        scanner_identity="python-ast-stdlib-1",
        symbols=tuple(sorted(symbols, key=_symbol_sort_key)),
        imports=tuple(sorted(imports, key=lambda item: (item.module, item.line, item.imported))),
        tests=tuple(sorted(tests, key=lambda item: (item.module, item.line, item.name))),
        cli_entries=tuple(sorted(cli_entries)),
        risk_flags=tuple(sorted(risk_flags)),
        syntax_diagnostics=tuple(sorted(diagnostics)),
        metrics=InventoryMetrics(
            implementation_loc=implementation_loc,
            test_loc=test_loc,
            python_files=len(files) - test_file_count,
            test_files=test_file_count,
            public_symbol_count=public_count,
            test_count=len(tests),
            import_count=len(imports),
        ),
        completeness={
            "syntax": not source_has_unresolved_syntax,
            "dynamic": not source_has_dynamic,
            "generated": "generated-code" not in risk_flags,
            "native": "native-extension" not in risk_flags,
            "external-service": "external-service" not in risk_flags,
        },
    )


def write_inventory(inventory: ApiInventory, output: Path) -> None:
    """Write one inventory atomically enough for stage-local authoring output."""

    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_name(f".{output.name}.tmp")
    temporary.write_bytes(inventory.to_json())
    temporary.replace(output)


class _InventoryVisitor(ast.NodeVisitor):
    def __init__(self, module: str, *, is_test: bool, exported_names: set[str]) -> None:
        self.module = module
        self.is_test = is_test
        self.exported_names = exported_names
        self.symbols: list[ApiSymbol] = []
        self.imports: list[ImportEdge] = []
        self.tests: list[TestReference] = []
        self.risk_flags: set[str] = set()
        self.dynamic_seen = False
        self._class_stack: list[str] = []

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            self._record_import(alias.name, node.lineno)
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        module = node.module or ""
        for alias in node.names:
            imported = f"{module}:{alias.name}" if module else alias.name
            self._record_import(imported, node.lineno, relative_level=node.level)
        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._record_callable(node, kind="function")
        self._record_test(node)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._record_callable(node, kind="async-function")
        self._record_test(node)
        self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        qualified = ".".join((*self._class_stack, node.name))
        qualified = f"{self.module}.{qualified}"
        self._record_symbol(
            node,
            name=node.name,
            qualified_name=qualified,
            kind="class",
            signature=None,
        )
        self._class_stack.append(node.name)
        self.generic_visit(node)
        self._class_stack.pop()

    def visit_Call(self, node: ast.Call) -> None:
        name = _called_name(node.func)
        if name in _DYNAMIC_CALLS:
            self.dynamic_seen = True
            self.risk_flags.add("dynamic-execution")
        self.generic_visit(node)

    def visit_Constant(self, node: ast.Constant) -> None:
        if isinstance(node.value, str) and "generated by" in node.value.casefold():
            self.risk_flags.add("generated-code")
        self.generic_visit(node)

    def _record_import(self, imported: str, line: int, *, relative_level: int = 0) -> None:
        self.imports.append(
            ImportEdge(
                module=self.module,
                imported=imported,
                line=line,
                relative_level=relative_level,
            )
        )
        root = imported.split(":", 1)[0].lstrip(".").split(".", 1)[0]
        for prefix in _RISKY_IMPORT_PREFIXES:
            if root == prefix or imported.startswith(f"{prefix}."):
                flag = "native-extension" if root in {"ctypes", "cffi"} else "external-service"
                self.risk_flags.add(flag)

    def _record_callable(self, node: ast.FunctionDef | ast.AsyncFunctionDef, *, kind: str) -> None:
        parent = ".".join(self._class_stack)
        local_name = f"{parent}.{node.name}" if parent else node.name
        qualified = f"{self.module}.{local_name}"
        self._record_symbol(
            node,
            name=node.name,
            qualified_name=qualified,
            kind="method" if parent else kind,
            signature=_function_signature(node),
        )

    def _record_symbol(
        self,
        node: ast.AST,
        *,
        name: str,
        qualified_name: str,
        kind: str,
        signature: str | None,
    ) -> None:
        line = getattr(node, "lineno", 0)
        end_line = getattr(node, "end_lineno", line) or line
        public = not name.startswith("_") or name in self.exported_names
        decorators = tuple(
            sorted(
                _expression_text(item)
                for item in getattr(node, "decorator_list", [])
            )
        )
        self.symbols.append(
            ApiSymbol(
                module=self.module,
                name=name,
                qualified_name=qualified_name,
                kind=kind,
                signature=signature,
                line=line,
                end_line=end_line,
                public=public,
                exported=name in self.exported_names,
                decorators=decorators,
            )
        )

    def _record_test(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        if not self.is_test or not (node.name.startswith("test_") or node.name == "test"):
            return
        names = sorted(
            {
                item.id
                for item in ast.walk(node)
                if isinstance(item, ast.Name) and isinstance(item.ctx, ast.Load)
            }
        )
        assertion_kinds = sorted(
            {
                kind
                for item in ast.walk(node)
                if isinstance(item, ast.Call)
                for kind in [_assertion_kind(item)]
                if kind is not None
            }
        )
        self.tests.append(
            TestReference(
                module=self.module,
                name=node.name,
                line=node.lineno,
                end_line=getattr(node, "end_lineno", node.lineno) or node.lineno,
                decorators=tuple(sorted(_expression_text(item) for item in node.decorator_list)),
                referenced_names=tuple(names),
                assertion_kinds=tuple(assertion_kinds),
            )
        )


def _function_signature(node: ast.FunctionDef | ast.AsyncFunctionDef) -> str:
    """Render a source-level signature without evaluating annotations/defaults."""

    arguments = ast.unparse(node.args)
    returns = f" -> {ast.unparse(node.returns)}" if node.returns is not None else ""
    prefix = "async " if isinstance(node, ast.AsyncFunctionDef) else ""
    return f"{prefix}{node.name}({arguments}){returns}"


def _assertion_kind(node: ast.Call) -> str | None:
    name = _called_name(node.func)
    if name is None:
        return None
    if name in {"raises", "raises_regex"} or name.endswith(".raises"):
        return "exception"
    if name in {"assert", "assert_equal", "assert_raises"}:
        return "assertion"
    if name.startswith("assert") or name.endswith(".assert_called_once_with"):
        return "assertion"
    if name in {"open", "Path", "write_text", "write_bytes", "unlink", "mkdir"}:
        return "filesystem"
    if name in {"get", "post", "request", "create_connection"}:
        return "external-call"
    return None


def _called_name(node: ast.AST) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        parent = _called_name(node.value)
        return f"{parent}.{node.attr}" if parent else node.attr
    return None


def _expression_text(node: ast.AST) -> str:
    try:
        return ast.unparse(node)
    except (AttributeError, TypeError):
        return type(node).__name__


def _explicit_exports(tree: ast.Module) -> set[str]:
    exports: set[str] = set()
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        if not any(
            isinstance(target, ast.Name) and target.id == "__all__"
            for target in node.targets
        ):
            continue
        value = node.value
        if isinstance(value, (ast.List, ast.Tuple, ast.Set)):
            exports.update(
                item.value
                for item in value.elts
                if isinstance(item, ast.Constant) and isinstance(item.value, str)
            )
    return exports


def _read_python_cli_entries(root: Path) -> tuple[str, ...]:
    path = root / "pyproject.toml"
    if not path.is_file():
        return ()
    try:
        import tomllib

        data = tomllib.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, tomllib.TOMLDecodeError):
        return ()
    project = data.get("project", {})
    scripts = project.get("scripts", {}) if isinstance(project, dict) else {}
    if not isinstance(scripts, dict):
        return ()
    return tuple(sorted(str(name) for name in scripts))


def _is_test_path(path: Path) -> bool:
    return "tests" in path.parts or path.name.startswith("test_") or path.name.endswith("_test.py")


def _module_name(path: Path) -> str:
    without_suffix = path.with_suffix("")
    parts = list(without_suffix.parts)
    if parts and parts[-1] == "__init__":
        parts.pop()
    return ".".join(parts)


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        raise InventoryError(f"cannot read Python source {path}: {exc}") from exc


def _non_comment_lines(text: str) -> int:
    """Count nonblank physical lines that are not comment-only lines."""

    return sum(
        1
        for line in text.splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    )


def _digest_files(root: Path, files: tuple[Path, ...]) -> str:
    digest = hashlib.sha256()
    for path in files:
        relative = path.relative_to(root).as_posix().encode("utf-8")
        data = path.read_bytes()
        digest.update(len(relative).to_bytes(8, "big"))
        digest.update(relative)
        digest.update(len(data).to_bytes(8, "big"))
        digest.update(data)
    return f"sha256:{digest.hexdigest()}"


def _symbol_sort_key(symbol: ApiSymbol) -> tuple[str, int, str]:
    return (symbol.module, symbol.line, symbol.qualified_name)


__all__ = [
    "ApiInventory",
    "ApiSymbol",
    "ImportEdge",
    "InventoryError",
    "InventoryMetrics",
    "TestReference",
    "scan_python_source",
    "write_inventory",
]
