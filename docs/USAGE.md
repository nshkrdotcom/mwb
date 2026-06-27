# Mechanistic Workbench Usage

This is the generic local workflow for Mechanistic Workbench. It does not
require any dogfood adapter or external experiment repository.

## Setup

```bash
uv sync
uv run mwb init --name mwb-demo
uv run mwb doctor
```

Runtime state is written under `.mechanism/`. That directory is intentionally
ignored by Git.

## Scratch Work

Launch IPython with Workbench context:

```bash
uv run mwb ipython
```

Run a captured one-cell session:

```bash
uv run mwb ipython --execute "bundle = ctx.domains.negation.load('demo_calibrated')"
uv run mwb inspect session latest
```

Resume from an existing captured session:

```bash
uv run mwb ipython --resume <session-ref> --execute "note = ctx.note('resumed work')"
```

`ctx.note(...)` creates a typed note object, and `ctx.record(obj, name=...)`
returns a labeled typed object copy that is captured when bound in IPython.

## Generic Demo

Run or validate the built-in negation demo:

```bash
uv run mwb demo negation --model EleutherAI/pythia-70m-deduped --device cpu --dry-run
```

The dry-run output is diagnostic-only and non-claim-bearing. It also
materializes a generic dry-run artifact set, so these commands work immediately
afterward:

```bash
uv run mwb card latest
uv run mwb diagnose latest
uv run mwb next-probe latest --materialize
uv run mwb graph rebuild
```

## Sweep Artifacts

Dry-run sweeps write a full non-claim-bearing artifact set under
`.mechanism/runs/<run_ref>/`:

```bash
uv run mwb sweep docs/fixtures/hypothesis_phase5.json \
  --axis layer=0,1 \
  --axis feature_selection_mode=top-absolute \
  --axis operation=ablate \
  --axis patch_mode=direct \
  --axis amplification_factor=1.0 \
  --axis control_family=negation_removed \
  --dry-run
```

The emitted files include `sweep_config.json`, `run_manifest.json`,
`verification_results.jsonl`, `intervention_receipts.jsonl`,
`control_metrics.json`, and `blocker_report.json`.

## Adapter Registry

Adapter inspection and source capability checks are separate:

```bash
uv run mwb adapters list --json
uv run mwb adapters inspect generic-bundle --json
uv run mwb adapters can-ingest generic-bundle tests/fixtures/generic_runs/control_leak --json
```

Adapters map external artifacts into generic MWB artifacts. Adapter ingestion
does not upgrade evidence tier or make a run claim-bearing.

Ingest a neutral MWB-shaped artifact bundle:

```bash
uv run mwb ingest external generic-bundle tests/fixtures/generic_runs/control_leak
```

## Optional Dogfood Adapter

SELF-GROUND is available only as an optional dogfood adapter:

```bash
uv run mwb adapters inspect self-ground --json
uv run mwb adapters can-ingest self-ground /path/to/self-ground/runs/<run-id> --json
uv run mwb ingest self-ground /path/to/self-ground/runs/<run-id>
uv run mwb ingest external self-ground /path/to/self-ground/runs/<run-id>
```

See `docs/adapters/self_ground/README.md`.

## Backend Checks

```bash
uv run mwb adapter conformance transformer-lens --model EleutherAI/pythia-70m-deduped --device cpu
uv run mwb adapter conformance saelens --model EleutherAI/pythia-70m-deduped --hook blocks.2.hook_resid_post --device cpu
```

Optional adapter diagnostics keep dependencies optional and non-claim-bearing:

```bash
uv run mwb adapter conformance nnsight \
  --model gpt2 \
  --module-path transformer.h.0.mlp \
  --device cpu \
  --dry-run

uv run mwb adapter conformance pyvene \
  --model gpt2 \
  --module-path transformer.h.0.mlp \
  --intervention-kind resample_ablation \
  --device cpu \
  --dry-run

uv run mwb adapter conformance neuronpedia \
  --model-id gemma-2-2b \
  --sae-id 20-gemmascope-res-16k \
  --feature-index 123 \
  --dry-run
```

Conformance artifacts are written under `.mechanism/adapters/<adapter>/`. See
`docs/ADAPTERS.md`.

## Diagnosis And Probes

```bash
uv run mwb diagnose latest
uv run mwb next-probe latest --materialize
uv run mwb run-probe .mechanism/runs/<run_ref>/probe.yaml
```

Diagnosis writes `diagnosis_tree.json`, `diagnosis_tree.yaml`, and
`diagnosis_tree.md`. Probe materialization writes `probe.json`, `probe.yaml`,
and `probe.md`. See `docs/DIAGNOSIS_AND_PROBES.md`.

## Evidence Graph

```bash
uv run mwb graph rebuild
uv run mwb graph query claims-depending-on <unit-or-object-ref>
uv run mwb graph query controls-contradicting <run-ref>
uv run mwb graph query cells-producing <artifact-ref>
uv run mwb graph query debt-blocking <claim-ref>
```

Graph edges are written to `.mechanism/graph/evidence_edges.jsonl` and indexed
in SQLite. See `docs/EVIDENCE_GRAPH.md`.

## Research Ledgers

```bash
uv run mwb ledger validate
uv run mwb ledger propose-run <run-ref>
uv run mwb ledger propose-claim <card-ref>
```

Committed ledgers live under `research/logs/`. Proposal files stay under
`.mechanism/` until reviewed. See `docs/LEDGERS.md`.

## Claim Grammar

```bash
uv run mwb claim check docs/fixtures/claim_association.json
uv run mwb draft-check docs/fixture_draft.md
```

Claim checks write `.mechanism/claims/<claim_ref>_grammar_report.json` and
block stronger language when evidence requirements, blockers, or unresolved
scientific debt do not support the requested claim type. See
`docs/CLAIM_GRAMMAR.md`.

## Policy, Space, Compiler, Verification

```bash
uv run mwb policy check
uv run mwb space check docs/fixtures/space_check_valid.json
uv run mwb compile hypothesis docs/fixtures/hypothesis_phase5.json
uv run mwb verify docs/fixtures/hypothesis_phase5.json --diagnostic-only --dry-run
```

Dry-run verification remains non-claim-bearing.

## Example Geometry

```bash
uv run mwb bundle audit negation_demo_calibrated
uv run mwb bundle rebalance --dry-run
```

The audit checks token validity, role balance, contaminated controls, and
baseline margins, then proposes heldout/control-balance improvements. See
`docs/EXAMPLE_GEOMETRY.md`.

## Reference Mechanisms

```bash
uv run mwb benchmark framework
```

The benchmark checks deterministic known-ground-truth tasks. See
`docs/REFERENCE_MECHANISMS.md`.

## Quality Gate

```bash
uv run ruff check .
uv run pytest
uv run mwb doctor
uv run mwb graph rebuild
uv run mwb ledger validate
```
