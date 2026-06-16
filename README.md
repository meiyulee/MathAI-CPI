# 🤖 MathAI-CPI: 美國通貨膨脹率雙引擎動態預測系統

<p align="center">
  <b>🌐 <a href="https://google.com">【 點此觀看：Live 互動式產品看板 (Google Sites) 】</a></b> 
  &nbsp;&nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;&nbsp;
  <b>🚀 <a href="https://streamlit.app">【 點此進入：Streamlit 雲端應用程式 】</a></b>
</p>


---

## 📌 專案概述 (Project Overview)
本專案為一獨立開發之生產級（Production-grade）總體經濟因子預測平台。傳統經濟學之計量迴歸往往受限於全樣本單一線性架構，在面臨結構性轉折或短期劇烈波動（如後疫情時代通膨）時容易失真。

**MathAI-CPI** 創新性地融合了**計量經濟學理論**與**非監督式資料驅動（Data-driven）演算法**，設計出雙軌預報引擎。本系統不僅能自動對接結構化總經數據庫，更具備全自動解析統計矩陣之能力，即時捕捉美國 CPI（消費者物價指數）年增率之短期趨勢拐點，為量化交易策略（Quantitative Trading）提供高信賴度的總經因子輸入。

👉 **[立即點此操作：Live 互動式產品看板](https://google.com)**

---

## 🚀 核心核心架構與技術特點 (Core Features)

### 1. 雙軌演算法引擎 (Dual-Engine Forecasting)
*   **外生限制短期趨勢內樣本 (Constrained Short-term Trend Engine)**：
    引入計量經濟學之外生控制限制（Exogenous Constraints），設定最小趨勢長度閾值，利用最小均方誤差（MSE）原則進行區間極致優化，剔除隨機雜訊，精準提煉歷史波動特徵。
*   **AI 自主進化版 (Unconstrained Data-driven Engine)**：
    移除一切人為外生假設，完全由非監督式 AI 演算法根據時間序列底層規律進行自主分段與拐點捕捉，實證自 2018 年起的結構性轉變中具備極高之靈敏度。

### 2. 生態化資料管線 (Data Pipeline & Engineering)
*   **多層級大數據解析**：系統可自動讀取包含多工作表（Multi-sheet）之複雜歷史數據庫，自動進行數據清洗（Data Cleaning）與型態強制轉換，保障運行之魯棒性（Robustness）。
*   **智慧統計矩陣提取**：採用進階**正則表達式（Regex）雷達**，全自動、倒序追蹤並精準提取各分頁 ANOVA 表中最新短期趨勢之解釋力（Short \(R^2\)）、整體模型解釋力（Overall \(R^2\)）與整體均方誤差（Overall MSE）。
*   **動態前端渲染**：捨棄傳統靜態報表，利用 `Plotly` 繪製高互動性金融圖表，將實際 CPI 散佈點與 MathAI 多線段短期預估實線完美重疊重合對照。

---

## 🏗️ 系統架構圖 (System Architecture)
```text
[FRED 大數據庫 / Excel DB] 
       │ (每月定時資料同步)
       ▼
[數據清洗與型態強制轉換管線]
       │
       ├──────────────────────────────────────────┐
       ▼ (引擎 A)                                 ▼ (引擎 B)
[外生限制短期趨勢優化 (MSE最小化)]         [AI 自主數據驅動分段演算法]
       │                                          │
       └────────────────────┬─────────────────────┘
                            ▼
               [進階正則表達式矩陣解析模組] ───► 自動提取 Short R² / Overall R² / MSE
                            │
                            ▼
               [Streamlit Cloud 生產級雲端主機]
                            │ (Websocket 實時動態穿透)
                            ▼
               [Google Sites 全球前端公開展示平台]
```

---

## 🛠️ 開發工具與環境配置 (Tech Stack)
*   **Core Logic & Data Science**: `Python 3.10+`, `Pandas`, `NumPy`, `OpenPyXL`
*   **Mathematical Regular Expressions**: `Re (Advanced Pattern Matching & Regex Parsing)`
*   **Data Visualization**: `Plotly (Dynamic Interactive Financial Charts)`
*   **Web Framework & Cloud Deployment**: `Streamlit`, `Streamlit Community Cloud`
*   **Web Integration**: `HTML5 / CSS3`, `Google Sites Platform`

---

## 📈 實證商業價值 (Business Value)
*   **量化交易因子輸入**：相較於傳統計量模型，本系統能提前 1-2 個月捕捉到通膨動態趨勢之拐點，提供宏觀量化策略（Macro Quant Strategies）絕佳的避險或多空訊號。
*   **自動化無人值守**：架構設計完美實現前後端分離，未來只需維持數據庫之規律追加，前端看板將全自動自適應更新，具備極高的軟體工程商業落地價值。

---

## 🧑‍💻 關於作者 (About the Author)
一位深耕於**計量經濟學邏輯與數據科學落地**的跨領域研究者。專長為總體經濟模型實證、時間序列機器學習演算法研發、以及量化金融因子工程。
*   **LinkedIn**: [點此建立專業聯繫](您的LinkedIn網址)
*   **Email**: [商務合作與技術交流](mailto:您的Email信箱)

---
*🔒 本倉庫所展示之程式碼為前端看板渲染與數據解析模組。MathAI 核心預估演算法引擎受智慧財產權保護，佈署並安全運行於後台安全伺服器。*
