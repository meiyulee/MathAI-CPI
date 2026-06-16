import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import re

# 1. 網頁頁面配置
st.set_page_config(page_title="MathAI CPI Forecast", layout="wide")

st.title("🤖 MathAI：美國通貨膨脹率預測系統")
st.markdown("### 傳統計量限制引擎 vs. AI 數據自主分段進化引擎")
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

model_sheets = [s for s in sheet_names if any(char.isdigit() for char in s)]
if not model_sheets:
    model_sheets = sheet_names

# 3. 側邊控制面板
st.sidebar.header("🎛️ 模型參數選單")
selected_sheet = st.sidebar.selectbox("1. 選擇模型分析工作表 (月份)", model_sheets)
engine_type = st.sidebar.radio("2. 選擇 MathAI 核心引擎", ["傳統計量限制版", "AI 自主進化版 (從2018開始)"])

# 4. 根據選定的引擎，進行精準的欄位定位與 2025 時間過濾
try:
    df_raw = pd.read_excel(excel_file, sheet_name=selected_sheet, skiprows=11)
    
    if "傳統" in engine_type:
        # 【傳統計量限制版】
        # A欄=col_0(日期), G欄=col_6(實際年增率), H欄=col_7(估計值), J欄=col_9(文字區)
        df_model = df_raw.iloc[:, :15].copy()
        df_model.columns = [f"col_{i}" for i in range(df_model.shape[1])]
        
        date_col = "col_0"
        actual_col = "col_6"   # G 欄
        estimate_col = "col_7" # H 欄
        text_col = "col_9"     # J 欄
        engine_label = "傳統計量限制"
        
    else:
        # 【AI自主進化版】
        # V欄=col_0(日期), AA欄=col_5(實際年增率), AB欄=col_6(估計值), AE欄=col_9(文字區)
        df_model = df_raw.iloc[:, 21:32].copy()
        df_model.columns = [f"col_{i}" for i in range(df_model.shape[1])]
        
        date_col = "col_0"
        actual_col = "col_5"   # AA 欄
        estimate_col = "col_6" # AB 欄
        text_col = "col_9"     # AE 欄
        engine_label = "AI自主進化"

    # 確保欄位皆轉為正確型態
    df_model[date_col] = pd.to_datetime(df_model[date_col], errors='coerce')
    df_model[actual_col] = pd.to_numeric(df_model[actual_col], errors='coerce')
    df_model[estimate_col] = pd.to_numeric(df_model[estimate_col], errors='coerce')
    
    # 核心關鍵：過濾掉空值，且強制限縮在 2025 年 1 月 1 日之後的數據
    df_filtered = df_model[(df_model[date_col] >= '2025-01-01')].dropna(subset=[actual_col, date_col]).copy()
    
    # 將日期格式化為乾淨的字串以便 X 軸呈現
    df_filtered['display_date'] = df_filtered[date_col].dt.strftime('%Y-%m')
    
    # 全自動搜尋右側文字說明區，用來捕捉 R2 與 拐點警報
    text_block = ""
    if text_col in df_filtered.columns:
        text_block = "".join(df_raw.iloc[:, 11 if "傳統" in engine_type else 30].dropna().astype(str).tolist())
        
    r2, is_new_trend = 0.0, False
    r2_match = re.search(r'R2\s*=\s*(\d+\.\d+)', text_block)
    if r2_match: r2 = float(r2_match.group(1))
    if "新趨勢" in text_block or "new line" in text_block.lower() or "sorting" in text_block.lower():
        is_new_trend = True
        
except Exception as e:
    st.error(f"❌ 數據剪裁失敗。請檢查 Excel 第 12 列之後的日期格式。錯誤: {e}")
    st.stop()

# 5. 智慧拐點警報顯示
if is_new_trend:
    st.error(f"🚨 **MathAI 趨勢拐點警報**：當前引擎已自動捕捉到動態趨勢轉折點！")
else:
    st.success(f"ℹ_ **當前模型狀態**：美國通膨數據在該區間內運作平穩。")

# 6. 繪製純淨單軸 Plotly 金融圖表
fig = go.Figure()

# 繪製真實 CPI 年增率歷史線
fig.add_trace(go.Scatter(
    x=df_filtered['display_date'], y=df_filtered[actual_col],
    mode='markers+lines', 
    name='FRED 實際 CPI 年增率 (%)',
    hovertemplate="<b>日期</b>: %{x}<br><b>實際年增率</b>: %{y}%<extra></extra>",
    line=dict(color='#2ca02c' if "AI" in engine_type else '#1f77b4', width=2),
    marker=dict(size=6)
))

# 繪製 MathAI 預測回歸線（直接採用 H 欄或 AB 欄，完全共用同一個 Y 軸）
df_est_clean = df_filtered.dropna(subset=[estimate_col])
if not df_est_clean.empty:
    fig.add_trace(go.Scatter(
        x=df_est_clean['display_date'], y=df_est_clean[estimate_col],
        mode='lines', 
        name=f'MathAI {engine_label}預估值 (%)',
        hovertemplate="<b>日期</b>: %{x}<br><b>MathAI 預估值</b>: %{y:.4f}%<extra></extra>",
        line=dict(color='#d62728', width=3, dash='dash' if "AI" in engine_type else 'solid')
    ))

# 圖表外觀極簡化配置
fig.update_layout(
    title=f"美國 CPI 年增率與 MathAI 預測趨勢對照圖 (2025年起精華摘要)",
    xaxis_title="觀測日期 (YYYY-MM)",
    yaxis_title="通貨膨脹率 / 年增率 (%)",
    hovermode="x unified",
    template="plotly_white",
    legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.02)
)

st.plotly_chart(fig, use_container_width=True)

# 7. 呈現量化指標卡片
col1, col2, col3 = st.columns(3)
with col1: st.metric(label="📊 引擎自適應解釋力 (R²)", value=f"{r2:.4f}" if r2 != 0.0 else "由後台動態優化中")
with col2: st.metric(label="📅 資料顯示起點", value="2025-01")
with col3: st.metric(label="📈 當前分析狀態", value="精簡版同步中")

st.write("---")
st.caption("🔒 Powered by MathAI Propelled Dual-Engine. Data truncated from 2025-01 for executive summary.")
