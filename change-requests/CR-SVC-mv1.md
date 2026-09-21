# CR-SVC-mv1: ID System Migration (org-wide Wave 2, services)

**Status**: Proposed
**Layer**: Catalog (business services)
**Owner**: Coder (for eaojnr)
**Date**: 2026-09-21
**Depends on**: dea-metaframework docs (`id-system.md`, `entity-storage-layout.md`, PR #31); Wave 1 (dea-catalog-business-processes PR #149); Wave 2a (dea-catalog-business-capabilities PR #73); Wave 2 decision review (eaojnr 2026-09-21: D2-1..D2-5 confirmed)

## 1. Summary

Migrates this catalog to the org-wide id system and storage layout
(dea-metaframework canonical specs). Every record's `id:` moves from
`dea:service-*` to `services:service-<slug>-<hash>` (18 records; hash per
id-system.md section 2.5). Entity directories move from
`entities/v1-alpha/dea:<id>/` to `entities/v1-alpha/<slug>-<hash>/`
(flat layout, entity-storage-layout.md section 3). Own-id
cross-references (`relationships[]`, mapping registers, viewpoints,
README examples) are rewritten through the migration id map.

## 2. Known residuals (disclosed, per Wave 2 decision D2-4)

All four residual classes are documented in
`reconciliation/migration-id-map.yaml`:

- `dea:capability-*` bindings (13 distinct ids in `capabilities[]`
  fields): every binding references a capability granularity that does
  not exist in the capabilities catalog (28 first-order records).
  Pre-existing org drift, not migration damage; no mapping target
  exists. Needs a binding-reconciliation CR (admit the finer-grained
  capabilities or remap bindings to first-order ids).
- `dea:component-*` (`solution_components[]`): component namespace is not
  in the ratified id registry.
- `dea:principle-*` and `dea:pattern-*` (`relationships[].target_id`):
  namespaces not in the ratified id registry.

## 3. What changes

- `scripts/migrate_to_new_ids.py`: the migration script (idempotent;
  dry-run by default). Consumes the Wave 2a capabilities id map
  read-only when available (no capability refs resolved this wave; see
  residuals).
- 18 record files moved + rewritten; README.md per entity dir (IDM-007).
- `scripts/check_id_system.py` (new): IDM-001..007 catalog-wide gate +
  IDM-008 PR-scoped coherence mode with per-PR report artifact. Wired
  into `catalog-conformance.yml`.
- Vendored STRUCT tools + catalog-index schema replaced with the
  dual-family, content-derived-id ports (same versions as Wave 2a;
  upstream: dea-metaframework PR #34). This also pulls in the newer
  git-commit-date `last_modified` machinery the services vendored copy
  was missing.
- Living registers rewritten via the id map: `mappings/` (3 files),
  `viewpoints/stakeholder-views.yaml`, README examples.
- Historical artifacts bannered `Layout note (CR-SVC-mv1, 2026-09-21)`
  (content verbatim): CR-CATALOG-STRUCT-04 + the CR index. Cross-check
  report: `reconciliation/cross-check-mv1.md` (2 artifacts, both
  HISTORICAL-ONLY; 0 NEEDS-FRAMING).
- CR index header repo name updated to `dea-catalog-business-services`
  (Wave 0a rename).

## 4. Verification

- `check_id_system.py --strict`: CONFORMANT, 18 records, 0 findings.
- `check_catalog_index.py --strict`: OK (18 entities).
- `regenerate_catalog.py --check`: CATALOG.yaml current.
- CST suite (dea-metaframework main, post-#33/#34): 16/16 pass --strict.
- Migration idempotence: re-run is a no-op.
