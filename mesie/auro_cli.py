"""Stable AURO CLI for POCKET/NEXUS and human operators."""
from __future__ import annotations

import argparse
import json

from mesie.auro_sdk import AuroSDK


def _payload(raw: str) -> dict:
    if not raw:
        return {}
    try:
        value = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid --json payload: {exc}")
    if not isinstance(value, dict):
        raise SystemExit("--json payload must be a JSON object")
    return value


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="auro", description="AURO / MESIE governed compute facade")
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("health", help="Describe AURO/MESIE runtime health")
    sub.add_parser("capabilities", help="List stable integration capabilities and authority boundary")
    sub.add_parser("channels", help="Describe POCKET doctrine v2 logical HZ channel contract")

    inv = sub.add_parser("invoke", help="Invoke one stable AURO SDK action")
    inv.add_argument("action")
    inv.add_argument("--json", default="{}", help="JSON object payload")
    inv.add_argument("--request-id", default="", help="Preserve POCKET/NEXUS request identity")
    inv.add_argument("--pretty", action="store_true")

    args = parser.parse_args(argv)
    if not args.command:
        parser.print_help()
        raise SystemExit(1)

    sdk = AuroSDK()
    if args.command == "health":
        out = sdk.health()
    elif args.command == "capabilities":
        out = sdk.capabilities()
    elif args.command == "channels":
        out = sdk.channels()
    else:
        out = sdk.invoke(args.action, _payload(args.json), request_id=args.request_id)

    print(json.dumps(out, indent=2 if getattr(args, "pretty", False) else None, sort_keys=True, default=str))
    raise SystemExit(0 if out.get("ok", True) else 2)


if __name__ == "__main__":
    main()
