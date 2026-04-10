"""
电信智能客服 Agent 核心调度引擎
严格遵循三层过滤法架构：
1. 语义解析层 (Parser)：自然语言 → 结构化意图
2. 逻辑校验层 (Logic Guard)：Pydantic 校验 + 业务规则拦截
3. 生成回复层 (Generator)：根据校验结果生成最终回复
"""
from models import (
    UserProfile,
    IntentRequest,
    ValidationResult,
    GeneratedResponse
)
from rules_config import get_enabled_rules
from config import llm_config
from typing import Dict, Any, Optional
import json


class SemanticParser:
    """语义解析层：将用户自然语言转化为结构化意图
    支持两种模式：
    - mock: 硬编码关键词匹配（Demo 默认）
    - llm: 调用 OpenAI 兼容接口做意图识别
    """

    def __init__(self):
        self.config = llm_config

    def _mock_parse(self, user_input: str) -> IntentRequest:
        """Mock 解析：关键词匹配"""
        print(f"\n[第一层: 语义解析] [Mock 模式] 开始解析用户输入: {user_input}")

        # Demo Mock 逻辑：根据关键词判断意图
        intent_type = "unknown"
        target_package = None

        if "降档" in user_input or "降低套餐" in user_input or "套餐降级" in user_input:
            intent_type = "downgrade_package"
            target_package = "standard"  # Mock：假设用户想要降到标准套餐
            confidence = 0.95
        elif "升级" in user_input or "升档" in user_input or "套餐升级" in user_input:
            intent_type = "upgrade_package"
            target_package = "premium"
            confidence = 0.93
        elif "查询" in user_input or "余额" in user_input:
            intent_type = "query_balance"
            confidence = 0.90
        else:
            intent_type = "unknown"
            confidence = 0.5

        result = IntentRequest(
            intent_type=intent_type,
            target_package_level=target_package,
            confidence=confidence,
            original_text=user_input
        )

        print(f"[第一层: 语义解析] [Mock 模式] 解析完成 → 意图: {intent_type}, 置信度: {confidence}, 目标套餐: {target_package}")
        return result

    def _llm_parse(self, user_input: str) -> IntentRequest:
        """LLM 解析：调用 OpenAI 兼容接口进行结构化意图识别"""
        print(f"\n[第一层: 语义解析] [LLM 模式] 开始解析用户输入: {user_input}")

        try:
            from openai import OpenAI

            # 初始化 OpenAI 客户端
            client = OpenAI(
                api_key=self.config.openai_api_key,
                base_url=self.config.openai_base_url
            )

            # 系统提示词：要求输出 JSON 结构化意图
            system_prompt = """你是电信客服的语义解析器，请将用户的自然语言输入解析为结构化的意图。

可能的意图类型:
- downgrade_package: 套餐降档，用户想要降低套餐档次
- upgrade_package: 套餐升档，用户想要升级套餐档次
- query_balance: 查询余额/账单
- unknown: 其他不明确的意图

请严格按照 JSON 格式输出，格式如下：
{
  "intent_type": "downgrade_package",
  "target_package_level": "basic/standard/premium 或 null（如果不是套餐变更）",
  "confidence": 0.95
}

只输出 JSON，不要其他解释。"""

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input}
            ]

            response = client.chat.completions.create(
                model=self.config.model_name,
                messages=messages,
                temperature=0.0,
                response_format={"type": "json_object"}
            )

            content = response.choices[0].message.content
            data = json.loads(content)

            result = IntentRequest(
                intent_type=data.get("intent_type", "unknown"),
                target_package_level=data.get("target_package_level"),
                confidence=data.get("confidence", 0.8),
                original_text=user_input
            )

            print(f"[第一层: 语义解析] [LLM 模式] 解析完成 → 意图: {result.intent_type}, 置信度: {result.confidence}, 目标套餐: {result.target_package_level}")
            return result

        except ImportError:
            print("[第一层: 语义解析] [LLM 模式] [错误] 未安装 openai 包，请运行: pip install openai")
            print("[第一层: 语义解析] 回退到 Mock 模式")
            return self._mock_parse(user_input)
        except Exception as e:
            print(f"[第一层: 语义解析] [LLM 模式] [错误] LLM 调用失败: {str(e)}")
            print("[第一层: 语义解析] 回退到 Mock 模式")
            return self._mock_parse(user_input)

    def parse(self, user_input: str) -> IntentRequest:
        """
        解析用户自然语言输入
        根据配置选择 Mock 模式或 LLM 模式

        Args:
            user_input: 用户自然语言输入

        Returns:
            结构化意图对象
        """
        if self.config.parse_mode == "llm":
            return self._llm_parse(user_input)
        else:
            return self._mock_parse(user_input)


class LogicGuard:
    """逻辑校验层：核心层，使用业务规则进行严格拦截"""

    def __init__(self):
        self.rules = get_enabled_rules()

    def validate(
        self,
        user_profile: UserProfile,
        intent_request: IntentRequest
    ) -> ValidationResult:
        """
        执行业务规则校验

        Args:
            user_profile: 用户画像（OneID 获取）
            intent_request: 结构化意图（语义解析层输出）

        Returns:
            校验结果，passed=True 表示通过，passed=False 表示拦截
        """
        print(f"\n[第二层: 逻辑校验] 开始执行规则校验")
        print(f"[第二层: 逻辑校验] 用户: {user_profile.name}, 合约剩余: {user_profile.contract_remaining_months} 个月")
        print(f"[第二层: 逻辑校验] 当前加载规则数量: {len(self.rules)}")

        # 按优先级排序规则
        sorted_rules = sorted(
            self.rules.values(),
            key=lambda x: x.get("priority", 0),
            reverse=True
        )

        # 逐条校验规则
        for rule in sorted_rules:
            rule_id = rule["rule_id"]
            condition = rule["condition"]
            action = rule["action"]

            print(f"[第二层: 逻辑校验] 检查规则: {rule['rule_name']} ({rule_id})")

            # 检查意图类型是否匹配
            if "intent_type" in condition:
                if intent_request.intent_type != condition["intent_type"]:
                    print(f"[第二层: 逻辑校验] 规则跳过 → 意图类型不匹配")
                    continue

            # 检查合约剩余时长条件
            if "contract_remaining_months_gt" in condition:
                threshold = condition["contract_remaining_months_gt"]
                actual = user_profile.contract_remaining_months
                if actual > threshold:
                    # 条件满足，执行拦截动作
                    if action == "block":
                        print(f"[第二层: 逻辑校验] [拦截] 规则触发拦截 → 实际剩余 {actual} 个月 > 阈值 {threshold}")
                        return ValidationResult(
                            passed=False,
                            error_code=rule["error_code"],
                            error_message=rule["error_message"],
                            rule_id=rule_id,
                            metadata={
                                "actual_contract_months": actual,
                                "threshold": threshold
                            }
                        )

            print(f"[第二层: 逻辑校验] [通过] 规则不触发，继续")

        print(f"[第二层: 逻辑校验] OK 所有规则校验通过，无拦截")
        return ValidationResult(
            passed=True,
            metadata={"total_rules_checked": len(sorted_rules)}
        )


class ResponseGenerator:
    """生成回复层：根据校验结果生成最终回复
    支持两种模式：
    - template: 使用预置模板（稳定可控）
    - llm: 使用大模型生成自然回复，严格基于逻辑层决策结果，不能改变决策
    """

    def __init__(self):
        self.config = llm_config

    def _template_generate(
        self,
        user_profile: UserProfile,
        intent_request: IntentRequest,
        validation_result: ValidationResult
    ) -> GeneratedResponse:
        """预置模板生成"""
        print(f"\n[第三层: 生成回复] [模板模式] 开始生成最终回复")

        if not validation_result.passed:
            # 校验失败，使用校验层提供的错误信息生成回复
            response_text = (
                f"尊敬的{user_profile.name}先生/女士，您好！\n"
                f"抱歉，{validation_result.error_message}\n"
                f"如有疑问，请联系您的客户经理或前往营业厅咨询。"
            )
            print(f"[第三层: 生成回复] [模板模式] 生成拒绝回复，错误码: {validation_result.error_code}")
            return GeneratedResponse(
                response_text=response_text,
                intent_handled=False,
                validation_result=validation_result
            )

        # 校验通过，准许办理
        if intent_request.intent_type == "downgrade_package":
            response_text = (
                f"尊敬的{user_profile.name}先生/女士，您好！\n"
                f"已核实您当前无合约在身，我们已为您办理套餐降档业务。\n"
                f"新套餐将在下一个计费周期生效，请您留意。感谢您的使用！"
            )
            print(f"[第三层: 生成回复] [模板模式] 生成通过回复，准许办理降档")
            return GeneratedResponse(
                response_text=response_text,
                intent_handled=True,
                validation_result=validation_result
            )

        # 默认回复
        response_text = "您好，已收到您的请求，我们正在处理中。"
        return GeneratedResponse(
            response_text=response_text,
            intent_handled=True,
            validation_result=validation_result
        )

    def _llm_generate(
        self,
        user_profile: UserProfile,
        intent_request: IntentRequest,
        validation_result: ValidationResult
    ) -> GeneratedResponse:
        """LLM 生成：基于逻辑层决策结果生成自然回复
        ❗ 重要：LLM 只负责润色文本，不能改变逻辑层做出的决策
        决策（通过/拦截）已经由逻辑层确定，LLM 不能推翻
        """
        print(f"\n[第三层: 生成回复] [LLM 模式] 开始生成最终回复")

        try:
            from openai import OpenAI

            # 初始化 OpenAI 客户端
            client = OpenAI(
                api_key=self.config.openai_api_key,
                base_url=self.config.openai_base_url
            )

            # 构建 prompt：明确告诉 LLM 决策已经做出，只需要生成自然回复
            if not validation_result.passed:
                system_prompt = f"""你是一位专业礼貌的电信客服。

业务背景：
- 用户姓名：{user_profile.name}
- 用户原始请求：{intent_request.original_text}
- 业务决策结果：请求被系统拦截，不允许办理
- 拦截原因：{validation_result.error_message}

请你以电信客服的口吻，礼貌地回复用户，说明无法办理的原因。
请保持礼貌和专业，不要道歉过度。直接回复内容，不要加前缀后缀。
"""
            else:
                system_prompt = f"""你是一位专业礼貌的电信客服。

业务背景：
- 用户姓名：{user_profile.name}
- 用户原始请求：{intent_request.original_text}
- 意图类型：{intent_request.intent_type}
- 业务决策结果：请求通过，允许办理
- 已完成业务办理

请你以电信客服的口吻，友好地回复用户，告知业务已办理成功，并提醒注意事项。
请保持礼貌和专业。直接回复内容，不要加前缀后缀。
"""

            messages = [
                {"role": "system", "content": system_prompt}
            ]

            response = client.chat.completions.create(
                model=self.config.model_name,
                messages=messages,
                temperature=0.7
            )

            response_text = response.choices[0].message.content.strip()
            print(f"[第三层: 生成回复] [LLM 模式] 生成完成")

            return GeneratedResponse(
                response_text=response_text,
                intent_handled=validation_result.passed,
                validation_result=validation_result
            )

        except ImportError:
            print("[第三层: 生成回复] [LLM 模式] [错误] 未安装 openai 包，回退到模板模式")
            return self._template_generate(user_profile, intent_request, validation_result)
        except Exception as e:
            print(f"[第三层: 生成回复] [LLM 模式] [错误] LLM 调用失败: {str(e)}，回退到模板模式")
            return self._template_generate(user_profile, intent_request, validation_result)

    def generate(
        self,
        user_profile: UserProfile,
        intent_request: IntentRequest,
        validation_result: ValidationResult
    ) -> GeneratedResponse:
        """
        根据校验结果生成最终回复，强制注入上下文

        Args:
            user_profile: 用户画像
            intent_request: 结构化意图
            validation_result: 逻辑校验结果（决策已经在这里确定）

        Returns:
            最终生成的回复对象
        """
        if self.config.generate_mode == "llm":
            return self._llm_generate(user_profile, intent_request, validation_result)
        else:
            return self._template_generate(user_profile, intent_request, validation_result)


class TelecomCustomerServiceAgent:
    """电信智能客服 Agent，串联三层过滤流程"""

    def __init__(self):
        self.parser = SemanticParser()
        self.logic_guard = LogicGuard()
        self.generator = ResponseGenerator()

    def process(
        self,
        user_input: str,
        user_profile: UserProfile
    ) -> GeneratedResponse:
        """
        完整处理用户请求

        Args:
            user_input: 用户自然语言输入
            user_profile: 已查询到的用户画像

        Returns:
            最终回复给用户的结果
        """
        # 第一层：语义解析
        intent = self.parser.parse(user_input)

        # Pydantic 自动校验（类型校验）
        # 这里如果类型不对会直接抛出异常，提前拦截非法数据

        # 第二层：逻辑校验
        validation_result = self.logic_guard.validate(user_profile, intent)

        # 第三层：生成回复
        response = self.generator.generate(user_profile, intent, validation_result)

        return response
