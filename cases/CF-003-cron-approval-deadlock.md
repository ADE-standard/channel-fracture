# CF-003: Cron Jobs Fail Silently Due to Tool Approval Deadlock

## Case ID
CF-003

## Date
2026-05-30

## Source
- Repository: [NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent)
- Issue: [#35214 - Cron Jobs Fail Silently Due to Tool Approval Deadlock](https://github.com/NousResearch/hermes-agent/issues/35214)
- Related code: `cron/scheduler.py`, tool approval system

## Classification
- **Type**: CF (Configuration Failure)
- **Severity**: High
- **Impact**: Automated background tasks silently timeout and fail

## Description

### What Happened
Cron jobs that trigger "Command Approval" requests fail silently because no user is present to approve commands in the background. The job waits until timeout and then fails with `BLOCKED: Command timed out`, even for safe commands like `ls` or `cat`.

### Root Cause
The tool approval system was designed for interactive sessions where a user is present. When cron jobs (which run autonomously) trigger approval requests:

1. The approval request is generated
2. No user is available to approve it
3. The job hangs waiting for approval
4. Eventually times out
5. Reports failure without clearly explaining why

### Evidence
- Cron jobs running safe commands (ls, cat) fail with "Command timed out"
- No clear error message indicating the actual cause (approval deadlock)
- False-positive failure alerts generated

## Connection to ADE Theory

### Which ADE Principle Does This Violate?
**Configuration Failure (CF)**: The security configuration (tool approval) is incompatible with the execution context (autonomous cron). This is a configuration-context mismatch.

**Silent Failure**: The failure mode is silent — the job times out without clearly communicating that the root cause is an approval deadlock.

### How Could ADE Prevent This?
1. **Context-Aware Configuration (BCP)**: Behavior contracts should differentiate between interactive and autonomous execution contexts
2. **Observable Failure Modes**: The error message should clearly state "approval required but no user available" rather than generic timeout
3. **Execution Context Verification**: Pre-flight checks should verify that all required approval channels are available before starting

## Lessons Learned

### For ADE Framework
- Security mechanisms designed for interactive use may create deadlocks in autonomous contexts
- Configuration-context mismatches are a common source of silent failures
- Error messages must accurately describe the root cause, not just the symptom

### For Practitioners
- Define auto-approval lists for autonomous execution contexts
- Test cron jobs with the same security settings they will use in production
- Ensure error messages are actionable and specific

## References
- GitHub Issue: [#35214](https://github.com/NousResearch/hermes-agent/issues/35214)
- ADE Paper: [Silent Failure](https://arxiv.org/abs/2606.08162)

---

## Metadata
- **Discovered by**: Community report
- **Reviewed by**: Dexing Liu
- **Last updated**: 2026-06-17
