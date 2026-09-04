"""Deterministic compilation of canonical tasks into Harbor bundles."""

__all__ = [
    "HarborCompileError",
    "HarborCompiler",
    "HarborToolchainLock",
    "load_toolchain_lock",
]


def __getattr__(name: str) -> object:
    if name in {"HarborCompileError", "HarborCompiler"}:
        from .compiler import HarborCompileError, HarborCompiler

        return {"HarborCompileError": HarborCompileError, "HarborCompiler": HarborCompiler}[name]
    if name in {"HarborToolchainLock", "load_toolchain_lock"}:
        from .models import HarborToolchainLock, load_toolchain_lock

        values = {
            "HarborToolchainLock": HarborToolchainLock,
            "load_toolchain_lock": load_toolchain_lock,
        }
        return values[name]
    raise AttributeError(name)
