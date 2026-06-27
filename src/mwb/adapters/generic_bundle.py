from __future__ import annotations

import json
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

# Required fields for control_metrics.json — blocker derivation uses these.
_REQUIRED_CONTROL_METRICS = ["target_delta", "matched_control_delta"]


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

        # --- run_manifest.json (required) ---
        manifest_path = source / "run_manifest.json"
        if not manifest_path.exists():
            artifacts["run_manifest.json"] = {"status": "missing"}
            errors.append("run_manifest.json: missing required artifact")
        else:
            manifest_errors, manifest_info = _validate_run_manifest(manifest_path)
            artifacts["run_manifest.json"] = manifest_info
            errors.extend(manifest_errors)

        # --- control_metrics.json (required) ---
        metrics_path = source / "control_metrics.json"
        if not metrics_path.exists():
            artifacts["control_metrics.json"] = {"status": "missing"}
            errors.append("control_metrics.json: missing required artifact")
        else:
            metrics_errors, metrics_info = _validate_control_metrics(metrics_path)
            artifacts["control_metrics.json"] = metrics_info
            errors.extend(metrics_errors)

        # --- optional artifacts ---
        for name in ["blocker_report.json", "scientific_debt.json", "mechanism_card.json"]:
            opt_path = source / name
            if not opt_path.exists():
                continue
            opt_errors, opt_info = _validate_optional_artifact(opt_path, name)
            artifacts[name] = opt_info
            errors.extend(opt_errors)

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

        # run_ref is required — validated above, so this is safe.
        source_ref = str(manifest["run_ref"])
        run_ref = f"run_external_generic_{slugify(source_ref)}"
        run_dir = project.mechanism_dir / "runs" / run_ref
        run_dir.mkdir(parents=True, exist_ok=True)

        # Force adapter provenance; do not preserve claim_bearing from source.
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

        # blocker_report.json — rewrite if present, derive if absent.
        if (source / "blocker_report.json").exists():
            old_source_ref = _original_run_ref(source / "run_manifest.json")
            blocker_report = _rewrite_blocker_report(
                source / "blocker_report.json",
                run_ref=run_ref,
                old_run_ref=old_source_ref,
            )
            _write_json(run_dir / "blocker_report.json", blocker_report)
        else:
            blocker_report = _derived_blocker_report(run_ref, metrics)
            _write_json(run_dir / "blocker_report.json", blocker_report)

        # scientific_debt.json — rewrite if present; do not copy unchanged.
        if (source / "scientific_debt.json").exists():
            old_source_ref = _original_run_ref(source / "run_manifest.json")
            debt = _rewrite_scientific_debt(
                source / "scientific_debt.json",
                old_run_ref=old_source_ref,
                new_run_ref=run_ref,
            )
            _write_json(run_dir / "scientific_debt.json", debt)

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


# ---------------------------------------------------------------------------
# Source-level validation helpers
# ---------------------------------------------------------------------------


def _source_errors(source: Path) -> list[str]:
    if not source.exists():
        return [f"source does not exist: {source}"]
    if not source.is_dir():
        return [f"source is not a directory: {source}"]
    return []


def _validate_run_manifest(path: Path) -> tuple[list[str], dict[str, Any]]:
    """Validate run_manifest.json. Returns (errors, artifact_info)."""
    errors: list[str] = []
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        info: dict[str, Any] = {"status": "invalid_json", "error": str(exc)}
        return [f"run_manifest.json: invalid JSON: {exc}"], info
    if not isinstance(raw, dict):
        return ["run_manifest.json: must be a JSON object"], {"status": "invalid_payload"}
    if "run_ref" not in raw:
        errors.append("run_manifest.json: missing required field: run_ref")
    return errors, {"status": "present" if not errors else "invalid_payload", "path": str(path)}


def _validate_control_metrics(path: Path) -> tuple[list[str], dict[str, Any]]:
    """Validate control_metrics.json. Returns (errors, artifact_info)."""
    errors: list[str] = []
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        info: dict[str, Any] = {"status": "invalid_json", "error": str(exc)}
        return [f"control_metrics.json: invalid JSON: {exc}"], info
    if not isinstance(raw, dict):
        return ["control_metrics.json: must be a JSON object"], {"status": "invalid_payload"}
    for field in _REQUIRED_CONTROL_METRICS:
        if field not in raw:
            errors.append(f"control_metrics.json: missing required metric: {field}")
    return errors, {"status": "present" if not errors else "invalid_payload", "path": str(path)}


def _validate_optional_artifact(path: Path, name: str) -> tuple[list[str], dict[str, Any]]:
    """Validate an optional artifact. Returns (errors, artifact_info)."""
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"{name}: invalid JSON: {exc}"], {"status": "invalid_json", "error": str(exc)}
    if not isinstance(raw, dict):
        return [f"{name}: must be a JSON object"], {"status": "invalid_payload"}
    return [], {"status": "present", "path": str(path)}


# ---------------------------------------------------------------------------
# Blocker report helpers
# ---------------------------------------------------------------------------


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


def _rewrite_blocker_report(
    path: Path,
    *,
    run_ref: str,
    old_run_ref: str,
) -> dict[str, Any]:
    """Rewrite stale run_ref/parents/wb_ref in an imported blocker report.

    Fails if the payload is not a JSON object.  Regenerates wb_ref to remove
    any embedding of the old run identity.
    """
    payload = _read_json(path)  # raises ValueError if not dict
    payload["run_ref"] = run_ref
    payload["parents"] = [run_ref]
    payload.setdefault("wb_type", "BlockerReport")
    # Always regenerate wb_ref so the old run identity is not embedded.
    payload["wb_ref"] = stable_ref("blocker", run_ref, payload)
    return payload


# ---------------------------------------------------------------------------
# Scientific debt helpers
# ---------------------------------------------------------------------------


def _rewrite_scientific_debt(
    path: Path,
    *,
    old_run_ref: str,
    new_run_ref: str,
) -> dict[str, Any]:
    """Rewrite stale refs in an imported scientific_debt.json.

    Rewrites:
      - top-level run_ref
      - top-level parents (if present)
      - mechanism_card_ref (if it clearly derives from old_run_ref)
      - per-item debt_ref (if it embeds old_run_ref)

    Raises ValueError if stale refs cannot be safely rewritten or if the
    payload is not a JSON object.

    Imported scientific debt remains debt: rewriting refs does NOT strengthen
    evidence or set claim_bearing=True.
    """
    payload = _read_json(path)  # raises ValueError if not dict

    # Rewrite top-level run_ref.
    payload["run_ref"] = new_run_ref

    # Rewrite top-level parents.
    if "parents" in payload:
        payload["parents"] = _rewrite_ref_list(
            payload["parents"], old_run_ref, new_run_ref, field="parents"
        )

    # Rewrite mechanism_card_ref if it embeds the old run ref.
    if "mechanism_card_ref" in payload:
        mcr = str(payload["mechanism_card_ref"])
        if old_run_ref in mcr:
            payload["mechanism_card_ref"] = mcr.replace(old_run_ref, new_run_ref)

    # Rewrite per-item debt_ref.
    items = payload.get("items", [])
    if not isinstance(items, list):
        raise ValueError(
            f"scientific_debt.json: 'items' must be a list, got {type(items).__name__}"
        )
    rewritten_items = []
    for i, item in enumerate(items):
        if not isinstance(item, dict):
            raise ValueError(
                f"scientific_debt.json: items[{i}] must be an object, got {type(item).__name__}"
            )
        item = dict(item)
        if "debt_ref" in item:
            dr = str(item["debt_ref"])
            if old_run_ref in dr:
                item["debt_ref"] = dr.replace(old_run_ref, new_run_ref)
        # Rewrite item-level run_ref / source run fields if present.
        for field in ("run_ref", "source_run_ref", "parent_run_ref"):
            if field in item and item[field] == old_run_ref:
                item[field] = new_run_ref
        rewritten_items.append(item)
    payload["items"] = rewritten_items

    # Imported debt remains non-claim-bearing.
    payload["claim_bearing"] = False

    return payload


# ---------------------------------------------------------------------------
# Low-level helpers
# ---------------------------------------------------------------------------


def _original_run_ref(manifest_path: Path) -> str:
    """Read the run_ref from a *source* manifest before it has been rewritten."""
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    if isinstance(payload, dict) and "run_ref" in payload:
        return str(payload["run_ref"])
    return ""


def _rewrite_ref_list(
    value: Any, old_ref: str, new_ref: str, *, field: str
) -> list[str]:
    if not isinstance(value, list):
        raise ValueError(
            f"scientific_debt.json: '{field}' must be a list, got {type(value).__name__}"
        )
    return [new_ref if item == old_ref else str(item) for item in value]


def _read_json(path: Path) -> dict[str, Any]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError(f"expected object JSON: {path}")
    return raw


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
