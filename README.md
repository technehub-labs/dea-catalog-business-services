# Digital Business Service Factory

> Enterprise business service definitions, capability decompositions, and solution component mappings — structured against the TechNeHub Labs DEA metamodel.

[![Layer: L1](https://img.shields.io/badge/Layer-L1%20—%20Reference%20Catalogs-8b5cf6?style=flat-square)](https://github.com/technehub-labs/dea-metamodel)
[![Status: Alpha](https://img.shields.io/badge/Status-Alpha-FF6B35?style=flat-square)](./)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-blue?style=flat-square)](LICENSE)

---

## Entity Scope

This catalog hosts the following entities from the DEA metamodel:

| Entity | ID | Status |
|---|---|---|
| Business Service | `dea:entity-business-service` | Primary host |
| Business Object | `dea:entity-business-object` | Hosted (relocation pending separate decision) |
| Organizational Unit | `dea:entity-organizational-unit` | Hosted (relocation pending separate decision) |

**Relocated (2026-08-08):** Business Process (`dea:entity-business-process`) moved to its own catalog: [`dea-catalog-processes`](https://github.com/technehub-labs/dea-catalog-processes). The entity-graph viewer reference has been updated in `dea-metamodel/viewer/entity-graph.json`. Business Object (BO) and Organizational Unit (OU) remain hosted here pending a separate relocation decision.

---

## Overview

The Digital Business Service Factory (DBSF) is the L1 reference catalog that defines, classifies, and governs enterprise business services — from high-level capabilities down to the solution components that realise them.

It provides enterprise architects and solutions architects with:
- A **taxonomy of business services** (Customer, Product, Order, Finance, Supply Chain, HR, etc.)
- **Capability maps** for each business domain showing how capabilities decompose into services
- **Governance contracts** attached to each service: SLA, security classification, compliance requirements
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
  └─ DBSF governance contracts enforced via branch protection and CODEOWNERS
```

---

## Structure

```
dea-catalog-digital-business-service-factory/
├── README.md
├── CATALOG/
│   ├── v1-alpha/
│   │   ├── index.yaml              ← version entry point
│   │   ├── business-services/       ← one YAML file per business service
│   │   │   ├── customer-services.yaml
│   │   │   ├── product-services.yaml
│   │   │   ├── order-services.yaml
│   │   │   ├── finance-services.yaml
│   │   │   ├── supply-chain-services.yaml
│   │   │   └── hr-services.yaml
│   │   ├── capabilities/            ← capability maps per domain
│   │   │   ├── customer-capability-map.yaml
│   │   │   └── finance-capability-map.yaml
│   │   └── governance-contracts/   ← service governance metadata
│   │       └── sla-classification.yaml
│   └── index.yaml                   ← catalog entry point
├── mappings/
│   └── service-to-component.yaml    ← service → solution component mappings
├── viewpoints/
│   └── stakeholder-views.yaml       ← CTO, ChiefArchitect, SolutionsArchitect viewpoints
└── LICENSE
```

---

## Business Service Entity

Each entry in DBSF is a `BusinessService` entity (from the DEA metamodel):

```yaml
id: dea:service-customer-360
type: BusinessService
name: Customer 360 Service
abbreviation: C360
version: "1.0.0"
status: active
description: >
  Provides a unified, real-time view of all customer interactions, attributes,
  and history across all channels and touchpoints.
domain: Customer
subdomain: Customer Insight
capabilities:
  - dea:capability-customer-data-management
  - dea:capability-customer-identity-resolution
governance:
  sla_uptime: "99.95%"
  security_classification: Confidential
  compliance:
    - GDPR
    - CCPA
solution_components:
  - dea:component-customer-data-platform
  - dea:component-identity-resolution-service
relationships:
  - source_id: dea:service-customer-360
    target_id: dea:principle-data-ownership
    relationship_type: implements
  - source_id: dea:service-customer-360
    target_id: dea:pattern-cqrs
    relationship_type: realised_through
tags:
  - customer
  - data-platform
  - real-time
  - gdpr
```

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
dea query --id dea:service-customer-360
```

---

## Contributing

1. Propose a new business service via issue
2. Ensure it conforms to the `BusinessService` schema in `dea-metamodel`
3. Add governance contract (SLA, security classification)
4. Declare relationships to capabilities and solution components
5. Submit PR — CI validates against metamodel schema

---

## License

Apache 2.0 — see [LICENSE](./LICENSE).