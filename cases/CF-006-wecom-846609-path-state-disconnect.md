# CF-006: WeCom 846609 — Send Path Receives Disconnect But Never Reconnects

## Case ID
CF-006

## Date
2026-06-17

## Source
- Repository: [NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent)
- Issue: [#47564 - WeCom adapter: send() receives errcode 846609 but does not trigger WebSocket reconnection](https://github.com/NousResearch/hermes-agent/issues/47564)
- Related code: `gateway/platforms/wecom.py` line 57-79

## Classification
- **Type**: CF (Configuration Failure)
- **Severity**: Critical
- **Impact**: 57-79 second dead window where all messages are silently dropped

## Description

### What Happened
When the WeCom send path receives errcode 846609 ("aibot websocket not subscribed"), it indicates the WebSocket connection is dead. However, the send path does NOT trigger reconnection — only the listen loop does. This creates a 57-79 second dead window where:

1. Send path gets 846609 error
2. Error is logged but no reconnection triggered
3. Listen loop hasn't detected the disconnect yet
4. All messages during this window are silently dropped

### Root Cause
The WeCom adapter has two separate connection management paths:
- **Listen loop**: Detects disconnect via `ws.receive()` → triggers reconnection
- **Send path**: Gets 846609 error → logs it → **does nothing**

The send path treats 846609 as a transient error rather than a connection-level failure.

### Evidence
Production logs show 846609 errors at 10:05:38, but reconnection doesn't begin until listen loop detects it at 10:06:08 — a 30-second gap. During this time, all user messages are lost.

## Connection to ADE Theory

### Which ADE Principle Does This Violate?
**Channel Fracture (CF)**: The send and receive paths are fractured — they don't share connection state. The send path knows the connection is dead but doesn't inform the system.

**Silent Failure**: Messages during the dead window fail without any notification to the sender or operator.

### How Could ADE Prevent This?
1. **Unified Connection State**: Send and receive paths must share connection state and trigger reconnection on any disconnect signal
2. **Error Classification**: 846609 is a connection-level error, not a transient error — it should trigger immediate reconnection
3. **Dead Window Detection**: Monitor time between last successful send and reconnection — alert if exceeds threshold

## Lessons Learned

### For ADE Framework
- Multi-path connection management creates fracture points
- Error classification errors (treating fatal as transient) are silent failure sources
- Dead windows between detection and recovery are a common anti-pattern

### For Practitioners
- Classify errors correctly: connection-level errors must trigger reconnection immediately
- Share connection state across all paths (send, receive, health check)
- Monitor and alert on dead windows

## References
- GitHub Issue: [#47564](https://github.com/NousResearch/hermes-agent/issues/47564)
- Related: [#47572](https://github.com/NousResearch/hermes-agent/issues/47572), [#29667](https://github.com/NousResearch/hermes-agent/issues/29667)
- ADE Paper: [Channel Fracture](https://arxiv.org/abs/2606.04896)

---

## Metadata
- **Discovered by**: Qijing Digital Technology AI Team (production incident)
- **Reviewed by**: Dexing Liu
- **Last updated**: 2026-06-17
