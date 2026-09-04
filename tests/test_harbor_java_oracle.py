from __future__ import annotations

import asyncio
import json
import sys
import tempfile
from pathlib import Path
from types import ModuleType, SimpleNamespace
from unittest.mock import AsyncMock

import pytest


class _OracleAgent:
    def __init__(self, **kwargs: object) -> None:
        self._task = SimpleNamespace(
            paths=SimpleNamespace(solution_dir=Path(str(kwargs["task_dir"])))
        )

    async def run(self, instruction: str, environment: object, context: object) -> None:
        del instruction, environment, context


harbor = ModuleType("harbor")
harbor_agents = ModuleType("harbor.agents")
harbor_oracle = ModuleType("harbor.agents.oracle")
harbor_oracle.OracleAgent = _OracleAgent  # type: ignore[attr-defined]
sys.modules.setdefault("harbor", harbor)
sys.modules.setdefault("harbor.agents", harbor_agents)
sys.modules.setdefault("harbor.agents.oracle", harbor_oracle)

from nl2repobench.domain.models import Visibility  # noqa: E402
from nl2repobench.harbor_java_oracle import JavaOracleAgent  # noqa: E402
from nl2repobench.storage.artifacts import FileArtifactStore  # noqa: E402
from nl2repobench.storage.canonical_ustar import (  # noqa: E402
    CanonicalEntry,
    encode_ustar,
)


def _agent_with_oracle(tmp_path: Path) -> tuple[JavaOracleAgent, Path]:
    store = FileArtifactStore(tmp_path / "cas")
    reference = store.put_bytes(
        encode_ustar(
            (CanonicalEntry("solve.sh", "file", 0o555, b"#!/bin/sh\nexit 0\n"),)
        ),
        media_type="application/vnd.nl2repobench.oracle+tar",
        visibility=Visibility.PRIVATE,
    )
    solution = tmp_path / "task/solution"
    solution.mkdir(parents=True)
    (solution / "oracle-ref.json").write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "oracle_ref": reference.model_dump(mode="json"),
            },
            sort_keys=True,
        ),
        encoding="utf-8",
    )
    agent = object.__new__(JavaOracleAgent)
    agent._task = SimpleNamespace(paths=SimpleNamespace(solution_dir=solution))
    agent._oracle_temp = None
    agent._get_env = lambda name: str(store.root) if name == "NL2REPO_ORACLE_CAS" else None
    return agent, solution


def test_java_oracle_resolves_private_solution_from_scoped_cas(tmp_path: Path) -> None:
    agent, _ = _agent_with_oracle(tmp_path)

    solution, solve = agent._resolve_solution_paths()  # noqa: SLF001

    assert solve == solution / "solve.sh"
    assert solve.read_text(encoding="utf-8") == "#!/bin/sh\nexit 0\n"
    assert agent._oracle_temp is not None  # noqa: SLF001
    agent._oracle_temp.cleanup()  # noqa: SLF001


def test_java_oracle_rejects_missing_or_invalid_refs(tmp_path: Path) -> None:
    agent, solution = _agent_with_oracle(tmp_path)
    ref = solution / "oracle-ref.json"
    ref.unlink()
    with pytest.raises(FileNotFoundError, match="ref is missing"):
        agent._resolve_solution_paths()  # noqa: SLF001

    ref.write_text('{"schema_version":"1.0","extra":true}', encoding="utf-8")
    with pytest.raises(FileNotFoundError, match="ref is invalid"):
        agent._resolve_solution_paths()  # noqa: SLF001


def test_java_oracle_requires_cas_and_cleans_temporary_solution(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    agent, _ = _agent_with_oracle(tmp_path)
    agent._get_env = lambda _name: None
    with pytest.raises(FileNotFoundError, match="NL2REPO_ORACLE_CAS"):
        agent._resolve_solution_paths()  # noqa: SLF001

    temporary = tempfile.TemporaryDirectory()
    agent._oracle_temp = temporary
    run = AsyncMock(return_value=None)
    monkeypatch.setattr(_OracleAgent, "run", run)
    asyncio.run(agent.run("instruction", object(), object()))
    run.assert_awaited_once()
    assert agent._oracle_temp is None  # noqa: SLF001


def test_java_oracle_init_requires_task_directory(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="NL2REPO_TASK_DIR"):
        JavaOracleAgent(logs_dir=tmp_path, extra_env={})


def test_java_oracle_rejects_public_or_wrong_media_reference(tmp_path: Path) -> None:
    agent, solution = _agent_with_oracle(tmp_path)
    path = solution / "oracle-ref.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["oracle_ref"]["visibility"] = "public"
    payload["oracle_ref"]["uri"] = payload["oracle_ref"]["uri"].replace(
        "private", "public"
    )
    path.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(FileNotFoundError, match="ref is invalid"):
        agent._resolve_solution_paths()  # noqa: SLF001

    payload["oracle_ref"]["visibility"] = "private"
    payload["oracle_ref"]["uri"] = payload["oracle_ref"]["uri"].replace(
        "public", "private"
    )
    payload["oracle_ref"]["media_type"] = "application/octet-stream"
    path.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(FileNotFoundError, match="ref is invalid"):
        agent._resolve_solution_paths()  # noqa: SLF001
