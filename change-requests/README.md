# Change Requests

This directory tracks formal change requests (CRs) for `dea-catalog-digital-business-service-factory`.

| CR | Title | Status | Summary |
|---|---|---|---|
| [CR-CATALOG-STRUCT-04](CR-CATALOG-STRUCT-04.md) | Digital Business Service Factory Adoption | Proposed | First adoption CR for DBSF. Migrates the 18 `BusinessService` entries from flat `CATALOG/v1-alpha/business-services/*.yaml` (6 files, 3 entries each) into per-entity subtrees. Vendors the regenerator + gate + schema; adds `catalog-conformance.yml` workflow; commits `CATALOG.yaml` + `TEMPLATE_VERSION`. No research distribution step (DBSF has no `docs/research/`). |
