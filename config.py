"""
LLM 配置文件
在这里配置你的大模型 API 信息
"""
from pydantic import BaseModel, Field
from typing import Optional, Literal


class LLMConfig(BaseModel):
    """LLM 配置"""
    # 解析模式：mock = 使用硬编码模拟，llm = 使用真实大模型
    parse_mode: Literal["mock", "llm"] = Field(
        default="mock",
        description="语义解析模式：mock=关键词匹配（不需要 API），llm=使用真实大模型解析意图"
    )

    # 生成模式：template = 使用预置模板，llm = 使用大模型生成回复（基于逻辑层结果）
    generate_mode: Literal["template", "llm"] = Field(
        default="template",
        description="回复生成模式：template=预置模板，llm=使用大模型生成自然回复"
    )

    # OpenAI 配置（使用 OpenAI 兼容接口）
    openai_api_key: str = Field(
        default="",
        description="OpenAI API Key，或兼容接口的 API Key"
    )
    openai_base_url: str = Field(
        default="https://api.openai.com/v1",
        description="API 基础 URL，可填第三方兼容代理地址"
    )
    model_name: str = Field(
        default="gpt-3.5-turbo",
        description="模型名称，例如：gpt-3.5-turbo, gpt-4, claude-3-sonnet 等（根据你的接口支持）"
    )

    # 如果你使用 Anthropic Claude，需要改这里
    # anthropic_api_key: str = ""

    @classmethod
    def from_env(cls):
        """从环境变量加载配置（可选）"""
        import os
        return cls(
            mode=os.getenv("LLM_MODE", "mock"),
            openai_api_key=os.getenv("OPENAI_API_KEY", ""),
            openai_base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
            model_name=os.getenv("LLM_MODEL", "gpt-3.5-turbo")
        )


# ========== 在这里修改你的配置 ==========
llm_config = LLMConfig(
    # 语义解析模式
    parse_mode="llm",  # mock = 关键词匹配, llm = 大模型解析

    # 回复生成模式
    generate_mode="llm",  # template = 预置模板, llm = 大模型生成回复

    # 填入你的 API Key
    openai_api_key="sk-B3dOLsy6g9wA6wLJ8177A66aEb4348Ed843847Dc1b0eCb05",

    # 如果用代理/第三方接口，修改这里
    openai_base_url="https://aihubmix.com/v1",

    # 模型名称
    model_name="qwen3.6-plus-preview-free"
)
