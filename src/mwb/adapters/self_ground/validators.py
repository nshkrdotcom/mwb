from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from mwb.adapters.base import ArtifactValidationReport

ADAPTER_ID = "self-ground"
DISPLAY_NAME = "SELF-GROUND"

SUMMARY_COLUMNS = [
    "layer",
    "feature_selection_mode",
    "claim_status",
    "top_target_delta",
    "top_control_delta",
    "specificity_gap",
    "family_min_specificity_gap",
    "multi_control_min_gap",
]
FORENSICS_BREAKDOWN_COLUMNS = [
    "n_rows",
    "n_tasks",
    "target_delta_mean",
    "control_delta_mean",
    "specificity_gap_mean",
    "control_dominant_rows",
]

REQUIRED_ARTIFACTS = {
    "capability.json": [],
    "matrix_run_summary.json": [
        "status",
        "attempted_cells",
        "completed_cells",
        "layers",
        "feature_selection_modes",
        "operations",
        "control_suite",
    ],
    "comparison/comparison.json": ["best_run", "interpretation"],
    "comparison/matrix_summary.json": SUMMARY_COLUMNS,
    "comparison/matrix_summary.csv": SUMMARY_COLUMNS,
    "comparison/best_runs_by_family.csv": SUMMARY_COLUMNS,
    "comparison/best_runs_by_specificity.csv": SUMMARY_COLUMNS,
    "comparison/blocked_runs.csv": SUMMARY_COLUMNS,
    "comparison/claim_adjudication.md": [],
    "forensics/control_suite_breakdown.csv": ["control_suite", *FORENSICS_BREAKDOWN_COLUMNS],
    "forensics/family_breakdown.csv": ["family", *FORENSICS_BREAKDOWN_COLUMNS],
    "forensics/feature_breakdown.csv": ["feature_set", *FORENSICS_BREAKDOWN_COLUMNS],
    "forensics/task_outlier_table.csv": [
        "run_name",
        "task_id",
        "family",
        "template_id",
        "token_pair",
        "feature_set_label",
        "control_suite",
        "target_absolute_delta",
        "control_absolute_delta",
        "specificity_gap",
    ],
    "forensics/template_breakdown.csv": ["template", *FORENSICS_BREAKDOWN_COLUMNS],
    "forensics/token_pair_breakdown.csv": ["token_pair", *FORENSICS_BREAKDOWN_COLUMNS],
    "forensics/forensics_summary.md": [],
}


def validate_self_ground_artifacts(source: Path) -> dict[str, dict[str, Any]]:
    statuses: dict[str, dict[str, Any]] = {}
    for relative, required_columns in REQUIRED_ARTIFACTS.items():
        path = source / relative
        if not path.exists():
            statuses[relative] = {"status": "missing", "required_columns": required_columns}
            continue
        status: dict[str, Any] = {
            "status": "present",
            "path": str(path),
            "required_columns": required_columns,
        }
        if required_columns:
            observed, row_count = _observed_fields(path)
            missing = [column for column in required_columns if column not in observed]
            status["observed_columns"] = sorted(observed)
            status["missing_columns"] = missing
            status["row_count"] = row_count
            if missing:
                status["status"] = "missing_columns"
        elif path.suffix in {".csv", ".json"}:
            _observed, row_count = _observed_fields(path)
            status["row_count"] = row_count
        statuses[relative] = status
    return statuses


def validation_report(source: Path) -> ArtifactValidationReport:
    artifacts = validate_self_ground_artifacts(source)
    errors = [
        f"{name}: {status['status']}"
        for name, status in artifacts.items()
        if status["status"] != "present"
    ]
    return ArtifactValidationReport(
        adapter_id=ADAPTER_ID,
        status="pass" if not errors else "fail",
        artifacts=artifacts,
        errors=errors,
    )


def _observed_fields(path: Path) -> tuple[set[str], int | None]:
    if path.suffix == ".csv":
        with path.open(newline="", encoding="utf-8") as handle:
            reader = csv.DictReader(handle)
            row_count = sum(1 for _row in reader)
            return {str(name) for name in reader.fieldnames or []}, row_count
    payload = _read_json(path)
    if isinstance(payload, list):
        fields: set[str] = set()
        for row in payload:
            if isinstance(row, dict):
                fields.update(str(key) for key in row)
        return fields, len(payload)
    if isinstance(payload, dict):
        fields = {str(key) for key in payload}
        best_run = payload.get("best_run")
        if isinstance(best_run, dict):
            fields.update(str(key) for key in best_run)
        return fields, 1
    return set(), None


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))
