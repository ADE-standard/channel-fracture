# Channel Fracture

**Channel Fracture: Architectural Blind Spots in Scheduled Cross-Agent Memory Injection for Multi-Agent Orchestration Systems**

📄 Paper: [arXiv:2606.04896](https://arxiv.org/abs/2606.04896)  
👤 Author: Dexing Liu (刘德星)

---

## 项目目标

Channel Fracture 揭示了多智能体编排系统中一个被忽视的架构盲区：当调度代理（Scheduler Agent）通过定时任务向目标代理（Target Agent）注入持久化内存时，由于 `skip_memory=True` 守卫机制的存在，写入操作会被静默丢弃，导致信息通道断裂。本仓库提供该问题的最小可复现示例（MVP）、CADVP（Cross-Agent Delivery Verification Protocol）修复方案，以及完整的实验数据。

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

运行后你将看到 Channel Fracture 现象的完整演示：
- ❌ **失败**：Scheduler Agent 写入被 `skip_memory=True` 静默丢弃
- 🔍 **检测**：CADVP CC-0 验证器捕获写入失败
- 🔧 **修复**：动态注册机制绕过守卫
- ✅ **成功**：Target Agent 成功接收持久化内存
- 🛡️ **ADE 三级门禁**：L1 自验 → L2 证据 → L3 复核 全链路验证交付质量

## 知识产权声明

**All Rights Reserved.** Copyright (c) 2026 Dexing Liu / Shanghai Qijing Digital Technology Co., Ltd.

学术研究可自由使用、修改、复制。商业用途请联系作者获取授权。作者保留所有权利，包括专利申请权。

详见 [LICENSE](LICENSE) 和 [CONTRIBUTING.md](CONTRIBUTING.md)。

## 模块说明

| 目录 | 说明 |
|------|------|
| [`mvp/`](mvp/) | 最小可复现示例 — 包含 Channel Fracture 演示脚本、模拟代理、内存守卫和 CADVP 验证协议 |
| [`docs/`](docs/) | 技术文档 — CADVP v1.1 规范文档和系统架构说明 |
| [`experiments/`](experiments/) | 实验数据 — 并发冲突检测、回滚安全、信息中继三组实验的完整结果 |

### MVP 子模块

- **`agents/`** — 模拟 Scheduler Agent（定时触发写入）和 Target Agent（带持久化内存）
- **`memory/`** — 持久化内存实现，含 `skip_memory=True` 守卫和内存隔离逻辑
- **`cadvp/`** — CADVP 跨代理交付验证协议，含 CC-0 确认检查 + ADE 三级门禁体系（L1 自验/L2 证据/L3 复核）
- **`demo_channel_fracture.py`** — 主演示脚本，一键复现 Channel Fracture 现象

## 引用

如果您在研究中使用了本项目，请引用：

```bibtex
@article{liu2026channelfracture,
  title={Channel Fracture: Architectural Blind Spots in Scheduled Cross-Agent Memory Injection for Multi-Agent Orchestration Systems},
  author={Liu, Dexing},
  journal={arXiv preprint arXiv:2606.04896},
  year={2026}
}
```

## License

All Rights Reserved — 详见 [LICENSE](LICENSE)。
