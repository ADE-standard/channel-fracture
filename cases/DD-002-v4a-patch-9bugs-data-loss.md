# DD-002: V4A Patch Parser — 9 Bugs Causing Silent Data Loss

## Case ID
DD-002

## Date
2026-04-09

## Source
- Repository: [NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent)
- Issue: [#6831 - 9 bugs in V4A patch parser and fuzzy match: data loss, partial apply, silent errors](https://github.com/NousResearch/hermes-agent/issues/6831)
- Related code: `tools/patch_parser.py`, `tools/fuzzy_match.py`

## Classification
- **Type**: DD (Data Decay)
- **Severity**: Critical
- **Impact**: Permanent data loss, silent corruption, partial file modifications

## Description

### What Happened
Nine confirmed bugs in the V4A patch parser and fuzzy match system, grouped into three tiers of severity. The most critical: files longer than 2000 lines were **silently truncated** during patch operations, permanently losing all content after line 2000.

### Tier 1 — Data Loss / Correctness (Critical)

**Bug 1: Files > 2000 lines silently truncated**
- `_apply_update` called `read_file(limit=10000)`, but `read_file` clamps to `MAX_LINES = 2000`
- `write_file` overwrites the file with only first 2000 lines — lines 2001-N permanently lost
- Long lines (>2000 chars) truncated with `"... [truncated]"`, permanently corrupting content

**Bug 2: Operations continue after failure — no rollback**
- When operation N fails, operations N+1 through M are still applied
- Result reports `success=False` but filesystem is already partially modified

**Bug 3: `parse_v4a_patch` never returns an error**
- Function signature promises error reporting but always returns `None`
- Empty patches indistinguishable from parse failures

### Tier 2 — Incorrect Match Behaviour (High)

**Bug 4**: Similarity threshold too low (10%) — silently replaces wrong blocks
**Bug 5**: Unicode characters bypass exact match strategies — fall through to permissive fuzzy
**Bug 6**: Match strategy not surfaced — no visibility when fuzzy fallback fires

### Tier 3 — Low-Severity Gaps

**Bug 7**: Ambiguous context hint silently inserts at wrong location
**Bug 8**: Delete operation returns success on missing file
**Bug 9**: Move operation silently overwrites pre-existing destination

## Connection to ADE Theory

### Which ADE Principle Does This Violate?
**Data Decay (DD)**: Multiple mechanisms for silent data loss and corruption. The patch system — designed to modify files — is itself a source of data destruction.

**BCP (Behavior Contract Protocol)**: The function signatures promise safety (error returns, success flags) but deliver silent failures. The behavior contract is broken.

### How Could ADE Prevent This?
1. **Data Integrity Verification**: Post-write verification comparing written content length with expected
2. **Atomic Operations**: All-or-nothing patch application with rollback on failure
3. **Contract Enforcement**: Function return values must accurately reflect actual outcomes

## Lessons Learned

### For ADE Framework
- File modification tools are high-risk surfaces for data decay
- Limit clamping in read operations can cascade into write operations as data loss
- Fallback strategies (fuzzy matching) increase risk without observability

### For Practitioners
- Always verify file length before and after modification
- Implement rollback for multi-operation patch sequences
- Surface match strategy information to callers for verification

## References
- GitHub Issue: [#6831](https://github.com/NousResearch/hermes-agent/issues/6831)
- ADE Paper: [Intelligence Entropy](https://arxiv.org/abs/2606.18065)

---

## Metadata
- **Discovered by**: Community report (systematic audit)
- **Reviewed by**: Dexing Liu
- **Last updated**: 2026-06-17
