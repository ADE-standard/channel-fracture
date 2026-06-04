# MVP — Channel Fracture Minimal Reproducible Example

最小可复现示例，演示 Channel Fracture 现象及其 CADVP 修复方案。

## 运行方式

```bash
pip install -r requirements.txt
python demo_channel_fracture.py
```

## 目录结构

```
mvp/
├── demo_channel_fracture.py  # 主演示脚本
├── agents/
│   ├── scheduler_agent.py    # 定时触发写入的代理
│   └── target_agent.py       # 有持久化内存的目标代理
├── memory/
│   ├── persistent_memory.py  # 带 skip_memory=True 守卫的内存
│   └── memory_guard.py       # 内存隔离逻辑
└── cadvp/
    ├── cc0_verifier.py        # CC-0 确认检查
    └── delivery_protocol.py   # 跨 Agent 交付协议
```

## 演示流程

1. **场景设置** — Scheduler Agent 尝试向 Target Agent 写入持久化内存
2. **失败演示** — `skip_memory=True` 导致写入被静默丢弃（Channel Fracture 现象）
3. **修复演示** — 启用 CADVP CC-0 验证，捕获失败并通过动态注册修复
4. **结果输出** — 完整的日志：失败 → 检测 → 修复 → 成功

## 依赖

仅使用 Python 标准库，无额外依赖。

---

**Author:** Dexing Liu  
**License:** All Rights Reserved — 学术研究可自由使用，商业用途需授权。
