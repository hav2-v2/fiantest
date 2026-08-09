import time
from datetime import datetime, timedelta
import pandas as pd
import requests
import streamlit as st

# --- 頁面基本設定 ---
st.set_page_config(
    page_title="台股籌碼與技術面篩選工具", page_icon="📈", layout="wide"
)

st.title("📈 證交所免費版：三大法人籌碼篩選工具")
st.markdown("快速查詢指定日期前 **N 個交易日** 的外資/投信/自營商累計買超個股 (僅限上市股票)。")

if st.sidebar.button("🧹 清除快取記憶"):
    st.cache_data.clear()
    st.sidebar.success("快取已清除！")


# --- 資料抓取與快取函式 (使用證交所 TWSE API) ---
@st.cache_data(ttl=3600)
def fetch_twse_institutional_data(target_date_str, n_days, investor_type):
    # 建立目標與當前推算日期
    current_dt = datetime.strptime(target_date_str, "%Y-%m-%d")
    
    all_records = []
    actual_dates = []
    
    # 建立進度條與狀態文字
    progress_bar = st.progress(0)
    status_text = st.empty()

    days_collected = 0
    attempts = 0
    max_attempts = max(n_days * 3, 20) # 最多往前推算天數，避免無窮迴圈

    # 迴圈往回找，直到收集滿 N 個「有開盤」的交易日
    while days_collected < n_days and attempts < max_attempts:
        date_twse_format = current_dt.strftime("%Y%m%d")
        date_display = current_dt.strftime("%Y-%m-%d")
        
        status_text.text(f"⏳ 正在向證交所查詢 {date_display} 資料... (已收集 {days_collected}/{n_days} 天)")
        
        # 呼叫 TWSE 每日三大法人買賣超 API
        url = f"https://www.twse.com.tw/rwd/zh/fund/T86?date={date_twse_format}&selectType=ALL&response=json"
        
        try:
            res = requests.get(url, timeout=10)
            if res.status_code == 200:
                data = res.json()
                
                # stat == 'OK' 代表這天有交易資料 (非假日)
                if data.get("stat") == "OK" and "data" in data:
                    fields = data["fields"]
                    raw_data = data["data"]
                    
                    df_day = pd.DataFrame(raw_data, columns=fields)
                    df_day["date"] = date_display
                    all_records.append(df_day)
                    actual_dates.append(date_display)
                    days_collected += 1
                    
                    # 更新進度條
                    progress_bar.progress(days_collected / n_days)
                    
                    # ⚠️ 關鍵：避免被證交所封鎖 IP，每次成功抓取後強迫暫停 3 秒
                    if days_collected < n_days:
                        time.sleep(3)
                else:
                    # 如果不是 OK (例如假日)，不需要暫停這麼久
                    time.sleep(0.5)
        except Exception as e:
            st.warning(f"抓取 {date_display} 時發生錯誤: {e}")
            time.sleep(2) # 錯誤時也暫停一下
            
        current_dt -= timedelta(days=1)
        attempts += 1

    # 清除進度 UI
    progress_bar.empty()
    status_text.empty()

    if not all_records:
        return None, []

    # 合併所有收集到的天數
    df_all = pd.concat(all_records, ignore_index=True)
    
    # 移除千分位逗號並轉為數值格式
    def clean_number(x):
        try:
            return int(str(x).replace(",", ""))
        except:
            return 0

    # 根據使用者選擇，對應證交所的欄位名稱
    if investor_type == "Foreign_Investor":
        target_col = "外陸資買賣超股數(不含外資自營商)"
    elif investor_type == "Investment_Trust":
        target_col = "投信買賣超股數"
    else: # Dealer_Self
        target_col = "自營商買賣超股數(自行買賣)"
        
    # 如果找不到精確欄位，做個防呆檢查 (證交所偶爾會微調欄位名稱)
    if target_col not in df_all.columns:
        # 嘗試模糊比對
        possible_cols = [c for c in df_all.columns if "買賣超" in c]
        if not possible_cols:
            return None, []
        target_col = possible_cols[0] # 退而求其次抓第一個買賣超欄位

    # 清理欄位數值
    df_all["net_buy_shares"] = df_all[target_col].apply(clean_number)
    
    # 依股票代號與名稱加總
    df_summary = df_all.groupby(["證券代號", "證券名稱"])["net_buy_shares"].sum().reset_index()
    
    # 將股數換算為張數 (除以 1000)
    df_summary["net_buy_lots"] = (df_summary["net_buy_shares"] / 1000).astype(int)
    
    # 排序
    df_result = df_summary.sort_values(by="net_buy_lots", ascending=False).reset_index(drop=True)

    return df_result, sorted(actual_dates)


# --- 側邊欄：表單與確認按鈕 ---
with st.sidebar.form(key="filter_form"):
    st.header("⚙️ 篩選條件設定")
    st.info("💡 目前資料源：台灣證交所 (TWSE) 免費官方 API")

    investor_type = st.selectbox(
        "選擇法人類別",
        options=["Foreign_Investor", "Investment_Trust", "Dealer_Self"],
        format_func=lambda x: {
            "Foreign_Investor": "外資 (不含外資自營商)",
            "Investment_Trust": "投信",
            "Dealer_Self": "自營商 (自行買賣)",
        }[x],
    )

    target_date = st.date_input("選擇基準日期", value=datetime.today())

    # 由於證交所需要一天天往回抓，不建議一次抓太多天以免等太久或被鎖
    n_days = st.slider(
        "往前計算交易日天數 (N)", min_value=1, max_value=10, value=3,
        help="建議設定 5 天以內，以免抓取時間過長。"
    )

    submit_button = st.form_submit_button(
        label="🚀 開始查詢 (完全免費)", use_container_width=True
    )


# --- 主畫面渲染邏輯 ---
if submit_button:
    date_str = target_date.strftime("%Y-%m-%d")

    try:
        df_result, actual_dates = fetch_twse_institutional_data(
            date_str, n_days, investor_type
        )

        if df_result is not None and not df_result.empty:
            investor_name_map = {
                "Foreign_Investor": "外資",
                "Investment_Trust": "投信",
                "Dealer_Self": "自營商",
            }
            inv_name = investor_name_map[investor_type]

            st.success("✅ 成功從證交所取得全市場資料！")

            st.info(
                f"📅 **實際採計的 {len(actual_dates)} 個交易日：** "
                + ", ".join(actual_dates)
            )

            col1, col2, col3 = st.columns(3)
            col1.metric("買超第一名", f"{df_result.iloc[0]['證券代號']} {df_result.iloc[0]['證券名稱']}")
            col2.metric("最高買超張數", f"{df_result.iloc[0]['net_buy_lots']:,} 張")
            col3.metric("上市股票總數", f"{len(df_result)} 支")

            st.divider()

            st.subheader(f"🔥 {inv_name} 累計買超排行榜 (上市前 100 名)")

            df_display = df_result.rename(
                columns={
                    "證券代號": "股票代號",
                    "證券名稱": "股票名稱",
                    "net_buy_lots": f"{inv_name}累計買超(張)",
                }
            )

            # 顯示前 100 名
            st.dataframe(
                df_display[["股票代號", "股票名稱", f"{inv_name}累計買超(張)"]].head(100),
                use_container_width=True,
                height=600,
            )

        else:
            st.warning("⚠️ 查無資料，可能原因：該區間皆為休市日，或尚未更新。")

    except Exception as e:
        st.error(f"❌ 發生未預期的錯誤：{e}")
else:
    st.info("👈 點擊左側 **「🚀 開始查詢」**，程式將自動向證交所請求資料。")
