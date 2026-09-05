"""One-shot extraction of DBSF entries into per-entity subtrees.

Reads CATALOG/v1-alpha/business-services/*.yaml and CATALOG/v1-alpha/capabilities/*.yaml,
splits the entries[] list into individual YAML files at
entities/v1-alpha/<id>/<id>.yaml, and drops the redundant source_id
from relationships.

Idempotent: re-running overwrites the same files. Does NOT remove
the source files; that is done by the post-extraction step.

Usage: python tools/extract_dbsf_entities.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import yaml


REPO = Path(__file__).resolve().parents[1]
ENTITIES_ROOT = REPO / "entities" / "v1-alpha"
SOURCE_ROOT = REPO / "CATALOG" / "v1-alpha"


def write_entity(entry: dict[str, object], out_path: Path) -> None:
    """Write a single entity YAML at its canonical path."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    # Drop the redundant source_id from relationships (the entity id is the source)
    relationships = entry.get("relationships")
    if isinstance(relationships, list):
        for rel in relationships:
            if isinstance(rel, dict):
                rel.pop("source_id", None)
    # Map the DBSF `status` field to the standard `lifecycle_status`.
    # Per CR-CATALOG-STRUCT-01, the regenerator reads `lifecycle_status`
    # (with enum: candidate | active | deprecated | retired | unknown).
    # DBSF entries use `status: active`; that is semantically the
    # `active` lifecycle value, not the catalog-level `status`.
    if "status" in entry and "lifecycle_status" not in entry:
        entry["lifecycle_status"] = entry.pop("status")
    # Stable YAML output: block style for mappings; preserve order
    body = yaml.safe_dump(entry, sort_keys=False, default_flow_style=False, allow_unicode=True)
    out_path.write_text(body, encoding="utf-8")


def extract_business_services() -> int:
    count = 0
    for src in sorted((SOURCE_ROOT / "business-services").glob("*.yaml")):
        doc = yaml.safe_load(src.read_text(encoding="utf-8"))
        for entry in doc.get("entries", []):
            eid = entry["id"]
            out = ENTITIES_ROOT / eid / f"{eid}.yaml"
            write_entity(entry, out)
            count += 1
    return count


def main() -> int:
    if not SOURCE_ROOT.exists():
        print(f"ERROR: source root not found: {SOURCE_ROOT}", file=sys.stderr)
        return 1
    n = extract_business_services()
    print(f"wrote {n} entities under {ENTITIES_ROOT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
