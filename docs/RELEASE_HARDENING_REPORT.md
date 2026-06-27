# Release Hardening Report

This report records the release-hardening gate for the world-class buildout.

## Phase 25 — Prior Baseline

Phase 25 hardened the local workbench after the evidence graph, ledgers,
hypothesis lifecycle, static compiler, causal verification, example geometry,
diagnosis/probes, reference mechanisms, claim grammar, policy profiles, and
adapter expansion phases.

Prior QC gate passed:

- `uv run pytest`: `119 passed, 3 skipped`
- Graph rebuild: `30` edges, `23` nodes, `7` relation kinds.
- `uv run mwb doctor`: `status: ok`.
- Adapter manifest check: `adapter_manifests: 5`
- Backend version check: `backend_versions: 5`

## Phase 26 — MWB Identity and Generic Adapter Boundary Hardening

### Scope

This pass completes the repo-wide hardening so that:

- MWB is the product.
- `generic-bundle` is the neutral ingest path for MWB-shaped artifacts.
- SELF-GROUND remains an optional dogfood adapter.
- Generic code, generic docs, generic tests, and default workflows do not
  depend on SELF-GROUND identity.
- Adapter ingestion never upgrades evidence by itself.

### What Changed

**Documentation (pre-existing; reviewed for consistency):**
- `README.md` was updated before this pass. Residual SELF-GROUND references in
  generic sections were removed during this pass (lines 14, 66, 100, 712, 730).
  Old SELF-GROUND-centric workflow sections replaced with:
  - Generic-bundle ingest workflow section
  - `## Optional Dogfood Adapter: SELF-GROUND` section (bounded)
  - `init --name mwb-demo` replacing `--name self-ground` in examples
  - `negation_demo_calibrated` replacing `negation_phase3_calibrated`
- `docs/USAGE.md` reviewed; no edits required.
- `docs/ADAPTERS.md` reviewed; no edits required.
- `docs/buildout/README.md` reviewed; no edits required.

**Generic bundle adapter (`src/mwb/adapters/generic_bundle.py`):**
- Strict validation for `run_manifest.json`: required to be valid JSON object
  containing `run_ref`; fails explicitly if missing.
- Strict validation for `control_metrics.json`: required to be valid JSON object
  containing `target_delta` and `matched_control_delta`; fails with actionable
  error per missing field.
- Optional artifact validation: `blocker_report.json`, `scientific_debt.json`,
  `mechanism_card.json` must be valid JSON objects if present; rejected with
  clear error otherwise.
- Adapter provenance (`source_kind`, `adapter_id`, `adapter_display_name`,
  `claim_bearing=False`) always written; cannot be inherited from source.
- `shutil.copyfile` for `scientific_debt.json` replaced with explicit rewrite.

**Scientific debt rewrite (`_rewrite_scientific_debt`):**
- Rewrites top-level `run_ref` to new run ref.
- Rewrites top-level `parents` if present.
- Rewrites `mechanism_card_ref` if it embeds the old run ref.
- Rewrites per-item `debt_ref` if it embeds the old run ref.
- Sets `claim_bearing=False` on imported debt.
- Raises `ValueError` if items or parents are not the expected types.

**Blocker report rewrite (`_rewrite_blocker_report`):**
- Always regenerates `wb_ref` to remove old run identity embedding.
- Rewrites `run_ref` and `parents` to new run ref.

**Package metadata (`pyproject.toml`):**
- Description updated: "adapter-backed execution" → "adapter-backed ingestion
  and explicitly validated execution paths".

**Boundary test (`tests/adapters/test_self_ground_boundary.py`):**
- Added `phase3_calibrated` to FORBIDDEN terms.
- Added `docs/ADAPTERS.md` and `docs/buildout/` to ALLOWED_PREFIXES.
- Added `## Adapter Registry` as an allowed section in `docs/USAGE.md`.
- Added allowed line patterns for USAGE.md adapter QC test references.
- Added regression assertion that README does not contain forbidden identities
  outside allowed sections.

**Generic bundle tests (`tests/adapters/test_generic_bundle_ingest.py`):**
All required tests implemented (no mocking; real filesystem fixtures):
- `test_generic_bundle_rejects_missing_run_manifest`
- `test_generic_bundle_rejects_missing_control_metrics`
- `test_generic_bundle_rejects_invalid_run_manifest_json`
- `test_generic_bundle_rejects_non_object_run_manifest`
- `test_generic_bundle_rejects_missing_run_ref`
- `test_generic_bundle_rejects_invalid_control_metrics_json`
- `test_generic_bundle_rejects_non_object_control_metrics`
- `test_generic_bundle_rejects_missing_required_control_metrics`
- `test_generic_bundle_rewrites_stale_blocker_report_refs`
- `test_generic_bundle_rewrites_stale_scientific_debt_refs`
- `test_generic_bundle_rejects_bad_blocker_report_json`
- `test_generic_bundle_rejects_non_object_blocker_report`
- `test_generic_bundle_rejects_invalid_scientific_debt_json`
- `test_generic_bundle_rejects_non_object_scientific_debt`
- `test_generic_bundle_ingest_remains_non_claim_bearing`
- `test_generic_bundle_ingest_supports_card_diagnose_next_probe_graph`
- `test_unknown_adapter_error_includes_available_adapter_ids`
- `test_can_ingest_failure_does_not_make_inspect_unavailable`
- `test_ingest_external_generic_bundle_routes_through_registry`
- `test_adapters_list_does_not_depend_on_order`

## QC Results

### Leak Scan

```
rg -n "SELF-GROUND|self-ground|self_ground|E004|e004_specificity_rescue_matrix|run_self_ground|/self-ground|ml_research/self-ground|negation_phase3|phase3_calibrated" README.md docs src tests pyproject.toml
```

Remaining hits — all allowed:

| File | Reason |
|------|--------|
| `README.md` | Only in `## Optional Dogfood Adapter: SELF-GROUND` (bounded) |
| `docs/ADAPTERS.md` | Adapter guide; explicitly covers both adapters by design |
| `docs/USAGE.md` | Only in `## Adapter Registry` and `## Optional Dogfood Adapter` sections |
| `docs/buildout/README.md` | Build plan; references the scan pattern itself |
| `docs/adapters/self_ground/` | Allowed location |
| `src/mwb/adapters/self_ground/` | Allowed location |
| `src/mwb/adapters/registry.py` | Explicit import line (allowed pattern) |
| `tests/adapters/` | Allowed location |

No hit appears in generic source, generic tests outside adapter tests, generic
top-level docs outside bounded sections, or package metadata.

### Full QC

- `uv sync`: passed.
- `uv run ruff check .`: passed (`All checks passed!`).
- `uv run pytest`: passed (`154 passed, 3 skipped`).
- `uv run mwb doctor`: passed (`status: ok`).
- `uv run mwb graph rebuild`: passed (`49 edges, 32 nodes, 7 relation kinds`).
- `uv run mwb ledger validate`: passed (`status: ok`).

### Adapter Commands

- `uv run mwb adapters list --json`: passed; both `generic-bundle` and
  `self-ground` listed.
- `uv run mwb adapters inspect generic-bundle --json`: passed; `status: available`.
- `uv run mwb adapters can-ingest generic-bundle tests/fixtures/generic_runs/control_leak --json`: passed; `status: available`.
- `uv run mwb ingest external generic-bundle tests/fixtures/generic_runs/control_leak`: passed; `run_ref: run_external_generic_run_demo_control_leak`, `primary_blocker: control_leaky`.

### Adapter Tests

- `uv run pytest tests/adapters/test_generic_bundle_ingest.py`: `23 passed`.
- `uv run pytest tests/adapters/test_self_ground_boundary.py`: `3 passed`.
- `uv run pytest tests/adapters/test_self_ground_ingest.py`: `9 passed`.

### Optional Real Integration

Not run in this environment — TransformerLens/SAELens model downloads and GPU
availability not present. Explicitly environment-gated, not relabelled as
passed.

## Scan Policy

No scan hit represents a live fake backend path, smoke-only acceptance, or an
unqualified paper-facing mechanism claim.

The boundary test (`test_self_ground_terms_do_not_appear_in_generic_surfaces`)
enforces the allowed/forbidden surface automatically on every test run.

## Residual Risk

Optional nnsight and pyvene dependencies are not installed in the current QC
environment. Their adapters remain diagnostic-only unless a user installs and
configures those backends for real conformance.

Optional real adapter integration tests require `MWB_RUN_REAL_ADAPTER_TESTS=1`
and a compatible GPU/CPU environment with model and SAE access.

## Phase 26 Follow-up — Boundary Hardening Patch

### What Changed

**Boundary allowlist tightened (`tests/adapters/test_self_ground_boundary.py`):**
- `docs/ADAPTERS.md` is no longer whole-file allowed. Each permitted line is
  named explicitly in `ALLOWED_LINE_PATTERNS["docs/ADAPTERS.md"]`.
- `docs/buildout/` is no longer whole-directory allowed. Permitted lines are
  named explicitly in `ALLOWED_LINE_PATTERNS["docs/buildout/README.md"]`.
- `## Adapter Registry` section of `docs/USAGE.md` is no longer a stripped
  section. Instead, the three permitted self-ground CLI lines are named
  explicitly in `ALLOWED_LINE_PATTERNS["docs/USAGE.md"]`.
- Added `test_active_docs_do_not_contain_forbidden_default_identity_patterns`
  to assert that all four active docs (README.md, USAGE.md, ADAPTERS.md,
  buildout/README.md) are free of forbidden regression patterns outside bounded
  sections.

**Buildout README updated (`docs/buildout/README.md`):**
- The rg scan-pattern code block that spelled out all forbidden strings verbatim
  was replaced with a reference to the automated boundary test.

**Residual stale-ref detection added (`src/mwb/adapters/generic_bundle.py`):**
- `_find_stale_ref_paths(value, needle, *, exclude, path)` recursively scans
  dicts/lists/strings for `needle`, masking out `exclude` before checking so
  that occurrences of `old_run_ref` that only appear as part of `new_run_ref`
  are not falsely flagged.
- `_rewrite_scientific_debt()` calls `_find_stale_ref_paths` with
  `exclude=new_run_ref` after all known-field rewrites. Raises `ValueError`
  with field path(s) if any residual stale ref is found.
- `_rewrite_blocker_report()` calls `_find_stale_ref_paths` with
  `exclude=run_ref` after regenerating `wb_ref`. Raises `ValueError` with
  field path(s) if any residual stale ref is found.

**Optional `mechanism_card.json` behavior clarified:**
- Comment added to `validate_source()` making clear that `mechanism_card.json`
  is accepted only as a validatable source artifact; MWB regenerates the
  authoritative MechanismCard via `card_from_run()` after ingest; the source
  card does not become authoritative and does not upgrade evidence posture.

**New tests (`tests/adapters/test_generic_bundle_ingest.py`):**
- `test_generic_bundle_rejects_unrewriteable_stale_debt_refs`: ingest of
  scientific_debt.json with stale ref in an unknown field (evidence_ref) raises
  ValueError with "stale source run ref".
- `test_rejects_unrewriteable_stale_debt_refs_error_names_field_path`: error
  message names the residual field path.
- `test_generic_bundle_rejects_unrewriteable_stale_blocker_report_refs`: ingest
  of blocker_report.json with stale ref in an unknown field (source_artifact)
  raises ValueError.
- `test_find_stale_ref_paths_helper`: direct unit test of the helper covering
  masking, empty needle, clean payload, and the exclude parameter.

### QC Results (Phase 26 Follow-up)

- `uv sync`: passed.
- `uv run ruff check .`: passed (`All checks passed!`).
- `uv run pytest`: `158 passed, 3 skipped`.
- `uv run mwb doctor`: passed (`status: ok`).
- `uv run mwb graph rebuild`: passed (`63 edges, 39 nodes, 7 relation kinds`).
- `uv run mwb ledger validate`: passed (`status: ok`).

### Adapter Command Results

- `uv run mwb adapters list --json`: both `generic-bundle` and `self-ground` listed.
- `uv run mwb adapters inspect generic-bundle --json`: `status: available`.
- `uv run mwb adapters can-ingest generic-bundle tests/fixtures/generic_runs/control_leak --json`: `status: available`.
- `uv run mwb ingest external generic-bundle tests/fixtures/generic_runs/control_leak`: `run_ref: run_external_generic_run_demo_control_leak`, `primary_blocker: control_leaky`.

### Adapter Test Results

- `uv run pytest tests/adapters/test_generic_bundle_ingest.py`: `27 passed`.
- `uv run pytest tests/adapters/test_self_ground_boundary.py`: `3 passed`.
- `uv run pytest tests/adapters/test_self_ground_ingest.py`: `9 passed`.

### Optional Real Integration

Not run — environment-gated, not relabelled as passed.
