# Mechanistic Workbench

Mechanistic Workbench is a local-first mechanistic interpretability workbench
for IPython research, typed artifacts, evidence graphs, agent-readable state,
adapter-backed execution, artifact validation, and claim-safe research
workflows.

MWB is designed for scratch-first human exploration that still leaves durable
research state behind: run manifests, control metrics, blocker reports,
MechanismCards, scientific debt, ledgers, graph edges, and JSON artifacts that
agents and humans can inspect without relying on a hosted service.

MWB is not a wrapper around one experiment codebase. External tools and
experiment sources enter through adapters.

## Quickstart

```bash
uv sync
uv run mwb init --name mwb-demo
uv run mwb doctor
uv run mwb ipython
uv run mwb demo negation --model EleutherAI/pythia-70m-deduped --device cpu --dry-run
uv run mwb graph rebuild
uv run mwb card latest
```

For a clean project smoke test:

```bash
rm -rf /tmp/mwb-generic-demo
mkdir -p /tmp/mwb-generic-demo
cd /tmp/mwb-generic-demo
uv run --project /path/to/mechanistic-workbench mwb init --name mwb-demo
uv run --project /path/to/mechanistic-workbench mwb doctor
```

## Core MWB

Core MWB owns:

- project/workspace initialization;
- IPython session capture;
- typed mechanistic objects;
- run manifests and refs;
- artifact contracts and validation reports;
- control metrics and blocker reports;
- MechanismCards and claim grammar;
- evidence graph rebuild/query;
- scientific debt and ledgers;
- context compaction and agent-readable JSON state;
- adapter protocol, registry, and generic dispatch.

Core logic derives claim posture from generic MWB artifacts. Adapter metadata is
metadata about provenance, not a core run type.

## Common Commands

```bash
uv run mwb init --name mwb-demo
uv run mwb doctor
uv run mwb ipython
uv run mwb demo negation --model EleutherAI/pythia-70m-deduped --device cpu --dry-run
uv run mwb sweep docs/fixtures/hypothesis_phase5.json --axis layer=0,1 --dry-run
uv run mwb diagnose latest
uv run mwb next-probe latest --materialize
uv run mwb graph rebuild
uv run mwb ledger validate
uv run mwb draft-check docs/fixture_draft.md
```

## Adapters

Adapters own external artifact shapes, backend command templates, validation
rules, output mapping, capability checks, and integration tests.

```bash
uv run mwb adapters list --json
uv run mwb adapters inspect self-ground --json
uv run mwb ingest external <adapter-id> <source>
```

The conformance adapter commands remain available under `mwb adapter
conformance`, with `mwb adapters` provided for registry inspection.

## Optional Dogfood Adapter: SELF-GROUND

MWB includes an optional SELF-GROUND adapter for importing selected
SELF-GROUND run artifacts into the generic MWB evidence model.

```bash
uv run mwb ingest self-ground /path/to/self-ground/run
uv run mwb ingest external self-ground /path/to/self-ground/run
```

This adapter is useful for dogfooding MWB against real
mechanistic-interpretability artifacts, but MWB does not depend on SELF-GROUND
and is not a SELF-GROUND-specific codebase. Adapter ingestion does not upgrade
claims by itself; dry-run and diagnostic states remain non-claim-bearing.

See `docs/adapters/self_ground/README.md`.

## Documentation

- `docs/USAGE.md` - generic local workflow.
- `docs/ADAPTERS.md` - adapter registry, conformance, and claim-bearing gates.
- `docs/CLAIM_GRAMMAR.md` - claim grammar and Draft Guard behavior.
- `docs/DIAGNOSIS_AND_PROBES.md` - diagnosis trees and materialized probes.
- `docs/EVIDENCE_GRAPH.md` - graph schema, rebuild, and queries.
- `docs/LEDGERS.md` - Git-visible research ledger schemas.
- `docs/EXAMPLE_GEOMETRY.md` - target/control bundle audits.
- `docs/RELEASE_HARDENING_REPORT.md` - latest release-hardening evidence.
- `docs/archive/README.md` - historical reports retained for provenance.

## Quality Gate

```bash
uv sync
uv run ruff check .
uv run pytest
uv run mwb doctor
uv run mwb graph rebuild
uv run mwb ledger validate
```
