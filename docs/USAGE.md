# Mechanistic Workbench Usage

This is the generic local workflow for Mechanistic Workbench (`mwb`). It does not require any dogfood adapter or external experiment repository.

MWB is a local-first, IPython-native research workbench for mechanistic interpretability. It preserves durable research state around exploratory work: typed objects, sessions, run artifacts, evidence graph edges, blockers, next probes, MechanismCards, claim checks, and Git-visible ledgers.

The core rule is:

```text
A scientific claim must be traceable to real artifacts, validated controls, and explicit evidence gates.
```

A command can succeed without producing claim-bearing evidence. A dry-run can be useful without being evidence. A card can render while mechanism language remains blocked.

## Setup

```bash
uv sync
uv run mwb init --name mwb-demo
uv run mwb doctor
```

Runtime state is written under `.mechanism/`. That directory is local/generated state unless explicitly exported.

Human-reviewed research state lives under `research/`, especially:

```text
research/logs/
  claim_ledger.md
  decision_log.md
  research_log.md
  run_ledger.csv
```

## Scratch Work

Launch IPython with the Workbench context:

```bash
uv run mwb ipython
```

Inside IPython:

```python
%load_ext mwb.ipython

note = ctx.note("first exploratory note")
display_graph()
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

* session metadata;
* cell source snapshots;
* execution index;
* cell status;
* bounded stdout and stderr;
* exceptions and tracebacks;
* typed MWB object creation;
* typed MWB object mutation;
* typed MWB object alias binding;
* typed MWB object alias deletion;
* lineage edges from cells to objects;
* parent-object lineage edges.

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

Important boundary: MWB does not currently snapshot every arbitrary Python variable. It tracks typed MWB workbench objects and session metadata. It does not automatically version all tensors, models, dataframes, or large objects by content hash. This is deliberate: scratch exploration should stay cheap, and formalization should be retrospective and selective.

Inspect the latest captured session:

```bash
uv run mwb inspect session latest
```

Rebuild or repair the SQLite operational index from file-backed records:

```bash
uv run mwb rebuild-index --output .mechanism/workbench.rebuilt.sqlite
uv run mwb repair-index --output .mechanism/workbench.repaired.sqlite
```

SQLite is an operational index, not the canonical research record.

## Built-In Demo Workflow

Run the built-in negation demo as a non-claim-bearing dry-run:

```bash
uv run mwb demo negation --model EleutherAI/pythia-70m-deduped --device cpu --dry-run
```

The built-in negation demo is a compact MWB demo bundle. It is not the product identity.

The dry-run materializes a generic non-claim-bearing artifact set, so these commands work immediately afterward:

```bash
uv run mwb card latest
uv run mwb diagnose latest
uv run mwb next-probe latest --materialize
uv run mwb graph rebuild
```

Dry-run output is diagnostic-only. It does not upgrade evidence tier and does not make any claim paper-ready.

## Generic Artifact-Bundle Ingest

MWB includes a neutral `generic-bundle` adapter for importing MWB-shaped run artifacts.

Inspect registered adapters:

```bash
uv run mwb adapters list --json
uv run mwb adapters inspect generic-bundle --json
```

Check whether a source path can be ingested:

```bash
uv run mwb adapters can-ingest generic-bundle tests/fixtures/generic_runs/control_leak --json
```

Ingest a neutral MWB-shaped artifact bundle:

```bash
uv run mwb ingest external generic-bundle tests/fixtures/generic_runs/control_leak
```

Then inspect the resulting run:

```bash
uv run mwb card latest
uv run mwb diagnose latest
uv run mwb next-probe latest --materialize
uv run mwb graph rebuild
```

Adapter ingestion maps external artifacts into generic MWB artifacts. Adapter ingestion does not upgrade evidence tier or make a run claim-bearing.

## Sweep Artifacts

Dry-run sweeps write a full non-claim-bearing artifact set under `.mechanism/runs/<run_ref>/`:

```bash
uv run mwb sweep docs/fixtures/hypothesis_phase5.json \
  --axis layer=0,1 \
  --axis patch_mode=direct \
  --dry-run
```

The emitted files include:

```text
sweep_config.json
run_manifest.json
verification_results.jsonl
intervention_receipts.jsonl
control_metrics.json
blocker_report.json
```

Dry-run sweeps are useful for checking shape, configuration, and artifact flow. They are not claim-bearing evidence.

## Diagnosis And Probes

Blocked runs should produce auditable next steps:

```bash
uv run mwb diagnose latest
uv run mwb next-probe latest --materialize
uv run mwb run-probe .mechanism/runs/<run_ref>/probe.yaml
```

Diagnosis reads run-local artifacts such as:

```text
run_manifest.json
control_metrics.json
blocker_report.json
scientific_debt.json
```

Probe materialization writes structured probe files:

```text
probe.json
probe.yaml
probe.md
```

The probe runner validates probe kind and parameters before running implemented workflows. Unsupported probe kinds are recorded as blocked materialized probes and must not emit fake runnable commands.

If a materialized probe is a dry-run or diagnostic workflow, it remains non-claim-bearing unless a real backend execution path and artifact validation gate explicitly support a stronger posture.

## Evidence Graph

Rebuild the evidence graph:

```bash
uv run mwb graph rebuild
```

Run focused graph queries:

```bash
uv run mwb graph query claims-depending-on <unit-or-object-ref>
uv run mwb graph query controls-contradicting <run-ref>
uv run mwb graph query cells-producing <artifact-ref>
uv run mwb graph query debt-blocking <claim-ref>
```

The graph records provenance and evidence relationships. A graph edge alone does not upgrade a claim.

## Ledgers

Validate Git-visible research ledgers:

```bash
uv run mwb ledger validate
```

Generate human-reviewable proposals from local state:

```bash
uv run mwb ledger propose-run <run-ref>
uv run mwb ledger propose-claim <card-ref>
```

Proposal files remain local until reviewed. Committed ledgers live under `research/logs/`.

## Hypothesis Lifecycle

Workflow state is separate from evidence tier and claim status.

```bash
uv run mwb hypothesis transition <hypothesis-ref> --to-state triaged
uv run mwb hypothesis explain <run-ref>
```

A hypothesis can be live, blocked, abandoned, or claimable without collapsing those concepts into one enum. Promotion to stronger claim language requires evidence gates and human review.

## Space Typing

Check tensor, hook, feature, and intervention compatibility:

```bash
uv run mwb space check docs/fixtures/space_check_valid.json
```

Space checks prevent invalid tensor, feature, hook, dictionary, or intervention operations from being treated as meaningful evidence.

## Static Compiler

Run cheap mechanistic plausibility checks before expensive interventions:

```bash
uv run mwb compile hypothesis docs/fixtures/hypothesis_phase5.json
```

Static checks can block or downgrade claim posture. Static evidence alone is not causal evidence.

## Causal Verification

Run implemented verification workflows in diagnostic mode:

```bash
uv run mwb verify docs/fixtures/hypothesis_phase5.json --diagnostic-only --dry-run
```

Verification workflows write receipts and telemetry for implemented operations. Diagnostic operations remain diagnostic unless all required claim-bearing gates pass.

## Example Geometry

Audit built-in example/control bundle geometry:

```bash
uv run mwb bundle audit negation_demo_calibrated
uv run mwb bundle rebalance --dry-run
```

Bundle audits check whether examples and controls are fit for serious causal claims. They can identify issues such as invalid examples, role imbalance, contaminated controls, weak margins, or inadequate heldout coverage.

## Reference Mechanisms

Run deterministic known-ground-truth framework checks:

```bash
uv run mwb benchmark framework
```

Reference mechanism tasks test the framework against known-good and known-bad cases, including toy mechanisms, synthetic SAE structures, and negative controls.

## Policy Profiles

Check strict evidence-policy settings:

```bash
uv run mwb policy check
```

Policy profiles define claim ceilings and evidence requirements. The default posture is strict: dry-runs, fixture-only evidence, unresolved control leakage, zero-ablation-only evidence, missing artifacts, and unresolved scientific debt should block stronger claims.

## Adapter Registry

Adapter inspection, source capability checks, ingestion, and conformance are separate operations.

Inspect registered ingest adapters:

```bash
uv run mwb adapters list --json
uv run mwb adapters inspect generic-bundle --json
uv run mwb adapters inspect self-ground --json
```

Check whether a source path can be ingested:

```bash
uv run mwb adapters can-ingest generic-bundle tests/fixtures/generic_runs/control_leak --json
uv run mwb adapters can-ingest self-ground /path/to/self-ground/runs/<run-id> --json
```

Ingest through the generic dispatcher:

```bash
uv run mwb ingest external generic-bundle tests/fixtures/generic_runs/control_leak
uv run mwb ingest external self-ground /path/to/self-ground/runs/<run-id>
```

The singular `adapter` namespace is used for backend conformance checks:

```bash
uv run mwb adapter conformance transformer-lens --model EleutherAI/pythia-70m-deduped --device cpu
uv run mwb adapter conformance saelens --model EleutherAI/pythia-70m-deduped --hook blocks.2.hook_resid_post --device cpu

uv run mwb adapter conformance nnsight --model gpt2 --module-path transformer.h.0.mlp --dry-run
uv run mwb adapter conformance pyvene --model gpt2 --module-path transformer.h.0.mlp --dry-run
uv run mwb adapter conformance neuronpedia --model-id gemma-2-2b --sae-id 20-gemmascope-res-16k --feature-index 123 --dry-run
```

Adapter conformance distinguishes:

```text
unsupported
diagnostic-only
claim-bearing candidate
claim-bearing
```

A successful import is not a valid backend. A valid backend is not automatically claim-bearing. A claim-bearing backend does not make every run claim-bearing.

## Optional Dogfood Adapter

SELF-GROUND is available only as an optional dogfood adapter:

```bash
uv run mwb adapters inspect self-ground --json
uv run mwb adapters can-ingest self-ground /path/to/self-ground/runs/<run-id> --json
uv run mwb ingest self-ground /path/to/self-ground/runs/<run-id>
uv run mwb ingest external self-ground /path/to/self-ground/runs/<run-id>
```

The `ingest self-ground` command is a convenience alias. It routes through the same generic adapter dispatcher as `ingest external self-ground`.

This adapter is useful for dogfooding MWB against real mechanistic-interpretability artifacts, but MWB does not depend on SELF-GROUND and is not a SELF-GROUND-specific codebase.

Adapter ingestion does not upgrade claims by itself. Dry-run and diagnostic states remain non-claim-bearing. A stronger claim requires validated artifacts, clean controls, sufficient effect, policy compliance, and human review before paper-facing language.

See `docs/adapters/self_ground/README.md`.

## Evidence Tiers And Claim Boundaries

MWB uses conservative evidence boundaries.

Typical claim language should move through stages such as:

```text
observed
associated with
candidate marker for
static projection support
diagnostic causal test
controlled causal test
claim-bearing candidate
```

Mechanism language is intentionally expensive. Terms such as:

```text
causes
is necessary for
is sufficient for
implements
mechanism for
```

should remain blocked unless the relevant artifact, control, verification, generalization, and policy gates pass.

Interpretation discipline:

```text
ingest != proof
diagnosis != proof
next probe != proof
materialized probe != proof
dry-run != proof
completed command != proof
card rendering != proof
```

## Development QC

Minimum local QC:

```bash
uv sync
uv run ruff check .
uv run pytest
uv run mwb doctor
uv run mwb graph rebuild
uv run mwb ledger validate
```

Adapter-sensitive changes should also run:

```bash
uv run mwb adapters list --json
uv run mwb adapters inspect generic-bundle --json
uv run mwb adapters can-ingest generic-bundle tests/fixtures/generic_runs/control_leak --json
uv run mwb ingest external generic-bundle tests/fixtures/generic_runs/control_leak

uv run pytest tests/adapters/test_generic_bundle_ingest.py
uv run pytest tests/adapters/test_self_ground_boundary.py
uv run pytest tests/adapters/test_self_ground_ingest.py
```

Run real integration checks when the environment supports them:

```bash
MWB_RUN_REAL_ADAPTER_TESTS=1 uv run pytest tests/test_phase4_context.py -m integration
uv run mwb adapter conformance transformer-lens --model EleutherAI/pythia-70m-deduped --device cpu
uv run mwb adapter conformance saelens --model EleutherAI/pythia-70m-deduped --hook blocks.2.hook_resid_post --device cpu
```

Optional backend integrations should fail clearly when missing and must not silently degrade into fake success.
