"""
Persistent Memory — 带 skip_memory=True 守卫的持久化内存

模拟多智能体系统中的持久化内存存储。当 skip_memory=True 时，
外部写入请求会被静默忽略，这是 Channel Fracture 的核心机制。

Author: Dexing Liu
License: All Rights Reserved
"""

import json
import time
from typing import Any, Dict, Optional


class PersistentMemory:
    """
    持久化内存存储。
    
    模拟 Agent 的持久化内存层，支持键值存储和操作日志。
    """

    def __init__(self, agent_name: str = "agent"):
        self.agent_name = agent_name
        self._store: Dict[str, Any] = {}
        self._history: list = []

    def store(self, key: str, value: Any, metadata: Optional[Dict] = None) -> bool:
        """
        存储键值对到持久化内存。
        
        Args:
            key: 存储键名
            value: 存储值
            metadata: 可选的元数据
            
        Returns:
            是否存储成功
        """
        old_value = self._store.get(key)
        self._store[key] = value

        record = {
            "timestamp": time.time(),
            "operation": "store",
            "key": key,
            "old_value": old_value,
            "new_value": value,
            "metadata": metadata or {}
        }
        self._history.append(record)
        return True

    def get(self, key: str, default: Any = None) -> Any:
        """获取指定键的值。"""
        return self._store.get(key, default)

    def get_all(self) -> Dict[str, Any]:
        """获取所有内存内容的快照。"""
        return dict(self._store)

    def has(self, key: str) -> bool:
        """检查键是否存在。"""
        return key in self._store

    def delete(self, key: str) -> bool:
        """删除指定键。"""
        if key in self._store:
            old_value = self._store.pop(key)
            self._history.append({
                "timestamp": time.time(),
                "operation": "delete",
                "key": key,
                "old_value": old_value
            })
            return True
        return False

    def get_history(self, limit: int = 10) -> list:
        """获取最近的操作历史。"""
        return self._history[-limit:]

    def clear(self):
        """清空所有内存。"""
        self._store.clear()
        self._history.append({
            "timestamp": time.time(),
            "operation": "clear"
        })

    def __len__(self):
        return len(self._store)

    def __repr__(self):
        return f"PersistentMemory(agent={self.agent_name}, keys={list(self._store.keys())})"
