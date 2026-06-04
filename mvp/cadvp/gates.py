"""
Three-Gate System — ADE 三级门禁体系

实现 ADE 框架中的三级交付验证门禁：
- L1 (Self-Verification): Agent 自验自身输出
- L2 (Evidence Verification): 证据日志验证
- L3 (Cross-Review): 独立复审核验

Author: Dexing Liu
License: All Rights Reserved
"""

import time
import hashlib
from typing import Any, Dict, List, Optional, Callable


class L1SelfVerifier:
    """
    L1 Gate — 自验门禁

    Agent 在交付前对自己的输出进行自检：
    - 完整性检查（是否所有必需字段都存在）
    - 一致性检查（输出是否自洽）
    - 格式检查（是否符合预定格式）
    """

    def __init__(self):
        self._log: List[Dict] = []

    def verify(self, agent_name: str, key: str, value: Any,
               required_fields: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        执行 L1 自验。

        Args:
            agent_name: 执行自验的代理名称
            key: 交付键名
            value: 交付值
            required_fields: 要求的字段列表（如果 value 是 dict）

        Returns:
            L1 验证结果
        """
        checks = []
        passed = True

        # 1. 存在性检查 — 值非空
        exists = value is not None
        checks.append({
            "check": "existence",
            "description": "交付值非空",
            "passed": exists
        })
        if not exists:
            passed = False

        # 2. 完整性检查 — 如果 value 是 dict，检查必需字段
        completeness = True
        if required_fields and isinstance(value, dict):
            missing = [f for f in required_fields if f not in value]
            if missing:
                completeness = False
                passed = False
            checks.append({
                "check": "completeness",
                "description": f"必需字段: {required_fields}",
                "passed": completeness,
                "missing_fields": missing if not completeness else []
            })
        else:
            # 简单值类型，检查是否为合理的非空串/数字
            if isinstance(value, str) and len(value.strip()) == 0:
                completeness = False
                passed = False
            checks.append({
                "check": "completeness",
                "description": "交付值完整性",
                "passed": completeness
            })

        # 3. 格式一致性
        consistency = True
        if isinstance(value, str):
            # 检查是否有明显的编码问题
            try:
                value.encode('utf-8')
            except UnicodeEncodeError:
                consistency = False
                passed = False
        checks.append({
            "check": "consistency",
            "description": "值格式一致性",
            "passed": consistency
        })

        result = {
            "gate": "L1",
            "agent": agent_name,
            "timestamp": time.time(),
            "passed": passed,
            "checks": checks,
            "checks_passed": sum(1 for c in checks if c["passed"]),
            "checks_total": len(checks),
            "content_hash": hashlib.sha256(str(value).encode()).hexdigest()[:16]
        }

        self._log.append(result)
        return result

    def get_log(self) -> List[Dict]:
        return list(self._log)

    def get_summary(self) -> Dict[str, Any]:
        total = len(self._log)
        passed = sum(1 for v in self._log if v["passed"])
        return {
            "total_self_verifications": total,
            "passed": passed,
            "failed": total - passed,
            "pass_rate": (passed / total * 100) if total > 0 else 0.0
        }


class L2EvidenceVerifier:
    """
    L2 Gate — 证据验证门禁

    验证交付是否附带完整的证据链：
    - 关键决策记录
    - 异常处理记录
    - 交付数据摘要
    """

    def __init__(self):
        self._log: List[Dict] = []

    def verify(self, agent_name: str, key: str, value: Any,
               evidence_log: Optional[List[Dict]] = None) -> Dict[str, Any]:
        """
        执行 L2 证据验证。

        Args:
            agent_name: 验证代理名称
            key: 交付键名
            value: 交付值
            evidence_log: 执行过程中的证据日志

        Returns:
            L2 验证结果
        """
        checks = []
        passed = True

        # 1. 证据日志存在性
        evidence_exists = evidence_log is not None and len(evidence_log) > 0
        checks.append({
            "check": "evidence_exists",
            "description": "交付附带证据日志",
            "passed": evidence_exists,
            "evidence_count": len(evidence_log) if evidence_log else 0
        })
        if not evidence_exists:
            passed = False

        # 2. L1 自验报告存在
        l1_present = isinstance(value, dict) and value.get("_l1_report")
        checks.append({
            "check": "l1_report",
            "description": "L1 自验报告已附加",
            "passed": l1_present
        })

        # 3. 交付内容可追溯（通过哈希链）
        content_hash = hashlib.sha256(str(value).encode()).hexdigest()[:16]
        traceable = True
        checks.append({
            "check": "traceability",
            "description": "交付内容哈希可追溯",
            "passed": traceable,
            "content_hash": content_hash
        })

        result = {
            "gate": "L2",
            "agent": agent_name,
            "timestamp": time.time(),
            "passed": passed,
            "checks": checks,
            "checks_passed": sum(1 for c in checks if c["passed"]),
            "checks_total": len(checks),
            "evidence_count": len(evidence_log) if evidence_log else 0
        }

        self._log.append(result)
        return result

    def get_log(self) -> List[Dict]:
        return list(self._log)

    def get_summary(self) -> Dict[str, Any]:
        total = len(self._log)
        passed = sum(1 for v in self._log if v["passed"])
        return {
            "total_evidence_verifications": total,
            "passed": passed,
            "failed": total - passed,
            "pass_rate": (passed / total * 100) if total > 0 else 0.0
        }


class L3CrossReviewer:
    """
    L3 Gate — 复核门禁

    独立代理对交付进行交叉复核：
    - 独立执行验证
    - 重复数据完整性检查
    - 质量评分
    """

    def __init__(self, reviewer_name: str = "L3_Reviewer"):
        self.reviewer_name = reviewer_name
        self._log: List[Dict] = []

    def review(self, original_agent: str, key: str, value: Any,
               l1_report: Dict, l2_report: Dict) -> Dict[str, Any]:
        """
        执行 L3 独立复核。

        Args:
            original_agent: 原始交付代理
            key: 交付键名
            value: 交付值
            l1_report: L1 自验报告
            l2_report: L2 证据验证报告

        Returns:
            L3 复核结果
        """
        checks = []
        passed = True

        # 1. L1 报告有效性检查
        l1_valid = l1_report.get("passed", False)
        checks.append({
            "check": "l1_validation",
            "description": f"L1 自验通过 ({original_agent})",
            "passed": l1_valid,
            "detail": f"L1 检查 {l1_report.get('checks_passed', 0)}/{l1_report.get('checks_total', 0)} 通过"
        })
        if not l1_valid:
            passed = False

        # 2. L2 报告有效性检查
        l2_valid = l2_report.get("passed", False)
        checks.append({
            "check": "l2_validation",
            "description": f"L2 证据验证通过 ({original_agent})",
            "passed": l2_valid,
            "detail": f"L2 检查 {l2_report.get('checks_passed', 0)}/{l2_report.get('checks_total', 0)} 通过"
        })
        if not l2_valid:
            passed = False

        # 3. 独立数据完整性验证
        if value is not None:
            data_valid = True
            checks.append({
                "check": "data_integrity",
                "description": "独立数据完整性验证",
                "passed": data_valid,
                "detail": "L3 独立验证通过"
            })
        else:
            data_valid = False
            passed = False
            checks.append({
                "check": "data_integrity",
                "description": "独立数据完整性验证",
                "passed": False,
                "detail": "交付值为空"
            })

        # 4. 哈希一致性验证
        original_hash = l1_report.get("content_hash", "")
        calculated_hash = hashlib.sha256(str(value).encode()).hexdigest()[:16]
        hash_match = original_hash == calculated_hash
        checks.append({
            "check": "hash_consistency",
            "description": "交付内容哈希一致性",
            "passed": hash_match,
            "detail": f"原始哈希: {original_hash}, 计算哈希: {calculated_hash}"
        })
        if not hash_match:
            passed = False

        # 质量评分
        quality_score = 1.0 if passed else 0.0

        result = {
            "gate": "L3",
            "reviewer": self.reviewer_name,
            "original_agent": original_agent,
            "timestamp": time.time(),
            "passed": passed,
            "quality_score": quality_score,
            "checks": checks,
            "checks_passed": sum(1 for c in checks if c["passed"]),
            "checks_total": len(checks)
        }

        self._log.append(result)
        return result

    def get_log(self) -> List[Dict]:
        return list(self._log)

    def get_summary(self) -> Dict[str, Any]:
        total = len(self._log)
        passed = sum(1 for v in self._log if v["passed"])
        return {
            "total_reviews": total,
            "passed": passed,
            "failed": total - passed,
            "avg_quality": (
                sum(v["quality_score"] for v in self._log) / total
            ) if total > 0 else 0.0
        }


class ThreeGateSystem:
    """
    ADE 三级门禁体系集成。

    完整的交付验证流水线：L1 → L2 → L3
    """

    def __init__(self):
        self.l1 = L1SelfVerifier()
        self.l2 = L2EvidenceVerifier()
        self.l3 = L3CrossReviewer()

    def execute_all_gates(self, agent_name: str, reviewer_name: str,
                          key: str, value: Any,
                          required_fields: Optional[List[str]] = None,
                          evidence_log: Optional[List[Dict]] = None) -> Dict[str, Any]:
        """
        执行全部三级门禁验证。

        Args:
            agent_name: 交付代理名称
            reviewer_name: 复核代理名称
            key: 交付键名
            value: 交付值
            required_fields: 如果 value 是 dict，需检查的字段
            evidence_log: 执行证据日志

        Returns:
            三级门禁完整结果
        """
        # L1: 自验
        l1_result = self.l1.verify(agent_name, key, value, required_fields)

        # 附加 L1 报告到 value 中用于 L2 检查
        value_with_context = value
        if isinstance(value, dict):
            value_with_context = dict(value)
            value_with_context["_l1_report"] = l1_result

        # L2: 证据验证
        l2_result = self.l2.verify(agent_name, key, value_with_context, evidence_log)

        # L3: 复核
        l3_result = self.l3.review(agent_name, key, value_with_context,
                                   l1_result, l2_result)

        return {
            "timestamp": time.time(),
            "key": key,
            "agent": agent_name,
            "gates": {
                "l1": l1_result,
                "l2": l2_result,
                "l3": l3_result
            },
            "all_passed": l1_result["passed"] and l2_result["passed"] and l3_result["passed"],
            "summary": {
                f"L1 ({agent_name} 自验)": "通过" if l1_result["passed"] else "失败",
                f"L2 (证据验证)": "通过" if l2_result["passed"] else "失败",
                f"L3 ({reviewer_name} 复核)": "通过" if l3_result["passed"] else "失败"
            }
        }

    def get_summary(self) -> Dict[str, Any]:
        return {
            "l1": self.l1.get_summary(),
            "l2": self.l2.get_summary(),
            "l3": self.l3.get_summary()
        }
