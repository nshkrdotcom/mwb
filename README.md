<p align="center">
  <img src="assets/mwb-readme.webp" alt="Mechanistic Workbench" width="800">
</p>

<p align="center">
  <a href="https://github.com/nshkrdotcom/mwb"><img src="https://img.shields.io/badge/GitHub-nshkrdotcom%2Fmwb-181717?logo=github" alt="GitHub repository"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-blue.svg" alt="MIT License"></a>
</p>

# Mechanistic Workbench

Mechanistic Workbench (`mwb`) is a local-first, IPython-native mechanistic
interpretability workbench for scratch-first research, typed artifacts,
evidence graphs, agent-readable state, artifact validation, adapter-backed
ingestion and execution paths, and claim-safe research workflows.

MWB is designed to sit between exploratory notebook work and claim-bearing
mechanistic evidence:

```text
scratch exploration
  -> typed mechanistic objects
  -> session provenance
  -> run artifacts
  -> evidence graph
  -> diagnosis and blockers
  -> next probes
  -> verification receipts
  -> MechanismCards
  -> claim-safe writing constraints
```

The workbench is intentionally local-first. Canonical project state lives in
`.mechanism/` and Git-visible research ledgers, not in a hosted service or
hidden database. SQLite is a rebuildable operational index, not the sole source
of truth.

## What MWB Is For

MWB helps mechanistic-interpretability researchers answer practical research
state questions:

```text
What did I run?
What code cell created this object?
What artifacts support this run?
What controls failed?
What claim language is allowed?
What claim language is blocked?
What is merely diagnostic?
What is real execution?
What should I test next?
Can another agent or researcher resume this work without reading the whole notebook?
```

The core invariant is:

```text
A scientific claim must be traceable to real artifacts, validated controls, and explicit evidence gates.
```

A command can succeed while producing no claim-bearing evidence. A run can
complete while controls still block the intended claim. A card can render while
mechanism language remains forbidden.

## Current Implementation Status

The repository contains a working local workbench with:

- project initialization and health checks;
- IPython extension and session capture;
- typed workbench objects and object lineage;
- local `.mechanism/` artifact workspace;
- SQLite indexing and rebuild/repair commands;
- TransformerLens and SAELens adapter identity/conformance paths;
- adapter registry and generic external ingest dispatch;
- generic MWB artifact-bundle ingestion;
- evidence graph rebuilds and graph queries;
- research ledgers for runs, claims, decisions, and research logs;
- hypothesis lifecycle states and transition receipts;
- alternative-explanation records;
- mechanistic space type checks;
- static mechanistic compiler checks;
- causal verification receipts for implemented diagnostic/verification operations;
- example/control bundle geometry audits;
- diagnosis trees and materialized next probes;
- reference mechanism benchmark fixtures;
- rich claim grammar and Draft Guard checks;
- policy profiles for claim ceilings;
- optional adapter conformance stubs for nnsight, pyvene, Neuronpedia, and artifact pointer integrations.

The current implementation distinguishes:

```text
scratch capture
diagnostic output
dry-run planning
real or external execution artifacts
artifact validation
association-tier evidence
claim-bearing candidates
blocked claims
```

Dry-runs, fixtures, schema-only checks, adapter inspection, and successful
command return codes do not upgrade evidence tiers by themselves.

## What MWB Is Not

MWB is not:

- a replacement for TransformerLens, SAELens, nnsight, pyvene, or other
  scientific execution libraries;
- a hosted experiment tracker;
- a dashboard-first ML platform;
- a generic tensor warehouse;
- an automatic proof system for mechanisms;
- a claim oracle;
- a system that treats notebook scratch work as paper-ready evidence;
- a tool that silently promotes dry-runs or fixture outputs into scientific claims.

MWB should make overclaiming harder, not easier.

## Requirements

- Python `>=3.11,<3.13`
- `uv`
- Git
- local filesystem access

Core Python dependencies include IPython, NumPy, pandas, Pydantic, Rich,
ruamel.yaml, Typer, Torch, TransformerLens, and SAELens.

Optional integrations are treated through explicit adapter/conformance paths.
Their presence does not automatically make any run claim-bearing.

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

## IPython Integration

MWB is IPython-native. Load the extension with:

```python
%load_ext mwb.ipython
```

or start through the CLI:

```bash
uv run mwb ipython
```

The extension injects:

```python
ctx
mwb
display_card
display_run
display_features
display_graph
```

The capture layer records:

- session metadata;
- cell source snapshots;
- execution index and cell status;
- bounded stdout and stderr;
- exceptions and tracebacks;
- MWB object creation, mutation, alias binding, and alias deletion;
- lineage edges from cells to objects;
- parent-object lineage edges.

Session state is written under:

```text
.mechanism/sessions/sess_*/
  session.json
  cells.jsonl
  namespace_objects.jsonl
  snapshots/
  stdout/
  stderr/
  exceptions/
```

MWB does not snapshot every arbitrary Python variable. It tracks typed MWB
objects and session metadata so scratch exploration stays cheap and
formalization remains selective.

## Project Workspace

A project has a local `.mechanism/` directory containing generated and
rebuildable workbench state:

```text
.mechanism/
  project.toml
  sessions/
  runs/
  artifacts/
  graph/
  hypotheses/
  claims/
  cards/
  adapters/
  bundle_audits/
  bundle_rebalance/
  workbench.sqlite
```

Human-approved research state lives in flat files under `research/`:

```text
research/
  logs/
    claim_ledger.md
    decision_log.md
    research_log.md
    run_ledger.csv
  experiments/
  bundles/
  paper/
  reference_tasks/
```

## SQLite Recovery

SQLite is an operational index. It can be rebuilt or repaired from file-backed
workbench records:

```bash
uv run mwb rebuild-index --output .mechanism/workbench.rebuilt.sqlite
uv run mwb repair-index --output .mechanism/workbench.repaired.sqlite
```

Deleting SQLite should not destroy the canonical research record if the
file-backed artifacts are intact.

## Evidence Graph

The evidence graph records typed relationships among cells, objects, artifacts,
runs, claims, blockers, and debt.

Relations include:

```text
derived_from
depends_on
tested_by
supports
contradicts
confounded_by
fails_on
generalizes_to
cited_by
```

Rebuild the graph:

```bash
uv run mwb graph rebuild
```

Run focused queries:

```bash
uv run mwb graph query claims-depending-on <unit-or-object-ref>
uv run mwb graph query controls-contradicting <run-ref>
uv run mwb graph query cells-producing <artifact-ref>
uv run mwb graph query debt-blocking <claim-ref>
```

Graph edges record provenance and evidence relationships. A graph edge alone
does not upgrade a claim.

## MechanismCards And Claim Safety

A MechanismCard summarizes what a run can and cannot support. It records:

- run reference;
- status;
- evidence tier;
- claim-bearing status;
- blockers;
- allowed language;
- blocked language;
- artifact references;
- policy implications;
- scientific debt.

Generate or inspect a card:

```bash
uv run mwb card latest
uv run mwb draft-check docs/fixture_draft.md
uv run mwb claim check docs/fixtures/claim_association.json
```

Draft Guard resolves `[CLAIM:<ref>]` tags to generated cards and typed claim
grammar. Stronger language is blocked when evidence requirements, blockers, or
unresolved debt do not support it.

## Diagnosis And Next Probes

Blocked runs should produce auditable next steps:

```bash
uv run mwb diagnose latest
uv run mwb next-probe latest --materialize
uv run mwb run-probe .mechanism/runs/<run_ref>/probe.yaml
```

Diagnosis reads run-local artifacts:

- `run_manifest.json`
- `control_metrics.json`
- `blocker_report.json`
- `scientific_debt.json`

Materialized probes are structured files, not free-form shell snippets. The
runner validates probe kind and parameters before executing any implemented
workflow.

## Adapters

Adapters own external artifact shapes, backend command templates, validation
rules, output mapping, capability checks, and integration tests. Core MWB owns
the generic protocol, registry, dispatch, and artifact contracts.

Inspect registered adapters:

```bash
uv run mwb adapters list --json
uv run mwb adapters inspect generic-bundle --json
uv run mwb adapters can-ingest generic-bundle tests/fixtures/generic_runs/control_leak --json
```

Ingest a generic MWB-shaped artifact bundle:

```bash
uv run mwb ingest external generic-bundle tests/fixtures/generic_runs/control_leak
```

Conformance commands remain under the singular `adapter` namespace:

```bash
uv run mwb adapter conformance transformer-lens \
  --model EleutherAI/pythia-70m-deduped \
  --device cpu
```

Adapter inspection and adapter source capability are separate operations:
`inspect` reports static adapter metadata, while `can-ingest` checks one source
path.

## Built-In Demo

The built-in negation demo is a compact MWB demo bundle, not a product identity:

```bash
uv run mwb demo negation --model EleutherAI/pythia-70m-deduped --device cpu --dry-run
```

The dry-run materializes a non-claim-bearing run so `card latest`, `diagnose
latest`, `next-probe latest`, and `graph rebuild` work in a clean project
without external experiment artifacts.

## Optional Dogfood Adapter: SELF-GROUND

MWB includes an optional SELF-GROUND adapter for importing selected
SELF-GROUND run artifacts into the generic MWB evidence model.

```bash
uv run mwb adapters inspect self-ground --json
uv run mwb adapters can-ingest self-ground /path/to/self-ground/run --json
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
- `docs/buildout/README.md` - active generic buildout direction.
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
