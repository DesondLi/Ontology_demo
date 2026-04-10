"""
业务规则配置
将业务规则外置，便于修改和维护，体现配置化思想
"""
from typing import Dict, Any

# 业务规则配置
BUSINESS_RULES: Dict[str, Dict[str, Any]] = {
    "rule_001_contract_downgrade_block": {
        "rule_id": "rule_001_contract_downgrade_block",
        "rule_name": "合约期内禁止降档套餐",
        "description": "如果用户合约剩余时长 > 0，则禁止套餐降档",
        "enabled": True,
        "condition": {
            "intent_type": "downgrade_package",
            "contract_remaining_months_gt": 0
        },
        "action": "block",
        "error_code": "CONTRACT_001",
        "error_message": "您当前仍在合约期内，根据合约约定，合约期内无法办理套餐降档业务。",
        "priority": 10
    }
}


def get_enabled_rules() -> Dict[str, Dict[str, Any]]:
    """获取所有启用的规则"""
    return {k: v for k, v in BUSINESS_RULES.items() if v["enabled"]}
