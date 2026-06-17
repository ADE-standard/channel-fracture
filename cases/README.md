# ADE Failure Case Studies

This directory contains real-world failure cases from the AI agent community, classified according to the ADE (Agent Delivery Engineering) taxonomy.

## Purpose

These case studies serve as empirical evidence for the ADE framework, demonstrating:
1. Real-world manifestations of the failure types described in our papers
2. How ADE protocols could have prevented these failures
3. Ongoing patterns in the evolving landscape of AI agent systems

## Classification System

- **CF (Configuration Failure)**: Misconfigurations or architectural gaps that lead to unintended system behavior
- **CFL (Cross-session Framework Lag)**: Inconsistencies between UI state and persistent state across sessions
- **DD (Data Decay)**: Degradation of data quality, silent data loss, or index corruption
- **KD (Knowledge Discontinuity)**: Gaps or inconsistencies in agent knowledge bases

## Case Index

| Case ID | Date | Type | Source | Severity | Description |
|---------|------|------|--------|----------|-------------|
| [CF-001](./CF-001-email-auto-reply.md) | 2026-06-17 | CF | Own discovery | Critical | Email Gateway auto-reply without human review |
| [CF-002](./CF-002-cron-memory-channel-fracture.md) | 2026-06-13 | CF | Issue #38647 | Critical | Cron agents silently lose memory write capability |
| [CF-003](./CF-003-cron-approval-deadlock.md) | 2026-05-30 | CF | Issue #35214 | High | Cron jobs fail silently due to tool approval deadlock |
| [CF-004](./CF-004-wecom-websocket-silent-reconnect.md) | 2026-06-17 | CF | Issue #47572 | High | WeCom WebSocket reconnection fails silently |
| [CF-005](./CF-005-qqbot-websocket-zombie-18h.md) | 2026-05-04 | CF | Issue #19821 | Critical | QQ Bot WebSocket zombie — 18+ hours silent death |
| [CF-006](./CF-006-wecom-846609-path-state-disconnect.md) | 2026-06-17 | CF | Issue #47564 | Critical | WeCom 846609: send path never triggers reconnection |
| [CF-007](./CF-007-wecom-ack-loss-duplicate-messages.md) | 2026-06-17 | CF | Issue #47573 | High | WeCom ACK loss causes duplicate message delivery |
| [CFL-001](./CFL-001-desktop-delete-profile-silent-fail.md) | 2026-06-17 | CFL | Issue #47368 | High | Desktop delete profile silently fails, profile reappears |
| [DD-001](./DD-001-context-compression-data-loss.md) | 2026-06-16 | DD | Issue #47202 | Critical | Context compression silently loses unflushed messages |
| [DD-002](./DD-002-v4a-patch-9bugs-data-loss.md) | 2026-04-09 | DD | Issue #6831 | Critical | V4A patch parser: 9 bugs causing silent data loss |
| [DD-003](./DD-003-state-db-fts-corruption.md) | 2026-05-28 | DD | Issue #33865 | Critical | state.db FTS corruption undetected, no repair |

**Total: 11 cases** (7 CF, 1 CFL, 3 DD)

## Statistics

| Type | Count | Critical | High |
|------|-------|----------|------|
| CF | 7 | 4 | 3 |
| CFL | 1 | 0 | 1 |
| DD | 3 | 3 | 0 |
| **Total** | **11** | **7** | **4** |

### Source Breakdown
- **Own discovery** (production incidents): 3 cases (CF-001, CF-004, CF-006, CF-007)
- **Community reports** (GitHub Issues): 7 cases

## Citation

These case studies support the following ADE papers:
- [Channel Fracture](https://github.com/ADE-standard/channel-fracture) (arXiv:2606.04896)
- [Silent Failure](https://github.com/ADE-standard/silent-failure) (arXiv:2606.08162)
- [Intelligence Entropy](https://github.com/ADE-standard/intelligence-entropy) (arXiv:2606.18065)

## How to Contribute

1. Use the [template](./failure-case-template.md) to document a case
2. Submit a PR with your case study

## License

CC-BY-4.0
