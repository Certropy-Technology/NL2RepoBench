# ruff: noqa: E501
"""Fail-closed static gate for candidate process-spawn boundaries.

This scanner is intentionally narrower than a generic subprocess linter.  A
verifier may run trusted orchestration, but candidate execution must enter the
shared candidate_process_cli transport and its one supervisor primitive.
"""

from __future__ import annotations

import argparse
import ast
import io
import json
import re
import stat
import tokenize
from collections.abc import Iterable
from pathlib import Path, PurePosixPath
from typing import NamedTuple

_PYTHON_SUFFIXES = {".py"}
_NODE_SUFFIXES = {".mjs", ".js", ".cjs"}
_TEXT_SUFFIXES = _PYTHON_SUFFIXES | _NODE_SUFFIXES | {".sh", ".toml", ".json"}

_PYTHON_SUBPROCESS_CALLS = {
    "run",
    "call",
    "check_call",
    "check_output",
    "Popen",
}
_PYTHON_OS_CALLS = {
    "system",
    "popen",
    "spawn",
    "spawnl",
    "spawnle",
    "spawnlp",
    "spawnlpe",
    "spawnv",
    "spawnve",
    "spawnvp",
    "spawnvpe",
    "fork",
    "forkpty",
    "execv",
    "execve",
    "execl",
    "execle",
    "execlp",
    "execvp",
    "execvpe",
}
_PYTHON_RESOURCE_CALLS = {"setrlimit", "prlimit"}
_NODE_CHILD_CALLS = {"spawn", "spawnSync", "exec", "execFile", "fork"}
_SHELL_WORDS = {"runuser", "su", "sudo", "prlimit", "timeout"}

# Exact repo-relative files only.  These files still need shape validation in
# _python_trusted_call/_node_trusted_call; this set is never a directory or a
# suffix match.
_TRUSTED_FILES = {
    "src/nl2repobench/verification/subprocess_supervisor.py",
    "src/nl2repobench/verification/candidate_process_cli.py",
    "src/nl2repobench/verification/candidate_client.py",
    "src/nl2repobench/verification/node_candidate_client.py",
    "src/nl2repobench/verification/node_candidate_install.py",
    "src/nl2repobench/verification/go_supervisor.py",
    "src/nl2repobench/verification/custom_verifier.py",
    "src/nl2repobench/verification/go_contract_runner.py",
    "src/nl2repobench/verification/node/run_tests.mjs",
    "src/nl2repobench/verification/node/validate-package.mjs",
    "src/nl2repobench/verification/node/grade-report.mjs",
}

_DEFAULT_ROOTS = (
    "src/nl2repobench/verification",
    "src/nl2repobench/harbor/compiler.py",
    "src/nl2repobench/harbor/task_writer.py",
    "src/nl2repobench/harbor/node_compiler.py",
    "src/nl2repobench/harbor/pnpm_compiler.py",
    "src/nl2repobench/harbor/go_compiler.py",
    "catalog/sources",
    "catalog/tasks",
)


class _Token(NamedTuple):
    value: str
    kind: str
    line: int


def _violation(path: str, line: int, reason: str, detail: str | None = None) -> dict[str, object]:
    result: dict[str, object] = {"path": path, "line": line, "reason": reason}
    if detail:
        result["detail"] = detail[:4096]
    return result


def _safe_relative(root: Path, path: Path) -> str:
    """Return a canonical relative path, rejecting lexical escape forms."""

    if path.is_symlink():
        raise ValueError("symlink path")
    relative = path.relative_to(root)
    text = PurePosixPath(*relative.parts).as_posix()
    if (
        not text
        or text.startswith("/")
        or any(part in {"", ".", ".."} for part in relative.parts)
    ):
        raise ValueError("path escapes scan root")
    return text


def _walk_regular_files(
    root: Path, *, relative_root: Path | None = None
) -> tuple[list[tuple[str, Path]], list[dict[str, object]]]:
    """Walk without following links and report every unsafe filesystem node."""

    files: list[tuple[str, Path]] = []
    violations: list[dict[str, object]] = []
    display_root = relative_root or root
    try:
        root_stat = root.lstat()
    except OSError as exc:
        return [], [_violation(".", 0, "scan-root-unavailable", str(exc))]
    if not stat.S_ISDIR(root_stat.st_mode) or stat.S_ISLNK(root_stat.st_mode):
        return [], [_violation(".", 0, "scan-root-unsafe")]

    def visit(directory: Path) -> None:
        try:
            entries = sorted(directory.iterdir(), key=lambda item: item.name.encode("utf-8"))
        except OSError as exc:
            try:
                relative = _safe_relative(display_root, directory)
            except ValueError:
                relative = "."
            violations.append(_violation(relative, 0, "directory-unreadable", str(exc)))
            return
        for path in entries:
            try:
                metadata = path.lstat()
                relative = _safe_relative(display_root, path)
            except (OSError, ValueError) as exc:
                try:
                    unsafe_relative = path.relative_to(display_root).as_posix()
                except ValueError:
                    unsafe_relative = "."
                violations.append(_violation(unsafe_relative, 0, "unsafe-path", str(exc)))
                continue
            mode = metadata.st_mode
            if stat.S_ISLNK(mode):
                violations.append(_violation(relative, 0, "symlink-path"))
            elif stat.S_ISDIR(mode):
                visit(path)
            elif stat.S_ISREG(mode):
                files.append((relative, path))
            else:
                violations.append(_violation(relative, 0, "special-path"))

    visit(root)
    return files, violations


def _python_tokens(text: str) -> Iterable[tokenize.TokenInfo]:
    try:
        return tokenize.generate_tokens(io.StringIO(text).readline)
    except (IndentationError, SyntaxError, tokenize.TokenError):
        return ()


def _string_shell_violation(token: tokenize.TokenInfo) -> bool:
    if token.type != tokenize.STRING:
        return False
    value = token.string.lower()
    return any(re.search(rf"(?<![a-z0-9_-]){re.escape(word)}(?![a-z0-9_-])", value) for word in _SHELL_WORDS)


def _python_trusted_call(relative: str, node: ast.Call, text: str) -> bool:
    """Allow only fixed trusted orchestration/transport calls."""

    if relative not in _TRUSTED_FILES:
        return False
    if isinstance(node.func, ast.Attribute) and node.func.attr == "run":
        if relative in {
            "src/nl2repobench/verification/candidate_client.py",
            "src/nl2repobench/verification/node_candidate_client.py",
            "src/nl2repobench/verification/go_supervisor.py",
        }:
            return "candidate_process_cli" in text and "-I" in text and "stdin" in text
        if relative == "src/nl2repobench/verification/custom_verifier.py":
            return "trusted verifier" in text.lower() or "pytest" in text
        if relative == "src/nl2repobench/verification/go_contract_runner.py":
            return "/bin/bash" in text and "args.script" in text
    # The supervisor's explicit fork/exec and the CLI's no-spawn parser are
    # trusted by exact file identity; calls outside those files are not.
    if relative == "src/nl2repobench/verification/subprocess_supervisor.py":
        return isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name) and node.func.value.id == "os"
    return False


def _scan_python(relative: str, text: str) -> list[dict[str, object]]:
    violations: list[dict[str, object]] = []
    try:
        tree = ast.parse(text, filename=relative)
    except SyntaxError as exc:
        return [_violation(relative, exc.lineno or 0, "python-syntax-error", str(exc))]

    subprocess_modules = {"subprocess"}
    os_modules = {"os"}
    resource_modules = {"resource"}
    imported_calls: dict[str, tuple[str, str]] = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for item in node.names:
                name = item.asname or item.name.split(".", 1)[0]
                if item.name == "subprocess":
                    subprocess_modules.add(name)
                elif item.name == "os":
                    os_modules.add(name)
                elif item.name == "resource":
                    resource_modules.add(name)
        elif isinstance(node, ast.ImportFrom) and node.module in {"subprocess", "os", "resource"}:
            for item in node.names:
                imported_calls[item.asname or item.name] = (node.module, item.name)

    for token in _python_tokens(text):
        if _string_shell_violation(token):
            violations.append(_violation(relative, token.start[0], "forbidden-shell-token"))

    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        line = getattr(node, "lineno", 0)
        if any(keyword.arg == "shell" and isinstance(keyword.value, ast.Constant) and keyword.value.value is True for keyword in node.keywords):
            violations.append(_violation(relative, line, "shell-true"))
        module: str | None = None
        member: str | None = None
        if isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name):
            module, member = node.func.value.id, node.func.attr
            if module in subprocess_modules:
                if member in _PYTHON_SUBPROCESS_CALLS and not _python_trusted_call(relative, node, text):
                    violations.append(_violation(relative, line, "python-direct-spawn", f"subprocess.{member}"))
            elif module in os_modules and member in _PYTHON_OS_CALLS:
                if not (relative == "src/nl2repobench/verification/subprocess_supervisor.py"):
                    violations.append(_violation(relative, line, "python-os-spawn", f"os.{member}"))
            elif module in resource_modules and member in _PYTHON_RESOURCE_CALLS:
                if any(
                    isinstance(argument, ast.Attribute) and argument.attr == "RLIMIT_AS"
                    or isinstance(argument, ast.Name) and argument.id == "RLIMIT_AS"
                    for argument in node.args
                ):
                    violations.append(_violation(relative, line, "address-space-limit"))
        elif isinstance(node.func, ast.Name) and node.func.id in imported_calls:
            imported_module, imported_name = imported_calls[node.func.id]
            if imported_module == "subprocess" and imported_name in _PYTHON_SUBPROCESS_CALLS:
                if not _python_trusted_call(relative, node, text):
                    violations.append(_violation(relative, line, "python-direct-spawn", f"from subprocess import {imported_name}"))
            elif imported_module == "os" and imported_name in _PYTHON_OS_CALLS:
                if relative != "src/nl2repobench/verification/subprocess_supervisor.py":
                    violations.append(_violation(relative, line, "python-os-spawn", f"from os import {imported_name}"))
            elif imported_module == "resource" and imported_name in _PYTHON_RESOURCE_CALLS:
                if any(isinstance(argument, ast.Name) and argument.id == "RLIMIT_AS" for argument in node.args):
                    violations.append(_violation(relative, line, "address-space-limit"))
        if isinstance(node.func, ast.Attribute) and node.func.attr in {"system", "popen"}:
            if not _python_trusted_call(relative, node, text):
                violations.append(_violation(relative, line, "python-os-spawn", node.func.attr))
    return violations


def _js_tokens(text: str) -> list[_Token]:
    """Tokenize enough JavaScript to identify calls without trusting comments/strings."""

    tokens: list[_Token] = []
    index = 0
    line = 1
    while index < len(text):
        char = text[index]
        if char in " \t\r":
            index += 1
            continue
        if char == "\n":
            line += 1
            index += 1
            continue
        if text.startswith("//", index):
            end = text.find("\n", index)
            index = len(text) if end < 0 else end
            continue
        if text.startswith("/*", index):
            end = text.find("*/", index + 2)
            chunk = text[index:] if end < 0 else text[index : end + 2]
            line += chunk.count("\n")
            index = len(text) if end < 0 else end + 2
            continue
        if char in "'\"`":
            quote = char
            start = index
            index += 1
            while index < len(text):
                if text[index] == "\\":
                    index += 2
                    continue
                if text[index] == quote:
                    index += 1
                    break
                if text[index] == "\n":
                    line += 1
                index += 1
            tokens.append(_Token(text[start:index], "string", line))
            continue
        match = re.match(r"[A-Za-z_$][A-Za-z0-9_$]*", text[index:])
        if match:
            value = match.group(0)
            tokens.append(_Token(value, "identifier", line))
            index += len(value)
            continue
        tokens.append(_Token(char, "punct", line))
        index += 1
    return tokens


def _js_aliases(tokens: list[_Token]) -> tuple[set[str], set[str]]:
    aliases: set[str] = set()
    module_aliases: set[str] = {"child_process", "cp"}
    for index, token in enumerate(tokens):
        if token.value in {"spawn", "spawnSync", "exec", "execFile", "fork"}:
            aliases.add(token.value)
        if token.value in _NODE_CHILD_CALLS and index + 2 < len(tokens):
            if tokens[index + 1].value == "as" and tokens[index + 2].kind == "identifier":
                aliases.add(tokens[index + 2].value)
            elif tokens[index + 1].value == ":" and tokens[index + 2].kind == "identifier":
                aliases.add(tokens[index + 2].value)
        if token.value == "as" and index + 1 < len(tokens):
            previous = tokens[index - 1].value if index else ""
            if previous == "*" and tokens[index + 1].kind == "identifier":
                module_aliases.add(tokens[index + 1].value)
    return aliases, module_aliases


def _node_trusted_call(relative: str, tokens: list[_Token], index: int, text: str) -> bool:
    if relative not in _TRUSTED_FILES:
        return False
    if relative == "src/nl2repobench/verification/node/run_tests.mjs":
        return "--test" in text and "NODE_TEST_CLIENT" in text
    if relative == "src/nl2repobench/verification/node/validate-package.mjs":
        return '"/usr/bin/tar"' in text or "'/usr/bin/tar'" in text
    if relative == "src/nl2repobench/verification/node/grade-report.mjs":
        return "python" in text and "grade" in text
    return False


def _scan_node(relative: str, text: str) -> list[dict[str, object]]:
    tokens = _js_tokens(text)
    aliases, module_aliases = _js_aliases(tokens)
    violations: list[dict[str, object]] = []
    for index, token in enumerate(tokens):
        if token.value in _SHELL_WORDS or (
            token.kind == "string"
            and any(re.search(rf"(?<![A-Za-z0-9_-]){re.escape(word)}(?![A-Za-z0-9_-])", token.value.lower()) for word in _SHELL_WORDS)
        ):
            violations.append(_violation(relative, token.line, "forbidden-shell-token"))
        if token.value in _NODE_CHILD_CALLS and index + 1 < len(tokens) and tokens[index + 1].value == "(":
            if not _node_trusted_call(relative, tokens, index, text):
                violations.append(_violation(relative, token.line, "node-direct-spawn", token.value))
        if token.value in aliases and index + 1 < len(tokens) and tokens[index + 1].value == "(":
            if not _node_trusted_call(relative, tokens, index, text):
                violations.append(_violation(relative, token.line, "node-direct-spawn", token.value))
        if token.value in module_aliases and index + 2 < len(tokens):
            if tokens[index + 1].value == "." and tokens[index + 2].value in _NODE_CHILD_CALLS:
                if not _node_trusted_call(relative, tokens, index + 2, text):
                    violations.append(_violation(relative, tokens[index + 2].line, "node-direct-spawn", tokens[index + 2].value))
        if token.value == "require" and index + 4 < len(tokens):
            if tokens[index + 1].value == "(" and "child_process" in tokens[index + 2].value:
                if tokens[index + 3].value == "." and tokens[index + 4].value in _NODE_CHILD_CALLS:
                    violations.append(_violation(relative, tokens[index + 4].line, "node-direct-spawn", tokens[index + 4].value))
    return violations


def _scan_file(relative: str, path: Path) -> list[dict[str, object]]:
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        return [_violation(relative, 0, "file-unreadable", str(exc))]
    if path.suffix in _PYTHON_SUFFIXES:
        return _scan_python(relative, text)
    if path.suffix in _NODE_SUFFIXES:
        return _scan_node(relative, text)
    violations: list[dict[str, object]] = []
    for line_number, line in enumerate(text.splitlines(), 1):
        if any(re.search(rf"(?<![A-Za-z0-9_-]){re.escape(word)}(?![A-Za-z0-9_-])", line) for word in _SHELL_WORDS):
            violations.append(_violation(relative, line_number, "forbidden-shell-token"))
        if "RLIMIT_AS" in line or "address-space-bytes" in line or "prlimit --as" in line:
            violations.append(_violation(relative, line_number, "address-space-limit"))
    return violations


def _selected_files(root: Path) -> tuple[list[tuple[str, Path]], list[dict[str, object]]]:
    files: list[tuple[str, Path]] = []
    violations: list[dict[str, object]] = []
    for configured in _DEFAULT_ROOTS:
        path = root / configured
        if path.is_symlink():
            violations.append(_violation(configured, 0, "symlink-root"))
            continue
        if path.is_file():
            try:
                relative = _safe_relative(root, path)
            except ValueError as exc:
                violations.append(_violation(configured, 0, "unsafe-path", str(exc)))
                continue
            files.append((relative, path))
            continue
        if not path.is_dir():
            continue
        found, unsafe = _walk_regular_files(path, relative_root=root)
        files.extend(found)
        violations.extend(unsafe)
    unique: dict[str, Path] = {}
    for relative, path in files:
        unique[relative] = path
    return sorted(unique.items()), violations


def scan(root: Path) -> dict[str, object]:
    """Scan selected candidate/verifier trees and return a JSON-safe report."""

    root = root.absolute()
    files, violations = _selected_files(root)
    scanned = 0
    for relative, path in files:
        # Source/task metadata is not executable scope.  Harbor test/private
        # and generated runtime trees remain in scope, including historical
        # private clients which are release blockers until version-migrated.
        if relative.startswith("catalog/sources/") and "/harbor/tests/" not in relative:
            continue
        if relative.startswith("catalog/tasks/") and not any(
            marker in relative for marker in ("/tests/", "/environment/", "/controls/")
        ):
            continue
        if path.suffix not in _TEXT_SUFFIXES:
            continue
        scanned += 1
        violations.extend(_scan_file(relative, path))
    return {"passed": not violations, "files_scanned": scanned, "violations": violations}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = scan(args.root)
    payload = json.dumps(report, sort_keys=True, separators=(",", ":")) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8")
    else:
        print(payload, end="")
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
