"""Small fixture for the static Python inventory."""

import requests  # noqa: F401

__all__ = ["Parser"]


class Parser:
    def parse(self, value: str, *, strict: bool = True) -> str:
        if strict and not value:
            raise ValueError("empty")
        return value.strip()


def helper(value: str) -> str:
    return value


def dynamic(value: str) -> object:
    return eval(value, {})
