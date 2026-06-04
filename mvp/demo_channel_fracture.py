#!/usr/bin/env python3
"""
Channel Fracture — 最小可复现示例 (MVP Demo)

演示多智能体编排系统中 Channel Fracture 现象及 CADVP 三级门禁修复方案：

  完整流程：
  1. 场景设置：Scheduler Agent 尝试向 Target Agent 写入持久化内存
  2. 失败演示：skip_memory=True 导致写入失败（Channel Fracture 现象）
  3. CADVP CC-0 检测：验证器捕获 Channel Fracture
  4. 动态修复：注册专用通道，绕过 skip_memory 守卫
  5. ADE 三级门禁验证：L1 自验 → L2 证据 → L3 复核

Author: Dexing Liu
License: All Rights Reserved
"""

import sys
import os
import time
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agents.scheduler_agent import SchedulerAgent
from agents.target_agent import TargetAgent
from cadvp.cc0_verifier import CC0Verifier
from cadvp.delivery_protocol import DeliveryProtocol
from cadvp.gates import ThreeGateSystem


# ============================================================
# 格式化输出
# ============================================================

SEP = "=" * 72
THIN = "-" * 72

def h(title):
    print(f"\n{SEP}\n  {title}\n{SEP}")

def s(num, text):
    print(f"\n  [{num}] {text}")

def ok(text):
    print(f"  ✅ {text}")

def fail(text):
    print(f"  ❌ {text}")

def info(text):
    print(f"  ℹ️  {text}")

def fix(text):
    print(f"  🔧 {text}")

def gate(text, gate_level):
    labels = {"L1": "🟢 L1", "L2": "🔵 L2", "L3": "🟣 L3"}
    print(f"  {labels.get(gate_level, gate_level)} {text}")


# ============================================================
# Part 1-2: 场景设置 + 失败演示
# ============================================================

def part1_setup():
    h("Part 1: 场景设置 — 创建 Agent")

    sched = SchedulerAgent(name="Scheduler-Agent")
    target = TargetAgent(name="Target-Agent", skip_memory=True)

    info(f"创建 SchedulerAgent: {sched.name}")
    info(f"创建 TargetAgent: {target.name}")
    info(f"Target Agent skip_memory = {target.skip_memory}")
    info("说明: skip_memory=True 是编排系统默认安全设置,")
    info("      会阻止外部代理向目标代理写入持久化内存.")
    return sched, target


def part2_fracture(sched, target):
    h("Part 2: 失败演示 — Channel Fracture 现象")

    s(1, "Scheduler 尝试写入持久化内存...")
    info("操作: scheduler.schedule_write(target, 'task_context', 'MISSION_DATA: target_356')")

    result = sched.schedule_write(target, "task_context", "MISSION_DATA: target_356")

    if result["status"] == "skipped":
        fail("写入被静默丢弃!")
        fail("数据 'MISSION_DATA: target_356' 未到达 Target Agent!")
    else:
        ok("写入成功 (不应发生)")

    s(2, "检查 Target Agent 内存...")
    snapshot = target.get_memory_snapshot()
    info(f"Target 内存: {snapshot}")

    if "task_context" not in snapshot:
        fail("确认: 'task_context' 不在 Target 内存中")
        fail(">>> 这就是 Channel Fracture <<<")

    s(3, "CC-0 验证器独立检测...")
    verifier = CC0Verifier()
    v = verifier.verify_write(target, "task_context", "MISSION_DATA: target_356", result)

    if v["status"] == "FRACTURE_DETECTED":
        fail(f"CC-0 检测到 Channel Fracture!")
        info(f"详情: {v['detail']}")
        info(f"建议修复: {v.get('suggested_fix')}")

    return verifier


# ============================================================
# Part 3: CADVP 修复
# ============================================================

def part3_repair(sched, verifier):
    h("Part 3: 修复演示 — CADVP 跨代理交付协议")

    s(1, "创建新 Target Agent (skip_memory=True)...")
    target_new = TargetAgent(name="Target-Agent-Fresh", skip_memory=True)
    info(f"skip_memory = {target_new.skip_memory}")

    s(2, "CADVP DeliveryProtocol 执行完整交付...")
    protocol = DeliveryProtocol(verifier=verifier)
    info("流程: 写入 → CC-0验证 → 检测Fracture → 注册通道 → 重试 → 确认")

    print(f"\n  {THIN}")
    delivery = protocol.deliver_with_verification(
        sched, target_new, "repaired_context", "REPAIRED_MISSION_DATA"
    )

    for step in delivery["steps"]:
        print(f"\n  Step {step['step']}: {step['action']}")
        print(f"  描述: {step['description']}")

        if "result" in step:
            r = step["result"]
            if isinstance(r, dict):
                status = r.get("status", "")
                if status in ("skipped",):
                    fail(f"状态: {status}")
                elif status == "FRACTURE_DETECTED":
                    fail(f"状态: {status}")
                elif status == "VERIFIED":
                    ok(f"状态: {status}")
                elif status in ("channel_registered", "success"):
                    fix(f"状态: {status}")
                    if r.get("written"):
                        ok("写入成功")
                else:
                    info(f"状态: {status}")
            else:
                info(f"结果: {r}")

    print(f"\n  {THIN}")

    s(3, "交付结果")
    ok(f"最终状态: {delivery['final_status']}")
    ok(f"是否修复: {delivery['repaired']}")
    if delivery.get("channel_id"):
        info(f"修复通道: {delivery['channel_id']}")

    return target_new, protocol


# ============================================================
# Part 4: ADE 三级门禁验证
# ============================================================

def part4_three_gates(sched, target_new, protocol):
    h("Part 4: ADE 三级门禁验证")

    gates = ThreeGateSystem()

    s(1, "构建交付证据日志...")
    evidence_log = [
        {"event": "write_attempt_1", "result": "skipped", "reason": "skip_memory=True"},
        {"event": "cc0_detection", "result": "FRACTURE_DETECTED"},
        {"event": "channel_registered", "channel_id": protocol.verifier._verification_log[-1].get("channel_id", "cadvp_repair_*") if protocol.verifier._verification_log else "cadvp_repair_*"},
        {"event": "retry_via_channel", "result": "success"},
        {"event": "cc0_reverify", "result": "VERIFIED"}
    ]
    for ev in evidence_log:
        info(f"{ev['event']}: {ev.get('result', ev.get('channel_id', 'N/A'))}")

    s(2, "L1 Gate — Agent 自验...")
    delivery_value = target_new.get_memory_value("repaired_context")
    l1_result = gates.l1.verify(
        agent_name=target_new.name,
        key="repaired_context",
        value=delivery_value,
        required_fields=None
    )
    gate(f"自验结果: {'通过' if l1_result['passed'] else '失败'} ({l1_result['checks_passed']}/{l1_result['checks_total']} 检查)", "L1")
    for c in l1_result["checks"]:
        info(f"  [{c['check']}] {c['description']}: {'通过' if c['passed'] else '失败'}")

    s(3, "L2 Gate — 证据验证...")
    value_with_l1 = {"delivery_value": delivery_value, "_l1_report": l1_result}
    l2_result = gates.l2.verify(
        agent_name=target_new.name,
        key="repaired_context",
        value=value_with_l1,
        evidence_log=evidence_log
    )
    gate(f"证据验证: {'通过' if l2_result['passed'] else '失败'} ({l2_result['checks_passed']}/{l2_result['checks_total']} 检查)", "L2")
    for c in l2_result["checks"]:
        info(f"  [{c['check']}] {c['description']}: {'通过' if c['passed'] else '失败'}")

    s(4, "L3 Gate — 独立复核...")
    # L3 对原始交付值做哈希一致性验证（不包 metadata）
    l3_result = gates.l3.review(
        original_agent=target_new.name,
        key="repaired_context",
        value=delivery_value,
        l1_report=l1_result,
        l2_report=l2_result
    )
    gate(f"复核结果: {'通过' if l3_result['passed'] else '失败'} (质量评分: {l3_result['quality_score']})", "L3")
    for c in l3_result["checks"]:
        info(f"  [{c['check']}] {c['description']}: {'通过' if c['passed'] else '失败'} ({c.get('detail', '')})")

    s(5, "三级门禁总结果")
    all_pass = l1_result["passed"] and l2_result["passed"] and l3_result["passed"]
    if all_pass:
        ok("三级门禁全部通过 — CADVP 修复方案验证成功!")
    else:
        fail("三级门禁未完全通过")

    final_memory = target_new.get_memory_snapshot()
    info(f"Target Agent 最终内存: {final_memory}")

    return gates


# ============================================================
# Part 5: 统计汇总
# ============================================================

def part5_summary(sched, target_new, verifier, protocol, gates):
    h("Part 5: 统计数据汇总")

    s(1, "Memory Guard 统计")
    stats = target_new.guard.get_stats()
    info(f"skip_memory: {stats['skip_memory']}")
    info(f"已注册通道: {stats['allowed_channels']}")
    info(f"拦截次数: {stats['blocked_count']}")
    info(f"放行次数: {stats['allowed_count']}")

    s(2, "CC-0 验证器统计")
    vs = verifier.get_verification_summary()
    info(f"总验证: {vs['total_verifications']}")
    info(f"通过: {vs['verified']}")
    info(f"Fracture: {vs['fractures_detected']}")
    info(f"验证成功率: {vs['verification_rate']:.1f}%")

    s(3, "ADE 三级门禁统计")
    gs = gates.get_summary()
    gate(f"L1 自验: {gs['l1']['passed']}/{gs['l1']['total_self_verifications']} 通过", "L1")
    gate(f"L2 证据: {gs['l2']['passed']}/{gs['l2']['total_evidence_verifications']} 通过", "L2")
    gate(f"L3 复核: {gs['l3']['passed']}/{gs['l3']['total_reviews']} 通过, 平均质量 {gs['l3']['avg_quality']:.2f}", "L3")

    s(4, "Scheduler 写入统计")
    ws = sched.get_write_summary()
    info(f"总写入: {ws['total_writes']}")
    info(f"成功: {ws['successful']}")
    info(f"跳过: {ws['skipped']}")


# ============================================================
# Main
# ============================================================

def main():
    print(f"{SEP}")
    print(f"  Channel Fracture MVP Demo")
    print(f"  Paper: arXiv:2606.04896")
    print(f"  Author: Dexing Liu (刘德星)")
    print(f"  License: All Rights Reserved")
    print(f"  ---")
    print(f"  流程: 失败 → CC-0检测 → CADVP修复 → 三级门禁验证")
    print(f"{SEP}")

    sched, target = part1_setup()
    verifier = part2_fracture(sched, target)
    target_new, protocol = part3_repair(sched, verifier)
    gates = part4_three_gates(sched, target_new, protocol)
    part5_summary(sched, target_new, verifier, protocol, gates)

    h("Demo 完成")
    print("""
  Channel Fracture:
    当 skip_memory=True, Scheduler Agent 向 Target Agent 的
    持久化内存写入会被静默丢弃, 导致信息通道断裂.

  CADVP + ADE 三级门禁修复:
    1. CC-0 验证 → 检测写入是否成功
    2. 动态通道注册 → 绕过 skip_memory 守卫
    3. L1 自验 → Agent 自我检查交付完整性
    4. L2 证据 → 决策日志和验证记录
    5. L3 复核 → 独立代理交叉验证

  论文: arXiv:2606.04896
  GitHub: https://github.com/ADE-standard/channel-fracture
    """)
    print(f"{SEP}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
