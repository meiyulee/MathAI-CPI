import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import re

# 1. 網頁頁面配置
st.set_page_config(page_title="MathAI CPI Forecast", layout="wide")

st.title("🤖 MathAI：美國通貨膨脹率預測系統")
st.markdown("### 經濟計量多線段限制引擎 vs. AI 數據自主分段進化引擎")
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
engine_type = st.sidebar.radio("2. 選擇 MathAI 核心引擎", ["計量限制版", "AI 自主進化版 (從2018開始)"])

# 4. 智慧動態對齊核心
try:
    # 讀取完整工作表（先不切欄位，保留原始標題列）
    df_raw = pd.read_excel(excel_file, sheet_name=selected_sheet, skiprows=11)
    
    # 根據選擇的引擎，切出左半邊或右半邊
    if "計量" in engine_type:
        df_block = df_raw.iloc[:, :15].copy()  # 左側 A-O 欄
        text_col_idx = 11  # 預設文字在 L 欄附近
    else:
        df_block = df_raw.iloc[:, 21:].copy()   # 右側 V 欄往後所有欄位
        text_col_idx = -1  # 預設文字在最後面
        
    # 清理欄位名稱去除前後空格
    df_block.columns = [str(c).strip() for c in df_block.columns]
    raw_cols = list(df_block.columns)
    
    # 初始化定位變數
    date_col, actual_col, estimate_col = None, None, None
    
    # === 🛑 智慧全自動模糊搜尋欄位 ===
    # 1. 找日期欄 (通常是第 1 欄，或包含 date, 日期)
    for c in raw_cols:
        if "date" in c.lower() or "日期" in c:
            date_col = c
            break
    if not date_col: date_col = raw_cols[0]
    
    # 2. 找實際值欄 (包含 CPI, 年增率, 原始值)
    for c in raw_cols:
        if c != date_col and any(k in c.lower() for k in ["cpi", "年增率", "原始", "actual"]):
            actual_col = c
            break
    # 容錯：如果是傳統限制版，強制對接第 7 欄(G欄); 進化版對接第 6 欄(AA欄)
    if not actual_col:
        actual_col = raw_cols[6] if "計量" in engine_type else raw_cols[5]

    # 3. 找估計值欄 (包含 估計, 預估, estimate, 或是 H欄/AB欄位置)
    for c in raw_cols:
        if c not in [date_col, actual_col] and any(k in c.lower() for k in ["估計", "預估", "estimate", "predict"]):
            estimate_col = c
            break
    if not estimate_col:
        estimate_col = raw_cols[7] if "計量" in engine_type else raw_cols[6]
    # ==================================

    # 數據清洗
    df_block[actual_col] = pd.to_numeric(df_block[actual_col], errors='coerce')
    df_block[estimate_col] = pd.to_numeric(df_block[estimate_col], errors='coerce')
    df_clean = df_block.dropna(subset=[actual_col, date_col]).copy()
    
    # 格式化日期 X 軸
    try:
        df_clean['display_date'] = pd.to_datetime(df_clean[date_col], errors='coerce').dt.strftime('%Y-%m')
    except:
        df_clean['display_date'] = df_clean[date_col].astype(str)
        
    # 自動捕捉 R2
    text_block = "".join(df_block.iloc[:, text_col_idx].dropna().astype(str).tolist()) if df_block.shape[1] > 2 else ""
    r2, is_new_trend = 0.0, False
    r2_match = re.search(r'R2\s*=\s*(\d+\.\d+)', text_block)
    if r2_match: r2 = float(r2_match.group(1))
    if "新趨勢" in text_block or "new line" in text_block.lower():
        is_new_trend = True
        
except Exception as e:
    st.error(f"❌ 欄位自動對齊失敗。請確認 Excel 欄位結構。錯誤: {e}")
    st.stop()

# 5. 智慧拐點警報顯示
if is_new_trend:
    st.error(f"🚨 **MathAI 趨勢拐點警報**：當前引擎已自動捕捉到動態趨勢轉折點！")
else:
    st.success(f"ℹ️ **當前模型狀態**：美國通膨數據在該區間內運作平穩。")

# 6. 繪製純淨 Plotly 金融圖表
fig = go.Figure()

# FRED 實際年增率（純點）
fig.add_trace(go.Scatter(
    x=df_clean['display_date'], y=df_clean[actual_col],
    mode='markers', 
    name='FRED 實際 CPI 年增率 (%)',
    hovertemplate="<b>日期</b>: %{x}<br><b>實際年增率</b>: %{y}%<extra></extra>",
    marker=dict(color='#2ca02c' if "AI" in engine_type else '#1f77b4', size=6, opacity=0.7)
))

# MathAI 預估實線
df_est_clean = df_clean.dropna(subset=[estimate_col])
if not df_est_clean.empty:
    fig.add_trace(go.Scatter(
        x=df_est_clean['display_date'], y=df_est_clean[estimate_col],
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
st.caption("🔒 Powered by MathAI Propelled Dual-Engine. Auto-aligning dynamic columns.")
