# CF-001: Email Gateway Auto-Reply Without Human Review

## Case ID
CF-001

## Date
2026-06-17

## Source
- Repository: [NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent)
- Issue: [#47790 - [Feature]: Add draft_mode configuration to Email Gateway](https://github.com/NousResearch/hermes-agent/issues/47790)
- Related code: `gateway/platforms/email.py`

## Classification
- **Type**: CF (Configuration Failure)
- **Severity**: Critical
- **Impact**: Unintended emails sent to external contacts without human approval

## Description

### What Happened
The Hermes Agent Email Gateway was designed as an auto-reply system:
```
Receive email → Agent processes → Automatically send reply via SMTP
```

In a business context, this resulted in:
- 4 emails automatically sent to external contacts (including customers)
- No human review or approval mechanism
- Violation of internal policy requiring all business emails to be reviewed before sending

### Root Cause
The Email Gateway's `send()` method directly sends emails via SMTP without any draft/review mechanism:

```python
# gateway/platforms/email.py
async def send(self, chat_id, content, reply_to=None, metadata=None):
    """Send an email reply to the given address."""
    try:
        loop = asyncio.get_running_loop()
        message_id = await loop.run_in_executor(
            None, self._send_email, chat_id, content, reply_to
        )
        return SendResult(success=True, message_id=message_id)
    except Exception as e:
        logger.error("[Email] Send failed to %s: %s", chat_id, e)
        return SendResult(success=False, error=str(e))
```

The design assumes email is a communication channel (like Telegram/WeChat) where auto-reply is acceptable, but in business scenarios, email is an output artifact requiring human review.

### Evidence

**Log entries showing automatic sends:**
```
2026-06-16 23:39:05,179 INFO gateway.platforms.base: [Email] Sending response (631 chars) to e-prints@arxiv.org
2026-06-17 09:29:41,536 INFO gateway.platforms.base: [Email] Sending response (562 chars) to e-prints@arxiv.org
2026-06-17 15:30:11,957 INFO gateway.platforms.base: [Email] Sending response (1288 chars) to wwang10@solventum.com
2026-06-17 16:42:31,801 INFO gateway.platforms.base: [Email] Sending response (131 chars) to wwang10@solventum.com
```

**Configuration check revealed no draft_mode option:**
```bash
$ grep -i "draft\|review\|approve" gateway/platforms/email.py
# (no matches)
```

## Connection to ADE Theory

### Which ADE Principle Does This Violate?
**BCP (Behavior Contract Protocol)**: The system violated the implicit behavior contract that business emails require human approval. The agent's actual behavior (auto-send) did not match the expected behavior (draft → review → send).

**PIP (Principle of Interest Protection)**: The system failed to protect the user's interest in controlling external communications, especially in business contexts where unauthorized emails could have legal or reputational consequences.

### How Could ADE Prevent This?
1. **BCP Gate**: Would have detected the mismatch between expected behavior (draft mode) and actual behavior (auto-send) during the first email send
2. **CADVP (Chain-of-Agent Delivery Verification Protocol)**: Would have required explicit confirmation before external communication
3. **Configuration Audit**: ADE's emphasis on configuration verification would have flagged the absence of draft_mode as a critical gap

## Lessons Learned

### For ADE Framework
This case demonstrates that:
1. **Communication channels require different trust levels**: Instant messaging (Telegram/WeChat) can tolerate auto-reply, but email (especially business email) requires human review
2. **Configuration gaps are silent failures**: The absence of a draft_mode option was not immediately obvious until the failure occurred
3. **Behavior contracts must be explicit**: Implicit assumptions about "how email should work" led to the failure

### For Practitioners
1. **Audit communication channels**: Review all external communication paths (email, SMS, API calls) to ensure they match your approval requirements
2. **Implement draft modes**: For any system that sends external communications, provide a draft/review option
3. **Test with real scenarios**: Configuration issues often only surface in production; test with realistic business scenarios
4. **Monitor logs**: Automated sends should be logged and reviewed regularly

## Proposed Solution

### Plugin-based mitigation (implemented)
Developed `qijing-email-draft` plugin that monkey-patches `EmailAdapter.send()` to save emails to IMAP Drafts folder instead of sending directly:

```python
async def patched_send(self, chat_id, content, reply_to=None, metadata=None):
    msg = self._build_email(chat_id, content, reply_to)
    await self._save_to_drafts(msg)  # IMAP APPEND
    logger.info(f"[Email-Draft] Saved to Drafts for {chat_id}")
    return SendResult(success=True, message_id=f"draft-{chat_id}")
```

### Official feature request
Submitted GitHub Issue #47790 requesting native `draft_mode` configuration option.

## References
- GitHub Issue: [#47790 - [Feature]: Add draft_mode configuration to Email Gateway](https://github.com/NousResearch/hermes-agent/issues/47790)
- Hermes Agent Email Gateway code: [`gateway/platforms/email.py`](https://github.com/NousResearch/hermes-agent/blob/main/gateway/platforms/email.py)
- ADE Plugin: [`qijing-email-draft`](https://github.com/ADE-standard/ade-papers/tree/main/cases/plugins/qijing-email-draft)

---

## Metadata
- **Discovered by**: Qijing Digital Technology AI Team
- **Reviewed by**: Dexing Liu
- **Last updated**: 2026-06-17
