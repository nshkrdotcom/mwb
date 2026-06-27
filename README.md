<p align="center">
  <img src="assets/mwb-readme.webp" alt="Mechanistic Workbench" width="800">
</p>

<p align="center">
  <a href="https://github.com/nshkrdotcom/mwb"><img src="https://img.shields.io/badge/GitHub-nshkrdotcom%2Fmwb-181717?logo=github" alt="GitHub repository"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-blue.svg" alt="MIT License"></a>
</p>

# Mechanistic Workbench

Mechanistic Workbench (`mwb`) is a local-first, IPython-native research workbench for mechanistic interpretability.

It is designed to sit between exploratory notebook work and claim-bearing mechanistic evidence. The goal is not to replace TransformerLens, SAELens, SELF-GROUND, nnsight, pyvene, or other scientific execution libraries. The goal is to give local mechanistic-interpretability work a durable research state:

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

The workbench is intentionally local-first. Canonical project state lives in `.mechanism/` and Git-visible research ledgers, not in a hosted service or hidden database. SQLite is used as a rebuildable operational index, not as the sole source of truth.

## What MWB is for

MWB helps mechanistic-interpretability researchers answer practical research-state questions:

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

It is built around one core epistemic invariant:

```text
A scientific claim must be traceable to real artifacts, validated controls, and explicit evidence gates.
```

A command can succeed while producing no claim-bearing evidence. A run can complete while controls still block the intended claim. A card can render while mechanism language remains forbidden.

## Current implementation status

This repository contains a working local workbench with:

* project initialization and health checks;
* IPython extension and session capture;
* typed workbench objects and object lineage;
* local `.mechanism/` artifact workspace;
* SQLite indexing and rebuild/repair commands;
* TransformerLens and SAELens adapter identity/conformance paths;
* SELF-GROUND run ingestion;
* evidence graph rebuilds and graph queries;
* research ledgers for runs, claims, decisions, and research logs;
* hypothesis lifecycle states and transition receipts;
* alternative-explanation records;
* mechanistic space type checks;
* static mechanistic compiler checks;
* causal verification receipts for implemented diagnostic/verification operations;
* example/control bundle geometry audits;
* diagnosis trees and materialized next probes;
* reference mechanism benchmark fixtures;
* rich claim grammar and draft guard checks;
* policy profiles for claim ceilings;
* optional adapter conformance stubs for nnsight, pyvene, Neuronpedia, and artifact pointer integrations.

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

Some probe workflows are currently diagnostic or dry-run unless a real backend path is explicitly implemented and validated. Dry-runs, fixtures, schema-only checks, and successful command return codes do not upgrade evidence tiers by themselves.

## What MWB is not

MWB is not:

* a replacement for TransformerLens, SAELens, nnsight, pyvene, or SELF-GROUND;
* a hosted experiment tracker;
* a dashboard-first ML platform;
* a generic tensor warehouse;
* an automatic proof system for mechanisms;
* a claim oracle;
* a system that treats notebook scratch work as paper-ready evidence;
* a tool that silently promotes dry-runs or fixture outputs into scientific claims.

MWB should make overclaiming harder, not easier.

## Requirements

The project is built for:

* Python `>=3.11,<3.13`
* `uv`
* Git
* local filesystem access

Core Python dependencies include:

* IPython
* NumPy
* pandas
* Pydantic
* Rich
* ruamel.yaml
* Typer
* Torch
* TransformerLens
* SAELens

Optional integrations such as nnsight, pyvene, Neuronpedia access, DVC, Git LFS, or git-annex are treated through explicit adapter/conformance paths. Their presence does not automatically make any run claim-bearing.

## Installation

Clone the repository and install dependencies:

```bash
git clone <repo-url>
cd mechanistic-workbench
uv sync
```

Run the test suite:

```bash
uv run ruff check .
uv run pytest
```

Initialize a local MWB project workspace:

```bash
uv run mwb init --name self-ground
uv run mwb doctor
```

This creates the local workbench workspace under `.mechanism/`.

## Quick start

A minimal local loop:

```bash
uv sync
uv run mwb init --name self-ground
uv run mwb doctor
uv run mwb ipython
```

Inside IPython:

```python
%load_ext mwb.ipython

note = ctx.note("first exploratory note")
display_graph()
```

Then inspect the captured session:

```bash
uv run mwb inspect session latest
uv run mwb rebuild-index --output .mechanism/workbench.rebuilt.sqlite
```

## IPython integration

MWB is IPython-native.

The IPython extension can be loaded with:

```python
%load_ext mwb.ipython
```

or started through the CLI:

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

The current capture layer automatically records:

* session metadata;
* cell source snapshots;
* execution index;
* cell status;
* bounded stdout and stderr;
* exceptions and tracebacks;
* MWB object creation;
* MWB object mutation;
* MWB object alias binding;
* MWB object alias deletion;
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

## Core concepts

### Project workspace

A project has a local `.mechanism/` directory containing generated and rebuildable workbench state:

```text
.mechanism/
  config.toml
  sessions/
  runs/
  graph/
  hypotheses/
  claims/
  bundle_audits/
  bundle_rebalance/
  workbench.sqlite
```

Large generated artifacts and local run outputs are not assumed to be Git-visible by default.

### Research ledgers

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

These ledgers are intended to be readable, reviewable, and committed.

### SQLite index

SQLite is an operational index. It can be rebuilt or repaired from file-backed workbench records.

```bash
uv run mwb rebuild-index --output .mechanism/workbench.rebuilt.sqlite
uv run mwb repair-index --output .mechanism/workbench.repaired.sqlite
```

Deleting SQLite should not destroy the canonical research record if the file-backed artifacts are intact.

### Evidence graph

The evidence graph records typed relationships among cells, objects, artifacts, runs, claims, blockers, and debt.

Examples of edge relations include:

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

The graph is a provenance and evidence structure. A graph edge alone does not upgrade a claim. Claim permission depends on mechanism cards, blockers, artifact validation, policy profiles, and claim grammar.

### MechanismCards

A MechanismCard summarizes what a run can and cannot support.

A card records, among other things:

* run reference;
* status;
* evidence tier;
* claim-bearing status;
* blockers;
* allowed language;
* blocked language;
* artifact references;
* policy implications.

Generate or inspect a card:

```bash
uv run mwb card latest
```

### Claim grammar

MWB separates claim types and evidence requirements. It can distinguish lightweight observations from stronger claims such as necessity, sufficiency, mediation, generalization, and mechanism claims.

Check a structured claim:

```bash
uv run mwb claim check docs/fixtures/claim_association.json
```

Check prose for unsafe claim language:

```bash
uv run mwb draft-check docs/fixture_draft.md
```

Claim checks are intended to behave like scientific tests:

```text
claim fails
  -> blockers are reported
  -> missing evidence is identified
  -> allowed language remains visible
  -> next action is suggested
```

## Common commands

### Setup and health

```bash
uv sync
uv run ruff check .
uv run pytest
uv run mwb init --name self-ground
uv run mwb doctor
```

### IPython/session workflow

```bash
uv run mwb ipython
uv run mwb ipython --execute "obj = ctx.note('hello from mwb')"
uv run mwb inspect session latest
uv run mwb rebuild-index --output .mechanism/workbench.rebuilt.sqlite
```

### Demo workflow

```bash
uv run mwb demo negation --model EleutherAI/pythia-70m-deduped --device cpu
```

### SELF-GROUND ingest workflow

```bash
uv run mwb ingest self-ground /path/to/self-ground/runs/e004_specificity_rescue_matrix
uv run mwb card latest
uv run mwb diagnose latest
uv run mwb next-probe latest
uv run mwb next-probe latest --materialize
uv run mwb run-probe .mechanism/runs/<run_ref>/probe.yaml
```

If a materialized probe is a dry-run or diagnostic workflow, it remains non-claim-bearing unless a real backend execution path and artifact validation gate explicitly support a stronger posture.

### Evidence graph and ledgers

```bash
uv run mwb graph rebuild
uv run mwb ledger validate
uv run mwb ledger propose-run <run-ref>
uv run mwb ledger propose-claim <card-ref>
```

### Hypothesis lifecycle

```bash
uv run mwb hypothesis transition <hypothesis-ref> --to-state triaged
uv run mwb hypothesis explain <run-ref>
```

Hypothesis lifecycle state is separate from evidence tier and claim status. A hypothesis can be live, blocked, abandoned, or claimable without collapsing those concepts into one enum.

### Space typing

```bash
uv run mwb space check docs/fixtures/space_check_valid.json
```

Space checks prevent invalid tensor, feature, hook, dictionary, or intervention operations from being treated as meaningful evidence.

### Static compiler

```bash
uv run mwb compile hypothesis docs/fixtures/hypothesis_phase5.json
```

The static compiler performs cheap mechanistic plausibility checks before expensive interventions. Static checks can block or downgrade claim posture, but static evidence alone is not causal evidence.

### Causal verification

```bash
uv run mwb verify docs/fixtures/hypothesis_phase5.json --diagnostic-only --dry-run
```

Verification workflows write receipts and telemetry for implemented operations. Diagnostic operations remain diagnostic unless all required claim-bearing gates pass.

### Example geometry

```bash
uv run mwb bundle audit negation_phase3_calibrated
uv run mwb bundle rebalance --dry-run
```

Bundle audits check whether examples and controls are fit for serious causal claims. They can identify issues such as invalid examples, role imbalance, contaminated controls, weak margins, or inadequate heldout coverage.

### Reference mechanisms

```bash
uv run mwb benchmark framework
```

Reference mechanism tasks test the framework against known-good and known-bad cases, including toy mechanisms, synthetic SAE structures, and negative controls.

### Policy profiles

```bash
uv run mwb policy check
```

Policy profiles define claim ceilings and evidence requirements. The default posture is strict: dry-runs, fixture-only evidence, unresolved control leakage, zero-ablation-only evidence, missing artifacts, and unresolved scientific debt should block stronger claims.

### Adapter conformance

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

## Evidence tiers and claim boundaries

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

## Typical SELF-GROUND dogfood loop

A common workflow is:

```bash
uv run mwb init --name self-ground

uv run mwb ingest self-ground /path/to/self-ground/runs/e004_specificity_rescue_matrix

uv run mwb diagnose latest

uv run mwb next-probe latest --materialize

uv run mwb run-probe .mechanism/runs/<run_ref>/probe.yaml

uv run mwb graph rebuild

uv run mwb card latest

uv run mwb draft-check docs/fixture_draft.md
```

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

A stronger claim requires validated artifacts, clean controls, sufficient effect, policy compliance, and human review before paper-facing language.

## Repository layout

```text
docs/
  ADAPTERS.md
  CAUSAL_VERIFICATION.md
  CLAIM_GRAMMAR.md
  DIAGNOSIS_AND_PROBES.md
  EVIDENCE_GRAPH.md
  EXAMPLE_GEOMETRY.md
  FUNDAMENTAL_FUNCTIONALITY_CHECKLIST.md
  HYPOTHESIS_LIFECYCLE.md
  LEDGERS.md
  POLICY_PROFILES.md
  REFERENCE_MECHANISMS.md
  SPACE_TYPES.md
  STATIC_COMPILER.md
  USAGE.md
  world_class_buildout/

research/
  logs/
  experiments/
  bundles/
  paper/
  reference_tasks/

src/mwb/
  adapters/
  domain/
  ipython/
  resources/
  workflows/
  artifacts.py
  bundle_audit.py
  causal_verification.py
  claim_grammar.py
  cli.py
  context.py
  doctor.py
  evidence_graph.py
  hypothesis_lifecycle.py
  ledgers.py
  policy_profiles.py
  reference_benchmarks.py
  session.py
  space_types.py
  sqlite_index.py
  static_compiler.py

tests/
  test_phase*_*.py
```

## Documentation map

Start with:

* `docs/USAGE.md` — common workflows and CLI usage.
* `docs/FUNDAMENTAL_FUNCTIONALITY_CHECKLIST.md` — source-traced implementation boundaries.
* `docs/EVIDENCE_GRAPH.md` — graph semantics and rebuild behavior.
* `docs/LEDGERS.md` — claim, run, decision, and research ledgers.
* `docs/HYPOTHESIS_LIFECYCLE.md` — hypothesis states and transitions.
* `docs/SPACE_TYPES.md` — tensor/feature/hook compatibility.
* `docs/STATIC_COMPILER.md` — static mechanistic checks.
* `docs/CAUSAL_VERIFICATION.md` — verification operations and receipts.
* `docs/EXAMPLE_GEOMETRY.md` — example/control bundle audits.
* `docs/DIAGNOSIS_AND_PROBES.md` — blocker diagnosis and probe materialization.
* `docs/REFERENCE_MECHANISMS.md` — known-ground-truth framework tests.
* `docs/CLAIM_GRAMMAR.md` — claim types and required evidence.
* `docs/POLICY_PROFILES.md` — strict evidence-policy settings.
* `docs/ADAPTERS.md` — adapter capabilities, limitations, and conformance.
* `docs/world_class_buildout/README.md` — source-mined long-term buildout plan.
* `docs/RELEASE_HARDENING_REPORT.md` — release gate and residual risks.
* `docs/PHASE0_ACCEPTANCE_REPORT.md` and `docs/PHASE10_COMPLETION_REPORT.md` — historical dogfood/acceptance reports.

## Development workflow

Use test-first or characterization-test-first development.

Minimum local QC:

```bash
uv sync
uv run ruff check .
uv run pytest
uv run mwb doctor
uv run mwb graph rebuild
uv run mwb ledger validate
```

For index recovery checks:

```bash
uv run mwb rebuild-index --output .mechanism/workbench.rebuilt.sqlite
uv run mwb repair-index --output .mechanism/workbench.repaired.sqlite
```

For adapter-sensitive changes, run relevant conformance checks:

```bash
uv run mwb adapter conformance transformer-lens --model EleutherAI/pythia-70m-deduped --device cpu
uv run mwb adapter conformance saelens --model EleutherAI/pythia-70m-deduped --hook blocks.2.hook_resid_post --device cpu
```

Optional backend integrations should fail clearly when missing and must not silently degrade into fake success.

## Non-negotiable implementation rules

Do not introduce:

* production mocks presented as real backends;
* dummy scientific outputs;
* fake success receipts;
* return-code-only validation;
* fixture-only claim-bearing acceptance;
* dry-run evidence promotion;
* schema-only completion;
* silent fallback from execution to dry-run;
* hidden failed controls;
* hidden contradictory evidence;
* automatic latest resolution that treats dry-run output as evidence;
* broad adapter wrappers without conformance tests;
* notebook capture that slows exploration or hashes giant tensors by default.

A feature is not complete merely because a file exists, a command returns output, or a card renders. It is complete only when the relevant workflow is artifact-backed, test-covered, documented, and honest about claim boundaries.

## Roadmap

Near-term priorities:

1. keep the IPython scratch workflow low-friction;
2. make agent-facing state compact and machine-readable;
3. strengthen safe latest-run semantics;
4. close real backend execution loops only where artifact validation and conformance are real;
5. preserve the distinction between diagnostic, association, causal-test, and claim-bearing states;
6. expand adapters only after core evidence behavior is stable;
7. keep context compaction and ledgers current enough for future agents or researchers to resume.

Longer-term directions include richer notebook promotion workflows, broader backend integration, more reference mechanisms, stronger run diffing, multi-run comparison, and better agent handoff files.

## License

See `LICENSE`.
