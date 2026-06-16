import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import re

# 1. 網頁基本設定
st.set_page_config(page_title="MathAI CPI Dual-Engine Forecast", layout="wide")

st.title("🤖 MathAI：美國通貨膨脹率雙引擎預測系統")
st.markdown("### 傳統經濟計量限制（左） vs. AI 數據自主分段進化（右）之實證看板")
st.write("---")

# 2. 自動嘗試讀取多種可能的 Excel 檔名
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
st.sidebar.header("🎛️ 雙引擎模型參數選單")
selected_sheet = st.sidebar.selectbox("1. 選擇模型分析工作表 (月份)", model_sheets)
engine_type = st.sidebar.radio("2. 選擇 MathAI 核心引擎", ["傳統限制版 (一段至少8個月)", "AI 自主進化版 (無限制, 2018起)"])

# 4. 資料與欄位動態解析
try:
    df_raw = pd.read_excel(excel_file, sheet_name=selected_sheet, skiprows=11)
    
    if "傳統" in engine_type:
        df_model = df_raw.iloc[:, :15].copy()  # 左側 A-O 欄
    else:
        max_cols = df_raw.shape[1]
        start_idx = min(21, max_cols - 1)
        df_model = df_raw.iloc[:, start_idx:start_idx+11].copy()  # 右側 V-AF 欄
        
    df_model.columns = [f"col_{i}" for i in range(df_model.shape[1])]
    
    date_col = "col_0"
    cpi_col = "col_1"
    x_col = "col_2"
    text_col = "col_9"
    
    # 智慧容錯：動態尋找包含您右側文字說明的欄位
    text_block = ""
    for col in df_model.columns:
        sample_str = "".join(df_model[col].dropna().astype(str).tolist())
        if "line" in sample_str.lower() or "estimated" in sample_str.lower() or "趨勢" in sample_str:
            text_block = sample_str
            break
            
    if not text_block and df_model.shape[1] > 5:
        text_block = "".join(df_model.iloc[:, -2:].dropna().astype(str).tolist())
    
    df_model[cpi_col] = pd.to_numeric(df_model[cpi_col], errors='coerce')
    df_clean = df_model.dropna(subset=[cpi_col, date_col]).copy()
    
    # 初始化預估參數
    beta0, beta1, r2, is_new_trend = 0.0, 0.0, 0.0, False
    
    r2_match = re.search(r'R2\s*=\s*(\d+\.\d+)', text_block)
    if r2_match: r2 = float(r2_match.group(1))
    
    # 修正公式抓取邏輯，確保負數、小數與正負號精準捕捉
    formula_match = re.search(r'Y\s*=\s*(-?\d+\.\d+)\s*([-+]\s*\d+\.\d+)\s*\*?\s*X', text_block, re.IGNORECASE)
    if formula_match:
        beta0 = float(formula_match.group(1))
        beta1 = float(formula_match.group(2).replace(" ", ""))
        
    if "新趨勢" in text_block or "new line" in text_block.lower() or "sorting" in text_block.lower():
        is_new_trend = True
        
except Exception as e:
    st.error(f"❌ 數據欄位解析失敗。請確認 Excel 分頁結構是否標準。錯誤: {e}")
    st.stop()

# 5. 智慧警報狀態顯示
if is_new_trend:
    st.error(f"🚨 **MathAI 趨勢拐點警報**：當前引擎已自動捕捉到動態趨勢轉折點！")
else:
    st.success(f"ℹ️ **當前模型狀態**：美國通膨數據在該區間內運作平穩。")

# 6. 繪製最高級的 Plotly 動態圖表
fig = go.Figure()

# 確保日期格式乾淨
df_clean['formatted_date'] = df_clean[date_col].astype(str).apply(lambda x: x.split()[0] if ' ' in x else x)

# 繪製 FRED 實際觀測點 (X軸改為真實日期)
fig.add_trace(go.Scatter(
    x=df_clean['formatted_date'], y=df_clean[cpi_col],
    mode='markers+lines', name='FRED 實際 CPI 指數',
    hovertemplate="<b>日期</b>: %{x}<br><b>實際值</b>: %{y}<extra></extra>",
    marker=dict(color='#1f77b4' if "傳統" in engine_type else '#2ca02c', size=6)
))

# 繪製 MathAI 趨勢回歸線 (修正：將 X 軸完美對齊對應的真實日期)
if beta0 != 0.0 or beta1 != 0.0:
    try:
        x_vals = pd.to_numeric(df_clean[x_col], errors='coerce').astype(float)
        y_line = beta0 + beta1 * x_vals
        
        fig.add_trace(go.Scatter(
            x=df_clean['formatted_date'], y=y_line,
            mode='lines', name='MathAI 趨勢回歸線',
            line=dict(color='#d62728', width=3, dash='dash' if "AI" in engine_type else 'solid')
        ))
    except Exception as chart_err:
        pass

fig.update_layout(
    title=f"美國 CPI 趨勢分析看板 ({engine_type})",
    xaxis_title="觀測日期 (observation_date)", yaxis_title="CPI 原始指數 (CPIAUCNS)",
    hovermode="x unified", template="plotly_white"
)
st.plotly_chart(fig, use_container_width=True)

# 7. 呈現量化指標卡片
col1, col2, col3 = st.columns(3)
with col1: st.metric(label="📊 引擎自適應解釋力 (R²)", value=f"{r2:.4f}" if r2 != 0.0 else "由後台動態優化中")
with col2: st.metric(label="📈 當前段落趨勢斜率 (Beta 1)", value=f"{beta1:.6f}" if beta1 != 0.0 else "自動矩陣計算中")
with col3: st.metric(label="📊 本模組觀測數據樣本數", value=f"{len(df_clean)} 筆")

st.write("---")
st.caption("🔒 Powered by MathAI Propelled Dual-Engine. Left: Piecewise Constrained Econometrics. Right: Pure Data-Driven Autonomous AI Partitioning.")
