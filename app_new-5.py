from datetime import datetime, timedelta
import pandas as pd
import requests
import streamlit as st

# --- 頁面基本設定 ---
st.set_page_config(
    page_title="台股籌碼與技術面篩選工具", page_icon="📈", layout="wide"
)

st.title("📈 台股三大法人籌碼篩選工具")
st.markdown("快速查詢指定日期前 **N 個交易日** 的外資/投信/自營商累計買超個股。")


# --- 資料抓取與快取函式 ---
@st.cache_data(ttl=3600)  # 快取 1 小時 (3600 秒)
def fetch_institutional_data(target_date_str, n_days, token, investor_code):
    target_dt = datetime.strptime(target_date_str, "%Y-%m-%d")

    # 💡 關鍵修復：不管 N 是多少，start_date 至少保底往前推算 10 天，確保能涵蓋假日與休市
    days_back = max(int(n_days * 2.5), 10)
    start_dt = target_dt - timedelta(days=days_back)
    start_date_str = start_dt.strftime("%Y-%m-%d")

    url = "https://api.finmindtrade.com/api/v4/data"
    params = {
        "dataset": "TaiwanStockInstitutionalInvestorsBuySell",
        "start_date": start_date_str,
        "end_date": target_date_str,
    }
    if token:
        params["token"] = token

    # 發起 API 請求，設定 10 秒 Timeout 避免卡死
    res = requests.get(url, params=params, timeout=10)
    data = res.json()

    if "data" not in data or not data["data"]:
        return None, []

    df = pd.DataFrame(data["data"])
    df_filtered = df[df["name"] == investor_code].copy()

    if df_filtered.empty:
        return None, []

    # 取出實際有交易的日期，並切出最後 N 天
    available_dates = sorted(df_filtered["date"].unique())
    selected_dates = (
        available_dates[-n_days:]
        if len(available_dates) >= n_days
        else available_dates
    )

    # 過濾資料並計算累計買超
    df_n_days = df_filtered[df_filtered["date"].isin(selected_dates)].copy()
    df_n_days["net_buy_shares"] = df_n_days["buy"] - df_n_days["sell"]

    # 依股票代號加總
    df_summary = (
        df_n_days.groupby("stock_id")["net_buy_shares"].sum().reset_index()
    )
    df_summary["net_buy_lots"] = (
        df_summary["net_buy_shares"] / 1000
    ).astype(int)

    # 排序
    df_result = df_summary.sort_values(
        by="net_buy_lots", ascending=False
    ).reset_index(drop=True)

    return df_result, selected_dates


# --- 側邊欄：表單與確認按鈕 ---
with st.sidebar.form(key="filter_form"):
    st.header("⚙️ 篩選條件設定")

    finmind_token = st.text_input(
        "FinMind API Token (選填)",
        value="",
        type="password",
        help="輸入免費申請的 Token 可享每小時 600 次請求。若留空則使用預設匿名權限。",
    )

    investor_type = st.selectbox(
        "選擇法人類別",
        options=["Foreign_Investor", "Investment_Trust", "Dealer_Self"],
        format_func=lambda x: {
            "Foreign_Investor": "外資",
            "Investment_Trust": "投信",
            "Dealer_Self": "自營商",
        }[x],
    )

    target_date = st.date_input("選擇基準日期", value=datetime.today())

    n_days = st.slider(
        "往前計算交易日天數 (N)", min_value=1, max_value=20, value=5
    )

    # 🔘 送出按鈕：點擊後才會發射 API 請求
    submit_button = st.form_submit_button(
        label="🚀 開始查詢", use_container_width=True
    )


# --- 主畫面渲染邏輯 (只有按鈕被按下後才執行) ---
if submit_button:
    date_str = target_date.strftime("%Y-%m-%d")

    with st.spinner("正在連線抓取籌碼資料，請稍後..."):
        try:
            df_result, actual_dates = fetch_institutional_data(
                date_str, n_days, finmind_token, investor_type
            )

            if df_result is not None and not df_result.empty:
                investor_name_map = {
                    "Foreign_Investor": "外資",
                    "Investment_Trust": "投信",
                    "Dealer_Self": "自營商",
                }
                inv_name = investor_name_map[investor_type]

                st.success("✅ 成功取得資料！")

                # 顯示實際採計的交易日細節
                st.info(
                    f"📅 **實際採計的 {len(actual_dates)} 個交易日：** "
                    + ", ".join(actual_dates)
                )

                # 指標卡片 (Metrics)
                col1, col2, col3 = st.columns(3)
                col1.metric("買超第一名", df_result.iloc[0]["stock_id"])
                col2.metric(
                    "最高買超張數", f"{df_result.iloc[0]['net_buy_lots']:,} 張"
                )
                col3.metric("符合條件股票總數", f"{len(df_result)} 支")

                st.divider()

                # 呈現表格 (前 50 名)
                st.subheader(f"🔥 {inv_name} 累計買超排行榜 (前 50 名)")

                df_display = df_result.rename(
                    columns={
                        "stock_id": "股票代號",
                        "net_buy_lots": f"{inv_name}累計買超(張)",
                        "net_buy_shares": "累計買超(股)",
                    }
                )

                st.dataframe(
                    df_display[
                        ["股票代號", f"{inv_name}累計買超(張)"]
                    ].head(50),
                    use_container_width=True,
                    height=500,
                )

            else:
                st.warning(
                    "⚠️ 查無資料，可能原因：該區間為休市日、或 API 額度達到上限。"
                )

        except requests.exceptions.Timeout:
            st.error(
                "❌ 連線逾時！FinMind 伺服器回應過慢，請重新整理頁面再試一次。"
            )
        except Exception as e:
            st.error(f"❌ 發生未預期的錯誤：{e}")
else:
    # 第一次開啟網頁，尚未點擊按鈕時的提示
    st.info("👈 請在左側設定條件並按下 **「🚀 開始查詢」** 按鈕。")
