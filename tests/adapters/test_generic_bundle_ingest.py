import json
import subprocess
from pathlib import Path

from typer.testing import CliRunner

from mwb.cli import app
from mwb.project import ProjectManager

ROOT = Path(__file__).resolve().parents[2]


def init_git_repo(path: Path) -> None:
    subprocess.run(["git", "init", "-b", "main"], cwd=path, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "test@example.local"], cwd=path, check=True)
    subprocess.run(["git", "config", "user.name", "Test User"], cwd=path, check=True)
    (path / "README.md").write_text("# repo\n", encoding="utf-8")
    subprocess.run(["git", "add", "README.md"], cwd=path, check=True)
    subprocess.run(["git", "commit", "-m", "initial"], cwd=path, check=True, capture_output=True)


def test_generic_bundle_adapter_ingests_neutral_mwb_artifacts(
    tmp_path: Path,
    monkeypatch,
) -> None:
    init_git_repo(tmp_path)
    ProjectManager.init(tmp_path, name="mwb-demo")
    monkeypatch.chdir(tmp_path)
    source = ROOT / "tests" / "fixtures" / "generic_runs" / "control_leak"
    runner = CliRunner()

    result = runner.invoke(app, ["ingest", "external", "generic-bundle", str(source)])
    card = runner.invoke(app, ["card", "latest"])

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["adapter_id"] == "generic-bundle"
    assert payload["run_ref"] == "run_external_generic_run_demo_control_leak"
    assert payload["primary_blocker"] == "control_leaky"
    assert card.exit_code == 0, card.output
    assert json.loads(card.output)["run_ref"] == "run_external_generic_run_demo_control_leak"


def test_registry_inspect_and_can_ingest_are_separate_static_and_source_checks(
    tmp_path: Path,
) -> None:
    runner = CliRunner()

    listed = runner.invoke(app, ["adapters", "list", "--json"])
    inspected = runner.invoke(app, ["adapters", "inspect", "generic-bundle", "--json"])
    can_ingest_missing = runner.invoke(
        app,
        ["adapters", "can-ingest", "generic-bundle", str(tmp_path / "missing"), "--json"],
    )

    assert listed.exit_code == 0, listed.output
    assert inspected.exit_code == 0, inspected.output
    assert can_ingest_missing.exit_code == 0, can_ingest_missing.output
    adapters = {row["adapter_id"]: row for row in json.loads(listed.output)["adapters"]}
    assert set(adapters) >= {"generic-bundle", "self-ground"}
    inspect_payload = json.loads(inspected.output)
    assert inspect_payload["status"] == "available"
    assert inspect_payload["modes"] == ["ingest"]
    capability = json.loads(can_ingest_missing.output)
    assert capability["status"] == "unavailable"
    assert capability["errors"]


def test_legacy_adapter_cli_alias_still_serves_conformance_help() -> None:
    runner = CliRunner()

    singular = runner.invoke(app, ["adapter", "conformance", "--help"])
    plural = runner.invoke(app, ["adapters", "list", "--help"])

    assert singular.exit_code == 0, singular.output
    assert plural.exit_code == 0, plural.output
    assert "transformer-lens" in singular.output
    assert "List registered workbench adapters" in plural.output
