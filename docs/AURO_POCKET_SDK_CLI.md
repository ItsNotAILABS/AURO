# AURO / MESIE SDK + CLI for POCKET

This document is the operator contract for using AURO/MESIE as a bounded native-intelligence runtime inside POCKET/NEXUS.

## Install surface

The Python package is `mesie` and now publishes three command surfaces:

```text
mesie        scientific corpus / record / REPL CLI
mesie-tools  tool-specific CLI
auro         stable POCKET/NEXUS product facade
```

The package release associated with this facade is `0.4.1`.

## Python SDK

```python
from mesie.auro_sdk import AuroSDK

auro = AuroSDK()
print(auro.health())
print(auro.capabilities())
print(auro.channels())

result = auro.invoke("spectral.embed", {"record": "record.json"})
print(result["receipt"])
```

`AuroSDK` wraps the existing `SpectralIntelligenceSDK`; it does not replace MESIE's research APIs.

## CLI

```bash
auro health
auro capabilities
auro channels
auro invoke foundation.describe --json '{}'
auro invoke spectral.validate --json '{"record":"record.json"}' --pretty
auro invoke spectral.embed --json '{"record":"record.json"}' --pretty
```

Exit code is `0` for successful bounded operations and `2` for a returned failure.

## Authority boundary

AURO/MESIE is compute-only at this interface:

```text
model_self_authority = false
external_side_effects = false
policy_authority = POCKET / NEXUS
```

A model result, benchmark or spectral transform does not authorize deployment, file mutation, account changes or device operations.

## Logical channels

The facade participates in the POCKET channel fabric:

| Channel | Logical HZ | Purpose |
|---|---:|---|
| `intel` | 5 | research and spectral intelligence |
| `model` | 6 | embeddings and foundation/model compute |
| `proof` | 8 | validation, benchmark and evidence |
| `recovery` | 11 | runtime failure and bounded repair |

These values are logical semantic/cadence labels. They are distinct from the physical frequency tiers in `mesie.edge.hz_ladder`.

## Physical Hz model

MESIE's existing `HzLadder` remains the physics-oriented model. It defines real frequency ranges and calculations for concepts such as wavelength, Shannon capacity, path loss, Doppler shift and link budgets. POCKET's logical HZ fabric must not be presented as a literal RF carrier merely because both use frequency vocabulary.

## Receipts

Every `AuroSDK.invoke()` call returns `auro.execution-receipt.v1` containing:

```text
action
ok
runtime
version
created_at
evidence_digest (SHA-256)
```

This is a witness/evidence receipt for bounded compute, not a permission token.

## POCKET integration order

POCKET should use:

1. installed `mesie` Python SDK through `pocket.auro_mesie` when available;
2. installed `auro` CLI as the stable process boundary;
3. fail closed when neither exists unless a separately declared fallback policy authorizes another runtime.

The older `mesie` CLI remains useful for scientific REPL/corpus workflows but should not be treated as a substitute for the `auro` product facade.

## Verification

```bash
pytest -q tests/test_auro_facade.py
auro health
auro capabilities
auro channels
```

For NEXUS compatibility, validate `ecosystem.surface.json` using the federation production gate in the NEXUS repository.
