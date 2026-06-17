# DD-003: state.db FTS Corruption Goes Undetected — No Integrity Check, No Repair

## Case ID
DD-003

## Date
2026-05-28

## Source
- Repository: [NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent)
- Issue: [#33865 - state.db FTS corruption goes undetected](https://github.com/NousResearch/hermes-agent/issues/33865)
- Related code: `agent/session_db.py`

## Classification
- **Type**: DD (Data Decay)
- **Severity**: Critical
- **Impact**: Session search returns incomplete or no results, no recovery path

## Description

### What Happened
The SQLite FTS5 (Full-Text Search) index in `state.db` can become corrupted without any detection mechanism. When corrupted:
- `session_search` returns incomplete or empty results
- No error is reported to the user
- No integrity check runs automatically
- No repair path exists

### Root Cause
The FTS5 virtual table is maintained separately from the main session table. Corruption can occur due to:
- Abnormal process termination during write
- Disk I/O errors
- Concurrent access conflicts

The system has no `PRAGMA integrity_check` or `FTS5 rebuild` mechanism, and no periodic health verification.

### Evidence
Users report `session_search` returning no results for queries that previously worked, while the underlying session data is intact. The FTS index is silently broken.

## Connection to ADE Theory

### Which ADE Principle Does This Violate?
**Data Decay (DD)**: The search index — a derived data structure — decays silently while the source data remains intact. This is data decay in a secondary structure.

**Intelligence Entropy**: The system's ability to retrieve knowledge (search) degrades over time without active preservation (integrity checks).

### How Could ADE Prevent This?
1. **Periodic Integrity Checks**: Run `PRAGMA integrity_check` and FTS rebuild on schedule
2. **Query Verification**: Cross-check search results with direct table queries for consistency
3. **Self-Healing**: Automatic FTS rebuild when corruption is detected

## Lessons Learned

### For ADE Framework
- Derived data structures (indexes, caches) require independent integrity monitoring
- Silent corruption in secondary structures is harder to detect than primary data loss
- Self-healing mechanisms are essential for long-running data stores

### For Practitioners
- Schedule periodic `PRAGMA integrity_check` for SQLite databases
- Implement FTS rebuild as a maintenance operation
- Cross-validate search results against primary data

## References
- GitHub Issue: [#33865](https://github.com/NousResearch/hermes-agent/issues/33865)
- Related: [#19434](https://github.com/NousResearch/hermes-agent/issues/19434) (session_search recall failures)
- ADE Paper: [Intelligence Entropy](https://arxiv.org/abs/2606.18065)

---

## Metadata
- **Discovered by**: Community report
- **Reviewed by**: Dexing Liu
- **Last updated**: 2026-06-17
