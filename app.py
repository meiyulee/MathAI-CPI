import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import re

# 1. 網頁頁面配置
st.set_page_config(page_title="MathAI CPI Forecast", layout="wide")

st.html("""
    <style>
        .block-container { padding-top: 4.5rem !important; padding-bottom: 2rem !important; }
        .main-title { font-size: 26px !important; font-weight: 700 !important; color: #1E293B !important; margin-bottom: 8px !important; }
        .sub-title { font-size: 15px !important; font-weight: 500 !important; color: #64748B !important; margin-bottom: 15px !important; }
    </style>
""")

st.html('<div class="main-title">📊 MathAI：美國通貨膨脹率預測系統</div>')
st.html('<div class="sub-title">外生限制短期趨勢引擎 <span style="color:#CBD5E1;">│</span> AI 數據自主分段進化引擎</div>')
st.write("---")

# 2. 自動讀取 Excel 檔案
@st.cache_data
def load_excel_data():
    for name in ["cpi_data.xlsx", "CPIAUCNS_2006_2025.xlsx"]:
        try:
            excel_obj = pd.ExcelFile(name)
            return excel_obj.sheet_names, name
        except:
            continue
    st.error("❌ 找不到您的 Excel 檔案，請確認您的 Excel 檔名是否為 cpi_data.xlsx")
    st.stop()

sheet_names, excel_file = load_excel_data()

model_sheets = []
for s in sheet_names:
    cleaned_name = str(s).strip()
    if cleaned_name.isdigit() and len(cleaned_name) == 6 and int(cleaned_name) >= 202501:
        model_sheets.append(cleaned_name)

if not model_sheets:
    model_sheets = [s for s in sheet_names if any(char.isdigit() for char in s)]
else:
    model_sheets.sort(reverse=True)

# 3. 側邊控制面板
st.sidebar.header("🎛️ 模型參數選單")
selected_sheet = st.sidebar.selectbox("1. 選擇模型分析工作表 (月份)", model_sheets)
engine_type = st.sidebar.radio("2. 選擇 MathAI 核心引擎", ["外生限制短期趨勢內樣本", "AI 自主進化版 (從2018開始)"])

# 4. 精準字母定位與雙軌統計指標提取核心
try:
    df_raw = pd.read_excel(excel_file, sheet_name=selected_sheet, skiprows=11)
    
    alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    extended_cols = list(alphabet) + [f"A{char}" for char in alphabet]
    col_mapping = {extended_cols[idx]: col_name for idx, col_name in enumerate(df_raw.columns) if idx < len(extended_cols)}

    if "外生" in engine_type:
        date_col = col_mapping.get("A")       # A 欄：日期
        actual_col = col_mapping.get("G")     # G 欄：實際年增率原始值
        estimate_col = col_mapping.get("H")   # H 欄：估計值
        text_col = col_mapping.get("I")       # I 欄：最新短期趨勢文字段落區
        overall_r2_col = col_mapping.get("K") # K 欄：整體 R²
        overall_mse_col = col_mapping.get("L") # L 欄：整體 MSE
        x_index_col = col_mapping.get("C")     # C 欄：時間序 X 欄位
        engine_label = "外生限制短期趨勢"
    else:
        date_col = col_mapping.get("V")       # V 欄：日期
        actual_col = col_mapping.get("AA")    # AA 欄：實際年增率原始值
        estimate_col = col_mapping.get("AB")  # AB 欄：估計值
        text_col = col_mapping.get("AC")      # AC 欄：趨勢文字區
        overall_r2_col = col_mapping.get("AE") # AE 欄：整體 R² 欄位
        overall_mse_col = col_mapping.get("AF") # AF 欄：整體 MSE 欄位
        x_index_col = col_mapping.get("W")     # W 欄：時間序 X 欄位
        engine_label = "AI自主進化"

    if not date_col or not actual_col or not estimate_col:
        st.error("❌ 找不到對應的 Excel 欄位字母，請檢查 Excel 結構。")
        st.stop()

    df_clean = pd.DataFrame({
        'Date': df_raw[date_col],
        'Actual': pd.to_numeric(df_raw[actual_col], errors='coerce'),
        'Estimate': pd.to_numeric(df_raw[estimate_col], errors='coerce'),
        'X_Idx': pd.to_numeric(df_raw[x_index_col], errors='coerce')
    }).dropna(subset=['Actual', 'Date']).copy()
    
    df_clean['display_date'] = pd.to_datetime(df_clean['Date'], errors='coerce').dt.strftime('%Y-%m')
        
    # === 🎯 統計指標與最新趨勢起點全自動提取 ===
    short_r2 = None
    overall_r2 = None
    overall_mse = None
    is_new_trend = False
    start_x_val = None 
    
    if text_col and text_col in df_raw.columns:
        text_list = df_raw[text_col].fillna("").astype(str).tolist()
        text_block = " ".join(text_list)
        
        # 1. 提取最新短期趨勢 R² 
        r2_matches = re.findall(r'(?:R2|R\^2|R_2)\s*=\s*(-?\d+\.?\d*(?:[eE][-+]?\d+)?)', text_block, re.IGNORECASE)
        if r2_matches: short_r2 = float(r2_matches[-1])
            
        if "新趨勢" in text_block or "new line" in text_block.lower() or "sorting" in text_block.lower():
            is_new_trend = True

        # 2. 🚀【核心優化：ANOVA 倒序空間平移鎖定演算法】
        # 倒序尋找 "ANOVA" 大字出現的精準行數
        anova_idx = -1
        for idx in range(len(text_list) - 1, -1, -1):
            if "anova" in text_list[idx].lower():
                anova_idx = idx
                break
        
        # 如果找到 ANOVA，直接精準往上抓取第 5 列（即 anova_idx - 5）
        if anova_idx >= 5:
            target_line_text = text_list[anova_idx - 5]
            # 從這行萬中選一的專屬文字中，抓取第一個數字（即起點 X 數字）
            x_matches = re.findall(r'(?:from|\s+X\s*=\s*|\s+X\s+|\D)(\d+)', target_line_text, re.IGNORECASE)
            if x_matches:
                start_x_val = int(x_matches[0]) # 鎖定 X 起點數字（如限制版的 115，進化版的 93）

    # 3. 全自動倒序 K 欄與 L 欄打撈長期指標
    if overall_r2_col and overall_r2_col in df_raw.columns:
        r2_list = df_raw[overall_r2_col].fillna("").astype(str).tolist()
        for i in range(len(r2_list) - 1, -1, -1):
            val_str = r2_list[i].strip()
            if re.match(r'^0\.\d+$', val_str):
                overall_r2 = f"{float(val_str):.6f}"
                break

    if overall_mse_col and overall_mse_col in df_raw.columns:
        mse_list = df_raw[overall_mse_col].fillna("").astype(str).tolist()
        for i in range(len(mse_list) - 1, -1, -1):
            try:
                val_num = float(mse_list[i])
                if 0.0 < val_num < 0.5:
                    overall_mse = f"{val_num:.6f}"
                    break
            except: continue

except Exception as e:
    st.error(f"❌ 數據與 ANOVA 指標提取失敗。請檢查 Excel 結構。錯誤: {e}")
    st.stop()

if is_new_trend:
    st.error(f"🚨 **MathAI 趨勢拐點警報**：當前引擎已自動捕捉到動態趨勢轉折點！")
else:
    st.success(f"ℹ️ **當前模型狀態**：美國通膨數據在該區間內運作平穩。")

# 5. 繪製純淨單軸 Plotly 金融圖表
fig = go.Figure()

# FRED 實際年增率（純點）
fig.add_trace(go.Scatter(
    x=df_clean['display_date'], y=df_clean['Actual'],
    mode='markers', 
    name='FRED 實際 CPI 年增率 (%)',
    hovertemplate="<b>日期</b>: %{x}<br><b>實際年增率</b>: %{y}%<extra></extra>",
    marker=dict(color='#2ca02c' if "AI" in engine_type else '#1f77b4', size=6, opacity=0.7)
))

# MathAI 精準多線段短期趨勢預估值（實線穿透）
df_est_clean = df_clean.dropna(subset=['Estimate']).copy()
if not df_est_clean.empty:
    fig.add_trace(go.Scatter(
        x=df_est_clean['display_date'], y=df_est_clean['Estimate'],
        mode='lines', 
        name='MathAI 精準多線段短期趨勢預估值 (%)',
        hovertemplate="<b>日期</b>: %{x}<br><b>MathAI 預估值</b>: %{y:.4f}%<extra></extra>",
        line=dict(color='#d62728', width=3, dash='dash' if "AI" in engine_type else 'solid')
    ))

    # === 🚨 【EconTech 空間大會合：100% 精準對齊最新線段起點】 ===
    if is_new_trend and start_x_val is not None:
        try:
            # 尋找 X_Idx 完全等於平移第 5 列所撈出的起點數字那一行
            df_target_node = df_est_clean[df_est_clean['X_Idx'] == start_x_val]
            
            # 智慧備用容錯保護
            if df_target_node.empty and len(df_est_clean) >= 8:
                df_target_node = df_est_clean.iloc[-8:-7]

            if not df_target_node.empty:
                break_date = str(df_target_node['display_date'].iloc[0])
                break_val = float(df_target_node['Estimate'].iloc[0])
                
                # 畫穿透灰色虛線
                fig.add_vline(x=break_date, line_width=1.5, line_dash="dash", line_color="#475569")
                
                # 彈出紅框標籤
                fig.add_annotation(
                    x=break_date, y=break_val, text="🚨 MathAI 內生趨勢轉折拐點",
                    showarrow=True, arrowhead=2, arrowcolor="#d62728", arrowsize=1, arrowwidth=2,
                    ax=0, ay=-40, bordercolor="#d62728", borderwidth=1, borderpad=4, bgcolor="#FEF2F2", opacity=0.95
                )
        except Exception as annotation_err:
            pass

fig.update_layout(
    title=None,
    xaxis_title="觀測日期 (YYYY-MM)", yaxis_title="通貨膨脹率 / 年增率 (%)",
    hovermode="x unified", template="plotly_white",
    legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.02), margin=dict(t=10, b=10)
)
st.plotly_chart(fig, use_container_width=True)

# 6. 呈現量化指標卡片
col1, col2, col3 = st.columns(3)
with col1: st.metric(label="📊 短期趨勢解釋力 (Short R²)", value=f"{short_r2:.6f}" if short_r2 is not None else "自動對齊中")
with col2: st.metric(label="🏛️ 模型整體解釋力 (Overall R²)", value=str(overall_r2) if overall_r2 is not None else "自動對齊中")
with col3: st.metric(label="📐 模型整體均方誤差 (Overall MSE)", value=str(overall_mse) if overall_mse is not None else "自動對齊中")

st.write("---")
st.caption("🔒 Powered by MathAI Propelled Dual-Engine. Relative Row Displacement Anchoring System.")
