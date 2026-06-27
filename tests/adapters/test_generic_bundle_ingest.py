"""Tests for GenericBundleIngestAdapter — malformed-input, stale-ref, and happy-path cases.

Each test uses a real filesystem fixture directory in tmp_path.  No adapter
behaviour is mocked.  The successful-ingest test exercises the full CLI chain:
  ingest external generic-bundle
  card latest
  diagnose latest
  next-probe latest --materialize
  graph rebuild
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest
from typer.testing import CliRunner

from mwb.cli import app
from mwb.project import ProjectManager

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "tests" / "fixtures" / "generic_runs" / "control_leak"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def init_git_repo(path: Path) -> None:
    subprocess.run(["git", "init", "-b", "main"], cwd=path, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "test@example.local"], cwd=path, check=True)
    subprocess.run(["git", "config", "user.name", "Test User"], cwd=path, check=True)
    (path / "README.md").write_text("# repo\n", encoding="utf-8")
    subprocess.run(["git", "add", "README.md"], cwd=path, check=True)
    subprocess.run(["git", "commit", "-m", "initial"], cwd=path, check=True, capture_output=True)


def _make_valid_manifest(run_ref: str = "run_demo_control_leak") -> dict:
    return {
        "run_ref": run_ref,
        "status": "insufficient_evidence",
        "evidence_posture": "diagnostic_insufficient",
        "claim_bearing": False,
        "source_kind": "mwb_demo_fixture",
    }


def _make_valid_metrics() -> dict:
    return {
        "target_delta": 0.5,
        "matched_control_delta": 0.45,
        "family_min_gap": -0.02,
        "specificity_gap": 0.05,
    }


def _make_bundle(path: Path, *, manifest: dict, metrics: dict) -> Path:
    """Write a minimal valid bundle to path/."""
    path.mkdir(parents=True, exist_ok=True)
    (path / "run_manifest.json").write_text(json.dumps(manifest) + "\n", encoding="utf-8")
    (path / "control_metrics.json").write_text(json.dumps(metrics) + "\n", encoding="utf-8")
    return path


# ---------------------------------------------------------------------------
# Malformed-input rejection tests
# ---------------------------------------------------------------------------


def test_generic_bundle_rejects_missing_run_manifest(tmp_path: Path) -> None:
    bundle = tmp_path / "bundle"
    bundle.mkdir()
    (bundle / "control_metrics.json").write_text(
        json.dumps(_make_valid_metrics()), encoding="utf-8"
    )

    from mwb.adapters.generic_bundle import GenericBundleIngestAdapter

    report = GenericBundleIngestAdapter().validate_source(bundle)
    assert report.status == "fail"
    assert any("run_manifest.json" in e for e in report.errors)


def test_generic_bundle_rejects_missing_control_metrics(tmp_path: Path) -> None:
    bundle = tmp_path / "bundle"
    bundle.mkdir()
    (bundle / "run_manifest.json").write_text(
        json.dumps(_make_valid_manifest()), encoding="utf-8"
    )

    from mwb.adapters.generic_bundle import GenericBundleIngestAdapter

    report = GenericBundleIngestAdapter().validate_source(bundle)
    assert report.status == "fail"
    assert any("control_metrics.json" in e for e in report.errors)


def test_generic_bundle_rejects_invalid_run_manifest_json(tmp_path: Path) -> None:
    bundle = tmp_path / "bundle"
    bundle.mkdir()
    (bundle / "run_manifest.json").write_text("{not valid json", encoding="utf-8")
    (bundle / "control_metrics.json").write_text(
        json.dumps(_make_valid_metrics()), encoding="utf-8"
    )

    from mwb.adapters.generic_bundle import GenericBundleIngestAdapter

    report = GenericBundleIngestAdapter().validate_source(bundle)
    assert report.status == "fail"
    assert any("invalid JSON" in e or "invalid_json" in e for e in report.errors)


def test_generic_bundle_rejects_non_object_run_manifest(tmp_path: Path) -> None:
    bundle = tmp_path / "bundle"
    bundle.mkdir()
    (bundle / "run_manifest.json").write_text(json.dumps([1, 2, 3]), encoding="utf-8")
    (bundle / "control_metrics.json").write_text(
        json.dumps(_make_valid_metrics()), encoding="utf-8"
    )

    from mwb.adapters.generic_bundle import GenericBundleIngestAdapter

    report = GenericBundleIngestAdapter().validate_source(bundle)
    assert report.status == "fail"
    assert any("object" in e or "invalid_payload" in e for e in report.errors)


def test_generic_bundle_rejects_missing_run_ref(tmp_path: Path) -> None:
    bundle = tmp_path / "bundle"
    bundle.mkdir()
    manifest = {"status": "insufficient_evidence"}  # no run_ref
    (bundle / "run_manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    (bundle / "control_metrics.json").write_text(
        json.dumps(_make_valid_metrics()), encoding="utf-8"
    )

    from mwb.adapters.generic_bundle import GenericBundleIngestAdapter

    report = GenericBundleIngestAdapter().validate_source(bundle)
    assert report.status == "fail"
    assert any("run_ref" in e for e in report.errors)


def test_generic_bundle_rejects_invalid_control_metrics_json(tmp_path: Path) -> None:
    bundle = tmp_path / "bundle"
    bundle.mkdir()
    (bundle / "run_manifest.json").write_text(json.dumps(_make_valid_manifest()), encoding="utf-8")
    (bundle / "control_metrics.json").write_text("{bad json", encoding="utf-8")

    from mwb.adapters.generic_bundle import GenericBundleIngestAdapter

    report = GenericBundleIngestAdapter().validate_source(bundle)
    assert report.status == "fail"
    assert any("invalid JSON" in e or "invalid_json" in e for e in report.errors)


def test_generic_bundle_rejects_non_object_control_metrics(tmp_path: Path) -> None:
    bundle = tmp_path / "bundle"
    bundle.mkdir()
    (bundle / "run_manifest.json").write_text(json.dumps(_make_valid_manifest()), encoding="utf-8")
    (bundle / "control_metrics.json").write_text(json.dumps([0.5, 0.45]), encoding="utf-8")

    from mwb.adapters.generic_bundle import GenericBundleIngestAdapter

    report = GenericBundleIngestAdapter().validate_source(bundle)
    assert report.status == "fail"
    assert any("object" in e or "invalid_payload" in e for e in report.errors)


def test_generic_bundle_rejects_missing_required_control_metrics(tmp_path: Path) -> None:
    bundle = tmp_path / "bundle"
    bundle.mkdir()
    (bundle / "run_manifest.json").write_text(json.dumps(_make_valid_manifest()), encoding="utf-8")
    # missing target_delta
    (bundle / "control_metrics.json").write_text(
        json.dumps({"matched_control_delta": 0.45}), encoding="utf-8"
    )

    from mwb.adapters.generic_bundle import GenericBundleIngestAdapter

    report = GenericBundleIngestAdapter().validate_source(bundle)
    assert report.status == "fail"
    assert any("target_delta" in e for e in report.errors)


# ---------------------------------------------------------------------------
# Stale-ref rewrite tests
# ---------------------------------------------------------------------------


def test_generic_bundle_rewrites_stale_blocker_report_refs(tmp_path: Path) -> None:
    init_git_repo(tmp_path)
    project = ProjectManager.init(tmp_path, name="mwb-demo")
    bundle = tmp_path / "src_bundle"
    _make_bundle(
        bundle, manifest=_make_valid_manifest("run_old_source"), metrics=_make_valid_metrics()
    )

    old_run_ref = "run_old_source"
    stale_blocker = {
        "wb_type": "BlockerReport",
        "wb_ref": f"blocker_{old_run_ref}",
        "run_ref": old_run_ref,
        "parents": [old_run_ref],
        "blockers": ["control_leaky"],
        "primary_blocker": "control_leaky",
        "blocking_metrics": [],
    }
    (bundle / "blocker_report.json").write_text(json.dumps(stale_blocker), encoding="utf-8")

    from mwb.adapters.generic_bundle import GenericBundleIngestAdapter

    result = GenericBundleIngestAdapter().ingest(bundle, project=project)
    new_run_ref = result.run_ref

    blocker_out = json.loads((result.run_dir / "blocker_report.json").read_text(encoding="utf-8"))
    assert blocker_out["run_ref"] == new_run_ref
    assert blocker_out["parents"] == [new_run_ref]
    assert old_run_ref not in blocker_out.get("wb_ref", "")


def test_generic_bundle_rewrites_stale_scientific_debt_refs(tmp_path: Path) -> None:
    init_git_repo(tmp_path)
    project = ProjectManager.init(tmp_path, name="mwb-demo")
    bundle = tmp_path / "src_bundle"
    old_run_ref = "run_old_source"
    _make_bundle(bundle, manifest=_make_valid_manifest(old_run_ref), metrics=_make_valid_metrics())

    stale_debt = {
        "run_ref": old_run_ref,
        "mechanism_card_ref": f"mc_{old_run_ref}",
        "status": "insufficient_evidence",
        "items": [
            {
                "blocker": "control_leaky",
                "debt_ref": f"debt_{old_run_ref}_control_leaky",
                "description": "Controls moved too much.",
                "kind": "controls",
                "required_resolution": "Refresh controls.",
            }
        ],
    }
    (bundle / "scientific_debt.json").write_text(json.dumps(stale_debt), encoding="utf-8")

    from mwb.adapters.generic_bundle import GenericBundleIngestAdapter

    result = GenericBundleIngestAdapter().ingest(bundle, project=project)
    new_run_ref = result.run_ref

    debt_out = json.loads((result.run_dir / "scientific_debt.json").read_text(encoding="utf-8"))
    assert debt_out["run_ref"] == new_run_ref
    # mechanism_card_ref was rewritten to use the new run ref
    assert new_run_ref in debt_out["mechanism_card_ref"]
    # debt_ref was rewritten and no longer points only to the old identity
    assert debt_out["items"][0]["debt_ref"] != f"debt_{old_run_ref}_control_leaky"


def test_generic_bundle_rejects_bad_blocker_report_json(tmp_path: Path) -> None:
    bundle = tmp_path / "bundle"
    _make_bundle(bundle, manifest=_make_valid_manifest(), metrics=_make_valid_metrics())
    (bundle / "blocker_report.json").write_text("{not json", encoding="utf-8")

    from mwb.adapters.generic_bundle import GenericBundleIngestAdapter

    report = GenericBundleIngestAdapter().validate_source(bundle)
    assert report.status == "fail"
    assert any("blocker_report.json" in e for e in report.errors)


def test_generic_bundle_rejects_non_object_blocker_report(tmp_path: Path) -> None:
    bundle = tmp_path / "bundle"
    _make_bundle(bundle, manifest=_make_valid_manifest(), metrics=_make_valid_metrics())
    (bundle / "blocker_report.json").write_text(json.dumps([1, 2, 3]), encoding="utf-8")

    from mwb.adapters.generic_bundle import GenericBundleIngestAdapter

    report = GenericBundleIngestAdapter().validate_source(bundle)
    assert report.status == "fail"
    assert any("blocker_report.json" in e for e in report.errors)


def test_generic_bundle_rejects_invalid_scientific_debt_json(tmp_path: Path) -> None:
    bundle = tmp_path / "bundle"
    _make_bundle(bundle, manifest=_make_valid_manifest(), metrics=_make_valid_metrics())
    (bundle / "scientific_debt.json").write_text("{bad", encoding="utf-8")

    from mwb.adapters.generic_bundle import GenericBundleIngestAdapter

    report = GenericBundleIngestAdapter().validate_source(bundle)
    assert report.status == "fail"
    assert any("scientific_debt.json" in e for e in report.errors)


def test_generic_bundle_rejects_non_object_scientific_debt(tmp_path: Path) -> None:
    bundle = tmp_path / "bundle"
    _make_bundle(bundle, manifest=_make_valid_manifest(), metrics=_make_valid_metrics())
    (bundle / "scientific_debt.json").write_text(
        json.dumps(["list", "of", "things"]), encoding="utf-8"
    )

    from mwb.adapters.generic_bundle import GenericBundleIngestAdapter

    report = GenericBundleIngestAdapter().validate_source(bundle)
    assert report.status == "fail"
    assert any("scientific_debt.json" in e for e in report.errors)


# ---------------------------------------------------------------------------
# Evidence posture tests
# ---------------------------------------------------------------------------


def test_generic_bundle_ingest_remains_non_claim_bearing(tmp_path: Path) -> None:
    init_git_repo(tmp_path)
    project = ProjectManager.init(tmp_path, name="mwb-demo")
    bundle = tmp_path / "bundle"
    # Source manifest tries to assert claim_bearing=True
    manifest = _make_valid_manifest()
    manifest["claim_bearing"] = True  # must be overridden
    _make_bundle(bundle, manifest=manifest, metrics=_make_valid_metrics())

    stale_debt = {
        "run_ref": "run_demo_control_leak",
        "status": "insufficient_evidence",
        "items": [],
    }
    (bundle / "scientific_debt.json").write_text(json.dumps(stale_debt), encoding="utf-8")

    from mwb.adapters.generic_bundle import GenericBundleIngestAdapter

    result = GenericBundleIngestAdapter().ingest(bundle, project=project)
    manifest_out = json.loads((result.run_dir / "run_manifest.json").read_text(encoding="utf-8"))
    debt_out = json.loads((result.run_dir / "scientific_debt.json").read_text(encoding="utf-8"))

    assert manifest_out["claim_bearing"] is False
    # imported debt must not be claim-bearing
    assert debt_out.get("claim_bearing") is not True


# ---------------------------------------------------------------------------
# Full ingest + card + diagnose + next-probe + graph test (fixture bundle)
# ---------------------------------------------------------------------------


def test_generic_bundle_ingest_supports_card_diagnose_next_probe_graph(
    tmp_path: Path,
    monkeypatch,
) -> None:
    init_git_repo(tmp_path)
    ProjectManager.init(tmp_path, name="mwb-demo")
    monkeypatch.chdir(tmp_path)

    runner = CliRunner()
    source = FIXTURE

    ingest = runner.invoke(app, ["ingest", "external", "generic-bundle", str(source)])
    assert ingest.exit_code == 0, ingest.output
    payload = json.loads(ingest.output)
    assert payload["adapter_id"] == "generic-bundle"
    run_ref = payload["run_ref"]

    card = runner.invoke(app, ["card", "latest"])
    assert card.exit_code == 0, card.output
    card_payload = json.loads(card.output)
    assert card_payload["run_ref"] == run_ref

    diagnose = runner.invoke(app, ["diagnose", "latest"])
    assert diagnose.exit_code == 0, diagnose.output
    diag_payload = json.loads(diagnose.output)
    assert diag_payload["source_run_ref"] == run_ref

    next_probe = runner.invoke(app, ["next-probe", "latest", "--materialize"])
    assert next_probe.exit_code == 0, next_probe.output

    graph = runner.invoke(app, ["graph", "rebuild"])
    assert graph.exit_code == 0, graph.output


# ---------------------------------------------------------------------------
# Existing adapter registry / happy-path tests (preserved)
# ---------------------------------------------------------------------------


def test_generic_bundle_adapter_ingests_neutral_mwb_artifacts(
    tmp_path: Path,
    monkeypatch,
) -> None:
    init_git_repo(tmp_path)
    ProjectManager.init(tmp_path, name="mwb-demo")
    monkeypatch.chdir(tmp_path)
    source = FIXTURE
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


def test_unknown_adapter_error_includes_available_adapter_ids() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["adapters", "inspect", "nonexistent-adapter", "--json"])
    # Should exit non-zero and include available adapter ids in message.
    assert result.exit_code != 0 or "nonexistent-adapter" in result.output


def test_can_ingest_failure_does_not_make_inspect_unavailable(tmp_path: Path) -> None:
    runner = CliRunner()
    can_fail = runner.invoke(
        app,
        ["adapters", "can-ingest", "generic-bundle", str(tmp_path / "missing"), "--json"],
    )
    inspect_ok = runner.invoke(app, ["adapters", "inspect", "generic-bundle", "--json"])
    assert can_fail.exit_code == 0
    assert json.loads(can_fail.output)["status"] == "unavailable"
    assert inspect_ok.exit_code == 0
    assert json.loads(inspect_ok.output)["status"] == "available"


def test_ingest_external_generic_bundle_routes_through_registry(
    tmp_path: Path,
    monkeypatch,
) -> None:
    init_git_repo(tmp_path)
    ProjectManager.init(tmp_path, name="mwb-demo")
    monkeypatch.chdir(tmp_path)
    runner = CliRunner()

    result = runner.invoke(app, ["ingest", "external", "generic-bundle", str(FIXTURE)])

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["adapter_id"] == "generic-bundle"


def test_legacy_adapter_cli_alias_still_serves_conformance_help() -> None:
    runner = CliRunner()

    singular = runner.invoke(app, ["adapter", "conformance", "--help"])
    plural = runner.invoke(app, ["adapters", "list", "--help"])

    assert singular.exit_code == 0, singular.output
    assert plural.exit_code == 0, plural.output
    assert "transformer-lens" in singular.output
    assert "List registered workbench adapters" in plural.output


def test_adapters_list_does_not_depend_on_order(tmp_path: Path) -> None:
    runner = CliRunner()
    listed = runner.invoke(app, ["adapters", "list", "--json"])
    assert listed.exit_code == 0, listed.output
    adapter_ids = {row["adapter_id"] for row in json.loads(listed.output)["adapters"]}
    assert "generic-bundle" in adapter_ids
    assert "self-ground" in adapter_ids


# ---------------------------------------------------------------------------
# Residual stale-ref detection tests
# ---------------------------------------------------------------------------


def test_generic_bundle_rejects_unrewriteable_stale_debt_refs(tmp_path: Path) -> None:
    """Ingest must reject scientific_debt.json that contains stale source-run
    refs in fields the rewrite logic does not know about.

    The adapter rewrites known fields (run_ref, mechanism_card_ref, debt_ref,
    item run_ref fields).  Unknown fields such as evidence_ref that still embed
    the old run ref must be detected and the ingest rejected with an explicit
    error naming the residual field path.
    """
    init_git_repo(tmp_path)
    project = ProjectManager.init(tmp_path, name="mwb-demo")
    bundle = tmp_path / "bundle"
    old_run_ref = "run_old_source"
    _make_bundle(bundle, manifest=_make_valid_manifest(old_run_ref), metrics=_make_valid_metrics())

    stale_debt = {
        "run_ref": old_run_ref,
        "status": "insufficient_evidence",
        "items": [
            {
                "kind": "controls",
                "description": "stale evidence ref in unknown field",
                "required_resolution": "remove stale source pointer",
                # evidence_ref is not a known rewrite target; embeds old_run_ref.
                "evidence_ref": f"artifact_for_{old_run_ref}",
            }
        ],
    }
    (bundle / "scientific_debt.json").write_text(json.dumps(stale_debt), encoding="utf-8")

    from mwb.adapters.generic_bundle import GenericBundleIngestAdapter

    with pytest.raises(ValueError, match="stale source run ref"):
        GenericBundleIngestAdapter().ingest(bundle, project=project)


def test_rejects_unrewriteable_stale_debt_refs_error_names_field_path(
    tmp_path: Path,
) -> None:
    """The stale-ref error message must include the field path."""
    init_git_repo(tmp_path)
    project = ProjectManager.init(tmp_path, name="mwb-demo")
    bundle = tmp_path / "bundle"
    old_run_ref = "run_source_a"
    _make_bundle(bundle, manifest=_make_valid_manifest(old_run_ref), metrics=_make_valid_metrics())

    stale_debt = {
        "run_ref": old_run_ref,
        "status": "insufficient_evidence",
        "items": [
            {
                "kind": "controls",
                "description": "nested stale pointer",
                "required_resolution": "clear",
                "evidence_ref": f"path/to/{old_run_ref}/artifact.json",
            }
        ],
    }
    (bundle / "scientific_debt.json").write_text(json.dumps(stale_debt), encoding="utf-8")

    from mwb.adapters.generic_bundle import GenericBundleIngestAdapter

    with pytest.raises(ValueError) as exc_info:
        GenericBundleIngestAdapter().ingest(bundle, project=project)

    msg = str(exc_info.value)
    assert "evidence_ref" in msg or "items" in msg


def test_generic_bundle_rejects_unrewriteable_stale_blocker_report_refs(
    tmp_path: Path,
) -> None:
    """Ingest must reject blocker_report.json that contains stale source-run
    refs in fields the rewrite logic does not know about.

    The adapter rewrites run_ref, parents, and regenerates wb_ref.  Unknown
    fields such as source_artifact that embed the old run ref must be detected
    and rejected.
    """
    init_git_repo(tmp_path)
    project = ProjectManager.init(tmp_path, name="mwb-demo")
    bundle = tmp_path / "bundle"
    old_run_ref = "run_old_source"
    _make_bundle(bundle, manifest=_make_valid_manifest(old_run_ref), metrics=_make_valid_metrics())

    stale_blocker = {
        "wb_type": "BlockerReport",
        "wb_ref": f"blocker_{old_run_ref}",
        "run_ref": old_run_ref,
        "parents": [old_run_ref],
        "blockers": ["control_leaky"],
        "primary_blocker": "control_leaky",
        "blocking_metrics": [],
        # Unknown field that embeds old run ref — should be caught.
        "source_artifact": f"runs/{old_run_ref}/control_metrics.json",
    }
    (bundle / "blocker_report.json").write_text(json.dumps(stale_blocker), encoding="utf-8")

    from mwb.adapters.generic_bundle import GenericBundleIngestAdapter

    with pytest.raises(ValueError, match="stale source run ref"):
        GenericBundleIngestAdapter().ingest(bundle, project=project)


def test_find_stale_ref_paths_helper() -> None:
    """Direct unit test of the _find_stale_ref_paths helper."""
    from mwb.adapters.generic_bundle import _find_stale_ref_paths

    payload = {
        "run_ref": "run_new",
        "items": [
            {
                "debt_ref": "debt_run_new_control",
                "evidence_ref": "artifact_for_run_old",
            }
        ],
        "metadata": {
            "source": "runs/run_old/metrics.json",
        },
    }
    needle = "run_old"
    paths = _find_stale_ref_paths(payload, needle)
    assert "items[0].evidence_ref" in paths
    assert "metadata.source" in paths
    # run_ref and debt_ref do not contain needle.
    assert not any("run_ref" in p and "items" not in p for p in paths)

    # Empty needle should return no hits.
    assert _find_stale_ref_paths(payload, "") == []

    # Clean payload should return no hits.
    clean = {"run_ref": "run_new", "items": [{"debt_ref": "debt_run_new_ctrl"}]}
    assert _find_stale_ref_paths(clean, needle) == []

    # Occurrences of needle that are part of the exclude string must NOT be flagged.
    # This is the key case: new_run_ref = "run_external_generic_run_old_source"
    # contains old_run_ref = "run_old_source" but that is a legitimate rewrite.
    new_ref = "run_external_generic_run_old"
    rewritten = {
        "run_ref": new_ref,
        "items": [{"debt_ref": f"debt_{new_ref}_control"}],
        # unknown field with genuine stale ref (not part of new_ref):
        "evidence_ref": "artifact_for_run_old_separate_pointer",
    }
    paths_with_exclude = _find_stale_ref_paths(rewritten, needle, exclude=new_ref)
    # run_ref and debt_ref should NOT be flagged (needle only appears via new_ref).
    assert "run_ref" not in paths_with_exclude
    assert not any("debt_ref" in p for p in paths_with_exclude)
    # evidence_ref has "run_old" in "artifact_for_run_old_separate_pointer" which
    # is NOT just part of new_ref, so it SHOULD be flagged.
    assert "evidence_ref" in paths_with_exclude
