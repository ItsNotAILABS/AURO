from mesie.auro_sdk import AuroSDK
from mesie.integration.pocket_channels import CHANNELS, capability_descriptor, envelope, manifest


def test_channel_contract_v2_and_dual_hz_boundary():
    m = manifest()
    assert m["schema"] == "auro.pocket-channel-contract.v2"
    assert m["pocket_envelope"] == "pocket.channel-envelope.v2"
    assert m["pocket_doctrine"] == "pocket.doctrine-laws.v2"
    assert m["physical_hz_model"] == "mesie.edge.hz_ladder"
    assert "semantic/cadence" in m["logical_hz_model"]
    assert set(CHANNELS) == {"intel", "model", "proof", "recovery"}


def test_capability_descriptor_denies_side_effect_authority():
    d = capability_descriptor()
    assert d["component"] == "auro-mesie-runtime"
    assert d["authority"] == "compute-only"
    assert d["external_side_effects"] is False
    assert d["policy_authority"] is False
    assert d["evidence_level"] == "runtime-receipt"


def test_channel_envelope_preserves_request_identity_and_freshness():
    msg = envelope("spectral.embed", {"ok": True}, request_id="req-test", channel="model")
    assert msg["schema"] == "pocket.channel-envelope.v2"
    assert msg["request_id"] == "req-test"
    assert msg["channel"] == "model"
    assert msg["logical_hz"] == 6
    assert msg["expires_at"] > msg["created_at"]
    assert msg["side_effect"] is False
    assert msg["side_effect_authority"] is False
    assert msg["capability_descriptor"]["component"] == "auro-mesie-runtime"


def test_auro_health_receipt_and_message_converge():
    sdk = AuroSDK()
    out = sdk.invoke("health", request_id="req-health")
    assert out["ok"] is True
    assert out["request_id"] == "req-health"
    assert out["receipt"]["schema"] == "auro.execution-receipt.v2"
    assert out["receipt"]["request_id"] == "req-health"
    assert len(out["receipt"]["evidence_digest"]) == 64
    assert out["message"]["request_id"] == "req-health"
    assert out["message"]["evidence"]["evidence_digest"] == out["receipt"]["evidence_digest"]
    assert out["message"]["channel"] == "model"


def test_validation_routes_to_proof_and_failure_routes_to_recovery():
    sdk = AuroSDK()
    assert sdk._channel_for("spectral.validate", True) == "proof"
    assert sdk._channel_for("benchmark.run", True) == "proof"
    assert sdk._channel_for("spectral.embed", True) == "model"
    assert sdk._channel_for("spectral.embed", False) == "recovery"
