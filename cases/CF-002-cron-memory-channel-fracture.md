# CF-002: Cron Agents Silently Lose Memory Write Capability

## Case ID
CF-002

## Date
2026-06-13

## Source
- Repository: [NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent)
- Issue: [#38647 - Channel Fracture: cron agents silently lose memory write capability](https://github.com/NousResearch/hermes-agent/issues/38647)
- Related code: `cron/scheduler.py`, `agent/agent_init.py`

## Classification
- **Type**: CF (Configuration Failure)
- **Severity**: Critical
- **Impact**: Cross-agent memory injection completely fails, no error reported

## Description

### What Happened
Cron job agents designed to inject knowledge into shared memory stores fail silently. The cron job completes without error, the agent reports task success, but the target memory remains empty.

This is the core scenario that motivated the **Channel Fracture** paper (arXiv:2606.04896).

### Root Cause
Two architectural constraints combine to create the failure:

**Primary** — The `AIAgent` constructor in cron mode is called with `skip_memory=True`:
```python
# cron/scheduler.py ~line 1652
AIAgent(
    ...
    skip_memory=True,
    platform="cron",
    ...
)
```

**Secondary** — Memory tools are only registered when `_memory_manager is not None`. Since cron bypasses memory init, the entire memory tool surface is absent:
```python
if agent._memory_manager and agent.tools is not None and (...):
    # memory tool registration — never reached in cron
```

### Evidence
1. Cron output shows `memory action='add': UNAVAILABLE`
2. Target memory store remains empty
3. Cron exit code is 0 — no error reported
4. Only receiver-side inspection reveals the failure

## Connection to ADE Theory

### Which ADE Principle Does This Violate?
**Channel Fracture (CF)**: This is the textbook example. The cross-agent memory injection channel appears functional from the writer side but is completely broken at the receiver. The fracture occurs between the cron agent and the target agent's memory store.

### How Could ADE Prevent This?
1. **Delivery Verification (CADVP)**: A verification step after memory injection would detect that the write did not persist
2. **Behavior Contract (BCP)**: The cron agent's behavior contract should include "memory writes succeed" as a deliverable
3. **Observability Layer**: Channel status monitoring would flag the disconnected memory channel

## Lessons Learned

### For ADE Framework
- Cross-agent channels require **bidirectional verification** — writer-side success is insufficient
- Cron/scheduled agents operate in degraded capability modes that may silently disable critical features
- The `skip_memory=True` pattern is a common anti-pattern in agent scheduling systems

### For Practitioners
- Always verify cron agent capabilities match expectations
- Test memory write paths from cron contexts explicitly
- Implement receiver-side verification for all cross-agent data transfers

## References
- GitHub Issue: [#38647](https://github.com/NousResearch/hermes-agent/issues/38647)
- ADE Paper: [Channel Fracture](https://arxiv.org/abs/2606.04896)

---

## Metadata
- **Discovered by**: Qijing Digital Technology AI Team
- **Reviewed by**: Dexing Liu
- **Last updated**: 2026-06-17
