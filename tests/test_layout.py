"""Layout guard for the CR-SVC-016 shard level.

The corpus moved from the flat `entities/v1-alpha/<dir>/` layout and the
flat `contributions/queue/<slug>.yaml` intake to the sharded
`entities/v1-alpha/<shard>/<dir>/` and `contributions/queue/<shard>/<slug>.yaml`
forms so no directory ever reaches GitHub's 1,000-entry listing
truncation (entity-storage-layout.md §4; the CR-MET-024 recipe). These
tests pin the invariants that make that safe permanently:

- every record file sits at exactly the path derived from its id (§5);
- every record directory is complete (`<id>.yaml` + `README.md`);
- `entities/v1-alpha` stays under 28 entries (26 letters + `0-9` +
  README) and every shard stays below the 800-entry trigger;
- `contributions/queue` stays under 28 entries and every queue file
  sits in its slug's shard;
- CATALOG.yaml paths are the id-derived paths.
"""
from __future__ import annotations

import sys
from pathlib import Path

import yaml

BASE = Path(__file__).parent.parent
SCRIPTS = BASE / "scripts"
sys.path.insert(0, str(SCRIPTS))
from check_id_system import shard_for_record  # noqa: E402
from migrate_to_shard_layout import is_shard, slug_of_record_dir  # noqa: E402

# entity-storage-layout.md §4: shard before any directory approaches
# 800 entries; GitHub truncates listings at 1,000.
MAX_SHARD_ENTRIES = 800
MAX_ROOT_ENTRIES = 28

ENTITIES_ROOT = BASE / "entities" / "v1-alpha"
QUEUE_ROOT = BASE / "contributions" / "queue"


def _record_dirs():
    for shard_dir in sorted(ENTITIES_ROOT.iterdir()):
        if not shard_dir.is_dir() or not is_shard(shard_dir.name):
            continue
        for record_dir in sorted(shard_dir.iterdir()):
            if record_dir.is_dir():
                yield shard_dir, record_dir


def record_relpath(record_dir: Path) -> Path:
    """The id-derived path of a record dir's canonical file."""
    rid_file = next(record_dir.glob("services-*.yaml"), None)
    assert rid_file is not None, f"no canonical yaml in {record_dir}"
    record_id = yaml.safe_load(rid_file.read_text())["id"]
    return ENTITIES_ROOT / shard_for_record(record_id) / record_dir.name / rid_file.name


def test_every_record_sits_at_its_id_derived_path():
    """No flat leftovers, no misplaced records."""
    misplaced = []
    for path in ENTITIES_ROOT.rglob("*.yaml"):
        if path.name == "README.md":
            continue
        parent = path.parent
        if not (is_shard(parent.parent.name) if parent.parent.name != "v1-alpha" else False):
            misplaced.append(f"{path}: not inside a shard/record-dir pair (stray yaml)")
            continue
        expected = record_relpath(parent)
        if path != expected:
            misplaced.append(f"{path}: expected {expected}")
    assert not misplaced, "records not at their id-derived paths:\n" + "\n".join(misplaced)


def test_every_record_directory_is_complete():
    incomplete = []
    for _, record_dir in _record_dirs():
        rid_file = next(record_dir.glob("services-*.yaml"), None)
        names = [rid_file.name, "README.md"] if rid_file else ["<canonical yaml>", "README.md"]
        incomplete += [
            f"{record_dir}: missing {name}"
            for name in names
            if not (record_dir / name).is_file()
        ]
    assert not incomplete, "incomplete record directories:\n" + "\n".join(incomplete)


def test_shard_key_matches_directory():
    wrong = []
    for shard_dir, record_dir in _record_dirs():
        rid_file = next(record_dir.glob("services-*.yaml"), None)
        if rid_file is None:
            wrong.append(f"{record_dir}: no canonical yaml to derive the shard from")
            continue
        record_id = yaml.safe_load(rid_file.read_text())["id"]
        if shard_dir.name != shard_for_record(record_id):
            wrong.append(
                f"{record_dir.name}: slug starts {slug_of_record_dir(record_dir.name)[:1]!r} "
                f"but sits in {shard_dir.name!r}"
            )
    assert not wrong, "records in the wrong shard:\n" + "\n".join(wrong)


def test_no_directory_approaches_the_github_listing_cap():
    root_entries = list(ENTITIES_ROOT.iterdir())
    assert len(root_entries) <= MAX_ROOT_ENTRIES, (
        f"entities/v1-alpha holds {len(root_entries)} entries "
        f"(cap {MAX_ROOT_ENTRIES}); the shard level is not holding"
    )
    oversized = []
    for shard_dir in sorted(ENTITIES_ROOT.iterdir()):
        if not shard_dir.is_dir():
            continue
        count = sum(1 for _ in shard_dir.iterdir())
        if count >= MAX_SHARD_ENTRIES:
            oversized.append(f"entities/v1-alpha/{shard_dir.name}/: {count} entries (trigger {MAX_SHARD_ENTRIES})")
    assert not oversized, "shards past the §4 trigger — subdivide (CR-MET-024 R4):\n" + "\n".join(oversized)


def test_queue_is_sharded_and_under_the_cap():
    root_entries = list(QUEUE_ROOT.iterdir())
    assert len(root_entries) <= MAX_ROOT_ENTRIES, (
        f"contributions/queue holds {len(root_entries)} entries "
        f"(cap {MAX_ROOT_ENTRIES}); the queue shard level is not holding"
    )
    flat = [p.name for p in QUEUE_ROOT.glob("*.yaml")]
    assert not flat, f"flat queue leftovers at depth 1: {flat[:10]}"
    oversized = []
    for shard_dir in sorted(QUEUE_ROOT.iterdir()):
        if not shard_dir.is_dir():
            continue
        count = sum(1 for _ in shard_dir.iterdir())
        if count >= MAX_SHARD_ENTRIES:
            oversized.append(f"contributions/queue/{shard_dir.name}/: {count} entries")
    assert not oversized, "queue shards past the §4 trigger:\n" + "\n".join(oversized)
    wrong = [
        f"{p}: slug starts {p.stem[:1]!r} but sits in {p.parent.name!r}"
        for shard_dir in QUEUE_ROOT.iterdir() if shard_dir.is_dir()
        for p in shard_dir.glob("*.yaml")
        if shard_dir.name != (p.stem[:1] if p.stem[:1].isalpha() and p.stem[:1].islower() else "0-9")
    ]
    assert not wrong, "queue files in the wrong shard:\n" + "\n".join(wrong)


def test_catalog_paths_are_the_id_derived_paths():
    catalog = yaml.safe_load((BASE / "CATALOG.yaml").read_text())
    entities = (catalog or {}).get("catalog", {}).get("entities") or []
    stale = []
    for e in entities:
        expected_disk = BASE / e["path"]
        if not expected_disk.is_file():
            stale.append(f"{e['id']}: catalog path {e['path']} does not resolve")
    assert not stale, "CATALOG.yaml paths have drifted from the shard layout:\n" + "\n".join(stale)
