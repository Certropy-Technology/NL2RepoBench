"""Oracle agent for Java tasks whose reference solution stays in private CAS."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path
from types import SimpleNamespace
from typing import Any

from harbor.agents.oracle import OracleAgent  # type: ignore[import-not-found]
from typing_extensions import override

from .domain.models import ArtifactRef
from .harbor.bundle_io import BundleLimits
from .harbor.task_writer import TaskWriterError, extract_private_bundle
from .storage.artifacts import FileArtifactStore, LocalArtifactResolver


class JavaOracleAgent(OracleAgent):  # type: ignore[misc]
    """Run a Java Oracle without embedding its solution in the task bundle."""

    def __init__(
        self,
        logs_dir: Path,
        model_name: str | None = None,
        logger: Any = None,
        extra_env: dict[str, str] | None = None,
        task_dir: Path | None = None,
        trial_paths: Any = None,
        agent_timeout_sec: float | None = None,
        **kwargs: Any,
    ) -> None:
        task_dir_value = task_dir or (extra_env or {}).get("NL2REPO_TASK_DIR")
        if task_dir_value is None:
            raise ValueError("NL2REPO_TASK_DIR is required for JavaOracleAgent")
        resolved_task_dir = Path(task_dir_value)
        resolved_trial_paths = trial_paths or SimpleNamespace(agent_dir=logs_dir)
        super().__init__(
            logs_dir=logs_dir,
            task_dir=resolved_task_dir,
            trial_paths=resolved_trial_paths,
            model_name=model_name,
            logger=logger,
            extra_env=extra_env,
            agent_timeout_sec=agent_timeout_sec,
            **kwargs,
        )
        self._oracle_temp: tempfile.TemporaryDirectory[str] | None = None

    @override
    async def run(self, instruction: str, environment: Any, context: Any) -> None:
        try:
            await super().run(instruction, environment, context)
        finally:
            if self._oracle_temp is not None:
                self._oracle_temp.cleanup()
                self._oracle_temp = None

    def _resolve_solution_paths(self) -> tuple[Path, Path]:
        ref_path = self._task.paths.solution_dir / "oracle-ref.json"
        if ref_path.is_symlink() or not ref_path.is_file():
            raise FileNotFoundError(f"Java Oracle ref is missing: {ref_path}")
        try:
            data = json.loads(ref_path.read_text(encoding="utf-8"))
            if not isinstance(data, dict) or set(data) != {"schema_version", "oracle_ref"}:
                raise ValueError("Oracle ref schema is invalid")
            reference = ArtifactRef.model_validate(data["oracle_ref"])
            if reference.visibility.value != "private":
                raise ValueError("Oracle ref must be private")
            if reference.media_type != "application/vnd.nl2repobench.oracle+tar":
                raise ValueError("Oracle ref media type is invalid")
        except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
            raise FileNotFoundError(f"Java Oracle ref is invalid: {ref_path}") from exc

        cas_root_value = self._get_env("NL2REPO_ORACLE_CAS")
        if not cas_root_value:
            raise FileNotFoundError("NL2REPO_ORACLE_CAS is required for Java Oracle runs")
        cas_root = Path(cas_root_value)
        resolver = LocalArtifactResolver(
            FileArtifactStore(cas_root),
            allow_private=True,
            allowed_private_digests=frozenset({reference.digest}),
        )
        self._oracle_temp = tempfile.TemporaryDirectory(prefix="nl2repo-java-oracle-")
        solution_dir = Path(self._oracle_temp.name) / "solution"
        try:
            extract_private_bundle(
                reference,
                solution_dir,
                artifact_resolver=resolver,
                limits=BundleLimits(
                    max_members=10_000,
                    max_member_bytes=512 * 1024 * 1024,
                    max_total_bytes=2 * 1024 * 1024 * 1024,
                ),
            )
        except TaskWriterError as exc:
            raise FileNotFoundError(f"Java Oracle artifact cannot be extracted: {exc}") from exc
        solve = solution_dir / "solve.sh"
        if solve.is_symlink() or not solve.is_file():
            raise FileNotFoundError("Java Oracle artifact does not contain solve.sh")
        solve.chmod(0o500)
        return solution_dir, solve


__all__ = ["JavaOracleAgent"]
