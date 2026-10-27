#!/usr/bin/env python3
"""Contribution queue gate (CR-SVC-004).

Validates every ``contributions/queue/*.yaml`` intake submission:

- explicit ``status`` from the queue vocabulary (draft / queued / admitted / rejected)
- NO top-level ``id`` — record ids are assigned at admission by
  ``scripts/admit_entity.py`` (content-derived hash, id-system.md section 2.5);
  hand-invented hashes are exactly what this gate exists to catch
- required identity fields (name, description, domain) and governance
  values drawn from the register at ``classifications/sla-classification.yaml``
  (SLA tiers, security classifications, compliance frameworks)
- reference fields are lists of colon-namespaced id strings (form check;
  cross-catalog resolution happens at admission via the id-system gate)

Exit codes: 0 = queue conforms (an empty queue conforms); 1 = findings.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[1]
QUEUE = REPO / "contributions" / "queue"
REGISTER = REPO / "classifications" / "sla-classification.yaml"

QUEUE_STATUSES = {"draft", "queued", "admitted", "rejected"}
SLUG_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
REF_RE = re.compile(r"^[a-z][a-z0-9-]*:[a-z0-9][a-z0-9-]*$")


def _register() -> dict:
    try:
        data = yaml.safe_load(REGISTER.read_text(encoding="utf-8")) or {}
    except (OSError, yaml.YAMLError):
        return {}
    gov = data.get("governance", {}) if isinstance(data, dict) else {}
    return {
        "sla_tiers": {t.get("tier") for t in gov.get("sla_tiers", []) or []},
        "security": {c.get("level") for c in gov.get("security_classifications", []) or []},
        "compliance": set(gov.get("compliance_frameworks", []) or []),
    }


def validate_queue_file(path: Path, reg: dict) -> list[str]:
    """Return a list of findings for one queue file (empty = valid)."""
    findings: list[str] = []
    try:
        entry = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        return [f"{path.name}: not valid YAML ({exc})"]
    if not isinstance(entry, dict):
        return [f"{path.name}: top level must be a mapping"]

    if "id" in entry:
        findings.append(
            f"{path.name}: submissions must not carry an 'id' — ids are assigned at "
            f"admission (content-derived hash, id-system.md section 2.5)"
        )
    status = entry.get("status")
    if status not in QUEUE_STATUSES:
        findings.append(
            f"{path.name}: 'status' must be one of {sorted(QUEUE_STATUSES)} (got {status!r})"
        )
    name = entry.get("name")
    if not isinstance(name, str) or not name.strip():
        findings.append(f"{path.name}: 'name' is required (non-empty string)")
    desc = entry.get("description")
    if not isinstance(desc, str) or len(desc.strip()) < 40:
        findings.append(
            f"{path.name}: 'description' is required (>= 40 chars; it seeds the entity README)"
        )
    if not isinstance(entry.get("domain"), str) or not entry["domain"].strip():
        findings.append(f"{path.name}: 'domain' is required (e.g. Customer, Finance)")

    slug = entry.get("slug")
    if slug is not None and (not isinstance(slug, str) or not SLUG_RE.match(slug) or len(slug) > 48):
        findings.append(
            f"{path.name}: optional 'slug' must be lowercase kebab-case, <= 48 chars"
        )

    gov = entry.get("governance")
    if not isinstance(gov, dict) or not gov:
        findings.append(
            f"{path.name}: 'governance' is required (sla_tier, security_classification, "
            f"compliance per classifications/sla-classification.yaml)"
        )
    else:
        tier = gov.get("sla_tier")
        if tier not in reg.get("sla_tiers", set()):
            findings.append(
                f"{path.name}: governance.sla_tier {tier!r} not in the register "
                f"(classifications/sla-classification.yaml)"
            )
        sec = gov.get("security_classification")
        if sec not in reg.get("security", set()):
            findings.append(
                f"{path.name}: governance.security_classification {sec!r} not in the register"
            )
        for c in gov.get("compliance", []) or []:
            if c not in reg.get("compliance", set()):
                findings.append(
                    f"{path.name}: governance.compliance entry {c!r} not in the register"
                )

    for field in ("capabilities", "solution_components"):
        refs = entry.get(field, []) or []
        if not isinstance(refs, list):
            findings.append(f"{path.name}: '{field}' must be a list of id references")
            continue
        for ref in refs:
            if not isinstance(ref, str) or not REF_RE.match(ref):
                findings.append(
                    f"{path.name}: {field} entry {ref!r} is not a colon-namespaced id"
                )

    tags = entry.get("tags", []) or []
    if not isinstance(tags, list) or any(
        not isinstance(t, str) or not SLUG_RE.match(t) for t in tags
    ):
        findings.append(f"{path.name}: 'tags' must be kebab-case tokens")
    return findings


def main() -> int:
    reg = _register()
    if not reg:
        print("ERROR: governance register missing or unreadable "
              "(classifications/sla-classification.yaml)")
        return 1
    findings: list[str] = []
    files = sorted(QUEUE.glob("*.yaml")) if QUEUE.is_dir() else []
    for path in files:
        findings.extend(validate_queue_file(path, reg))
    for f in findings:
        print(f"ERROR: {f}")
    print(f"Contribution queue (CR-SVC-004): "
          f"{'CONFORMANT' if not findings else f'{len(findings)} finding(s)'} "
          f"({len(files)} queue file(s))")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
