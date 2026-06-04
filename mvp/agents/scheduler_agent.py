"""
Scheduler Agent — 定时触发写入的代理

模拟多智能体编排系统中的调度代理，负责按计划向目标代理注入信息。

Author: Dexing Liu
License: All Rights Reserved
"""

import time
from typing import Any, Dict, Optional


class SchedulerAgent:
    """调度代理：定时触发向目标代理的内存写入操作。"""

    def __init__(self, name: str = "SchedulerAgent"):
        self.name = name
        self.write_log: list = []
        self._scheduled_writes: list = []

    def schedule_write(self, target_agent, key: str, value: Any, 
                        delay: float = 0.0) -> Dict[str, Any]:
        """
        安排一次向目标代理的写入操作。
        
        Args:
            target_agent: 目标代理实例
            key: 写入的键名
            value: 写入的值
            delay: 延迟秒数（模拟定时触发）
            
        Returns:
            写入操作的结果字典
        """
        write_record = {
            "timestamp": time.time(),
            "target": target_agent.name,
            "key": key,
            "value": value,
            "delay": delay,
            "status": "pending"
        }

        if delay > 0:
            time.sleep(delay)

        # 执行写入
        result = target_agent.receive_memory_write(key, value)
        write_record["status"] = result["status"]
        write_record["response"] = result

        self.write_log.append(write_record)
        return write_record

    def batch_schedule(self, target_agent, writes: list) -> list:
        """
        批量调度写入操作。
        
        Args:
            target_agent: 目标代理实例
            writes: [(key, value), ...] 写入列表
            
        Returns:
            所有写入操作的结果列表
        """
        results = []
        for key, value in writes:
            result = self.schedule_write(target_agent, key, value)
            results.append(result)
        return results

    def get_write_summary(self) -> Dict[str, Any]:
        """获取写入操作摘要。"""
        total = len(self.write_log)
        success = sum(1 for w in self.write_log if w["status"] == "success")
        failed = sum(1 for w in self.write_log if w["status"] == "failed")
        skipped = sum(1 for w in self.write_log if w["status"] == "skipped")

        return {
            "total_writes": total,
            "successful": success,
            "failed": failed,
            "skipped": skipped,
            "success_rate": (success / total * 100) if total > 0 else 0.0
        }
