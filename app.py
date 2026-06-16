import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import re

# 1. 網頁基本設定
st.set_page_config(page_title="MathAI CPI Dual-Engine Forecast", layout="wide")

st.title("🤖 MathAI：美國通貨膨脹率雙引擎預測系統")
st.markdown("### 傳統經濟計量限制（左） vs. AI 數據自主分段進化（右）之實證看板")
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
st.sidebar.header("🎛️ 雙引擎模型參數選單")
selected_sheet = st.sidebar.selectbox("1. 選擇模型分析工作表 (月份)", model_sheets)
engine_type = st.sidebar.radio("2. 選擇 MathAI 核心引擎", ["傳統限制版 (一段至少8個月)", "AI 自主進化版 (無限制, 2018起)"])

# 4. 根據選定的引擎，進行完全獨立的 Excel 欄位定位
try:
    df_raw = pd.read_excel(excel_file, sheet_name=selected_sheet, skiprows=11)
    
    if "傳統" in engine_type:
        # 【傳統限制版】讀取 A-O 欄 (Index 0-14)
        df_model = df_raw.iloc[:, :15].copy()
        df_model.columns = [f"col_{i}" for i in range(df_model.shape[1])]
        
        date_col = "col_0"     # A欄：日期
        actual_col = "col_1"   # B欄：實際CPI原始指數
        estimate_col = "col_7" # H欄：估計值
        text_col = "col_9"     # J欄：文字描述區
        
        y_axis_left_title = "CPI 原始指數 (CPIAUCNS)"
        y_axis_right_title = "MathAI 傳統估計值 (%)"
        is_secondary = True    # 傳統版單位不同，需要雙 Y 軸
        
    else:
        # 【AI自主進化版】從 V 欄 (Index 21) 開始往後抓取 11 欄 (V 到 AF)
        df_model = df_raw.iloc[:, 21:32].copy()
        df_model.columns = [f"col_{i}" for i in range(df_model.shape[1])]
        
        date_col = "col_0"     # V欄：日期 (2018開始)
        actual_col = "col_2"   # X欄：CPI年增率實際值
        estimate_col = "col_6" # AB欄：進化版估計值
        text_col = "col_9"     # AE欄：文字描述區
        
        y_axis_left_title = "CPI 年增率 (%)"
        y_axis_right_title = "MathAI AI進化估計值 (%)"
        is_secondary = False   # 進化版兩者都是「年增率(%)」，共用單一 Y 軸最漂亮，不會錯配
        
    # 強制清洗與轉換格式
    df_model[actual_col] = pd.to_numeric(df_model[actual_col], errors='coerce')
    df_model[estimate_col] = pd.to_numeric(df_model[estimate_col], errors='coerce')
    df_clean = df_model.dropna(subset=[actual_col, date_col]).copy()
    
    # 全自動搜尋該區間的文字說明區，單純用來抓 R2 和 判定拐點警報
    text_block = ""
    if text_col in df_model.columns:
        text_block = "".join(df_model[text_col].dropna().astype(str).tolist())
    else:
        text_block = "".join(df_model.iloc[:, -2:].dropna().astype(str).tolist())
        
    r2, is_new_trend = 0.0, False
    r2_match = re.search(r'R2\s*=\s*(\d+\.\d+)', text_block)
    if r2_match: r2 = float(r2_match.group(1))
    if "新趨勢" in text_block or "new line" in text_block.lower() or "sorting" in text_block.lower():
        is_new_trend = True
        
except Exception as e:
    st.error(f"❌ 數據欄位解析失敗。請確認 Excel 結構是否與最新格式一致。錯誤: {e}")
    st.stop()

# 5. 智慧警報狀態顯示
if is_new_trend:
    st.error(f"🚨 **MathAI 趨勢拐點警報**：當前引擎已自動捕捉到動態趨勢轉折點！")
else:
    st.success(f"ℹ️ **當前模型狀態**：美國通膨數據在該區間內運作平穩。")

# 6. 建立專業金融圖表
fig = make_subplots(specs=[[{"secondary_y": True}]])
df_clean['formatted_date'] = df_clean[date_col].astype(str).apply(lambda x: x.split()[0] if ' ' in str(x) else str(x))

# 【繪製實際值藍點/綠點】
fig.add_trace(
    go.Scatter(
        x=df_clean['formatted_date'], y=df_clean[actual_col],
        mode='markers+lines', 
        name=f'FRED 實際值: {y_axis_left_title}',
        hovertemplate="<b>日期</b>: %{x}<br><b>實際值</b>: %{y}<extra></extra>",
        marker=dict(color='#1f77b4' if "傳統" in engine_type else '#2ca02c', size=6)
    ),
    secondary_y=False,
)

# 【繪製 MathAI 數學估計值紅線】
df_est_clean = df_clean.dropna(subset=[estimate_col])
if not df_est_clean.empty:
    fig.add_trace(
        go.Scatter(
            x=df_est_clean['formatted_date'], y=df_est_clean[estimate_col],
            mode='lines', 
            name=f'MathAI 估計值: {y_axis_right_title}',
            hovertemplate="<b>日期</b>: %{x}<br><b>MathAI 預估值</b>: %{y:.4f}%<extra></extra>",
            line=dict(color='#d62728', width=3, dash='dash' if "AI" in engine_type else 'solid')
        ),
        secondary_y=is_secondary, # 根據版本決定是否放到右側軸
    )

# 圖表外觀與雙座標軸標題調整
fig.update_layout(
    title=f"美國 CPI 趨勢分析對照圖 ({engine_type})",
    xaxis_title="觀測日期 (observation_date)",
    hovermode="x unified",
    template="plotly_white",
    legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.07)
)

fig.update_yaxes(title_text=f"<b>{y_axis_left_title}</b>", secondary_y=False)

if is_secondary:
    fig.update_yaxes(title_text=f"<b>{y_axis_right_title}</b>", secondary_y=True)
else:
    # 進化版不開右軸，保持隱藏，確保左右數值共用同個刻度
    fig.update_yaxes(visible=False, secondary_y=True)

st.plotly_chart(fig, use_container_width=True)

# 7. 呈現量化指標卡片
col1, col2, col3 = st.columns(3)
with col1: st.metric(label="📊 引擎自適應解釋力 (R²)", value=f"{r2:.4f}" if r2 != 0.0 else "由後台動態優化中")
with col2: st.metric(label="📊 本模組有效數據觀測樣本數", value=f"{len(df_clean)} 筆")
with col3: st.metric(label="📈 當前分析狀態", value="雙軌同步 Excel 直流數據")

st.write("---")
st.caption("🔒 Powered by MathAI Propelled Dual-Engine. Auto-switching between constrained economics and unconstrained data-driven columns.")
