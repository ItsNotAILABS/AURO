"""POCKET/NEXUS channel contract for AURO/MESIE.

Logical HZ values are semantic coordination lanes. They are distinct from the
physical electromagnetic Hz ladder implemented in ``mesie.edge.hz_ladder``.
"""
from __future__ import annotations

import time
import uuid
from typing import Any, Dict

CHANNELS: Dict[str, Dict[str, Any]] = {
    "intel": {"logical_hz":5,"purpose":"research and spectral intelligence"},
    "model": {"logical_hz":6,"purpose":"model inference, embeddings and foundation compute"},
    "proof": {"logical_hz":8,"purpose":"benchmark, validation and evidence"},
    "recovery": {"logical_hz":11,"purpose":"runtime failure and bounded repair"},
}


def manifest() -> Dict[str, Any]:
    return {
        "schema": "auro.pocket-channel-contract.v1",
        "channels": {k: dict(v) for k, v in CHANNELS.items()},
        "physical_hz_model": "mesie.edge.hz_ladder",
        "logical_hz_model": "semantic/cadence routing only",
        "authority": "compute-only; POCKET/NEXUS policy remains external",
    }


def envelope(kind: str, body: Any, *, channel: str = "model", request_id: str = "", recipient: str = "POCKET_HOST") -> Dict[str, Any]:
    ch = CHANNELS.get(channel, CHANNELS["model"])
    return {
        "schema": "auro.channel-envelope.v1",
        "message_id": f"auro-{uuid.uuid4().hex[:16]}",
        "request_id": request_id or f"req-{uuid.uuid4().hex[:16]}",
        "from": "AURO_MESIE",
        "to": recipient,
        "channel": channel,
        "logical_hz": ch["logical_hz"],
        "kind": kind,
        "body": body,
        "state": "published",
        "created_at": time.time(),
        "side_effect_authority": False,
    }
