"""POCKET/NEXUS channel contract for AURO/MESIE.

Logical HZ values are semantic coordination lanes. They are distinct from the
physical electromagnetic Hz ladder implemented in ``mesie.edge.hz_ladder``.
AURO/MESIE is a compute participant, never a policy or side-effect authority.
"""
from __future__ import annotations

import time
import uuid
from typing import Any, Dict, Optional

CHANNELS: Dict[str, Dict[str, Any]] = {
    "intel": {"logical_hz":5,"purpose":"research and spectral intelligence","risk":"compute","max_inflight":128},
    "model": {"logical_hz":6,"purpose":"model inference, embeddings and foundation compute","risk":"compute","max_inflight":128},
    "proof": {"logical_hz":8,"purpose":"benchmark, validation and evidence","risk":"append-only","max_inflight":128},
    "recovery": {"logical_hz":11,"purpose":"runtime failure and bounded repair","risk":"bounded","max_inflight":32},
}


def capability_descriptor() -> Dict[str, Any]:
    return {
        "schema": "nexus.capability-descriptor.v1",
        "component": "auro-mesie-runtime",
        "locality": "local-or-explicit-runtime",
        "authority": "compute-only",
        "external_side_effects": False,
        "policy_authority": False,
        "evidence_level": "runtime-receipt",
        "channels": list(CHANNELS),
    }


def manifest() -> Dict[str, Any]:
    return {
        "schema": "auro.pocket-channel-contract.v2",
        "pocket_envelope": "pocket.channel-envelope.v2",
        "pocket_doctrine": "pocket.doctrine-laws.v2",
        "channels": {k: dict(v) for k, v in CHANNELS.items()},
        "physical_hz_model": "mesie.edge.hz_ladder",
        "logical_hz_model": "semantic/cadence routing only",
        "authority": "compute-only; POCKET/NEXUS policy remains external",
        "capability_descriptor": capability_descriptor(),
        "laws": ["continuity","addressability","evidence","model-non-authority","temporal-coherence","replay-safety","capability-disclosure","proof-convergence","channel-failover"],
    }


def envelope(kind: str, body: Any, *, channel: str = "model", request_id: str = "",
             recipient: str = "POCKET_HOST", parent_id: str = "", state: str = "published",
             evidence: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    ch_name = channel if channel in CHANNELS else "model"
    ch = CHANNELS[ch_name]
    now = time.time()
    return {
        "schema": "pocket.channel-envelope.v2",
        "message_id": f"auro-{uuid.uuid4().hex[:16]}",
        "request_id": request_id or f"req-{uuid.uuid4().hex[:16]}",
        "parent_id": parent_id or None,
        "from": "AURO_MESIE",
        "to": recipient,
        "channel": ch_name,
        "logical_hz": ch["logical_hz"],
        "semantic_class": ch["purpose"],
        "risk": ch["risk"],
        "max_inflight": ch["max_inflight"],
        "kind": kind,
        "body": body,
        "state": state,
        "created_at": now,
        "expires_at": now + (900 if ch_name == "model" else 14400),
        "freshness_required": True,
        "side_effect": False,
        "approval": "allow",
        "owner": "AURO_MESIE",
        "capability_selected": True,
        "capability_descriptor": capability_descriptor(),
        "evidence": evidence,
        "lineage": {"parent_id": parent_id or None},
        "side_effect_authority": False,
    }
