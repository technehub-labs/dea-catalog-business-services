# CR-SVC-003: Rename Residue Cleanup + README Truth + Authorship Correction

**Status**: Merged
**Layer**: L1 (catalog operations: docs truth, recorded corrections, hygiene)
**Owner**: Emmanuel A. Otchere
**Date**: 2026-10-27
**Trigger**: Full-repo review 2026-10-27 (user directive: "lets work on the repo" → "proceed") found the Wave 0a repo rename unpropagated (upstream model included), a README that documents a dead tree and claims governance machinery that does not exist, one Authorship Cardinal Rule violation on `main`, and two migration leftovers. Prepared by the review agent under eaojnr's direction; authorship of record per the Authorship Cardinal Rule (CR-BP-118 / CR-DEA-BC-34).
**Carrier**: Single PR on feature branch `feat/CR-SVC-003-rename-residue-and-readme-truth`. PR review, not direct push.
**Lands against**: `main`
**Depends on**: CR-SVC-002 (this CR's landing appends its entry to the `CHANGELOG.md` that CR-SVC-002 bootstraps; landing-order contract at CR-SVC-002 §6).

## 1. Problem statement (verified 2026-10-27, `main` @ `63c3ddc`)

| Item | Evidence |
|---|---|
| Pointer carries pre-rename repo name | `metamodel-pointer.yaml` — `repository:`, `homepage:`, `catalog.repo:`, `links.github:` all say the Wave 0a pre-rename name (4 occurrences) |
| Root cause is upstream | OpenDEAM `model/opendeam-model.yaml` still says the pre-rename `catalog_repo` value at `v0.2.1` (lines 331/361) **and** current `v0.7.1` (lines 496/527) — `validate-allocation` is green only because model and pointer are consistently stale |
| README documents a dead tree | Structure section renders the pre-rename directory name with `CATALOG/v1-alpha/business-services/*.yaml` etc.; the repo is flat `entities/v1-alpha/<slug>-<hash>/` since CR-SVC-mv1 |
| README entity-scope contradictions | "Business Capability, Solution Component, and Business Service remain here" + "DBSF becomes a pure Business Service host" in the same paragraph; pointer allocates only Business Service (primary) + Solution Component (shared); the canonical capability host is `dea-catalog-business-capabilities` |
| README governance overclaim | "enforced via branch protection and CODEOWNERS" — no CODEOWNERS exists; branch protection is unavailable on this GitHub plan (API 403, verified) |
| Authorship violation on `main` | `change-requests/CR-SVC-mv1.md:5` — `**Owner**` carries the 2026-10-13 denylisted agent signature, denylisted org-wide (CR-BP-118, propagated as CR-DEA-BC-34; gate `check_authorship.py` AUT-001 in both sibling repos) |
| Legacy-tree vestige | `CATALOG/v1-alpha/governance-contracts/sla-classification.yaml` — a live register (SLA tiers, security classifications, compliance frameworks — the vocabulary record `governance` fields use) stranded in the pre-mv1 path; referenced only by the stale README and a historical CR |
| Spent one-shot | `tools/extract_dbsf_entities.py` — reads `CATALOG/v1-alpha/business-services/*.yaml`, a source tree that no longer exists |

## 2. Authorship correction (recorded, not silent)

`change-requests/CR-SVC-mv1.md`: the `**Owner**` value → `Emmanuel A. Otchere` (from the denylisted agent signature), plus one line under the metadata block: `> **Correction (CR-SVC-003, 2026-10-27):** Owner corrected per the Authorship Cardinal Rule (CR-BP-118 / CR-DEA-BC-34); the CR was prepared by the authoring agent under eaojnr's direction, recorded in the **Depends on** narrative above.` The agency narrative (Wave 2 decision review, eaojnr 2026-09-21) already lives in that CR's metadata; only the authorship-of-record value changes.

## 3. README truth pass

- **Structure section**: render the actual tree — `entities/v1-alpha/<slug>-<hash>/` (one YAML + README per record; `entities/v1-alpha/README.md` layout spec), `mappings/` (`service-to-component.yaml`, `capability-maps/`), `viewpoints/`, `reconciliation/` (`migration-id-map.yaml`, `cross-check-mv1.md`), `classifications/` (holding the governance register relocated in §5), `contributions/`, `schemas/`, `scripts/` (4 gates/regenerator/migration tool), `catalog-index-schema/`, `CATALOG.yaml`, `metamodel-pointer.yaml`, `TEMPLATE_VERSION`, `tools/` (removed per §5).
- **Entity Scope**: primary host Business Service (`dea:entity-business-service`); shared host Solution Component (`dea:entity-solution-component`, pointer `entities:` block, ADR-0002 D6); `capabilities[]` bindings in records are many-to-many references into `dea-catalog-business-capabilities` (canonical host; 13 finer-grained bindings are disclosed mv1 residuals awaiting binding reconciliation). Drop the "Business Capability … remain here" and "pure Business Service host" sentences; keep the relocation history table (PRs #3/#4).
- **Governance wording**: replace the branch-protection/CODEOWNERS claim with what is real — enforcement via the blocking CI gates (`catalog-conformance`, `validate-allocation`); CODEOWNERS/branch protection recorded as unavailable on the current GitHub plan (org backlog).
- **Local gates snippet**: add the verified invocations (venv note; `--schema catalog-index-schema/catalog-index-schema.json` on regenerator/index gate — documents the vendored `DEFAULT_SCHEMA_PATH` footgun instead of diverging the copies from the pinned tag, per CR-SVC-001 §4).
- **BusinessService example**: keep; ids are already in the `services:*` family; fix the example's cross-references to the entity-scope wording above.

## 4. Model-side dependency (specified here, landed separately)

Regenerating the pointer requires the root model to know the new name first (`metamodel-pointer.yaml` header: do-not-edit-manually; structural changes via ADR + minor bump in `dea-architecture-framework`). The dependency PR, to be filed in that repo: rename both pre-rename `catalog_repo` values in `model/opendeam-model.yaml` (Business Service entity block + shared Solution Component block) → `dea-catalog-business-services`, carried by an ADR + minor bump per that repo's governance; then this repo regenerates `metamodel-pointer.yaml` from the released model version and re-runs `validate-allocation`. Until then the pointer stays as-generated (green against the equally-stale model); hand-editing it now would be reverted at the next regeneration — hence this CR does not touch it.

## 5. Hygiene

- Relocate `CATALOG/v1-alpha/governance-contracts/sla-classification.yaml` → `classifications/sla-classification.yaml` (the register directory exists for exactly this class of vocabulary; kills the last `CATALOG/` vestige — remove the empty tree). Content unchanged. The README §3 rewrite points at the new path; `CR-CATALOG-STRUCT-04.md`'s reference stays historical under its existing layout-note banner (landed CRs are not rewritten).
- Delete `tools/extract_dbsf_entities.py` (spent one-shot; its source tree is gone; git history preserves it) and the `tools/` directory if empty.
- Append this CR's `### CR-SVC-003` entry under `[Unreleased]` in `CHANGELOG.md` (per CR-SVC-002 §6 landing-order contract); add this CR's row to `change-requests/README.md`.

## 6. NOT-List

- NOT an edit to `metamodel-pointer.yaml` (§4: blocked on the model-side rename; do-not-edit contract).
- NOT the `dea-architecture-framework` model PR itself (separate repo, separate governance; specified in §4 for immediate filing).
- NOT vendoring an authorship gate into this repo (`check_authorship.py` has no canonical home in `dea-metaframework`; the sibling copies were authored in-repo there — blocked until upstream ships one; the §2 correction removes the only current violation).
- NOT CODEOWNERS/branch-protection enablement (GitHub plan limitation; org-level decision).
- NOT CI pip/action pinning (deferred backlog, recorded with CR-SVC-001 §4's deferred items).
- NOT binding reconciliation for the 13 `dea:capability-*` bindings or the unregistered `dea:component-*`/`dea:principle-*`/`dea:pattern-*` namespaces (CR-SVC-mv1 §2 residuals — a content decision needing the capabilities catalog's admission process; separate CR).
- NOT any entity-record, id, mapping, or viewpoint content change.

## 7. Acceptance criteria (verifiable from a clean clone of the landing PR)

1. A repo-wide content grep for the Wave 0a pre-rename repository name (the hyphenated factory name; reconstruct it from `metamodel-pointer.yaml` `repository:`) returns hits only in historical artifacts: the two landed CR bodies and layout-note banners, `reconciliation/` (migration map, cross-check), `CHANGELOG.md` history sections, and `metamodel-pointer.yaml` (unchanged per §4). README has zero hits.
2. `grep -rn "CODEOWNERS\|branch protection" README.md` → no enforcement claim; the CI-gates sentence is present.
3. A repo-wide grep for the denylisted agent signature (the denylisted agent-name prefix; see §2) → zero hits.
4. `test -f classifications/sla-classification.yaml && test ! -e CATALOG && test ! -e tools/extract_dbsf_entities.py` → all true; `mappings/`, `viewpoints/`, `reconciliation/` untouched.
5. README Structure section lists `entities/v1-alpha/<slug>-<hash>/`, `classifications/sla-classification.yaml`, `catalog-index-schema/`, `metamodel-pointer.yaml`, `TEMPLATE_VERSION`; Entity Scope names Business Service (primary) + Solution Component (shared) only.
6. `CHANGELOG.md` `[Unreleased]` contains `### CR-SVC-003`; `change-requests/README.md` carries its row.
7. Gates green: `check_id_system.py --strict` CONFORMANT (18/0); `regenerate_catalog.py --check --schema catalog-index-schema/catalog-index-schema.json` exit 0; CST suite at the pinned tag `--strict` 16/16; CI green on the landing PR.
