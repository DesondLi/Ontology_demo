"""
电信智能客服 Agent - 三层过滤法架构演示
测试入口：运行两个测试用例验证"套餐变更防冲突"场景
"""
from agent_engine import TelecomCustomerServiceAgent
from mock_services import query_user_profile_by_phone
from models import GeneratedResponse

import sys
from importlib.metadata import version, PackageNotFoundError

try:
    version('pydantic')
    print("[OK] Pydantic 已安装")
except PackageNotFoundError:
    print("[ERROR] 请先安装 pydantic: pip install pydantic")
    sys.exit(1)


def print_separator(title: str):
    """打印分隔线"""
    print("\n" + "=" * 60)
    print(f"{title}")
    print("=" * 60)


def print_response(response: GeneratedResponse):
    """格式化打印回复结果"""
    print("\n" + "-" * 60)
    print("【最终回复给用户】")
    print("-" * 60)
    print(response.response_text)
    print("-" * 60)
    print(f"校验结果: {'通过' if response.validation_result.passed else '拦截'}")
    if not response.validation_result.passed:
        print(f"错误码: {response.validation_result.error_code}")
        print(f"错误原因: {response.validation_result.error_message}")
    print("-" * 60)


def main():
    print("\n" + "=" * 60)
    print("电信智能客服 Agent 演示（三层过滤法 Neuro-symbolic 架构）")
    print("=" * 60)
    print("\n架构说明：")
    print("  第一层：语义解析层 → 自然语言转结构化意图")
    print("  第二层：逻辑校验层 → Pydantic 校验 + 业务规则拦截（核心！）")
    print("  第三层：生成回复层 → 根据校验结果生成最终回复")
    print("\n测试场景：套餐变更防冲突 → 合约期内禁止降档套餐")

    # 初始化 Agent
    agent = TelecomCustomerServiceAgent()

    # ========== 测试用例 1：张三，合约剩 6 个月，请求降档（应该被拦截） ==========
    print_separator("测试用例 1 - 拦截场景：张三（合约剩余 6 个月）请求降档套餐")
    profile = query_user_profile_by_phone("13800138001")
    if profile:
        response = agent.process("我想要把我的套餐降档", profile)
        print_response(response)

    # ========== 测试用例 2：李四，无合约，请求降档（应该通过） ==========
    print_separator("测试用例 2 - 通过场景：李四（无合约）请求降档套餐")
    profile = query_user_profile_by_phone("13900139002")
    if profile:
        response = agent.process("想办理套餐降档业务", profile)
        print_response(response)

    print("\n" + "=" * 60)
    print("演示完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()
