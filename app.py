"""
电信智能客服 Agent - Streamlit 前端演示
三层过滤法（Neuro-symbolic 架构）可视化演示
"""
import streamlit as st
from agent_engine import TelecomCustomerServiceAgent
from mock_services import query_user_profile_by_phone
from config import llm_config

# 页面配置
st.set_page_config(
    page_title="电信智能客服 Agent",
    page_icon="▷",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义 CSS - 现代科技极简风格
st.markdown("""
<style>
/* 导入字体 */
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@300;400;500;700&family=Poppins:wght@300;400;500;600;700&display=swap');

/* 全局样式重置 */
* {
    font-family: 'Poppins', 'Noto Sans SC', -apple-system, BlinkMacSystemFont, sans-serif;
}

/* 主背景渐变 */
.stApp {
    background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
}

/* 侧边栏美化 */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
    padding: 2rem 1rem;
}

/* Streamlit 默认文本在侧边栏 */
section[data-testid="stSidebar"] .stMarkdown p,
section[data-testid="stSidebar"] .stMarkdown li,
section[data-testid="stSidebar"] .css-16idsys p {
    color: #ffffff !important;
    opacity: 1;
}

section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {
    color: #ffffff !important;
    font-weight: 600;
    letter-spacing: 0.5px;
}

section[data-testid="stSidebar"] label {
    color: #e2e8f0 !important;
    font-weight: 500;
}

/* Radio 选项文字 */
section[data-testid="stSidebar"] .stRadio label {
    color: #f1f5f9 !important;
}

/* 所有输入组件文字 */
section[data-testid="stSidebar"] .st-bk {
    background-color: rgba(255, 255, 255, 0.1);
}

section[data-testid="stSidebar"] .st-bk:hover {
    background-color: rgba(255, 255, 255, 0.15);
}

/* 单选框按钮文字 */
section[data-testid="stSidebar"] .st-cm {
    color: #ffffff !important;
}

/* 滑块等其他控件 */
section[data-testid="stSidebar"] .css-1nhtac2 {
    color: #ffffff !important;
}

/* Streamlit 组件文字覆盖 */
section[data-testid="stSidebar"] span {
    color: #f1f5f9 !important;
}

section[data-testid="stSidebar"] div {
    color: #f1f5f9;
}

/* 帮助文字 */
section[data-testid="stSidebar"] .stTooltipIcon {
    color: #cbd5e1;
}

/* 勾选框 */
section[data-testid="stSidebar"] input[type="radio"] + span {
    color: #f1f5f9 !important;
}

/* 卡片容器 */
.arch-card {
    background: white;
    border-radius: 16px;
    padding: 1.5rem;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
    margin-bottom: 1.5rem;
    border-left: 4px solid #0ea5e9;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.arch-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.08), 0 4px 6px -2px rgba(0, 0, 0, 0.04);
}

/* 层级卡片不同颜色 */
.card-layer-0 {
    border-left-color: #64748b;
}
.card-layer-1 {
    border-left-color: #0ea5e9;
}
.card-layer-2 {
    border-left-color: #f59e0b;
}
.card-layer-3 {
    border-left-color: #10b981;
}

/* 状态徽章 */
.badge {
    display: inline-block;
    padding: 0.25rem 0.75rem;
    border-radius: 9999px;
    font-size: 0.875rem;
    font-weight: 500;
}

.badge-mock {
    background: #e2e8f0;
    color: #334155;
}

.badge-llm {
    background: #dbeafe;
    color: #1d4ed8;
}

.badge-passed {
    background: #d1fae5;
    color: #065f46;
}

.badge-blocked {
    background: #fee2e2;
    color: #991b1b;
}

/* 标题美化 */
.main-title {
    font-size: 2.5rem;
    font-weight: 700;
    background: linear-gradient(135deg, #0f172a 0%, #0ea5e9 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 0.5rem;
    letter-spacing: -0.5px;
}

.subtitle {
    font-size: 1.1rem;
    color: #64748b;
    font-weight: 400;
    margin-bottom: 2rem;
}

/* 流程箭头 */
.flow-arrow {
    text-align: center;
    font-size: 2rem;
    color: #0ea5e9;
    margin: 0.5rem 0;
    animation: bounce 2s infinite;
}

@keyframes bounce {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(5px); }
}

/* 最终回复框 */
.final-response {
    background: linear-gradient(135deg, #f0fdfa 0%, #ecfeff 100%);
    border: 1px solid #a5f3fc;
    border-radius: 12px;
    padding: 1.5rem;
    color: #083344;
    line-height: 1.7;
    font-size: 1rem;
}

/* 按钮美化 */
.stButton > button {
    background: linear-gradient(135deg, #0ea5e9 0%, #06b6d4 100%);
    border: none;
    border-radius: 12px;
    padding: 0.75rem 2rem;
    font-weight: 600;
    transition: all 0.3s ease;
    box-shadow: 0 4px 14px 0 rgba(14, 165, 233, 0.35);
}

.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px 0 rgba(14, 165, 233, 0.45);
}

/* 输入框美化 */
.stTextInput > div > div > input {
    border-radius: 12px;
    border: 1px solid #e2e8f0;
    padding: 0.75rem 1rem;
    transition: border-color 0.2s ease;
}

.stTextInput > div > div > input:focus {
    border-color: #0ea5e9;
    box-shadow: 0 0 0 3px rgba(14, 165, 233, 0.1);
}

.stTextArea > div > div > textarea {
    border-radius: 12px;
    border: 1px solid #e2e8f0;
    transition: border-color 0.2s ease;
}

.stTextArea > div > div > textarea:focus {
    border-color: #0ea5e9;
    box-shadow: 0 0 0 3px rgba(14, 165, 233, 0.1);
}

/* 架构流程图 */
.architecture-diagram {
    background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
    color: white;
    padding: 1.5rem;
    border-radius: 12px;
    margin-bottom: 1rem;
}

.architecture-step {
    display: flex;
    align-items: center;
    margin-bottom: 1rem;
    padding: 0.75rem;
    border-radius: 8px;
    background: rgba(255, 255, 255, 0.05);
}

.step-number {
    width: 32px;
    height: 32px;
    border-radius: 50%;
    background: #0ea5e9;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 700;
    margin-right: 1rem;
}

.step-desc {
    flex: 1;
}

.step-desc h4 {
    margin: 0;
    font-size: 0.95rem;
}

.step-desc p {
    margin: 0.25rem 0 0 0;
    font-size: 0.8rem;
    color: #94a3b8;
}

/* 测试账号卡片 */
.test-account {
    background: rgba(14, 165, 233, 0.1);
    border: 1px solid rgba(14, 165, 233, 0.2);
    border-radius: 8px;
    padding: 0.75rem;
    margin-bottom: 0.5rem;
}

.test-account-name {
    font-weight: 600;
    color: #0ea5e9;
}

.test-account-desc {
    font-size: 0.8rem;
    color: #64748b;
}

/* Radio 按钮样式覆盖 */
.stRadio > div {
    background: transparent;
}

.stRadio > div > label {
    font-weight: 500;
}

/* Divider 在深色侧边栏 */
section[data-testid="stSidebar"] .stDivider {
    border-color: rgba(148, 163, 184, 0.2);
}

/* 状态信息条 */
.status-bar {
    display: flex;
    gap: 1rem;
    padding: 1rem;
    background: #f8fafc;
    border-radius: 12px;
    margin-bottom: 1rem;
}

.status-item {
    flex: 1;
    text-align: center;
}

.status-label {
    font-size: 0.75rem;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.status-value {
    font-size: 1rem;
    font-weight: 600;
    margin-top: 0.25rem;
}
</style>
""", unsafe_allow_html=True)

# ========== 侧边栏 ==========
with st.sidebar:
    st.markdown('<h2 style="color: white; margin-top: 0;">⚙️ 运行配置</h2>', unsafe_allow_html=True)

    # 语义解析模式
    st.markdown('<p style="color: #cbd5e1; margin-bottom: 0.5rem;"><strong>语义解析模式</strong></p>', unsafe_allow_html=True)
    parse_mode_option = st.radio(
        "",
        options=["mock", "llm"],
        index=0 if llm_config.parse_mode == "mock" else 1,
        format_func=lambda x: "🔧 Mock - 关键词匹配" if x == "mock" else "🤖 LLM - 大模型解析",
        label_visibility="collapsed"
    )
    if parse_mode_option != llm_config.parse_mode:
        llm_config.parse_mode = parse_mode_option

    st.divider()

    # 回复生成模式
    st.markdown('<p style="color: #cbd5e1; margin-bottom: 0.5rem;"><strong>回复生成模式</strong></p>', unsafe_allow_html=True)
    generate_mode_option = st.radio(
        "",
        options=["template", "llm"],
        index=0 if llm_config.generate_mode == "template" else 1,
        format_func=lambda x: "📄 Template - 预置模板" if x == "template" else "🤖 LLM - AI 生成",
        label_visibility="collapsed"
    )
    if generate_mode_option != llm_config.generate_mode:
        llm_config.generate_mode = generate_mode_option

    st.divider()

    # 当前状态
    st.markdown('<p style="color: #cbd5e1;"><strong>当前状态</strong></p>', unsafe_allow_html=True)

    parse_badge = f'<span class="badge {"badge-mock" if llm_config.parse_mode == "mock" else "badge-llm"}">{llm_config.parse_mode.upper()}</span>'
    generate_badge = f'<span class="badge {"badge-mock" if llm_config.generate_mode == "template" else "badge-llm"}">{llm_config.generate_mode.upper()}</span>'
    st.markdown(f"**解析**: {parse_badge}<br>**生成**: {generate_badge}", unsafe_allow_html=True)

    # LLM 配置信息
    if parse_mode_option == "llm" or generate_mode_option == "llm":
        st.divider()
        st.markdown('<p style="color: #cbd5e1;"><strong>LLM 配置</strong></p>', unsafe_allow_html=True)
        st.markdown(f'<p style="color: #cbd5e1; font-size: 0.85rem;"><strong>Endpoint:</strong><br><code style="background: rgba(255,255,255,0.1); padding: 2px 6px; border-radius: 4px; color: #e2e8f0;">{llm_config.openai_base_url}</code></p>', unsafe_allow_html=True)
        st.markdown(f'<p style="color: #cbd5e1; font-size: 0.85rem;"><strong>Model:</strong><br><code style="background: rgba(255,255,255,0.1); padding: 2px 6px; border-radius: 4px; color: #e2e8f0;">{llm_config.model_name}</code></p>', unsafe_allow_html=True)
        if not llm_config.openai_api_key:
            st.markdown('<p style="color: #fca5a5; font-size: 0.85rem;">⚠️ API Key 未配置</p>', unsafe_allow_html=True)
        else:
            st.markdown('<p style="color: #86efac; font-size: 0.85rem;">✅ API Key 已配置</p>', unsafe_allow_html=True)

    st.divider()

    # 架构说明
    st.markdown('<h3 style="color: #f1f5f9;">🏗️ 三层架构</h3>', unsafe_allow_html=True)
    st.markdown('<div class="architecture-diagram">', unsafe_allow_html=True)

    st.markdown('''
<div class="architecture-step">
  <div class="step-number">1</div>
  <div class="step-desc">
    <h4>语义解析层</h4>
    <p>自然语言 → 结构化意图</p>
  </div>
</div>

<div class="architecture-step">
  <div class="step-number" style="background: #f59e0b;">2</div>
  <div class="step-desc">
    <h4>逻辑校验层 ⚠️ 核心</h4>
    <p>规则拦截，大模型不碰业务逻辑</p>
  </div>
</div>

<div class="architecture-step">
  <div class="step-number" style="background: #10b981;">3</div>
  <div class="step-desc">
    <h4>生成回复层</h4>
    <p>根据校验结果生成回复</p>
  </div>
</div>
''', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    st.divider()

    # 测试账号
    st.markdown('<h3 style="color: #f1f5f9;">📋 测试账号</h3>', unsafe_allow_html=True)

    st.markdown('''
<div class="test-account">
  <div class="test-account-name">张三 · 13800138001</div>
  <div class="test-account-desc">合约剩余 6 个月 → 应该被拦截</div>
</div>

<div class="test-account">
  <div class="test-account-name">李四 · 13900139002</div>
  <div class="test-account-desc">无合约 → 应该通过</div>
</div>
''', unsafe_allow_html=True)

# ========== 主内容区 ==========
# 重新初始化 Agent（因为配置可能被修改）
agent = TelecomCustomerServiceAgent()

# 标题
st.markdown('<h1 class="main-title">Telecom AI Customer Service</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">三层过滤法 · Neuro-symbolic 架构 · 电信智能客服 Agent 演示</p>', unsafe_allow_html=True)

# 状态条
st.markdown(f'''
<div class="status-bar">
  <div class="status-item">
    <div class="status-label">语义解析</div>
    <div class="status-value">{llm_config.parse_mode.upper()}</div>
  </div>
  <div class="status-item">
    <div class="status-label">回复生成</div>
    <div class="status-value">{llm_config.generate_mode.upper()}</div>
  </div>
  <div class="status-item">
    <div class="status-label">核心规则</div>
    <div class="status-value">合约禁降档</div>
  </div>
</div>
''', unsafe_allow_html=True)

# 主布局：输入区 + 处理流程区
col_input, col_process = st.columns([1, 1.5])

with col_input:
    st.markdown('<div class="arch-card card-layer-0"><h3 style="margin-top: 0;">用户输入</h3>', unsafe_allow_html=True)

    phone_number = st.text_input(
        "📞 手机号码",
        placeholder="例如：13800138001",
        help="使用测试账号体验不同场景"
    )

    user_input = st.text_area(
        "💬 用户需求",
        placeholder="例如：我想要办理套餐降档",
        height=100
    )

    submit_button = st.button("▶️ 开始处理", use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # 设计说明卡片
    st.markdown('''
<div class="arch-card card-layer-0">
  <h4 style="margin-top: 0;">💡 设计要点</h4>
  <ul style="margin-bottom: 0; padding-left: 1rem;">
    <li><strong>业务规则外置配置</strong>，易于维护</li>
    <li>Pydantic 严格类型校验，提前拦截</li>
    <li>逻辑层强制拦截，大模型不做业务决策</li>
    <li>完整日志可追溯，每一步清晰可见</li>
  </ul>
</div>
''', unsafe_allow_html=True)

with col_process:
    if submit_button:
        if not phone_number or not user_input:
            st.warning("⚠️ 请输入手机号码和用户需求")
        else:
            # ========== 步骤 0：查询用户画像 ==========
            st.markdown('<div class="arch-card card-layer-0"><h4 style="margin-top: 0;">🔍 Step 0 - 查询用户画像（OneID）</h4>', unsafe_allow_html=True)

            profile = query_user_profile_by_phone(phone_number)

            if profile is None:
                st.error("❌ 未找到该用户，请检查手机号码")
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                # 用户信息卡片
                # 用户信息网格
                st.markdown("""
                <style>
                .user-info-grid {
                    display: grid;
                    grid-template-columns: repeat(4, 1fr);
                    gap: 1rem;
                    margin-bottom: 1rem;
                }
                .info-card {
                    background: #f8fafc;
                    padding: 0.75rem;
                    border-radius: 8px;
                    text-align: center;
                }
                .info-label {
                    font-size: 0.75rem;
                    color: #64748b;
                    text-transform: uppercase;
                    letter-spacing: 0.5px;
                    margin-bottom: 0.25rem;
                }
                .info-value {
                    font-size: 0.95rem;
                    font-weight: 600;
                    color: #0f172a;
                }
                </style>
                <div class="user-info-grid">
                    <div class="info-card">
                        <div class="info-label">姓名</div>
                        <div class="info-value">""" + profile.name + """</div>
                    </div>
                    <div class="info-card">
                        <div class="info-label">手机号</div>
                        <div class="info-value">""" + profile.phone_number + """</div>
                    </div>
                    <div class="info-card">
                        <div class="info-label">合约剩余</div>
                        <div class="info-value">""" + str(profile.contract_remaining_months) + """ 月</div>
                    </div>
                    <div class="info-card">
                        <div class="info-label">当前套餐</div>
                        <div class="info-value">""" + profile.current_package_level + """</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                with st.expander("查看完整 JSON", expanded=False):
                    st.json({
                        "user_id": profile.user_id,
                        "name": profile.name,
                        "phone_number": profile.phone_number,
                        "contract_remaining_months": profile.contract_remaining_months,
                        "current_package_level": profile.current_package_level
                    })

                st.markdown('</div>', unsafe_allow_html=True)

                st.markdown('<div class="flow-arrow">↓</div>', unsafe_allow_html=True)

                # ========== 第一层：语义解析 ==========
                st.markdown('<div class="arch-card card-layer-1"><h4 style="margin-top: 0;">🧩 Layer 1 - 语义解析</h4>', unsafe_allow_html=True)

                intent = agent.parser.parse(user_input)

                # 意图信息网格
                st.markdown("""
                <style>
                .intent-grid {
                    display: grid;
                    grid-template-columns: repeat(3, 1fr);
                    gap: 0.75rem;
                    margin-bottom: 1rem;
                }
                .intent-card {
                    background: #f1f5f9;
                    padding: 0.6rem;
                    border-radius: 8px;
                    text-align: center;
                }
                .intent-label {
                    font-size: 0.7rem;
                    color: #64748b;
                    text-transform: uppercase;
                    letter-spacing: 0.5px;
                    margin-bottom: 0.25rem;
                }
                .intent-value {
                    font-size: 0.9rem;
                    font-weight: 600;
                    color: #0f172a;
                }
                </style>
                <div class="intent-grid">
                    <div class="intent-card">
                        <div class="intent-label">意图类型</div>
                        <div class="intent-value">""" + intent.intent_type + """</div>
                    </div>
                    <div class="intent-card">
                        <div class="intent-label">目标套餐</div>
                        <div class="intent-value">""" + (intent.target_package_level or "-") + """</div>
                    </div>
                    <div class="intent-card">
                        <div class="intent-label">置信度</div>
                        <div class="intent-value">""" + f"{intent.confidence:.2f}" + """</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                with st.expander("查看完整 JSON", expanded=False):
                    st.json({
                        "intent_type": intent.intent_type,
                        "target_package_level": intent.target_package_level,
                        "confidence": intent.confidence,
                        "original_text": intent.original_text
                    })

                st.markdown('</div>', unsafe_allow_html=True)

                st.markdown('<div class="flow-arrow">↓</div>', unsafe_allow_html=True)

                # ========== 第二层：逻辑校验 ==========
                st.markdown('<div class="arch-card card-layer-2"><h4 style="margin-top: 0;">🛡️ Layer 2 - 逻辑校验 (核心)</h4>', unsafe_allow_html=True)

                validation_result = agent.logic_guard.validate(profile, intent)

                if validation_result.passed:
                    st.success("✅ 校验通过，可以办理")
                    badge = '<span class="badge badge-passed">PASSED</span>'
                else:
                    st.error("❌ 校验拦截，禁止办理")
                    badge = '<span class="badge badge-blocked">REJECTED</span>'

                st.markdown(f"**校验结果**: {badge}", unsafe_allow_html=True)

                if not validation_result.passed:
                    st.markdown("---")
                    col_err1, col_err2 = st.columns(2)
                    with col_err1:
                        st.markdown(f"**错误码:** `{validation_result.error_code}`")
                    with col_err2:
                        st.markdown(f"**规则ID:** `{validation_result.rule_id}`")
                    st.error(f"**原因:** {validation_result.error_message}")

                with st.expander("查看元数据", expanded=False):
                    st.json(validation_result.metadata)

                st.markdown('</div>', unsafe_allow_html=True)

                st.markdown('<div class="flow-arrow">↓</div>', unsafe_allow_html=True)

                # ========== 第三层：生成回复 ==========
                st.markdown('<div class="arch-card card-layer-3"><h4 style="margin-top: 0;">💬 Layer 3 - 生成回复</h4>', unsafe_allow_html=True)

                response = agent.generator.generate(profile, intent, validation_result)

                st.markdown(f'<div class="final-response">{response.response_text}</div>', unsafe_allow_html=True)

                st.markdown("---")
                col_r1, col_r2 = st.columns(2)
                with col_r1:
                    st.markdown(f"**意图处理**: {'✅ 已处理' if response.intent_handled else '❌ 未处理'}")
                with col_r2:
                    final_badge = 'badge-passed' if response.validation_result.passed else 'badge-blocked'
                    final_text = '通过' if response.validation_result.passed else '拦截'
                    st.markdown(f"**校验结果**: <span class=\"badge {final_badge}\">{final_text}</span>", unsafe_allow_html=True)

                st.markdown('</div>', unsafe_allow_html=True)

    else:
        # 欢迎卡片
        st.markdown('''
<div class="arch-card card-layer-0" style="text-align: center; padding: 3rem 1rem;">
  <div style="font-size: 4rem; margin-bottom: 1rem;">▷</div>
  <h3>三层过滤法 Neuro-symbolic 架构演示</h3>
  <p style="color: #64748b;">请在左侧输入用户信息，点击「开始处理」查看完整流程</p>
  <p style="color: #94a3b8; font-size: 0.9rem;">核心原则：绝对不让大模型直接处理业务逻辑，规则硬拦截</p>
</div>

<div class="arch-card card-layer-0">
  <h4>🎯 测试场景：套餐变更防冲突</h4>
  <blockquote style="border-left: 4px solid #0ea5e9; padding-left: 1rem; margin: 0; color: #475569; background: #f8fafc;">
  <strong>规则</strong>：如果用户的 OneID 画像中显示「合约剩余时长 > 0」，则<strong>绝对禁止</strong>降档套餐。
  </blockquote>
</div>
''', unsafe_allow_html=True)
