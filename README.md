<p align="center">
  <img src="assets/mwb-readme.webp" alt="Mechanistic Workbench" width="800">
</p>

<p align="center">
  <a href="https://github.com/nshkrdotcom/mwb"><img src="https://img.shields.io/badge/GitHub-nshkrdotcom%2Fmwb-181717?logo=github" alt="GitHub repository"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-blue.svg" alt="MIT License"></a>
</p>

# Mechanistic Workbench

Mechanistic Workbench (`mwb`) is a local-first, IPython-native research workbench for mechanistic interpretability.

It is designed to sit between exploratory notebook work and claim-bearing mechanistic evidence. The goal is not to replace TransformerLens, SAELens, nnsight, pyvene, or other scientific execution libraries. The goal is to give local mechanistic-interpretability work a durable research state:

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
* generic-bundle and optional adapter ingest paths;
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

* a replacement for TransformerLens, SAELens, nnsight, pyvene, or similar execution libraries;
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
uv run mwb init --name mwb-demo
uv run mwb doctor
```

This creates the local workbench workspace under `.mechanism/`.

## Quick start

A minimal local loop:

```bash
uv sync
uv run mwb init --name mwb-demo
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
uv run mwb init --name mwb-demo
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

### Generic-bundle ingest workflow

```bash
uv run mwb ingest external generic-bundle tests/fixtures/generic_runs/control_leak
uv run mwb card latest
uv run mwb diagnose latest
uv run mwb next-probe latest
uv run mwb next-probe latest --materialize
uv run mwb graph rebuild
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
uv run mwb bundle audit negation_demo_calibrated
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

## Optional Dogfood Adapter: SELF-GROUND

SELF-GROUND is an optional dogfood adapter. MWB does not depend on SELF-GROUND and is not a SELF-GROUND-specific codebase.

When SELF-GROUND run artifacts are available, ingest them with:

```bash
uv run mwb ingest self-ground /path/to/self-ground/runs/<run-id>
uv run mwb ingest external self-ground /path/to/self-ground/runs/<run-id>
```

Both routes go through the same adapter registry dispatcher.

After ingest:

```bash
uv run mwb card latest
uv run mwb diagnose latest
uv run mwb next-probe latest --materialize
uv run mwb graph rebuild
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

1. **Close one complete real execution loop.** The first major target is an end-to-end workflow where MWB can diagnose a blocked run, generate the next probe, materialize it, execute it through a real backend, validate the resulting artifacts, ingest the outputs, update the evidence graph, regenerate a claim-safe card, and produce the next concrete action.

2. **Keep the IPython scratch workflow low-friction.** Human research should remain fast, exploratory, and notebook-friendly. MWB should preserve scratch work through passive capture and useful context, without forcing every cell, plot, failed attempt, or hunch into formal project ceremony.

3. **Support retrospective promotion from scratch work to formal evidence.** Notebook and IPython exploration should be promotable when it becomes useful: selected cells, artifacts, runs, or notes should be convertible into hypotheses, probes, evidence-linked artifacts, or claim-relevant records. Scratch work should motivate formal work, not automatically become formal evidence.

4. **Make agent-facing state compact and machine-readable.** Agents should be able to ask MWB what is currently true, what is blocked, what the latest real execution is, what artifacts are missing, what language is allowed, what language is forbidden, and what exact action should happen next. Core commands should expose stable JSON suitable for tool-calling agents.

5. **Add first-class agent status and next-action workflows.** MWB should provide explicit commands for agent status, diagnosis, next-probe generation, probe execution, card generation, claim checks, and context compaction. These commands should return enough structured information for an agent to continue without rereading notebooks, terminal logs, or scattered project notes.

6. **Strengthen safe latest-run semantics.** `latest` should never be ambiguous when evidence is involved. MWB should distinguish latest-any, latest-dry-run, latest-diagnostic, latest-real-execution, latest-artifact-validated, and latest-claim-bearing-candidate. Commands that require real evidence should fail or warn when the selected run is weaker than required.

7. **Separate operational status, evidence posture, and claim permission.** A command can complete successfully without producing usable scientific evidence. A backend can execute successfully while artifacts are incomplete. A diagnostic result can be scientifically useful without being claim-bearing. MWB should keep dry-run, diagnostic, real-executed, artifact-validated, causal-test, controlled-causal-test, and claim-bearing-candidate states visibly separate.

8. **Stabilize typed run and artifact contracts.** Runs should have clear manifests, execution requests, execution receipts, backend manifests, artifact validation reports, blocker reports, scientific debt records, evidence edges, and mechanism cards. Missing files should have explicit meaning: not applicable, optional, missing because dry-run, missing because backend failed, or missing because the implementation is incomplete.

9. **Implement strict artifact validation.** Scientific status should come from validated artifact content, not command success. MWB should validate required files, required fields, control metrics, intervention receipts, blocker reports, and claim-impacting artifacts before allowing stronger evidence posture or stronger claim language.

10. **Build a configurable but strict optional adapter execution bridge.** MWB should call optional adapter backends through explicit command templates and typed execution requests. The bridge should capture the command, arguments, working directory, environment summary, git identity, stdout, stderr, return code, start/end time, duration, produced paths, and validation results. It should never fake execution, write dummy success artifacts, silently fall back to dry-run, or treat return code `0` as scientific success.

11. **Execute one real supported probe class before broadening scope.** The first real backend loop should support one concrete probe type well, such as a smallest-axis-extension / sweep-style follow-up, rather than presenting many superficial probe types that only work as dry-runs.

12. **Map backend outputs back into MWB state.** Real backend outputs should be located deterministically, validated, copied or referenced as source artifacts, indexed, linked to the originating probe, and reflected in the evidence graph, blocker reports, scientific debt, cards, and next actions.

13. **Make evidence graph semantics precise.** MWB should distinguish provenance from support. Edges such as derived-from, depends-on, tested-by, supports, contradicts, confounded-by, fails-on, and generalizes-to should have clear meanings. A materialized probe, successful dry-run, or successful command with invalid artifacts should not create a support edge.

14. **Treat claim checks as scientific test gates.** Claim and draft validation should behave like tests: a claim fails with explicit blockers, MWB identifies the missing artifact or control, recommends the next action, the agent runs the probe, artifacts are validated, and the claim is either still blocked or narrowly allowed. Claim grammar should be an active guardrail, not just a reporting feature.

15. **Make blocked claims actionable.** A useful failure should say what is blocked, why it is blocked, which artifact or control is missing, what command or probe would address it, and what weaker language remains allowed. Blockers should produce next diagnostic paths where possible, not just dead-end status labels.

16. **Preserve scientific debt explicitly.** MWB should distinguish implementation TODOs from scientific debt. Scientific debt should record the specific reason stronger claims are blocked, such as leaky controls, incomplete artifacts, insufficient effect size, missing heldout generalization, metadata mismatch, or unsupported backend capability.

17. **Carry policy profiles through runs.** Strictness settings should be explicit and copied into run manifests so future changes to project policy do not rewrite history. Dry-run claim-bearing should remain forbidden, artifact validation should remain required, and stronger claims should require the relevant controls and validation gates.

18. **Harden backend and adapter conformance.** Backend integrations should have explicit capability reports, dependency identity, model identity, SAE identity where relevant, hook or space compatibility checks, artifact schemas, failure-mode tests, and integration tests. Unsupported or diagnostic-only adapters should not be allowed to raise evidence tier.

19. **Expand adapters only after the core evidence loop is stable.** TransformerLens, SAELens, nnsight, pyvene, Neuronpedia, SAEBench, ACDC, EAP, Tracr, or other integrations should be added or promoted only when their real capabilities, artifacts, identities, and conformance behavior are clear. Optional dogfood adapters follow the same rule. Adapter breadth should not come before one reliable evidence loop.

20. **Improve CLI and research UX without turning MWB into ceremony.** The CLI should be the actuator layer for agents and reproducible workflows, not the primary mental model for human researchers. Commands should improve real execution, artifact validation, claim safety, state compaction, next-action quality, run comparison, or failure diagnosis. They should not make humans manually do bookkeeping MWB can infer or capture.

21. **Harden command output and error messages.** Relevant commands should report execution status, evidence posture, claim-bearing status, primary blocker, next command, warnings, and missing artifacts. Errors should be structured for unsupported probe kinds, missing backends, failed conformance, dry-run latest selection, incomplete artifacts, and missing context files.

22. **Improve probe materialization UX.** Materialized probes should say where the probe file is, whether it is runnable, what dry-run command exists, what real execution command exists if supported, what artifacts are expected, whether claim-bearing evidence is possible, and why execution is blocked if unsupported.

23. **Keep IPython helpers aligned with safe workflow semantics.** IPython helpers should make it easy to inspect runs, diagnose blockers, view cards, create notes, request next probes, and launch supported probe workflows while still making scratch-vs-formal and dry-run-vs-real distinctions visible.

24. **Make persistence rebuildable from artifacts.** The local SQLite index should be treated as an operational index, not the source of truth. MWB should be able to rebuild or repair the index from artifact files, sessions, runs, ledgers, evidence edges, cards, and manifests.

25. **Use atomic writes for important local artifacts.** Critical files such as manifests, execution requests, execution receipts, artifact validation reports, evidence graph outputs, ledgers, and context files should be written safely enough for local-first research work.

26. **Keep ledgers and context compaction current.** MWB should maintain run ledgers, claim ledgers, decision logs, blocker reports, scientific debt, current context, phase status, open questions, and agent resume prompts. A future researcher or agent should be able to resume from canonical state rather than reconstructing the project from memory.

27. **Add compact change and run-diff reporting.** Agents should not have to reread the entire repo or all artifacts after each step. MWB should summarize what changed, what became stronger or weaker, what blockers were added or resolved, whether claim language changed, and what should run next.

28. **Support exportable evidence bundles.** MWB should eventually produce portable bundles containing manifests, policy snapshots, artifact references or copies, hashes, evidence graph state, cards, and claim constraints so work can be reviewed or handed off without relying on ambient local context.

29. **Preserve backward compatibility with existing runs.** Older ingested or dry-run artifacts should remain readable. Missing newer execution files should be classified correctly rather than silently rewritten or treated as evidence.

30. **Expand reference mechanisms and benchmark-style examples.** Once the real execution and evidence semantics are stable, MWB should include more reference mechanisms and known example workflows that exercise artifact validation, claim checks, blocker derivation, and evidence graph behavior.

31. **Improve report and paper-facing provenance only after evidence behavior is reliable.** Drafting workflows should help cite artifacts, cards, claims, and evidence constraints without overclaiming. Paper-facing tools should not become a way to launder weak evidence into stronger language.

32. **Add broader notebook promotion and provenance features later.** Richer notebook capture, larger object provenance, session browsing, cell selection, artifact promotion, and formalization workflows are useful longer-term directions, but they should not delay the real backend loop.

33. **Add deeper multi-run comparison.** Longer-term MWB should compare runs across axes, models, layers, hooks, controls, prompt sets, and probe types; identify regressions or strengthened evidence; and summarize what changed scientifically rather than only what changed operationally.

34. **Add UI layers only after the state model is trustworthy.** A UI may eventually be useful for browsing runs, blockers, evidence graphs, cards, sessions, and next actions. It should come after the underlying artifacts, graph semantics, validation, and claim gates are dependable.

35. **Keep release hardening continuous.** Each completed phase should keep tests green, preserve real integration paths, update documentation, update compact context, and avoid fake progress. Unit fixtures are acceptable for coverage, but fixture-only paths must not satisfy scientific or claim-bearing acceptance.

Longer-term, MWB should become a local-first research operating layer for mechanistic interpretability: fast enough for human scratch work, strict enough for agent execution, durable enough for long-running projects, and disciplined enough that scientific claims remain tied to real artifacts, validated controls, explicit blockers, and reproducible execution history.

## License

See `LICENSE`.
