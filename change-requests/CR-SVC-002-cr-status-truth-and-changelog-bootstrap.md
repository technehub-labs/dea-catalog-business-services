# CR-SVC-002: CR Status Truth + CHANGELOG Bootstrap

**Status**: Merged
**Layer**: L1 (catalog operations: change-request bookkeeping, index, changelog)
**Owner**: Emmanuel A. Otchere
**Date**: 2026-10-27
**Trigger**: Full-repo review 2026-10-27 (user directive: "lets work on the repo" → "proceed") found `CATALOG.yaml` reporting `open_change_requests: 2` while zero CRs are open — both landed CRs still carry their authoring-time status. Prepared by the review agent under eaojnr's direction; authorship of record per the Authorship Cardinal Rule (CR-BP-118 / CR-DEA-BC-34).
**Carrier**: Single PR on feature branch `feat/CR-SVC-002-cr-status-truth`. PR review, not direct push.
**Lands against**: `main`
**Depends on**: none hard. Landing-order contract: **after CR-SVC-001** (see §6), so the count is regenerated under the pinned toolchain.

## 1. Problem statement (verified 2026-10-27, `main` @ `63c3ddc`)

- `change-requests/CR-CATALOG-STRUCT-04.md` — `**Status**: Proposed`, landed via PR #6 (merged 2026-09-05).
- `change-requests/CR-SVC-mv1.md` — `**Status**: Proposed`, landed via PR #7 (merged 2026-09-21).
- Committed `CATALOG.yaml` → `open_change_requests: 2`. Truthful count: 0.
- The counter (`scripts/regenerate_catalog.py:499-529`) carries the org-wide family bug: duplicated condition at line 518 (the same closed-status probe appears on both sides of the `or`; the second operand was meant to be a different closed status), and the closed set is `Merged` only — **the same bug exists in upstream `dea-metaframework` at `main`**, and CR-SVC-001 §3 makes CI compute counts with the pinned upstream copy. A local counter fix would therefore diverge from CI and fail the `--check` freshness gate. (Drafting note: CR heads must not quote these probe strings verbatim within their first 30 lines — the substring match would misclassify the CR itself.)

## 2. Status vocabulary (decision of record)

This repo adopts, effective with this CR:

| Status | Meaning | Counter treatment |
|---|---|---|
| `Draft`, `Proposed` | not landed | open |
| `Merged` | landed via its carrier PR | closed |
| `Rejected`, `Superseded` | not landed / replaced | conservative-open (documented limitation, §7) |

Rationale: `Merged` is the one closed status the *effective* toolchain (vendored copies and pinned CI copies alike) already recognizes, so the count becomes truthful with zero tool delta — no local divergence from the pinned upstream code (the divergence trap is §1's third bullet). `Merged` remains closed under any future upstream counter fix, so the vocabulary is forward-compatible. Cross-repo note: the capabilities catalog instead fixed its counter locally and kept its `Landed/Applied/…` vocabulary (CR-DEA-BC-38 §2); that repo runs vendored copies in CI, this one will run pinned upstream copies — each vocabulary must match its effective toolchain until the upstream counter fix unifies them.

## 3. Recorded status backfill (not silent rewrites)

Landed CRs are immutable; corrections are recorded by later PRs (house rule; GOVERNANCE §2.2 in the sibling catalogs). This section is that record:

- `change-requests/CR-CATALOG-STRUCT-04.md`: `**Status**: Proposed` → `**Status**: Merged`, plus one line under the metadata block: `> **Correction (CR-SVC-002, 2026-10-27):** Status backfilled Proposed → Merged; landed via PR #6 (merged 2026-09-05).`
- `change-requests/CR-SVC-mv1.md`: same change, citing PR #7 (merged 2026-09-21).
- `change-requests/README.md`: the two index rows' Status column `Proposed` → `Merged`.

## 4. CHANGELOG.md bootstrap

Create `CHANGELOG.md` (Keep-a-Changelog adapted, shape mirroring `dea-catalog-business-capabilities/CHANGELOG.md`):

- Header: purpose + versioning note (this repo has no release procedure yet; entries track CR landings and PRs).
- `## [Unreleased]` — empty at bootstrap, filled by subsequent landings per the house convention.
- Retrospective sections, in landing order:
  - `### CR-CATALOG-STRUCT-04` — DBSF adoption: 18 `BusinessService` records into per-entity subtrees, vendored regenerator/gate/schema, `catalog-conformance.yml`, `CATALOG.yaml` + `TEMPLATE_VERSION` (PR #6, 2026-09-05).
  - `### CR-SVC-mv1` — org-wide id-system migration Wave 2b: 18 records → `services:service-<slug>-<hash>`, flat layout, `check_id_system.py` gate (IDM-001..008) wired into CI, id map + cross-check report, disclosed residuals (PR #7, 2026-09-21).
  - `### docs: entity README template mirror` — per-entity READMEs mirrored from processes PR #153 (PR #8, 2026-09-21).
  - `### CR-SVC-001` — CI toolchain pinning + vendored refresh (PR landing this CR-SVC-001, filled at that landing; see §6).
- A one-line pre-CR history note: PRs #3/#4 (2026-08-08/09) announced entity relocations, before CR tracking began.

## 5. Regenerate `CATALOG.yaml` in the same PR

`python scripts/regenerate_catalog.py --schema catalog-index-schema/catalog-index-schema.json` → `open_change_requests: 2 → 0`. The freshness gate is blocking in CI; the regeneration rides the same PR per the house landing convention.

## 6. Landing-order contract for CR-SVC-001/002/003

1. CR-SVC-001 lands (its PR flips its own `**Status**` to `Merged`; CHANGELOG does not exist yet — §4's bootstrap records it retrospectively; `open_change_requests` stays 2 at this landing: the two stale rows are §3's target, not 001's).
2. This CR lands (backfill §3 + CHANGELOG §4 + regeneration §5 → open count 0).
3. CR-SVC-003 lands (appends its `### CR-SVC-003` entry under `[Unreleased]`; flips its own status; open count stays 0).

Each landing PR carries exactly one CR file (status `Merged`), its implementation, the regenerated `CATALOG.yaml`, its CHANGELOG entry, and its `change-requests/README.md` row update; the not-yet-landed proposals stay out of the repo until their turn.

## 7. NOT-List

- NOT a code change to `count_open_change_requests` or any vendored script (see §1; upstream fix in `dea-metaframework` — this CR records that follow-up: fix the duplicated condition, recognize `Rejected`/`Superseded` as closed, and tag a release so this repo can adopt it via the §CR-SVC-001 pin).
- NOT table-format status parsing (`| **Status** | … |`) — this repo's CRs use bold-line metadata only.
- NOT a CR-metadata validator/gate (no `check_cr_metadata.py` equivalent exists here; a future CR may vendor one).
- NOT renumbering, renaming, or restructuring the existing CR files beyond the §3 status corrections.
- NOT a pointer/`open_change_requests`-schema change beyond the regenerated value.

## 8. Acceptance criteria (verifiable from a clean clone of the landing PR)

1. `grep -n "^\*\*Status\*\*" change-requests/CR-*.md` → both pre-existing CRs report `Merged`; each carries the dated correction line; my CR-SVC-001/002 files likewise reflect their landed state at their own landings.
2. `python scripts/regenerate_catalog.py --check --schema catalog-index-schema/catalog-index-schema.json` exits 0 against the committed `CATALOG.yaml`, whose `counts.open_change_requests` is `0`.
3. `CHANGELOG.md` exists with `[Unreleased]` and the retrospective sections listed in §4.
4. `git diff` of the landing PR shows no changes under `scripts/` or `catalog-index-schema/` (toolchain untouched; CR-SVC-001 already refreshed the copies).
5. `change-requests/README.md` rows for CR-CATALOG-STRUCT-04 and CR-SVC-mv1 read `Merged`.
6. CI green on the landing PR.
