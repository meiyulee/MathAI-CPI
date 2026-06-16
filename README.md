# 🤖 MathAI-CPI: 美國通貨膨脹率雙引擎動態預測系統

<p align="center">
  <b>🌐 <a href="https://sites.google.com/view/usinflation/">【 點此觀看：Live 互動式產品看板 (Google Sites) 】</a></b> 
  &nbsp;&nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;&nbsp;
  <b>🚀 <a href="https://mathai-cpi-dynamicplot.streamlit.app/">【 點此進入：Streamlit 雲端應用程式 】</a></b>
</p>

---

## 📌 專案概述 (Project Overview)
本專案為 **MathAI (Symbolic Mathematics & Computation Engine)** 在量化金融與宏觀因子預測領域的生產級（Production-grade）延伸應用。

系統之核心方法論與優化判斷原則，完全建立在 **SCIE 國際權威期刊之嚴謹數學論證** 之上：
> Lin, Y. S., Fan, C. P.*, Lee, M. Y., & Lee, Y. H. (2026). Mathematical Computation of Piecewise Linear Regression with Endogenous Segmentation for Accurate Data-Based Model Building: An Example of the Phillips Curve. *Mathematics*, 14(6), 1041. (SCIE, IF=2.2). [[https://doi.org](https://doi.org/10.3390/math14061041)]

**💡 本專案之創新工程轉型 (Academic-to-Industry Engineering Transition)：**
原論文聚焦於雙總經指標空間（如非線性菲利浦曲線）之內生分段優化。本專案將其**創新演進為以「時間代號 (Time Variable)」為自變數的動態時間序列分析**。

所有核心計量經濟數據分析與轉折點捕捉，皆由自研之 **MathAI 核心運算引擎** 獨立完成。後台再透過 Python 管道自動對接美國 FRED 數據庫、同步提取 ANOVA 統計矩陣，即時輸出美國 CPI 年增率之短期趨勢拐點，為量化交易策略（Quantitative Trading）提供高信賴度的總經因子輸入。

---

## 🚀 核心架構與技術特點 (Core Features)

### 1. 基於 SCIE 論文原則之雙軌預報引擎 (Dual-Engine System)
*   **外生限制短期趨勢內樣本 (Constrained Short-term Trend Engine)**：
    完全依循論文方法論之優化控制原則，引入計量經濟學之外生控制限制（如設定最小趨勢長度閾值），由 MathAI 利用最小均方誤差（MSE）原則進行區間極致優化，精準提煉歷史波動特徵。
*   **AI 自主進化版 (Unconstrained Endogenous Segmentation Engine)**：
    **完全落地 2026 年 Mathematics 期刊論文之「內生分段（Endogenous Segmentation）」核心公式**。移除一切人為外生假設，完全由 MathAI 運算引擎根據時間序列底層矩陣進行自主最佳化分段，實證在結構性轉變中具備極高之靈敏度。

### 2. 生態化資料管線與自動化指標提取 (Data Pipeline)
*   **多層級數據解析管線**：後台利用 Python 自動讀取包含多工作表（Multi-sheet）之 Excel 歷史數據庫，並自動進行數據清洗（Data Cleaning）與型態強制轉換，保障系統運行之魯棒性。
*   **論文規則自適應同步**：系統根據論文設定之判斷原則，全自動、倒序追蹤並精準提取各分頁 ANOVA 表中最新短期趨勢之解釋力（Short \(R^2\)）、整體模型解釋力（Overall \(R^2\)）與整體均方誤差（Overall MSE），實現完全去固定值的全動態指標串流。
*   **互動式金融渲染**：利用 `Plotly` 繪製高互動性金融圖表，將實際 CPI 散佈點（純點模式）與 MathAI 數學式計算出之多線段短期預估實線完美重疊對照。

---

## 🏗️ 系統架構圖 (System Architecture)
```text
[FRED 大數據庫 / Excel DB] 
       │ (每月定時資料同步)
       ▼
[數據清洗與型態強制轉換管線]
       │
       ├──────────────────────────────────────────┐
       ▼ (引擎 A: 外生控制原則)               ▼ (引擎 B: 2026 SCIE 論文核心方法論)
[MathAI 外生限制短期趨勢優化計算]         [MathAI 內生分段演算法 (時間自變數轉型)]
       │                                          │
       └────────────────────┬─────────────────────┘
                            ▼
               [論文統計指標自適應對齊模組] ───► 自動提取 Short R² / Overall R² / MSE
                            │
                            ▼
               [Streamlit Cloud 生產級雲端主機]
                            │ (Websocket 實時動態穿透)
                            ▼
               [Google Sites 全球前端公開展示平台]
```

---

## 🛠️ 開發工具與環境配置 (Tech Stack)
*   **Core Mathematical Computation Engine**: **[MathAI (自研符號數學與計量分析引擎)](https://github.com/meiyulee/MathAI)**
*   **Data Pipeline & Automation**: `Python 3.10+`, `Pandas`, `NumPy`, `OpenPyXL`
*   **Data Visualization**: `Plotly (Dynamic Interactive Financial Charts)`
*   **Web Framework & Cloud Deployment**: `Streamlit`, `Streamlit Community Cloud`
*   **Web Integration**: `HTML5 / CSS3`, `Google Sites Platform`

---

## 📈 實證商業價值 (Business Value)
*   **量化交易因子輸入**：相較於傳統單一迴規模型，本系統能依據 2026 SCIE 期刊證實之數學最優化路徑，由 MathAI 提前捕捉到通膨動態趨勢之拐點，提供宏觀量化策略絕佳的避險訊號。
*   **自動化無人值守**：架構設計完美實現前後端分離，未來只需維持數據庫之規律追加，前端看板將全自動自適應更新，具備極高的軟體工程商業落地價值。

---

## 🧑‍💻 關於作者 (About the Author)
一位深耕於**計量經濟學邏輯與數據科學落地**的跨領域研究者。專長為總體經濟模型實證、時間序列機器學習演算法研發、以及量化金融因子工程。
*   **Messenger**: [點此建立專業聯繫](https://m.me/116876593050551)
*   **Email**: [商務合作、教學與技術應用](mailto:phoebus9168@gmail.com)

---
*🔒 本倉庫所展示之程式碼為前端看板渲染與數據解析模組。MathAI 核心預估演算法引擎（基於 2026 Mathematics 發表之學術結晶）受智慧財產權保護，佈署並安全運行於後台伺服器。*
