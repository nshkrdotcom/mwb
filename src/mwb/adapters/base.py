from __future__ import annotations

from pathlib import Path
from typing import Any, Protocol

from pydantic import BaseModel, Field

from mwb.project import Project


class AdapterCapabilityReport(BaseModel):
    adapter_id: str
    display_name: str
    status: str
    modes: list[str] = Field(default_factory=list)
    claim_bearing: bool = False
    notes: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)


class AdapterMetadata(BaseModel):
    adapter_id: str
    display_name: str
    status: str = "available"
    modes: list[str] = Field(default_factory=list)
    claim_bearing: bool = False
    notes: list[str] = Field(default_factory=list)


class ArtifactValidationReport(BaseModel):
    adapter_id: str
    status: str
    artifacts: dict[str, dict[str, Any]] = Field(default_factory=dict)
    errors: list[str] = Field(default_factory=list)


class IngestResult(BaseModel):
    adapter_id: str
    display_name: str
    run_ref: str
    run_dir: Path
    status: str
    primary_blocker: str | None = None
    validation: ArtifactValidationReport


class ArtifactIngestAdapter(Protocol):
    adapter_id: str
    display_name: str
    modes: list[str]
    claim_bearing: bool
    notes: list[str]

    def can_ingest(self, source: Path) -> AdapterCapabilityReport:
        """Report whether this adapter can ingest a source path."""

    def validate_source(self, source: Path) -> ArtifactValidationReport:
        """Validate external artifacts without writing MWB state."""

    def ingest(self, source: Path, *, project: Project) -> IngestResult:
        """Map external artifacts into generic MWB run artifacts."""
