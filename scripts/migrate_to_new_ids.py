#!/usr/bin/env python3
"""
migrate_to_new_ids.py
CR-SVC-mv1: id system migration (org-wide Wave 2, flat-layout repo).

Rewrites every canonical record's id from the legacy `dea:service-*` form
to `services:service-<slug>-<hash>` (hash per dea-metaframework
docs/id-system.md section 2.5), moves every entity directory to the
flat-layout form `<slug>-<hash>/`, rewrites cross-references (own service
ids via the local id map; `dea:capability-*` bindings via the Wave 2a
capabilities id map), generates a README.md per entity dir (IDM-007),
and emits the migration id map.

References to namespaces outside the ratified registry (`dea:component-*`,
`dea:principle-*`, `dea:pattern-*`) are NOT rewritten; they are documented
as known_residuals in the id map (Wave 2 decision D2-4).

Usage:
  python scripts/migrate_to_new_ids.py [--execute]

Idempotent: re-running on a migrated tree no-ops.
"""
from __future__ import annotations

import argparse
import hashlib
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
ENTITIES = ROOT / "entities" / "v1-alpha"
RECONCILIATION = ROOT / "reconciliation"

NAMESPACE = "services"
BASE32 = "abcdefghjkmnpqrstuvwxyz23456789"
LEGACY_PREFIX = "dea:service-"

# Wave 2a capabilities id map (consumed read-only; sibling checkout).
CAPABILITIES_ID_MAP = (
    ROOT.parent / "dea-catalog-business-capabilities"
    / "reconciliation" / "migration-id-map.yaml"
)

RESIDUAL_PATTERNS = ("dea:component-", "dea:principle-", "dea:pattern-")

RESIDUAL_BLOCK = '''known_residuals:
- legacy_value: dea:capability-* (13 distinct ids in capabilities[] bindings)
  where: canonical records (capabilities fields)
  reason: >-
    Every capability binding in this catalog references a granularity that
    does not exist in the capabilities catalog (28 first-order records).
    Pre-existing org drift, not migration damage; no mapping target exists.
    Needs a binding-reconciliation CR (either admit the finer-grained
    capabilities or remap bindings to first-order ids).
- legacy_value: dea:component-*
  where: canonical records (solution_components fields)
  reason: component namespace is not in the ratified id registry
- legacy_value: dea:principle-*
  where: canonical records (relationships[] target_id)
  reason: principle namespace is not in the ratified id registry
- legacy_value: dea:pattern-*
  where: canonical records (relationships[] target_id)
  reason: pattern namespace is not in the ratified id registry
'''


def _content_hash(text: str) -> str:
    h = hashlib.sha256(text.encode("utf-8")).digest()
    val = int.from_bytes(h[:4], "big")
    chars = []
    for _ in range(6):
        chars.append(BASE32[val % 31])
        val //= 31
    return "".join(reversed(chars))


def _rewrite(text: str, id_map: dict[str, str]) -> str:
    for old in sorted(id_map, key=len, reverse=True):
        text = re.sub(rf"(?<![a-z0-9:-]){re.escape(old)}(?![a-z0-9-])",
                      lambda _: id_map[old], text)
    return text


def _readme(record: dict, new_id: str) -> str:
    name = record.get("name", new_id)
    desc = str(record.get("description", "")).strip()
    first = desc.split(". ")[0].strip()
    if first and not first.endswith("."):
        first += "."
    return (
        f"# {name}\n\n"
        f"**Level**: BusinessService\n"
        f"**Record id**: `{new_id}`\n\n"
        f"{first}\n"
    )


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[1])
    p.add_argument("--execute", action="store_true")
    args = p.parse_args()

    dirs = [d for d in sorted(ENTITIES.iterdir())
            if d.is_dir() and d.name.startswith(LEGACY_PREFIX)]
    if not dirs:
        print("No legacy records found; tree already migrated (no-op).")
        return 0

    # Cross-repo maps (capabilities Wave 2a).
    xref_map: dict[str, str] = {}
    if CAPABILITIES_ID_MAP.exists():
        data = yaml.safe_load(CAPABILITIES_ID_MAP.read_text())
        xref_map.update(data.get("id_map", {}))
    else:
        print(f"WARN: capabilities id map not found at {CAPABILITIES_ID_MAP}; "
              "capability bindings will not be rewritten", file=sys.stderr)

    id_map: dict[str, str] = {}
    contents: dict[str, str] = {}
    for d in dirs:
        yf = d / f"{d.name}.yaml"
        content = yf.read_text()
        old_id = d.name
        slug = old_id[len(LEGACY_PREFIX):]
        id_map[old_id] = f"{NAMESPACE}:service-{slug}-{_content_hash(content)}"
        contents[old_id] = content

    if len(set(id_map.values())) != len(id_map):
        print("FATAL: hash collision", file=sys.stderr)
        return 2

    full_map = {**id_map, **xref_map}
    print(f"Records to migrate: {len(dirs)}; cross-repo refs available: {len(xref_map)}")
    if not args.execute:
        for old, new in sorted(id_map.items()):
            print(f"  {old} -> {new}")
        print("Dry run. Re-run with --execute to apply.")
        return 0

    for d in dirs:
        old_id = d.name
        new_id = id_map[old_id]
        slug = new_id.split(":", 1)[1].split("-", 1)[1]
        new_dir = ENTITIES / slug
        yf = d / f"{d.name}.yaml"
        text = _rewrite(yf.read_text(), full_map)
        record = yaml.safe_load(text)
        d.rename(new_dir)
        target = new_dir / (new_id.replace(":", "-").lower() + ".yaml")
        (new_dir / yf.name).rename(target)
        target.write_text(text)
        (new_dir / "README.md").write_text(_readme(record, new_id))

    RECONCILIATION.mkdir(exist_ok=True)
    lines = [
        "version: 1",
        f"namespace: {NAMESPACE}",
        "migrated_at: '2026-09-21'",
        "carrier_cr: CR-SVC-mv1",
        "id_map:",
    ]
    lines += [f"  {old}: {new}" for old, new in sorted(id_map.items())]
    lines += RESIDUAL_BLOCK.strip().split("\n")
    (RECONCILIATION / "migration-id-map.yaml").write_text("\n".join(lines) + "\n")
    print(f"Migrated {len(dirs)} records.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
