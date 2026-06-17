# CF-005: QQ Bot WebSocket Zombie Connection — 18+ Hours Silent Death

## Case ID
CF-005

## Date
2026-05-04

## Source
- Repository: [NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent)
- Issue: [#19821 - QQ Bot WebSocket silently dies — adapter waits on dead connection for 18+ hours](https://github.com/NousResearch/hermes-agent/issues/19821)
- Related code: `gateway/platforms/qqbot.py`

## Classification
- **Type**: CF (Configuration Failure)
- **Severity**: Critical
- **Impact**: All messages lost for 18+ hours, gateway appears healthy

## Description

### What Happened
QQ Bot WebSocket adapter entered a "zombie" state where the TCP connection appeared alive but QQ server had silently dropped it. The adapter waited forever on a dead connection instead of triggering reconnection. **Messages were lost for 18+ hours** while the gateway process stayed alive.

### Evidence from production logs
```
05-04 03:59  Last successful WebSocket resume (seq=1752)
             ===== SILENCE =====
05-04 07:07  Access token refreshed (token refresh still works!)
05-04 09:04  Access token refreshed
05-04 14:01  Access token refreshed
05-04 18:01  Access token refreshed
             ===== 18 HOURS, NO MESSAGES, NO WEBSOCKET EVENTS =====
05-04 22:35  Auto-update triggered restart → works again
```

### Root Cause
The QQ WebSocket adapter lacked a **ping/pong or application-level heartbeat**. QQ server dropped the connection silently after the session aged past ~30 hours, but the TCP connection appeared open to the client. Without a close frame, the reconnect loop never fired.

**This is a TCP half-open connection problem** — the most insidious form of silent failure in networked systems.

## Connection to ADE Theory

### Which ADE Principle Does This Violate?
**Silent Failure**: The connection appeared healthy while being completely dead. This is the textbook "zombie connection" anti-pattern.

**Channel Fracture**: The communication channel between the agent and QQ users was fractured for 18 hours, but the system reported no error.

**Intelligence Entropy**: System disorder increased maximally (total communication loss) while all observable indicators showed normal operation.

### How Could ADE Prevent This?
1. **Application-Level Heartbeat**: Periodic ping/pong to detect dead connections
2. **Activity-Based Health Check**: If no messages received for N minutes, force reconnect
3. **Cross-Thread Health Correlation**: Token refresh works but WebSocket is dead → inconsistency should trigger alert

## Lessons Learned

### For ADE Framework
- TCP-level connection status is insufficient for health monitoring
- Long-lived connections require application-level liveness checks
- Independent subsystems (token refresh vs WebSocket) can mask each other's failures

### For Practitioners
- Implement receive timeouts: if no event in N minutes, force reconnect
- Add periodic WebSocket ping/pong
- Monitor message frequency — sudden silence is itself a signal

## References
- GitHub Issue: [#19821](https://github.com/NousResearch/hermes-agent/issues/19821)
- Related QQ Bot issues: [#25505](https://github.com/NousResearch/hermes-agent/issues/25505), [#14539](https://github.com/NousResearch/hermes-agent/issues/14539)
- ADE Paper: [Silent Failure](https://arxiv.org/abs/2606.08162)

---

## Metadata
- **Discovered by**: Community report (production incident)
- **Reviewed by**: Dexing Liu
- **Last updated**: 2026-06-17
