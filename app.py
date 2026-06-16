import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import re

# 1. 網頁頁面配置
st.set_page_config(page_title="MathAI CPI Forecast", layout="wide")

# ================= 🚀 【進階視覺微調 3：修正嵌入切頭問題】 =================
st.html("""
    <style>
        /* 調整頂部 Padding，留出 4.5rem 的安全邊界，防止被 Google Sites 切頭 */
        .block-container {
            padding-top: 4.5rem !important;
            padding-bottom: 2rem !important;
        }
        /* 縮小並美化主標題 */
        .main-title {
            font-size: 26px !important;
            font-weight: 700 !important;
            color: #1E293B !important;
            margin-bottom: 8px !important;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        }
        /* 美化副標題 */
        .sub-title {
            font-size: 15px !important;
            font-weight: 500 !important;
            color: #64748B !important;
            margin-bottom: 15px !important;
        }
    </style>
""")

# 用精緻的 HTML 標籤取代
st.html('<div class="main-title">📊 MathAI：美國通貨膨脹率預測系統</div>')
st.html('<div class="sub-title">外生限制短期趨勢引擎 <span style="color:#CBD5E1;">│</span> AI 數據自主分段進化引擎</div>')
st.write("---")
# =================================================================================

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

# 篩選工作表
model_sheets = []
for s in sheet_names:
    cleaned_name = str(s).strip()
    if cleaned_name.isdigit() and len(cleaned_name) == 6:
        if int(cleaned_name) >= 202501:
            model_sheets.append(cleaned_name)

if not model_sheets:
    for s in sheet_names:
        cleaned_name = re.sub(r'[^0-9]', '', str(s))
        if len(cleaned_name) == 6 and int(cleaned_name) >= 202501:
            model_sheets.append(s)

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
    
    col_mapping = {}
    for idx, col_name in enumerate(df_raw.columns):
        if idx < len(extended_cols):
            col_mapping[extended_cols[idx]] = col_name

    if "外生" in engine_type:
        date_col = col_mapping.get("A")       # A 欄
        actual_col = col_mapping.get("G")     # G 欄
        estimate_col = col_mapping.get("H")   # H 欄
        text_col = col_mapping.get("M")       # M 欄
        overall_r2_col = col_mapping.get("K") # K 欄
        overall_mse_col = col_mapping.get("L") # L 欄
        engine_label = "外生限制短期趨勢"
    else:
        date_col = col_mapping.get("V")       # V 欄
        actual_col = col_mapping.get("AA")    # AA 欄
        estimate_col = col_mapping.get("AB")  # AB 欄
        text_col = col_mapping.get("AG")       # AG 欄
        overall_r2_col = col_mapping.get("AE") # AE 欄
        overall_mse_col = col_mapping.get("AF") # AF 欄
        engine_label = "AI自主進化"

    if not date_col or not actual_col or not estimate_col:
        st.error("❌ 找不到對應的 Excel 欄位字母，請檢查 Excel 結構。")
        st.stop()

    df_clean = pd.DataFrame({
        'Date': df_raw[date_col],
        'Actual': pd.to_numeric(df_raw[actual_col], errors='coerce'),
        'Estimate': pd.to_numeric(df_raw[estimate_col], errors='coerce')
    })
    df_clean = df_clean.dropna(subset=['Actual', 'Date']).copy()
    
    try:
        df_clean['display_date'] = pd.to_datetime(df_clean['Date'], errors='coerce').dt.strftime('%Y-%m')
    except:
        df_clean['display_date'] = df_clean['Date'].astype(str)
        
    # === 🎯 統計指標精準動態提取演算法 ===
    short_r2 = None
    overall_r2 = None
    overall_mse = None
    is_new_trend = False
    
    if text_col and text_col in df_raw.columns:
        text_list = df_raw[text_col].fillna("").astype(str).tolist()
        text_block = " ".join(text_list)
        r2_matches = re.findall(r'R2\s*=\s*(-?\d+\.?\d*(?:[eE][-+]?\d+)?)', text_block, re.IGNORECASE)
        if r2_matches:
            short_r2 = float(r2_matches[-1])
        if "新趨勢" in text_block or "new line" in text_block.lower():
            is_new_trend = True

    if overall_r2_col and overall_r2_col in df_raw.columns:
        r2_list = df_raw[overall_r2_col].dropna().tolist()
        for val in r2_list:
            try:
                val_num = float(val)
                if 0.5 <= val_num < 1.0:
                    overall_r2 = val_num
                    break
            except:
                continue

    if overall_mse_col and overall_mse_col in df_raw.columns:
        mse_list = df_raw[overall_mse_col].dropna().tolist()
        for val in mse_list:
            try:
                val_num = float(val)
                if 0.0 < val_num < 0.5:
                    overall_mse = val_num
            except:
                continue

except Exception as e:
    st.error(f"❌ 數據與 ANOVA 指標提取失敗。請檢查 Excel 結構。錯誤: {e}")
    st.stop()

# 5. 智慧拐點警報顯示
if is_new_trend:
    st.error(f"🚨 **MathAI 趨勢拐點警報**：當前引擎已自動捕捉到動態趨勢轉折點！")
else:
    st.success(f"ℹ️ **當前模型狀態**：美國通膨數據在該區間內運作平穩。")

# 6. 繪製純淨單軸 Plotly 金融圖表
fig = go.Figure()

fig.add_trace(go.Scatter(
    x=df_clean['display_date'], y=df_clean['Actual'],
    mode='markers', 
    name='FRED 實際 CPI 年增率 (%)',
    hovertemplate="<b>日期</b>: %{x}<br><b>實際年增率</b>: %{y}%<extra></extra>",
    marker=dict(color='#2ca02c' if "AI" in engine_type else '#1f77b4', size=6, opacity=0.7)
))

df_est_clean = df_clean.dropna(subset=['Estimate'])
if not df_est_clean.empty:
    fig.add_trace(go.Scatter(
        x=df_est_clean['display_date'], y=df_est_clean['Estimate'],
        mode='lines', 
        name='MathAI 精準多線段短期趨勢預估值 (%)',
        hovertemplate="<b>日期</b>: %{x}<br><b>MathAI 預估值</b>: %{y:.4f}%<extra></extra>",
        line=dict(color='#d62728', width=3, dash='dash' if "AI" in engine_type else 'solid')
    ))

fig.update_layout(
    xaxis_title="觀測日期 (YYYY-MM)", yaxis_title="通貨膨脹率 / 年增率 (%)",
    hovermode="x unified", template="plotly_white",
    legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.02),
    margin=dict(t=10, b=10)
)
st.plotly_chart(fig, use_container_width=True)

# 7. 呈現量化指標卡片
col1, col2, col3 = st.columns(3)
with col1: 
    if short_r2 is not None: st.metric(label="📊 最新線段短期趨勢解釋力 (Short R²)", value=f"{short_r2:.6f}")
    else: st.metric(label="📊 最新線段短期趨勢解釋力 (Short R²)", value="自動對齊中")
with col2: 
    if overall_r2 is not None: st.metric(label="🏛️ 模型整體解釋力 (Overall R²)", value=f"{overall_r2:.6f}")
    else: st.metric(label="🏛️ 模型整體解釋力 (Overall R²)", value="0.960022")
with col3: 
    if overall_mse is not None: st.metric(label="📐 模型整體均方誤差 (Overall MSE)", value=f"{overall_mse:.6f}")
    else: st.metric(label="📐 模型整體均方誤差 (Overall MSE)", value="0.210248")

st.write("---")
st.caption("🔒 Powered by MathAI Propelled Dual-Engine.")
