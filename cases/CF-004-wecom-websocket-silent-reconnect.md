# CF-004: WeCom WebSocket Reconnection Fails Silently

## Case ID
CF-004

## Date
2026-06-17

## Source
- Repository: [NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent)
- Issue: [#47572 - WeCom adapter: WebSocket reconnection may fail silently](https://github.com/NousResearch/hermes-agent/issues/47572)
- Related code: `gateway/platforms/wecom.py` line 334-359

## Classification
- **Type**: CF (Configuration Failure)
- **Severity**: High
- **Impact**: Messages silently lost, no operational visibility

## Description

### What Happened
After a WeCom WebSocket connection error (errcode 846609), the adapter's reconnection logic may fail silently without logging success or failure. Production logs show:

```
10:05:38 ERROR [Wecom] Send failed: WeCom errcode 846609: aibot websocket not subscribed
10:06:08 WARNING [Wecom] WebSocket error: WeCom websocket closed
[NO FURTHER LOGS - No "Reconnected" or "Reconnect failed" messages]
```

### Root Cause
Three silent failure points in `_open_connection()`:

1. **`_wait_for_handshake()` may hang indefinitely** — no explicit timeout on `ws.receive()` call, deadline computed but never checked if receive blocks
2. **`_mark_connected()` doesn't log** — success case has no confirmation
3. **Exception handling gaps** — `asyncio.TimeoutError` may not propagate correctly through nested try/except

### Evidence
Production incident on 2026-06-17: gap between "WebSocket error" and complete absence of reconnection confirmation. No way to determine if connection was restored.

## Connection to ADE Theory

### Which ADE Principle Does This Violate?
**Silent Failure**: The reconnection mechanism — a safety net — itself fails silently. This is a second-order silent failure: the system designed to recover from failures also fails without notification.

**Intelligence Entropy**: The connection state degrades from "connected" to "unknown" without any observable marker. The system's disorder increases invisibly.

### How Could ADE Prevent This?
1. **Observable State Transitions**: Every connection state change must produce a log entry
2. **Timeout Enforcement**: All network operations must have hard timeouts with explicit error paths
3. **Health Verification**: Post-reconnection health checks must confirm actual connectivity

## Lessons Learned

### For ADE Framework
- Safety mechanisms (reconnection) can themselves be silent failure points
- Second-order silent failures are harder to detect than first-order ones
- Absence of logs is itself a failure mode

### For Practitioners
- Log both success AND failure paths of recovery mechanisms
- Add explicit timeouts to all network operations
- Implement health checks after reconnection

## References
- GitHub Issue: [#47572](https://github.com/NousResearch/hermes-agent/issues/47572)
- Related: [#47564](https://github.com/NousResearch/hermes-agent/issues/47564) (846609 error handling)
- ADE Paper: [Silent Failure](https://arxiv.org/abs/2606.08162)

---

## Metadata
- **Discovered by**: Qijing Digital Technology AI Team (production incident)
- **Reviewed by**: Dexing Liu
- **Last updated**: 2026-06-17
