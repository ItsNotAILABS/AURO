"""Stable AURO facade over MESIE's broad runtime.

This is the product integration surface for POCKET/NEXUS. It deliberately keeps
policy and external side effects outside the model runtime while exposing a
versioned channel contract and evidence receipt for every stable invocation.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
import time
from typing import Any, Dict, Optional

from mesie.sdk import SpectralIntelligenceSDK
from mesie.integration.pocket_channels import capability_descriptor, envelope as channel_envelope


@dataclass(frozen=True)
class AuroReceipt:
    schema: str
    action: str
    ok: bool
    runtime: str
    version: str
    created_at: float
    evidence_digest: str
    request_id: str


class AuroSDK:
    """Provider-neutral compute facade for MESIE and AURO model-family work."""

    def __init__(self) -> None:
        self.spectral = SpectralIntelligenceSDK()

    @property
    def version(self) -> str:
        return self.spectral.version

    def capabilities(self) -> Dict[str, Any]:
        return {
            "schema": "auro.capabilities.v2",
            "version": self.version,
            "actions": [
                "health", "capabilities", "spectral.validate", "spectral.embed",
                "spectral.generate.psd", "spectral.generate.fas", "spectral.generate.rotdnn",
                "foundation.describe", "channels.describe",
            ],
            "channels": ["intel", "model", "proof", "recovery"],
            "descriptor": capability_descriptor(),
            "authority": {
                "model_self_authority": False,
                "external_side_effects": False,
                "policy_authority": "POCKET/NEXUS",
            },
        }

    def health(self) -> Dict[str, Any]:
        return {
            "ok": True,
            "runtime": "AURO/MESIE",
            "version": self.version,
            "sdk": "AuroSDK",
            "channel_contract": "auro.pocket-channel-contract.v2",
            "doctrine": "pocket.doctrine-laws.v2",
        }

    def channels(self) -> Dict[str, Any]:
        from mesie.integration.pocket_channels import manifest
        return manifest()

    def invoke(self, action: str, payload: Optional[Dict[str, Any]] = None, *, request_id: str = "") -> Dict[str, Any]:
        payload = dict(payload or {})
        action = (action or "health").lower().strip()
        request_id = request_id or f"auro-req-{hashlib.sha256((action + json.dumps(payload, sort_keys=True, default=str) + str(time.time_ns())).encode()).hexdigest()[:16]}"
        started = time.time()
        try:
            if action == "health":
                out = self.health()
            elif action == "capabilities" or action == "foundation.describe":
                out = self.capabilities()
            elif action == "channels.describe":
                out = self.channels()
            elif action == "spectral.validate":
                report = self.spectral.validate(payload.get("record"))
                to_dict = getattr(report, "to_dict", None)
                out = {"ok": True, "result": to_dict() if callable(to_dict) else str(report)}
            elif action == "spectral.embed":
                arr = self.spectral.embed(payload.get("record"))
                out = {"ok": True, "embedding": arr.tolist(), "shape": list(arr.shape)}
            elif action == "spectral.generate.psd":
                out = {"ok": True, "record": self._record(self.spectral.generate_psd(**payload))}
            elif action == "spectral.generate.fas":
                out = {"ok": True, "record": self._record(self.spectral.generate_fas(**payload))}
            elif action == "spectral.generate.rotdnn":
                out = {"ok": True, "record": self._record(self.spectral.generate_rotdnn(**payload))}
            else:
                out = {"ok": False, "error": f"unsupported AURO facade action: {action}"}
        except Exception as exc:
            out = {"ok": False, "error": str(exc)[:800]}

        out["action"] = action
        out["request_id"] = request_id
        out["elapsed_ms"] = round((time.time() - started) * 1000, 3)
        receipt = self._receipt(action, out, request_id=request_id)
        out["receipt"] = receipt
        channel = self._channel_for(action, bool(out.get("ok")))
        out["message"] = channel_envelope(
            action,
            {"ok": bool(out.get("ok")), "runtime": "AURO/MESIE", "version": self.version, "elapsed_ms": out["elapsed_ms"]},
            channel=channel,
            request_id=request_id,
            state="succeeded" if out.get("ok") else "failed",
            evidence=receipt,
        )
        return out

    @staticmethod
    def _channel_for(action: str, ok: bool) -> str:
        if not ok:
            return "recovery"
        if any(x in action for x in ("validate", "benchmark", "receipt", "evidence")):
            return "proof"
        if any(x in action for x in ("research", "intel")):
            return "intel"
        return "model"

    def _record(self, record: Any) -> Any:
        for attr in ("to_dict", "model_dump", "dict"):
            fn = getattr(record, attr, None)
            if callable(fn):
                return fn()
        return str(record)

    def _receipt(self, action: str, result: Dict[str, Any], *, request_id: str) -> Dict[str, Any]:
        core = {
            "action": action,
            "ok": bool(result.get("ok")),
            "runtime": "AURO/MESIE",
            "version": self.version,
            "request_id": request_id,
            "result": result.get("result") or result.get("shape") or result.get("record") or result.get("error"),
        }
        digest = hashlib.sha256(json.dumps(core, sort_keys=True, default=str).encode()).hexdigest()
        return asdict(AuroReceipt("auro.execution-receipt.v2", action, bool(result.get("ok")), "AURO/MESIE", self.version, time.time(), digest, request_id))
