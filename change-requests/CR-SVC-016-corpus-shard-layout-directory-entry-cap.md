# CR-SVC-016: Corpus Shard Layout (Directory-Entry Cap)

**Status**: Proposed
**Layer**: Catalog structure (storage layout, entity-storage-layout.md §4)
**Owner**: Emmanuel A. Otchere
**Date**: 2026-11-10
**Trigger**: Owner directive 2026-11-09: an org-wide audit and enforcement scheme for directories nearing GitHub's 1,000-entry listing cap, remediated the metrics/processes way when tripped. This repo carries the org's two hottest watch entries (reconciler R5, dea-governance CR-019, first live run 2026-11-10): `entities/v1-alpha` at 535 record directories and `contributions/queue` at 517 flat intake files, both growing (the CR-SVC-004 admission programme continues), both approaching the 800-entry shard trigger with 1,000 hard truncation behind it.
**Carrier**: Single PR on feature branch `feat/cr-svc-016-shard-layout`. PR review, not direct push.
**Lands against**: `main`
**Depends on**: CR-SVC-001 (pinned toolchain), CR-SVC-004 (the intake workflow this CR shards behind), CR-MET-024 in dea-catalog-metrics (the sharding recipe), CR-CATALOG-STRUCT-11 in dea-metaframework (CST-017; v2.7.0 pin target).

## 1. What changes

| Site | Change |
|---|---|
| `entities/v1-alpha/<slug>-<hash>/` (535 dirs) | `git mv` to `entities/v1-alpha/<shard>/<slug>-<hash>/`; `<shard>` = first character of the slug (`0-9` for digit-leading); 24 letter shards land (largest `c/` at 90) |
| `contributions/queue/<slug>.yaml` (517 files) | `git mv` to `contributions/queue/<shard>/<slug>.yaml`; same key |
| `entities/v1-alpha/<shard>/README.md`, `contributions/queue/<shard>/README.md` | new shard READMEs naming the rule |
| `reconciliation/migration-id-map.yaml` | new: migration header + 535 from/to entries |
| `scripts/regenerate_catalog.py` | re-vendored from dea-metaframework v2.7.0 (carries the CR-ECF-011 truthful CR-status counter and the hyphen-form infer_state repair); `list_subtrees` and `entity_path_for` made shard-aware (flat form still accepted across the migration window) |
| `scripts/check_id_system.py` | IDM-005 path derivation becomes `entities/v1-alpha/<shard>/<dir>/<file>` via the new `shard_for_record()`; `_load_all_records()` walks both layout eras |
| `scripts/check_contributions.py` | queue walk covers `<shard>/<slug>.yaml` (flat still accepted) |
| `scripts/admit_entity.py` | new records write into the slug's shard; `existing_ids()` walks both eras |
| `scripts/check_catalog_index.py` | vendored copy's `list_subtrees` made shard-aware |
| `scripts/migrate_to_shard_layout.py` | new: `--dry-run/--execute/--verify`, chunked `git mv`, shard READMEs, id map; idempotent |
| `tests/test_layout.py` | new: 6 layout guards (id-derived paths; complete record dirs; shard-key correctness; both roots' entry caps; queue shard correctness; CATALOG paths resolve), `MAX_SHARD_ENTRIES = 800` |
| `.github/workflows/catalog-conformance.yml` | toolchain pin v2.6.0 -> v2.7.0 (CST-017 reachability); staging step flips to vendored-copies-preferred (install-if-missing), matching the workflow's own stated convention and the processes pattern: the vendored copies carry this repo's shard-aware walks, which the generic upstream tools do not implement, so an unconditional `cp` would clobber them in CI; `pytest tests/test_layout.py -q` step added |

## 2. The shard rule

The CR-MET-024 ruling set, lifted to this repo: one shard level under each root, keyed on the first character of the slug (record id minus `services:service-` prefix and `-<hash>` suffix; queue filename minus `.yaml`); lowercase letters `a`..`z`, everything else `0-9`. **The id system does not change** (record ids, content, and record READMEs are byte-identical); only paths move. The path stays derivable from the id alone (entity-storage-layout.md §5), now including the shard key. After the move: `entities/v1-alpha` holds 25 entries (24 letter shards + `.gitkeep`), `contributions/queue` holds 24 (23 letter shards + `.gitkeep`), and the worst shard holds 90 entries, a compression from 535/517 to 25/24 with 800-entry headroom in every directory.

## 3. The infer_state repair (named side effect)

Re-vendoring the v2.7.0 regenerator repairs a pre-existing index defect: the old vendored copy probed the colon-form `<entity_id>.yaml` (e.g. `services:service-....yaml`) for the canonical file, while every record file on disk carries the hyphen form (`services-service-....yaml`), so `read_canonical_yaml` found nothing and every admitted record classified `candidate`. The same defect was fixed per-repo in stakeholders (CR-CATALOG-STRUCT-12, the hyphen-form infer_state repair; steward_note exposure resolved) and metrics; v2.7.0 is the source fix. Consequence, verified: the regenerated index flips `candidates: 535 / canonical: 0` to `candidates: 0 / canonical: 535`, matching what the records actually are (535 records admitted canonical through the CR-SVC-004 8-step admission gate, each carrying `lifecycle_status: active`). The dea-governance register row for this repo (`state: skeleton, canonical_count: 0`) was reconciled green against the lying index; a register refresh (CR-020, register v11) follows this landing so R3 stays truthful. The CR-status counter fix (CR-ECF-011) also lands here: `open_change_requests` becomes truthfully computed over the closed set `{Merged, Landed, Applied, Accepted, Rejected, Superseded, Withdrawn}`; observed 0.

## 4. Verification (all run locally on the migrated tree)

1. `scripts/migrate_to_shard_layout.py --verify`: PASS (no flat leftovers, no misplaced records).
2. `scripts/regenerate_catalog.py --check`: current; re-run byte-idempotent.
3. `scripts/check_catalog_index.py --strict`: OK, 535 entities, 0 warnings (the 24 pre-edit shard-letter warnings gone).
4. `scripts/check_id_system.py --strict`: 535 records, 0 findings.
5. `scripts/check_id_system.py --base-ref origin/main` (IDM-008, PR-scoped): CONFORMANT over 1,645 changed files, 0 blocking.
6. `scripts/check_contributions.py`: CONFORMANT, 517 queue files.
7. `python -m pytest tests/test_layout.py -q`: 6 passed.
8. Cross-repo conformance suite (v2.7.0): **17/17 CSTs passed**, 0 warnings.
9. Record-count parity: 535 record dirs and 517 queue files before and after (`git status` rename detection preserves history; only renames plus the named new files in the diff).

## 5. NOT-List

- **No id, content, or record-README change**: pure storage-layout move; the id map exists precisely so downstream consumers can resolve stale paths.
- **No register or metamodel edits**: the governance register refresh is dea-governance CR-020; the metamodel naming-drift reconciliation (repo renamed to dea-catalog-business-services; pointer still says dea-catalog-digital-business-service-factory) remains its own named follow-up.
- **No queue semantics change**: statuses, the register, and the admission flow are untouched; only file locations move.
- **No CATALOG.yaml by hand**: regenerated by the vendored tool in the same PR (part 2 commit), after the migration commit, so `last_modified` git-log dates resolve deterministically in CI.
- **No intake pipeline rewrite**: the workspace-side batch drivers (`generate_queue.py`, `admit_batch.py` in the OpenDEA workspace tools) are updated to the sharded queue paths after this lands; the repo-side gates accept both eras until then.

## 6. Acceptance criteria

1. CI green on this PR, including the CST suite at the v2.7.0 pin (17 CSTs, `--strict`), the ID system gate, the queue gate, the index gate, and the new layout tests.
2. `migrate_to_shard_layout.py --verify` exits 0 on the merged tree.
3. `entities/v1-alpha` and `contributions/queue` each hold fewer than 30 entries; no tracked directory holds 500+ entries anywhere in the repo (the R5 watch tier clears for this repo).
4. `CATALOG.yaml` counts read `canonical: 535, candidates: 0, entities: 535, open_change_requests: 0`.
