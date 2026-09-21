# CR-CATALOG-STRUCT-04: Digital Business Service Factory Adoption

> **Layout note (CR-SVC-mv1, 2026-09-21):** This document was authored against the
> pre-migration catalog layout (`entities/v1-alpha/dea:*`) and the legacy `dea:*` id
> family. Ids and paths cited below are historical; see `reconciliation/migration-id-map.yaml`
> for the old-to-new id mapping and dea-metaframework `docs/entity-storage-layout.md` for
> the current layout.

**Status**: Proposed
**Layer**: L1 (Business Service Catalog)
**Owner**: TechNeHub Labs
**Depends on**: CR-CATALOG-STRUCT-01, CR-CATALOG-STRUCT-06a+06b
**Adoption pattern**: STRUCT-03 (single-PR; smaller blast radius than STRUCT-03a+03b because there is no research distribution step)

## What this CR is

Adopt the catalog repository standard (CR-CATALOG-STRUCT-01) in `dea-catalog-digital-business-service-factory` end-to-end. The DBSF repo is the third catalog to adopt; it has 18 canonical `BusinessService` entries (one file per domain currently) plus a governance-contracts layer (system-wide reference data).

The migration follows STRUCT-03's pattern (per-entity subtrees + vendored regenerator + `catalog-conformance.yml` workflow) but in a single PR because there is no research distribution step: DBSF has no `docs/research/` and the 18 entities are flat-domain-grouped in `CATALOG/v1-alpha/business-services/`, not cross-linked through per-entity research.

## Decisions locked during planning

- **Q1 (entity grouping)**: Q1 lock: (a) drop domain grouping; CATALOG.yaml `entities[].domain` field preserves it for queries.
- **Q2 (capability maps)**: (a) move to `mappings/`; they are already mappings and the BC catalog owns the canonical capabilities.
- **Q3 (governance contract)**: (a) keep `governance-contracts/` at `CATALOG/v1-alpha/`; system-level metadata.
- **Q5 (PR shape)**: single PR (no research distribution).

## What changes

### Files moved

| From | To |
|---|---|
| `CATALOG/v1-alpha/business-services/customer-services.yaml` (3 entries) | `entities/v1-alpha/dea:service-customer-360/dea:service-customer-360.yaml`, `entities/v1-alpha/dea:service-customer-identity/dea:service-customer-identity.yaml`, `entities/v1-alpha/dea:service-customer-notification/dea:service-customer-notification.yaml` |
| `CATALOG/v1-alpha/business-services/finance-services.yaml` (3 entries) | `entities/v1-alpha/dea:service-finance-accounting/dea:service-finance-accounting.yaml`, `entities/v1-alpha/dea:service-finance-reporting/dea:service-finance-reporting.yaml`, `entities/v1-alpha/dea:service-treasury-management/dea:service-treasury-management.yaml` |
| `CATALOG/v1-alpha/business-services/hr-services.yaml` (3 entries) | `entities/v1-alpha/dea:service-hr-core/dea:service-hr-core.yaml`, `entities/v1-alpha/dea:service-talent-management/dea:service-talent-management.yaml`, `entities/v1-alpha/dea:service-payroll/dea:service-payroll.yaml` |
| `CATALOG/v1-alpha/business-services/order-services.yaml` (3 entries) | `entities/v1-alpha/dea:service-order-taking/dea:service-order-taking.yaml`, `entities/v1-alpha/dea:service-order-fulfillment/dea:service-order-fulfillment.yaml`, `entities/v1-alpha/dea:service-order-tracking/dea:service-order-tracking.yaml` |
| `CATALOG/v1-alpha/business-services/product-services.yaml` (3 entries) | `entities/v1-alpha/dea:service-product-catalog/dea:service-product-catalog.yaml`, `entities/v1-alpha/dea:service-product-lifecycle/dea:service-product-lifecycle.yaml`, `entities/v1-alpha/dea:service-product-pricing/dea:service-product-pricing.yaml` |
| `CATALOG/v1-alpha/business-services/supply-chain-services.yaml` (3 entries) | `entities/v1-alpha/dea:service-inventory-management/dea:service-inventory-management.yaml`, `entities/v1-alpha/dea:service-procurement/dea:service-procurement.yaml`, `entities/v1-alpha/dea:service-logistics-coordination/dea:service-logistics-coordination.yaml` |
| `CATALOG/v1-alpha/capabilities/customer-capability-map.yaml` | `mappings/capability-maps/customer-capability-map.yaml` |
| `CATALOG/v1-alpha/capabilities/finance-capability-map.yaml` | `mappings/capability-maps/finance-capability-map.yaml` |
| `CATALOG/index.yaml` | deleted (superseded by `CATALOG.yaml`) |
| `CATALOG/v1-alpha/index.yaml` | deleted (superseded by `CATALOG.yaml`) |

### Files added

- `entities/v1-alpha/dea:service-*` (18 subtrees; canonical at root)
- `scripts/regenerate_catalog.py` (vendored)
- `scripts/check_catalog_index.py` (vendored)
- `scripts/extract_dbsf_entities.py` (one-shot extractor; idempotent)
- `catalog-index-schema/catalog-index-schema.json` (vendored)
- `CATALOG.yaml` (generated)
- `TEMPLATE_VERSION` (`0.1.0`)
- `change-requests/`, `classifications/`, `contributions/`, `schemas/` (empty `.gitkeep`)
- `.github/workflows/catalog-conformance.yml` (58 lines)
- `change-requests/CR-CATALOG-STRUCT-04.md` (this file)
- `01_plan/pr-struct-04.md` (PR body, untracked)

### Files kept

- `CATALOG/v1-alpha/governance-contracts/sla-classification.yaml`: kept; system-level SLA/security/compliance metadata; Q3 lock.
- `mappings/service-to-component.yaml`: already a cross-cutting mapping.
- `viewpoints/stakeholder-views.yaml`: already cross-cutting.
- `.github/workflows/validate-allocation.yml`: pinned against `dea-architecture-framework@v0.2.1`; orthogonal to catalog structure.
- `metamodel-pointer.yaml`: augmented with top-level metadata (additive only); nested blocks unchanged.
- `README.md`, `LICENSE`, `NOTICE`: unchanged.

### `metamodel-pointer.yaml` changes

The DBSF pointer is consumed by TWO tools with different expectations:

1. The catalog regenerator (`tools/regenerate_catalog.py`) reads top-level keys: `id`, `name`, `abbreviation`, `version`, `status`, `metamodel_version`, `owner`, `license`, `repository`, `homepage`, `conformance_status`, `description`.
2. The OpenDEAM allocation validator (`dea-architecture-framework/scripts/validate_consumer.py`) reads nested `metamodel.`, `entities[]`, `catalog.`, and (via `--model`) the OpenDEAM root model.

The previous pointer had a root-level `description:` that was actually the entity-class description ("A service exposed to the business..."). The regenerator was reading that as the catalog description, which was wrong. The fix:

- New top-level metadata block (`id`, `name`, `abbreviation`, `owner`, `license`, `repository`, `homepage`, `metamodel_version`, `conformance_status`).
- Existing root-level `description:` is REWRITTEN to the catalog-level description ("Enterprise business service definitions, capability decompositions, and solution component mappings for TechNeHub Labs.").
- The entity-class description moves to `metamodel.description:` (nested under `metamodel:` where the allocation validator expects entity-class metadata).

This is the same additive-plus-relocate pattern used in STRUCT-02 (process catalog). The `metamodel:` / `entities:` / `catalog:` / `links:` nested blocks are unchanged.

### Entity YAML changes (extractor-mediated)

The extractor (`tools/extract_dbsf_entities.py`) does the following on each entry from the old grouped YAMLs:

- Drops the redundant `source_id` from each `relationships[]` entry (the entity id is the source).
- Maps the legacy `status:` field to `lifecycle_status:` (the standard's regenerator vocabulary uses `lifecycle_status` with enum `candidate | active | deprecated | retired | unknown`).
- Writes one YAML per entity at `entities/v1-alpha/<id>/<id>.yaml`.

The extractor is idempotent: re-running overwrites the same files. It does NOT remove the source files (the migration step is a separate `git rm`).

## Pointer false alarm (NOT a real issue)

While verifying locally I observed that running `dea-architecture-framework/scripts/validate_consumer.py` against the local `model/opendeam-model.yaml` (the framework's HEAD) flags `entities[0].layer: L3` for `dea:entity-solution-component` as drift ("solution-component is an abstract kernel; layer should not be declared"). This is a local-vs-pinned mismatch, not a real issue:

- The DBSF CI workflow pins to `dea-architecture-framework@v0.2.1`.
- In the pinned `v0.2.1` model, `dea:entity-solution-component` has `layer: L3` directly (it is L3-instantiable, not an abstract kernel).
- The drift only appears when validating against HEAD/main of the framework (where the kernel classification has been refined).

This is exactly the kind of model drift the pinning mechanism is designed to defend against. CI passes against the pinned v0.2.1 model:

```
allocation / validate   pass   11s
```

Documented here for clarity so a future reader does not re-investigate.

## Verification

Local run (all green):

- `python scripts/regenerate_catalog.py --check --schema catalog-index-schema/catalog-index-schema.json` returns `OK: CATALOG.yaml is current`.
- `python scripts/check_catalog_index.py --strict --schema catalog-index-schema/catalog-index-schema.json` returns `OK: CATALOG.yaml validates (18 entities)`.
- `python .metaframework/tools/conformance_test_catalog_structure.py --catalog-root . --template-root .metaframework/tools/catalog-repo-template --strict` returns `OK: 16 CST(s) passed (0 warning(s))`.
- Dash sweep on new prose: clean.
- Secret scan: 0.
- `git diff --check`: clean.

## Conformance after this PR

- 18 entities in per-entity subtrees (canonical at root).
- 0 per-entity research files (no research distribution step).
- 0 candidates, 0 retired (no state directories; new entities only).
- 2 capability maps in `mappings/capability-maps/` (cross-cutting, not entities).
- 1 governance contract unchanged at `CATALOG/v1-alpha/governance-contracts/`.
- CATALOG.yaml: 18 entities, DBSF catalog, Apache-2.0, owner TechNeHub Labs.
- 16/16 CSTs pass under `--strict`.
- Cross-repo adoption tracker flips DBSF row from `not-started` to `conforming`.

## Sequencing

After this merges:

| Slice | Status |
|---|---|
| STRUCT-01 | Merged |
| STRUCT-06a | Merged |
| STRUCT-06b | Merged |
| STRUCT-02 (process catalog) | Merged (PR #21) |
| STRUCT-03 (BC catalog) | Merged (PRs #44 + #45) |
| STRUCT-04 (DBSF catalog) | This PR |
| STRUCT-05 (stakeholders catalog) | queued (smallest adoption; scaffold-only) |
| STRUCT-07 (cross-repo consumer) | unblocked (three conformant adopters) |
