# MWB Buildout

This is the active generic buildout direction for Mechanistic Workbench. It
supersedes historical phase reports kept under `docs/archive/`.

## Product Boundary

MWB core remains responsible for:

- IPython-native scratch capture;
- typed mechanistic objects and refs;
- artifact contracts and validation reports;
- run manifests, control metrics, blocker reports, and scientific debt;
- MechanismCards and claim grammar;
- evidence graph rebuild/query;
- Git-visible research ledgers;
- adapter protocol, registry, and generic dispatch.

Adapters remain responsible for:

- external artifact shapes;
- external backend command templates;
- external output mapping;
- source-specific validation;
- source-specific conformance checks;
- integration tests.

## Near-Term Priorities

1. Broaden neutral MWB fixture coverage for generic ingest, cards, diagnosis,
   graph, and ledger flows.
2. Keep adapter inspection, source capability checks, and ingest dispatch
   separate.
3. Extend backend adapters only when their real capabilities and conformance
   behavior are explicit.
4. Keep dry-run and diagnostic states non-claim-bearing.
5. Keep public docs MWB-first and quarantine dogfood material under adapter or
   archive paths.

## Regression Rules

- Generic docs, generic tests, and core modules must not use dogfood adapter
  terminology as default project identity.
- Public docs may mention a dogfood adapter only inside explicit optional
  adapter sections.
- Historical docs may retain old terms only under `docs/archive/`.
- New adapter-specific behavior must come with adapter-specific tests.
