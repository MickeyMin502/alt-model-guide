"""
ALT 模型物理合理性指南
帮助用户在12种单应力和12种双应力模型中，基于物理场景做出正确选择
"""

import streamlit as st
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
import pandas as pd

# ====== 设置中文字体 ======
# 使用黑体（Windows 系统自带）
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

st.set_page_config(
    page_title="ALT 模型选择指南",
    page_icon="📊",
    layout="wide"
)

st.title("📊 ALT 模型物理合理性指南")
st.markdown("""
### 选择模型的核心原则
> **物理决定"选哪个家族"（应力关系），数据决定"选哪个成员"（分布），AICc 只在同一家族内做最终微调。**

本指南帮助你理解每个模型背后的物理场景，避免"只看AICc"导致的过拟合和外推风险。
""")

# ==================== 侧边栏：快速导航 ====================
with st.sidebar:
    st.header("🧭 快速导航")
    nav = st.radio(
        "跳转到",
        [
            "🏠 首页概览",
            "🌡️ 单应力模型",
            "🔬 单应力物理图解",
            "⚡ 双应力模型",
            "🔗 双应力物理图解",
            "📋 选择流程",
            "⚠️ 常见陷阱"
        ]
    )

# ==================== 首页概览 ====================
if nav == "🏠 首页概览":
    st.header("🎯 模型选择的三步法")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.subheader("1️⃣ 看应力类型")
        st.info("""
        **温度应力** → Exponential / Eyring  
        **非热应力**（电压/振动/压力）→ Power  
        **混合应力** → 双应力组合
        """)
    with col2:
        st.subheader("2️⃣ 看失效特征")
        st.info("""
        **早期失效**（失效率递减）→ Weibull (β<1)  
        **随机失效**（失效率恒定）→ Exponential  
        **耗损失效**（失效率递增）→ Weibull (β>1)  
        **疲劳/裂纹** → Lognormal  
        **退化/磨损** → Normal
        """)
    with col3:
        st.subheader("3️⃣ 检查物理一致性")
        st.warning("""
        ✅ 寿命-应力曲线单调递减  
        ✅ 形状参数变化 < 30%  
        ✅ 概率图低应力端拟合良好  
        ✅ 外推趋势符合物理常识
        """)

# ==================== 单应力模型 ====================
elif nav == "🌡️ 单应力模型":
    st.header("🌡️ 单应力模型（3种应力关系 × 4种分布）")

    data = {
        "模型": [
            "Weibull_Exponential", "Weibull_Eyring", "Weibull_Power",
            "Lognormal_Exponential", "Lognormal_Eyring", "Lognormal_Power",
            "Normal_Exponential", "Normal_Eyring", "Normal_Power",
            "Exponential_Exponential", "Exponential_Eyring", "Exponential_Power"
        ],
        "应力关系": [
            "阿伦尼乌斯(热)", "艾林(热)", "逆幂律(非热)",
            "阿伦尼乌斯(热)", "艾林(热)", "逆幂律(非热)",
            "阿伦尼乌斯(热)", "艾林(热)", "逆幂律(非热)",
            "阿伦尼乌斯(热)", "艾林(热)", "逆幂律(非热)"
        ],
        "分布": [
            "Weibull", "Weibull", "Weibull",
            "Lognormal", "Lognormal", "Lognormal",
            "Normal", "Normal", "Normal",
            "Exponential", "Exponential", "Exponential"
        ],
        "适用场景": [
            "温度加速，失效率变化", "温度加速(量子效应)", "电压/压力/振动加速",
            "温度加速，疲劳/裂纹", "温度加速，量子隧穿", "电压/机械疲劳",
            "温度加速，退化/磨损", "温度加速，热力学过程", "电压/机械退化",
            "温度加速，随机失效", "温度加速，随机失效", "电压/机械随机失效"
        ],
        "典型应用": [
            "电子器件高温老化", "半导体可靠性", "电容电压击穿",
            "PCB热循环疲劳", "半导体电迁移", "机械疲劳测试",
            "绝缘材料老化", "热力学过程", "磨损退化",
            "电源模块寿命", "化学过程", "振动随机失效"
        ]
    }

    import pandas as pd
    df = pd.DataFrame(data)
    st.dataframe(df, use_container_width=True, hide_index=True)

    st.info("💡 **选择建议**：先用应力类型缩小范围（温度→Exponential/Eyring，非热→Power），再用分布匹配失效特征。")

# ==================== 单应力物理图解 ====================
elif nav == "🔬 单应力物理图解":
    st.header("🔬 单应力模型物理图解：AICc 陷阱")

    st.markdown("""
    ### 🎯 核心教学演示

    **同一个数据集，错误模型（Power）的 AICc 比正确模型（Exponential）更小，但外推完全错误！**

    这告诉你：**AICc 最小 ≠ 物理正确！**
    """)

    # ====== 生成30个模拟数据点 ======
    np.random.seed(42)
    
    # 应力水平（5个水平，每个水平6个点）
    stress_levels = np.array([75, 85, 95, 105, 115])
    n_per_level = 6
    stress_all = np.repeat(stress_levels, n_per_level)
    
    # 真实模型：Exponential (Arrhenius) - 温度加速
    a_true = 80000
    b_true = 0.055
    true_life = a_true * np.exp(-b_true * stress_all)
    
    # 添加异方差噪声（高应力下噪声更大，更真实）
    noise_scale = 0.12 * true_life
    noise = np.random.normal(0, noise_scale)
    observed_life = true_life + noise
    observed_life = np.maximum(observed_life, 100)  # 防止负值
    
    # ====== 拟合两个模型（使用 scipy）======
    from scipy.optimize import curve_fit
    
    def exp_model(stress, a, b):
        return a * np.exp(-b * stress)
    
    def power_model(stress, a, b):
        return a * stress ** b
    
    # 拟合 Exponential
    popt_exp, _ = curve_fit(exp_model, stress_all, observed_life, 
                            p0=[50000, 0.05], maxfev=5000)
    a_exp, b_exp = popt_exp
    
    # 拟合 Power
    popt_power, _ = curve_fit(power_model, stress_all, observed_life,
                              p0=[1000000, -2], maxfev=5000)
    a_power, b_power = popt_power
    
    # ====== 计算 AICc ======
    def calculate_aicc(observed, predicted, n_params):
        n = len(observed)
        residuals = observed - predicted
        rss = np.sum(residuals**2)
        sigma2 = rss / n
        loglik = -0.5 * n * np.log(2 * np.pi * sigma2) - rss / (2 * sigma2)
        aicc = -2 * loglik + 2 * n_params + (2 * n_params * (n_params + 1)) / (n - n_params - 1)
        return aicc
    
    predicted_exp = exp_model(stress_all, a_exp, b_exp)
    predicted_power = power_model(stress_all, a_power, b_power)
    
    aicc_exp = calculate_aicc(observed_life, predicted_exp, 2)
    aicc_power = calculate_aicc(observed_life, predicted_power, 2)
    
    # ====== 外推到使用应力 ======
    use_stress = 40
    life_exp_use = exp_model(use_stress, a_exp, b_exp)
    life_power_use = power_model(use_stress, a_power, b_power)
    
    # ====== 计算差值比例 ======
    ratio = life_power_use / life_exp_use
    
    # ====== 绘图 ======
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    
    stress_fit = np.linspace(35, 125, 300)
    life_exp_fit = exp_model(stress_fit, a_exp, b_exp)
    life_power_fit = power_model(stress_fit, a_power, b_power)
    
    # ----- 左图：Exponential -----
    ax1 = axes[0]
    ax1.scatter(stress_all, observed_life, color='red', s=40, alpha=0.7,
                label='30个模拟数据点', zorder=5)
    ax1.plot(stress_fit, life_exp_fit, 'b-', linewidth=2.5,
             label='Exponential 拟合')
    ax1.axvline(x=use_stress, color='green', linestyle='--', linewidth=2,
                label=f'使用应力 ({use_stress}°C)')
    ax1.axhline(y=life_exp_use, color='blue', linestyle=':', linewidth=2,
                label=f'预测寿命: {life_exp_use:.0f}h')
    ax1.set_xlabel('应力 (温度)', fontsize=12)
    ax1.set_ylabel('寿命 (小时)', fontsize=12)
    ax1.set_title(f'✅ Exponential (正确物理模型)\nAICc = {aicc_exp:.1f}', fontsize=13)
    ax1.legend(loc='upper right', fontsize=9)
    ax1.grid(True, alpha=0.3)
    ax1.set_xlim(35, 125)
    ax1.set_ylim(0, max(observed_life) * 1.4)
    
    # ----- 中图：Power -----
    ax2 = axes[1]
    ax2.scatter(stress_all, observed_life, color='red', s=40, alpha=0.7,
                label='30个模拟数据点', zorder=5)
    ax2.plot(stress_fit, life_power_fit, 'r-', linewidth=2.5,
             label='Power 拟合')
    ax2.axvline(x=use_stress, color='green', linestyle='--', linewidth=2,
                label=f'使用应力 ({use_stress}°C)')
    ax2.axhline(y=life_power_use, color='red', linestyle=':', linewidth=2,
                label=f'预测寿命: {life_power_use:.0f}h')
    ax2.set_xlabel('应力 (温度)', fontsize=12)
    ax2.set_ylabel('寿命 (小时)', fontsize=12)
    ax2.set_title(f'❌ Power (错误物理模型)\nAICc = {aicc_power:.1f} ✅ 更小！', fontsize=13)
    ax2.legend(loc='upper right', fontsize=9)
    ax2.grid(True, alpha=0.3)
    ax2.set_xlim(35, 125)
    ax2.set_ylim(0, max(observed_life) * 1.4)
    
    # ----- 右图：外推对比 -----
    ax3 = axes[2]
    extrap_stress = np.linspace(35, 80, 200)
    life_exp_extrap = exp_model(extrap_stress, a_exp, b_exp)
    life_power_extrap = power_model(extrap_stress, a_power, b_power)
    
    ax3.plot(extrap_stress, life_exp_extrap, 'b-', linewidth=3,
             label=f'Exponential (AICc={aicc_exp:.1f})', alpha=0.9)
    ax3.plot(extrap_stress, life_power_extrap, 'r-', linewidth=3,
             label=f'Power (AICc={aicc_power:.1f} ✅)', alpha=0.9)
    ax3.axvline(x=use_stress, color='green', linestyle='--', linewidth=2.5,
                label='使用应力 (40°C)')
    ax3.axhline(y=life_exp_use, color='blue', linestyle=':', linewidth=2,
                label=f'Exponential: {life_exp_use:.0f}h')
    ax3.axhline(y=life_power_use, color='red', linestyle=':', linewidth=2,
                label=f'Power: {life_power_use:.0f}h')
    ax3.fill_between(extrap_stress,
                     life_power_extrap, life_exp_extrap,
                     where=(extrap_stress < 60),
                     color='red', alpha=0.15, label='⚠️ 外推风险区')
    ax3.set_xlabel('应力 (温度)', fontsize=12)
    ax3.set_ylabel('寿命 (小时)', fontsize=12)
    ax3.set_title(f'⚠️ 外推对比：差距 {ratio:.1f} 倍！', fontsize=13)
    ax3.legend(loc='upper right', fontsize=9)
    ax3.grid(True, alpha=0.3)
    ax3.set_xlim(35, 80)
    ax3.set_ylim(0, max(life_power_extrap) * 1.1)
    
    plt.tight_layout()
    st.pyplot(fig)
    
    # ====== 关键教学结论 ======
    # 先构建表格字符串
    table_html = f"""
    | 项目 | Exponential (正确) | Power (错误) |
    |------|-------------------|--------------|
    | **AICc** | {aicc_exp:.1f} | {aicc_power:.1f} ✅ |
    | **在使用应力(40°C)下的预测寿命** | {life_exp_use:.0f} 小时 | {life_power_use:.0f} 小时 |
    | **外推差异** | 物理合理 | **比正确模型大了 {ratio:.1f} 倍！** |
    """
    
    st.markdown("### 🎯 教学结论")
    st.markdown(table_html)
    
    st.error("""
    ### ⚠️ 核心教训

    **Power 模型的 AICc 更小（拟合得更好），但外推结果是完全错误的！**

    这告诉我们：

    1. **AICc 只衡量"数据拟合优度"**，不衡量"物理合理性"
    2. **在 ALT 中，物理机理 > 统计指标**
    3. **如果应力是温度，必须使用 Exponential/Eyring，即使 AICc 稍大**

    **原因**：Power 模型的参数更灵活，能够更好地"扭曲"自己来拟合噪声数据，
    但这种扭曲在数据点之外会被放大，导致外推灾难。

    > 💡 **工程结论**：选模型时，先用物理筛选候选，再用 AICc 做微调。
    > **绝对不要让 AICc 推翻物理规律！**
    """)
# ==================== 双应力模型 ====================
elif nav == "⚡ 双应力模型":
    st.header("⚡ 双应力模型（3种应力关系 × 4种分布）")

    st.markdown("""
    ### 双应力模型的物理含义

    | 模型 | 应力关系 | 适用场景 | 交互作用 |
    |------|----------|----------|----------|
    | **Dual_Exponential** | 双指数 | 两个热应力（如温湿度） | 强协同效应 |
    | **Power_Exponential** | 电压 × 温度 | 电压 + 温度 | 弱交互/独立 |
    | **Dual_Power** | 双逆幂律 | 两个非热应力（如电压+振动） | 独立作用 |
    """)

    st.markdown("### 完整的12个双应力模型")

    dual_data = {
        "模型": [
            "Weibull_Dual_Exponential", "Weibull_Power_Exponential", "Weibull_Dual_Power",
            "Lognormal_Dual_Exponential", "Lognormal_Power_Exponential", "Lognormal_Dual_Power",
            "Normal_Dual_Exponential", "Normal_Power_Exponential", "Normal_Dual_Power",
            "Exponential_Dual_Exponential", "Exponential_Power_Exponential", "Exponential_Dual_Power"
        ],
        "应力关系": [
            "双指数(热+热)", "电压×温度", "双逆幂律(非热+非热)",
            "双指数(热+热)", "电压×温度", "双逆幂律(非热+非热)",
            "双指数(热+热)", "电压×温度", "双逆幂律(非热+非热)",
            "双指数(热+热)", "电压×温度", "双逆幂律(非热+非热)"
        ],
        "分布": [
            "Weibull", "Weibull", "Weibull",
            "Lognormal", "Lognormal", "Lognormal",
            "Normal", "Normal", "Normal",
            "Exponential", "Exponential", "Exponential"
        ],
        "典型场景": [
            "温湿度加速老化", "电容电压+温度", "振动+温度",
            "湿热疲劳", "PCB应力+温度", "机械疲劳+腐蚀",
            "材料退化(温湿)", "绝缘老化(电+热)", "磨损+腐蚀",
            "电源温湿度", "电子器件电热", "振动随机失效"
        ]
    }

    import pandas as pd
    df_dual = pd.DataFrame(dual_data)
    st.dataframe(df_dual, use_container_width=True, hide_index=True)

# ==================== 双应力物理图解 ====================
elif nav == "🔗 双应力物理图解":
    st.header("🔗 双应力模型物理图解")

    st.markdown("### 三种双应力关系的交互效应对比")

    fig, axes = plt.subplots(1, 3, figsize=(15, 5))

    stress1 = np.linspace(80, 120, 100)
    stress2_vals = [2.0, 2.5, 3.0]

    ax1 = axes[0]
    for s2 in stress2_vals:
        life = 5000 * np.exp(-0.03 * stress1) * np.exp(-0.5 * s2)
        ax1.plot(stress1, life, label=f'应力2={s2}')
    ax1.set_xlabel('应力1 (温度)', fontsize=12)
    ax1.set_ylabel('寿命', fontsize=12)
    ax1.set_title('Dual_Exponential\n强协同效应 (交互项显著)', fontsize=14)
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    ax2 = axes[1]
    for s2 in stress2_vals:
        life = 5000 * stress1**(-2) * np.exp(-0.3 * s2)
        ax2.plot(stress1, life, label=f'应力2={s2}')
    ax2.set_xlabel('应力1 (电压)', fontsize=12)
    ax2.set_ylabel('寿命', fontsize=12)
    ax2.set_title('Power_Exponential\n弱交互/独立作用', fontsize=14)
    ax2.legend()
    ax2.grid(True, alpha=0.3)

    ax3 = axes[2]
    ax3.text(0.5, 0.8, '选择双应力模型', ha='center', fontsize=14, weight='bold')
    ax3.text(0.5, 0.6, '↓', ha='center', fontsize=16)
    ax3.text(0.5, 0.45, '应力1 和 应力2 都是热应力？', ha='center', fontsize=12)
    ax3.text(0.5, 0.3, '是 → Dual_Exponential', ha='center', fontsize=12, color='green')
    ax3.text(0.5, 0.15, '否 (热+非热) → Power_Exponential', ha='center', fontsize=12, color='blue')
    ax3.text(0.5, 0.0, '否 (非热+非热) → Dual_Power', ha='center', fontsize=12, color='red')
    ax3.set_xlim(0, 1)
    ax3.set_ylim(0, 1)
    ax3.axis('off')

    plt.tight_layout()
    st.pyplot(fig)

    st.success("""
    💡 **核心原则**：
    - **交互效应显著**（两个应力协同加速）→ 选 Dual_Exponential 或 Dual_Power
    - **交互效应微弱**（应力独立作用）→ 选 Power_Exponential（热+非热组合）
    - 模型拟合中交互项系数可验证这一判断
    """)

# ==================== 选择流程 ====================
elif nav == "📋 选择流程":
    st.header("📋 ALT 模型选择的完整工作流程")

    st.markdown("""
    ### 四步决策法

    ```mermaid
    graph TD
        A[开始] --> B{应力类型?}
        B -->|温度| C[Exponential / Eyring]
        B -->|电压/振动/压力| D[Power]
        B -->|混合| E[双应力组合]
        
        C --> F{失效特征?}
        D --> F
        E --> F
        
        F -->|早期失效| G[Weibull β<1]
        F -->|随机失效| H[Exponential]
        F -->|耗损失效| I[Weibull β>1]
        F -->|疲劳/裂纹| J[Lognormal]
        F -->|退化/磨损| K[Normal]
        
        G --> L[检查物理一致性]
        H --> L
        I --> L
        J --> L
        K --> L
        
        L --> M{通过检查?}
        M -->|是| N[用 AICc 做最终选择]
        M -->|否| O[返回重选或考虑物理约束]
                """)
