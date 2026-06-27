from __future__ import annotations

import json
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from mwb.project import ProjectManager
from mwb.workflows.ingest import ingest_external_run

console = Console()


def register_commands(ingest_app: typer.Typer) -> None:
    @ingest_app.command("self-ground")
    def ingest_self_ground(
        source: Annotated[Path, typer.Argument(help="SELF-GROUND run directory.")],
    ) -> None:
        """Ingest a SELF-GROUND run through the SELF-GROUND adapter."""
        project = ProjectManager.discover_or_create()
        result = ingest_external_run("self-ground", source, project=project)
        console.print_json(
            json.dumps(
                {
                    "adapter_id": result.adapter_id,
                    "run_ref": result.run_ref,
                    "status": result.status,
                    "run_dir": str(result.run_dir),
                    "primary_blocker": result.primary_blocker,
                }
            )
        )
