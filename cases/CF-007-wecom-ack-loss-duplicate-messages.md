# CF-007: WeCom ACK Loss Causes Duplicate Message Delivery

## Case ID
CF-007

## Date
2026-06-17

## Source
- Repository: [NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent)
- Issue: [#47573 - WeCom adapter: duplicate messages delivered when WebSocket ACK is lost or delayed](https://github.com/NousResearch/hermes-agent/issues/47573)
- Related code: `gateway/platforms/wecom.py`

## Classification
- **Type**: CF (Configuration Failure)
- **Severity**: High
- **Impact**: Users receive duplicate messages, potential confusion and operational errors

## Description

### What Happened
When the WeCom server sends a message but the ACK (acknowledgment) is lost or delayed, the server retries the message. The adapter has no deduplication mechanism, so users receive the same message multiple times.

### Root Cause
The WeCom protocol requires the client to ACK received messages within a timeout window. If the ACK is lost (network issue) or delayed (processing bottleneck), the server assumes the message wasn't delivered and resends it. The adapter processes every received message without checking for duplicates.

### Evidence
Production incidents show users receiving 2-3 copies of the same bot response, especially during high-load periods when ACK processing is delayed.

## Connection to ADE Theory

### Which ADE Principle Does This Violate?
**Channel Fracture (CF)**: The ACK channel is fractured — the server doesn't receive confirmation, triggering retries. The message delivery channel lacks idempotency.

**Data Decay**: Duplicate messages corrupt the user's perception of system reliability and can cause operational errors (e.g., double-processing a command).

### How Could ADE Prevent This?
1. **Message Deduplication**: Track recently received message IDs and reject duplicates
2. **ACK Reliability**: Prioritize ACK sending over other processing
3. **Idempotent Delivery**: Ensure message delivery is idempotent — same message ID = same result

## Lessons Learned

### For ADE Framework
- ACK-based protocols require robust deduplication
- Message delivery must be idempotent to handle retries safely
- ACK reliability is as important as message reliability

### For Practitioners
- Implement message ID tracking with TTL for deduplication
- Send ACKs immediately upon receipt, before processing
- Design message handlers to be idempotent

## References
- GitHub Issue: [#47573](https://github.com/NousResearch/hermes-agent/issues/47573)
- Related: [#14061](https://github.com/NousResearch/hermes-agent/issues/14061), [#38922](https://github.com/NousResearch/hermes-agent/issues/38922)
- ADE Paper: [Channel Fracture](https://arxiv.org/abs/2606.04896)

---

## Metadata
- **Discovered by**: Qijing Digital Technology AI Team (production incident)
- **Reviewed by**: Dexing Liu
- **Last updated**: 2026-06-17
