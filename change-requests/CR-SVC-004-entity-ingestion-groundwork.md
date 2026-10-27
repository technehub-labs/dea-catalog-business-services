# CR-SVC-004: Entity Ingestion Groundwork (Contribution Queue + Admission Tool)

**Status**: Merged
**Layer**: L1 (catalog operations: intake process, tooling, CI gate)
**Owner**: Emmanuel A. Otchere
**Date**: 2026-10-27
**Trigger**: User directive 2026-10-27 ("proceed as recommended and lets lay the ground to begin ingesting entities") after the review-remediation CRs landed (PRs #10/#11/#12). The repo had 18 records, an empty `contributions/` queue, and no documented intake path: nothing defined how a new `BusinessService` enters the catalog with a spec-conformant id. Prepared by the authoring agent under eaojnr's direction; authorship of record per the Authorship Cardinal Rule (CR-BP-118 / CR-DEA-BC-34).
**Carrier**: Single PR on feature branch `feat/CR-SVC-004-entity-ingestion-groundwork`. PR review, not direct push.
**Lands against**: `main`
**Depends on**: CR-SVC-001 (pinned toolchain this gate runs under), CR-SVC-003 (the governance register at `classifications/sla-classification.yaml` that intake validation reads).

## 1. What this CR builds

| Artifact | Role |
|---|---|
| `contributions/README.md` | Intake process: submit → CI-validated queue → admission CR → canonical entity |
| `contributions/intake-template.yaml` | Submission template (no `id`; governance from the register) |
| `contributions/queue/` (+`.gitkeep`) | The queue proper — one YAML per submission |
| `scripts/check_contributions.py` | CI gate: validates every queue file (blocking, wired into `catalog-conformance.yml`) |
| `scripts/admit_entity.py` | Admission tool: validates, assigns the id (§2), scaffolds the entity subtree, gate-verifies |

## 2. Id assignment (id-system.md §2.5 conformance)

New records take `services:service-<slug>-<hash6>`, where `<hash6>` = first 4 bytes of the SHA-256 of the canonical (sorted-key YAML) serialization of the intake **content mapping** (all fields except queue metadata), big-endian, 6 base-31 digits over the visually-unambiguous alphabet — the same derivation as CR-SVC-mv1's `migrate_to_new_ids.py`. For migrated records the preimage was the pre-migration record; for new records there is no predecessor, so the intake content is the documented preimage (`contributions/README.md` "Hash preimage convention"). The suffix is assigned once, collision-checked against every existing record id, recorded in the queue entry (`assigned_id`), and never recomputed — the rename-stability contract. IDM-004 continues to verify well-formedness only, so this convention adds no gate coupling.

## 3. Queue rules (enforced by `check_contributions.py`, blocking in CI)

- No top-level `id` on submissions — hand-invented hashes are exactly what the gate catches.
- `status` ∈ {`draft`, `queued`, `admitted`, `rejected`}.
- `name`, `description` (≥ 40 chars — it seeds the entity README), `domain` required; optional `slug` (lowercase kebab, ≤ 48).
- `governance.sla_tier` / `security_classification` / `compliance[]` must come from `classifications/sla-classification.yaml` (the register CR-SVC-003 relocated).
- `capabilities` / `solution_components` are lists of colon-namespaced id references (form check in CI; cross-catalog resolution verified at admission by the id-system gate, IDM-003/006).

## 4. Admission (`scripts/admit_entity.py`)

Validates via the same rules; derives slug (explicit or from `name`); computes and collision-checks the id; scaffolds `entities/v1-alpha/<slug>-<hash>/` with the record YAML (`id`, `type: BusinessService`, `version: 0.1.0`, candidate) and the per-entity `README.md` (IDM-007; same shape as the mv1-generated ones); flips the queue entry to `status: admitted` with `assigned_id` + date; then runs `check_id_system.py --strict` — a red gate aborts admission. `--dry-run` computes and prints the id without writing. The admission PR carries the house landing set: entity subtree + queue entry, regenerated `CATALOG.yaml`, `CHANGELOG.md` entry, admission CR + index row.

## 5. Verification (round-trip performed at authoring, then reverted)

1. Queue gate on a valid template-derived submission: CONFORMANT (1 queue file), exit 0.
2. Negative tests — injected hand-invented `id` and out-of-register `sla_tier: Diamond`: 2 findings, exit 1.
3. `admit_entity.py --dry-run`: assigned `services:service-order-orchestration-9r3s7d` (hash over the unambiguous alphabet), no writes.
4. Full admission: IDM gate CONFORMANT over **19 records, 0 findings**; regenerated `CATALOG.yaml` → `entities: 19`, index gate OK (19 entities); queue gate CONFORMANT with the admitted entry; generated README in the mv1 shape.
5. Test artifacts reverted; clean state re-verified: queue gate CONFORMANT (0 files), IDM 18/0, `regenerate --check` OK, CST 16/16 at v2.6.0.

## 6. NOT-List

- NOT an admission of any real entity (the round-trip entity was scaffolding proof and is not landed; the first real admission rides its own CR).
- NOT a queue-state automation (no bot moves entries between statuses; maintainers run the tool).
- NOT cross-catalog reference resolution inside the queue gate (form-check only; resolution is the admission-time IDM gate's job — same contract as the 18 existing records' disclosed residuals).
- NOT an upstream `dea-metaframework` contribution (the intake tooling is repo-local; if the org later standardizes intake across catalogs, a metaframework CR can adopt it).
- NOT a schema file under `schemas/` (the queue's contract is enforced by the gate; `schemas/` stays reserved per the template).

## 7. Acceptance criteria (verifiable from a clean clone of the landing PR)

1. `python scripts/check_contributions.py` → exit 0 with the empty queue ("CONFORMANT (0 queue file(s))"); exits 1 on a queue file carrying an `id`, an off-register governance value, or a missing required field.
2. Copy `contributions/intake-template.yaml` to `contributions/queue/` and run `python scripts/admit_entity.py contributions/queue/intake-template.yaml --dry-run`: prints a `services:service-<slug>-<hash6>` id whose hash uses only the alphabet `abcdefghjkmnpqrstuvwxyz23456789`, and writes nothing.
3. The round-trip of §5 reproduces: after admission, `check_id_system.py --strict` counts 19 records with 0 findings; `regenerate_catalog.py --check` passes after regeneration.
4. `.github/workflows/catalog-conformance.yml` runs the queue gate as a blocking step between the id-system gate and the IDM-008 coherence step.
5. `contributions/README.md` documents submit → queue → admission → landing, the queue rules, and the hash preimage convention; the repo README's Contributing section points at it.
6. CI green on the landing PR.
