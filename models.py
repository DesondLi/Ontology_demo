"""
Pydantic 模型定义
定义了系统中使用的核心数据结构，确保数据类型安全
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Literal


class UserProfile(BaseModel):
    """用户画像模型，存储从 OneID 获取的用户基础信息"""
    user_id: str = Field(description="用户ID")
    name: str = Field(description="用户姓名")
    phone_number: str = Field(description="手机号码")
    contract_remaining_months: int = Field(
        description="合约剩余月数，>0 表示仍在合约期内，0 表示无合约"
    )
    current_package_level: Literal["basic", "standard", "premium"] = Field(
        description="当前套餐等级"
    )


class IntentRequest(BaseModel):
    """语义解析层输出的结构化意图请求"""
    intent_type: str = Field(description="意图类型，如：downgrade_package, upgrade_package 等")
    target_package_level: Optional[Literal["basic", "standard", "premium"]] = Field(
        None,
        description="目标套餐等级（套餐变更场景使用）"
    )
    confidence: float = Field(description="语义解析置信度，0-1之间")
    original_text: str = Field(description="用户原始输入文本")
    parsed_parameters: Dict = Field(default_factory=dict, description="其他解析参数")


class ValidationResult(BaseModel):
    """逻辑校验层输出的校验结果"""
    passed: bool = Field(description="是否通过校验，True=通过，False=拦截")
    error_code: Optional[str] = Field(None, description="错误码（校验失败时填充）")
    error_message: Optional[str] = Field(None, description="错误信息（校验失败时填充）")
    rule_id: Optional[str] = Field(None, description="触发的规则ID")
    metadata: Dict = Field(default_factory=dict, description="校验过程元数据，用于日志追踪")


class GeneratedResponse(BaseModel):
    """生成回复层输出的最终回复"""
    response_text: str = Field(description="回复给用户的自然语言文本")
    intent_handled: bool = Field(description="意图是否被成功处理")
    validation_result: ValidationResult = Field(description="原始校验结果")
