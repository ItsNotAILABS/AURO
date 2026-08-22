# AURO / MESIE Runtime

**Provider-neutral model runtime and evaluation plane for the POCKET/NEXUS ecosystem.**

AURO exposes model capability discovery, inference, embeddings, benchmarks, health and release evidence through a bounded runtime contract. MESIE remains the compute/evaluation substrate used by the wider model family.

```text
POCKET / NEXUS request
        │
        ▼
      AURO
        │
        ├── model capability
        ├── inference
        ├── embeddings
        ├── benchmark
        ├── health
        └── release evidence
        │
        ▼
telemetry + artifact + receipt
```

## NEXUS federation

The runtime declaration is [`ecosystem.surface.json`](ecosystem.surface.json).

AURO consumes bounded ecosystem inputs such as:

```text
nexus.task.v1
nexus.budget.v1
nexus.context-pack.v1
nexus.policy-decision.v1
```

and produces operational objects such as:

```text
nexus.health.v1
nexus.telemetry.v1
nexus.artifact.v1
nexus.release-evidence.v1
```

The model runtime specializes in model work; POCKET remains the user/tenant/policy authority and NEXUS remains the federation authority.

## Runtime responsibilities

- describe available model/checkpoint capabilities;
- run bounded inference through configured model lanes;
- generate embeddings where supported;
- execute benchmark/evaluation profiles;
- expose dependency/readiness state;
- produce artifact-backed benchmark/release evidence;
- accept bounded context packs rather than unrestricted workspace state.

## Model-family relationship

The broader AURO family includes atomic, micro, core and orchestration lanes. Checkpoint lineage and model-family architecture are maintained in the dedicated model repositories, including [Auro14B](https://github.com/ItsNotAILABS/Auro14B).

Use model manifests/checkpoint inventories when selecting a concrete checkpoint; use this runtime contract when integrating model capability into products and agents.

## Production integration pattern

```text
identity / tenant scope     POCKET
          │
policy + route              NEXUS / POCKET
          │
context + budget            NEXUS contracts
          │
model call                  AURO / MESIE
          │
health / telemetry          AURO
          │
artifact / release evidence NEXUS-compatible output
```

## Operating checklist

```text
[ ] model/checkpoint is explicitly selected
[ ] token/time/cost budget is set
[ ] context pack is bounded and attributable
[ ] provider/local runtime health is ready
[ ] benchmark profile is named for benchmark work
[ ] produced artifacts are hashed
[ ] runtime/model version is included in receipts
[ ] failed dependencies follow retry/circuit policy
```

## Verification

Run the repository's model/runtime tests and benchmark harness for the lane being changed. For ecosystem compatibility, validate NEXUS after modifying `ecosystem.surface.json` or shared protocol behavior:

```bash
# in ItsNotAILABS/nexus
python tools/validate_ecosystem_protocols.py
python tools/validate_ecosystem_registry.py
python tools/production_gate.py
```

## Ecosystem

- [NEXUS](https://github.com/ItsNotAILABS/nexus) — protocols, planning and federation
- [POCKET](https://github.com/ItsNotAILABS/pocket) — identity/policy/product host
- [POCKET Agent](https://github.com/ItsNotAILABS/pocket-agent) — long-running model-consuming execution
- [Medina Memory](https://github.com/ItsNotAILABS/MedinaMemorySystems) — durable context/outcomes
- [MatDaemon](https://github.com/ItsNotAILABS/MatDaemon) — numerical compute worker
- [Auro14B](https://github.com/ItsNotAILABS/Auro14B) — AURO model-family/checkpoint architecture

AURO's product role is to make models interchangeable **at the runtime boundary without making them interchangeable at the evidence/checkpoint boundary**.
