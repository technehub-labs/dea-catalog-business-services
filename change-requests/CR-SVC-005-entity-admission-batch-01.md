# CR-SVC-005: Entity Admission Batch 01 (Access Certification Service … Career Development Service)

**Status**: Merged
**Layer**: Catalog content (business services admission)
**Owner**: Emmanuel A. Otchere
**Date**: 2026-11-01
**Trigger**: User directive 2026-11-01: "let's build at least, say, 500 business services that can be gated through the contribution workflow." This CR is one batch of the approved programme, executed through the CR-SVC-004 contribution workflow (queue gate → admission tool → id-system gate). Prepared by the authoring agent under eaojnr's direction; authorship of record per the Authorship Cardinal Rule (CR-BP-118 / CR-DEA-BC-34).
**Carrier**: Single PR on feature branch `feat/entity-admission-batch-01`. PR review, not direct push.
**Lands against**: `main`
**Depends on**: CR-SVC-004 (intake machinery), CR-SVC-001 (pinned toolchain).

## 1. What this CR admits

50 new `BusinessService` records, admitted from `contributions/queue/` by `scripts/admit_entity.py`:

| Domain | Admitted |
|---|---|
| Change & Transformation | 3 |
| Customer Experience | 1 |
| Cybersecurity | 1 |
| Data & Analytics | 5 |
| Enterprise Strategy & Performance | 6 |
| Facilities & Asset Management | 5 |
| Finance & Accounting | 6 |
| Human Resources | 3 |
| IT Operations & Infrastructure | 4 |
| Marketing & Brand | 5 |
| Order Management | 1 |
| Product & Offering Management | 1 |
| Risk & Compliance | 5 |
| Sales & Revenue Operations | 1 |
| Sourcing & Procurement | 1 |
| Supply Chain & Logistics | 1 |
| Sustainability & ESG | 1 |

Each admission: id `services:service-<slug>-<hash6>` assigned by the CR-SVC-004 content-derived hash (collision-checked against all record ids), entity subtree `entities/v1-alpha/<slug>-<hash>/` with record (`version: 0.1.0`) and per-entity README (IDM-007), queue entry flipped to `status: admitted` with `assigned_id`. Capability bindings reference the canonical capabilities catalog; governance values come from `classifications/sla-classification.yaml`.

## 2. What changes

- `50` entity subtrees under `entities/v1-alpha/` (Access Certification Service … Career Development Service)
- `50` queue files moved to `status: admitted` with `assigned_id` + date
- `CATALOG.yaml` regenerated (entity count +50)
- This CR file, CHANGELOG entry, and index row

## 3. Verification

- `check_contributions.py`: CONFORMANT (queue valid post-admission)
- `check_id_system.py --strict`: run per admission by the admission tool; CONFORMANT over the full tree
- `regenerate_catalog.py --check`: CATALOG.yaml current
- CI green on the landing PR (catalog-conformance + validate-allocation)

## 4. NOT-List

- NOT a change to any of the 18 pre-existing records or their disclosed residuals (binding reconciliation is a separate CR).
- NOT a change to gates, schemas, or the intake tooling (CR-SVC-004 artifacts untouched).
- NOT a release/tag action; records stay candidate-state in v1-alpha.
- NOT an assertion that every admitted record's `solution_components` reference resolves today — component ids follow the established `dea:component-*` register pattern of the existing records (disclosed mv1 residual class, unchanged by this programme).

## 5. Correction (in-landing)

First CI run caught CST-004 (`lifecycle_status` required on canonical records): the CR-SVC-004 admission tool did not write the field. Fixed in this PR — the tool now emits `lifecycle_status: active` (the existing-records convention) and all 50 admitted records carry it. The authoring-time round-trip had verified the IDM/index/queue gates but not the CST suite; the CST suite now runs per batch via CI.

## 6. Acceptance criteria

1. Entity count in `CATALOG.yaml` increases by exactly 50; all records id/README/path-conformant (IDM gate 0 findings).
2. All 50 queue files carry `status: admitted` and a recorded `assigned_id`.
3. All repo gates green on the landing PR.
