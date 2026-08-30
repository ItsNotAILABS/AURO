from mesie.auro_sdk import AuroSDK
from mesie.integration.pocket_channels import envelope, manifest


def test_auro_health_and_capabilities():
    sdk = AuroSDK()
    health = sdk.health()
    caps = sdk.capabilities()
    assert health["ok"] is True
    assert health["runtime"] == "AURO/MESIE"
    assert caps["authority"]["model_self_authority"] is False
    assert "spectral.embed" in caps["actions"]


def test_logical_hz_contract_is_not_physical_claim():
    m = manifest()
    assert m["logical_hz_model"] == "semantic/cadence routing only"
    assert m["physical_hz_model"] == "mesie.edge.hz_ladder"
    assert m["channels"]["model"]["logical_hz"] == 6
    assert m["channels"]["proof"]["logical_hz"] == 8


def test_channel_envelope_has_lineage_fields():
    msg = envelope("spectral.embed", {"shape": [1, 8]}, request_id="req-test")
    assert msg["schema"] == "auro.channel-envelope.v1"
    assert msg["request_id"] == "req-test"
    assert msg["side_effect_authority"] is False


def test_facade_receipt_is_evidence_digest():
    out = AuroSDK().invoke("health")
    assert out["ok"] is True
    assert out["receipt"]["schema"] == "auro.execution-receipt.v1"
    assert len(out["receipt"]["evidence_digest"]) == 64
