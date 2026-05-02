import streamlit as st
import pandas as pd
from FinMind.data import DataLoader
from datetime import datetime

# 設定網頁標題
st.set_page_config(page_title="台股精準查詢工具", layout="centered")

st.title("📊 台股分鐘級股價查詢")
st.info("如果看到紅色錯誤，請嘗試重新整理網頁或更換瀏覽器。")

# --- 介面設計 ---
st.subheader("1. 設定連線資訊")
# 提供輸入框讓使用者輸入 Token，更靈活且安全
user_token = st.text_input("請輸入你的 FinMind Token", type="password", help="請至 FinMind 官網取得 Token")

st.subheader("2. 查詢參數")
col1, col2, col3 = st.columns(3)

with col1:
    stock_id = st.text_input("股票代號", value="2330")
with col2:
    select_date = st.date_input("選擇日期", value=datetime.now())
with col3:
    # 預設 09:30
    select_time = st.time_input("選擇時間", value=datetime.strptime("09:30", "%H:%M").time())

# --- 查詢邏輯 ---
if st.button("執行查詢", btn_label="search_button"):
    if not user_token:
        st.warning("請先輸入 Token 才能進行查詢。")
    else:
        try:
            with st.spinner('正在從 FinMind 伺服器抓取資料...'):
                api = DataLoader()
                api.login_by_token(api_token=user_token)
                
                # 轉為字串格式
                date_str = select_date.strftime('%Y-%m-%d')
                time_str = select_time.strftime('%H:%M:%S')
                
                # 抓取分 K 資料
                df = api.taiwan_stock_daily_minute(
                    stock_id=stock_id,
                    start_date=date_str
                )
                
                if df is not None and not df.empty:
                    # 格式化日期欄位
                    df['date'] = pd.to_datetime(df['date'])
                    target_dt = pd.to_datetime(f"{date_str} {time_str}")
                    
                    # 篩選最接近該時間的一筆資料
                    match_data = df[df['date'] <= target_dt].sort_values('date').iloc[-1:]
                    
                    if not match_data.empty:
                        st.success(f"查詢成功！資料時間：{match_data['date'].dt.strftime('%H:%M').values[0]}")
                        
                        # 呈現主要數據
                        res = match_data.iloc[0]
                        m1, m2, m3 = st.columns(3)
                        m1.metric("成交價", f"{res['close']} TWD")
                        m2.metric("成交量", f"{int(res['volume']):,} 股")
                        # 計算該分鐘內金額 (簡單估算：成交價 * 成交量)
                        amount = res['close'] * res['volume']
                        m3.metric("估計成交金額", f"{int(amount):,} TWD")
                        
                        st.write("### 詳細分時數據")
                        st.dataframe(match_data)
                    else:
                        st.error("該時間點前無資料，請確認是否為交易時間（09:00 - 13:30）。")
                else:
                    st.error("查無此日期的資料。請確認日期是否為開盤日，或股票代號是否正確。")
                    
        except Exception as e:
            st.error(f"程式執行出錯：{str(e)}")
            st.info("提示：如果出現 'tqdm' 錯誤，請確認 requirements.txt 是否包含 tqdm。")

