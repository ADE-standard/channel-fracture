# DD-001: Context Compression Silently Loses Unflushed Messages

## Case ID
DD-001

## Date
2026-06-16

## Source
- Repository: [NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent)
- Issue: [#47202 - Context compression silently loses unflushed messages](https://github.com/NousResearch/hermes-agent/issues/47202)
- Related code: `agent/conversation_compression.py`, `cli.py`

## Classification
- **Type**: DD (Data Decay)
- **Severity**: Critical
- **Impact**: Permanent, silent data loss during context compression

## Description

### What Happened
When auto-compression triggers mid-turn (because context exceeds the threshold), all messages generated during the current turn are permanently lost. The old session's database entry remains incomplete — it has `message_count` from its last clean turn, but ALL messages from the turn that triggered compression are gone.

### Root Cause
`compress_context()` calls `end_session()` → `create_session()` **without first calling `_flush_messages_to_session_db()`**. Messages generated during the current turn that haven't yet been persisted to `state.db` are permanently lost.

The compression pipeline:
1. `compress_context()` is called with in-memory `messages` list
2. Compressor summarizes old messages → produces shorter `compressed` list
3. `end_session()` is called on old session_id — messages never written to DB
4. New session_id created with `parent_session_id=old_session_id`
5. `_last_flushed_db_idx` is reset to 0 for new session

### Evidence
- `session_search` returns incomplete results for compressed conversations
- `/resume` produces a gap in conversation history
- No offline backup or recovery path for lost messages
- Particularly devastating for long tool-heavy turns (50+ messages)

## Connection to ADE Theory

### Which ADE Principle Does This Violate?
**Data Decay (DD)**: Data (conversation messages) is permanently lost without any notification or recovery mechanism. The decay is invisible — the system continues operating as if nothing happened.

**Intelligence Entropy**: This is a direct manifestation of the entropy principle — the system's structured knowledge (conversation context) degrades over time without active preservation mechanisms.

### How Could ADE Prevent This?
1. **Flush-Before-Rotate**: Mandate that all in-memory state be persisted before any session rotation
2. **Data Integrity Verification**: Post-compression checks should verify message count consistency
3. **Observable Decay Markers**: Flag compressed sessions as potentially incomplete

## Lessons Learned

### For ADE Framework
- Data persistence and session lifecycle must be tightly coupled
- Mid-turn state changes are the most dangerous time for data loss
- Compression/optimization operations must never trade data integrity for efficiency

### For Practitioners
- Always flush pending writes before session rotation
- Implement data integrity checks after compression
- Monitor message count consistency across session transitions

## References
- GitHub Issue: [#47202](https://github.com/NousResearch/hermes-agent/issues/47202)
- ADE Paper: [Intelligence Entropy](https://arxiv.org/abs/2606.18065)

---

## Metadata
- **Discovered by**: Community report
- **Reviewed by**: Dexing Liu
- **Last updated**: 2026-06-17
