# Business Services Catalog Changelog

All notable changes to this catalog are recorded here. The format is based
on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), adapted for
CR-carried changes: each entry records the change request, the scope, the
rationale, and the PR that landed it. Bootstrapped by CR-SVC-002
(2026-10-27); landings before it are recorded retrospectively below.

Status vocabulary for change requests: `Draft`/`Proposed` (open) →
`Merged` (landed). See `change-requests/CR-SVC-002` §2 (decision of
record).

## [Unreleased]

### CR-SVC-010: Entity Admission Batch 06

Admitted 50 new `BusinessService` records through the CR-SVC-004 contribution workflow (1 Communications & Workplace, 2 Customer Experience, 4 Data & Analytics, 3 Enterprise Strategy & Performance, 1 Facilities & Asset Management, 1 Finance & Accounting, 8 Human Resources, 6 IT Operations & Infrastructure, 6 Legal & Privacy, 5 Marketing & Brand, 5 Order Management, 2 Product & Offering Management, 2 Risk & Compliance, 1 Sales & Revenue Operations, 3 Supply Chain & Logistics); ids content-derived and collision-checked; entity count +50; queue entries flipped to `admitted`.

### CR-SVC-009: Entity Admission Batch 05

Admitted 50 new `BusinessService` records through the CR-SVC-004 contribution workflow (2 Customer Experience, 2 Data & Analytics, 7 Enterprise Strategy & Performance, 4 Facilities & Asset Management, 8 Finance & Accounting, 5 Human Resources, 5 IT Operations & Infrastructure, 1 Legal & Privacy, 2 Marketing & Brand, 2 Order Management, 5 Risk & Compliance, 1 Sales & Revenue Operations, 2 Sourcing & Procurement, 4 Supply Chain & Logistics); ids content-derived and collision-checked; entity count +50; queue entries flipped to `admitted`.

### CR-SVC-008: Entity Admission Batch 04

Admitted 50 new `BusinessService` records through the CR-SVC-004 contribution workflow (7 Communications & Workplace, 1 Customer Experience, 4 Cybersecurity, 3 Data & Analytics, 1 Enterprise Strategy & Performance, 4 Facilities & Asset Management, 2 Finance & Accounting, 4 Human Resources, 5 IT Operations & Infrastructure, 4 Marketing & Brand, 2 Product & Offering Management, 2 Risk & Compliance, 1 Supply Chain & Logistics, 10 Sustainability & ESG); ids content-derived and collision-checked; entity count +50; queue entries flipped to `admitted`.

### CR-SVC-007: Entity Admission Batch 03

Admitted 50 new `BusinessService` records through the CR-SVC-004 contribution workflow (1 Change & Transformation, 2 Communications & Workplace, 9 Customer Experience, 1 Cybersecurity, 8 Data & Analytics, 2 Enterprise Strategy & Performance, 1 Facilities & Asset Management, 7 Finance & Accounting, 1 Human Resources, 2 IT Operations & Infrastructure, 5 Legal & Privacy, 2 Marketing & Brand, 1 Partner & Channel Management, 1 Risk & Compliance, 2 Sales & Revenue Operations, 1 Sourcing & Procurement, 4 Supply Chain & Logistics); ids content-derived and collision-checked; entity count +50; queue entries flipped to `admitted`.

### CR-SVC-006: Entity Admission Batch 02

Admitted 50 new `BusinessService` records through the CR-SVC-004 contribution workflow (7 Change & Transformation, 4 Customer Experience, 1 Data & Analytics, 1 Enterprise Strategy & Performance, 5 Finance & Accounting, 3 Human Resources, 7 IT Operations & Infrastructure, 1 Legal & Privacy, 3 Marketing & Brand, 1 Order Management, 3 Partner & Channel Management, 1 Product & Offering Management, 3 Risk & Compliance, 3 Sales & Revenue Operations, 3 Sourcing & Procurement, 2 Supply Chain & Logistics, 2 Sustainability & ESG); ids content-derived and collision-checked; entity count +50; queue entries flipped to `admitted`.

### CR-SVC-005: Entity Admission Batch 01

Admitted 50 new `BusinessService` records through the CR-SVC-004 contribution workflow (3 Change & Transformation, 1 Customer Experience, 1 Cybersecurity, 5 Data & Analytics, 6 Enterprise Strategy & Performance, 5 Facilities & Asset Management, 6 Finance & Accounting, 3 Human Resources, 4 IT Operations & Infrastructure, 5 Marketing & Brand, 1 Order Management, 1 Product & Offering Management, 5 Risk & Compliance, 1 Sales & Revenue Operations, 1 Sourcing & Procurement, 1 Supply Chain & Logistics, 1 Sustainability & ESG); ids content-derived and collision-checked; entity count +50; queue entries flipped to `admitted`.

### CR-SVC-004: Entity Ingestion Groundwork (Contribution Queue + Admission Tool)

Defines the intake path for new `BusinessService` entities: a contribution queue (`contributions/queue/`, template + process doc) validated by a new blocking CI gate (`scripts/check_contributions.py` — no hand-invented ids, governance values from the `classifications/sla-classification.yaml` register), and an admission tool (`scripts/admit_entity.py`) that assigns the org-wide id (`services:service-<slug>-<hash6>`, the id-system §2.5 content-derived hash over the intake content — same derivation as the mv1 migration), collision-checks it, scaffolds the entity subtree with the per-entity README (IDM-007), marks the queue entry admitted, and gate-verifies the result (a red id-system gate aborts admission). End-to-end round-trip verified at authoring (18 → 19 records CONFORMANT, index regenerated and valid, then reverted); no real entity lands with this CR — the first real admission rides its own CR.

### CR-SVC-003: Rename Residue Cleanup + README Truth + Authorship Correction

Recorded authorship correction on `CR-SVC-mv1.md` (Owner per the Authorship Cardinal Rule, CR-BP-118 / CR-DEA-BC-34; the original value carried the 2026-10-13 denylisted agent signature). README rewritten to the truth: actual flat entity tree, entity scope = Business Service primary + Solution Component shared per the pointer (capability bindings are references into the capabilities catalog), governance wording now names the real CI gates (no branch-protection/CODEOWNERS claim — unavailable on this plan), plus a verified local-gates section. The stranded governance register relocated from the legacy pre-migration tree to `classifications/sla-classification.yaml`; the spent one-shot `tools/extract_dbsf_entities.py` removed. The `metamodel-pointer.yaml` URLs are documented as blocked on a root-model rename in `dea-architecture-framework` (specified in the CR §4; the pointer itself is generated and untouched).

### CR-SVC-002: CR Status Truth + CHANGELOG Bootstrap

Adopts `Merged` as this repo's landed-CR status (the effective toolchain — vendored copies and the CI-pinned upstream regenerator alike — recognizes exactly one closed status, so the count becomes truthful with zero tool delta; the counter's duplicated condition and single-status closed set exist upstream too and are recorded there as follow-up). Both previously landed CRs backfilled from their authoring-time status with recorded corrections: CR-CATALOG-STRUCT-04 (PR #6, 2026-09-05) and CR-SVC-mv1 (PR #7, 2026-09-21). This CHANGELOG bootstrapped (Keep-a-Changelog shape) with retrospective entries for the pre-changelog landings. `CATALOG.yaml` regenerated in the same PR: `open_change_requests` 2 → 0. No entity, id, schema, or vendored-script changes.

---

## Pre-changelog history (recorded retrospectively by CR-SVC-002, 2026-10-27)

> Entries below this line predate this CHANGELOG and are reconstructed
> from the merged PRs and their carrier CRs. PRs #3 (2026-08-08) and #4
> (2026-08-09) were docs-only relocation announcements and carried no CR.

### CR-SVC-001: CI Toolchain Pinning + Vendored Copy Refresh — 2026-10-27

The `dea-metaframework` checkout in `catalog-conformance.yml` pinned to release tag `v2.6.0` with tools staged unconditionally from the pinned checkout (CST-013/014 canonical shape; the checks were redefined 2026-10-22 to require a pinned upstream, and the unpinned checkout would have turned every subsequent PR red). Repo checkout gains `fetch-depth: 0`: the regenerator's `last_modified` machinery resolves every path to HEAD's date under a depth-1 clone, churning all 18 entity dates and failing the freshness gate on any PR merged on a later day (reproduced at landing). Vendored `regenerate_catalog.py` / `check_catalog_index.py` / `catalog-index-schema.json` refreshed to be byte-identical to the pin, fixing the hash-alphabet regex drift (all 18 current hashes already conform). `timeout-minutes: 15`. (PR #10; first attempt #9 was auto-closed when its head was orphaned by a force-push.)

### docs: entity README template mirror — 2026-09-21

Per-entity `README.md` files under `entities/v1-alpha/*/` mirrored from the structural template set in `dea-catalog-processes` PR #153: flat-layout sections replacing the containment-tree and ECF-matrix sections specific to ECF-coordinated catalogs. (PR #8.)

### CR-SVC-mv1: ID System Migration (org-wide Wave 2, services) — 2026-09-21

Migrated the catalog to the org-wide id system and storage layout (`dea-metaframework` canonical specs): 18 records rewritten from `dea:service-*` to `services:service-<slug>-<hash>` (hash per id-system.md §2.5, 31-symbol alphabet); entity directories moved to the flat `entities/v1-alpha/<slug>-<hash>/` layout; own-id cross-references rewritten via `reconciliation/migration-id-map.yaml`; new blocking `check_id_system.py` gate (IDM-001..008) wired into CI with a per-PR coherence report artifact; vendored STRUCT tools + catalog-index schema replaced with the dual-family ports. Disclosed residuals: 13 finer-grained `dea:capability-*` bindings with no mapping target, and `dea:component-*` / `dea:principle-*` / `dea:pattern-*` namespaces not in the ratified registry — binding-reconciliation CR needed. (PR #7.)

### CR-CATALOG-STRUCT-04: Digital Business Service Factory Adoption — 2026-09-05

Adopted the catalog repository standard (CR-CATALOG-STRUCT-01) end-to-end: the 18 `BusinessService` entries migrated from flat `CATALOG/v1-alpha/business-services/*.yaml` (6 files, 3 entries each) into per-entity subtrees; vendored regenerator + index gate + schema; new `catalog-conformance.yml` workflow; committed `CATALOG.yaml` + `TEMPLATE_VERSION`. (PR #6.)
