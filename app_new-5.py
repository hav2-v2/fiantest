import streamlit as st
import pandas as pd
from datetime import datetime

# 嘗試匯入套件
try:
    from FinMind.data import DataLoader
except ImportError:
    st.error("缺少 FinMind 套件，請檢查 requirements.txt")
    st.stop()

st.set_page_config(page_title="台股精準查詢", layout="wide")

st.title("📊 台股分鐘級股價查詢器")

with st.sidebar:
    st.header("1. 設定")
    api_token = st.text_input("輸入 FinMind Token", type="password")
    st.divider()
    st.header("2. 查詢條件")
    stock_id = st.text_input("股票代號", value="2330")
    select_date = st.date_input("日期", value=datetime.now())
    select_time = st.time_input("時間", value=datetime.strptime("09:30", "%H:%M").time())
    search_btn = st.button("開始查詢")

if search_btn:
    if not api_token:
        st.warning("請在側邊欄輸入你的 Token。")
    else:
        try:
            with st.spinner('正在獲取數據...'):
                api = DataLoader()
                api.login_by_token(api_token=api_token)
                
                # --- 修正處：函數名稱改為 taiwan_stock_price_minute ---
                df = api.taiwan_stock_price_minute(
                    stock_id=stock_id,
                    start_date=select_date.strftime('%Y-%m-%d')
                )
                # --------------------------------------------------
                
                if df is not None and not df.empty:
                    # 處理日期與篩選
                    df['date'] = pd.to_datetime(df['date'])
                    target_dt = pd.to_datetime(f"{select_date} {select_time}")
                    
                    # 取得該時刻或最接近該時刻的前一筆資料
                    match = df[df['date'] <= target_dt].sort_values('date').iloc[-1:]
                    
                    if not match.empty:
                        row = match.iloc[0]
                        st.success(f"資料時間：{row['date'].strftime('%Y-%m-%d %H:%M')}")
                        
                        c1, c2, c3 = st.columns(3)
                        # price 資料集中通常是 Close 價格
                        price = row.get('close', row.get('Close', 0))
                        vol = row.get('volume', row.get('Volume', 0))
                        
                        c1.metric("成交價", f"{price} TWD")
                        c2.metric("成交量", f"{int(vol):,} 股")
                        c3.metric("估計成交額", f"{int(price * vol):,} TWD")
                        
                        st.dataframe(match, use_container_width=True)
                    else:
                        st.error("該時間點前無資料，請確認是否為交易時間。")
                else:
                    st.error("查無資料，請確認日期是否為開盤日（或 Token 是否正確）。")
        except Exception as err:
            st.error(f"執行錯誤：{err}")
