# CFL-001: Desktop "Delete Profile" Silently Fails — Profile Keeps Reappearing

## Case ID
CFL-001

## Date
2026-06-17

## Source
- Repository: [NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent)
- Issue: [#47368 - Desktop "Delete profile" silently fails and the profile keeps reappearing](https://github.com/NousResearch/hermes-agent/issues/47368)
- Related code: Desktop TUI profile management

## Classification
- **Type**: CFL (Cross-session Framework Lag)
- **Severity**: High
- **Impact**: User believes profile is deleted but it persists, causing confusion

## Description

### What Happened
When a user deletes a profile through the Desktop TUI, the operation appears to succeed (no error shown), but the profile reappears after the application restarts. The deletion was never actually persisted.

### Root Cause
The profile deletion in the Desktop TUI likely:
1. Removes the profile from the in-memory UI state
2. Fails to delete the profile directory on disk (permissions, locked files, or missing implementation)
3. On restart, the profile is re-discovered from disk and re-added to the UI

This is a **state inconsistency between the UI layer and the persistence layer** — the UI believes the profile is gone, but the filesystem disagrees.

### Evidence
Users report deleting profiles, seeing them disappear from the UI, only to find them back after restarting the application.

## Connection to ADE Theory

### Which ADE Principle Does This Violate?
**Cross-session Framework Lag (CFL)**: The framework's state (UI) diverges from the persistent state (disk) across sessions. The deletion action creates a temporary illusion that doesn't survive session boundaries.

**BCP (Behavior Contract Protocol)**: The "Delete" button promises permanent removal but delivers temporary UI-only removal. The behavior contract is violated.

### How Could ADE Prevent This?
1. **Persistence Verification**: After delete, verify the profile directory is actually removed from disk
2. **Atomic State Updates**: UI state and disk state must be updated atomically
3. **Error Propagation**: If disk deletion fails, the UI must show an error, not silently succeed

## Lessons Learned

### For ADE Framework
- UI state and persistent state can diverge silently
- Operations that appear successful may have only partially completed
- Cross-session consistency requires verification at session boundaries

### For Practitioners
- Always verify persistence operations after completion
- Show errors to users when operations partially fail
- Implement state reconciliation on application startup

## References
- GitHub Issue: [#47368](https://github.com/NousResearch/hermes-agent/issues/47368)
- Related: [#44580](https://github.com/NousResearch/hermes-agent/issues/44580) (update reports success when rebuild fails)
- ADE Paper: [Silent Failure](https://arxiv.org/abs/2606.08162)

---

## Metadata
- **Discovered by**: Community report
- **Reviewed by**: Dexing Liu
- **Last updated**: 2026-06-17
