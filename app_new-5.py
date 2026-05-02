import streamlit as st
import pandas as pd
from FinMind.data import DataLoader
from datetime import datetime

# 使用快取功能：同一天、同個 Token 的查詢結果會暫存在記憶體
@st.cache_data(ttl=3600)  # 快取 1 小時
def get_all_market_data(token, target_date):
    try:
        api = DataLoader()
        api.login_by_token(api_token=token)
        
        # 修正重點：明確傳入 data_id=""，解決 "can't be none" 的錯誤
        df = api.get_data(
            dataset="TaiwanStockTradingDailyReport",
            data_id="",  # 關鍵修正：傳入空字串代表抓取全市場
            start_date=target_date,
            end_date=target_date
        )
        
        if df is not None and not df.empty:
            df.columns = [c.lower() for c in df.columns]
            return df
        return None
    except Exception as e:
        # 將錯誤詳細資訊印出來，方便除錯
        st.error(f"FinMind API 回傳錯誤：{e}")
        return None

# --- Streamlit 介面 ---
st.title("🏛️ 台股全市場行情快速掃描")

# 側邊欄設定
with st.sidebar:
    st.header("1. 認證")
    token = st.text_input("輸入 FinMind Token", type="password").strip()
    st.header("2. 查詢設定")
    # 預設為昨天，因為當天盤後資料通常下午 4 點才齊全
    target_date = st.date_input("選擇交易日期", value=datetime(2026, 4, 30)) 
    fetch_btn = st.button("🚀 執行一鍵全市場抓取")

# 按鈕觸發邏輯
if fetch_btn:
    if not token:
        st.warning("請在左側欄輸入您的 FinMind Token。")
    else:
        date_str = target_date.strftime("%Y-%m-%d")
        with st.spinner(f"正在向 FinMind 請求 {date_str} 的全市場行情..."):
            df = get_all_market_data(token, date_str)
            
            if df is not None:
                st.success(f"抓取成功！共計 {len(df)} 檔股票資料。")
                
                # 簡單計算統計數據
                # 注意：spread 可能是字串或數值，視 API 版本而定，這裡做數值轉換確保正確
                df['spread'] = pd.to_numeric(df['spread'], errors='coerce')
                up_count = len(df[df['spread'] > 0])
                down_count = len(df[df['spread'] < 0])
                
                c1, c2, c3 = st.columns(3)
                c1.metric("今日上漲", f"{up_count} 家")
                c2.metric("今日下跌", f"{down_count} 家")
                c3.metric("資料總數", f"{len(df)} 檔")

                # 顯示資料表
                st.subheader("📋 完整行情清單")
                st.dataframe(df, use_container_width=True)
            else:
                st.info(f"【{date_str}】查無資料。請注意：\n1. 假日不開盤。\n2. 當日資料通常在 15:30 後才更新。")
