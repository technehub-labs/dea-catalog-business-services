# Change Requests

> **Layout note (CR-SVC-mv1, 2026-09-21):** This document was authored against the
> pre-migration catalog layout (`entities/v1-alpha/dea:*`) and the legacy `dea:*` id
> family. Ids and paths cited below are historical; see `reconciliation/migration-id-map.yaml`
> for the old-to-new id mapping and dea-metaframework `docs/entity-storage-layout.md` for
> the current layout.

This directory tracks formal change requests (CRs) for `dea-catalog-business-services` (renamed from `dea-catalog-digital-business-service-factory` in the org-wide Wave 0a rename).

| CR | Title | Status | Summary |
|---|---|---|---|
| [CR-CATALOG-STRUCT-04](CR-CATALOG-STRUCT-04.md) | Digital Business Service Factory Adoption | Proposed | First adoption CR for DBSF. Migrates the 18 `BusinessService` entries from flat `CATALOG/v1-alpha/business-services/*.yaml` (6 files, 3 entries each) into per-entity subtrees. Vendors the regenerator + gate + schema; adds `catalog-conformance.yml` workflow; commits `CATALOG.yaml` + `TEMPLATE_VERSION`. No research distribution step (DBSF has no `docs/research/`). |
| [CR-SVC-mv1](CR-SVC-mv1.md) | ID System Migration (org-wide Wave 2) | Proposed | Migrates the catalog to the org-wide id system and flat layout: 18 records rewritten to `services:service-<slug>-<hash>`; dirs to `<slug>-<hash>/`; own-id refs rewritten via `reconciliation/migration-id-map.yaml`; READMEs per entity dir; new blocking `check_id_system.py` gate (IDM-001..008) in CI; vendored STRUCT tools + catalog-index schema ported (dual-family ids, content-derived entity ids); 13 dangling `dea:capability-*` bindings + component/principle/pattern refs documented as known residuals (binding-reconciliation CR needed). Gates: id system CONFORMANT (18 records, 0 findings); catalog index OK; CST 16/16. |
