import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import re

# 1. 網頁頁面配置
st.set_page_config(page_title="MathAI CPI Forecast", layout="wide")

# ================= 🚀 【手機版響應式外觀極致 CSS 優化】 =================
st.html("""
    <style>
        .block-container {
            padding-top: 4.5rem !important;
            padding-bottom: 2rem !important;
            padding-left: 1rem !important;
            padding-right: 1rem !important;
        }
        .main-title {
            font-size: calc(20px + 0.5vw) !important;
            font-weight: 700 !important;
            color: #1E293B !important;
            margin-bottom: 8px !important;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        }
        .sub-title {
            font-size: calc(12px + 0.3vw) !important;
            font-weight: 500 !important;
            color: #64748B !important;
            margin-bottom: 15px !important;
        }
        [data-testid="stMetric"] {
            background-color: #F8FAFC !important;
            border: 1px solid #E2E8F0 !important;
            padding: 12px 16px !important;
            border-radius: 8px !important;
            margin-bottom: 10px !important;
        }
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
        date_col = col_mapping.get("A")       
        actual_col = col_mapping.get("G")     
        estimate_col = col_mapping.get("H")   
        text_col = col_mapping.get("I")       
        overall_r2_col = col_mapping.get("K") 
        overall_mse_col = col_mapping.get("L") 
        x_index_col = col_mapping.get("C")     
        engine_label = "外生限制短期趨勢"
    else:
        date_col = col_mapping.get("V")       
        actual_col = col_mapping.get("AA")    
        estimate_col = col_mapping.get("AB")  
        text_col = col_mapping.get("AC")      
        overall_r2_col = col_mapping.get("AE") 
        overall_mse_col = col_mapping.get("AF") 
        x_index_col = col_mapping.get("W")     
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
        
    short_r2 = None
    overall_r2 = None
    overall_mse = None
    is_new_trend = False
    start_x_val = None 
    
    if text_col and text_col in df_raw.columns:
        text_list = df_raw[text_col].fillna("").astype(str).tolist()
        text_block = " ".join(text_list)
        
        r2_matches = re.findall(r'(?:R2|R\^2|R_2)\s*=\s*(-?\d+\.?\d*(?:[eE][-+]?\d+)?)', text_block, re.IGNORECASE)
        if r2_matches: short_r2 = float(r2_matches[-1])
            
        if "新趨勢" in text_block or "new line" in text_block.lower() or "sorting" in text_block.lower():
            is_new_trend = True

        anova_idx = -1
        for idx in range(len(text_list) - 1, -1, -1):
            if "anova" in text_list[idx].lower():
                anova_idx = idx
                break
        
        if anova_idx >= 5:
            target_line_text = text_list[anova_idx - 5]
            x_matches = re.findall(r'(?:from|\s+X\s*=\s*|\s+X\s+|\D)(\d+)', target_line_text, re.IGNORECASE)
            if x_matches:
                start_x_val = int(x_matches[-1])

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
    st.error(f"❌ 數據與 ANOVA 指標提取失敗。錯誤: {e}")
    st.stop()

if is_new_trend:
    st.error(f"🚨 **MathAI 趨勢拐點警報**：當前引擎已自動捕捉到動態趨勢轉折點！")
else:
    st.success(f"ℹ️ **當前模型狀態**：美國通膨數據在該區間內運作平穩。")

# 5. 💡【重構原生圖表物件】：直接在 layout 中使用極簡、純淨的規格，確保完全相容 Python 3.14
layout = go.Layout(
    xaxis=dict(title="觀測日期 (YYYY-MM)"),
    yaxis=dict(title="年增率 (%)"),
    template="plotly_white",
    hovermode="x unified"
)
fig = go.Figure(layout=layout)

# FRED 實際年增率（純點）
fig.add_trace(go.Scatter(
    x=df_clean['display_date'], y=df_clean['Actual'],
    mode='markers', 
    name='FRED 實際 CPI 年增率',
    hovertemplate="<b>日期</b>: %{x}<br><b>實際值</b>: %{y}%<extra></extra>",
    marker=dict(color='#2ca02c' if "AI" in engine_type else '#1f77b4', size=6, opacity=0.7)
))

df_est_clean = df_clean.dropna(subset=['Estimate']).copy()
if not df_est_clean.empty:
    fig.add_trace(go.Scatter(
        x=df_est_clean['display_date'], y=df_est_clean['Estimate'],
        mode='lines', 
        name='MathAI 短期趨勢預估值',
        hovertemplate="<b>日期</b>: %{x}<br><b>預估值</b>: %{y:.4f}%<extra></extra>",
        line=dict(color='#d62728', width=3, dash='dash' if "AI" in engine_type else 'solid')
    ))

    if is_new_trend and start_x_val is not None:
        try:
            df_target_node = df_est_clean[df_est_clean['X_Idx'] == start_x_val]
            if df_target_node.empty and len(df_est_clean) >= 8:
                df_target_node = df_est_clean.iloc[-8:-7]

            if not df_target_node.empty:
                break_date = str(df_target_node['display_date'].iloc)
                break_val = float(df_target_node['Estimate'].iloc)
                
                fig.add_vline(x=break_date, line_width=1.5, line_dash="dash", line_color="#475569")
                fig.add_annotation(
                    x=break_date, y=break_val, text="🚨 趨勢轉折拐點",
                    showarrow=True, arrowhead=2, arrowcolor="#d62728", arrowsize=1, arrowwidth=2,
                    ax=0, ay=-40, bordercolor="#d62728", borderwidth=1, borderpad=4, bgcolor="#FEF2F2", opacity=0.95
                )
        except: pass

st.plotly_chart(fig, use_container_width=True)

# 6. 呈現自適應數據卡片
col1, col2, col3 = st.columns(3, gap="medium")
with col1: st.metric(label="📊 短期趨勢解釋力 (Short R²)", value=f"{short_r2:.6f}" if short_r2 is not None else "自動對齊中")
with col2: st.metric(label="🏛️ 模型整體解釋力 (Overall R²)", value=str(overall_r2) if overall_r2 is not None else "自動對齊中")
with col3: st.metric(label="📐 模型整體均方誤差 (Overall MSE)", value=str(overall_mse) if overall_mse is not None else "自動對齊中")

st.write("---")
st.caption("🔒 Powered by MathAI Propelled Dual-Engine.")
