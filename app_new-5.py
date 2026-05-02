import streamlit as st
import pandas as pd
from datetime import datetime

try:
    from FinMind.data import DataLoader
except ImportError:
    st.error("環境初始化失敗，請檢查 requirements.txt 是否包含 FinMind")
    st.stop()

st.set_page_config(page_title="台股分鐘查詢器", layout="wide")
st.title("📊 台股分鐘級 K 線查詢 (KBar)")

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
            with st.spinner('正在從 TaiwanStockKBar 獲取數據...'):
                api = DataLoader()
                api.login_by_token(api_token=api_token)
                
                date_str = select_date.strftime('%Y-%m-%d')
                
                # --- 根據錯誤訊息修正：使用 TaiwanStockKBar ---
                df = api.get_data(
                    dataset="TaiwanStockKBar",
                    data_id=stock_id,
                    start_date=date_str,
                    end_date=date_str  # 限制在當天
                )
                
                if df is not None and not df.empty:
                    # 統一轉小寫以利處理
                    df.columns = [c.lower() for c in df.columns]
                    
                    # FinMind KBar 的時間欄位通常叫 date
                    df['date'] = pd.to_datetime(df['date'])
                    
                    target_dt = pd.to_datetime(f"{date_str} {select_time}")
                    
                    # 篩選：找出小於等於目標時間的最後一筆資料
                    match = df[df['date'] <= target_dt].sort_values('date').iloc[-1:]
                    
                    if not match.empty:
                        row = match.iloc[0]
                        st.success(f"成功取得數據！ 資料點時間：{row['date'].strftime('%H:%M')}")
                        
                        m1, m2, m3, m4 = st.columns(4)
                        # KBar 包含開高低收，這裡呈現「收盤價」作為該分鐘價格
                        close_p = row.get('close', 0)
                        open_p = row.get('open', 0)
                        vol = row.get('volume', 0)
                        
                        # 計算漲跌幅度 (簡單以該分鐘開收盤比)
                        diff = close_p - open_p
                        
                        m1.metric("成交價 (Close)", f"{close_p} TWD", f"{diff:.2f}")
                        m2.metric("成交量 (股)", f"{int(vol):,}")
                        m3.metric("最高價 (High)", f"{row.get('high', 0)}")
                        m4.metric("最低價 (Low)", f"{row.get('low', 0)}")
                        
                        st.write("### 該時段詳細數據")
                        st.dataframe(match, use_container_width=True)
                        
                        # 呈現當天至該時間點的走勢圖 (可選)
                        st.write("### 當日走勢圖")
                        chart_data = df[df['date'] <= target_dt].set_index('date')['close']
                        st.line_chart(chart_data)
                    else:
                        st.error("選定時間前無 K 線資料，請確認是否為交易時間。")
                else:
                    st.error("查無資料。請檢查：1.股票代號 2.日期是否為開盤日 3.Token 權限。")

        except Exception as err:
            st.error(f"API 回傳錯誤：{err}")
            st.info("提示：FinMind API 有時會調整資料集名稱，目前已嘗試使用 TaiwanStockKBar。")
