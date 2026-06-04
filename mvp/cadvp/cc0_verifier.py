"""
CC-0 Verifier — CC-0 确认检查

CC-0 (Cross-agent Confirmation Level 0) 是 CADVP 协议的基础验证层。
它验证跨代理信息交付是否成功到达目标，检测 Channel Fracture 等传输失败。

Author: Dexing Liu
License: All Rights Reserved
"""

import time
from typing import Any, Dict, List, Optional


class CC0Verifier:
    """
    CC-0 验证器：验证跨代理写入是否成功到达。
    
    CC-0 检查的核心逻辑：
    1. 写入操作执行后，立即验证目标内存中是否存在该数据
    2. 如果数据不存在，标记为 Channel Fracture
    3. 提供修复建议（如动态注册通道）
    """

    def __init__(self):
        self._verification_log: List[Dict] = []
        self._fracture_detections: int = 0

    def verify_write(self, target_agent, key: str, expected_value: Any,
                     write_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        验证写入是否成功到达目标代理。
        
        Args:
            target_agent: 目标代理实例
            key: 写入的键名
            expected_value: 期望写入的值
            write_result: 写入操作的返回结果
            
        Returns:
            验证结果字典
        """
        verification = {
            "timestamp": time.time(),
            "key": key,
            "target": target_agent.name,
            "cc0_level": 0,
        }

        # 检查写入结果状态
        if write_result.get("status") == "skipped":
            # Channel Fracture 检测到！
            self._fracture_detections += 1
            verification["status"] = "FRACTURE_DETECTED"
            verification["reason"] = write_result.get("reason", "unknown")
            verification["detail"] = (
                f"Write to '{key}' was silently dropped. "
                f"skip_memory={write_result.get('skip_memory', True)} "
                f"blocked the delivery. This is a Channel Fracture."
            )
            verification["suggested_fix"] = "register_channel"
            verification["data_reached_target"] = False

        elif write_result.get("status") == "success":
            # 验证数据确实到达
            actual_value = target_agent.get_memory_value(key)
            if actual_value == expected_value:
                verification["status"] = "VERIFIED"
                verification["detail"] = f"Data successfully stored at '{key}'."
                verification["data_reached_target"] = True
            else:
                verification["status"] = "MISMATCH"
                verification["detail"] = (
                    f"Write reported success but value mismatch. "
                    f"Expected: {expected_value}, Got: {actual_value}"
                )
                verification["data_reached_target"] = False

        else:
            verification["status"] = "UNKNOWN"
            verification["detail"] = f"Unexpected write status: {write_result.get('status')}"
            verification["data_reached_target"] = False

        self._verification_log.append(verification)
        return verification

    def verify_channel_write(self, target_agent, key: str, expected_value: Any,
                             write_result: Dict[str, Any],
                             channel_id: str) -> Dict[str, Any]:
        """
        验证通过注册通道的写入（修复后验证）。
        
        Args:
            target_agent: 目标代理实例
            key: 写入键名
            expected_value: 期望值
            write_result: 写入结果
            channel_id: 使用的通道ID
            
        Returns:
            验证结果字典
        """
        base_verification = self.verify_write(
            target_agent, key, expected_value, write_result
        )
        base_verification["channel_id"] = channel_id
        base_verification["repair_method"] = "dynamic_channel_registration"
        return base_verification

    def get_fracture_count(self) -> int:
        """获取检测到的 Channel Fracture 次数。"""
        return self._fracture_detections

    def get_verification_summary(self) -> Dict[str, Any]:
        """获取验证摘要。"""
        total = len(self._verification_log)
        verified = sum(1 for v in self._verification_log if v["status"] == "VERIFIED")
        fractures = sum(1 for v in self._verification_log if v["status"] == "FRACTURE_DETECTED")

        return {
            "total_verifications": total,
            "verified": verified,
            "fractures_detected": fractures,
            "mismatches": sum(1 for v in self._verification_log if v["status"] == "MISMATCH"),
            "verification_rate": (verified / total * 100) if total > 0 else 0.0
        }
