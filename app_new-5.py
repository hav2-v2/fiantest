import streamlit as st
import pandas as pd
from datetime import datetime

# 嘗試匯入套件，並給予明確報錯提示
try:
    from FinMind.data import DataLoader
    import tqdm
except ImportError as e:
    st.error(f"環境初始化失敗：缺少套件 {e.name}。請確認 requirements.txt 是否包含該套件。")
    st.stop()

st.set_page_config(page_title="台股精準查詢", layout="wide")

# --- 介面 ---
st.title("📊 台股分鐘級股價查詢器")

# 在側邊欄放置 Token 輸入框，確保隱私與彈性
with st.sidebar:
    st.header("1. 設定")
    api_token = st.text_input("輸入 FinMind Token", type="password")
    st.divider()
    st.header("2. 查詢條件")
    stock_id = st.text_input("股票代號", value="2330")
    select_date = st.date_input("日期", value=datetime.now())
    select_time = st.time_input("時間", value=datetime.strptime("09:30", "%H:%M").time())
    search_btn = st.button("開始查詢")

# --- 邏輯 ---
if search_btn:
    if not api_token:
        st.warning("請在側邊欄輸入你的 Token。")
    else:
        try:
            with st.spinner('正在獲取數據...'):
                api = DataLoader()
                api.login_by_token(api_token=api_token)
                
                # 抓取分K資料
                df = api.taiwan_stock_daily_minute(
                    stock_id=stock_id,
                    start_date=select_date.strftime('%Y-%m-%d')
                )
                
                if df is not None and not df.empty:
                    df['date'] = pd.to_datetime(df['date'])
                    target_dt = pd.to_datetime(f"{select_date} {select_time}")
                    
                    # 篩選最接近該時間的一筆
                    match = df[df['date'] <= target_dt].sort_values('date').iloc[-1:]
                    
                    if not match.empty:
                        row = match.iloc[0]
                        st.success(f"資料時間：{row['date'].strftime('%Y-%m-%d %H:%M')}")
                        
                        c1, c2, c3 = st.columns(3)
                        c1.metric("成交價", f"{row['close']} TWD")
                        c2.metric("成交量", f"{int(row['volume']):,} 股")
                        c3.metric("成交金額", f"{int(row['close'] * row['volume']):,} TWD")
                        
                        st.dataframe(match, use_container_width=True)
                    else:
                        st.error("該時段尚未開盤或無交易資料。")
                else:
                    st.error("查無資料，請確認日期是否為開盤日。")
        except Exception as err:
            st.error(f"執行錯誤：{err}")
