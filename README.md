# Digital Business Service Factory

> Enterprise business service definitions, capability decompositions, and solution component mappings — structured against the TechNeHub Labs DEA metamodel.

[![Layer: L1](https://img.shields.io/badge/Layer-L1%20—%20Reference%20Catalogs-8b5cf6?style=flat-square)](https://github.com/technehub-labs/dea-metamodel)
[![Status: Alpha](https://img.shields.io/badge/Status-Alpha-FF6B35?style=flat-square)](./)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-blue?style=flat-square)](LICENSE)

---

## Entity Scope

This catalog hosts the following entities from the DEA metamodel (allocation declared in [`metamodel-pointer.yaml`](metamodel-pointer.yaml), pinned against the OpenDEAM root model):

| Entity | ID | Allocation |
|---|---|---|
| Business Service | `dea:entity-business-service` | Primary host |
| Solution Component | `dea:entity-solution-component` | Shared host (ADR-0002 D6) |

Business services are **not** ECF-coordinated; the `capabilities[]` field on each record is a many-to-many *reference* into the canonical capabilities catalog, [`dea-catalog-business-capabilities`](https://github.com/technehub-labs/dea-catalog-business-capabilities). Thirteen finer-grained `dea:capability-*` bindings are disclosed residuals from CR-SVC-mv1 §2 and await a binding-reconciliation CR. Component, principle, and pattern references (`dea:component-*`, `dea:principle-*`, `dea:pattern-*`) likewise reference namespaces not yet in the ratified id registry.

**Relocated (history):**

- **2026-08-08** — Business Process (`dea:entity-business-process`) → [`dea-catalog-business-processes`](https://github.com/technehub-labs/dea-catalog-business-processes)
- **2026-08-09** — Business Object (`dea:entity-business-object`) → [`dea-catalog-business-objects`](https://github.com/technehub-labs/dea-catalog-business-objects)
- **2026-08-09** — Organizational Unit (`dea:entity-organizational-unit`) → [`dea-catalog-organizational-units`](https://github.com/technehub-labs/dea-catalog-organizational-units)

---

## Overview

The Digital Business Service Factory (DBSF) is the L1 reference catalog that defines, classifies, and governs enterprise business services — from the capabilities they compose down to the solution components that realise them.

It provides enterprise architects and solutions architects with:
- A **taxonomy of business services** (Customer, Product, Order, Finance, Supply Chain, HR)
- **Capability bindings** on each service showing which capabilities it draws on
- **Governance contracts** attached to each service: SLA tier/uptime, security classification, compliance requirements (tier vocabulary: [`classifications/sla-classification.yaml`](classifications/sla-classification.yaml))
- **Solution component mappings** linking services to the technology components that implement them

---

## Framework Position

```
L0 — Metamodel (dea-metamodel)
  └─ defines: BusinessService, BusinessCapability, SolutionComponent, Relationship
L1 — DBSF (this repo)
  └─ seeds and governs enterprise business service definitions
L2 — Tooling (dea-cli, dea-scripts, dea-web-viewer)
  └─ consume DBSF entries for viewpoint generation and component mapping
L3 — Governance
  └─ blocking CI gates: catalog-conformance (id system, index freshness,
     structure conformance) + validate-allocation (OpenDEAM pointer)
```

Governance here is enforced by the blocking CI gates on every PR and push to `main`. (Branch protection and CODEOWNERS enforcement are not available on this repository's GitHub plan; recorded as an org-level backlog item.)

---

## Structure

```
dea-catalog-business-services/
├── README.md
├── CHANGELOG.md                        ← Keep-a-Changelog, CR-carried landings
├── CATALOG.yaml                        ← generated index (regenerator output; do not hand-edit)
├── metamodel-pointer.yaml              ← OpenDEAM allocation declaration (generated; do not hand-edit)
├── TEMPLATE_VERSION                    ← catalog template version
├── catalog-index-schema/               ← vendored index schema (pinned: dea-metaframework v2.6.0)
├── entities/v1-alpha/                  ← flat layout: one <slug>-<hash>/ subtree per record
│   ├── README.md                       ← layout spec (mirrors dea-catalog-processes PR #153)
│   └── <slug>-<hash>/
│       ├── services-service-<slug>-<hash>.yaml   ← the BusinessService record
│       └── README.md                   ← per-entity README (IDM-007)
├── classifications/
│   └── sla-classification.yaml         ← governance vocabulary register (SLA tiers,
│                                          security classifications, compliance frameworks)
├── mappings/
│   ├── service-to-component.yaml       ← service → solution component mappings
│   └── capability-maps/                ← per-domain capability maps
├── viewpoints/
│   └── stakeholder-views.yaml          ← CTO / ChiefArchitect / SolutionsArchitect viewpoints
├── reconciliation/
│   ├── migration-id-map.yaml           ← CR-SVC-mv1 old→new id map (audit trail)
│   └── cross-check-mv1.md              ← historical-artifact cross-check report
├── contributions/                      ← intake queue (see Contributing)
├── schemas/                            ← reserved for local schemas (currently empty)
├── scripts/                            ← id-system gate, regenerator, index gate (pinned copies), migration tool
└── change-requests/                    ← CR index + files (house governance)
```

---

## Business Service Entity

Each entry in DBSF is a `BusinessService` entity (from the DEA metamodel), identified in the org-wide id system (`dea-metaframework` `docs/id-system.md`):

```yaml
id: services:service-customer-360-ut9yeu
type: BusinessService
name: Customer 360 Service
abbreviation: C360
version: "1.0.0"
description: >
  Provides a unified, real-time view of all customer interactions, attributes,
  and history across all channels and touchpoints.
domain: Customer
subdomain: Customer Insight
capabilities:                          # references into dea-catalog-business-capabilities
  - dea:capability-customer-data-management
  - dea:capability-customer-identity-resolution
governance:
  sla_tier: Platinum                   # vocabulary: classifications/sla-classification.yaml
  sla_uptime: "99.99%"
  recovery_time_minutes: 15
  security_classification: Confidential
  compliance:
    - GDPR
    - CCPA
solution_components:
  - dea:component-customer-data-platform
  - dea:component-identity-resolution-service
relationships:
  - target_id: dea:principle-data-ownership
    relationship_type: implements
  - target_id: dea:pattern-cqrs
    relationship_type: realised_through
tags:
  - customer
  - data-platform
  - real-time
  - gdpr
```

---

## Local Gates & Verification

The CI toolchain is pinned to `dea-metaframework` `v2.6.0` (`catalog-conformance.yml`); the vendored copies under `scripts/` and `catalog-index-schema/` are byte-identical to that tag. Run the gates from the repo root (Python ≥ 3.11 with `pyyaml` + `jsonschema`):

```bash
python scripts/check_id_system.py --strict          # IDM-001..007: CONFORMANT, 18 records, 0 findings
python scripts/regenerate_catalog.py --check \
    --schema catalog-index-schema/catalog-index-schema.json   # CATALOG.yaml freshness (blocking)
python scripts/check_catalog_index.py --strict \
    --schema catalog-index-schema/catalog-index-schema.json   # index schema validation (blocking)
```

Note the `--schema` flag: the vendored scripts' built-in default path (`tools/catalog-index-schema.json`) applies when running them in-place upstream, not from this repo's layout. The cross-repo structure conformance suite (CST-001..016) runs in CI from the pinned `dea-metaframework` checkout.

---

## How to Use

**Browse by domain:**
```bash
dea query --type BusinessService --tag customer
```

**Generate a CTO viewpoint:**
```bash
dea viewpoint --stakeholder CTO --tag finance
```

**Map a service to its components:**
```bash
dea query --id services:service-customer-360-ut9yeu
```

---

## Contributing

1. Propose a new business service via issue or a queued contribution file under `contributions/`
2. Ensure it conforms to the `BusinessService` schema in `dea-metamodel` and the id system (`dea-metaframework` `docs/id-system.md`)
3. Attach a governance contract (SLA tier, security classification, compliance) per the vocabulary in `classifications/sla-classification.yaml`
4. Declare relationships to capabilities and solution components
5. Submit PR — CI validates the id system, index freshness, structure conformance, and OpenDEAM allocation

Structural changes are carried by change requests in `change-requests/` (see its README); landings regenerate `CATALOG.yaml` and record a `CHANGELOG.md` entry in the same PR.

---

## License

Apache 2.0 — see [LICENSE](./LICENSE).
