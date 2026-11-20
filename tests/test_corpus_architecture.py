from __future__ import annotations

from tools.corpus_runtime import (
    build_council_receipt,
    build_sovereignty_profile,
    load_binding,
    validate_binding,
)


def test_binding_matches_canonical_family_and_triad():
    binding = load_binding()
    assert validate_binding(binding) == []
    assert binding["family_lanes"][:3] == ["Auro-156K", "Auro-250M", "Auro-500M"]
    assert binding["council"]["parent"] == "Auro-2B"
    assert binding["specialist_triad"] == [
        "Auro-500M-SENSUS",
        "Auro-500M-PRAXIS",
        "Auro-500M-VERBUM",
    ]


def test_council_receipt_requires_bounded_capsules_and_preserves_truth_boundary():
    result = build_council_receipt(
        council_id="council-test",
        task_id="task-test",
        parent_model="Auro-2B",
        specialists=["Auro-500M-SENSUS", "Auro-500M-PRAXIS", "Auro-500M-VERBUM"],
        task_capsules=[{
            "task_id": "task-test",
            "expert_model_id": "Auro-250M",
            "role": "retrieval_filter",
            "objective": "Filter the supplied evidence references.",
            "capsule_hash": "a" * 64,
        }],
        observations=[{"expert_model_id": "Auro-250M", "status": "recorded"}],
        consensus={"status": "candidate", "answer_ref": "artifact:test"},
    )
    assert result["schema"] == "nexus.model-council.v1"
    assert result["evidence_class"] == "E1-source"
    assert result["receipt"]["signed"] is False
    assert result["receipt"]["external_custody"] is False


def test_sovereignty_profile_rejects_unsupported_nonzero_scores():
    dimensions = load_binding()["sovereignty_dimensions"]
    scores = {dimension: 0.0 for dimension in dimensions}
    scores["local-execution"] = 0.5
    try:
        build_sovereignty_profile(subject="AURO", scores=scores, evidence={})
    except ValueError as exc:
        assert "requires evidence" in str(exc)
    else:
        raise AssertionError("nonzero score without evidence must fail")


def test_sovereignty_profile_accepts_evidence_indexed_scores():
    dimensions = load_binding()["sovereignty_dimensions"]
    scores = {dimension: 0.0 for dimension in dimensions}
    evidence = {dimension: [] for dimension in dimensions}
    scores["local-execution"] = 1.0
    evidence["local-execution"] = ["receipt:local-inference-test"]
    result = build_sovereignty_profile(subject="AURO", scores=scores, evidence=evidence)
    assert result["schema"] == "nexus.sovereignty-profile.v1"
    assert result["scores"]["local-execution"] == 1.0
    assert len(result["profile_sha256"]) == 64
