import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import re

# 1. 網頁頁面配置
st.set_page_config(page_title="MathAI CPI Forecast", layout="wide")

st.title("🤖 MathAI：美國通貨膨脹率預測系統")
st.markdown("### 外生限制短期趨勢引擎 vs. AI 數據自主分段進化引擎")
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

# 篩選工作表：只保留大於等於 202501 的月份
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

# 完美更新為您指定的專業學術名稱
engine_type = st.sidebar.radio("2. 選擇 MathAI 核心引擎", ["外生限制短期趨勢內樣本", "AI 自主進化版 (從2018開始)"])

# 4. 精準字母定位核心 (完全根據您的指定對接欄位)
try:
    # 讀取完整 Excel，不預先切欄位
    df_raw = pd.read_excel(excel_file, sheet_name=selected_sheet, skiprows=11)
    
    # 建立一個從 A 開始的字母索引表，用來精準對接
    alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    extended_cols = list(alphabet) + [f"A{char}" for char in alphabet] # 生成 A-Z, AA-AZ
    
    # 將 Excel 的欄位名稱強制定對應到它的英文字母標籤
    col_mapping = {}
    for idx, col_name in enumerate(df_raw.columns):
        if idx < len(extended_cols):
            col_mapping[extended_cols[idx]] = col_name

    # 根據選定的引擎，抓取您指定的絕對字母欄位
    if "外生" in engine_type:
        date_col = col_mapping.get("A")   # A 欄：日期
        actual_col = col_mapping.get("G") # G 欄：CPI 年增率原始值
        estimate_col = col_mapping.get("H") # H 欄：估計值
        text_col = col_mapping.get("J")   # J 欄：文字說明區
        engine_label = "外生限制短期趨勢"
    else:
        date_col = col_mapping.get("V")   # V 欄：日期 (2018開始)
        actual_col = col_mapping.get("AA") # AA 欄：CPI 年增率原始值
        estimate_col = col_mapping.get("AB") # AB 欄：估計值
        text_col = col_mapping.get("AE")  # AE 欄：文字說明區
        engine_label = "AI自主進化"

    if not date_col or not actual_col or not estimate_col:
        st.error("❌ 找不到對應的 Excel 欄位字母（A, G, H 或 V, AA, AB），請檢查 Excel 結構。")
        st.stop()

    # 建立乾淨的繪圖資料集
    df_clean = pd.DataFrame({
        'Date': df_raw[date_col],
        'Actual': pd.to_numeric(df_raw[actual_col], errors='coerce'),
        'Estimate': pd.to_numeric(df_raw[estimate_col], errors='coerce')
    })
    
    # 剔除實際值為空值的列
    df_clean = df_clean.dropna(subset=['Actual', 'Date']).copy()
    
    # 格式化 X 軸日期顯示 (YYYY-MM)
    try:
        df_clean['display_date'] = pd.to_datetime(df_clean['Date'], errors='coerce').dt.strftime('%Y-%m')
    except:
        df_clean['display_date'] = df_clean['Date'].astype(str)
        
    # 自動從指定的文字欄抓取 R2 與 智慧拐點警報
    r2, is_new_trend = 0.0, False
    if text_col and text_col in df_raw.columns:
        text_block = "".join(df_raw[text_col].dropna().astype(str).tolist())
        r2_match = re.search(r'R2\s*=\s*(\d+\.\d+)', text_block)
        if r2_match: r2 = float(r2_match.group(1))
        if "新趨勢" in text_block or "new line" in text_block.lower():
            is_new_trend = True
            
except Exception as e:
    st.error(f"❌ 數據載入失敗。請確認 Excel 欄位標籤與結構。錯誤: {e}")
    st.stop()

# 5. 智慧拐點警報顯示
if is_new_trend:
    st.error(f"🚨 **MathAI 趨勢拐點警報**：當前引擎已自動捕捉到動態趨勢轉折點！")
else:
    st.success(f"ℹ️ **當前模型狀態**：美國通膨數據在該區間內運作平穩。")

# 6. 繪製純淨單軸 Plotly 金融圖表
fig = go.Figure()

# FRED 實際年增率（純點，無連線）
fig.add_trace(go.Scatter(
    x=df_clean['display_date'], y=df_clean['Actual'],
    mode='markers', 
    name='FRED 實際 CPI 年增率 (%)',
    hovertemplate="<b>日期</b>: %{x}<br><b>實際年增率</b>: %{y}%<extra></extra>",
    marker=dict(color='#2ca02c' if "AI" in engine_type else '#1f77b4', size=6, opacity=0.7)
))

# MathAI 精準多線段短期趨勢預估值（實線穿透）
df_est_clean = df_clean.dropna(subset=['Estimate'])
if not df_est_clean.empty:
    fig.add_trace(go.Scatter(
        x=df_est_clean['display_date'], y=df_est_clean['Estimate'],
        mode='lines', 
        name='MathAI 精準多線段短期趨勢預估值 (%)',
        hovertemplate="<b>日期</b>: %{x}<br><b>MathAI 預估值</b>: %{y:.4f}%<extra></extra>",
        line=dict(color='#d62728', width=3, dash='dash' if "AI" in engine_type else 'solid')
    ))

# 圖表外觀配置
fig.update_layout(
    title=f"美國 CPI 年增率與 MathAI 預測趨勢對照圖 (當前分析月份: {selected_sheet})",
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
with col2: st.metric(label="📅 當前分析樣本數", value=f"{len(df_clean)} 筆資料")
with col3: st.metric(label="📈 預報選單範圍", value="2025 年 1 月起")

st.write("---")
st.caption("🔒 Powered by MathAI Propelled Dual-Engine. Explicit grid-letter indexing architecture.")
