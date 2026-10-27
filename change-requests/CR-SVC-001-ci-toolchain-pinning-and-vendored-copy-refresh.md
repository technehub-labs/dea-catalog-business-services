# CR-SVC-001: CI Toolchain Pinning + Vendored Copy Refresh

**Status**: Merged
**Layer**: L1 (catalog operations: CI, vendored toolchain)
**Owner**: Emmanuel A. Otchere
**Date**: 2026-10-27
**Trigger**: Full-repo review 2026-10-27 (user directive: "lets work on the repo" → "proceed"; report at workspace `review-report-dea-catalog-business-services.md`) found CI green only because its last run predates the 2026-10-22 CST-013/014 redefinition in `dea-metaframework`. Prepared by the review agent under eaojnr's direction; authorship of record per the Authorship Cardinal Rule (CR-BP-118 / CR-DEA-BC-34).
**Carrier**: Single PR on feature branch `feat/CR-SVC-001-ci-toolchain-pinning`. PR review, not direct push (CR-BP-116 pattern).
**Lands against**: `main`

## 1. Problem statement (verified 2026-10-27, `main` @ `63c3ddc`)

| Check | Result |
|---|---|
| CST suite at metaframework `main` (`3ad9bdd`) | exit 2 — CST-013 + CST-014: `dea-metaframework` checked out but not at a release tag |
| Last `catalog-conformance` run on `main` | success, 2026-09-21 (PR #8) — predates the CST-013/014 redefinition (`a10ddf8`, 2026-10-22) |
| Vendored `scripts/regenerate_catalog.py`, `scripts/check_catalog_index.py` vs upstream | old hash-alphabet regex `[a-z2-9]{6}`; upstream since `4d421be` (2026-09-21, ⊆ v2.6.0) uses the 31-symbol visually-unambiguous alphabet |
| Vendored `catalog-index-schema/catalog-index-schema.json` vs upstream | same regex divergence (id `pattern` field) |
| Bare local gate run (`python scripts/check_catalog_index.py`) | exit 1 — `DEFAULT_SCHEMA_PATH` is `tools/catalog-index-schema.json`, which does not exist in this repo |

Every future PR or `main` push runs the current CST suite (the checkout is unpinned, so CI tracks the moving target) and fails CST-013/014. This is the identical defect CR-DEA-BC-37 §4 fixed in the capabilities catalog.

## 2. Pin the metaframework checkout (CST-013/014 canonical shape)

In `.github/workflows/catalog-conformance.yml`, step "Fetch catalog index machinery from dea-metaframework":

```yaml
        with:
          repository: technehub-labs/dea-metaframework
          path: .metaframework
          ref: v2.6.0          # latest release tag at authoring; re-verify at landing
```

`v2.6.0` (cut 2026-10-21) contains the id-regex fix (`4d421be`) and does **not** contain the CST-013/014 redefinition (`a10ddf8` is post-tag), so the pinned suite's file-presence semantics pass with vendored copies present — and when a later tag bump pulls in the new "pinned upstream resolution" semantics, this repo passes by construction, because §3 below satisfies exactly that shape (pin + tools sourced from `.metaframework/tools/`).

## 3. Always stage tools from the pinned checkout; refresh the vendored copies

- The "Install regenerator + gate + schema" step drops the `if [ ! -f … ]` vendored-preference guards: unconditionally `cp` `regenerate_catalog.py`, `check_catalog_index.py` (to `scripts/`) and `catalog-index-schema.json` (to `catalog-index-schema/`) out of the pinned checkout. CI therefore runs exactly the pinned tag's code (the CST canonical shape; also keeps CST-015 satisfied, since the workflow still invokes `python scripts/…`). `scripts/check_id_system.py` is repo-native (CR-SVC-mv1), not copied, and is untouched.
- The committed vendored copies of the same three files are refreshed from the `v2.6.0` tag in this PR, restoring local↔CI parity and bringing the 31-symbol hash regex into the vendored validator and schema. All 18 current hashes already conform to the stricter alphabet (verified), so no record changes.
- Add `timeout-minutes: 15` to the `catalog-conformance` job.
- Add `fetch-depth: 0` to the repo checkout step. Verified while landing: the regenerator's `last_modified` machinery (`git_last_commit_date`) runs `git log -1 -- <entity subtree>`; under the default depth-1 CI checkout every subtree resolves to HEAD's date, so all 18 dates churn to the PR merge date and the freshness gate fails on any PR merged on a later day (reproduced locally with a depth-1 clone: exit 3; the September merges only passed because PRs #7/#8 merged the same day `CATALOG.yaml` was last regenerated). Full history makes each subtree resolve to its true last-touch commit, matching the committed index.

## 4. NOT-List

- NOT a fix for `count_open_change_requests` (`scripts/regenerate_catalog.py:518` duplicated condition; `Merged`-only closed set): once §3 lands, CI computes counts with the pinned upstream copy, so a local counter fix would diverge from CI and fail the freshness gate. The data-side truth fix is CR-SVC-002; the code fix belongs upstream in `dea-metaframework` (follow-up recorded in CR-SVC-002 §7).
- NOT a change to `DEFAULT_SCHEMA_PATH` in the vendored scripts (they stay byte-identical to the tag; the local invocation, including `--schema catalog-index-schema/catalog-index-schema.json`, is documented in the README via CR-SVC-003 §3 instead).
- NOT a pip/action pinning sweep (`pyyaml`/`jsonschema`/`pytest` unpinned, actions by tag — deferred backlog, same class as CR-DEA-BC-39's deferred items).
- NOT a change to `validate-allocation.yml` (already pinned: reusable workflow and `model_ref` both at `v0.2.1`).
- NOT any catalog-content change: no entity, id, schema-shape, mapping, or viewpoint edits.

## 5. Acceptance criteria (verifiable from a clean clone of the landing PR)

1. `.github/workflows/catalog-conformance.yml`: the metaframework checkout step carries `ref: v2.6.0`; the copy step references `.metaframework/tools/regenerate_catalog.py`, `.metaframework/tools/check_catalog_index.py`, `.metaframework/tools/catalog-index-schema.json` without vendored-preference guards; the job declares `timeout-minutes`.
2. `grep -c "abcdefghjkmnpqrstuvwxyz23456789"` returns ≥ 1 in each of `scripts/regenerate_catalog.py`, `scripts/check_catalog_index.py`, `catalog-index-schema/catalog-index-schema.json`, and `[a-z2-9]{6}` no longer appears as the hash pattern in any of the three.
3. `diff <(git -C .metaframework show v2.6.0:tools/regenerate_catalog.py) scripts/regenerate_catalog.py` is empty (likewise the gate and the schema) — vendored copies byte-identical to the pinned tag.
4. Against a metaframework checkout at `v2.6.0`: CST suite `--strict` passes 16/16; `python scripts/regenerate_catalog.py --check --schema catalog-index-schema/catalog-index-schema.json` exits 0; `python scripts/check_catalog_index.py --strict --schema catalog-index-schema/catalog-index-schema.json` exits 0; `python scripts/check_id_system.py --strict` → CONFORMANT (18 records, 0 findings).
5. CI green on the landing PR (both workflows).
