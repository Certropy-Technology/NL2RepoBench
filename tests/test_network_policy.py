"""Tests for run-time network egress policy and the catalog lint."""

from __future__ import annotations

from pathlib import Path

import pytest

from nl2repobench.authoring.network_lint import lint_catalog, lint_catalog_roots, lint_task
from nl2repobench.domain.models import EnvironmentLock, HarborExecutionProfile, NetworkPolicy
from nl2repobench.domain.network_policy import (
    NetworkPolicyViolation,
    host_category,
    scan_forbidden_hosts,
    scan_reference_source_acquisition,
    validate_allowed_host,
)

BAKED = 'offline_dependencies = "preinstalled-image"'


def _task_toml(policy: str, *, agent_mode: str = "no-network", env_mode: str = "no-network") -> str:
    return f"""schema_version = "1.0"
task_id = "sample"
version = "0.1.0"
instruction = "instruction.md"

[source]
upstream_url = "https://github.com/example/sample"

[environment]
network_mode = "{env_mode}"
{policy}

[tests]
framework = "pytest"
expected_total = 1
commands = ["pytest"]

[harbor]
description = "d"
keywords = ["a", "b", "c"]
agent_network_mode = "{agent_mode}"
"""


class TestPolicyModel:
    def test_no_network_with_baked_dependencies_is_the_default_shape(self) -> None:
        policy = NetworkPolicy(mode="no-network", offline_dependencies="preinstalled-image")
        assert policy.mode == "no-network"
        assert policy.allowed_hosts == ()
        assert policy.reference_source_fetch == "forbidden"

    def test_public_mode_is_not_expressible(self) -> None:
        with pytest.raises(ValueError):
            NetworkPolicy(mode="public")  # type: ignore[arg-type]

    def test_allowlist_splits_registry_from_model_provider(self) -> None:
        policy = NetworkPolicy(
            mode="allowlist",
            allowed_hosts=["api.openai.com", "pypi.org"],
            offline_dependencies="preinstalled-image",
            reason="package X cannot be baked",
        )
        assert policy.model_provider_hosts == ("api.openai.com",)
        assert policy.registry_hosts == ("pypi.org",)

    def test_allowlist_requires_hosts_and_reason(self) -> None:
        with pytest.raises(ValueError):
            NetworkPolicy(mode="allowlist", reason="why")
        with pytest.raises(ValueError):
            NetworkPolicy(mode="allowlist", allowed_hosts=["pypi.org"])

    def test_hosts_rejected_outside_allowlist_mode(self) -> None:
        with pytest.raises(ValueError):
            NetworkPolicy(mode="no-network", allowed_hosts=["pypi.org"])

    def test_missing_dependencies_requires_a_blocker_reason(self) -> None:
        with pytest.raises(ValueError):
            NetworkPolicy(mode="no-network", offline_dependencies="missing")
        assert (
            NetworkPolicy(
                mode="no-network", offline_dependencies="missing", reason="wheelhouse absent"
            ).offline_dependencies
            == "missing"
        )

    @pytest.mark.parametrize(
        "host",
        [
            "github.com",
            "raw.githubusercontent.com",
            "codeload.github.com",
            "gitlab.com",
            "bitbucket.org",
            "sourceforge.net",
            "registry.npmmirror.com",
            "pypi.tuna.tsinghua.edu.cn",
            "cdn.jsdelivr.net",
        ],
    )
    def test_source_serving_hosts_are_forbidden(self, host: str) -> None:
        with pytest.raises(NetworkPolicyViolation):
            validate_allowed_host(host)

    @pytest.mark.parametrize(
        "host",
        ["*.pypi.org", "*", "https://pypi.org/simple", "pypi.org:443", "pypi.org/simple", ""],
    )
    def test_ambiguous_entries_are_rejected(self, host: str) -> None:
        with pytest.raises(NetworkPolicyViolation):
            validate_allowed_host(host)

    def test_admissible_hosts_are_categorized(self) -> None:
        assert host_category("pypi.org") == "registry"
        assert host_category("api.anthropic.com") == "model-provider"
        assert host_category("example.com") is None

    def test_environment_lock_rejects_contradiction(self) -> None:
        baked = NetworkPolicy(mode="no-network", offline_dependencies="preinstalled-image")
        with pytest.raises(ValueError):
            EnvironmentLock(network_mode="public", network_policy=baked)
        assert (
            EnvironmentLock(network_mode="no-network", network_policy=baked).network_policy is baked
        )

    def test_harbor_profile_allowlist_requires_hosts(self) -> None:
        with pytest.raises(ValueError):
            HarborExecutionProfile(
                description="d", keywords=("a", "b", "c"), agent_network_mode="allowlist"
            )

    def test_harbor_profile_policy_override_is_compiler_authority(self) -> None:
        profile = HarborExecutionProfile(
            description="d", keywords=("a", "b", "c"), agent_network_mode="public"
        )
        policy = NetworkPolicy(mode="no-network", offline_dependencies="preinstalled-image")
        resolved = profile.apply_network_policy(policy)
        assert resolved.agent_network_mode == "no-network"
        assert resolved.agent_allowed_hosts == ()

    def test_v2_environment_accepts_network_policy(self) -> None:
        from nl2repobench.domain.models_v2 import EnvironmentLockV2

        policy = NetworkPolicy(mode="no-network", offline_dependencies="preinstalled-image")
        env = EnvironmentLockV2(network_mode="no-network", network_policy=policy)
        assert env.network_policy is policy


class TestReferenceSourceScan:
    @pytest.mark.parametrize(
        "text",
        [
            "git clone https://github.com/x/y",
            'git -C "$SOURCE_DIR" fetch --depth 1 origin abc',
            "pip install git+https://github.com/x/y",
            "curl -L https://raw.githubusercontent.com/x/y/main/a.py",
        ],
    )
    def test_acquisition_is_detected(self, text: str) -> None:
        assert scan_reference_source_acquisition(text)

    def test_line_breaks_do_not_create_false_positives(self) -> None:
        assert scan_reference_source_acquisition("we use git\nplease clone the docs") == ()

    def test_forbidden_hosts_need_a_fetchable_url(self) -> None:
        assert scan_forbidden_hosts("hosted on github.com") == ()
        assert scan_forbidden_hosts("https://github.com/x/y")


class TestCatalogLint:
    def _write(self, root: Path, name: str, toml: str, *, bundle: bool = True) -> Path:
        task = root / name
        task.mkdir(parents=True)
        (task / "task.toml").write_text(toml)
        (task / "instruction.md").write_text("Build the library.\n")
        if bundle:
            (task / "harbor").mkdir()
            (task / "harbor" / "task.toml").write_text('schema_version = "1.4"\n')
        return task

    def test_compliant_task_has_no_findings(self, tmp_path: Path) -> None:
        task = self._write(
            tmp_path,
            "ok",
            _task_toml(f'[environment.network_policy]\nmode = "no-network"\n{BAKED}'),
        )
        findings, has_bundle, has_policy = lint_task(task)
        assert has_bundle and has_policy
        assert [f for f in findings if f.severity == "error"] == []

    def test_missing_policy_on_bundle_is_an_error(self, tmp_path: Path) -> None:
        task = self._write(tmp_path, "nopolicy", _task_toml(""))
        findings, _, has_policy = lint_task(task)
        assert not has_policy
        assert any(f.rule == "policy-missing" and f.severity == "error" for f in findings)

    def test_flat_harbor_runtime_no_network_is_accepted(self, tmp_path: Path) -> None:
        task = self._write(tmp_path, "flat", _task_toml(""), bundle=False)
        (task / "environment").mkdir()
        (task / "solution").mkdir()
        (task / "tests").mkdir()
        text = (task / "task.toml").read_text()
        (task / "task.toml").write_text(
            text.replace('schema_version = "1.0"', 'schema_version = "1.4"')
        )
        findings, has_bundle, has_policy = lint_task(task)
        assert has_bundle and has_policy
        assert not any(f.rule == "policy-missing" and f.severity == "error" for f in findings)

    def test_flat_harbor_runtime_public_is_an_error(self, tmp_path: Path) -> None:
        task = self._write(tmp_path, "flat-public", _task_toml("", env_mode="public"), bundle=False)
        (task / "environment").mkdir()
        (task / "solution").mkdir()
        (task / "tests").mkdir()
        (task / "task.toml").write_text(
            (task / "task.toml")
            .read_text()
            .replace('schema_version = "1.0"', 'schema_version = "1.4"')
        )
        findings, has_bundle, _ = lint_task(task)
        assert has_bundle
        assert any(f.rule == "agent-network-public" and f.severity == "error" for f in findings)

    def test_public_agent_mode_is_an_error(self, tmp_path: Path) -> None:
        task = self._write(
            tmp_path,
            "pub",
            _task_toml(
                f'[environment.network_policy]\nmode = "no-network"\n{BAKED}', agent_mode="public"
            ),
        )
        findings, _, _ = lint_task(task)
        assert any(f.rule == "agent-network-public" for f in findings)

    def test_mode_contradiction_is_an_error(self, tmp_path: Path) -> None:
        task = self._write(
            tmp_path,
            "clash",
            _task_toml(
                f'[environment.network_policy]\nmode = "no-network"\n{BAKED}', env_mode="public"
            ),
        )
        findings, _, _ = lint_task(task)
        assert any(f.rule == "network-mode-contradiction" for f in findings)

    def test_forbidden_allowlist_host_is_an_error(self, tmp_path: Path) -> None:
        task = self._write(
            tmp_path,
            "bad",
            _task_toml(
                '[environment.network_policy]\nmode = "allowlist"\n'
                'allowed_hosts = ["github.com"]\nreason = "r"\n' + BAKED
            ),
        )
        findings, _, _ = lint_task(task)
        assert any(f.rule == "allowlist-host-forbidden" for f in findings)

    def _with_solution(self, tmp_path: Path, name: str, script: str) -> Path:
        task = self._write(
            tmp_path,
            name,
            _task_toml(f'[environment.network_policy]\nmode = "no-network"\n{BAKED}'),
        )
        solution = task / "harbor" / "solution"
        solution.mkdir(parents=True)
        (solution / "solve.sh").write_text(script)
        return task

    def test_unverified_oracle_fetch_is_an_error(self, tmp_path: Path) -> None:
        task = self._with_solution(
            tmp_path,
            "unverified",
            'git -C "$SRC" fetch --depth 1 origin abc\ncp -a "$SRC/." /workspace/\n',
        )
        findings, _, _ = lint_task(task)
        assert any(f.rule == "oracle-source-unverified" and f.severity == "error" for f in findings)

    def test_digest_verified_oracle_fetch_is_allowed(self, tmp_path: Path) -> None:
        revision = "a" * 40
        task = self._with_solution(
            tmp_path,
            "verified",
            f'UPSTREAM_REVISION="{revision}"\n'
            f'git -C "$SRC" fetch -q --depth 1 origin "$UPSTREAM_REVISION"\n'
            f'git -C "$SRC" archive --format=tar "$UPSTREAM_REVISION" > "$A"\n'
            'printf \'%s  %s\\n\' "$SHA" "$A" | sha256sum --check --strict\n',
        )
        findings, _, _ = lint_task(task)
        assert [f for f in findings if f.severity == "error"] == []
        assert any(f.rule == "oracle-requires-host-authorization" for f in findings)

    def test_tree_verified_oracle_fetch_is_allowed(self, tmp_path: Path) -> None:
        revision = "c" * 40
        tree = "d" * 40
        task = self._with_solution(
            tmp_path,
            "treeverified",
            f'UPSTREAM_REVISION="{revision}"\n'
            f'EXPECTED_TREE="{tree}"\n'
            f'git -C "$SRC" fetch -q --depth 1 origin "$UPSTREAM_REVISION"\n'
            'resolved_tree="$(git -C "$SRC" rev-parse "${UPSTREAM_REVISION}^{tree}")"\n'
            'if [[ "$resolved_tree" != "$EXPECTED_TREE" ]]; then exit 1; fi\n',
        )
        findings, _, _ = lint_task(task)
        assert [f for f in findings if f.severity == "error"] == []

    def test_tree_value_without_a_lookup_is_not_verification(self, tmp_path: Path) -> None:
        revision = "e" * 40
        task = self._with_solution(
            tmp_path,
            "treefake",
            f'UPSTREAM_REVISION="{revision}"\n'
            f'EXPECTED_TREE="{"f" * 40}"\n'
            f'git -C "$SRC" fetch -q --depth 1 origin "$UPSTREAM_REVISION"\n',
        )
        findings, _, _ = lint_task(task)
        assert any(f.rule == "oracle-source-unverified" for f in findings)

    def test_digest_verified_but_unpinned_revision_is_an_error(self, tmp_path: Path) -> None:
        task = self._with_solution(
            tmp_path,
            "moving-ref",
            'git -C "$SRC" fetch --depth 1 origin main\n'
            'printf \'%s  %s\\n\' "$SHA" "$A" | sha256sum --check --strict\n',
        )
        findings, _, _ = lint_task(task)
        assert any(f.rule == "oracle-source-unpinned-revision" for f in findings)

    def test_solution_upstream_url_is_not_a_leak(self, tmp_path: Path) -> None:
        revision = "b" * 40
        task = self._with_solution(
            tmp_path,
            "solurl",
            f'UPSTREAM_URL="https://github.com/example/sample"\n'
            f'UPSTREAM_REVISION="{revision}"\n'
            f'git -C "$SRC" fetch -q --depth 1 origin "$UPSTREAM_REVISION"\n'
            'printf \'%s  %s\\n\' "$SHA" "$A" | sha256sum --check --strict\n',
        )
        findings, _, _ = lint_task(task)
        assert not any(f.rule == "upstream-source-endpoint" for f in findings)

    def test_provenance_url_in_task_toml_is_not_a_finding(self, tmp_path: Path) -> None:
        task = self._write(
            tmp_path,
            "prov",
            _task_toml(f'[environment.network_policy]\nmode = "no-network"\n{BAKED}'),
        )
        findings, _, _ = lint_task(task)
        assert not any("task.toml" in (f.location or "") and "endpoint" in f.rule for f in findings)

    def test_own_upstream_source_endpoint_is_an_error(self, tmp_path: Path) -> None:
        task = self._write(
            tmp_path,
            "leak",
            _task_toml(f'[environment.network_policy]\nmode = "no-network"\n{BAKED}'),
        )
        (task / "instruction.md").write_text(
            "Fetch https://raw.githubusercontent.com/example/sample/main/core.py\n"
        )
        findings, _, _ = lint_task(task)
        assert any(f.rule == "upstream-source-endpoint" and f.severity == "error" for f in findings)

    def test_third_party_project_page_is_not_an_error(self, tmp_path: Path) -> None:
        task = self._write(
            tmp_path,
            "docref",
            _task_toml(f'[environment.network_policy]\nmode = "no-network"\n{BAKED}'),
        )
        (task / "instruction.md").write_text(
            "Expand 'gh' into https://github.com/other/template as the library documents.\n"
        )
        findings, _, _ = lint_task(task)
        assert [f for f in findings if f.severity == "error"] == []

    def test_lint_catalog_aggregates_counts(self, tmp_path: Path) -> None:
        self._write(
            tmp_path, "a", _task_toml(f'[environment.network_policy]\nmode = "no-network"\n{BAKED}')
        )
        self._write(tmp_path, "b", _task_toml(""), bundle=True)
        report = lint_catalog(tmp_path)
        assert report.tasks_scanned == 2
        assert report.tasks_with_bundle == 2
        assert report.tasks_with_policy == 1
        assert report.as_dict()["error_count"] == len(report.errors)

    def test_lint_catalog_roots_deduplicates_findings(self, tmp_path: Path) -> None:
        source = tmp_path / "sources"
        generated = tmp_path / "tasks"
        self._write(source, "same", _task_toml(""), bundle=True)
        self._write(generated, "same", _task_toml(""), bundle=True)
        report = lint_catalog_roots(source, generated)
        assert report.tasks_scanned == 2
        assert sum(f.rule == "policy-missing" for f in report.findings) == 1

    def test_missing_root_is_reported(self, tmp_path: Path) -> None:
        report = lint_catalog(tmp_path / "absent")
        assert any(f.rule == "tasks-root-missing" for f in report.findings)
