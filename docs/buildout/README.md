# MWB Buildout

This is the active generic buildout direction for Mechanistic Workbench. It supersedes historical phase reports and source-mining notes kept under `docs/archive/`.

The repository already has the right high-level shape: MWB core, adapter protocol, generic-bundle ingest, optional dogfood adapter support, Git-visible ledgers, evidence graph tooling, claim checks, MechanismCards, reference benchmarks, and boundary tests.

The current buildout task is to harden that shape so the repo consistently presents and enforces the intended product boundary:

```text
MWB is the product.

Dogfood adapters are optional integrations.

Generic code, generic docs, generic tests, and default workflows must not depend on dogfood adapter identity.
```

## Product Boundary

MWB core remains responsible for:

* project/workspace initialization;
* IPython-native scratch capture;
* typed mechanistic objects and stable refs;
* session provenance;
* artifact contracts and validation reports;
* run manifests;
* control metrics;
* blocker reports;
* scientific debt;
* MechanismCards;
* claim grammar and Draft Guard;
* evidence graph rebuild/query;
* Git-visible research ledgers;
* safe latest-run semantics;
* adapter protocol, registry, and generic dispatch;
* claim-bearing boundaries.

Adapters remain responsible for:

* external artifact shapes;
* external backend command templates;
* external output mapping;
* source-specific validation;
* source-specific capability checks;
* source-specific conformance checks;
* dependency/version identity;
* integration tests;
* source-specific docs.

Adapter identity is provenance metadata. It is not a core run type and must not upgrade evidence by itself.

## Current Active Priorities

### 1. Keep public identity MWB-first

The README and active docs should introduce Mechanistic Workbench as a local-first, IPython-native research workbench for mechanistic interpretability.

Active docs should emphasize:

* scratch-first research;
* typed workbench objects;
* session provenance;
* run artifacts;
* evidence graph edges;
* blockers and scientific debt;
* next probes;
* MechanismCards;
* claim grammar;
* Git-visible ledgers;
* adapter-backed ingestion/conformance;
* explicitly validated execution paths where implemented.

Active docs should not define the product through any dogfood adapter or external experiment repository.

### 2. Keep generic examples generic

Default examples should use:

```text
mwb-demo
generic-bundle
run_external_generic_*
negation_demo_calibrated
tests/fixtures/generic_runs/control_leak
docs/fixtures/runs/control_leaky
```

Default examples should not use dogfood run IDs, dogfood local paths, or adapter-specific artifact names.

The built-in negation demo is allowed as a compact MWB demo bundle. It is not the product identity.

### 3. Keep dogfood adapters optional

Dogfood adapters are useful for validating MWB against real mechanistic-interpretability artifacts. They must remain optional integrations.

Adapter-specific docs belong under:

```text
docs/adapters/<adapter>/
```

Adapter-specific implementation belongs under:

```text
src/mwb/adapters/<adapter>/
```

Adapter-specific tests belong under:

```text
tests/adapters/
```

Historical source-mining notes and phase reports belong under:

```text
docs/archive/
```

### 4. Harden generic-bundle ingest

`generic-bundle` is the neutral ingest path for MWB-shaped artifact bundles. It should be strong enough to support tests, examples, and external tools that already emit generic MWB contracts.

Required generic-bundle behavior:

* validate `run_manifest.json`;
* validate `control_metrics.json`;
* reject invalid JSON;
* reject non-object JSON;
* require `run_manifest.run_ref`;
* require or explicitly default `status`;
* require or explicitly default `evidence_posture`;
* force `claim_bearing=false` during adapter ingest;
* record adapter provenance;
* validate optional `blocker_report.json`;
* validate optional `scientific_debt.json`;
* rewrite or reject stale refs in optional imported artifacts;
* generate or refresh next-probe and MechanismCard artifacts after ingest;
* preserve non-claim-bearing posture unless a future explicit evidence gate supports stronger posture.

### 5. Keep evidence posture conservative

A command can succeed without producing usable scientific evidence.

The following must not upgrade evidence by themselves:

* adapter inspection;
* source capability checks;
* successful ingest;
* dry-run output;
* diagnostic-only output;
* schema-only validation;
* fixture-only output;
* command return code `0`;
* graph edge creation;
* card rendering.

Evidence posture should come from validated artifact content, controls, blockers, policy profiles, and claim grammar.

### 6. Keep latest-run semantics safe

Commands that use `latest` must not silently treat weak output as strong evidence.

Longer-term, MWB should distinguish:

```text
latest-any
latest-dry-run
latest-diagnostic
latest-real-execution
latest-artifact-validated
latest-claim-bearing-candidate
```

Commands that require real evidence should fail or warn when the selected run is weaker than required.

### 7. Keep claim boundaries explicit

Claim checks should behave like scientific tests:

```text
claim fails
  -> blockers are reported
  -> missing evidence is identified
  -> allowed language remains visible
  -> next action is suggested
```

Mechanism language should remain blocked unless the relevant artifact, control, verification, generalization, and policy gates pass.

### 8. Keep IPython scratch work cheap

MWB is IPython-native. It should preserve scratch context without turning every notebook cell into formal evidence.

The capture layer should remain bounded and selective:

* capture typed MWB objects;
* capture session/cell metadata;
* capture bounded stdout/stderr;
* capture exceptions;
* capture lineage edges;
* avoid hashing giant tensors by default;
* avoid slowing exploration.

Scratch work may motivate formal evidence. It does not automatically become formal evidence.

## Active Documentation Set

Active docs should remain MWB-first:

```text
README.md
docs/USAGE.md
docs/ADAPTERS.md
docs/EVIDENCE_GRAPH.md
docs/LEDGERS.md
docs/HYPOTHESIS_LIFECYCLE.md
docs/SPACE_TYPES.md
docs/STATIC_COMPILER.md
docs/CAUSAL_VERIFICATION.md
docs/EXAMPLE_GEOMETRY.md
docs/DIAGNOSIS_AND_PROBES.md
docs/REFERENCE_MECHANISMS.md
docs/CLAIM_GRAMMAR.md
docs/POLICY_PROFILES.md
docs/buildout/README.md
```

Adapter-specific docs should stay adapter-specific:

```text
docs/adapters/
```

Historical docs should stay historical:

```text
docs/archive/
```

Archived docs may contain dogfood terms, old local paths, and previous phase details. They are retained for provenance and do not define the current product identity.

## Active Implementation Scope

The next hardening pass should complete these items.

### README and active docs

* Replace `README.md` with the MWB-first version.
* Update `docs/USAGE.md` to mirror the generic workflow.
* Update `docs/ADAPTERS.md` to make `generic-bundle` the neutral ingest example.
* Keep this buildout document focused on active generic work.
* Keep dogfood adapter material in bounded optional sections only.

### Generic-bundle adapter

* Strengthen `GenericBundleIngestAdapter.validate_source`.
* Validate required manifest fields.
* Validate required control metrics.
* Validate optional blocker/debt/card artifacts.
* Rewrite or reject stale refs in optional imported artifacts.
* Ensure all generic-bundle ingests remain non-claim-bearing by default.
* Add malformed-input tests.

### Boundary tests

* Keep dogfood terms out of generic code, generic docs, generic tests, and package metadata.
* Allow dogfood terms only in adapter paths, archive paths, bounded optional adapter sections, and explicit backward-compatibility tests.
* Ensure the boundary test does not allow all of `README.md` or all of `docs/USAGE.md`.

### Command examples

* Use `mwb-demo` as the default project name.
* Use `generic-bundle` for neutral external ingest examples.
* Use `negation_demo_calibrated` for built-in bundle examples.
* Avoid dogfood local paths in active docs.
* Avoid dogfood run IDs in generic docs.

## Regression Rules

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
* dogfood adapter names as generic product identity.

A feature is not complete merely because a file exists, a command returns output, or a card renders. It is complete only when the relevant workflow is artifact-backed, test-covered, documented, and honest about claim boundaries.

## Required QC

Minimum local QC:

```bash
uv sync
uv run ruff check .
uv run pytest
uv run mwb doctor
uv run mwb graph rebuild
uv run mwb ledger validate
```

Adapter-sensitive QC:

```bash
uv run mwb adapters list --json
uv run mwb adapters inspect generic-bundle --json
uv run mwb adapters can-ingest generic-bundle tests/fixtures/generic_runs/control_leak --json
uv run mwb ingest external generic-bundle tests/fixtures/generic_runs/control_leak

uv run pytest tests/adapters/test_generic_bundle_ingest.py
uv run pytest tests/adapters/test_self_ground_boundary.py
uv run pytest tests/adapters/test_self_ground_ingest.py
```

Optional real integration QC, when the environment supports it:

```bash
MWB_RUN_REAL_ADAPTER_TESTS=1 uv run pytest tests/test_phase4_context.py -m integration
uv run mwb adapter conformance transformer-lens --model EleutherAI/pythia-70m-deduped --device cpu
uv run mwb adapter conformance saelens --model EleutherAI/pythia-70m-deduped --hook blocks.2.hook_resid_post --device cpu
```

Boundary scan:

```bash
# Run the automated boundary scan instead of this grep directly.
# See tests/adapters/test_self_ground_boundary.py for the exact terms and
# allowed-location policy.
uv run pytest tests/adapters/test_self_ground_boundary.py -v
```

Allowed hits only in:

```text
src/mwb/adapters/self_ground/
tests/adapters/test_self_ground_*.py
docs/adapters/self_ground/
docs/archive/
bounded optional adapter sections in README.md and docs/USAGE.md
explicit backward-compatibility tests
explicit adapter registry import lines
```

Every remaining hit must be reported and justified.

## Completion Criteria

This hardening pass is complete only when:

1. README is MWB-first and uses `mwb-demo`.
2. `docs/USAGE.md` mirrors the generic workflow.
3. `docs/ADAPTERS.md` presents `generic-bundle` as the neutral ingest adapter and dogfood adapters as optional.
4. `GenericBundleIngestAdapter` validates required contracts.
5. Imported optional artifacts do not retain stale source refs.
6. Generic-bundle malformed-input tests exist.
7. Boundary tests pass.
8. Leak scan has only allowed hits.
9. Full QC passes.
10. Adapter QC passes.
11. Any skipped real integration gate is explicitly reported as environment-gated, not silently treated as passed.
12. Commit and push are complete.

## Reporting Requirements

The final implementation report should include:

```text
Summary:
- What changed.

Docs:
- README updated.
- USAGE updated.
- ADAPTERS updated.
- buildout README updated.

Generic bundle:
- Validation changes.
- Scientific debt rewrite/validation behavior.
- Malformed-input tests.

Boundary:
- Remaining dogfood-term hits and why allowed.
- Leak scan command and output.

QC:
- uv sync
- ruff
- pytest
- doctor
- graph rebuild
- ledger validate
- adapter tests
- optional real integration if run

Commit:
- commit SHA
- push status
```
