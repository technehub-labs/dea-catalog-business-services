#!/usr/bin/env python3
"""CR-SVC-016: migrate the corpus to the slug-first-letter shard layout.

Moves every record directory from the flat
`entities/v1-alpha/<slug>-<hash>/` form to
`entities/v1-alpha/<shard>/<slug>-<hash>/`, and every queue intake file
from `contributions/queue/<slug>.yaml` to
`contributions/queue/<shard>/<slug>.yaml`, where `<shard>` is the first
character of the slug (lowercase ASCII letters; digit-leading slugs go
to `0-9`). Ids, record content, READMEs and queue content are untouched:
this is a storage-layout move only (entity-storage-layout.md §4; the
CR-MET-024 recipe). GitHub truncates a directory listing at 1,000
entries and both roots were approaching the trigger (535 and 517).

The move is staged with `git mv` so rename detection preserves history,
and the script emits `reconciliation/migration-id-map.yaml` (id ->
previous path -> new path) so downstream consumers can resolve stale
paths. Each shard directory receives a short README naming the shard
rule.

Usage:
    python3 scripts/migrate_to_shard_layout.py --dry-run
    python3 scripts/migrate_to_shard_layout.py --execute
    python3 scripts/migrate_to_shard_layout.py --verify

The script is idempotent: re-running on a migrated tree no-ops.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
ENTITIES_ROOT = ROOT / "entities" / "v1-alpha"
QUEUE_ROOT = ROOT / "contributions" / "queue"
MAP_PATH = ROOT / "reconciliation" / "migration-id-map.yaml"

GIT_MV_CHUNK = 50  # keep each git mv invocation well inside argv limits

ENTITY_SHARD_README = """# Shard `{shard}`

CR-SVC-016 bucket for record slugs starting with `{shard}`. The shard
key is the first character of the record's slug (the id minus the
`services:service-` prefix and the `-<hash>` suffix); digit-leading
slugs live in `0-9/`. The path stays derivable from the id alone
(entity-storage-layout.md §5):
`entities/v1-alpha/<shard>/<slug>-<hash>/<id>.yaml`.
"""

QUEUE_SHARD_README = """# Queue shard `{shard}`

CR-SVC-016 bucket for intake submissions whose slug starts with
`{shard}`; digit-leading slugs live in `0-9/`. The queue gate
(`scripts/check_contributions.py`) and the admission tool
(`scripts/admit_entity.py`) resolve the shard from the filename, so the
intake path stays derivable from the submission slug alone.
"""


def is_shard(name: str) -> bool:
    return name == "0-9" or (len(name) == 1 and name.isalpha() and name.islower())


def shard_for_slug(slug: str) -> str:
    first = slug[:1]
    return first if first.isalpha() and first.islower() else "0-9"


def slug_of_record_dir(name: str) -> str:
    """The slug part of a record dir name `<slug>-<hash6>`."""
    return name.rsplit("-", 1)[0]


def flat_record_dirs() -> list[Path]:
    """Depth-1 record directories (the flat-era leftovers)."""
    return sorted(
        p for p in ENTITIES_ROOT.iterdir()
        if p.is_dir() and not is_shard(p.name)
    ) if ENTITIES_ROOT.exists() else []


def flat_queue_files() -> list[Path]:
    """Depth-1 intake submissions (the flat-era leftovers)."""
    return sorted(
        p for p in QUEUE_ROOT.glob("*.yaml")
    ) if QUEUE_ROOT.exists() else []


def git_mv(sources: list[Path], dest_dir: Path) -> None:
    subprocess.run(
        ["git", "mv", *[str(s) for s in sources], str(dest_dir)],
        cwd=ROOT, check=True,
    )


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true", help="plan the moves; write nothing")
    mode.add_argument("--execute", action="store_true", help="git mv the flat records and queue files into shards")
    mode.add_argument("--verify", action="store_true", help="assert the tree is fully migrated")
    args = ap.parse_args()

    if args.verify:
        stale: list[str] = []
        for path in ENTITIES_ROOT.rglob("*/*.yaml"):
            rel_parent = path.parent
            if rel_parent.parent.name != "v1-alpha" or is_shard(rel_parent.parent.name):
                continue
            shard = shard_for_slug(slug_of_record_dir(rel_parent.name))
            if rel_parent != ENTITIES_ROOT / shard / rel_parent.name:
                stale.append(f"misplaced: {path.relative_to(ROOT)}")
        for path in flat_record_dirs():
            stale.append(f"flat entity dir: {path.relative_to(ROOT)}")
        for path in flat_queue_files():
            stale.append(f"flat queue file: {path.relative_to(ROOT)}")
        if stale:
            print("FAIL: tree is not fully migrated")
            for s in stale[:20]:
                print(f"  {s}")
            print(f"  ({len(stale)} total)")
            return 1
        print("PASS: every record dir and queue file sits at its shard path")
        return 0

    flat = flat_record_dirs()
    qflat = flat_queue_files()
    if not flat and not qflat:
        print("PASS: nothing to migrate (no flat record dirs or queue files)")
        return 0

    planned: dict[str, list[tuple[Path, Path]]] = {}
    for record_dir in flat:
        shard = shard_for_slug(slug_of_record_dir(record_dir.name))
        planned.setdefault(shard, []).append(
            (record_dir, ENTITIES_ROOT / shard / record_dir.name)
        )
    qplanned: dict[str, list[tuple[Path, Path]]] = {}
    for qf in qflat:
        shard = shard_for_slug(qf.stem)
        qplanned.setdefault(shard, []).append(
            (qf, QUEUE_ROOT / shard / qf.name)
        )

    total = sum(len(m) for m in planned.values())
    qtotal = sum(len(m) for m in qplanned.values())
    print(f"flat record directories: {total}")
    for shard in sorted(planned):
        print(f"  entities/v1-alpha/{shard}/: {len(planned[shard])}")
    print(f"flat queue files: {qtotal}")
    for shard in sorted(qplanned):
        print(f"  contributions/queue/{shard}/: {len(qplanned[shard])}")
    if args.dry_run:
        print("dry run: no changes written")
        return 0

    id_map: list[dict] = []
    for shard in sorted(planned):
        shard_dir = ENTITIES_ROOT / shard
        shard_dir.mkdir(parents=True, exist_ok=True)
        readme = shard_dir / "README.md"
        if not readme.exists():
            readme.write_text(ENTITY_SHARD_README.format(shard=shard))
        moves = planned[shard]
        for start in range(0, len(moves), GIT_MV_CHUNK):
            chunk = moves[start:start + GIT_MV_CHUNK]
            git_mv([src for src, _ in chunk], shard_dir)
        for src, dst in moves:
            id_map.append({
                "id": f"services:service-{slug_of_record_dir(src.name)}-{src.name.rsplit('-', 1)[1]}",
                "from": str(src.relative_to(ROOT)),
                "to": str(dst.relative_to(ROOT)),
            })
    for shard in sorted(qplanned):
        shard_dir = QUEUE_ROOT / shard
        shard_dir.mkdir(parents=True, exist_ok=True)
        readme = shard_dir / "README.md"
        if not readme.exists():
            readme.write_text(QUEUE_SHARD_README.format(shard=shard))
        moves = qplanned[shard]
        for start in range(0, len(moves), GIT_MV_CHUNK):
            chunk = moves[start:start + GIT_MV_CHUNK]
            git_mv([src for src, _ in chunk], shard_dir)

    MAP_PATH.parent.mkdir(parents=True, exist_ok=True)
    MAP_PATH.write_text(yaml.dump(
        {
            "migration": "CR-SVC-016",
            "rule": {
                "entities": "entities/v1-alpha/<slug-first-letter|0-9>/<slug>-<hash>/<id>.yaml",
                "queue": "contributions/queue/<slug-first-letter|0-9>/<slug>.yaml",
            },
            "moved": {"entity_dirs": len(id_map), "queue_files": qtotal},
            "records": id_map,
        },
        sort_keys=False, width=100, allow_unicode=True,
    ))
    print(f"PASS: {len(id_map)} record dirs + {qtotal} queue files moved; "
          f"map written to {MAP_PATH.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
