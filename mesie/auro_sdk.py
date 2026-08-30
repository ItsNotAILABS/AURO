"""Stable AURO facade over MESIE's broad runtime.

This is the product integration surface for POCKET/NEXUS. It deliberately keeps
policy and external side effects outside the model runtime.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
import time
from typing import Any, Dict, Optional

from mesie.sdk import SpectralIntelligenceSDK


@dataclass(frozen=True)
class AuroReceipt:
    schema: str
    action: str
    ok: bool
    runtime: str
    version: str
    created_at: float
    evidence_digest: str


class AuroSDK:
    """Provider-neutral compute facade for MESIE and AURO model-family work."""

    def __init__(self) -> None:
        self.spectral = SpectralIntelligenceSDK()

    @property
    def version(self) -> str:
        return self.spectral.version

    def capabilities(self) -> Dict[str, Any]:
        return {
            "schema": "auro.capabilities.v1",
            "version": self.version,
            "actions": [
                "health", "capabilities", "spectral.validate", "spectral.embed",
                "spectral.generate.psd", "spectral.generate.fas", "spectral.generate.rotdnn",
                "foundation.describe", "channels.describe",
            ],
            "authority": {
                "model_self_authority": False,
                "external_side_effects": False,
                "policy_authority": "POCKET/NEXUS",
            },
        }

    def health(self) -> Dict[str, Any]:
        return {"ok": True, "runtime": "AURO/MESIE", "version": self.version, "sdk": "AuroSDK"}

    def channels(self) -> Dict[str, Any]:
        from mesie.integration.pocket_channels import manifest
        return manifest()

    def invoke(self, action: str, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        payload = dict(payload or {})
        action = (action or "health").lower().strip()
        started = time.time()
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
        out["action"] = action
        out["elapsed_ms"] = round((time.time() - started) * 1000, 3)
        out["receipt"] = self._receipt(action, out)
        return out

    def _record(self, record: Any) -> Any:
        for attr in ("to_dict", "model_dump", "dict"):
            fn = getattr(record, attr, None)
            if callable(fn):
                return fn()
        return str(record)

    def _receipt(self, action: str, result: Dict[str, Any]) -> Dict[str, Any]:
        core = {"action": action, "ok": bool(result.get("ok")), "version": self.version, "result": result.get("result") or result.get("shape") or result.get("error")}
        digest = hashlib.sha256(json.dumps(core, sort_keys=True, default=str).encode()).hexdigest()
        return asdict(AuroReceipt("auro.execution-receipt.v1", action, bool(result.get("ok")), "AURO/MESIE", self.version, time.time(), digest))
