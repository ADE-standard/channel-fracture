# ADE Failure Case Studies

This directory contains real-world failure cases from the AI agent community, classified according to the ADE (Agent Delivery Engineering) taxonomy.

## Purpose

These case studies serve as empirical evidence for the ADE framework, demonstrating:
1. Real-world manifestations of the failure types described in our papers
2. How ADE protocols could have prevented these failures
3. Ongoing patterns in the evolving landscape of AI agent systems

## Classification System

- **CF (Configuration Failure)**: Misconfigurations that lead to unintended system behavior
- **CFL (Cross-session Framework Lag)**: Inconsistencies across sessions or deployments
- **DD (Data Decay)**: Degradation of data quality or relevance over time
- **KD (Knowledge Discontinuity)**: Gaps or inconsistencies in agent knowledge bases

## Case Index

| Case ID | Date | Type | Repository | Severity | Description |
|---------|------|------|------------|----------|-------------|
| [CF-001](./CF-001-email-auto-reply.md) | 2026-06-17 | CF | Hermes Agent | Critical | Email Gateway auto-reply without human review |

## How to Contribute

1. Identify a failure case in an AI agent system (GitHub Issue, blog post, personal experience)
2. Use the [template](../failure-case-template.md) to document the case
3. Submit a PR with your case study

## Citation

These case studies support the following ADE papers:
- [Channel Fracture](https://github.com/ADE-standard/channel-fracture) (arXiv:2606.04896)
- [Silent Failure](https://github.com/ADE-standard/silent-failure) (arXiv:2606.08162)
- [Intelligence Entropy](https://github.com/ADE-standard/intelligence-entropy) (arXiv:2606.18065)

## License

CC-BY-4.0
