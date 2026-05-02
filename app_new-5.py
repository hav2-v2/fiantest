import streamlit as st
import pandas as pd
from datetime import datetime

try:
    from FinMind.data import DataLoader
except ImportError:
    st.error("環境初始化失敗，請檢查 requirements.txt")
    st.stop()

st.set_page_config(page_title="台股精準查詢", layout="wide")
st.title("📊 台股分鐘級股價查詢器")

with st.sidebar:
    st.header("1. 連線設定")
    raw_token = st.text_input("輸入 FinMind Token", type="password")
    st.divider()
    st.header("2. 查詢條件")
    stock_id = st.text_input("股票代號", value="2330").strip()
    select_date = st.date_input("日期", value=datetime.now())
    select_time = st.time_input("時間", value=datetime.strptime("09:30", "%H:%M").time())
    search_btn = st.button("開始查詢")

if search_btn:
    api_token = raw_token.strip() if raw_token else None
    
    if not api_token:
        st.warning("請在側邊欄輸入正確的 Token。")
    else:
        try:
            with st.spinner('正在與 FinMind 伺服器通訊...'):
                api = DataLoader()
                api.login_by_token(api_token=api_token)
                
                date_str = select_date.strftime('%Y-%m-%d')
                
                # --- 萬用抓取法：直接指定 dataset 名稱 ---
                # 這是 FinMind 最底層的抓取方式，能避開函式名稱錯誤
                df = api.get_data(
                    dataset="TaiwanStockPriceMinute",
                    data_id=stock_id,
                    start_date=date_str
                )
                # --------------------------------------
                
                if df is not None and not df.empty:
                    # 統一欄位名稱（確保不分大小寫）
                    df.columns = [c.lower() for c in df.columns]
                    df['date'] = pd.to_datetime(df['date'])
                    
                    target_dt = pd.to_datetime(f"{date_str} {select_time}")
                    
                    # 篩選
                    match = df[df['date'] <= target_dt].sort_values('date').iloc[-1:]
                    
                    if not match.empty:
                        row = match.iloc[0]
                        st.success(f"成功取得數據：{row['date'].strftime('%Y-%m-%d %H:%M')}")
                        
                        m1, m2, m3 = st.columns(3)
                        price = row.get('close', 0)
                        vol = row.get('volume', 0)
                        
                        m1.metric("當前成交價", f"{price} TWD")
                        m2.metric("成交量 (股)", f"{int(vol):,}")
                        # 成交金額通常在分鐘數據中指的是該分鐘的累計額
                        m3.metric("總成交金額", f"{int(price * vol):,}")
                        
                        st.dataframe(match, use_container_width=True)
                    else:
                        st.error("該時間點前無交易資料（台股開盤時間為 09:00 - 13:30）。")
                else:
                    st.error("查無資料。請確認日期是否為開盤日，或檢查 Token 權限。")

        except Exception as err:
            st.error(f"連線或資料處理錯誤：{err}")
