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

# =================【關鍵核心優化】=================
# 篩選工作表：只保留純數字，且格式符合 YYYYMM 且 大於等於 202501 的工作表
model_sheets = []
for s in sheet_names:
    cleaned_name = str(s).strip()
    if cleaned_name.isdigit() and len(cleaned_name) == 6: # 確保是 6 碼數字 (如 202501)
        if int(cleaned_name) >= 202501:
            model_sheets.append(cleaned_name)

# 如果 Excel 命名習慣有斜線（如 2025/01），則改用這個容錯規則
if not model_sheets:
    for s in sheet_names:
        cleaned_name = re.sub(r'[^0-9]', '', str(s)) # 只留數字
        if len(cleaned_name) == 6 and int(cleaned_name) >= 202501:
            model_sheets.append(s)

# 如果真的找不到符合的分頁，就保留原本全部
if not model_sheets:
    model_sheets = [s for s in sheet_names if any(char.isdigit() for char in s)]
else:
    # 讓月份由新到舊排序（最新月份排在最上面，使用者體驗最好）
    model_sheets.sort(reverse=True)
# =================================================

# 3. 側邊控制面板
st.sidebar.header("🎛️ 模型參數選單")
# 這邊的選單將會非常乾淨，只從 2025 年 1 月開始讓使用者挑選！
selected_sheet = st.sidebar.selectbox("1. 選擇模型分析工作表 (月份)", model_sheets)
engine_type = st.sidebar.radio("2. 選擇 MathAI 核心引擎", ["傳統計量限制版", "AI 自主進化版 (從2018開始)"])

# 4. 根據選定的引擎進行欄位定位（保留完整數據不剪裁）
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

    # 格式轉換
    df_model[actual_col] = pd.to_numeric(df_model[actual_col], errors='coerce')
    df_model[estimate_col] = pd.to_numeric(df_model[estimate_col], errors='coerce')
    
    # 剔除空值，保留您的模型原本所有的歷史觀測區間（不截斷歷史數據）
    df_clean = df_model.dropna(subset=[actual_col, date_col]).copy()
    
    # 將日期格式化，支援 Timestamp 或文字日期
    try:
        df_clean['display_date'] = pd.to_datetime(df_clean[date_col], errors='coerce').dt.strftime('%Y-%m')
    except:
        df_clean['display_date'] = df_clean[date_col].astype(str)
        
    # 自動搜尋右側文字說明區，捕捉 R2 與 拐點警報
    text_block = ""
    if text_col in df_clean.columns:
        text_block = "".join(df_raw.iloc[:, 11 if "傳統" in engine_type else 30].dropna().astype(str).tolist())
        
    r2, is_new_trend = 0.0, False
    r2_match = re.search(r'R2\s*=\s*(\d+\.\d+)', text_block)
    if r2_match: r2 = float(r2_match.group(1))
    if "新趨勢" in text_block or "new line" in text_block.lower() or "sorting" in text_block.lower():
        is_new_trend = True
        
except Exception as e:
    st.error(f"❌ 數據載入失敗。請確認 Excel 欄位結構。錯誤: {e}")
    st.stop()

# 5. 智慧拐點警報顯示
if is_new_trend:
    st.error(f"🚨 **MathAI 趨勢拐點警報**：當前引擎已自動捕捉到動態趨勢轉折點！")
else:
    st.success(f"ℹ️ **當前模型狀態**：美國通膨數據在該區間內運作平穩。")

# 6. 繪製純淨單軸 Plotly 金融圖表
fig = go.Figure()

# 繪製真實 CPI 年增率歷史線
fig.add_trace(go.Scatter(
    x=df_clean['display_date'], y=df_clean[actual_col],
    mode='markers+lines', 
    name='FRED 實際 CPI 年增率 (%)',
    hovertemplate="<b>日期</b>: %{x}<br><b>實際年增率</b>: %{y}%<extra></extra>",
    line=dict(color='#2ca02c' if "AI" in engine_type else '#1f77b4', width=2),
    marker=dict(size=6)
))

# 繪製 MathAI 預測回歸線（直接採用 H 欄或 AB 欄）
df_est_clean = df_clean.dropna(subset=[estimate_col])
if not df_est_clean.empty:
    fig.add_trace(go.Scatter(
        x=df_est_clean['display_date'], y=df_est_clean[estimate_col],
        mode='lines', 
        name=f'MathAI {engine_label}預估值 (%)',
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
with col3: st.metric(label="📈 選單過濾機制", value="已鎖定 2025 年起之預報")

st.write("---")
st.caption("🔒 Powered by MathAI Propelled Dual-Engine. Dashboard workspace restricted from 2025-01 onwards.")
