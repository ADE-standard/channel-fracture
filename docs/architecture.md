# 架构说明

## Channel Fracture 系统架构

**作者:** Dexing Liu  
**论文:** arXiv:2606.04896

---

## 1. 系统概览

```
┌─────────────────────────────────────────────────────────────┐
│                   Multi-Agent Orchestration                  │
│                                                              │
│  ┌──────────────┐     skip_memory=True     ┌──────────────┐ │
│  │  Scheduler   │ ──────── ✕ ──────────── │   Target     │ │
│  │    Agent     │   (Channel Fracture)     │    Agent     │ │
│  └──────────────┘                          └──────────────┘ │
│         │                                         │         │
│         │              ┌──────────────┐           │         │
│         └──────────────│   CADVP      │──────────┘         │
│                        │   Protocol   │                     │
│                        └──────────────┘                     │
└─────────────────────────────────────────────────────────────┘
```

## 2. 核心组件

### 2.1 Scheduler Agent（调度代理）

负责按计划触发跨代理写入操作。

**职责:**
- 维护写入计划队列
- 定时触发向目标代理的内存注入
- 记录写入操作日志

**关键接口:**
- `schedule_write(target, key, value)` — 调度单次写入
- `batch_schedule(target, writes)` — 批量调度
- `get_write_summary()` — 获取统计

### 2.2 Target Agent（目标代理）

拥有持久化内存的接收端代理。

**职责:**
- 管理持久化内存存储
- 通过 Memory Guard 控制外部写入准入
- 支持动态通道注册

**关键接口:**
- `receive_memory_write(key, value)` — 接收标准写入
- `receive_channel_write(key, value, channel_id)` — 接收通道写入
- `register_memory_channel(channel_id)` — 注册写入通道
- `get_memory_snapshot()` — 获取内存快照

### 2.3 Persistent Memory（持久化内存）

目标代理的内部键值存储层。

**特性:**
- 键值存储
- 操作历史记录
- 快照导出

### 2.4 Memory Guard（内存守卫）

控制外部写入准入的安全层。

**核心机制:**
```
if channel_id in allowed_channels:
    → 允许写入（已注册通道）
elif skip_memory == True:
    → 拦截写入（Channel Fracture 发生点）
else:
    → 允许写入（skip_memory 关闭）
```

**统计:**
- 拦截次数
- 放行次数
- 已注册通道列表

### 2.5 CADVP Protocol（交付验证协议）

跨代理交付的验证和修复层。

**流程:**
```
写入请求 → 执行写入 → CC-0 验证 → 
  ├─ VERIFIED → 完成
  └─ FRACTURE_DETECTED → 注册通道 → 重新写入 → 再次验证 → 完成
```

## 3. Channel Fracture 发生机制

```
时间线:

t0: Scheduler Agent 构造写入请求 {key, value}
t1: 请求到达 Target Agent 的 Memory Guard
t2: Memory Guard 检查 skip_memory 标志
t3: skip_memory == True → 写入被拦截
t4: 返回 {"status": "skipped", "reason": "skip_memory=True"}
t5: Scheduler Agent 收到响应（可能被误认为"已处理"）
t6: Target Agent 内存中数据不存在 → Channel Fracture

关键点: 整个过程没有任何异常抛出或错误日志
```

## 4. CADVP 修复机制

```
修复时间线:

t0: CC-0 验证器检查写入结果
t1: 检测到 status="skipped" → FRACTURE_DETECTED
t2: 生成修复通道 ID: cadvp_repair_{timestamp}
t3: 在 Target Agent 注册修复通道
t4: 通过修复通道重新写入
t5: Memory Guard 检查 channel_id ∈ allowed_channels → 允许
t6: 数据写入 Persistent Memory
t7: CC-0 再次验证 → VERIFIED
t8: Channel Fracture 修复完成
```

## 5. 数据流图

```
┌─────────────┐
│  Scheduler  │
│    Agent    │
└──────┬──────┘
       │ ① write(key, value)
       ▼
┌─────────────────────────────────────────────┐
│            Memory Guard                      │
│                                              │
│  channel_id ∈ allowed? ──Yes──→ ② Allow     │
│         │ No                                 │
│         ▼                                    │
│  skip_memory=True? ──Yes──→ ③ BLOCK ✕       │
│         │ No                   (Fracture!)   │
│         ▼                                    │
│  ④ Allow                                     │
└──────┬──────────────────────────────────────┘
       │ (if allowed)
       ▼
┌──────────────┐
│  Persistent  │
│   Memory     │
└──────────────┘
       │
       ▼
┌──────────────┐
│   CC-0       │
│  Verifier    │──→ VERIFIED / FRACTURE_DETECTED
└──────────────┘
```

## 6. 扩展性考量

- **多通道:** 支持为不同源代理注册不同通道
- **通道过期:** 可为通道设置 TTL 自动过期
- **审计日志:** 所有通道操作和验证结果可追溯
- **批量修复:** 支持一次性检测和修复多个 Channel Fracture

---

**Author:** Dexing Liu  
**License:** All Rights Reserved
