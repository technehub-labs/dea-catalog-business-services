#!/usr/bin/env python3
"""Entity admission tool (CR-SVC-004).

Turns a queued intake submission (``contributions/queue/<slug>.yaml``) into a
canonical entity subtree:

- validates the submission via the queue gate (``check_contributions``)
- derives the slug (explicit or from ``name``)
- assigns the record id ``services:service-<slug>-<hash6>`` where ``<hash6>`` is
  the id-system.md section 2.5 suffix: first 4 bytes of the SHA-256 of the
  canonical YAML serialization of the intake content, big-endian, 6 base-31
  digits over the visually-unambiguous alphabet (same derivation as
  CR-SVC-mv1's ``migrate_to_new_ids.py``). The preimage here is the intake
  content mapping (everything except queue metadata) dumped with sorted keys —
  deterministic for a given submission. Assigned once; never recomputed
  (rename-stability contract, id-system.md section 2.5).
- checks the id against every existing record id (collision aborts)
- scaffolds ``entities/v1-alpha/<slug>-<hash>/`` — record YAML (``id``,
  ``type: BusinessService``, ``version: 0.1.0``, content) + per-entity
  ``README.md`` (IDM-007; same shape as the mv1-generated ones)
- marks the queue entry ``status: admitted`` with the assigned id and date
- runs the id-system gate over the result (admission is gate-verified)

The admission PR then regenerates ``CATALOG.yaml`` (18 -> 19 entities), adds
the CHANGELOG entry, and records the admission CR/index row per house rules.

Usage:
  python scripts/admit_entity.py contributions/queue/<slug>.yaml [--dry-run]
"""

from __future__ import annotations

import hashlib
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
from check_contributions import _register, validate_queue_file  # noqa: E402

REPO = Path(__file__).resolve().parents[1]
ENTITIES = REPO / "entities" / "v1-alpha"
ALPHABET = "abcdefghjkmnpqrstuvwxyz23456789"  # id-system.md section 2.5 (31 symbols)
QUEUE_META = {"status", "slug", "submitted_by", "submitted", "assigned_id", "admitted"}


def content_hash(payload: dict) -> str:
    text = yaml.safe_dump(payload, sort_keys=True, allow_unicode=True, default_flow_style=False)
    digest = hashlib.sha256(text.encode("utf-8")).digest()
    val = int.from_bytes(digest[:4], "big")
    digits = []
    for _ in range(6):
        digits.append(ALPHABET[val % 31])
        val //= 31
    return "".join(reversed(digits))


def slug_from_name(name: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", name.strip().lower()).strip("-")
    slug = re.sub(r"-+", "-", slug)[:48].strip("-")
    if not slug:
        raise SystemExit("ERROR: cannot derive a slug from the given name")
    return slug


def existing_ids() -> set[str]:
    ids = set()
    for p in sorted(ENTITIES.glob("*/services-*.yaml")):
        try:
            rec = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
        except yaml.YAMLError:
            continue
        if isinstance(rec.get("id"), str):
            ids.add(rec["id"])
    return ids


def entity_readme(record_id: str, record: dict) -> str:
    name = record.get("name", record_id)
    desc = str(record.get("description", "")).strip()
    first = desc.split(". ")[0].strip()
    if first and not first.endswith("."):
        first += "."
    return (
        f"# {name}\n\n"
        f"**Level**: BusinessService\n"
        f"**Record id**: `{record_id}`\n\n"
        f"{first}\n"
    )


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    dry_run = "--dry-run" in sys.argv
    if len(args) != 1:
        print(__doc__)
        return 2
    queue_path = Path(args[0]).resolve()
    if not queue_path.is_file():
        print(f"ERROR: queue file not found: {queue_path}")
        return 2

    reg = _register()
    findings = validate_queue_file(queue_path, reg)
    if findings:
        for f in findings:
            print(f"ERROR: {f}")
        return 1

    entry = yaml.safe_load(queue_path.read_text(encoding="utf-8"))
    slug = entry.get("slug") or slug_from_name(entry["name"])
    content = {k: v for k, v in entry.items() if k not in QUEUE_META}
    suffix = content_hash(content)
    record_id = f"services:service-{slug}-{suffix}"

    collisions = existing_ids()
    if record_id in collisions:
        print(f"ERROR: derived id {record_id} collides with an existing record — "
              f"disambiguate the name/slug")
        return 1

    record = {"id": record_id, "type": "BusinessService", "version": "0.1.0",
             "lifecycle_status": "active", **content}
    entity_dir = ENTITIES / f"{slug}-{suffix}"
    record_path = entity_dir / (record_id.replace(":", "-").lower() + ".yaml")

    print(f"submission : {queue_path.name}")
    print(f"slug       : {slug}")
    print(f"assigned id: {record_id}")
    print(f"entity dir : entities/v1-alpha/{slug}-{suffix}/")
    if dry_run:
        print("dry run: no files written")
        return 0

    entity_dir.mkdir(parents=True, exist_ok=False)
    record_path.write_text(
        yaml.safe_dump(record, sort_keys=False, allow_unicode=True, default_flow_style=False),
        encoding="utf-8",
    )
    (entity_dir / "README.md").write_text(entity_readme(record_id, record), encoding="utf-8")

    entry["status"] = "admitted"
    entry["assigned_id"] = record_id
    entry["admitted"] = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    queue_path.write_text(
        yaml.safe_dump(entry, sort_keys=False, allow_unicode=True, default_flow_style=False),
        encoding="utf-8",
    )

    print("\nRunning the id-system gate over the admitted tree ...")
    gate = subprocess.run(
        [sys.executable, str(REPO / "scripts" / "check_id_system.py"), "--strict"],
        cwd=REPO,
    )
    print(
        "\nAdmitted. The admission PR must also:\n"
        "  1. regenerate CATALOG.yaml:\n"
        "     python scripts/regenerate_catalog.py --schema catalog-index-schema/catalog-index-schema.json\n"
        "  2. add the CHANGELOG.md [Unreleased] entry and the admission CR + index row\n"
        "  3. commit queue entry (status: admitted) together with the entity subtree"
    )
    return gate.returncode


if __name__ == "__main__":
    sys.exit(main())
