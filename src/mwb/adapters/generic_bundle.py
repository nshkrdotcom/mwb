from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any

from mwb.adapters.base import AdapterCapabilityReport, ArtifactValidationReport, IngestResult
from mwb.domain.objects import BlockerReport
from mwb.project import Project
from mwb.refs import slugify, stable_ref
from mwb.time import utc_now
from mwb.workflows.blockers import diagnose_blockers
from mwb.workflows.cards import card_from_run, write_card
from mwb.workflows.next_probe import build_next_probe, load_next_probe_payload, write_next_probe


class GenericBundleIngestAdapter:
    adapter_id = "generic-bundle"
    display_name = "Generic MWB Artifact Bundle"
    modes = ["ingest"]
    claim_bearing = False
    notes = [
        "Imports an existing MWB-shaped run artifact bundle",
        "Useful for tests, examples, and external tools that already emit MWB contracts",
    ]

    def can_ingest(self, source: Path) -> AdapterCapabilityReport:
        errors = _source_errors(source)
        return AdapterCapabilityReport(
            adapter_id=self.adapter_id,
            display_name=self.display_name,
            status="available" if not errors else "unavailable",
            modes=list(self.modes),
            claim_bearing=self.claim_bearing,
            notes=list(self.notes),
            errors=errors,
        )

    def validate_source(self, source: Path) -> ArtifactValidationReport:
        artifacts: dict[str, dict[str, Any]] = {}
        errors = _source_errors(source)
        for name in ["run_manifest.json", "control_metrics.json"]:
            path = source / name
            if not path.exists():
                artifacts[name] = {"status": "missing"}
                continue
            try:
                payload = _read_json(path)
            except json.JSONDecodeError as exc:
                artifacts[name] = {"status": "invalid_json", "error": str(exc)}
                errors.append(f"{name}: invalid_json")
                continue
            artifacts[name] = {
                "status": "present" if isinstance(payload, dict) else "invalid_payload",
                "path": str(path),
            }
            if not isinstance(payload, dict):
                errors.append(f"{name}: invalid_payload")
        return ArtifactValidationReport(
            adapter_id=self.adapter_id,
            status="pass" if not errors else "fail",
            artifacts=artifacts,
            errors=errors,
        )

    def ingest(self, source: Path, *, project: Project) -> IngestResult:
        source = source.resolve()
        validation = self.validate_source(source)
        if validation.status != "pass":
            raise ValueError(
                f"generic MWB artifact bundle is incomplete: {', '.join(validation.errors)}"
            )

        manifest = dict(_read_json(source / "run_manifest.json"))
        metrics = dict(_read_json(source / "control_metrics.json"))
        source_ref = str(manifest.get("run_ref") or source.name)
        run_ref = f"run_external_generic_{slugify(source_ref)}"
        run_dir = project.mechanism_dir / "runs" / run_ref
        run_dir.mkdir(parents=True, exist_ok=True)

        manifest.update(
            {
                "run_ref": run_ref,
                "source_kind": "external_adapter_ingest",
                "adapter_id": self.adapter_id,
                "adapter_display_name": self.display_name,
                "source_path": str(source),
                "ingested_at": utc_now(),
                "claim_bearing": False,
            }
        )
        manifest.setdefault("status", "insufficient_evidence")
        manifest.setdefault("evidence_posture", "diagnostic_insufficient")
        manifest.setdefault("source_artifacts", validation.artifacts)

        _write_json(run_dir / "run_manifest.json", manifest)
        _write_json(run_dir / "control_metrics.json", metrics)
        if (source / "blocker_report.json").exists():
            blocker_report = _rewrite_blocker_report(source / "blocker_report.json", run_ref)
            _write_json(run_dir / "blocker_report.json", blocker_report)
        else:
            blocker_report = _derived_blocker_report(run_ref, metrics)
            _write_json(run_dir / "blocker_report.json", blocker_report)

        for name in ["scientific_debt.json"]:
            if (source / name).exists():
                shutil.copyfile(source / name, run_dir / name)

        plan = build_next_probe(load_next_probe_payload(run_dir))
        write_next_probe(run_dir, plan)
        write_card(run_dir, card_from_run(run_dir), mechanism_dir=project.mechanism_dir)

        return IngestResult(
            adapter_id=self.adapter_id,
            display_name=self.display_name,
            run_ref=run_ref,
            run_dir=run_dir,
            status=str(manifest["status"]),
            primary_blocker=str(blocker_report.get("primary_blocker") or "") or None,
            validation=validation,
        )


def _source_errors(source: Path) -> list[str]:
    if not source.exists():
        return [f"source does not exist: {source}"]
    if not source.is_dir():
        return [f"source is not a directory: {source}"]
    required = ["run_manifest.json", "control_metrics.json"]
    return [
        f"missing required artifact: {name}"
        for name in required
        if not (source / name).exists()
    ]


def _derived_blocker_report(run_ref: str, metrics: dict[str, Any]) -> dict[str, Any]:
    blockers = diagnose_blockers(metrics, thresholds={"control_leaky_ratio": 0.8})
    report = BlockerReport(
        wb_ref=stable_ref("blocker", run_ref, blockers),
        run_ref=run_ref,
        blockers=list(blockers["blockers"]),
        primary_blocker=blockers["primary_blocker"],
        blocking_metrics=list(blockers["blocking_metrics"]),
        parents=[run_ref],
    )
    return report.model_dump(mode="json")


def _rewrite_blocker_report(path: Path, run_ref: str) -> dict[str, Any]:
    payload = _read_json(path)
    payload["run_ref"] = run_ref
    payload["parents"] = [run_ref]
    payload.setdefault("wb_type", "BlockerReport")
    payload.setdefault("wb_ref", stable_ref("blocker", run_ref, payload))
    return payload


def _read_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"expected object JSON: {path}")
    return payload


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
