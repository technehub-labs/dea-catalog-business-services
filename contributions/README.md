# Contribution Queue — Entity Intake

> Process defined by **CR-SVC-004** (2026-10-27). This directory is the intake
> queue for new `BusinessService` entities: submissions land here as YAML,
> CI validates them, and an admission turns each one into a canonical entity
> subtree under `entities/v1-alpha/`.

## How to submit

1. Copy [`intake-template.yaml`](intake-template.yaml) to
   `contributions/queue/<slug>.yaml` and fill it in.
2. Open a PR. CI runs the queue gate
   (`python scripts/check_contributions.py`) on every PR — an invalid
   submission blocks the PR.
3. Review per the repo's CR governance: content changes to the catalog ride
   change requests, so the admission itself is carried by an admission CR
   (small, one per batch or per entity).

## Queue-entry rules (enforced by the gate)

- **No `id` field.** Record ids are `services:service-<slug>-<hash6>`,
  assigned once at admission from the content-derived hash
  (`dea-metaframework` `docs/id-system.md` §2.5 — the same derivation the
  CR-SVC-mv1 migration used). Hand-invented hashes are rejected.
- `status` is one of `draft` / `queued` / `admitted` / `rejected`.
- `governance` values (SLA tier, security classification, compliance
  frameworks) come from the register at
  [`classifications/sla-classification.yaml`](../classifications/sla-classification.yaml).
- `capabilities` / `solution_components` are colon-namespaced id references
  (form-checked in CI; resolution is verified at admission by the id-system
  gate, IDM-003/006).

## Admission

A maintainer runs, on the PR branch:

```bash
python scripts/admit_entity.py contributions/queue/<slug>.yaml [--dry-run]
```

The tool validates the submission, assigns the id, checks it against all
existing record ids (collision aborts), scaffolds
`entities/v1-alpha/<slug>-<hash>/` with the record YAML (version `0.1.0`,
candidate) and the per-entity `README.md` (IDM-007), flips the queue entry to
`status: admitted` with the assigned id, and runs the id-system gate over the
result — admission is gate-verified before it can merge.

The admission PR then carries (house landing convention): the entity subtree +
updated queue entry, the regenerated `CATALOG.yaml`, the `CHANGELOG.md`
`[Unreleased]` entry, and the admission CR + `change-requests/README.md` row.

## Hash preimage convention

For new records (no migration predecessor) the §2.5 hash is computed over the
intake **content mapping** — every field except queue metadata (`status`,
`slug`, `submitted_by`, `submitted`, `assigned_id`, `admitted`) — serialized
as sorted-key YAML. The suffix is assigned once and never recomputed; the
queue entry's `assigned_id` is the audit record of the assignment.
