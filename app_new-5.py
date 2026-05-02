import streamlit as st
import shioaji as sj
import datetime
import pytz
import time
import pandas as pd
import yfinance as yf

# ══════════════════════════════════════════════════════════
#  頁面設定
# ══════════════════════════════════════════════════════════
st.set_page_config(page_title="股票監控", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Noto+Sans+TC:wght@400;700&display=swap');
.stApp { background: #0a0e1a; font-family: 'Noto Sans TC', sans-serif; }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 1rem 0.8rem 2rem 0.8rem; max-width: 100%; }
.app-title { font-family:'JetBrains Mono',monospace; font-size:1.4rem; font-weight:700; color:#e2e8f0; text-align:center; padding:1rem 0 0.3rem 0; }
.clock-bar { display:flex; gap:0.6rem; margin-bottom:0.6rem; }
.clock-box { flex:1; background:#0d1424; border:1px solid #1e293b; border-radius:10px; padding:0.5rem 0.8rem; }
.clock-label { font-family:'JetBrains Mono',monospace; font-size:0.58rem; color:#4a5568; text-transform:uppercase; letter-spacing:.1em; display:block; }
.clock-time  { font-family:'JetBrains Mono',monospace; font-size:1.1rem; font-weight:700; color:#e2e8f0; display:block; margin-top:1px; }
.clock-date  { font-family:'JetBrains Mono',monospace; font-size:0.62rem; color:#4a5568; display:block; }
.market-open  { color:#10b981 !important; }
.market-close { color:#ef4444 !important; }
.status-bar { display:flex; justify-content:space-between; align-items:center; padding:0.35rem 0.7rem; background:#0d1424; border-radius:8px; margin-bottom:0.7rem; border:1px solid #1e293b; }
.status-dot { width:7px; height:7px; border-radius:50%; background:#10b981; display:inline-block; margin-right:5px; animation:pulse 2s infinite; }
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:.4} }
.status-text { font-family:'JetBrains Mono',monospace; font-size:0.62rem; color:#4a5568; }
.signed-badge { font-family:'JetBrains Mono',monospace; font-size:0.6rem; padding:2px 7px; border-radius:4px; font-weight:700; }
.signed-ok { background:#052e16; color:#34d399; border:1px solid #166534; }
.signed-no { background:#450a0a; color:#f87171; border:1px solid #991b1b; }

/* ── 自選卡片 ── */
.stock-card { background:linear-gradient(135deg,#111827 0%,#1a2035 100%); border:1px solid #1e293b; border-radius:16px; padding:1.1rem 1.2rem; margin-bottom:0.75rem; position:relative; overflow:hidden; }
.stock-card::before { content:''; position:absolute; top:0; left:0; right:0; height:3px; border-radius:16px 16px 0 0; }
.stock-card.up::before   { background:linear-gradient(90deg,#ef4444,#f87171); }
.stock-card.down::before { background:linear-gradient(90deg,#22c55e,#4ade80); }
.stock-card.flat::before { background:linear-gradient(90deg,#6b7280,#9ca3af); }
.card-top { display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:0.6rem; }
.stock-code { font-family:'JetBrains Mono',monospace; font-size:0.8rem; color:#64748b; letter-spacing:.1em; }
.stock-name { font-size:1rem; font-weight:700; color:#e2e8f0; margin-top:0.1rem; }
.exchange-badge { font-family:'JetBrains Mono',monospace; font-size:0.62rem; padding:2px 7px; border-radius:4px; font-weight:700; }
.badge-tw { background:#1e3a5f; color:#60a5fa; }
.card-price-row { display:flex; justify-content:space-between; align-items:flex-end; margin-bottom:0.6rem; }
.price-main { font-family:'JetBrains Mono',monospace; font-size:1.9rem; font-weight:700; line-height:1; }
.price-main.up{color:#ef4444} .price-main.down{color:#22c55e} .price-main.flat{color:#9ca3af}
.change-block { text-align:right; }
.change-val { font-family:'JetBrains Mono',monospace; font-size:1rem; font-weight:700; display:block; }
.change-val.up{color:#ef4444} .change-val.down{color:#22c55e} .change-val.flat{color:#9ca3af}
.change-pct { font-family:'JetBrains Mono',monospace; font-size:0.78rem; display:block; margin-top:1px; }
.change-pct.up{color:#fca5a5} .change-pct.down{color:#86efac} .change-pct.flat{color:#6b7280}
.card-stats { display:flex; gap:1rem; border-top:1px solid #1e293b; padding-top:0.55rem; }
.stat-item { flex:1; }
.stat-label { font-size:0.6rem; color:#4a5568; text-transform:uppercase; letter-spacing:.08em; display:block; }
.stat-val   { font-family:'JetBrains Mono',monospace; font-size:0.78rem; color:#94a3b8; display:block; margin-top:1px; }

.section-title { font-size:0.68rem; color:#4a5568; text-transform:uppercase; letter-spacing:.12em; font-family:'JetBrains Mono',monospace; margin:1rem 0 0.4rem 0.2rem; border-left:3px solid #2563eb; padding-left:0.5rem; }
.stButton > button { background:transparent !important; border:1px solid #1e293b !important; color:#4a5568 !important; border-radius:8px !important; font-size:0.75rem !important; padding:0.2rem 0.6rem !important; }
.stButton > button:hover { border-color:#ef4444 !important; color:#ef4444 !important; background:#1a0a0a !important; }
.stTextInput > div > div > input { background:#0d1424 !important; border:1px solid #1e293b !important; color:#e2e8f0 !important; border-radius:8px !important; font-family:'JetBrains Mono',monospace !important; font-size:0.85rem !important; }
.stTextInput > div > div > input:focus { border-color:#2563eb !important; box-shadow:0 0 0 2px rgba(37,99,235,.2) !important; }

/* ── 漏斗篩選器 ── */
.funnel-step {
  border-radius:14px;
  padding:0.9rem 1.1rem;
  margin-bottom:0.7rem;
  border-left:4px solid;
  position: relative;
}
/* 各層顏色 - 邊框 */
.funnel-step-1 { background:rgba(37,99,235,0.07);  border-color:#2563eb; }
.funnel-step-2 { background:rgba(139,92,246,0.07); border-color:#8b5cf6; }
.funnel-step-3 { background:rgba(20,184,166,0.07); border-color:#14b8a6; }
.funnel-step-4 { background:rgba(245,158,11,0.07); border-color:#f59e0b; }
.funnel-step-5 { background:rgba(236,72,153,0.07); border-color:#ec4899; }

.funnel-step-label {
  font-family:'JetBrains Mono',monospace;
  font-size:0.62rem;
  font-weight:700;
  text-transform:uppercase;
  letter-spacing:.1em;
  margin-bottom:0.55rem;
  display:flex;
  align-items:center;
  gap:0.5rem;
}
.lbl-1 { color:#60a5fa; }
.lbl-2 { color:#a78bfa; }
.lbl-3 { color:#2dd4bf; }
.lbl-4 { color:#fbbf24; }
.lbl-5 { color:#f472b6; }

.funnel-arrow {
  text-align:center;
  font-size:1.1rem;
  color:#1e293b;
  margin: -0.2rem 0;
  line-height:1;
}

/* ── 結果卡片（各層顏色） ── */
.result-row {
  border-radius:10px;
  padding:0.6rem 0.9rem;
  margin-bottom:0.35rem;
  display:flex;
  justify-content:space-between;
  align-items:center;
  border:1px solid;
}
.result-row-1 { background:rgba(37,99,235,0.08);   border-color:rgba(37,99,235,0.25); }
.result-row-2 { background:rgba(139,92,246,0.08);  border-color:rgba(139,92,246,0.25); }
.result-row-3 { background:rgba(20,184,166,0.08);  border-color:rgba(20,184,166,0.25); }
.result-row-4 { background:rgba(245,158,11,0.08);  border-color:rgba(245,158,11,0.25); }
.result-row-5 { background:rgba(236,72,153,0.08);  border-color:rgba(236,72,153,0.25); }

.rcode { font-family:'JetBrains Mono',monospace; font-size:0.85rem; font-weight:700; }
.rcode-1{color:#60a5fa} .rcode-2{color:#a78bfa} .rcode-3{color:#2dd4bf} .rcode-4{color:#fbbf24} .rcode-5{color:#f472b6}
.rname  { font-size:0.8rem; color:#94a3b8; margin-left:0.45rem; }
.rprice { font-family:'JetBrains Mono',monospace; font-size:0.78rem; color:#cbd5e1; margin-left:0.6rem; }
.rmkt   { font-family:'JetBrains Mono',monospace; font-size:0.58rem; padding:1px 5px; border-radius:3px; background:#1e293b; color:#64748b; }

.rpct-up   { font-family:'JetBrains Mono',monospace; font-size:0.92rem; font-weight:700; color:#ef4444; }
.rpct-down { font-family:'JetBrains Mono',monospace; font-size:0.92rem; font-weight:700; color:#22c55e; }

.layer-badge {
  font-family:'JetBrains Mono',monospace; font-size:0.55rem; padding:1px 5px; border-radius:3px; font-weight:700;
}
.layer-badge-1{background:rgba(37,99,235,.2);  color:#60a5fa; border:1px solid rgba(37,99,235,.4);}
.layer-badge-2{background:rgba(139,92,246,.2); color:#a78bfa; border:1px solid rgba(139,92,246,.4);}
.layer-badge-3{background:rgba(20,184,166,.2); color:#2dd4bf; border:1px solid rgba(20,184,166,.4);}
.layer-badge-4{background:rgba(245,158,11,.2); color:#fbbf24; border:1px solid rgba(245,158,11,.4);}
.layer-badge-5{background:rgba(236,72,153,.2); color:#f472b6; border:1px solid rgba(236,72,153,.4);}

.ds-yf   { font-family:'JetBrains Mono',monospace; font-size:0.55rem; padding:1px 4px; border-radius:3px; background:#1a2e1a; color:#4ade80; border:1px solid #166534; }
.ds-live { font-family:'JetBrains Mono',monospace; font-size:0.55rem; padding:1px 4px; border-radius:3px; background:#2a1a0a; color:#fb923c; border:1px solid #7c2d12; }

/* 條件選單選項（禁用樣式） */
.cond-option-disabled {
  opacity: 0.35;
  cursor: not-allowed;
  pointer-events: none;
}

/* 漏斗連接線 */
.funnel-connector {
  display:flex; align-items:center; justify-content:center;
  margin: 0.15rem 0;
  gap: 0.4rem;
}
.funnel-connector-line {
  flex:1; height:1px; background: linear-gradient(90deg,transparent,#1e293b,transparent);
}
.funnel-connector-text {
  font-family:'JetBrains Mono',monospace; font-size:0.6rem; color:#334155;
  white-space:nowrap;
}

/* 結果區段標題 */
.result-section-hdr {
  font-family:'JetBrains Mono',monospace;
  font-size:0.62rem;
  font-weight:700;
  text-transform:uppercase;
  letter-spacing:.08em;
  padding: 0.35rem 0.7rem;
  border-radius:6px;
  margin: 0.5rem 0 0.3rem 0;
  display:inline-block;
}
.rsh-1{background:rgba(37,99,235,.12);  color:#60a5fa;}
.rsh-2{background:rgba(139,92,246,.12); color:#a78bfa;}
.rsh-3{background:rgba(20,184,166,.12); color:#2dd4bf;}
.rsh-4{background:rgba(245,158,11,.12); color:#fbbf24;}
.rsh-5{background:rgba(236,72,153,.12); color:#f472b6;}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
#  常數
# ══════════════════════════════════════════════════════════
BATCH_SIZE  = 50
BATCH_SLEEP = 1.5
YF_SUFFIX   = {"TSE": ".TW", "OTC": ".TWO"}

# 漏斗層數最多 5 層
MAX_LAYERS = 5
# 各層顏色名稱（對應 CSS class 後綴）
LAYER_COLORS = ["1","2","3","4","5"]
LAYER_NAMES  = ["第一層","第二層","第三層","第四層","第五層"]
LAYER_ICONS  = ["🔵","🟣","🟢","🟡","🔴"]

# 可用條件定義
COND_TYPES = {
    "price_change":    "📈 前N交易日漲跌幅",
    "volume":          "📊 成交張數",
    "intraday_change": "⏱ 指定時間點漲跌幅",
}

def yf_ticker(code, exchange):
    return f"{code}{YF_SUFFIX.get(exchange,'.TW')}"

# ══════════════════════════════════════════════════════════
#  Session State
# ══════════════════════════════════════════════════════════
def ss_init():
    if "tw_watchlist" not in st.session_state:
        st.session_state.tw_watchlist = ["2330","2317","0050"]

    # 漏斗：layers 是 list of dicts
    # 每個 dict: { "cond_type": str, "params": dict, "results": list[dict] or None }
    if "funnel_layers" not in st.session_state:
        st.session_state.funnel_layers = []   # 空 = 尚未設定任何條件

    # 所有股票的歷史資料快取（code -> list of closes）
    if "hist_cache" not in st.session_state:
        st.session_state.hist_cache = {}

    # 全市場股票清單快取
    if "all_stocks_cache" not in st.session_state:
        st.session_state.all_stocks_cache = None

ss_init()

# ══════════════════════════════════════════════════════════
#  時間工具
# ══════════════════════════════════════════════════════════
def is_tw_market_open():
    tz_tw  = pytz.timezone("Asia/Taipei")
    now_tw = datetime.datetime.now(tz_tw)
    return now_tw.weekday() < 5 and datetime.time(9,0) <= now_tw.time() <= datetime.time(13,30)

def render_clocks():
    tz_tw  = pytz.timezone("Asia/Taipei")
    tz_us  = pytz.timezone("America/New_York")
    now_tw = datetime.datetime.now(tz_tw)
    now_us = datetime.datetime.now(tz_us)
    tw_open = now_tw.weekday()<5 and datetime.time(9,0)<=now_tw.time()<=datetime.time(13,30)
    us_open = now_us.weekday()<5 and datetime.time(9,30)<=now_us.time()<=datetime.time(16,0)
    tw_cls = "market-open" if tw_open else "market-close"
    us_cls = "market-open" if us_open else "market-close"
    return f"""
<div class="clock-bar">
  <div class="clock-box">
    <span class="clock-label">🇹🇼 台灣時間</span>
    <span class="clock-time">{now_tw.strftime('%H:%M:%S')}</span>
    <span class="clock-date">{now_tw.strftime('%Y/%m/%d %a')}&nbsp;<span class="{tw_cls}">{"● 開盤中" if tw_open else "○ 收盤"}</span></span>
  </div>
  <div class="clock-box">
    <span class="clock-label">🇺🇸 美東時間 (ET)</span>
    <span class="clock-time">{now_us.strftime('%H:%M:%S')}</span>
    <span class="clock-date">{now_us.strftime('%Y/%m/%d %a')}&nbsp;<span class="{us_cls}">{"● OPEN" if us_open else "○ CLOSED"}</span></span>
  </div>
</div>"""

# ══════════════════════════════════════════════════════════
#  永豐 API
# ══════════════════════════════════════════════════════════
@st.cache_resource
def init_shioaji():
    api = sj.Shioaji(simulation=False)
    try:
        accounts = api.login(
            api_key    = st.secrets["SHIOAJI_API_KEY"],
            secret_key = st.secrets["SHIOAJI_SECRET_KEY"],
            fetch_contract=True,
            contracts_timeout=20000,
        )
        return api, accounts
    except Exception as e:
        st.error(f"登入發生異常: {e}")
        return None, []

def get_tw_contract(api, code):
    try:    return api.Contracts.Stocks.get(code)
    except: return None

# ══════════════════════════════════════════════════════════
#  台股清單
# ══════════════════════════════════════════════════════════
@st.cache_resource
def get_all_tw_stock_list(_api):
    result = []
    for exch in ["TSE","OTC"]:
        try:
            ex_obj = getattr(_api.Contracts.Stocks, exch, None)
            if ex_obj is None: continue
            for c in ex_obj:
                code = c.code
                if not (code.isdigit() and len(code)==4): continue
                num = int(code)
                if 7000<=num<=7999: continue
                if 8800<=num<=8999: continue
                if 9000<=num<=9999: continue
                result.append({"code":code,"name":getattr(c,"name",""),"exchange":exch})
        except: pass
    return result

# ══════════════════════════════════════════════════════════
#  yfinance 批次下載
# ══════════════════════════════════════════════════════════
def fetch_batch_closes(tickers, start_str, end_str):
    if not tickers:
        return pd.DataFrame()
    try:
        raw = yf.download(
            tickers=tickers, start=start_str, end=end_str,
            interval="1d", auto_adjust=True, progress=False, threads=True,
        )
        if raw.empty: return pd.DataFrame()
        if isinstance(raw.columns, pd.MultiIndex):
            if "Close" in raw.columns.get_level_values(0):
                df = raw["Close"].copy()
            else: return pd.DataFrame()
        else:
            if "Close" in raw.columns:
                df = raw[["Close"]].rename(columns={"Close":tickers[0]})
            else: return pd.DataFrame()
        return df.dropna(how="all")
    except: return pd.DataFrame()

def calc_pct(series, n_days):
    vals = series.dropna().values
    if len(vals) < n_days+1: return None
    p0, p1 = vals[-(n_days+1)], vals[-1]
    if p0==0: return None
    return float((p1-p0)/p0*100)


# ══════════════════════════════════════════════════════════
#  指定時間點漲跌幅：yfinance 分鐘線抓取
# ══════════════════════════════════════════════════════════
TW_TZ = pytz.timezone("Asia/Taipei")

def _last_trading_date() -> datetime.date:
    """
    回傳「最近一次有交易的日期」：
    - 今日已開盤且已休盤 → 今日
    - 今日尚未開盤 / 今日是休假日 → 往前找最近一個週一到週五
    注意：此處只排除週末，台灣國定假日交由 yfinance 資料是否為空來決定。
    """
    tz_tw  = pytz.timezone("Asia/Taipei")
    now_tw = datetime.datetime.now(tz_tw)
    today  = now_tw.date()

    # 今日是交易日 且 已過收盤（13:30）
    if now_tw.weekday() < 5 and now_tw.time() > datetime.time(13, 30):
        return today

    # 往前找最近的週一~週五
    candidate = today - datetime.timedelta(days=1)
    for _ in range(14):   # 最多往前找 14 天
        if candidate.weekday() < 5:
            return candidate
        candidate -= datetime.timedelta(days=1)
    return today   # fallback


def fetch_intraday_batch(
    tickers: list,
    target_hour: int,
    target_min: int,
    trading_date: datetime.date,
) -> dict:
    """
    批次下載指定交易日的 1 分鐘線，
    找到 target_hour:target_min（台灣時間）的收盤價（ffill 填補無成交）。
    同時取得前一日收盤價（日線 auto_adjust=True）以計算漲跌幅。

    回傳 dict: ticker -> {"intraday_price": float, "prev_close": float, "pct": float}
    """
    if not tickers:
        return {}

    result = {}

    # ── Step 1：前一交易日收盤價（日線，2 天）──────────────
    prev_start = str(trading_date - datetime.timedelta(days=14))
    prev_end   = str(trading_date)   # exclusive → 取到 trading_date 前一日

    try:
        day_raw = yf.download(
            tickers     = tickers,
            start       = prev_start,
            end         = prev_end,
            interval    = "1d",
            auto_adjust = True,
            progress    = False,
            threads     = True,
        )
        if isinstance(day_raw.columns, pd.MultiIndex):
            prev_close_df = day_raw["Close"] if "Close" in day_raw.columns.get_level_values(0) else pd.DataFrame()
        elif "Close" in day_raw.columns:
            prev_close_df = day_raw[["Close"]].rename(columns={"Close": tickers[0]})
        else:
            prev_close_df = pd.DataFrame()
    except:
        prev_close_df = pd.DataFrame()

    prev_close_map = {}  # ticker -> prev_close float
    if not prev_close_df.empty:
        for tk in tickers:
            if tk in prev_close_df.columns:
                s = prev_close_df[tk].dropna()
                if len(s) > 0:
                    prev_close_map[tk] = float(s.values[-1])

    # ── Step 2：指定日 1 分鐘線 ──────────────────────────
    intra_start = str(trading_date)
    intra_end   = str(trading_date + datetime.timedelta(days=1))

    try:
        min_raw = yf.download(
            tickers     = tickers,
            start       = intra_start,
            end         = intra_end,
            interval    = "1m",
            auto_adjust = True,
            progress    = False,
            threads     = True,
        )
    except:
        min_raw = pd.DataFrame()

    if min_raw.empty:
        return result

    # 取 Close 欄
    if isinstance(min_raw.columns, pd.MultiIndex):
        if "Close" in min_raw.columns.get_level_values(0):
            intra_close = min_raw["Close"].copy()
        else:
            return result
    elif "Close" in min_raw.columns:
        intra_close = min_raw[["Close"]].rename(columns={"Close": tickers[0]})
    else:
        return result

    # 確保 index 是 DatetimeTZAware（台灣時間）
    if intra_close.index.tzinfo is None:
        intra_close.index = intra_close.index.tz_localize("UTC").tz_convert(TW_TZ)
    else:
        intra_close.index = intra_close.index.tz_convert(TW_TZ)

    # ffill 填補無成交分鐘
    intra_close = intra_close.ffill()

    # 找目標時間點：target_hour:target_min（台灣時間）
    target_dt = TW_TZ.localize(
        datetime.datetime.combine(trading_date, datetime.time(target_hour, target_min))
    )

    # 找 <= target_dt 的最後一根分K（ffill 已做，直接取最近的）
    mask = intra_close.index <= target_dt
    if not mask.any():
        return result   # 該時間點之前沒有資料（未開盤）

    intra_at_target = intra_close.loc[mask].iloc[-1]   # Series: ticker -> price

    for tk in tickers:
        intra_price = None
        if tk in intra_at_target.index:
            v = intra_at_target[tk]
            if pd.notna(v) and float(v) > 0:
                intra_price = float(v)
        elif len(tickers) == 1 and len(intra_at_target) == 1:
            v = intra_at_target.iloc[0]
            if pd.notna(v) and float(v) > 0:
                intra_price = float(v)

        if intra_price is None:
            continue

        prev_c = prev_close_map.get(tk)
        if prev_c is None or prev_c == 0:
            continue

        pct = (intra_price - prev_c) / prev_c * 100
        result[tk] = {
            "intraday_price": round(intra_price, 2),
            "prev_close":     round(prev_c, 2),
            "pct":            round(pct, 2),
        }

    return result


# ══════════════════════════════════════════════════════════
#  核心篩選引擎（支援多種條件 + 針對 subset 篩選）
# ══════════════════════════════════════════════════════════
def run_filter(
    stock_subset: list,      # list of dict {code, name, exchange, 最後收盤, 成交量(張), ...}
    cond_type: str,
    params: dict,
    progress_bar,
    live_holder,
    layer_idx: int,          # 0-based，用於顯示顏色
    all_stocks_meta: dict,   # code -> {name, exchange}  （全市場，第一層用）
) -> list:
    """
    根據 cond_type 對 stock_subset 進行篩選。
    第一層（layer_idx==0）：stock_subset 是全市場股票清單（含 code/name/exchange），
                           需要抓 yfinance 歷史資料。
    後續層：stock_subset 已有 {'代碼','名稱','市場','最後收盤',...} 格式，
            直接用快取資料計算，不重新抓取。
    """
    layer_color = LAYER_COLORS[min(layer_idx, 4)]
    results = []

    if cond_type == "price_change":
        n_days        = int(params["n_days"])
        direction     = params["direction"]   # "下跌" | "上漲"
        pct_threshold = float(params["pct_threshold"])

        end_dt    = datetime.date.today()
        start_dt  = end_dt - datetime.timedelta(days=int(n_days*3)+20)
        end_str   = str(end_dt + datetime.timedelta(days=1))
        start_str = str(start_dt)

        # 建立工作清單
        if layer_idx == 0:
            work_list = stock_subset   # [{code, name, exchange}]
        else:
            work_list = [{
                "code":     r["代碼"],
                "name":     r["名稱"],
                "exchange": "TSE" if r["市場"]=="上市" else "OTC",
                "_row":     r,
            } for r in stock_subset]

        total   = len(work_list)
        batches = [work_list[i:i+BATCH_SIZE] for i in range(0, total, BATCH_SIZE)]
        processed = 0

        for b_idx, batch in enumerate(batches):
            tickers    = [yf_ticker(s["code"], s["exchange"]) for s in batch]
            ticker_map = {yf_ticker(s["code"], s["exchange"]): s for s in batch}
            closes_df  = fetch_batch_closes(tickers, start_str, end_str)

            for tk, info in ticker_map.items():
                processed += 1
                progress_bar.progress(
                    min(processed/total, 1.0),
                    text=f"[第{layer_idx+1}層] 批次{b_idx+1}/{len(batches)} ｜ {processed}/{total} ｜ {info['code']} {info['name']}"
                )

                if closes_df.empty or tk not in closes_df.columns:
                    continue

                pct = calc_pct(closes_df[tk], n_days)
                if pct is None: continue

                hit = (direction=="下跌" and pct<=-pct_threshold) or \
                      (direction=="上漲" and pct>=pct_threshold)
                if not hit: continue

                last_close = float(closes_df[tk].dropna().values[-1])

                if layer_idx == 0:
                    row = {
                        "代碼":      info["code"],
                        "名稱":      info["name"],
                        "市場":      "上市" if info["exchange"]=="TSE" else "上櫃",
                        "最後收盤":  round(last_close, 2),
                        "漲跌幅(%)": round(pct, 2),
                        "成交量(張)": None,
                        "layer":     layer_idx+1,
                        "資料來源":  "yfinance",
                    }
                else:
                    row = info["_row"].copy()
                    row["漲跌幅(%)"] = round(pct, 2)
                    row["最後收盤"]  = round(last_close, 2)
                    row["layer"]    = layer_idx+1

                results.append(row)
                _show_live_funnel(live_holder, results, layer_color)

            if b_idx < len(batches)-1:
                time.sleep(BATCH_SLEEP)

    elif cond_type == "volume":
        min_vol = int(params["min_vol"])

        # 批次抓最近 1 天成交量（用 yfinance Volume 欄位）
        if layer_idx == 0:
            work_list = stock_subset
        else:
            work_list = [{
                "code":     r["代碼"],
                "name":     r["名稱"],
                "exchange": "TSE" if r["市場"]=="上市" else "OTC",
                "_row":     r,
            } for r in stock_subset]

        total   = len(work_list)
        batches = [work_list[i:i+BATCH_SIZE] for i in range(0, total, BATCH_SIZE)]
        processed = 0

        end_dt    = datetime.date.today()
        start_dt  = end_dt - datetime.timedelta(days=10)
        end_str   = str(end_dt + datetime.timedelta(days=1))
        start_str = str(start_dt)

        for b_idx, batch in enumerate(batches):
            tickers    = [yf_ticker(s["code"], s["exchange"]) for s in batch]
            ticker_map = {yf_ticker(s["code"], s["exchange"]): s for s in batch}

            # 下載 Volume 資料
            try:
                raw = yf.download(
                    tickers=tickers, start=start_str, end=end_str,
                    interval="1d", auto_adjust=True, progress=False, threads=True,
                )
                if not raw.empty and isinstance(raw.columns, pd.MultiIndex):
                    vol_df = raw["Volume"].copy() if "Volume" in raw.columns.get_level_values(0) else pd.DataFrame()
                elif not raw.empty and "Volume" in raw.columns:
                    vol_df = raw[["Volume"]].rename(columns={"Volume": tickers[0]})
                else:
                    vol_df = pd.DataFrame()
            except:
                vol_df = pd.DataFrame()

            for tk, info in ticker_map.items():
                processed += 1
                progress_bar.progress(
                    min(processed/total, 1.0),
                    text=f"[第{layer_idx+1}層] 批次{b_idx+1}/{len(batches)} ｜ {processed}/{total} ｜ {info['code']} {info['name']}"
                )

                if vol_df.empty or tk not in vol_df.columns:
                    continue

                v_vals = vol_df[tk].dropna().values
                if len(v_vals) == 0: continue
                # yfinance Volume 是「股」，台股 1 張 = 1000 股
                last_vol_shares = float(v_vals[-1])
                last_vol_lots   = last_vol_shares / 1000.0

                if last_vol_lots < min_vol: continue

                if layer_idx == 0:
                    row = {
                        "代碼":       info["code"],
                        "名稱":       info["name"],
                        "市場":       "上市" if info["exchange"]=="TSE" else "上櫃",
                        "最後收盤":   None,
                        "漲跌幅(%)":  None,
                        "成交量(張)": round(last_vol_lots),
                        "layer":      layer_idx+1,
                        "資料來源":   "yfinance",
                    }
                else:
                    row = info["_row"].copy()
                    row["成交量(張)"] = round(last_vol_lots)
                    row["layer"]     = layer_idx+1

                results.append(row)
                _show_live_funnel(live_holder, results, layer_color)

            if b_idx < len(batches)-1:
                time.sleep(BATCH_SLEEP)

    # ── 指定時間點漲跌幅篩選 ──────────────────────────────
    elif cond_type == "intraday_change":
        direction     = params["direction"]      # "下跌" | "上漲"
        pct_threshold = float(params["pct_threshold"])
        is_live       = bool(params.get("is_live", False))  # True = 開盤中，用永豐

        # 決定工作清單
        if layer_idx == 0:
            work_list = stock_subset
        else:
            work_list = [{
                "code":     r["代碼"],
                "name":     r["名稱"],
                "exchange": "TSE" if r["市場"]=="上市" else "OTC",
                "_row":     r,
            } for r in stock_subset]

        total     = len(work_list)
        processed = 0

        if is_live:
            # ── 開盤中：用永豐 snapshot 批次抓取 ──────────
            # 永豐 snapshot change_rate 就是相對前一日收盤的即時漲跌幅
            _api = params["_api"]   # 傳入 api 物件
            SNAP_BATCH = 200        # 永豐 snapshot 一次最多約 200 檔

            snap_batches = [work_list[i:i+SNAP_BATCH] for i in range(0, total, SNAP_BATCH)]
            for b_idx, batch in enumerate(snap_batches):
                contracts_batch = []
                info_batch      = []
                for s in batch:
                    processed += 1
                    c = get_tw_contract(_api, s["code"])
                    if c:
                        contracts_batch.append(c)
                        info_batch.append(s)

                progress_bar.progress(
                    min(processed/total, 1.0),
                    text=f"[第{layer_idx+1}層-即時] {processed}/{total}"
                )

                if not contracts_batch:
                    continue

                try:
                    snaps = _api.snapshots(contracts_batch)
                except Exception:
                    continue

                for c_obj, snap, info in zip(contracts_batch, snaps, info_batch):
                    rate = getattr(snap, "change_rate", None)
                    if rate is None: continue
                    rate = float(rate)

                    hit = (direction=="下跌" and rate<=-pct_threshold) or \
                          (direction=="上漲" and rate>= pct_threshold)
                    if not hit: continue

                    close_live = float(getattr(snap, "close", 0) or 0)

                    if layer_idx == 0:
                        row = {
                            "代碼":         info["code"],
                            "名稱":         info["name"],
                            "市場":         "上市" if info["exchange"]=="TSE" else "上櫃",
                            "最後收盤":     round(close_live, 2) if close_live else None,
                            "漲跌幅(%)":    round(rate, 2),
                            "盤中漲跌幅(%)": round(rate, 2),
                            "成交量(張)":   None,
                            "layer":        layer_idx+1,
                            "資料來源":     "shioaji_live",
                        }
                    else:
                        row = info["_row"].copy()
                        row["盤中漲跌幅(%)"] = round(rate, 2)
                        row["最後收盤"]      = round(close_live, 2) if close_live else row.get("最後收盤")
                        row["layer"]         = layer_idx+1
                        row["資料來源"]      = "shioaji_live"

                    results.append(row)
                    _show_live_funnel(live_holder, results, layer_color)

        else:
            # ── 收盤後：yfinance 1 分鐘線 ──────────────────
            target_hour   = int(params["target_hour"])
            target_min    = int(params["target_min"])
            trading_date  = _last_trading_date()

            batches = [work_list[i:i+BATCH_SIZE] for i in range(0, total, BATCH_SIZE)]

            for b_idx, batch in enumerate(batches):
                tickers    = [yf_ticker(s["code"], s["exchange"]) for s in batch]
                ticker_map = {yf_ticker(s["code"], s["exchange"]): s for s in batch}

                processed += len(batch)
                progress_bar.progress(
                    min(processed/total, 1.0),
                    text=f"[第{layer_idx+1}層] 批次{b_idx+1}/{len(batches)} ｜ {processed}/{total} ｜ 抓取 {trading_date} {target_hour:02d}:{target_min:02d} 分K"
                )

                intra_map = fetch_intraday_batch(tickers, target_hour, target_min, trading_date)

                for tk, info in ticker_map.items():
                    data = intra_map.get(tk)
                    if data is None: continue

                    pct = data["pct"]
                    hit = (direction=="下跌" and pct<=-pct_threshold) or \
                          (direction=="上漲" and pct>= pct_threshold)
                    if not hit: continue

                    if layer_idx == 0:
                        row = {
                            "代碼":         info["code"],
                            "名稱":         info["name"],
                            "市場":         "上市" if info["exchange"]=="TSE" else "上櫃",
                            "最後收盤":     data["intraday_price"],
                            "漲跌幅(%)":    round(pct, 2),
                            "盤中漲跌幅(%)": round(pct, 2),
                            "盤中時間":     f"{trading_date} {target_hour:02d}:{target_min:02d}",
                            "成交量(張)":   None,
                            "layer":        layer_idx+1,
                            "資料來源":     "yfinance_1m",
                        }
                    else:
                        row = info["_row"].copy()
                        row["盤中漲跌幅(%)"] = round(pct, 2)
                        row["盤中時間"]      = f"{trading_date} {target_hour:02d}:{target_min:02d}"
                        row["最後收盤"]      = data["intraday_price"]
                        row["layer"]         = layer_idx+1
                        row["資料來源"]      = "yfinance_1m"

                    results.append(row)
                    _show_live_funnel(live_holder, results, layer_color)

                if b_idx < len(batches)-1:
                    time.sleep(BATCH_SLEEP)

    return results


def _show_live_funnel(container, results, layer_color):
    """掃描過程即時顯示"""
    html = (f'<div style="font-family:JetBrains Mono,monospace;font-size:0.62rem;'
            f'color:#4a5568;margin-bottom:0.4rem;">&#x2705; 已找到 {len(results)} 檔</div>')
    for r in results[-20:]:
        pct   = r.get("盤中漲跌幅(%)") if r.get("盤中漲跌幅(%)") is not None else r.get("漲跌幅(%)")
        pct_s = f"{pct:+.2f}%" if pct is not None else "—"
        # 台股：上漲=紅，下跌=綠
        pct_cls = "rpct-down" if (pct or 0) < 0 else "rpct-up"
        vol   = r.get("成交量(張)")
        vol_s = f" | {int(vol):,}張" if vol else ""
        close = r.get("最後收盤")
        close_s = f"{close:.2f}" if close else "—"
        intra_time = r.get("盤中時間") or ""
        time_s = f" &#x23F1;{intra_time}" if intra_time else ""
        html += (
            '<div class="result-row result-row-' + layer_color + '">'
            + '<div style="display:flex;align-items:center;">'
            + '<span class="rcode rcode-' + layer_color + '">' + r["代碼"] + "</span>"
            + '<span class="rname">' + r["名稱"] + "</span>"
            + '<span class="rprice">收 ' + close_s + vol_s + time_s + "</span>"
            + "</div>"
            + '<span class="' + pct_cls + '">' + pct_s + "</span>"
            + "</div>"
        )
    container.markdown(html, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════
#  開盤補充永豐即時
# ══════════════════════════════════════════════════════════
def enrich_realtime(api, results):
    if not results: return results
    contracts = []
    for r in results:
        c = get_tw_contract(api, r["代碼"])
        if c: contracts.append(c)
    snap_map = {}
    if contracts:
        try:
            snaps = api.snapshots(contracts)
            for c, snap in zip(contracts, snaps):
                snap_map[c.code] = snap
        except: pass
    enriched = []
    for r in results:
        snap = snap_map.get(r["代碼"])
        if snap and getattr(snap,"close",0) and snap.close>0:
            r = r.copy()
            r["最後收盤"]  = round(float(snap.close), 2)
            r["今日漲跌%"] = round(float(getattr(snap,"change_rate",0)), 2)
            r["成交量(張)"] = round(float(getattr(snap,"total_volume",0))/1000) if getattr(snap,"total_volume",None) else r.get("成交量(張)")
            r["資料來源"]  = "shioaji_live"
        enriched.append(r)
    return enriched

# ══════════════════════════════════════════════════════════
#  自選卡片渲染
# ══════════════════════════════════════════════════════════
def render_card(snap, contract):
    change = snap.change_price
    rate   = snap.change_rate
    close  = snap.close
    if change>0: cls,arrow,sign = "up","▲","+"
    elif change<0: cls,arrow,sign = "down","▼",""
    else: cls,arrow,sign = "flat","—",""
    name = getattr(contract,"name",contract.code)
    return f"""
<div class="stock-card {cls}">
  <div class="card-top">
    <div><div class="stock-code">{contract.code}</div><div class="stock-name">{name}</div></div>
    <span class="exchange-badge badge-tw">🇹🇼 TW</span>
  </div>
  <div class="card-price-row">
    <div class="price-main {cls}">{close:.2f} <span style="font-size:.65rem;color:#4a5568;">TWD</span></div>
    <div class="change-block">
      <span class="change-val {cls}">{sign}{change:.2f}</span>
      <span class="change-pct {cls}">{arrow} {sign}{rate:.2f}%</span>
    </div>
  </div>
  <div class="card-stats">
    <div class="stat-item"><span class="stat-label">最高</span><span class="stat-val">{snap.high:.2f}</span></div>
    <div class="stat-item"><span class="stat-label">最低</span><span class="stat-val">{snap.low:.2f}</span></div>
    <div class="stat-item"><span class="stat-label">均價</span><span class="stat-val">{snap.average_price:.2f}</span></div>
    <div class="stat-item"><span class="stat-label">成交量</span><span class="stat-val">{snap.total_volume:,}</span></div>
  </div>
</div>"""

def render_card_yf(code, name, close_val, chg_pct):
    # 台股：上漲=紅(up)，下跌=綠(down)
    cls   = "up" if (chg_pct or 0) > 0 else ("down" if (chg_pct or 0) < 0 else "flat")
    arrow = "▲" if cls == "up" else ("▼" if cls == "down" else "—")
    sign  = "+" if cls == "up" else ""
    chg_s = f"{sign}{chg_pct:.2f}%" if chg_pct is not None else "—"
    return (
        '<div class="stock-card ' + cls + '">'
        + '<div class="card-top">'
        + '<div><div class="stock-code">' + code + '</div>'
        + '<div class="stock-name">' + name + '</div></div>'
        + '<span class="exchange-badge badge-tw">&#x1F1F9;&#x1F1FC; TW</span>'
        + '</div>'
        + '<div class="card-price-row">'
        + '<div class="price-main ' + cls + '">' + f"{close_val:.2f}"
        + ' <span style="font-size:.65rem;color:#4a5568;">TWD</span></div>'
        + '<div class="change-block">'
        + '<span class="change-pct ' + cls + '">' + arrow + " " + chg_s + '</span>'
        + '<span style="font-family:JetBrains Mono,monospace;font-size:0.55rem;color:#4a5568;">昨→今收盤</span>'
        + '</div></div></div>'
    )


# ══════════════════════════════════════════════════════════
#  條件參數輸入 UI（回傳 params dict 或 None）
# ══════════════════════════════════════════════════════════
def render_cond_params(cond_type: str, key_prefix: str) -> dict:
    """依條件類型渲染參數輸入欄，回傳 params dict"""
    if cond_type == "price_change":
        c1, c2, c3 = st.columns([2,2,2])
        with c1:
            n_days = st.number_input(
                "前幾個交易日", min_value=1, max_value=60, value=5, step=1,
                key=f"{key_prefix}_ndays",
            )
        with c2:
            direction = st.selectbox(
                "漲跌方向", ["下跌","上漲"], index=0,
                key=f"{key_prefix}_dir",
            )
        with c3:
            pct = st.number_input(
                f"{'跌幅' if direction=='下跌' else '漲幅'} ≥ %",
                min_value=0.1, max_value=100.0, value=10.0, step=0.5, format="%.1f",
                key=f"{key_prefix}_pct",
            )
        sym = "📉" if direction=="下跌" else "📈"
        st.caption(f"{sym} 前 **{int(n_days)}** 個交易日 **{direction}** ≥ **{pct:.1f}%**")
        return {"n_days": int(n_days), "direction": direction, "pct_threshold": pct}

    elif cond_type == "volume":
        c1, _ = st.columns([2,4])
        with c1:
            min_vol = st.number_input(
                "最低成交張數", min_value=1, max_value=1000000, value=1000, step=100,
                key=f"{key_prefix}_vol",
                help="單位：張（1張=1000股）",
            )
        st.caption(f"📊 成交量 ≥ **{int(min_vol):,}** 張")
        return {"min_vol": int(min_vol)}

    elif cond_type == "intraday_change":
        # 判斷現在是開盤中還是收盤後，決定 UI 模式
        if is_tw_market_open():
            # ── 開盤中：只能選漲跌方向 + 幅度，時間固定為「現在」
            st.info("📡 **開盤中模式**：篩選當下即時漲跌幅（永豐 API），時間固定為現在，無需選擇。", icon="⚡")
            c1, c2 = st.columns([2,2])
            with c1:
                direction = st.selectbox("漲跌方向", ["下跌","上漲"], index=0, key=f"{key_prefix}_id_dir")
            with c2:
                pct = st.number_input(
                    f"{'跌幅' if direction=='下跌' else '漲幅'} ≥ %",
                    min_value=0.1, max_value=100.0, value=3.0, step=0.5, format="%.1f",
                    key=f"{key_prefix}_id_pct",
                )
            sym = "📉" if direction=="下跌" else "📈"
            st.caption(f"{sym} 即時 **{direction}** ≥ **{pct:.1f}%**（永豐即時快照）")
            return {
                "direction":     direction,
                "pct_threshold": pct,
                "target_hour":   None,
                "target_min":    None,
                "is_live":       True,
            }
        else:
            # ── 收盤後：可指定時間點
            tz_tw   = pytz.timezone("Asia/Taipei")
            now_tw  = datetime.datetime.now(tz_tw)
            trading = _last_trading_date()

            st.info(
                f"🌙 **收盤後模式**：以 yfinance 1 分鐘線篩選  "
                f"**{trading}** 指定時間點的漲跌幅",
                icon="📅",
            )
            c1, c2, c3 = st.columns([2,2,2])
            with c1:
                direction = st.selectbox("漲跌方向", ["下跌","上漲"], index=0, key=f"{key_prefix}_id_dir")
            with c2:
                t_hour = st.number_input(
                    "時（點）", min_value=9, max_value=13, value=13, step=1,
                    key=f"{key_prefix}_id_hr",
                    help="台灣時間，範圍 09~13",
                )
            with c3:
                # 時間限制：09:00 ~ 13:30
                max_min = 30 if int(t_hour) == 13 else 59
                t_min = st.number_input(
                    "分", min_value=0, max_value=max_min, value=20, step=1,
                    key=f"{key_prefix}_id_min",
                )
            pct = st.number_input(
                f"{'跌幅' if direction=='下跌' else '漲幅'} ≥ %",
                min_value=0.1, max_value=100.0, value=3.0, step=0.5, format="%.1f",
                key=f"{key_prefix}_id_pct",
            )
            sym = "📉" if direction=="下跌" else "📈"
            st.caption(
                f"{sym} {trading} **{int(t_hour):02d}:{int(t_min):02d}** "
                f"**{direction}** ≥ **{pct:.1f}%**（vs 前日收盤，ffill 填補無成交）"
            )
            return {
                "direction":     direction,
                "pct_threshold": pct,
                "target_hour":   int(t_hour),
                "target_min":    int(t_min),
                "is_live":       False,
            }

    return {}


def cond_label(cond_type: str, params: dict) -> str:
    """條件的簡短文字描述"""
    if cond_type == "price_change":
        sym = "📉" if params["direction"]=="下跌" else "📈"
        return f"{sym} 前{params['n_days']}日{params['direction']}≥{params['pct_threshold']:.1f}%"
    elif cond_type == "volume":
        return f"📊 成交≥{params['min_vol']:,}張"
    elif cond_type == "intraday_change":
        sym = "📉" if params["direction"]=="下跌" else "📈"
        if params.get("is_live"):
            return f"⚡ 即時{params['direction']}≥{params['pct_threshold']:.1f}%"
        else:
            return (f"⏱ {params['target_hour']:02d}:{params['target_min']:02d} "
                    f"{params['direction']}≥{params['pct_threshold']:.1f}%")
    return cond_type


# ══════════════════════════════════════════════════════════
#  漏斗結果渲染
# ══════════════════════════════════════════════════════════
def render_funnel_results(layers: list):
    """
    layers: list of { cond_type, params, results: list[dict] }
    結果排序：layer 數字越小（越精準）排越前面
    """
    if not any(l.get("results") for l in layers):
        return

    # 收集所有結果，按 layer 升序（layer 1 最精 → 最前）
    # 每個股票只出現一次（取最高層次）
    # 實際上同一股票可能通過多層，取最大 layer
    code_to_best = {}
    for layer_dict in layers:
        res = layer_dict.get("results") or []
        for r in res:
            code = r["代碼"]
            if code not in code_to_best or r["layer"] > code_to_best[code]["layer"]:
                code_to_best[code] = r

    all_results = list(code_to_best.values())
    if not all_results:
        st.info("🔎 未找到符合條件的股票。")
        return

    # 依 layer 降序（最多層通過的排最前），同層依漲跌幅排序
    def sort_key(r):
        layer = r.get("layer", 1)
        pct   = r.get("漲跌幅(%)", 0) or 0
        return (-layer, -abs(pct))

    all_results.sort(key=sort_key)

    # 圖例說明
    legend_html = '<div style="display:flex;gap:0.5rem;flex-wrap:wrap;margin-bottom:0.7rem;">'
    for i, layer_dict in enumerate(layers):
        if not layer_dict.get("results"): continue
        c   = LAYER_COLORS[min(i,4)]
        lbl = cond_label(layer_dict["cond_type"], layer_dict["params"])
        cnt = len(layer_dict.get("results") or [])
        legend_html += f'<span class="result-section-hdr rsh-{c}">{LAYER_ICONS[i]} 第{i+1}層 {lbl} ({cnt}檔)</span>'
    legend_html += '</div>'
    st.markdown(legend_html, unsafe_allow_html=True)

    # 表格
    df_rows = []
    for r in all_results:
        df_rows.append({
            "層次":      f"第{r.get('layer',1)}層",
            "代碼":      r["代碼"],
            "名稱":      r["名稱"],
            "市場":      r["市場"],
            "漲跌幅(%)": r.get("漲跌幅(%)"),
            "盤中漲跌幅(%)": r.get("盤中漲跌幅(%)"),
            "盤中時間":  r.get("盤中時間"),
            "收盤價":    r.get("最後收盤"),
            "成交量(張)": r.get("成交量(張)"),
        })
    df = pd.DataFrame(df_rows)
    # 只顯示有資料的欄位
    show_cols = ["層次","代碼","名稱","市場","漲跌幅(%)","盤中漲跌幅(%)","盤中時間","收盤價","成交量(張)"]
    show_cols = [c for c in show_cols if c in df.columns and df[c].notna().any()]
    st.dataframe(
        df[show_cols], use_container_width=True, hide_index=True,
        column_config={
            "層次":          st.column_config.TextColumn("層次",     width=65),
            "代碼":          st.column_config.TextColumn("代碼",     width=70),
            "名稱":          st.column_config.TextColumn("名稱",     width=110),
            "市場":          st.column_config.TextColumn("市場",     width=65),
            "漲跌幅(%)":     st.column_config.NumberColumn("前N日漲跌%",  format="%.2f", width=110),
            "盤中漲跌幅(%)": st.column_config.NumberColumn("盤中漲跌%",   format="%.2f", width=110),
            "盤中時間":      st.column_config.TextColumn("盤中時間",  width=130),
            "收盤價":        st.column_config.NumberColumn("收盤",    format="%.2f", width=80),
            "成交量(張)":    st.column_config.NumberColumn("成交量(張)", format="%d",   width=100),
        }
    )

    # 卡片列表（分層顯示）
    st.markdown('<div class="section-title" style="margin-top:1rem;">詳細列表（層次越高 = 通過條件越多）</div>', unsafe_allow_html=True)
    for r in all_results:
        layer     = r.get("layer", 1)
        c         = LAYER_COLORS[min(layer-1, 4)]
        pct       = r.get("漲跌幅(%)")
        intra_pct = r.get("盤中漲跌幅(%)")

        # 優先顯示盤中，其次前N日
        disp_pct  = intra_pct if intra_pct is not None else pct
        pct_s     = f"{disp_pct:+.2f}%" if disp_pct is not None else "—"
        # 台股：上漲=紅(rpct-up)，下跌=綠(rpct-down)
        pct_cls   = "rpct-down" if (disp_pct or 0) < 0 else "rpct-up"

        vol    = r.get("成交量(張)")
        close  = r.get("最後收盤")
        close_s = f"{close:.2f}" if close else "—"
        mkt    = "上市" if r["市場"] == "上市" else "上櫃"
        src    = r.get("資料來源", "yfinance")

        if src == "shioaji_live":
            src_badge = '<span class="ds-live">LIVE</span>'
        elif src == "yfinance_1m":
            src_badge = '<span class="ds-yf">yf&#xB7;1m</span>'
        else:
            src_badge = '<span class="ds-yf">yf</span>'

        # 盤中時間 — 純文字組裝，不用巢狀 f-string 引號
        intra_time = r.get("盤中時間") or ""
        intra_s = ""
        if intra_time:
            intra_s = (
                '<span style="font-size:.68rem;color:#94a3b8;margin-left:0.4rem;">'
                + "&#x23F1;" + str(intra_time)
                + "</span>"
            )

        # 成交量
        vol_s = ""
        if vol:
            vol_s = '<span class="rprice">' + f"{int(vol):,}張" + "</span>"

        # 若同時有前N日 & 盤中，額外顯示前N日（小字）
        pct_extra = ""
        if pct is not None and intra_pct is not None:
            pct_cls2  = "rpct-down" if pct < 0 else "rpct-up"
            pct_extra = (
                '<span class="' + pct_cls2
                + '" style="font-size:0.72rem;opacity:0.7;">'
                + f"{pct:+.2f}%前N日"
                + "</span>"
            )

        html = (
            '<div class="result-row result-row-' + c + '">'
            + '<div style="display:flex;align-items:center;flex-wrap:wrap;gap:0.25rem;">'
            + '<span class="layer-badge layer-badge-' + c + '">L' + str(layer) + "</span>"
            + '<span class="rcode rcode-' + c + '">' + r["代碼"] + "</span>"
            + '<span class="rname">' + r["名稱"] + "</span>"
            + '<span class="rprice">收 ' + close_s + "</span>"
            + vol_s
            + intra_s
            + "</div>"
            + '<div style="display:flex;align-items:center;gap:0.5rem;flex-wrap:wrap;">'
            + '<span class="rmkt">' + mkt + "</span>"
            + src_badge
            + pct_extra
            + '<span class="' + pct_cls + '">' + pct_s + "</span>"
            + "</div>"
            + "</div>"
        )
        st.markdown(html, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════
#  ── 主頁面 ──
# ══════════════════════════════════════════════════════════
st.markdown('<div class="app-title">📊 Stock Monitor</div>', unsafe_allow_html=True)

api, accounts = init_shioaji()
if api is None:
    st.error("❌ API 初始化失敗")
    st.stop()

s_ok = any("Stock"  in type(a).__name__ and getattr(a,"signed",False) for a in accounts)
f_ok = any("Future" in type(a).__name__ and getattr(a,"signed",False) for a in accounts)
s_b  = f'<span class="signed-badge {"signed-ok" if s_ok else "signed-no"}">{"✓ 證券" if s_ok else "✗ 證券"}</span>'
f_b  = f'<span class="signed-badge {"signed-ok" if f_ok else "signed-no"}">{"✓ 期貨" if f_ok else "✗ 期貨"}</span>'
st.markdown(
    f'<div class="status-bar"><div><span class="status-dot"></span>'
    f'<span class="status-text">PRODUCTION &nbsp;|&nbsp;</span>{s_b}&nbsp;{f_b}</div></div>',
    unsafe_allow_html=True
)
st.markdown(render_clocks(), unsafe_allow_html=True)

col_r1, col_r2 = st.columns([3,2])
with col_r1: auto_refresh = st.toggle("自動更新", value=True)
with col_r2: refresh_sec  = st.select_slider("", options=[10,15,30,60], value=15, label_visibility="collapsed")
market_open_now = is_tw_market_open()

# ════════════════════════════════════════════════════════════
#  台股自選
# ════════════════════════════════════════════════════════════
st.markdown('<div class="section-title">🇹🇼 台股自選</div>', unsafe_allow_html=True)
col_in, col_btn = st.columns([4,1])
with col_in:
    new_tw = st.text_input("", placeholder="輸入台股代碼（如 2330）", key="input_tw", label_visibility="collapsed")
with col_btn:
    st.write("")
    if st.button("＋ 新增", key="add_tw"):
        code = new_tw.strip()
        if code and code not in st.session_state.tw_watchlist:
            st.session_state.tw_watchlist.append(code); st.rerun()

tw_ok, tw_fail = [], []
for code in st.session_state.tw_watchlist:
    c = get_tw_contract(api, code)
    if c: tw_ok.append((code,c))
    else: tw_fail.append(code)
if tw_fail: st.warning(f"找不到台股代碼：{', '.join(tw_fail)}")
if tw_ok:
    if market_open_now:
        try:
            snaps = api.snapshots([c for _,c in tw_ok])
            for i,(code,contract) in enumerate(tw_ok):
                cc, cd = st.columns([10,1])
                with cc: st.markdown(render_card(snaps[i],contract), unsafe_allow_html=True)
                with cd:
                    st.write(""); st.write("")
                    if st.button("✕", key=f"del_tw_{code}"):
                        st.session_state.tw_watchlist.remove(code); st.rerun()
        except Exception as e: st.error(f"台股查詢錯誤：{e}")
    else:
        st.caption("🌙 收盤後模式（yfinance）")
        today_yf = datetime.date.today()
        tickers_w = [yf_ticker(code,"TSE") for code,_ in tw_ok]
        try:
            cw = fetch_batch_closes(tickers_w, str(today_yf-datetime.timedelta(days=10)), str(today_yf+datetime.timedelta(days=1)))
            for code,contract in tw_ok:
                name = getattr(contract,"name",code)
                cv,cp = None,None
                for exch in ["TSE","OTC"]:
                    tk = yf_ticker(code,exch)
                    if not cw.empty and tk in cw.columns:
                        s = cw[tk].dropna()
                        if len(s)>=2: cv,cp = float(s.values[-1]), float((s.values[-1]-s.values[-2])/s.values[-2]*100)
                        elif len(s)==1: cv=float(s.values[-1])
                        break
                cc, cd = st.columns([10,1])
                with cc:
                    if cv: st.markdown(render_card_yf(code,name,cv,cp), unsafe_allow_html=True)
                    else: st.warning(f"⚠️ {code} {name} 無收盤資料")
                with cd:
                    st.write(""); st.write("")
                    if st.button("✕", key=f"del_tw_{code}"):
                        st.session_state.tw_watchlist.remove(code); st.rerun()
        except Exception as e: st.error(f"yfinance 查詢錯誤：{e}")


# ════════════════════════════════════════════════════════════
#  🔍 動態過濾漏斗篩選器
# ════════════════════════════════════════════════════════════
st.markdown('<div class="section-title">🔍 動態過濾漏斗（台股上市 ＋ 上櫃）</div>', unsafe_allow_html=True)

if market_open_now:
    st.caption("📡 開盤中：yfinance 歷史篩選 ＋ 永豐即時補充")
else:
    st.caption("🌙 收盤後：yfinance 批次篩選（批次50檔，間隔1.5s）")

# ── 取得全市場清單（僅做一次）────────────────────────────
if st.session_state.all_stocks_cache is None:
    with st.spinner("載入台股清單..."):
        st.session_state.all_stocks_cache = get_all_tw_stock_list(api)
all_stocks = st.session_state.all_stocks_cache

# ── 已使用條件類型集合（用於禁用選單）────────────────────
used_cond_types = set(l["cond_type"] for l in st.session_state.funnel_layers)

# ══════════════════════════════════════════════════════════
#  逐層顯示已設定的條件 ＋ 執行按鈕
# ══════════════════════════════════════════════════════════
for i, layer in enumerate(st.session_state.funnel_layers):
    color = LAYER_COLORS[min(i,4)]
    icon  = LAYER_ICONS[i]
    lbl   = cond_label(layer["cond_type"], layer["params"])
    has_result = bool(layer.get("results"))

    with st.expander(
        f"{icon} 第{i+1}層篩選：{lbl}  {'✅ ' + str(len(layer['results'])) + ' 檔' if has_result else '⏳ 尚未執行'}",
        expanded=not has_result,
    ):
        st.markdown(
            f'<div class="funnel-step funnel-step-{color}">'
            f'<div class="funnel-step-label lbl-{color}">{icon} 第 {i+1} 層條件</div>',
            unsafe_allow_html=True,
        )

        # 條件描述（已鎖定，不可修改）
        st.info(f"條件：{lbl}", icon="🔒")

        col_run, col_del = st.columns([3,1])
        with col_run:
            if st.button(f"🚀 執行第{i+1}層篩選", key=f"run_layer_{i}", use_container_width=True):
                # 決定輸入清單：第1層用全市場，後續層用前一層結果
                if i == 0:
                    input_list = all_stocks
                else:
                    prev_results = st.session_state.funnel_layers[i-1].get("results") or []
                    if not prev_results:
                        st.warning(f"⚠️ 請先執行第{i}層篩選！")
                        st.stop()
                    input_list = prev_results

                prog = st.progress(0, text="準備中...")
                live = st.empty()

                # intraday_change 開盤模式需要傳入 api
                run_params = layer["params"].copy()
                if layer["cond_type"] == "intraday_change" and run_params.get("is_live"):
                    run_params["_api"] = api

                results = run_filter(
                    stock_subset    = input_list,
                    cond_type       = layer["cond_type"],
                    params          = run_params,
                    progress_bar    = prog,
                    live_holder     = live,
                    layer_idx       = i,
                    all_stocks_meta = {s["code"]:s for s in all_stocks},
                )

                prog.empty()
                live.empty()

                if market_open_now and results:
                    with st.spinner("📡 補充永豐即時資料..."):
                        results = enrich_realtime(api, results)

                st.session_state.funnel_layers[i]["results"] = results
                st.rerun()

        with col_del:
            if st.button(f"🗑 刪除", key=f"del_layer_{i}", use_container_width=True):
                st.session_state.funnel_layers.pop(i)
                st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

    # 漏斗連接線
    if i < len(st.session_state.funnel_layers)-1:
        next_lbl = cond_label(
            st.session_state.funnel_layers[i+1]["cond_type"],
            st.session_state.funnel_layers[i+1]["params"],
        )
        cnt = len(layer.get("results") or [])
        st.markdown(f"""
<div class="funnel-connector">
  <div class="funnel-connector-line"></div>
  <div class="funnel-connector-text">▼ {cnt} 檔進入下一層</div>
  <div class="funnel-connector-line"></div>
</div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
#  新增條件按鈕（下拉展開清單）
# ══════════════════════════════════════════════════════════
if len(st.session_state.funnel_layers) < MAX_LAYERS:
    next_layer_idx = len(st.session_state.funnel_layers)
    color_next     = LAYER_COLORS[min(next_layer_idx,4)]
    icon_next      = LAYER_ICONS[next_layer_idx]

    with st.expander(f"＋ 新增第 {next_layer_idx+1} 層篩選條件", expanded=(next_layer_idx==0)):
        st.markdown(
            f'<div class="funnel-step funnel-step-{color_next}">'
            f'<div class="funnel-step-label lbl-{color_next}">'
            f'{icon_next} 第 {next_layer_idx+1} 層  ·  選擇條件類型</div>',
            unsafe_allow_html=True,
        )

        # 條件選單（已用過的反白禁用）
        avail_options = {}
        for k, v in COND_TYPES.items():
            if k in used_cond_types:
                avail_options[k] = f"🚫 {v}（已使用）"
            else:
                avail_options[k] = v

        selected_cond = st.radio(
            "選擇篩選條件",
            options=list(COND_TYPES.keys()),
            format_func=lambda k: avail_options[k],
            key=f"new_cond_type_{next_layer_idx}",
            horizontal=True,
        )

        # 如果選到已使用的條件，阻擋
        if selected_cond in used_cond_types:
            st.warning(f"⚠️ 「{COND_TYPES[selected_cond]}」已在其他層使用，請選擇其他條件。")
        else:
            # 顯示參數輸入
            params = render_cond_params(selected_cond, key_prefix=f"new_layer_{next_layer_idx}")

            st.markdown('</div>', unsafe_allow_html=True)

            if st.button(f"✅ 確認新增第{next_layer_idx+1}層條件", key=f"confirm_layer_{next_layer_idx}", use_container_width=True):
                st.session_state.funnel_layers.append({
                    "cond_type": selected_cond,
                    "params":    params,
                    "results":   None,
                })
                st.rerun()
else:
    st.caption(f"已達最大層數 {MAX_LAYERS} 層")

# ── 全部清除 ──────────────────────────────────────────────
if st.session_state.funnel_layers:
    st.markdown("")
    if st.button("🗑 清除所有篩選條件與結果", key="clear_all_funnel"):
        st.session_state.funnel_layers = []
        st.rerun()

# ══════════════════════════════════════════════════════════
#  漏斗結果總覽
# ══════════════════════════════════════════════════════════
if any(l.get("results") for l in st.session_state.funnel_layers):
    st.markdown('<div class="section-title" style="margin-top:1.2rem;">📋 篩選結果總覽</div>', unsafe_allow_html=True)
    render_funnel_results(st.session_state.funnel_layers)


# ── 自動更新 ──────────────────────────────────────────────
if auto_refresh:
    st.caption(f"⏱ 每 {refresh_sec} 秒自動更新")
    time.sleep(refresh_sec)
    st.rerun()
