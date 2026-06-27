# Adapter Guide

Mechanistic Workbench adapters are thin, audited boundaries over external tools, artifact sources, and optional backend integrations.

Adapters do not replace backend libraries. They do not make diagnostic metadata into claim-bearing evidence. They do not define MWB’s core ontology. They map external capabilities or artifacts into explicit MWB contracts.

## Adapter Boundary

MWB core owns:

* project/workspace initialization;
* IPython-native scratch capture;
* typed mechanistic objects and refs;
* run manifests;
* artifact contracts and validation reports;
* control metrics and blocker reports;
* scientific debt;
* MechanismCards and claim grammar;
* evidence graph rebuild/query;
* Git-visible research ledgers;
* adapter protocol, registry, and generic dispatch.

Adapters own:

* external artifact shapes;
* external backend command templates;
* external output mapping;
* source-specific validation;
* source-specific capability checks;
* source-specific conformance checks;
* integration tests.

Adapter identity is provenance metadata. It is not a core run type and does not upgrade evidence by itself.

## Registry Commands

Adapter registry commands separate static adapter metadata from source-specific capability checks.

List registered adapters:

```bash
uv run mwb adapters list --json
```

Inspect static adapter metadata:

```bash
uv run mwb adapters inspect generic-bundle --json
uv run mwb adapters inspect self-ground --json
```

Check whether a specific source path can be ingested:

```bash
uv run mwb adapters can-ingest generic-bundle tests/fixtures/generic_runs/control_leak --json
uv run mwb adapters can-ingest self-ground /path/to/self-ground/runs/<run-id> --json
```

Ingest an external artifact source through the generic dispatcher:

```bash
uv run mwb ingest external generic-bundle tests/fixtures/generic_runs/control_leak
uv run mwb ingest external self-ground /path/to/self-ground/runs/<run-id>
```

Adapter inspection and source capability checks are intentionally separate:

```text
inspect     -> static adapter metadata
can-ingest  -> source-specific ingest capability
ingest      -> map external artifacts into generic MWB artifacts
conformance -> backend capability and evidence posture checks
```

## Built-In Ingest Adapters

| Adapter          | Dependency posture       | Main purpose                                                         | Claim-bearing |
| ---------------- | ------------------------ | -------------------------------------------------------------------- | ------------- |
| `generic-bundle` | built in                 | import MWB-shaped artifact bundles                                   | no            |
| `self-ground`    | optional dogfood adapter | import selected SELF-GROUND run artifacts into generic MWB contracts | no            |

## Generic Bundle Adapter

`generic-bundle` imports MWB-shaped artifact bundles that already contain generic contracts such as:

```text
run_manifest.json
control_metrics.json
blocker_report.json      # optional but recommended
scientific_debt.json     # optional
mechanism_card.json      # optional source artifact; generated card is authoritative after ingest
```

Use it for neutral tests, examples, and external tools that already emit MWB-compatible artifact bundles.

Example:

```bash
uv run mwb adapters inspect generic-bundle --json
uv run mwb adapters can-ingest generic-bundle tests/fixtures/generic_runs/control_leak --json
uv run mwb ingest external generic-bundle tests/fixtures/generic_runs/control_leak
```

After ingest:

```bash
uv run mwb card latest
uv run mwb diagnose latest
uv run mwb next-probe latest --materialize
uv run mwb graph rebuild
```

Generic-bundle ingest must remain non-claim-bearing by default. It may preserve or derive blockers, cards, next probes, and graph inputs, but it must not convert imported artifacts into stronger evidence than their validated content supports.

## Optional Dogfood Adapter

SELF-GROUND is available only as an optional dogfood adapter.

```bash
uv run mwb adapters inspect self-ground --json
uv run mwb adapters can-ingest self-ground /path/to/self-ground/runs/<run-id> --json
uv run mwb ingest self-ground /path/to/self-ground/runs/<run-id>
uv run mwb ingest external self-ground /path/to/self-ground/runs/<run-id>
```

The `ingest self-ground` command is a convenience alias. It routes through the same generic adapter dispatcher as `ingest external self-ground`.

This adapter is useful for dogfooding MWB against real mechanistic-interpretability artifacts, but MWB does not depend on SELF-GROUND and is not a SELF-GROUND-specific codebase.

SELF-GROUND-specific artifact schemas, filenames, metric mappings, source validation, and run-shape assumptions must remain under:

```text
src/mwb/adapters/self_ground/
tests/adapters/test_self_ground_*.py
docs/adapters/self_ground/
docs/archive/
```

Generic docs, generic tests, and core modules must not use SELF-GROUND terminology as default product identity.

## Backend Conformance

Backend conformance commands remain under the singular `adapter` namespace:

```bash
uv run mwb adapter conformance transformer-lens --model EleutherAI/pythia-70m-deduped --device cpu
uv run mwb adapter conformance saelens --model EleutherAI/pythia-70m-deduped --hook blocks.2.hook_resid_post --device cpu

uv run mwb adapter conformance nnsight --model gpt2 --module-path transformer.h.0.mlp --dry-run
uv run mwb adapter conformance pyvene --model gpt2 --module-path transformer.h.0.mlp --dry-run
uv run mwb adapter conformance neuronpedia --model-id gemma-2-2b --sae-id 20-gemmascope-res-16k --feature-index 123 --dry-run
```

Every adapter conformance command writes under:

```text
.mechanism/adapters/<adapter>/
```

Typical conformance artifacts include:

```text
manifest.json
version_manifest.json
conformance_result.json
limitations.json
```

Conformance distinguishes:

```text
unsupported
diagnostic-only
claim-bearing candidate
claim-bearing
```

A successful import is not a valid backend. A valid backend is not automatically claim-bearing. A claim-bearing backend does not make every run claim-bearing.

## Adapter Capability Matrix

| Adapter            | Dependency posture                       | Main purpose                                                               | Claim-bearing                                                 |
| ------------------ | ---------------------------------------- | -------------------------------------------------------------------------- | ------------------------------------------------------------- |
| `generic-bundle`   | built in                                 | import MWB-shaped artifact bundles                                         | no                                                            |
| `transformer-lens` | required P0 dependency                   | model load, hook identity, activation capture                              | yes, after full conformance pass and run-level evidence gates |
| `saelens`          | required P0 dependency                   | SAE identity, hook compatibility, feature refs                             | yes, after full conformance pass and run-level evidence gates |
| `nnsight`          | optional P1 dependency                   | HF-exact tracing/intervention target, nnterp naming when installed         | no by default                                                 |
| `pyvene`           | optional P1 dependency                   | intervention API availability and version/target metadata when installed   | no by default                                                 |
| `neuronpedia`      | optional network/read-only metadata path | feature metadata lookup and provenance pointers                            | no                                                            |
| `self-ground`      | optional dogfood adapter                 | import selected external run artifacts into generic MWB artifact contracts | no                                                            |

## Artifact Pointer Support

MWB may record artifact pointers without dereferencing large external stores.

Supported pointer types may include:

```text
Git LFS pointer
DVC pointer
git-annex pointer
external file path pointer
```

Pointer recording does not make an artifact available for claim-bearing evidence unless the downstream workflow validates the required artifact content.

## Claim-Bearing Boundary

Adapters can contribute to evidence only through explicit MWB artifacts.

A claim-bearing run requires, at minimum:

* real or external execution artifacts;
* explicit run manifest;
* validated required artifacts;
* control metrics;
* blocker report;
* scientific debt visibility;
* policy-profile compatibility;
* MechanismCard generation;
* claim grammar compatibility;
* no hidden failed controls;
* no silent fallback to dry-run.

The following never upgrade evidence by themselves:

* adapter inspection;
* adapter source capability checks;
* missing optional dependency diagnostics;
* schema-only success;
* fixture-only outputs;
* dry-run plans;
* command return code `0`;
* card rendering;
* graph edge creation.

## Regression Rules

Do not add broad adapter wrappers without conformance tests.

Do not silently degrade from real execution to dry-run.

Do not report unsupported optional dependencies as working backends.

Do not make dogfood adapter names part of generic project identity.

Do not allow adapter-specific schemas to leak into core run/card/claim/graph logic.

SELF-GROUND terms are allowed only in:

```text
src/mwb/adapters/self_ground/
tests/adapters/test_self_ground_*.py
docs/adapters/self_ground/
docs/archive/
bounded optional adapter sections in README.md and docs/USAGE.md
explicit backward-compatibility tests
```

All other appearances are boundary violations unless explicitly justified.
