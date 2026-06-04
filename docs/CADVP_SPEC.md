# CADVP v1.1 规范文档

## Cross-Agent Delivery Verification Protocol（跨代理交付验证协议）

**版本:** v1.1  
**作者:** Dexing Liu  
**论文:** arXiv:2606.04896  
**日期:** 2026-06

---

## 1. 概述

CADVP（Cross-Agent Delivery Verification Protocol）是为解决多智能体编排系统中 Channel Fracture 问题而设计的交付验证协议。它提供了一种系统性的方法来检测、修复和预防跨代理信息传递中的静默失败。

## 2. 问题背景

### 2.1 Channel Fracture 定义

在多智能体编排系统中，当调度代理（Scheduler Agent）通过定时任务向目标代理（Target Agent）注入持久化内存时，由于 `skip_memory=True` 守卫机制的存在，写入操作被静默丢弃，导致信息通道断裂。

### 2.2 核心特征

- **系统性:** 不是偶发错误，而是架构设计导致的系统性问题
- **静默性:** 写入失败不会抛出异常或产生错误日志
- **隐蔽性:** 调度代理可能误认为写入成功

## 3. 协议层级

CADVP 定义了多个确认级别：

### 3.1 CC-0（Cross-agent Confirmation Level 0）

基础验证层，验证数据是否到达目标代理的内存存储。

**验证流程:**
1. 执行写入操作
2. 立即检查目标代理内存中是否存在该数据
3. 对比写入值与实际存储值
4. 如果不一致，标记为 Channel Fracture

**输出:**
- `VERIFIED`: 数据成功到达
- `FRACTURE_DETECTED`: 检测到 Channel Fracture
- `MISMATCH`: 数据到达但值不匹配
- `UNKNOWN`: 无法确定状态

### 3.2 CC-1（Cross-agent Confirmation Level 1）

语义验证层，验证数据在目标代理上下文中是否被正确理解和使用。

### 3.3 CC-2（Cross-agent Confirmation Level 2）

端到端验证层，验证数据是否最终影响了预期的系统行为。

## 4. ADE 三级门禁体系

ADE Three-Gate System 在 CC-0 交付验证之上增加了三层独立交付质量门禁：

### 4.1 L1 Gate — 自验门禁 (Self-Verification)

由交付 Agent 对自己即将交付的内容执行自检：

| 检查 | 说明 |
|------|------|
| 存在性 (Existence) | 交付值非空 |
| 完整性 (Completeness) | 必需字段全部存在 |
| 一致性 (Consistency) | 值格式和编码无异常 |

自验通过后，生成内容哈希用于后续追踪。

### 4.2 L2 Gate — 证据门禁 (Evidence Verification)

验证交付是否附带完整的证据链：

| 检查 | 说明 |
|------|------|
| 证据存在 (Evidence Exists) | 交付附带执行日志 |
| L1 报告 (L1 Report) | L1 自验报告已附加到交付 |
| 可追溯 (Traceability) | 内容哈希可独立验证 |

### 4.3 L3 Gate — 复核门禁 (Cross-Review)

由独立 Reviewer Agent 执行交叉验证：

| 检查 | 说明 |
|------|------|
| L1 有效性 (L1 Validation) | 验证 L1 自验是否真实通过 |
| L2 有效性 (L2 Validation) | 验证 L2 证据是否完备 |
| 数据完整性 (Data Integrity) | 独立重复数据完整性检查 |
| 哈希一致性 (Hash Consistency) | 内容哈希与 L1 记录一致 |

L3 输出质量评分 (0.0~1.0)，低于阈值时拒绝交付。

### 4.4 三级门禁流程图

```
交付内容 → [L1 自验] → [L2 证据] → [L3 复核] → 交付确认
              ↑              ↑             ↑
          Agent自检     证据日志     独立Reviewer
```

### 4.5 实现接口

```python
class L1SelfVerifier:
    def verify(agent_name, key, value, required_fields) -> dict
    def get_log() -> list
    def get_summary() -> dict

class L2EvidenceVerifier:
    def verify(agent_name, key, value, evidence_log) -> dict
    def get_log() -> list
    def get_summary() -> dict

class L3CrossReviewer:
    def review(original_agent, key, value, l1_report, l2_report) -> dict
    def get_log() -> list
    def get_summary() -> dict

class ThreeGateSystem:
    def execute_all_gates(...) -> dict
    def get_summary() -> dict
```

## 5. 修复机制

### 5.1 动态通道注册

当 CC-0 检测到 Channel Fracture 时，通过动态注册专用写入通道来绕过 `skip_memory` 守卫：

```
1. 生成唯一通道标识 (channel_id)
2. 在目标代理的 Memory Guard 中注册该通道
3. 通过注册通道重新执行写入
4. 再次 CC-0 验证确认成功
```

### 5.2 通道生命周期

- **创建:** 检测到 Fracture 时动态创建
- **注册:** 添加到目标代理的允许通道列表
- **使用:** 后续写入可通过该通道直接写入
- **注销:** 任务完成后可选择注销通道
- **审计:** 所有通道操作记录在案

## 6. 数据模型

### 6.1 写入记录 (Write Record)

```json
{
  "timestamp": "ISO8601",
  "source_agent": "string",
  "target_agent": "string",
  "key": "string",
  "value": "any",
  "channel_id": "string | null",
  "metadata": {}
}
```

### 6.2 验证结果 (Verification Result)

```json
{
  "timestamp": "ISO8601",
  "cc0_level": 0,
  "status": "VERIFIED | FRACTURE_DETECTED | MISMATCH | UNKNOWN",
  "key": "string",
  "target": "string",
  "data_reached_target": true | false,
  "detail": "string",
  "suggested_fix": "string | null"
}
```

### 6.3 交付日志 (Delivery Log)

```json
{
  "timestamp": "ISO8601",
  "source": "string",
  "target": "string",
  "key": "string",
  "value": "any",
  "steps": [],
  "final_status": "string",
  "repaired": true | false,
  "channel_id": "string | null"
}
```

## 7. 实现接口

### 7.1 CC0Verifier

```python
class CC0Verifier:
    def verify_write(target_agent, key, expected_value, write_result) -> dict
    def verify_channel_write(target_agent, key, expected_value, write_result, channel_id) -> dict
    def get_fracture_count() -> int
    def get_verification_summary() -> dict
```

### 7.2 DeliveryProtocol

### 7.3 ThreeGateSystem

```python
class ThreeGateSystem:
    def execute_all_gates(agent_name, reviewer_name, key, value) -> dict
    def get_summary() -> dict
```

```python
class DeliveryProtocol:
    def deliver_with_verification(scheduler_agent, target_agent, key, value) -> dict
    def get_delivery_summary() -> dict
```

## 8. 实验结果

CADVP 在以下实验场景中进行了验证：

| 实验 | 场景 | 核心指标 |
|------|------|----------|
| Concurrent T5 | 并发冲突检测 | 数据损坏率从 38% 降至 0% |
| Rollback T4 | 回滚安全 | 回滚成功率从 0% 升至 100% |
| Relay T3 | 信息中继 | 信息保留率从 91% 升至 100% |

详见 `experiments/results/` 目录。

## 9. 安全考量

- 通道注册应受到访问控制限制
- 修复通道不应被滥用为绕过安全机制的后门
- 所有通道操作应有审计日志
- 建议在生产环境中对通道设置 TTL（生存时间）

---

**Author:** Dexing Liu  
**License:** All Rights Reserved
