#!/usr/bin/env python3
"""Evidence-bounded helpers for the AURO Corpus architecture binding.

The module emits model-council and sovereignty protocol objects. It does not
run a model, train a checkpoint, or convert routing identities into checkpoint
claims. Callers must attach their own exact execution and artifact evidence.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

ROOT = Path(__file__).resolve().parents[1]
BINDING_PATH = ROOT / "corpus.architecture.json"


def canonical_sha(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str).encode("utf-8")
    ).hexdigest()


def load_binding() -> dict[str, Any]:
    value = json.loads(BINDING_PATH.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError("corpus.architecture.json must contain an object")
    return value


def validate_binding(value: Mapping[str, Any] | None = None) -> list[str]:
    data = dict(value or load_binding())
    errors: list[str] = []
    expected_lanes = [
        "Auro-156K", "Auro-250M", "Auro-500M", "Auro-2B",
        "Auro-4B", "Auro-8B", "Auro-14B", "Auro-100B",
    ]
    expected_triad = ["Auro-500M-SENSUS", "Auro-500M-PRAXIS", "Auro-500M-VERBUM"]
    if data.get("schema") != "auro.corpus-architecture.v1":
        errors.append("unexpected schema")
    if data.get("authority") != "ItsNotAILABS/nexus":
        errors.append("NEXUS must remain protocol authority")
    if data.get("family_lanes") != expected_lanes:
        errors.append("AURO family lane order mismatch")
    if data.get("specialist_triad") != expected_triad:
        errors.append("Auro-2B specialist triad mismatch")
    council = data.get("council") or {}
    if council.get("parent") != "Auro-2B":
        errors.append("council parent must be Auro-2B")
    if council.get("full_context_broadcast") is not False:
        errors.append("atomic work must use bounded task capsules, not full-context broadcast")
    if len(data.get("claim_boundaries") or []) != 8:
        errors.append("all eight claim boundaries are required")
    if len(data.get("evidence_classes") or []) != 6:
        errors.append("E0-E5 evidence classes are required")
    return errors


def build_council_receipt(
    *,
    council_id: str,
    task_id: str,
    parent_model: str,
    specialists: Sequence[str],
    task_capsules: Sequence[Mapping[str, Any]],
    observations: Sequence[Mapping[str, Any]],
    consensus: Mapping[str, Any],
    execution_evidence: Iterable[str] = (),
) -> dict[str, Any]:
    binding = load_binding()
    errors = validate_binding(binding)
    if errors:
        raise ValueError("invalid AURO corpus binding: " + "; ".join(errors))
    if parent_model != binding["council"]["parent"]:
        raise ValueError("parent model differs from canonical council parent")
    if list(specialists) != binding["specialist_triad"]:
        raise ValueError("specialists differ from canonical SENSUS/PRAXIS/VERBUM triad")
    if not task_capsules:
        raise ValueError("at least one bounded task capsule is required")
    for capsule in task_capsules:
        required = {"task_id", "expert_model_id", "role", "objective", "capsule_hash"}
        missing = sorted(required - set(capsule))
        if missing:
            raise ValueError(f"task capsule missing fields: {missing}")
        if capsule.get("task_id") != task_id:
            raise ValueError("task capsule task_id mismatch")
    evidence = [str(item) for item in execution_evidence if str(item).strip()]
    payload = {
        "schema": "nexus.model-council.v1",
        "council_id": council_id,
        "task_id": task_id,
        "parent_model": parent_model,
        "specialists": list(specialists),
        "task_capsules": [dict(item) for item in task_capsules],
        "observations": [dict(item) for item in observations],
        "consensus": dict(consensus),
        "execution_evidence": evidence,
        "evidence_class": "E2-execution-log" if evidence else "E1-source",
        "claim_boundary": "this receipt proves the described runtime record, not model quality or checkpoint promotion",
    }
    payload["receipt"] = {"sha256": canonical_sha(payload), "signed": False, "external_custody": False}
    return payload


def build_sovereignty_profile(
    *,
    subject: str,
    scores: Mapping[str, float],
    evidence: Mapping[str, Sequence[str]],
) -> dict[str, Any]:
    binding = load_binding()
    required = binding["sovereignty_dimensions"]
    missing = [dimension for dimension in required if dimension not in scores]
    if missing:
        raise ValueError(f"missing sovereignty dimensions: {missing}")
    normalized: dict[str, float] = {}
    evidence_map: dict[str, list[str]] = {}
    for dimension in required:
        score = float(scores[dimension])
        if not 0.0 <= score <= 1.0:
            raise ValueError(f"{dimension} score must be between 0 and 1")
        refs = [str(item) for item in evidence.get(dimension, ()) if str(item).strip()]
        if score > 0 and not refs:
            raise ValueError(f"{dimension} requires evidence for a nonzero score")
        normalized[dimension] = score
        evidence_map[dimension] = refs
    payload = {
        "schema": "nexus.sovereignty-profile.v1",
        "subject": subject,
        "dimensions": required,
        "scores": normalized,
        "evidence": evidence_map,
        "observed_at": "runtime-generated",
        "claim_boundary": "scores are evidence-indexed observations, not certification",
    }
    payload["profile_sha256"] = canonical_sha(payload)
    return payload


def main() -> int:
    binding = load_binding()
    errors = validate_binding(binding)
    report = {
        "schema": "auro.corpus-binding-validation.v1",
        "status": "pass" if not errors else "fail",
        "component": "auro-mesie-runtime",
        "corpus": binding.get("corpus"),
        "family_lanes": binding.get("family_lanes"),
        "errors": errors,
    }
    report["receipt_sha256"] = canonical_sha(report)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
