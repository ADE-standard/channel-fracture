"""
Memory Guard — 内存隔离逻辑

实现 skip_memory 守卫机制。当 skip_memory=True 时，来自外部代理的
写入请求会被静默拦截，这正是 Channel Fracture 问题的根源。

Author: Dexing Liu
License: All Rights Reserved
"""

from typing import Any, Dict, Optional, Set


class MemoryGuard:
    """
    内存守卫：控制外部写入的准入。
    
    skip_memory=True 时，所有来自外部代理的写入都会被拦截（默认行为）。
    这是多智能体编排系统的默认安全设置，但也导致了 Channel Fracture。
    """

    def __init__(self, skip_memory: bool = True):
        """
        Args:
            skip_memory: 是否跳过外部内存写入（默认 True）
        """
        self.skip_memory = skip_memory
        self._allowed_channels: Set[str] = set()
        self._blocked_count: int = 0
        self._allowed_count: int = 0

    def check_write(self, write_record: Dict[str, Any]) -> Dict[str, Any]:
        """
        检查写入请求是否被允许。
        
        Args:
            write_record: 写入记录，包含 key, value, source 等字段
            
        Returns:
            检查结果字典
        """
        # 检查是否通过已注册通道
        channel_id = write_record.get("channel_id")
        if channel_id and channel_id in self._allowed_channels:
            self._allowed_count += 1
            return {
                "blocked": False,
                "reason": f"registered_channel:{channel_id}",
                "channel": channel_id
            }

        # 检查 skip_memory 标志
        if self.skip_memory:
            self._blocked_count += 1
            return {
                "blocked": True,
                "reason": "skip_memory=True",
                "detail": "External memory writes are blocked by skip_memory guard. "
                          "This is the Channel Fracture point.",
                "key": write_record.get("key"),
                "blocked_count": self._blocked_count
            }

        # skip_memory=False，允许写入
        self._allowed_count += 1
        return {
            "blocked": False,
            "reason": "skip_memory=False",
        }

    def register_allowed_channel(self, channel_id: str) -> None:
        """
        注册一个允许的写入通道。
        
        这是 CADVP 修复方案的核心：通过动态注册通道来绕过 skip_memory 守卫。
        
        Args:
            channel_id: 通道标识符
        """
        self._allowed_channels.add(channel_id)

    def unregister_channel(self, channel_id: str) -> bool:
        """注销一个写入通道。"""
        if channel_id in self._allowed_channels:
            self._allowed_channels.discard(channel_id)
            return True
        return False

    def get_stats(self) -> Dict[str, Any]:
        """获取守卫统计信息。"""
        return {
            "skip_memory": self.skip_memory,
            "allowed_channels": list(self._allowed_channels),
            "blocked_count": self._blocked_count,
            "allowed_count": self._allowed_count,
            "total_checks": self._blocked_count + self._allowed_count
        }

    def __repr__(self):
        return (f"MemoryGuard(skip_memory={self.skip_memory}, "
                f"channels={self._allowed_channels}, "
                f"blocked={self._blocked_count}, allowed={self._allowed_count})")
