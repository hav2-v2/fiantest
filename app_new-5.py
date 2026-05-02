import streamlit as st
import pandas as pd
from datetime import datetime
from FinMind.data import DataLoader

# 網頁配置
st.set_page_config(page_title="台股多功能查詢器", layout="wide")

# --- 核心資料抓取函式 ---
def fetch_data(dataset, stock_id, date, token):
    try:
        api = DataLoader()
        api.login_by_token(api_token=token)
        # 使用萬用 get_data 避開函式名稱變動問題，直接指定資料集名稱
        df = api.get_data(
            dataset=dataset,
            data_id=stock_id,
            start_date=date
        )
        if df is not None and not df.empty:
            # 統一將欄位名稱轉為小寫，避免大小寫不一導致程式崩潰
            df.columns = [c.lower() for c in df.columns]
            return df
        return None
    except Exception as e:
        st.error(f"資料抓取失敗: {e}")
        return None

# --- 介面設計 ---
st.title("📈 台股多功能查詢儀表板")

with st.sidebar:
    st.header("🔑 連線設定")
    # 清理 Token 兩端的空白字元，防止 latin-1 編碼錯誤
    user_token = st.text_input("輸入 FinMind Token", type="password").strip()
    
    st.header("🔍 查詢條件")
    stock_id = st.text_input("股票代號", value="2330").strip()
    # 預設從今年初開始看，可以看到更完整的趨勢
    query_date = st.date_input("資料起始日期", value=datetime(2024, 1, 1))
    
    st.header("📋 功能選擇")
    mode = st.radio("想要查看的資訊：", 
                    ["日成交行情 (Price)", "每月營收 (Revenue)", "本益比/殖利率 (PER)"])
    
    search_btn = st.button("更新數據")

# --- 邏輯執行 ---
if search_btn:
    if not user_token:
        st.warning("請先在側邊欄輸入 Token。")
    else:
        date_str = query_date.strftime('%Y-%m-%d')
        
        with st.spinner(f'正在獲取 {mode} 數據...'):
            if mode == "日成交行情 (Price)":
                st.subheader(f"📊 {stock_id} 日成交行情")
                df = fetch_data("TaiwanStockPrice", stock_id, date_str, user_token)
                if df is not None:
                    latest = df.iloc[-1]
                    c1, c2, c3, c4 = st.columns(4)
                    c1.metric("最新收盤價", f"{latest['close']} TWD", f"{latest['spread']}")
                    c2.metric("成交量 (股)", f"{int(latest['trading_volume']):,}")
                    c3.metric("最高價", f"{latest['max']}")
                    c4.metric("最低價", f"{latest['min']}")
                    st.line_chart(df.set_index('date')['close'])
                    st.dataframe(df.sort_values('date', ascending=False), use_container_width=True)

            elif mode == "每月營收 (Revenue)":
                st.subheader(f"💰 {stock_id} 歷月營收表現")
                df = fetch_data("TaiwanStockMonthRevenue", stock_id, date_str, user_token)
                if df is not None:
                    # 畫出營收趨勢圖
                    st.line_chart(df.set_index('date')['revenue'])
                    st.dataframe(df.sort_values('date', ascending=False), use_container_width=True)

            elif mode == "本益比/殖利率 (PER)":
                st.subheader(f"💎 {stock_id} 價值指標")
                df = fetch_data("TaiwanStockPER", stock_id, date_str, user_token)
                if df is not None:
                    latest = df.iloc[-1]
                    c1, c2, c3 = st.columns(3)
                    c1.metric("本益比 (PE)", f"{latest['per']}")
                    c2.metric("本淨比 (PB)", f"{latest['pbr']}")
                    c3.metric("殖利率 (%)", f"{latest['dividend_yield']}%")
                    st.line_chart(df.set_index('date')['per'])
                    st.dataframe(df.sort_values('date', ascending=False), use_container_width=True)
            
            if df is None:
                st.error("查無資料，請確認該日是否為開盤日，或 Token 權限是否正確。")
