import streamlit as st
import pandas as pd
from FinMind.data import DataLoader
from datetime import datetime

# --- 初始化 DataLoader ---
def get_all_market_data(token, target_date):
    try:
        api = DataLoader()
        api.login_by_token(api_token=token)
        # 一次抓取當天全市場
        df = api.get_data(
            dataset="TaiwanStockTradingDailyReport",
            start_date=target_date,
            end_date=target_date
        )
        if df is not None and not df.empty:
            # 統一欄位名稱為小寫
            df.columns = [c.lower() for c in df.columns]
            return df
        return None
    except Exception as e:
        st.error(f"抓取失敗：{e}")
        return None

# --- Streamlit 介面 ---
st.title("🏛️ 台股全市場行情快速掃描")

with st.sidebar:
    token = st.text_input("輸入 FinMind Token", type="password").strip()
    target_date = st.date_input("選擇日期", value=datetime.now())
    fetch_btn = st.button("🚀 抓取全市場 (1800檔) 資料")

if fetch_btn:
    if not token:
        st.warning("請先輸入 Token")
    else:
        date_str = target_date.strftime("%Y-%m-%d")
        with st.spinner(f"正在掃描 {date_str} 全市場資料..."):
            df = get_all_market_data(token, date_str)
            
            if df is not None:
                # 簡單的數據統計
                total_count = len(df)
                up_count = len(df[df['spread'] > 0])
                down_count = len(df[df['spread'] < 0])
                unchanged_count = len(df[df['spread'] == 0])

                st.success(f"抓取成功！共計 {total_count} 筆資料。")
                
                # 顯示儀表板亮點
                c1, c2, c3 = st.columns(3)
                c1.metric("今日上漲", f"{up_count} 家", delta_color="normal")
                c2.metric("今日下跌", f"{down_count} 家", delta="-", delta_color="inverse")
                c3.metric("平盤/未成交", f"{unchanged_count} 家")

                # 顯示前 10 大成交量股票 (選用功能)
                st.subheader("🔥 今日成交量 Top 10")
                top_volume = df.sort_values('trading_volume', ascending=False).head(10)
                st.table(top_volume[['stock_id', 'stock_name', 'close', 'spread', 'trading_volume']])

                # 顯示完整資料表
                st.subheader("📋 全市場完整清單")
                st.dataframe(df, use_container_width=True)
                
                # 提供下載按鈕 (CSV)
                csv = df.to_csv(index=False).encode('utf-8-sig')
                st.download_button(
                    label="📥 下載全市場 CSV 檔",
                    data=csv,
                    file_name=f"Taiwan_Market_{date_str}.csv",
                    mime="text/csv",
                )
            else:
                st.error("該日期無資料 (可能是非交易日或資料尚未更新)")
