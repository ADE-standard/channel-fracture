"""
Target Agent — 有持久化内存的目标代理

模拟具有持久化内存存储的目标代理，其内存写入接口受 memory guard 保护。

Author: Dexing Liu
License: All Rights Reserved
"""

import time
from typing import Any, Dict, Optional
from memory.persistent_memory import PersistentMemory
from memory.memory_guard import MemoryGuard


class TargetAgent:
    """目标代理：拥有持久化内存，受 memory guard 保护。"""

    def __init__(self, name: str = "TargetAgent", skip_memory: bool = True):
        """
        Args:
            name: 代理名称
            skip_memory: 是否启用 skip_memory 守卫（默认 True，导致 Channel Fracture）
        """
        self.name = name
        self.memory = PersistentMemory(agent_name=name)
        self.guard = MemoryGuard(skip_memory=skip_memory)
        self.receive_log: list = []

    @property
    def skip_memory(self) -> bool:
        return self.guard.skip_memory

    @skip_memory.setter
    def skip_memory(self, value: bool):
        self.guard.skip_memory = value

    def receive_memory_write(self, key: str, value: Any) -> Dict[str, Any]:
        """
        接收来自调度代理的内存写入请求。
        
        Args:
            key: 写入键名
            value: 写入值
            
        Returns:
            写入结果字典
        """
        write_record = {
            "timestamp": time.time(),
            "key": key,
            "value": value,
            "source": "external_agent"
        }

        # 通过 memory guard 检查
        guard_result = self.guard.check_write(write_record)

        if guard_result["blocked"]:
            # Channel Fracture 发生点：写入被静默丢弃
            result = {
                "status": "skipped",
                "reason": guard_result["reason"],
                "key": key,
                "written": False,
                "skip_memory": self.guard.skip_memory
            }
        else:
            # 写入成功
            self.memory.store(key, value)
            result = {
                "status": "success",
                "reason": "write_allowed",
                "key": key,
                "written": True,
                "skip_memory": self.guard.skip_memory
            }

        self.receive_log.append(result)
        return result

    def get_memory_snapshot(self) -> Dict[str, Any]:
        """获取当前内存快照。"""
        return self.memory.get_all()

    def get_memory_value(self, key: str) -> Optional[Any]:
        """获取指定键的内存值。"""
        return self.memory.get(key)

    def register_memory_channel(self, channel_id: str) -> bool:
        """
        动态注册内存写入通道（CADVP 修复机制）。
        
        通过在 memory guard 中注册特定通道，允许该通道的写入绕过 skip_memory 守卫。
        
        Args:
            channel_id: 通道标识符
            
        Returns:
            是否注册成功
        """
        self.guard.register_allowed_channel(channel_id)
        return True

    def receive_channel_write(self, key: str, value: Any, 
                             channel_id: str) -> Dict[str, Any]:
        """
        通过已注册通道接收写入（CADVP 修复后的写入路径）。
        
        Args:
            key: 写入键名
            value: 写入值
            channel_id: 通道标识符
            
        Returns:
            写入结果字典
        """
        write_record = {
            "timestamp": time.time(),
            "key": key,
            "value": value,
            "source": "external_agent",
            "channel_id": channel_id
        }

        guard_result = self.guard.check_write(write_record)

        if guard_result["blocked"]:
            result = {
                "status": "skipped",
                "reason": guard_result["reason"],
                "key": key,
                "written": False
            }
        else:
            self.memory.store(key, value)
            result = {
                "status": "success",
                "reason": f"channel_{channel_id}_allowed",
                "key": key,
                "written": True
            }

        self.receive_log.append(result)
        return result
