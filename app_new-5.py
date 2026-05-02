import streamlit as st
import pandas as pd
from datetime import datetime

try:
    from FinMind.data import DataLoader
except ImportError:
    st.error("環境初始化失敗，請檢查 requirements.txt")
    st.stop()

st.set_page_config(page_title="台股查詢-免費版", layout="wide")
st.title("📊 台股價格查詢器 (免費權限版)")

# 顯示目前的錯誤提示
st.warning("提示：由於您的 FinMind 等級為 Register，無法存取分鐘級 KBar 資料。本程式已自動切換為『日成交資料』模式。")

with st.sidebar:
    st.header("1. 連線設定")
    raw_token = st.text_input("輸入 FinMind Token", type="password")
    st.divider()
    st.header("2. 查詢條件")
    stock_id = st.text_input("股票代號", value="2330").strip()
    select_date = st.date_input("日期", value=datetime.now())
    # 分鐘輸入在免費版中將失效，僅供參考
    st.caption("註：免費版僅支援日收盤價，無法指定分鐘。")
    search_btn = st.button("開始查詢")

if search_btn:
    api_token = raw_token.strip() if raw_token else None
    
    if not api_token:
        st.warning("請先輸入 Token。")
    else:
        try:
            with st.spinner('正在獲取日成交數據...'):
                api = DataLoader()
                api.login_by_token(api_token=api_token)
                
                date_str = select_date.strftime('%Y-%m-%d')
                
                # --- 切換為免費版支援的資料集：TaiwanStockPrice ---
                df = api.get_data(
                    dataset="TaiwanStockPrice",
                    data_id=stock_id,
                    start_date=date_str,
                    end_date=date_str
                )
                
                if df is not None and not df.empty:
                    df.columns = [c.lower() for c in df.columns]
                    row = df.iloc[0]
                    
                    st.success(f"成功取得 {stock_id} 在 {date_str} 的成交資料")
                    
                    # 計算漲跌幅度
                    spread = row.get('spread', 0)
                    
                    m1, m2, m3, m4 = st.columns(4)
                    m1.metric("收盤價", f"{row.get('close')} TWD", f"{spread}")
                    m2.metric("成交量 (張)", f"{int(row.get('trading_volume', 0) / 1000):,}")
                    m3.metric("最高價", f"{row.get('max')}")
                    m4.metric("最低價", f"{row.get('min')}")
                    
                    st.write("### 當日完整數據")
                    st.dataframe(df, use_container_width=True)
                else:
                    st.error("查無資料。可能原因：1.該日非交易日 2.股票代號錯誤 3.當日數據尚未更新。")

        except Exception as err:
            if "update your user level" in str(err):
                st.error("權限錯誤：您的 FinMind 帳號等級不足，無法抓取此類資料。")
            else:
                st.error(f"連線錯誤：{err}")

