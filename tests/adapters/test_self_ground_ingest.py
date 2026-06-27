import json
import subprocess
from pathlib import Path

from typer.testing import CliRunner

from mwb.adapters.self_ground import ingest_self_ground_run, validate_self_ground_artifacts
from mwb.cli import app
from mwb.project import ProjectManager
from mwb.workflows.draft_guard import check_draft_text


def init_git_repo(path: Path) -> None:
    subprocess.run(["git", "init", "-b", "main"], cwd=path, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "test@example.local"], cwd=path, check=True)
    subprocess.run(["git", "config", "user.name", "Test User"], cwd=path, check=True)
    (path / "README.md").write_text("# repo\n")
    subprocess.run(["git", "add", "README.md"], cwd=path, check=True)
    subprocess.run(["git", "commit", "-m", "initial"], cwd=path, check=True, capture_output=True)


def write_e004_artifact(path: Path) -> None:
    comparison = path / "comparison"
    forensics = path / "forensics"
    comparison.mkdir(parents=True)
    forensics.mkdir()
    row = {
        "layer": "blocks.2.hook_resid_post",
        "sae_release": "pythia-70m-deduped-res-sm",
        "sae_id": "blocks.2.hook_resid_post",
        "feature_selection_mode": "ensemble-specificity",
        "operation": "ablate,amplify",
        "control_suite": "multi_control",
        "run_status": "completed",
        "claim_status": "insufficient_evidence",
        "valid_tasks": 69,
        "behavioral_rows": 5520,
        "skipped_rows": 0,
        "baseline_pass_rate": 1.0,
        "top_target_delta": 0.9,
        "top_control_delta": 0.82,
        "specificity_gap": 0.08,
        "top_vs_control_ratio": 1.09,
        "density_control_gap": 0.0,
        "multi_control_min_gap": -0.01,
        "family_min_specificity_gap": -0.04,
        "passes_all_controls": False,
        "limitations": "Multi-control evidence failed.",
        "artifact_paths": "runs/e004_specificity_rescue_matrix/eval/block2",
    }
    (path / "capability.json").write_text(
        json.dumps({"cuda_available": False, "torch_version": "2.12.1+cpu"}) + "\n",
        encoding="utf-8",
    )
    (path / "matrix_run_summary.json").write_text(
        json.dumps(
            {
                "status": "completed",
                "attempted_cells": 1,
                "completed_cells": 1,
                "blocked_cells": 0,
                "layers": ["blocks.2.hook_resid_post"],
                "feature_selection_modes": ["ensemble-specificity"],
                "operations": ["ablate,amplify"],
                "control_suite": "multi_control",
            }
        )
        + "\n",
        encoding="utf-8",
    )
    (comparison / "comparison.json").write_text(
        json.dumps(
            {
                "attempted_cells": 1,
                "completed_cells": 1,
                "blocked_cells": 0,
                "candidate_cells": 0,
                "interpretation": "current_sae_model_layer_search_insufficient",
                "best_run": row,
            }
        )
        + "\n",
        encoding="utf-8",
    )
    (comparison / "matrix_summary.json").write_text(json.dumps([row]) + "\n", encoding="utf-8")
    (comparison / "matrix_summary.csv").write_text(
        ",".join(row.keys())
        + "\n"
        + ",".join(str(value) for value in row.values())
        + "\n",
        encoding="utf-8",
    )
    for name in ["best_runs_by_family.csv", "best_runs_by_specificity.csv", "blocked_runs.csv"]:
        (comparison / name).write_text(
            ",".join(row.keys())
            + "\n"
            + ",".join(str(value) for value in row.values())
            + "\n",
            encoding="utf-8",
        )
    (comparison / "claim_adjudication.md").write_text(
        "# E004 Claim Adjudication\n\n"
        "- interpretation: `current_sae_model_layer_search_insufficient`\n\n"
        "Broad negation mechanism discovery is not supported.\n",
        encoding="utf-8",
    )
    for name, header, line in [
        (
            "control_suite_breakdown.csv",
            (
                "control_suite,n_rows,n_tasks,target_delta_mean,control_delta_mean,"
                "specificity_gap_mean,control_dominant_rows"
            ),
            "multi_control,10,5,0.9,0.82,0.08,3",
        ),
        (
            "family_breakdown.csv",
            (
                "family,n_rows,n_tasks,target_delta_mean,control_delta_mean,"
                "specificity_gap_mean,control_dominant_rows"
            ),
            "negation_removed,10,5,0.9,0.82,0.08,3",
        ),
        (
            "feature_breakdown.csv",
            (
                "feature_set,n_rows,n_tasks,target_delta_mean,control_delta_mean,"
                "specificity_gap_mean,control_dominant_rows"
            ),
            "top,10,5,0.9,0.82,0.08,3",
        ),
        (
            "task_outlier_table.csv",
            (
                "run_name,task_id,family,template_id,token_pair,feature_set_label,"
                "control_suite,target_absolute_delta,control_absolute_delta,specificity_gap"
            ),
            "run,task,negation_removed,tpl,no/not,top,multi_control,0.9,0.82,0.08",
        ),
        (
            "template_breakdown.csv",
            (
                "template,n_rows,n_tasks,target_delta_mean,control_delta_mean,"
                "specificity_gap_mean,control_dominant_rows"
            ),
            "tpl,10,5,0.9,0.82,0.08,3",
        ),
        (
            "token_pair_breakdown.csv",
            (
                "token_pair,n_rows,n_tasks,target_delta_mean,control_delta_mean,"
                "specificity_gap_mean,control_dominant_rows"
            ),
            "no/not,10,5,0.9,0.82,0.08,3",
        ),
    ]:
        (forensics / name).write_text(f"{header}\n{line}\n", encoding="utf-8")
    (forensics / "forensics_summary.md").write_text("# Forensics\n", encoding="utf-8")


def test_self_ground_ingest_writes_workbench_run_artifacts(tmp_path: Path) -> None:
    init_git_repo(tmp_path)
    project = ProjectManager.init(tmp_path, name="mwb-demo")
    source = tmp_path / "e004_specificity_rescue_matrix"
    write_e004_artifact(source)

    run_dir = ingest_self_ground_run(source, project=project)

    assert run_dir == (
        project.mechanism_dir / "runs" / "run_adapter_self_ground_e004_specificity_rescue_matrix"
    )
    manifest = json.loads((run_dir / "run_manifest.json").read_text())
    metrics = json.loads((run_dir / "control_metrics.json").read_text())
    blockers = json.loads((run_dir / "blocker_report.json").read_text())
    next_probe = json.loads((run_dir / "next_probe.json").read_text())
    card = json.loads((run_dir / "mechanism_card.json").read_text())

    assert manifest["source_kind"] == "external_adapter_ingest"
    assert manifest["adapter_id"] == "self-ground"
    assert manifest["adapter_source_kind"] == "self_ground_e004"
    assert manifest["status"] == "insufficient_evidence"
    assert manifest["tried_axes"]["layers"] == ["blocks.2.hook_resid_post"]
    assert manifest["source_artifacts"]["comparison/matrix_summary.csv"]["status"] == "present"
    assert metrics["target_delta"] == 0.9
    assert metrics["matched_control_delta"] == 0.82
    assert metrics["family_min_gap"] == -0.04
    assert metrics["multi_control_min_gap"] == -0.01
    assert blockers["primary_blocker"] == "control_leaky"
    assert next_probe["diagnosis"]["primary"] == "control_leaky"
    assert "mechanism for" in card["blocked_language"]


def test_self_ground_validation_requires_comparison_and_forensics_csvs(tmp_path: Path) -> None:
    source = tmp_path / "e004_specificity_rescue_matrix"
    write_e004_artifact(source)

    statuses = validate_self_ground_artifacts(source)

    assert statuses["comparison/best_runs_by_family.csv"]["status"] == "present"
    assert statuses["comparison/best_runs_by_specificity.csv"]["row_count"] == 1
    assert statuses["forensics/control_suite_breakdown.csv"]["status"] == "present"
    assert statuses["forensics/task_outlier_table.csv"]["row_count"] == 1


def test_self_ground_ingest_cli_and_latest_resolution(tmp_path: Path, monkeypatch) -> None:
    init_git_repo(tmp_path)
    monkeypatch.chdir(tmp_path)
    ProjectManager.init(tmp_path, name="mwb-demo")
    source = tmp_path / "e004_specificity_rescue_matrix"
    write_e004_artifact(source)
    runner = CliRunner()

    ingest = runner.invoke(app, ["ingest", "self-ground", str(source)])
    next_probe = runner.invoke(app, ["next-probe", "latest"])
    card = runner.invoke(app, ["card", "latest"])

    assert ingest.exit_code == 0, ingest.output
    assert next_probe.exit_code == 0, next_probe.output
    assert card.exit_code == 0, card.output
    ingest_payload = json.loads(ingest.output)
    assert ingest_payload["run_ref"] == "run_adapter_self_ground_e004_specificity_rescue_matrix"
    assert json.loads(next_probe.output)["diagnosis"]["primary"] == "control_leaky"
    assert json.loads(card.output)["run_ref"] == (
        "run_adapter_self_ground_e004_specificity_rescue_matrix"
    )


def test_generic_ingest_dispatcher_routes_to_self_ground_adapter(
    tmp_path: Path, monkeypatch
) -> None:
    init_git_repo(tmp_path)
    monkeypatch.chdir(tmp_path)
    ProjectManager.init(tmp_path, name="mwb-demo")
    source = tmp_path / "e004_specificity_rescue_matrix"
    write_e004_artifact(source)
    runner = CliRunner()

    result = runner.invoke(app, ["ingest", "external", "self-ground", str(source)])

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["adapter_id"] == "self-ground"
    assert payload["run_ref"] == "run_adapter_self_ground_e004_specificity_rescue_matrix"


def test_adapter_registry_cli_exposes_self_ground_as_optional_dogfood() -> None:
    runner = CliRunner()

    listed = runner.invoke(app, ["adapters", "list", "--json"])
    inspected = runner.invoke(app, ["adapters", "inspect", "self-ground", "--json"])

    assert listed.exit_code == 0, listed.output
    assert inspected.exit_code == 0, inspected.output
    list_payload = json.loads(listed.output)
    inspect_payload = json.loads(inspected.output)
    assert list_payload["adapters"][0]["adapter_id"] == "self-ground"
    assert inspect_payload["adapter_id"] == "self-ground"
    assert inspect_payload["claim_bearing"] is False
    assert "Optional dogfood adapter" in inspect_payload["notes"]


def test_draft_guard_ignores_blocked_terms_inside_claim_marker() -> None:
    report = check_draft_text(
        (
            "The feature family is associated with inspected negation examples. "
            "[CLAIM:claim_run_self_ground_e004_specificity_rescue_matrix]"
        ),
        {
            "claim_run_self_ground_e004_specificity_rescue_matrix": {
                "blocked_language": ["specificity", "implements"],
                "allowed_language": ["is associated with"],
            }
        },
    )

    assert report["status"] == "allowed"
