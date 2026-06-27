from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from mwb.adapters.base import AdapterCapabilityReport, ArtifactValidationReport, IngestResult
from mwb.adapters.self_ground.mapper import map_run_artifacts
from mwb.adapters.self_ground.validators import (
    ADAPTER_ID,
    DISPLAY_NAME,
    REQUIRED_ARTIFACTS,
    validate_self_ground_artifacts,
    validation_report,
)
from mwb.domain.objects import BlockerReport
from mwb.project import Project, ProjectManager
from mwb.refs import stable_ref
from mwb.workflows.blockers import diagnose_blockers
from mwb.workflows.cards import card_from_run, write_card
from mwb.workflows.next_probe import build_next_probe, write_next_probe


class SelfGroundIngestAdapter:
    adapter_id = ADAPTER_ID
    display_name = DISPLAY_NAME

    def can_ingest(self, source: Path) -> AdapterCapabilityReport:
        if not source.exists():
            return AdapterCapabilityReport(
                adapter_id=self.adapter_id,
                display_name=self.display_name,
                status="unavailable",
                modes=["ingest"],
                claim_bearing=False,
                notes=["Optional dogfood adapter", "Does not define MWB core ontology"],
                errors=[f"source does not exist: {source}"],
            )
        if not source.is_dir():
            return AdapterCapabilityReport(
                adapter_id=self.adapter_id,
                display_name=self.display_name,
                status="unavailable",
                modes=["ingest"],
                claim_bearing=False,
                notes=["Optional dogfood adapter", "Does not define MWB core ontology"],
                errors=[f"source is not a directory: {source}"],
            )
        expected = ["capability.json", "matrix_run_summary.json", "comparison/comparison.json"]
        missing = [relative for relative in expected if not (source / relative).exists()]
        return AdapterCapabilityReport(
            adapter_id=self.adapter_id,
            display_name=self.display_name,
            status="available" if not missing else "unavailable",
            modes=["ingest"],
            claim_bearing=False,
            notes=["Optional dogfood adapter", "Does not define MWB core ontology"],
            errors=[f"missing recognizable source artifact: {item}" for item in missing],
        )

    def validate_source(self, source: Path) -> ArtifactValidationReport:
        return validation_report(source)

    def ingest(self, source: Path, *, project: Project) -> IngestResult:
        source = source.resolve()
        if not source.is_dir():
            raise FileNotFoundError(f"{self.display_name} run directory not found: {source}")

        validation = self.validate_source(source)
        if validation.status != "pass":
            raise ValueError(
                f"{self.display_name} artifact set is incomplete: {', '.join(validation.errors)}"
            )

        mapped = map_run_artifacts(source, validation=validation)
        manifest = mapped["run_manifest"]
        metrics = mapped["control_metrics"]
        run_ref = str(manifest["run_ref"])
        run_dir = project.mechanism_dir / "runs" / run_ref
        run_dir.mkdir(parents=True, exist_ok=True)

        blockers = diagnose_blockers(metrics, thresholds={"control_leaky_ratio": 0.8})
        _write_json(run_dir / "run_manifest.json", manifest)
        _write_json(run_dir / "control_metrics.json", metrics)
        _write_blocker_report(run_dir, run_ref, blockers)
        plan = build_next_probe(
            {
                "run_ref": run_ref,
                "status": manifest["status"],
                "metrics": metrics,
                "blockers": blockers["blockers"],
                "tried_axes": manifest["tried_axes"],
                "available_axes": manifest["available_axes"],
                "backend_capabilities": manifest["backend_capabilities"],
            }
        )
        write_next_probe(run_dir, plan)
        card = card_from_run(run_dir)
        write_card(run_dir, card, mechanism_dir=project.mechanism_dir)
        return IngestResult(
            adapter_id=self.adapter_id,
            display_name=self.display_name,
            run_ref=run_ref,
            run_dir=run_dir,
            status=str(manifest["status"]),
            primary_blocker=blockers.get("primary_blocker"),
            validation=validation,
        )


def ingest_self_ground_run(source: Path, *, project: Project | None = None) -> Path:
    project = project or ProjectManager.discover_or_create()
    return SelfGroundIngestAdapter().ingest(source, project=project).run_dir


def _write_blocker_report(
    run_dir: Path, run_ref: str, blockers: dict[str, Any]
) -> BlockerReport:
    report = BlockerReport(
        wb_ref=stable_ref("blocker", run_ref, blockers),
        run_ref=run_ref,
        blockers=list(blockers["blockers"]),
        primary_blocker=blockers["primary_blocker"],
        blocking_metrics=list(blockers["blocking_metrics"]),
        parents=[run_ref],
    )
    _write_json(run_dir / "blocker_report.json", report.model_dump(mode="json"))
    return report


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


__all__ = [
    "REQUIRED_ARTIFACTS",
    "SelfGroundIngestAdapter",
    "ingest_self_ground_run",
    "validate_self_ground_artifacts",
]
