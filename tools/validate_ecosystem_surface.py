#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "ecosystem.surface.json"
def fail(message: str) -> None: raise SystemExit(f"ecosystem-surface: FAIL: {message}")
def main() -> int:
    data = json.loads(PATH.read_text(encoding="utf-8"))
    if data.get("schema") != "nexus.capability.v1": fail("schema")
    if not isinstance(data.get("component"), str) or not data["component"]: fail("component")
    repo = data.get("repository")
    if not isinstance(repo, str) or "/" not in repo: fail("repository")
    if not isinstance(data.get("role"), str) or not data["role"]: fail("role")
    actions = data.get("actions")
    if not isinstance(actions, list) or not actions or len(actions) != len(set(actions)): fail("actions")
    for key in ("produces", "consumes"):
        if not isinstance(data.get(key), list): fail(key)
    if not isinstance(data.get("limits"), dict): fail("limits")
    if not isinstance(data.get("proof"), dict) or not data["proof"].get("state"): fail("proof")
    if data.get("authority") != "ItsNotAILABS/nexus": fail("authority")
    print(f"ecosystem-surface: PASS {data['component']} ({len(actions)} actions)")
    return 0
if __name__ == "__main__": sys.exit(main())
