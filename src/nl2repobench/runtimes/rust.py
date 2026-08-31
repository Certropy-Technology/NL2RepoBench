"""Rust/Cargo R0 policy primitives."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Never

from nl2repobench.domain.canonical_contract import PackageManager, RuntimeLanguage
from nl2repobench.domain.runtime import RuntimeDiscriminator

SELECTED_TARGET = "x86_64-unknown-linux-gnu"
TARGET_SELECTOR_VERSION = "rust-target-selector-v1"

_TARGET_VALUES = {
    "target_arch": "x86_64",
    "target_os": "linux",
    "target_env": "gnu",
    "target_family": "unix",
    "target_pointer_width": "64",
}
_FEATURE_NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_+.-]*$")


def _utf8_key(value: str) -> bytes:
    return value.encode("utf-8")


def cargo_feature_args(
    default_features: bool, enabled_sorted: tuple[str, ...]
) -> tuple[str, ...]:
    """Return the sole canonical Cargo feature argv fragment."""

    if not isinstance(default_features, bool):
        raise ValueError("default_features must be a boolean")
    if any(
        not isinstance(item, str) or not _FEATURE_NAME.fullmatch(item)
        for item in enabled_sorted
    ):
        raise ValueError("Cargo features must use the frozen feature-name grammar")
    if tuple(sorted(enabled_sorted, key=_utf8_key)) != enabled_sorted or len(
        set(enabled_sorted)
    ) != len(enabled_sorted):
        raise ValueError("Cargo features must be sorted and unique")
    result: list[str] = []
    if not default_features:
        result.append("--no-default-features")
    if enabled_sorted:
        result.extend(("--features", ",".join(enabled_sorted)))
    return tuple(result)


@dataclass(frozen=True, slots=True)
class _Selector:
    kind: str
    value: tuple[str, str] | str | None = None
    children: tuple[_Selector, ...] = ()

    def evaluate(self) -> bool:
        if self.kind == "triple":
            return self.value == SELECTED_TARGET
        if self.kind == "atom":
            assert isinstance(self.value, tuple)
            return _TARGET_VALUES[self.value[0]] == self.value[1]
        if self.kind == "all":
            return all(child.evaluate() for child in self.children)
        if self.kind == "any":
            return any(child.evaluate() for child in self.children)
        if self.kind == "not":
            return not self.children[0].evaluate()
        raise AssertionError(f"unknown selector node: {self.kind}")

    def canonical(self) -> str:
        if self.kind == "triple":
            assert isinstance(self.value, str)
            return self.value
        if self.kind == "atom":
            assert isinstance(self.value, tuple)
            return f'{self.value[0]}="{self.value[1]}"'
        if self.kind == "not":
            return f"not({self.children[0].canonical()})"
        return f"{self.kind}({','.join(child.canonical() for child in self.children)})"


class _SelectorParser:
    def __init__(self, source: str) -> None:
        self.source = source
        self.offset = 0

    def parse(self) -> _Selector:
        if self.source == SELECTED_TARGET:
            return _Selector("triple", SELECTED_TARGET)
        if not self._take("cfg("):
            self._fail()
        result = self._selector()
        if not self._take(")") or self.offset != len(self.source):
            self._fail()
        return result

    def _selector(self) -> _Selector:
        for operator in ("all", "any"):
            if self._take(f"{operator}("):
                children = [self._selector()]
                if not self._take(","):
                    self._fail()
                children.append(self._selector())
                while self._take(","):
                    children.append(self._selector())
                if not self._take(")"):
                    self._fail()
                return _Selector(operator, children=tuple(children))
        if self._take("not("):
            child = self._selector()
            if not self._take(")"):
                self._fail()
            return _Selector("not", children=(child,))
        for name, value in _TARGET_VALUES.items():
            token = f'{name}="{value}"'
            if self._take(token):
                return _Selector("atom", (name, value))
        self._fail()

    def _take(self, token: str) -> bool:
        if self.source.startswith(token, self.offset):
            self.offset += len(token)
            return True
        return False

    def _fail(self) -> Never:
        raise ValueError(
            f"target selector is outside the frozen grammar at byte {self.offset}: "
            f"{self.source!r}"
        )


def _parse_target_selector(selector: str) -> _Selector:
    if not isinstance(selector, str) or not selector:
        raise ValueError("target selector must be a non-empty string")
    return _SelectorParser(selector).parse()


def normalize_target_selector(selector: str) -> str:
    """Validate and return the byte-exact canonical selector spelling."""

    parsed = _parse_target_selector(selector)
    canonical = parsed.canonical()
    if selector.startswith("cfg("):
        canonical = f"cfg({canonical})"
    if canonical != selector:
        raise ValueError("target selector is not in canonical form")
    return canonical


def evaluate_target_selector(selector: str) -> bool:
    """Evaluate one canonical selector against the single Rust v1 target."""

    normalize_target_selector(selector)
    return _parse_target_selector(selector).evaluate()


@dataclass(frozen=True)
class RustRuntimeAdapter:
    identity = RuntimeDiscriminator(
        language=RuntimeLanguage.RUST,
        package_manager=PackageManager.CARGO,
    )
    runtime = "rust"


__all__ = [
    "SELECTED_TARGET",
    "TARGET_SELECTOR_VERSION",
    "RustRuntimeAdapter",
    "cargo_feature_args",
    "evaluate_target_selector",
    "normalize_target_selector",
]
