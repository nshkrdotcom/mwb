# Example Geometry

Example geometry audits check whether a target/control bundle is fit for serious
causal claims.

## Commands

```bash
uv run mwb bundle audit negation_demo_calibrated
uv run mwb bundle rebalance --dry-run
```

Audit reports are written to:

```text
.mechanism/bundle_audits/latest_bundle_audit.json
```

Rebalance proposals are written to:

```text
.mechanism/bundle_rebalance/latest_rebalance_proposal.json
```

## Audit Checks

`token_validity` verifies that every example/control row has a non-empty id,
prompt, and target.

`role_balance` compares target count with each control-family count.
Underrepresented control families produce improvement proposals.

`control_contamination` flags target markers inside controls that are supposed
to remove the target contrast.

`baseline_margin` checks explicit `baseline_margin` values when present.
Missing margins warn; low margins block.

## Proposals

The rebalance dry-run proposes:

- additional control examples for underrepresented families;
- heldout prompt templates;
- heldout target/foil vocabulary.

These are proposals only. The command does not rewrite bundle source files.

## Claim Boundary

An audit warning does not invalidate exploratory work. It does block clean
mechanism-level claims until the bundle has balanced controls, token validity,
explicit baseline margins, and contamination checks.
