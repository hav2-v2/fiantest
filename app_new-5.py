from datetime import datetime, timedelta
import pandas as pd
import requests


def get_institutional_buy_before_date(target_date_str, n_days=5, token=""):
    """抓取指定日期的前 N 個交易日法人買賣超資料

    :param target_date_str: 指定日期 (格式: 'YYYY-MM-DD')
    :param n_days: 往前計算的交易日天數 (預設 5 天)
    :param token: FinMind 免費 API Token
    """
    # 1. 計算 start_date（往前推 n_days * 2.5 天，確保涵蓋週末與例假日）
    target_dt = datetime.strptime(target_date_str, "%Y-%m-%d")
    start_dt = target_dt - timedelta(days=int(n_days * 2.5))
    start_date_str = start_dt.strftime("%Y-%m-%d")

    # 2. 設定 FinMind API 參數
    url = "https://api.finmindtrade.com/api/v4/data"
    params = {
        "dataset": "TaiwanStockInstitutionalInvestorsBuySell",
        "start_date": start_date_str,
        "end_date": target_date_str,  # 指定結束日期為我們的目標日
        "token": token,
    }

    print(
        f"正在抓取 {start_date_str} 至 {target_date_str} 的三大法人資料..."
    )
    res = requests.get(url, params=params).json()

    if "data" not in res or not res["data"]:
        print("未抓取到資料，請檢查日期或 Token 是否正確。")
        return None

    df = pd.DataFrame(res["data"])

    # 3. 篩選外資資料 (Foreign_Investor)
    df_foreign = df[df["name"] == "Foreign_Investor"].copy()

    # 4. 取得該區間內「實際有交易」的日期列表，並只留最後 N 個交易日
    available_dates = sorted(df_foreign["date"].unique())

    if len(available_dates) < n_days:
        print(
            f"⚠️ 警告：該區間內的有效交易日只有 {len(available_dates)} 天，不足 {n_days} 天。"
        )
        selected_dates = available_dates
    else:
        selected_dates = available_dates[-n_days:]

    print(
        f"✅ 成功鎖定以 {target_date_str} 為基準的前 {len(selected_dates)} 個交易日："
    )
    print(selected_dates)

    # 5. 過濾出這 N 個交易日的資料並計算累計買超
    df_n_days = df_foreign[df_foreign["date"].isin(selected_dates)].copy()

    # 計算淨買超股數，並轉為「張數」
    df_n_days["net_buy_shares"] = df_n_days["buy"] - df_n_days["sell"]

    df_summary = (
        df_n_days.groupby("stock_id")["net_buy_shares"].sum().reset_index()
    )
    df_summary["net_buy_lots"] = (
        df_summary["net_buy_shares"] / 1000
    ).astype(int)

    # 6. 依買超張數由大到小排序
    df_result = df_summary.sort_values(by="net_buy_lots", ascending=False)

    return df_result


# --- 使用測試 ---
MY_TOKEN = "你的FinMind_Token"  # 填入免費申請的 Token
TARGET_DATE = "2026-08-05"  # 指定任何你想查詢的歷史日期

# 抓取 2026-08-05（含）往前 5 個交易日的外資買超排行
df_top_buy = get_institutional_buy_before_date(
    target_date_str=TARGET_DATE, n_days=5, token=MY_TOKEN
)

if df_top_buy is not None:
    print(
        f"\n🔥 {TARGET_DATE} 前 5 個交易日外資買超前 10 名（張）："
    )
    print(df_top_buy.head(10).to_string(index=False))
