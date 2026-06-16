import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import re

# 1. 網頁頁面配置
st.set_page_config(page_title="MathAI PCE Forecast", layout="wide")

st.html("""
    <style>
        .block-container { padding-top: 4.5rem !important; padding-bottom: 2rem !important; }
        .main-title { font-size: 26px !important; font-weight: 700 !important; color: #1E293B !important; margin-bottom: 8px !important; }
        .sub-title { font-size: 15px !important; font-weight: 500 !important; color: #64748B !important; margin-bottom: 15px !important; }
    </style>
""")

st.html('<div class="main-title">📊 MathAI：美國 PCE 物價指數預測系統</div>')
st.html('<div class="sub-title">純資料驅動：AI 數據自主分段進化引擎（自 2018 年 1 月起始）</div>')
st.write("---")

# 2. 自動讀取 PCE Excel 檔案
@st.cache_data
def load_excel_data():
    excel_file = "PCE_data.xlsx"
    try:
        excel_obj = pd.ExcelFile(excel_file)
        return excel_obj.sheet_names, excel_file
    except Exception as e:
        st.error(f"❌ 找不到您的 Excel 檔案，請確認您的 Excel 檔名是否為 PCE_data.xlsx。錯誤: {e}")
        st.stop()

sheet_names, excel_file = load_excel_data()

# 篩選工作表：只保留大於等於 202501 的月份，且自動跳過缺失的 202601
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

# 4. 精準字母定位（完全根據 PCE 實測結構，從 A 欄起始對接）
try:
    df_raw = pd.read_excel(excel_file, sheet_name=selected_sheet, skiprows=11)
    
    alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    extended_cols = list(alphabet) + [f"A{char}" for char in alphabet]
    col_mapping = {extended_cols[idx]: col_name for idx, col_name in enumerate(df_raw.columns) if idx < len(extended_cols)}

    # 🚀 根據您的最新截圖，精準綁定絕對字母座標
    date_col = col_mapping.get("A")       # A 欄：日期 (2018-01開始)
    x_index_col = col_mapping.get("C")     # C 欄：時間代號
    actual_col = col_mapping.get("G")     # G 欄：PCE物價指數年增率原始值
    estimate_col = col_mapping.get("H")   # H 欄：估計值
    text_col = col_mapping.get("I")       # I 欄：數據分析結果與 ANOVA 文字區

    if not date_col or not actual_col or not estimate_col:
        st.error("❌ 找不到對應的 Excel 欄位字母（A, G, H），請檢查 Excel 結構。")
        st.stop()

    df_clean = pd.DataFrame({
        'Date': df_raw[date_col],
        'Actual': pd.to_numeric(df_raw[actual_col], errors='coerce'),
        'Estimate': pd.to_numeric(df_raw[estimate_col], errors='coerce'),
        'X_Idx': pd.to_numeric(df_raw[x_index_col], errors='coerce')
    }).dropna(subset=['Actual', 'Date']).copy()
    
    df_clean['display_date'] = pd.to_datetime(df_clean['Date'], errors='coerce').dt.strftime('%Y-%m')
        
    # === 🎯 統計指標精準動態提取與容錯演算法 ===
    short_r2 = None
    overall_r2 = None
    overall_mse = None
    is_new_trend = False
    lines_found = []
    
    if text_col and text_col in df_raw.columns:
        text_list = df_raw[text_col].fillna("").astype(str).tolist()
        text_block = " ".join(text_list)
        
        # 1. 提取最新短期趨勢 R²
        r2_matches = re.findall(r'(?:R2|R\^2|R_2)\s*=\s*(-?\d+\.?\d*(?:[eE][-+]?\d+)?)', text_block, re.IGNORECASE)
        if r2_matches: short_r2 = float(r2_matches[-1])
            
        if "新趨勢" in text_block or "new line" in text_block.lower():
            is_new_trend = True

        # 2. 盲抓文字區中的公式參數（用來精準對齊轉折點）
        formula_matches = re.findall(r'Y\s*=\s*(-?\d+\.\d+)\s*([-+]\s*\d+\.\d+)\s*\*?\s*X', text_block, re.IGNORECASE)
        for f in formula_matches:
            lines_found.append({'beta0': float(f), 'beta1': float(f.replace(" ", ""))})

        # 3. 提取整體模型指標 (動態相容 202506 之後才產生的 ANOVA 區塊)
        for i in range(len(text_list) - 1, -1, -1):
            val_str = text_list[i].strip()
            if "error" in val_str.lower() or "殘差" in val_str:
                try:
                    row_chunk = " ".join(text_list[i:i+5])
                    mse_matches = re.findall(r'0\.\d+', row_chunk)
                    if mse_matches: overall_mse = float(mse_matches)
                except: pass
            if re.match(r'^0\.\d+$', val_str) and overall_r2 is None:
                try:
                    val_num = float(val_str)
                    if 0.5 <= val_num < 1.0: overall_r2 = val_num
                except: pass

except Exception as e:
    st.error(f"❌ 數據與 ANOVA 指標提取失敗。請檢查 Excel 結構。錯誤: {e}")
    st.stop()

if is_new_trend:
    st.error(f"🚨 **MathAI 趨勢拐點警報**：系統已自動捕捉到動態趨勢轉折點！")
else:
    st.success(f"ℹ️ **當前模型狀態**：美國 PCE 數據在該區間內運作平穩。")

# 6. 繪製純淨單軸 Plotly 金融圖表
fig = go.Figure()

# FRED 實際年增率（純點，綠色）
fig.add_trace(go.Scatter(
    x=df_clean['display_date'], y=df_clean['Actual'],
    mode='markers', 
    name='FRED 實際 PCE 年增率 (%)',
    hovertemplate="<b>日期</b>: %{x}<br><b>實際年增率</b>: %{y}%<extra></extra>",
    marker=dict(color='#2ca02c', size=6, opacity=0.7)
))

# MathAI 精準多線段短期趨勢預估值（實線穿透）
df_est_clean = df_clean.dropna(subset=['Estimate']).copy()
if not df_est_clean.empty:
    fig.add_trace(go.Scatter(
        x=df_est_clean['display_date'], y=df_est_clean['Estimate'],
        mode='lines', 
        name='MathAI 精準多線段短期趨勢預估值 (%)',
        hovertemplate="<b>日期</b>: %{x}<br><b>MathAI 預估值</b>: %{y:.4f}%<extra></extra>",
        line=dict(color='#d62728', width=3)
    ))

    # === 🚨 【EconTech 核心演算優化：後台公式自動比對精準定位最新線段起點】 ===
    if is_new_trend and len(lines_found) > 0 and 'X_Idx' in df_est_clean.columns:
        try:
            latest_line = lines_found[-1]
            b0, b1 = latest_line['beta0'], latest_line['beta1']
            df_est_clean['pure_latest_y'] = b0 + b1 * df_est_clean['X_Idx']
            df_est_clean['diff'] = abs(df_est_clean['Estimate'] - df_est_clean['pure_latest_y'])
            df_latest_segment = df_est_clean[df_est_clean['diff'] < 1e-4]
            
            if not df_latest_segment.empty:
                break_date = str(df_latest_segment['display_date'].iloc)
                break_val = float(df_latest_segment['Estimate'].iloc)
                
                fig.add_vline(x=break_date, line_width=1.5, line_dash="dash", line_color="#475569")
                fig.add_annotation(
                    x=break_date, y=break_val, text="🚨 MathAI 內生趨勢轉折拐點",
                    showarrow=True, arrowhead=2, arrowcolor="#d62728", arrowsize=1, arrowwidth=2,
                    ax=0, ay=-40, bordercolor="#d62728", borderwidth=1, borderpad=4, bgcolor="#FEF2F2", opacity=0.95
                )
        except:
            pass

fig.update_layout(
    title=f"美國 PCE 年增率與 MathAI 預測趨勢對照圖 (當前分析月份: {selected_sheet})",
    xaxis_title="觀測日期 (YYYY-MM)", yaxis_title="個人消費支出物價年增率 (%)",
    hovermode="x unified", template="plotly_white",
    legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.02), margin=dict(t=10, b=10)
)
st.plotly_chart(fig, use_container_width=True)

# 7. 呈現量化指標卡片 (加入 2025/06 歷史分頁無 ANOVA 之自動文字相容機制)
col1, col2, col3 = st.columns(3)
with col1: 
    st.metric(
        label="📊 短期趨勢解釋力 (Short R²)", 
        value=f"{short_r2:.6f}" if short_r2 is not None else "未紀錄此指標"
    )
with col2: 
    st.metric(
        label="🏛️ 模型整體解釋力 (Overall R²)", 
        value=f"{overall_r2:.6f}" if overall_r2 is not None else "2025/06起提供"
    )
with col3: 
    st.metric(
        label="📐 模型整體均方誤差 (Overall MSE)", 
        value=f"{overall_mse:.6f}" if overall_mse is not None else "2025/06起提供"
    )

st.write("---")
st.caption("🔒 Powered by MathAI Propelled Unconstrained Autonomous Evolution Engine. Explicitly mapping A to I column schema.")
