# Channel Fracture

**Channel Fracture: Architectural Blind Spots in Scheduled Cross-Agent Memory Injection for Multi-Agent Orchestration Systems**

📄 Paper: [arXiv:2606.04896](https://arxiv.org/abs/2606.04896) (v3, 2026-06-09)  
📥 PDF: [papers/channel-fracture-v3.pdf](papers/channel-fracture-v3.pdf)  
👤 Author: Dexing Liu (刘德星)  
🏢 Affiliation: Shanghai Qijing Digital Technology Co., Ltd.

---

## 项目目标

Channel Fracture 揭示了多智能体编排系统中一个被忽视的架构盲区：当调度代理（Scheduler Agent）通过定时任务向目标代理（Target Agent）注入持久化内存时，由于 `skip_memory=True` 守卫机制的存在，写入操作会被静默丢弃，导致信息通道断裂。

本仓库提供该问题的**最小可复现示例（MVP）**、**ADE 三级门禁验证体系**，以及完整的实验数据。

## 版本说明

| 版本 | 日期 | 更新内容 |
|:----|:-----|:--------|
| **v3** | 2026-06-09 | 论文定稿，扩展 5 组对照实验 + 理论分析 + 去偏策略；简化仓库结构，移除协议实现细节 |
| v2 | 2026-06-04 | 扩展受控实验（210次模拟 + 99次真实运行 = 309总实验数），架构可视化增强，三级门禁验证体系全面集成 |
| v1 | 2026-06-03 | 初始版本：210次独立实验验证 |

## 架构对比

左：Channel Fracture 发生时的信息断裂 ｜ 右：CADVP 修复后的可靠交付

![Architecture Overview](experiments/visuals/architecture_overview.png)

## 快速体验

```bash
# 1. 克隆仓库
git clone https://github.com/ADE-standard/channel-fracture.git
cd channel-fracture

# 2. 安装依赖
cd mvp
pip install -r requirements.txt

# 3. 运行 Demo
python demo_channel_fracture.py
```

运行后你将看到完整流程：

| 阶段 | 说明 |
|:-----|:-----|
| ❌ **失败** | Scheduler Agent 写入被 `skip_memory=True` 静默丢弃 |
| 🔍 **检测** | 验证器捕获写入失败 |
| 🔧 **修复** | 动态注册专用通道绕过守卫 |
| ✅ **成功** | Target Agent 成功接收持久化内存 |
| 🛡️ **三级门禁** | L1 自验 → L2 证据 → L3 复核 全链路验证 |

## 实验验证

三组受控模拟实验（T3/T4/T5，总计210次）+ 四组真实运行实验（99次），合计309次独立实验验证了 CADVP 的有效性：

### 综合对比

![Experiment Summary](experiments/visuals/all_experiments_summary.png)

### T3: 跨域信息中继

信息保留率从 **87-94%** 提升至 **100%**，数据失真和需求误解完全消除。

![Relay Comparison](experiments/visuals/relay_comparison.png)

### T4: 回滚恢复安全

回滚成功率和状态恢复率从 **0%** 提升至 **100%**，脏文件从平均 2.0 降至 0。

![Rollback Comparison](experiments/visuals/rollback_comparison.png)

### T5: 并发冲突检测

裸并发下数据损坏率 **38-99%**（取决于场景和并发数），CADVP 保护后全部降至 **0%**。

![Concurrent Comparison](experiments/visuals/concurrent_comparison.png)

## 讨论与引用

本工作是 Agent Delivery Engineering (ADE) 标准的一部分。若本工作对您的研究或工程实践有启发，欢迎引用：

```bibtex
@misc{liu2026channel,
  author = {Dexing Liu},
  title = {Channel Fracture: Architectural Blind Spots in Scheduled Cross-Agent Memory Injection 
           for Multi-Agent Orchestration Systems},
  year = {2026},
  eprint = {2606.04896},
  archivePrefix = {arXiv},
  primaryClass = {cs.MA},
  note = {v3}
}
```

## 安全声明

本仓库仅公开论文和最小可复现示例（MVP）。完整的 **CADVP 协议规范**、**ADE 交付标准** 属于商业机密，可通过 [qijing@qijing.ai](mailto:qijing@qijing.ai) 联系授权。

## License

All Rights Reserved. Academic research use is free. Commercial use requires authorization.
