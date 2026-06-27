from __future__ import annotations

from pathlib import Path
from typing import Any

import typer

from mwb.adapters.base import AdapterCapabilityReport, ArtifactIngestAdapter


class AdapterRegistry:
    def __init__(self) -> None:
        self._adapters: dict[str, ArtifactIngestAdapter] = {}

    def register(self, adapter: ArtifactIngestAdapter) -> None:
        self._adapters[adapter.adapter_id] = adapter

    def get(self, adapter_id: str) -> ArtifactIngestAdapter:
        try:
            return self._adapters[adapter_id]
        except KeyError as exc:
            available = ", ".join(sorted(self._adapters)) or "<none>"
            raise KeyError(f"unknown adapter {adapter_id!r}; available: {available}") from exc

    def list_capabilities(self, *, source: Path | None = None) -> list[AdapterCapabilityReport]:
        reports: list[AdapterCapabilityReport] = []
        for adapter in sorted(self._adapters.values(), key=lambda item: item.adapter_id):
            if source is None:
                reports.append(
                    AdapterCapabilityReport(
                        adapter_id=adapter.adapter_id,
                        display_name=adapter.display_name,
                        status="available",
                        modes=["ingest"],
                        claim_bearing=False,
                        notes=[
                            "Registered ingest adapter",
                            "Adapter metadata does not define MWB core ontology",
                        ],
                    )
                )
            else:
                reports.append(adapter.can_ingest(source))
        return reports

    def inspect(self, adapter_id: str) -> dict[str, Any]:
        adapter = self.get(adapter_id)
        capability = adapter.can_ingest(Path.cwd())
        return {
            "adapter_id": adapter.adapter_id,
            "display_name": adapter.display_name,
            "status": "available",
            "modes": sorted(set(capability.modes or ["ingest"])),
            "claim_bearing": capability.claim_bearing,
            "notes": capability.notes,
        }


def default_registry() -> AdapterRegistry:
    registry = AdapterRegistry()
    from mwb.adapters.self_ground.ingest import SelfGroundIngestAdapter

    registry.register(SelfGroundIngestAdapter())
    return registry


def register_adapter_cli_commands(ingest_app: typer.Typer) -> None:
    from mwb.adapters.self_ground.commands import register_commands

    register_commands(ingest_app)
