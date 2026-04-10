"""
模拟底层主数据服务
模拟根据手机号查询 OneID 用户画像和合约状态的功能
"""
from models import UserProfile
from typing import Optional


# 模拟数据库：存储测试用户数据
MOCK_USER_DB = {
    "13800138001": {
        "user_id": "zhangsan_001",
        "name": "张三",
        "phone_number": "13800138001",
        "contract_remaining_months": 6,
        "current_package_level": "premium"
    },
    "13900139002": {
        "user_id": "lisi_002",
        "name": "李四",
        "phone_number": "13900139002",
        "contract_remaining_months": 0,
        "current_package_level": "premium"
    }
}


def query_user_profile_by_phone(phone_number: str) -> Optional[UserProfile]:
    """
    模拟调用 CRM/OneID 主数据系统，根据手机号查询用户画像

    Args:
        phone_number: 用户手机号码

    Returns:
        UserProfile 用户画像对象，如果未找到用户返回 None
    """
    print(f"[Mock 服务] 调用 OneID 查询用户信息，手机号: {phone_number}")

    user_data = MOCK_USER_DB.get(phone_number)
    if not user_data:
        print(f"[Mock 服务] 未找到该用户")
        return None

    print(f"[Mock 服务] 查询成功，用户: {user_data['name']}, 合约剩余: {user_data['contract_remaining_months']} 个月")
    return UserProfile(**user_data)
