from __future__ import annotations

from pathlib import Path

import typer

from mwb.adapters.base import AdapterCapabilityReport, AdapterMetadata, ArtifactIngestAdapter


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

    def list_metadata(self) -> list[AdapterMetadata]:
        reports: list[AdapterMetadata] = []
        for adapter in sorted(self._adapters.values(), key=lambda item: item.adapter_id):
            reports.append(self.inspect(adapter.adapter_id))
        return reports

    def list_capabilities(self, *, source: Path | None = None) -> list[AdapterCapabilityReport]:
        if source is None:
            return [
                AdapterCapabilityReport(
                    adapter_id=metadata.adapter_id,
                    display_name=metadata.display_name,
                    status=metadata.status,
                    modes=metadata.modes,
                    claim_bearing=metadata.claim_bearing,
                    notes=metadata.notes,
                )
                for metadata in self.list_metadata()
            ]
        return [
            adapter.can_ingest(source)
            for adapter in sorted(self._adapters.values(), key=lambda item: item.adapter_id)
        ]

    def inspect(self, adapter_id: str) -> AdapterMetadata:
        adapter = self.get(adapter_id)
        return AdapterMetadata(
            adapter_id=adapter.adapter_id,
            display_name=adapter.display_name,
            status="available",
            modes=sorted(set(getattr(adapter, "modes", ["ingest"]))),
            claim_bearing=bool(getattr(adapter, "claim_bearing", False)),
            notes=list(getattr(adapter, "notes", [])),
        )

    def can_ingest(self, adapter_id: str, source: Path) -> AdapterCapabilityReport:
        return self.get(adapter_id).can_ingest(source)


def default_registry() -> AdapterRegistry:
    registry = AdapterRegistry()
    from mwb.adapters.generic_bundle import GenericBundleIngestAdapter
    from mwb.adapters.self_ground.ingest import SelfGroundIngestAdapter

    registry.register(GenericBundleIngestAdapter())
    registry.register(SelfGroundIngestAdapter())
    return registry


def register_adapter_cli_commands(ingest_app: typer.Typer) -> None:
    from mwb.adapters.self_ground.commands import register_commands

    register_commands(ingest_app)
