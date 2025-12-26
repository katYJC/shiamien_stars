import streamlit as st
import gspread
import json
from google.oauth2.service_account import Credentials
import time
import uuid
from streamlit_cookies_manager import EncryptedCookieManager

# =========================
# Page config
# =========================
st.set_page_config(
    page_title="原初之星計算器｜Season 2",
    page_icon="⭐",
    layout="wide"
)

# =========================
# 訪客節流設定：N 秒內同一人不重複計入
# =========================
THROTTLE_SECONDS = 10 * 60  # 10 分鐘（你可改成 5*60 等）

cookies = EncryptedCookieManager(
    prefix="shrimp_",
    password="PLEASE_CHANGE_THIS_TO_A_RANDOM_LONG_STRING_32+CHARS"
)
if not cookies.ready():
    st.stop()

# 產生/取得訪客ID（存在 cookie）
visitor_id = cookies.get("vid")
if not visitor_id:
    visitor_id = str(uuid.uuid4())
    cookies["vid"] = visitor_id

# 上次計入時間（存在 cookie）
last_counted = cookies.get("last_counted")
now = int(time.time())
last_counted_ts = int(last_counted) if last_counted and last_counted.isdigit() else 0

should_count = (now - last_counted_ts) > THROTTLE_SECONDS

# =========================
# 固定規則（不顯示給使用者）
# =========================
BASE_LV = 130
RELIC_BASE_LV = 13

BASE_STARS = 45       # 本季初始原初之星
CONVERT_DIV = 27      # 原初之星換算除數（總分 ÷ 27）

P_CHAR = 100          # 角色 +1 加分
P_EQUIP = 18          # 裝備 +1 加分
P_SKILL = 7           # 技能 +1 加分
P_BEAST = 8           # 幻獸 +1 加分
P_RELIC = 33          # 古遺物 +1 加分

EXP_TABLE = {
    131: 6791971, 132: 7349165, 133: 7896724, 134: 8431041, 135: 8948504,
    136: 9536985, 137: 10062872, 138: 10591166, 139: 11201308, 140: 11280750,
    141: 11334730, 142: 11387696, 143: 11440662, 144: 11493628, 145: 11546594,
    146: 11599560, 147: 11652526, 148: 11679009, 149: 11731975, 150: 11784941,
    151: 11811613, 152: 11838097, 153: 11864580, 154: 11917547, 155: 11970514,
    156: 12049964, 157: 12155898, 158: 12208865, 159: 12261832, 160: 12314799,
    161: 12394079, 162: 12447046, 163: 12500012, 164: 12500012, 165: 12526495,
    166: 12579461, 167: 12632427, 168: 12658910, 169: 12711876, 170: 12764842,
    171: 12817637, 172: 12870602, 173: 12950050, 174: 13029499, 175: 13082464,
    176: 13135429, 177: 13188395, 178: 13214878, 179: 13267843, 180: 13320809,
    181: 13372809, 182: 13399290, 183: 13425771, 184: 13452251, 185: 13478732,
    186: 13478732, 187: 13478732, 188: 13478732, 189: 13478732, 190: 13478732,
    191: 13478732, 192: 13478732, 193: 13478732, 194: 13478732, 195: 13478732,
    196: 13478732, 197: 13478732, 198: 13478732, 199: 13478732, 200: 13478732,
    201: 13478732, 202: 13478732, 203: 13478732, 204: 13478732, 205: 13478732,
    206: 13478732, 207: 13478732, 208: 13478732, 209: 13478732, 210: 13478732,
}

# =========================
# Styling
# =========================
st.markdown(
    """
    <style>
      .bulk-box {
        background: rgba(255, 193, 7, 0.10);
        border: 1px solid rgba(255, 193, 7, 0.35);
        border-left: 6px solid rgba(255, 193, 7, 0.85);
        padding: 12px 14px;
        border-radius: 12px;
        margin: 6px 0 10px 0;
      }
      .bulk-title { font-weight: 800; font-size: 0.98rem; }
      .bulk-hint  { color: rgba(0,0,0,0.6); font-size: 0.85rem; }
      /* 黑色模式：快速輸入說明文字 */
      [data-theme="dark"] .bulk-hint {
      color: #9BE7FF !important;   /* 淡藍色，黑底清楚 */
      }
      .brand-footer {
        margin-top: 48px;
        padding: 18px 12px;
        background: linear-gradient(90deg, rgba(255,193,7,0.15), rgba(255,193,7,0.04));
        border-top: 2px solid rgba(255,193,7,0.85);
        text-align: center;
        border-radius: 12px 12px 0 0;
      }
      .brand-title {
        font-size: 1.05rem;
        font-weight: 700;
        letter-spacing: 0.5px;
        margin-bottom: 2px;
      }
      .brand-author {
        font-size: 1.2rem;
        font-weight: 900;
        color: #ff9800;
      }
    </style>
    """,
    unsafe_allow_html=True,
)

# =========================
# Helper functions
# =========================
def effective_lv(lv: int) -> int:
    return max(0, lv - BASE_LV)
def effective_relic_lv(lv: int) -> int:
    return max(0, lv - RELIC_BASE_LV)
def get_visits_only():
    sa_info = json.loads(st.secrets["gcp"]["json"])
    creds = Credentials.from_service_account_info(sa_info, scopes=SCOPE)
    client = gspread.authorize(creds)
    ws = client.open_by_key(SPREADSHEET_ID).worksheet(SHEET_NAME)
    return int(ws.acell("A2").value)
def get_and_update_visits():
    sa_info = json.loads(st.secrets["gcp"]["json"])
    creds = Credentials.from_service_account_info(sa_info, scopes=SCOPE)

    client = gspread.authorize(creds)
    ws = client.open_by_key(SPREADSHEET_ID).worksheet(SHEET_NAME)

    count = int(ws.acell("A2").value)
    count += 1
    ws.update("A2", [[count]])
    return count

# =========================
# 全站訪客計數（Google Sheet）
# =========================
SCOPE = ["https://www.googleapis.com/auth/spreadsheets"]
SPREADSHEET_ID = "1F4fAB14ae2AxTPMGRnMqvh5BiouCdTKND8atqufWG98"
SHEET_NAME = "工作表1"

if "total_visits" not in st.session_state:
    st.session_state.total_visits = None

if should_count:
    # ✅ 只有超過節流時間才+1
    st.session_state.total_visits = get_and_update_visits()
    cookies["last_counted"] = str(now)
    cookies.save()
else:
    # ✅ 節流期間：不+1，但仍顯示目前總數（讀A2即可）
    # 建議你做一個只讀不寫的函式，避免多次寫入
    st.session_state.total_visits = get_visits_only()  # 你需要新增此函式

def get_grade(score: int) -> str:
    if score >= 15900:
        return "SSS"
    elif score >= 14500:
        return "SS"
    elif score >= 13100:
        return "S"
    elif score >= 10400:
        return "A"
    elif score >= 7600:
        return "B"
    elif score >= 4800:
        return "C"
    else:
        return "D"

def exp_percent_score(level: int, current_exp: int) -> tuple[int, int, int]:
    total = EXP_TABLE.get(level)
    if total is None or total <= 0:
        return 0, 0, 0
    cur = max(0, int(current_exp))
    if cur > total:
        cur = total
    pct = int((cur / total) * 100)  # 取整數（向下取整）
    return pct, pct, total


def apply_bulk(prefix: str, count: int):
    """
    只有在 bulk 值『真的改變』時才套用，
    套用後允許使用者微調單一欄位（不會被 rerun 覆蓋）
    """
    bulk_key = f"{prefix}_bulk"
    last_key = f"{prefix}_last_bulk"
    bulk_val = st.session_state.get(bulk_key)

    if st.session_state.get(last_key) == bulk_val:
        return

    for i in range(count):
        st.session_state[f"{prefix}_{i}"] = bulk_val

    st.session_state[last_key] = bulk_val

def bulk_ui(title: str, hint: str):
    st.markdown(
        f"""
        <div class="bulk-box">
          <div class="bulk-title">⚡ {title}</div>
          <div class="bulk-hint">{hint}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

# =========================
# Title
# =========================
st.title("⭐ 原初之星計算器｜Season 2")
st.caption("快速輸入只在變更時套用，其後可自由微調，分數會正確計算。")
# =========================
# 👀 全站拜訪人數
# =========================
st.caption(f"👀 全站累積拜訪次數：{st.session_state.total_visits:,}")

# =========================
# 上季原初之星（保留：用於最後合計）
# =========================
prev_season_stars = st.number_input("第1季原初之星", min_value=0, value=0, step=1)

# =========================
# 角色（含：等級加分 + 經驗%加分）
# 直接用這整段取代你原本的「角色」區塊即可
# （前提：你已經在上方加入 EXP_TABLE 與 exp_percent_score()）
# =========================
st.subheader("🧍 角色")

c1, c2 = st.columns(2)
with c1:
    char_lv = st.number_input(
        "目前角色等級（基礎 130）",
        value=130,
        min_value=1,
        step=1
    )
with c2:
    char_exp = st.number_input(
        "目前擁有經驗",
        value=0,
        min_value=0,
        step=1
    )

# 原本的等級加分（維持不變）
char_eff = effective_lv(int(char_lv))
score_char = char_eff * P_CHAR

# 新增：經驗%加分（依 EXP_TABLE）
exp_score, exp_pct, exp_total = exp_percent_score(int(char_lv), int(char_exp))

# （可選）提示文字：不想顯示可以整段刪掉
if exp_total == 0:
    st.caption("經驗%加分：此等級不在經驗表（目前支援 131～210），因此加分為 0。")
else:
    st.caption(f"經驗%加分：{int(char_exp):,} ÷ {exp_total:,} = {exp_pct}%（取整數）→ +{exp_score} 分")


# =========================
# 裝備（5）
# =========================
st.subheader("🛡 裝備（5）")
bulk_ui("裝備快速輸入（套用 5 欄）", "只在改變時覆蓋；套用後可再微調")

st.number_input(
    "equip_bulk_label",
    key="equip_bulk",
    value=130,
    min_value=1,
    step=1,
    label_visibility="collapsed",
    on_change=apply_bulk,
    kwargs={"prefix": "equip", "count": 5},
)

equip_eff = []
cols = st.columns(5)
for i in range(5):
    with cols[i]:
        lv = st.number_input(f"裝備 {i+1}", key=f"equip_{i}", value=130, min_value=1, step=1)
        equip_eff.append(effective_lv(lv))
score_equip = sum(equip_eff) * P_EQUIP

# =========================
# 技能（8）
# =========================
st.subheader("📘 技能（8）")
bulk_ui("技能快速輸入（套用 8 欄）", "只在改變時覆蓋；套用後可再微調")

st.number_input(
    "skill_bulk_label",
    key="skill_bulk",
    value=130,
    min_value=1,
    step=1,
    label_visibility="collapsed",
    on_change=apply_bulk,
    kwargs={"prefix": "skill", "count": 8},
)

skill_eff = []
cols = st.columns(4)
for i in range(8):
    with cols[i % 4]:
        lv = st.number_input(f"技能 {i+1}", key=f"skill_{i}", value=130, min_value=1, step=1)
        skill_eff.append(effective_lv(lv))
score_skill = sum(skill_eff) * P_SKILL

# =========================
# 幻獸（4）
# =========================
st.subheader("🐉 幻獸（4）")
bulk_ui("幻獸快速輸入（套用 4 欄）", "只在改變時覆蓋；套用後可再微調")

st.number_input(
    "beast_bulk_label",
    key="beast_bulk",
    value=130,
    min_value=1,
    step=1,
    label_visibility="collapsed",
    on_change=apply_bulk,
    kwargs={"prefix": "beast", "count": 4},
)

beast_eff = []
cols = st.columns(4)
for i in range(4):
    with cols[i]:
        lv = st.number_input(f"幻獸 {i+1}", key=f"beast_{i}", value=130, min_value=1, step=1)
        beast_eff.append(effective_lv(lv))
score_beast = sum(beast_eff) * P_BEAST

# =========================
# 古遺物（20，基礎 13；仍分光暗風水火顯示）
# =========================
st.subheader("🔮 古遺物（光 / 暗 / 風 / 水 / 火）")
bulk_ui("古遺物總快速輸入（套用 20 欄）", "基礎 13；只在改變時覆蓋；套用後可再微調")

st.number_input(
    "relic_bulk_label",
    key="relic_bulk",
    value=13,
    min_value=1,
    step=1,
    label_visibility="collapsed",
    on_change=apply_bulk,
    kwargs={"prefix": "relic", "count": 20},
)

elements = ["光", "暗", "風", "水", "火"]
relic_eff = []
idx = 0
for element in elements:
    st.markdown(f"### {element}")
    cols = st.columns(4)
    for i in range(4):
        with cols[i]:
            lv = st.number_input(
                f"{element}-{i+1}",
                key=f"relic_{idx}",
                value=13,
                min_value=1,
                step=1
            )
            relic_eff.append(effective_relic_lv(lv))
            idx += 1
score_relic = sum(relic_eff) * P_RELIC

# =========================
# Compute
# =========================
season_score = score_char + exp_score + score_equip + score_skill + score_beast + score_relic
season_grade = get_grade(season_score)

earned_stars = season_score // CONVERT_DIV
season_total_stars = BASE_STARS + earned_stars
grand_total_stars = prev_season_stars + season_total_stars

# =========================
# Output
# =========================
st.markdown("---")
st.subheader("📌 第 2 季結算")

m1, m2, m3, m4 = st.columns(4)
m1.metric("本季養成總分", f"{season_score:,}")
m2.metric("本季評級", season_grade)
m3.metric("本季獲得原初之星", f"{earned_stars:,}")
m4.metric("本季原初之星合計", f"{season_total_stars:,}")

st.markdown("### ⭐ 原初之星總計")
g1, g2 = st.columns(2)
g1.metric("上季原初之星", f"{prev_season_stars:,}")
g2.metric("總原初之星（上季 + 本季）", f"{grand_total_stars:,}")

with st.expander("📊 得分明細（各系統貢獻）"):
    st.write({
        "角色等級得分": score_char,
        "角色經驗%加分": exp_score,
        "裝備得分": score_equip,
        "技能得分": score_skill,
        "幻獸得分": score_beast,
        "古遺物得分": score_relic,
    })
    st.markdown("---")
    st.write({
        "本季養成總分": season_score,
        "本季評級": season_grade,
        "本季獲得原初之星": earned_stars,
        "本季原初之星合計": season_total_stars,
        "上季原初之星": prev_season_stars,
        "總原初之星": grand_total_stars,
    })

# =========================
# Brand Footer（方案二）
# =========================
st.markdown(
    """
    <div class="brand-footer">
        <div class="brand-title">原初之星計算器｜Season 2</div>
        <div class="brand-author">by 甜蝦麵(浮世千澤：夢 熱烈招生中！)</div>
    </div>
    """,
    unsafe_allow_html=True,
)

# =========================
# 💛 自由斗內（PayPal）
# =========================
st.markdown("---")
with st.expander("💛 自由斗內（支持作者）", expanded=False):
    st.write("如果這個工具對你有幫助，歡迎透過 PayPal 自由支持作者 🙏")
    st.link_button(
        "💳 使用 PayPal 支持",
        "https://paypal.me/katherinechou"
    )
    st.caption("※ 付款流程由 PayPal 處理，不會顯示你的銀行資訊。")

