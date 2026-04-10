# 电信智能客服 Agent - 三层过滤法 Neuro-symbolic 架构演示

严格遵循**三层过滤法（Neuro-symbolic 架构）**的电信智能客服 Demo，核心思想：**绝对不让大模型直接处理业务逻辑**，规则硬拦截，LLM 只做自然语言处理。

## 🏗️ 三层架构

| 层级 | 职责 | 说明 |
|------|------|------|
| **第一层：语义解析层** | 用户自然语言 → 结构化意图 | 支持 Mock（关键词匹配）或 LLM（大模型解析）两种模式 |
| **第二层：逻辑校验层** | Pydantic 校验 + 配置化规则拦截 | **核心！** 业务决策在这里，大模型不碰业务规则 |
| **第三层：生成回复层** | 根据校验结果生成最终回复 | 支持预置模板或 LLM 生成，决策不可推翻 |

### 核心设计原则

1. **规则外置**：业务规则配置化，不用改代码就能增删改规则
2. **强制校验**：Pydantic 做严格类型校验，格式错提前拦截
3. **责任分离**：LLM 只处理自然语言，业务逻辑由规则控制，不会 "幻觉" 出问题
4. **可追溯**：每一步处理都有日志，问题好排查

## 🎯 演示场景：套餐变更防冲突

**规则**：如果用户合约剩余时长 > 0 → 禁止降档套餐。

| 测试用例 | 结果 |
|----------|------|
| 张三，合约剩 6 个月，申请降档 | ❌ 硬拦截 |
| 李四，无合约，申请降档 | ✅ 准许办理 |

## 📁 项目结构

```
.
├── models.py          # Pydantic 数据模型定义
├── rules_config.py   # 业务规则配置（外置）
├── mock_services.py  # Mock OneID 用户查询服务
├── agent_engine.py   # 核心调度引擎，串联三层
├── config.py         # LLM API 配置
├── main.py           # 命令行测试入口
├── app.py            # Streamlit 交互式前端
└── requirements.txt  # 依赖列表
```

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置 LLM（可选）

编辑 `config.py`：

```python
llm_config = LLMConfig(
    parse_mode="llm",      # 语义解析：mock / llm
    generate_mode="llm",   # 回复生成：template / llm
    openai_api_key="your-api-key",
    openai_base_url="https://api.openai.com/v1",  # 可填代理地址
    model_name="gpt-3.5-turbo"
)
```

### 3. 运行

命令行演示：
```bash
python main.py
```

Web 交互式演示：
```bash
streamlit run app.py
```

## ⚙️ 配置说明

在 `config.py` 中可独立配置两个阶段：

| 阶段 | 选项 | 说明 |
|------|------|------|
| `parse_mode` | `mock` | 关键词匹配，不需要 API Key，适合演示 |
| `parse_mode` | `llm` | 大模型解析意图，需要 API Key |
| `generate_mode` | `template` | 预置模板回复，稳定可控 |
| `generate_mode` | `llm` | 大模型生成自然回复，决策不变 |

**重要**：无论开不开 LLM，**业务规则拦截永远由第二层逻辑校验层控制**，LLM 无法推翻规则。

## 🖼️ 界面预览

Streamlit 前端采用现代科技极简风格：
- 深色侧边栏配置区
- 分层卡片展示处理流程
- 清晰的视觉层次，每一步结果一目了然

## 📝 技术栈

- Python 3.11+
- Pydantic v2 - 数据校验
- OpenAI SDK - LLM 调用（兼容 OpenAI 格式接口）
- Streamlit - 交互式前端

## 🔄 扩展新规则

在 `rules_config.py` 的 `BUSINESS_RULES` 添加新规则即可：

```python
"rule_xxx_new_rule": {
    "rule_id": "rule_xxx_new_rule",
    "rule_name": "规则名称",
    "description": "规则描述",
    "enabled": True,
    "condition": {
        "intent_type": "target_intent",
        # 其他条件...
    },
    "action": "block",
    "error_code": "ERR_XXX",
    "error_message": "错误信息",
    "priority": 10
}
```

不需要修改核心引擎，配置化扩展！

## 📄 许可证

MIT
