"""
Delivery Protocol — 跨 Agent 交付协议

实现 CADVP 的完整交付流程：写入 → 验证 → 检测失败 → 修复 → 重试 → 确认。

Author: Dexing Liu
License: All Rights Reserved
"""

import time
from typing import Any, Dict, Optional
from .cc0_verifier import CC0Verifier


class DeliveryProtocol:
    """
    CADVP 跨代理交付协议。
    
    完整的交付流程：
    1. 源代理发起写入
    2. CC-0 验证器检查写入是否到达
    3. 如果检测到 Channel Fracture，触发修复机制
    4. 通过动态注册通道重新写入
    5. 再次验证确认修复成功
    """

    def __init__(self):
        self.verifier = CC0Verifier()
        self._delivery_log: list = []

    def deliver_with_verification(self, scheduler_agent, target_agent,
                                  key: str, value: Any) -> Dict[str, Any]:
        """
        带验证的完整交付流程。
        
        自动完成：写入 → 验证 → 检测 → 修复 → 重试 → 确认
        
        Args:
            scheduler_agent: 源代理（调度代理）
            target_agent: 目标代理
            key: 写入键名
            value: 写入值
            
        Returns:
            完整的交付流程日志
        """
        delivery = {
            "timestamp": time.time(),
            "key": key,
            "value": value,
            "source": scheduler_agent.name,
            "target": target_agent.name,
            "steps": []
        }

        # Step 1: 尝试写入
        step1 = {
            "step": 1,
            "action": "attempt_write",
            "description": f"{scheduler_agent.name} → {target_agent.name}: write '{key}'"
        }
        write_result = scheduler_agent.schedule_write(target_agent, key, value)
        step1["result"] = write_result
        delivery["steps"].append(step1)

        # Step 2: CC-0 验证
        step2 = {
            "step": 2,
            "action": "cc0_verify",
            "description": "CC-0 Verification: check if data reached target"
        }
        verification = self.verifier.verify_write(
            target_agent, key, value, write_result
        )
        step2["result"] = verification
        delivery["steps"].append(step2)

        # Step 3: 如果检测到 Fracture，触发修复
        if verification["status"] == "FRACTURE_DETECTED":
            step3 = {
                "step": 3,
                "action": "fracture_detected",
                "description": (
                    f"Channel Fracture detected! "
                    f"Reason: {verification['reason']}. "
                    f"Initiating repair..."
                )
            }
            delivery["steps"].append(step3)

            # Step 4: 动态注册通道
            channel_id = f"cadvp_repair_{int(time.time())}"
            step4 = {
                "step": 4,
                "action": "register_channel",
                "description": f"Registering repair channel: {channel_id}",
                "channel_id": channel_id
            }
            target_agent.register_memory_channel(channel_id)
            step4["result"] = "channel_registered"
            delivery["steps"].append(step4)

            # Step 5: 通过注册通道重新写入
            step5 = {
                "step": 5,
                "action": "retry_via_channel",
                "description": f"Retrying write via channel '{channel_id}'"
            }
            retry_result = target_agent.receive_channel_write(key, value, channel_id)
            step5["result"] = retry_result
            delivery["steps"].append(step5)

            # Step 6: 再次验证
            step6 = {
                "step": 6,
                "action": "cc0_reverify",
                "description": "CC-0 Re-verification after repair"
            }
            re_verification = self.verifier.verify_channel_write(
                target_agent, key, value, retry_result, channel_id
            )
            step6["result"] = re_verification
            delivery["steps"].append(step6)

            delivery["final_status"] = re_verification["status"]
            delivery["repaired"] = True
            delivery["channel_id"] = channel_id
        else:
            delivery["final_status"] = verification["status"]
            delivery["repaired"] = False

        self._delivery_log.append(delivery)
        return delivery

    def get_delivery_summary(self) -> Dict[str, Any]:
        """获取交付摘要。"""
        total = len(self._delivery_log)
        repaired = sum(1 for d in self._delivery_log if d.get("repaired"))
        direct_success = sum(
            1 for d in self._delivery_log 
            if d.get("final_status") == "VERIFIED" and not d.get("repaired")
        )

        return {
            "total_deliveries": total,
            "direct_success": direct_success,
            "repaired_success": repaired,
            "overall_success_rate": (
                (direct_success + repaired) / total * 100 if total > 0 else 0.0
            )
        }
