from __future__ import annotations

from pathlib import Path

from mwb.adapters.base import IngestResult
from mwb.adapters.registry import AdapterRegistry, default_registry
from mwb.project import Project, ProjectManager


def ingest_external_run(
    adapter_id: str,
    source: Path,
    *,
    project: Project | None = None,
    registry: AdapterRegistry | None = None,
) -> IngestResult:
    project = project or ProjectManager.discover_or_create()
    adapter = (registry or default_registry()).get(adapter_id)
    capability = adapter.can_ingest(source)
    if capability.status == "unavailable":
        detail = "; ".join(capability.errors) or f"{adapter_id} cannot ingest {source}"
        raise ValueError(detail)
    return adapter.ingest(source, project=project)
