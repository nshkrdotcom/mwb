# SELF-GROUND Adapter

SELF-GROUND is an optional dogfood adapter for importing selected experiment
artifacts into the generic MWB evidence model. MWB does not depend on
SELF-GROUND, and SELF-GROUND does not define MWB's core ontology, command
surface, claims, graph, cards, ledgers, or default examples.

## Commands

```bash
uv run mwb adapters inspect self-ground --json
uv run mwb adapters can-ingest self-ground /path/to/self-ground/runs/<run-id> --json
uv run mwb ingest self-ground /path/to/self-ground/runs/<run-id>
uv run mwb ingest external self-ground /path/to/self-ground/runs/<run-id>
```

The `ingest self-ground` command is a convenience alias. It routes through the
same generic adapter dispatcher as `ingest external self-ground`.

## Artifact Shape

The adapter validates the SELF-GROUND run shape under the adapter package. The
expected files include summary JSON, comparison tables, forensics tables, and a
claim-adjudication note from the source run. Those source-specific filenames are
not part of MWB core.

## MWB Mapping

On successful ingest, the adapter writes generic MWB artifacts under
`.mechanism/runs/<run-ref>/`:

- `run_manifest.json`
- `control_metrics.json`
- `blocker_report.json`
- `scientific_debt.json`
- `mechanism_card.json`
- `next_probe.json`

New ingests use adapter-scoped run refs such as
`run_adapter_self_ground_<source-id>`. Older refs such as
`run_self_ground_<source-id>` remain readable when they already exist as run
directories.

Adapter ingestion is non-claim-bearing by itself. It maps source metrics into
generic control metrics and lets MWB's generic blocker, card, diagnosis,
next-probe, evidence graph, and ledger logic decide the evidence posture.
