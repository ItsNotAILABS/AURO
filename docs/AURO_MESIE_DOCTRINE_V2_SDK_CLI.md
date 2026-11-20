# AURO / MESIE Doctrine v2 SDK + CLI Channel Specification

**Runtime:** AURO / MESIE  
**Integration:** POCKET / NEXUS  
**Channel contract:** `auro.pocket-channel-contract.v2`  
**Envelope:** `pocket.channel-envelope.v2`  
**Receipt:** `auro.execution-receipt.v2`

## Purpose

AURO/MESIE is the native scientific/model compute plane of the POCKET/NEXUS ecosystem. This document defines how it participates in the shared communications fabric without acquiring user-policy or external-side-effect authority.

The stable product interfaces are:

- Python: `mesie.auro_sdk:AuroSDK`
- CLI: `auro`
- scientific SDK: `mesie.sdk:SpectralIntelligenceSDK`
- legacy scientific CLI: `mesie`
- physical frequency model: `mesie.edge.hz_ladder`

## Authority boundary

AURO/MESIE may compute, validate, embed, generate scientific records, describe capabilities, emit evidence, and participate in model/intel/proof/recovery channels. It may not independently authorize deployment, account mutation, device actuation, repository writes, or other external side effects.

POCKET Host retains user/tenant/policy authority. NEXUS remains the federation/protocol authority.

## Dual-HZ contract

The logical channel numbers below are **not physical RF carriers**. They encode routing semantics and cadence inside POCKET.

| Channel | Logical HZ | AURO/MESIE purpose |
|---|---:|---|
| intel | 5 | research and spectral intelligence |
| model | 6 | model inference, embeddings, foundation compute |
| proof | 8 | validation, benchmark, evidence |
| recovery | 11 | failure and bounded repair |

Physical-frequency mathematics lives separately in `mesie.edge.hz_ladder`.

## Python SDK

```python
from mesie.auro_sdk import AuroSDK

auro = AuroSDK()
print(auro.health())
print(auro.capabilities())
print(auro.channels())

result = auro.invoke(
    "spectral.embed",
    {"record": "signal.json"},
    request_id="req-123",
)
```

A stable invocation returns the compute result plus:

- `request_id`
- `elapsed_ms`
- `auro.execution-receipt.v2`
- `pocket.channel-envelope.v2`
- evidence digest
- explicit capability descriptor
- explicit no-side-effect authority

The message and receipt preserve the same request identity.

## CLI

```bash
auro health
auro capabilities
auro channels
auro invoke spectral.embed --json '{"record":"signal.json"}' --request-id req-123
auro invoke spectral.validate --json '{"record":"signal.json"}' --request-id req-124 --pretty
```

Exit code is zero for a successful facade response and nonzero for a failed invocation. The CLI is a transport to the same SDK contract; it does not create a second policy model.

## Routing semantics

The SDK routes outcomes by semantic class:

```text
health / capabilities / embeddings / generation -> model@6
validation / benchmark / evidence              -> proof@8
research / spectral intelligence                -> intel@5
failed invocation                               -> recovery@11
```

This keeps evidence separate from normal model output and makes failure visible to recovery systems.

## Receipt contract

`auro.execution-receipt.v2` binds:

- action
- success/failure state
- AURO/MESIE runtime identity
- runtime version
- creation time
- request ID
- SHA-256 evidence digest

The receipt witnesses computation. It does not authorize another action.

## Capability disclosure

Before routing, AURO/MESIE can publish a `nexus.capability-descriptor.v1` object describing:

- component identity
- locality posture
- compute-only authority
- external side effects disabled
- evidence level
- supported logical channels

This satisfies the POCKET Capability Disclosure Law without importing POCKET implementation code into AURO.

## Failure and fallback

The runtime reports failures explicitly. POCKET may attempt its documented local integration sequence - AuroSDK, MESIE SDK, installed AURO CLI - but it must not silently substitute an unrelated cloud model when that changes privacy, cost, authority, or evidence semantics.

## Proof convergence

A consequential workflow should not treat an AURO model completion as final proof. The calling operation correlates the AURO receipt with its own execution artifact and verifier evidence using the same request ID and lineage.

```text
POCKET request req-X
   |-- AURO compute ---- auro receipt(req-X)
   |-- executor -------- artifact(req-X)
   `-- verifier -------- proof(req-X)
                       |
                 convergence gate
```

## Physical Hz model boundary

`mesie.edge.hz_ladder` is a scientific/engineering model of real frequency tiers and link properties. POCKET logical HZ is a software coordination abstraction. A consumer must not convert the presence of a logical channel number into a claim of radio transmission.

## Verification commands

```bash
python -m pytest -q tests/test_auro_doctrine_v2.py
auro health
auro capabilities
auro channels
```

Full production promotion additionally requires the repository's wider regression suite and ecosystem/NEXUS protocol validation.
