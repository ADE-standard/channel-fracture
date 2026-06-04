#!/usr/bin/env python3
"""
Channel Fracture — 最小可复现示例 (MVP Demo)

演示多智能体编排系统中 Channel Fracture 现象：
  Scheduler Agent → Target Agent 的持久化内存写入被 skip_memory=True 静默丢弃

完整流程：
  1. 场景设置：Scheduler Agent 尝试向 Target Agent 写入持久化内存
  2. 失败演示：skip_memory=True 导致写入失败（Channel Fracture 现象）
  3. 修复演示：启用 CADVP CC-0 验证，捕获失败并通过动态注册修复
  4. 结果输出：完整的日志 — 失败 → 检测 → 修复 → 成功

Author: Dexing Liu
License: All Rights Reserved
"""

import sys
import os
import time
import json

# 确保可以导入同级模块
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agents.scheduler_agent import SchedulerAgent
from agents.target_agent import TargetAgent
from cadvp.cc0_verifier import CC0Verifier
from cadvp.delivery_protocol import DeliveryProtocol


# ============================================================
# 格式化输出工具
# ============================================================

SEPARATOR = "=" * 70
THIN_SEP = "-" * 70

def header(title: str):
    print(f"\n{SEPARATOR}")
    print(f"  {title}")
    print(f"{SEPARATOR}")

def step(num: int, text: str):
    print(f"\n  [{num}] {text}")

def success(text: str):
    print(f"  ✅ {text}")

def failure(text: str):
    print(f"  ❌ {text}")

def info(text: str):
    print(f"  ℹ️  {text}")

def warning(text: str):
    print(f"  ⚠️  {text}")

def repair(text: str):
    print(f"  🔧 {text}")

def detail(key: str, value):
    print(f"     {key}: {value}")


# ============================================================
# 主演示流程
# ============================================================

def main():
    print(f"\n{SEPARATOR}")
    print(f"  Channel Fracture MVP Demo")
    print(f"  Paper: arXiv:2606.04896")
    print(f"  Author: Dexing Liu (刘德星)")
    print(f"{SEPARATOR}")

    # ----------------------------------------------------------
    # 第一部分：场景设置
    # ----------------------------------------------------------
    header("Part 1: 场景设置 — 创建 Agent 实例")

    scheduler = SchedulerAgent(name="SchedulerAgent")
    target = TargetAgent(name="TargetAgent", skip_memory=True)

    info(f"创建 SchedulerAgent: {scheduler.name}")
    info(f"创建 TargetAgent: {target.name}")
    info(f"Target Agent skip_memory = {target.skip_memory}")
    info("说明: skip_memory=True 是编排系统的默认安全设置，")
    info("      它会阻止外部代理向目标代理写入持久化内存。")

    # ----------------------------------------------------------
    # 第二部分：失败演示 — Channel Fracture 现象
    # ----------------------------------------------------------
    header("Part 2: 失败演示 — Channel Fracture 现象")

    step(1, "Scheduler Agent 尝试写入持久化内存...")
    info("操作: scheduler.schedule_write(target, 'task_context', 'critical_data')")

    write_result = scheduler.schedule_write(
        target_agent=target,
        key="task_context",
        value="critical_data"
    )

    detail("写入状态", write_result["status"])
    detail("写入原因", write_result.get("response", {}).get("reason", "N/A"))

    if write_result["status"] == "skipped":
        failure("写入被静默丢弃！")
        failure("数据 'critical_data' 未到达 Target Agent 的持久化内存")
    else:
        success("写入成功（不应该发生，skip_memory=True）")

    step(2, "验证 Target Agent 内存状态...")
    memory_snapshot = target.get_memory_snapshot()
    info(f"Target Agent 内存内容: {memory_snapshot}")

    if "task_context" not in memory_snapshot:
        failure("确认：'task_context' 不在 Target Agent 内存中")
        failure(">>> 这就是 Channel Fracture <<<")
    else:
        success("'task_context' 存在于内存中")

    step(3, "CC-0 验证器独立检测...")
    verifier = CC0Verifier()
    v_result = verifier.verify_write(
        target_agent=target,
        key="task_context",
        expected_value="critical_data",
        write_result=write_result["response"]
    )

    detail("CC-0 验证状态", v_result["status"])
    detail("验证详情", v_result.get("detail", "N/A"))
    detail("数据到达目标", v_result.get("data_reached_target"))

    if v_result["status"] == "FRACTURE_DETECTED":
        failure("CC-0 验证器检测到 Channel Fracture!")
        info(f"建议修复方式: {v_result.get('suggested_fix', 'N/A')}")

    # ----------------------------------------------------------
    # 第三部分：修复演示 — CADVP 协议
    # ----------------------------------------------------------
    header("Part 3: 修复演示 — CADVP 跨代理交付协议")

    step(1, "创建全新的 Target Agent（skip_memory=True）...")
    target_fresh = TargetAgent(name="TargetAgent_Fresh", skip_memory=True)
    info(f"新 Target Agent skip_memory = {target_fresh.skip_memory}")

    step(2, "使用 CADVP DeliveryProtocol 执行完整交付流程...")
    info("流程: 写入 → CC-0验证 → 检测Fracture → 注册通道 → 重试 → 确认")

    protocol = DeliveryProtocol()

    print(f"\n  {THIN_SEP}")
    delivery_result = protocol.deliver_with_verification(
        scheduler_agent=scheduler,
        target_agent=target_fresh,
        key="repaired_context",
        value="repaired_critical_data"
    )

    # 逐步输出交付日志
    for s in delivery_result["steps"]:
        step_num = s["step"]
        action = s["action"]
        desc = s["description"]
        print(f"\n  Step {step_num}: {action}")
        print(f"  描述: {desc}")

        if "result" in s:
            result = s["result"]
            if isinstance(result, dict):
                status = result.get("status", "N/A")
                if status == "skipped":
                    failure(f"状态: {status}")
                    detail("原因", result.get("reason", "N/A"))
                elif status == "FRACTURE_DETECTED":
                    failure(f"状态: {status}")
                    detail("原因", result.get("reason", "N/A"))
                    detail("数据到达", result.get("data_reached_target"))
                elif status == "VERIFIED":
                    success(f"状态: {status}")
                    detail("数据到达", result.get("data_reached_target"))
                elif status == "channel_registered":
                    repair(f"通道注册成功: {s.get('channel_id', 'N/A')}")
                elif status == "success":
                    success(f"写入状态: {status}")
                    detail("键", result.get("key", "N/A"))
                    detail("写入成功", result.get("written"))
                else:
                    info(f"状态: {status}")

    print(f"\n  {THIN_SEP}")

    # 最终结果
    final_status = delivery_result.get("final_status")
    repaired = delivery_result.get("repaired")

    step(3, "交付结果汇总")
    detail("最终状态", final_status)
    detail("是否修复", repaired)
    detail("修复通道", delivery_result.get("channel_id", "N/A"))

    if final_status == "VERIFIED" and repaired:
        success("Channel Fracture 已通过 CADVP 协议成功修复！")
        success("数据 'repaired_critical_data' 已成功写入 Target Agent 内存")
    else:
        failure("修复未成功")

    # ----------------------------------------------------------
    # 第四部分：验证修复效果
    # ----------------------------------------------------------
    header("Part 4: 验证修复效果")

    step(1, "检查 Target Agent 内存...")
    final_memory = target_fresh.get_memory_snapshot()
    info(f"Target Agent 内存内容: {final_memory}")

    if "repaired_context" in final_memory:
        success(f"确认：'repaired_context' = '{final_memory['repaired_context']}'")
        success("数据已成功通过 CADVP 修复通道写入持久化内存")
    else:
        failure("'repaired_context' 不在内存中")

    step(2, "Memory Guard 统计...")
    guard_stats = target_fresh.guard.get_stats()
    detail("skip_memory", guard_stats["skip_memory"])
    detail("已注册通道", guard_stats["allowed_channels"])
    detail("拦截次数", guard_stats["blocked_count"])
    detail("放行次数", guard_stats["allowed_count"])

    step(3, "CC-0 验证器统计...")
    v_summary = protocol.verifier.get_verification_summary()
    detail("总验证次数", v_summary["total_verifications"])
    detail("验证通过", v_summary["verified"])
    detail("Fracture 检测", v_summary["fractures_detected"])
    detail("验证成功率", f"{v_summary['verification_rate']:.1f}%")

    step(4, "Scheduler Agent 写入统计...")
    write_summary = scheduler.get_write_summary()
    detail("总写入次数", write_summary["total_writes"])
    detail("成功", write_summary["successful"])
    detail("失败", write_summary["failed"])
    detail("跳过", write_summary["skipped"])

    # ----------------------------------------------------------
    # 总结
    # ----------------------------------------------------------
    header("Demo 总结")

    print("""
  Channel Fracture 问题:
    当 skip_memory=True（多智能体编排系统默认设置），Scheduler Agent
    向 Target Agent 的持久化内存写入会被静默丢弃，导致信息通道断裂。

  CADVP 修复方案:
    1. CC-0 验证器检测写入是否成功到达目标
    2. 检测到 Channel Fracture 后，动态注册专用写入通道
    3. 通过注册通道重新写入，绕过 skip_memory 守卫
    4. 再次验证确认数据成功到达

  关键发现:
    • Channel Fracture 是系统性的，不是偶发错误
    • 静默丢弃（silent drop）使其难以被常规日志发现
    • CADVP 的 CC-0 验证层可以可靠地检测并修复此问题
    """)

    print(f"{SEPARATOR}")
    print(f"  Demo 完成。如需更多信息，请参阅论文 arXiv:2606.04896")
    print(f"{SEPARATOR}\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
