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
      .bulk-hint  { font-size: 0.85rem; }     
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
      /* ✅ 黑色模式：強制改 hint 文字顏色（命中 span） */
      .stApp[data-theme="dark"] .bulk-hint-text,
      .stApp[data-theme="dark"] .bulk-hint-text * {
      color: #9BE7FF !important;
      }
      /* ✅ 保底：命中 Streamlit markdown 容器裡的 bulk-hint */
      .stApp[data-theme="dark"] div[data-testid="stMarkdownContainer"] .bulk-hint-text,
      .stApp[data-theme="dark"] div[data-testid="stMarkdownContainer"] .bulk-hint-text * {
      color: #9BE7FF !important;
      }
      .donate-box {
  margin-top: 32px;
  padding: 18px 14px;
  text-align: center;
  border-radius: 14px;
  background: linear-gradient(
    135deg,
    rgba(255,193,7,0.18),
    rgba(255,193,7,0.05)
  );
}

.donate-title {
  font-size: 1.05rem;
  font-weight: 800;
  margin-bottom: 6px;
}

.donate-text {
  font-size: 0.9rem;
  opacity: 0.85;
  margin-bottom: 12px;
}

.donate-btn {
  display: inline-block;
  background: #ffdd00;
  color: #000;
  padding: 10px 20px;
  border-radius: 22px;
  font-weight: 900;
  text-decoration: none;
}

.donate-btn:hover {
  transform: scale(1.03);
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
          <div class="bulk-hint"><span class="bulk-hint-text">{hint}</span></div>
        </div>
        """,
        unsafe_allow_html=True
    )

# =========================
# Tabs（不使用 sidebar）
# =========================
tab_main, tab_cost, tab_exp_forecast = st.tabs(["⭐ 原初之星計算器", "🧮 資源需求計算器", "📅 等級計算表(8:00)"])

with tab_main:
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
    #  Brand Footer（方案二）
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
    st.markdown(
        """
        <div class="donate-box">
          <div class="donate-title">☕ 支持開發者</div>
          <div class="donate-text">
            如果這個原初之星計算器幫助到你，<br>
            歡迎請我喝杯咖啡，讓工具持續更新 💛
          </div>
          <a href="https://buymeacoffee.com/katyjc"
             target="_blank"
             class="donate-btn">
            ☕ Buy Me a Coffee
          </a>
        </div>
        """,
        unsafe_allow_html=True
    )
with tab_cost:
    st.title("🧮 資源需求計算器")
    st.caption("輸入目前等級與目標等級，計算升級『需要消耗的資源總量』（不含已花費）。")

    # =========================
    # 資源表（你提供的資料）
    # =========================
    RELIC_COST = {
        14: {"rare_sand": 6750, "epic_sand": 1350, "lola": 60700},
        15: {"rare_sand": 7425, "epic_sand": 1485, "lola": 66800},
        16: {"rare_sand": 8100, "epic_sand": 1620, "lola": 72900},
        17: {"rare_sand": 8775, "epic_sand": 1755, "lola": 78900},
        18: {"rare_sand": 9450, "epic_sand": 1890, "lola": 85000},
        19: {"rare_sand": 10125, "epic_sand": 2025, "lola": 91100},
        20: {"rare_sand": 10800, "epic_sand": 2160, "lola": 97200},
        21: {"rare_sand": 11475, "epic_sand": 2295, "lola": 103300},
        22: {"rare_sand": 12150, "epic_sand": 2430, "lola": 109400},
        23: {"rare_sand": 12825, "epic_sand": 2565, "lola": 115500},
        24: {"rare_sand": 13500, "epic_sand": 2700, "lola": 121600},
        25: {"rare_sand": 14175, "epic_sand": 2835, "lola": 127700},
    }

    EQUIP_COST = {
        131: {"rough": 16500, "lola": 33200, "fine": 0},
        132: {"rough": 16700, "lola": 33500, "fine": 0},
        133: {"rough": 16900, "lola": 33900, "fine": 0},
        134: {"rough": 17100, "lola": 34200, "fine": 0},
        135: {"rough": 17200, "lola": 34500, "fine": 510},
        136: {"rough": 17400, "lola": 34900, "fine": 0},
        137: {"rough": 17600, "lola": 35200, "fine": 0},
        138: {"rough": 17700, "lola": 35500, "fine": 0},
        139: {"rough": 17900, "lola": 35900, "fine": 0},
        140: {"rough": 18100, "lola": 36200, "fine": 510},
        141: {"rough": 18200, "lola": 36500, "fine": 0},
        142: {"rough": 18400, "lola": 36900, "fine": 0},
        143: {"rough": 18600, "lola": 37200, "fine": 0},
        144: {"rough": 18700, "lola": 37500, "fine": 0},
        145: {"rough": 18900, "lola": 37900, "fine": 510},
        146: {"rough": 19100, "lola": 38200, "fine": 0},
        147: {"rough": 19200, "lola": 38500, "fine": 0},
        148: {"rough": 19400, "lola": 38900, "fine": 0},
        149: {"rough": 19600, "lola": 39200, "fine": 0},
        150: {"rough": 19700, "lola": 39500, "fine": 510},
        151: {"rough": 19900, "lola": 39900, "fine": 0},
        152: {"rough": 20100, "lola": 40200, "fine": 0},
        153: {"rough": 20200, "lola": 40500, "fine": 0},
        154: {"rough": 20400, "lola": 40900, "fine": 0},
        155: {"rough": 20600, "lola": 41200, "fine": 510},
        156: {"rough": 20700, "lola": 41500, "fine": 0},
        157: {"rough": 20900, "lola": 41900, "fine": 0},
        158: {"rough": 21100, "lola": 42200, "fine": 0},
        159: {"rough": 21200, "lola": 42500, "fine": 0},
        160: {"rough": 21400, "lola": 42900, "fine": 510},
        161: {"rough": 21600, "lola": 43200, "fine": 0},
        162: {"rough": 21700, "lola": 43500, "fine": 0},
        163: {"rough": 21900, "lola": 43900, "fine": 0},
        164: {"rough": 22100, "lola": 44200, "fine": 0},
        165: {"rough": 22200, "lola": 44500, "fine": 510},
        166: {"rough": 22400, "lola": 44900, "fine": 0},
        167: {"rough": 22600, "lola": 45200, "fine": 0},
        168: {"rough": 22700, "lola": 45500, "fine": 0},
        169: {"rough": 22900, "lola": 45900, "fine": 0},
        170: {"rough": 23100, "lola": 46200, "fine": 510},
        171: {"rough": 23200, "lola": 46500, "fine": 0},
        172: {"rough": 23400, "lola": 46900, "fine": 0},
        173: {"rough": 23600, "lola": 47200, "fine": 0},
        174: {"rough": 23700, "lola": 47500, "fine": 0},
        175: {"rough": 23900, "lola": 47900, "fine": 510},
        176: {"rough": 24100, "lola": 48200, "fine": 0},
        177: {"rough": 24200, "lola": 48500, "fine": 0},
        178: {"rough": 24400, "lola": 48900, "fine": 0},
        179: {"rough": 24600, "lola": 49200, "fine": 0},
        180: {"rough": 24700, "lola": 49500, "fine": 510},
        181: {"rough": 24900, "lola": 49900, "fine": 0},
        182: {"rough": 25100, "lola": 50200, "fine": 0},
        183: {"rough": 25200, "lola": 50500, "fine": 0},
        184: {"rough": 25400, "lola": 50900, "fine": 0},
        185: {"rough": 25600, "lola": 51200, "fine": 510},
        186: {"rough": 25700, "lola": 51500, "fine": 0},
        187: {"rough": 25900, "lola": 51900, "fine": 0},
        188: {"rough": 26100, "lola": 52200, "fine": 0},
        189: {"rough": 26200, "lola": 52500, "fine": 0},
        190: {"rough": 26400, "lola": 52900, "fine": 510},
        191: {"rough": 26600, "lola": 53200, "fine": 0},
        192: {"rough": 26700, "lola": 53500, "fine": 0},
        193: {"rough": 26900, "lola": 53900, "fine": 0},
        194: {"rough": 27100, "lola": 54200, "fine": 0},
        195: {"rough": 27200, "lola": 54500, "fine": 510},
        196: {"rough": 27400, "lola": 54900, "fine": 0},
        197: {"rough": 27600, "lola": 55200, "fine": 0},
        198: {"rough": 27700, "lola": 55500, "fine": 0},
        199: {"rough": 27900, "lola": 55900, "fine": 0},
        200: {"rough": 28100, "lola": 56200, "fine": 510},
        201: {"rough": 28200, "lola": 56500, "fine": 0},
        202: {"rough": 28400, "lola": 56900, "fine": 0},
        203: {"rough": 28600, "lola": 57200, "fine": 0},
        204: {"rough": 28700, "lola": 57500, "fine": 0},
        205: {"rough": 28900, "lola": 57900, "fine": 510},
        206: {"rough": 29100, "lola": 58200, "fine": 0},
        207: {"rough": 29200, "lola": 58500, "fine": 0},
        208: {"rough": 29400, "lola": 58900, "fine": 0},
        209: {"rough": 29600, "lola": 59200, "fine": 0},
        210: {"rough": 29700, "lola": 59500, "fine": 510},
    }

    BEAST_EXP = {
        131: 57300, 132: 58500, 133: 59600, 134: 60800, 135: 61900,
        136: 63100, 137: 64200, 138: 65400, 139: 66500, 140: 67700,
        141: 68800, 142: 69900, 143: 71100, 144: 72300, 145: 73400,
        146: 74600, 147: 75700, 148: 76800, 149: 78000, 150: 79200,
        151: 80300, 152: 81500, 153: 82600, 154: 83800, 155: 84900,
        156: 86100, 157: 87200, 158: 88400, 159: 89500, 160: 90700,
        161: 91800, 162: 93000, 163: 94100, 164: 95300, 165: 96400,
        166: 97600, 167: 98700, 168: 99900, 169: 101000, 170: 102200,
        171: 103300, 172: 104500, 173: 105600, 174: 106800, 175: 107900,
        176: 109100, 177: 110200, 178: 111400, 179: 112500, 180: 113700,
        181: 114800, 182: 116000, 183: 117100, 184: 118300, 185: 119400,
        186: 120600, 187: 121700, 188: 122900, 189: 124000, 190: 125200,
        191: 126300, 192: 127500, 193: 128600, 194: 129800, 195: 130900,
        196: 132100, 197: 133200, 198: 134400, 199: 135500, 200: 136700,
        201: 137800, 202: 139000, 203: 140100, 204: 141300, 205: 142400,
        206: 143600, 207: 144700, 208: 145900, 209: 147000, 210: 148200,
    }

    SKILL_ESSENCE = {
        131: 12120, 132: 12240, 133: 12360, 134: 12480, 135: 12600,
        136: 12720, 137: 12840, 138: 12960, 139: 13080, 140: 13200,
        141: 13320, 142: 13440, 143: 13560, 144: 13680, 145: 13800,
        146: 13920, 147: 14040, 148: 14160, 149: 14280, 150: 14400,
        151: 14520, 152: 14640, 153: 14760, 154: 14880, 155: 15000,
        156: 15120, 157: 15240, 158: 15360, 159: 15480, 160: 15600,
        161: 15720, 162: 15840, 163: 15960, 164: 16080, 165: 16200,
        166: 16320, 167: 16440, 168: 16560, 169: 16680, 170: 16800,
        171: 16920, 172: 17040, 173: 17160, 174: 17280, 175: 17400,
        176: 17520, 177: 17640, 178: 17760, 179: 17880, 180: 18000,
        181: 18120, 182: 18240, 183: 18360, 184: 18480, 185: 18600,
        186: 18720, 187: 18840, 188: 18960, 189: 19080, 190: 19200,
        191: 19320, 192: 19440, 193: 19560, 194: 19680, 195: 19800,
        196: 19920, 197: 20040, 198: 20160, 199: 20280, 200: 20400,
        201: 20520, 202: 20640, 203: 20760, 204: 20880, 205: 21000,
        206: 21120, 207: 21240, 208: 21360, 209: 21480, 210: 21600,
    }

    def sum_range(table: dict, start_lv: int, target_lv: int, field: str | None = None) -> int:
        """
        計算『從 start_lv 升到 target_lv』的總消耗（target_lv 不含起點，含終點那一級的成本）
        規則：升級到 L，需要支付表中 L 那一列的成本
        例如：古遺物 13->14 會算 RELIC_COST[14]
        """
        if target_lv <= start_lv:
            return 0
        total = 0
        for lv in range(start_lv + 1, target_lv + 1):
            row = table.get(lv)
            if not row:
                continue
            total += row if isinstance(row, int) else row.get(field, 0)
        return total

    # =========================================================
    # ① 古遺物升級消耗（13→25）— ✅只顯示史詩石之砂 + 蘿拉
    #    稀有石之砂 = 史詩石之砂 * 5（需合成） -> 只做「等價顯示」
    # =========================================================
    st.markdown("### ① 古遺物升級消耗（13→25）")
    r1, r2, r3 = st.columns(3)
    with r1:
        relic_now = st.number_input("目前古遺物等級", min_value=13, max_value=25, value=13, step=1)
    with r2:
        relic_target = st.number_input("目標古遺物等級", min_value=13, max_value=25, value=14, step=1)
    with r3:
        relic_count = st.number_input("幾個古遺物要升？", min_value=1, value=20, step=1)

    # 只算史詩石之砂（主要展示）
    relic_epic = sum_range(RELIC_COST, int(relic_now), int(relic_target), "epic_sand") * int(relic_count)
    relic_lola = sum_range(RELIC_COST, int(relic_now), int(relic_target), "lola") * int(relic_count)

    # 稀有石之砂等價（史詩 * 5）——不再用表內 rare_sand 計算，避免雙口徑
    relic_rare_equiv = relic_epic * 5

    c1, c2, c3 = st.columns(3)
    c1.metric("史詩石之砂", f"{relic_epic:,}")
    c2.metric("相當於稀有石之砂（需合成）", f"{relic_rare_equiv:,}")
    c3.metric("蘿拉", f"{relic_lola:,}")

    st.caption("📌 換算規則：稀有石之砂 = 史詩石之砂 × 5（合成所需），此處僅做等價顯示。")

    st.markdown("---")

    # =========================
    # ② 裝備升級消耗（130→210）
    # =========================
    st.markdown("### ② 裝備升級消耗（130→210）")
    e1, e2, e3 = st.columns(3)
    with e1:
        equip_now = st.number_input("目前裝備等級", min_value=130, max_value=210, value=130, step=1)
    with e2:
        equip_target = st.number_input("目標裝備等級", min_value=130, max_value=210, value=131, step=1)
    with e3:
        equip_count = st.number_input("幾件裝備要升？", min_value=1, value=5, step=1)

    equip_rough = sum_range(EQUIP_COST, int(equip_now), int(equip_target), "rough") * int(equip_count)
    equip_lola = sum_range(EQUIP_COST, int(equip_now), int(equip_target), "lola") * int(equip_count)
    equip_fine = sum_range(EQUIP_COST, int(equip_now), int(equip_target), "fine") * int(equip_count)

    d1, d2, d3 = st.columns(3)
    d1.metric("粗煉石", f"{equip_rough:,}")
    d2.metric("蘿拉", f"{equip_lola:,}")
    d3.metric("精煉石", f"{equip_fine:,}")

    st.markdown("---")

    # =========================
    # ③ 幻獸升級經驗（130→210）
    # =========================
    st.markdown("### ③ 幻獸升級經驗（130→210）")
    b1, b2, b3 = st.columns(3)
    with b1:
        beast_now = st.number_input("目前幻獸等級", min_value=130, max_value=210, value=130, step=1)
    with b2:
        beast_target = st.number_input("目標幻獸等級", min_value=130, max_value=210, value=131, step=1)
    with b3:
        beast_count = st.number_input("幾隻幻獸要升？", min_value=1, value=4, step=1)

    beast_exp_total = sum_range(BEAST_EXP, int(beast_now), int(beast_target)) * int(beast_count)
    st.metric("需要總經驗", f"{beast_exp_total:,}")

    st.markdown("---")

    # =========================
    # ④ 技能升級消耗（130→210）
    # =========================
    st.markdown("### ④ 技能升級消耗（130→210）")
    s1, s2, s3 = st.columns(3)
    with s1:
        skill_now = st.number_input("目前技能等級", min_value=130, max_value=210, value=130, step=1)
    with s2:
        skill_target = st.number_input("目標技能等級", min_value=130, max_value=210, value=131, step=1)
    with s3:
        skill_count = st.number_input("幾個技能要升？", min_value=1, value=8, step=1)

    essence_total = sum_range(SKILL_ESSENCE, int(skill_now), int(skill_target)) * int(skill_count)
    st.metric("歷戰精華", f"{essence_total:,}")

    st.markdown("---")

    # =========================
    # ✅ 資源需求總表（你要的總表）
    # =========================
    st.markdown("## 📋 資源需求總表")

    total_lola = relic_lola + equip_lola
    # 石之砂總量（顯示史詩 + 等價稀有）
    total_epic_sand = relic_epic
    total_rare_equiv = relic_rare_equiv

    # 建議用 dataframe 呈現（不需要額外 import pandas 也能用 st.dataframe(list[dict])）
    summary_rows = [
        {"系統": "古遺物", "資源": "史詩石之砂", "需求量": total_epic_sand},
        {"系統": "古遺物", "資源": "稀有石之砂（等價，史詩×5）", "需求量": total_rare_equiv},
        {"系統": "古遺物", "資源": "蘿拉", "需求量": relic_lola},
        {"系統": "裝備", "資源": "粗煉石", "需求量": equip_rough},
        {"系統": "裝備", "資源": "精煉石", "需求量": equip_fine},
        {"系統": "裝備", "資源": "蘿拉", "需求量": equip_lola},
        {"系統": "幻獸", "資源": "總經驗", "需求量": beast_exp_total},
        {"系統": "技能", "資源": "歷戰精華", "需求量": essence_total},
        {"系統": "合計", "資源": "蘿拉（古遺物+裝備）", "需求量": total_lola},
    ]

    # 讓數字好看：用 st.dataframe 前先把需求量轉字串（帶千分位）
    summary_rows_fmt = []
    for r in summary_rows:
        rr = dict(r)
        rr["需求量"] = f"{int(rr['需求量']):,}"
        summary_rows_fmt.append(rr)

    st.dataframe(summary_rows_fmt, use_container_width=True, hide_index=True)

    with st.expander("📌 計算規則說明"):
        st.write(
            "以你的表為準：升到某等級要支付該等級那一列的成本。例如裝備 130→131 會計入 131 的成本；"
            "古遺物 13→14 會計入 14 的成本。"
        )
        st.write("古遺物石之砂顯示口徑：只顯示『史詩石之砂』，並額外提供『稀有石之砂等價（史詩×5）』作為合成參考。")
    # =========================
    #  Brand Footer（方案二）
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
    st.markdown(
        """
        <div class="donate-box">
          <div class="donate-title">☕ 支持開發者</div>
          <div class="donate-text">
            如果這個原初之星計算器幫助到你，<br>
            歡迎請我喝杯咖啡，讓工具持續更新 💛
          </div>
          <a href="https://buymeacoffee.com/katyjc"
             target="_blank"
             class="donate-btn">
            ☕ Buy Me a Coffee
          </a>
        </div>
        """,
        unsafe_allow_html=True
    )

import datetime as dt

with tab_exp_forecast:
    st.title("⏱️ 等級推算表（到指定日期 08:00）")
    st.caption("現Exp 為『等級內經驗』。日常加速＝每日免費一顆（+2 小時產量/天）；時光結晶＝每顆 +2 小時產量，但只加到總經驗一次。")

    # =========================
    # 1) 版本經驗表（每升 1 級所需 EXP）
    #    格式：{等級: 升到下一級所需exp}
    #    例：LV 98 -> 99 需要 EXP_TABLE[98]
    # =========================
    # ⚠️ 你貼的 S1~S4 很長，建議你整理成 dict 後貼進來
    EXP_TABLES = {
        "S1": {
            1: 80, 2: 90, 3: 90, 4: 90, 5: 90,
            6: 90, 7: 90, 8: 90, 9: 100, 10: 350,
            11: 355, 12: 360, 13: 370, 14: 375, 15: 390,
            16: 400, 17: 450, 18: 500, 19: 500, 20: 1483,
            21: 1844, 22: 1865, 23: 1916, 24: 2043, 25: 2067,
            26: 2169, 27: 2437, 28: 2536, 29: 2860, 30: 2995,
            31: 3607, 32: 3794, 33: 3876, 34: 3996, 35: 4261,
            36: 4289, 37: 4510, 38: 4928, 39: 5086, 40: 17203,
            41: 19189, 42: 21484, 43: 21509, 44: 23052, 45: 24627,
            46: 25480, 47: 26852, 48: 29068, 49: 32008, 50: 33168,
            51: 33332, 52: 34095, 53: 35628, 54: 35929, 55: 37680,
            56: 38331, 57: 38878, 58: 39016, 59: 41731, 60: 43128,
            61: 45042, 62: 45412, 63: 47152, 64: 47282, 65: 47340,
            66: 50487, 67: 53076, 68: 54257, 69: 54405, 70: 197114,
            71: 310414, 72: 330204, 73: 334735, 74: 348791, 75: 360389,
            76: 360701, 77: 362826, 78: 378632, 79: 379059, 80: 408765,
            81: 440713, 82: 464670, 83: 467234, 84: 477970, 85: 484690,
            86: 509874, 87: 513879, 88: 527583, 89: 532378, 90: 583801,
            91: 612907, 92: 643189, 93: 644274, 94: 670957, 95: 678226,
            96: 706678, 97: 712891, 98: 749807, 99: 751452, 100: 886086,
            101: 888547, 102: 926501, 103: 964086, 104: 1012164, 105: 1054111,
            106: 1096529, 107: 1135645, 108: 1174997, 109: 1214584, 110: 1258533,
            111: 1303677, 112: 1348574, 113: 1393941, 114: 1439780, 115: 1486091,
            116: 1532872, 117: 1580125, 118: 1627849, 119: 1676044, 120: 1730017,
            121: 1783360, 122: 1833196, 123: 1833196, 124: 1833196, 125: 1833196,
            126: 1833196, 127: 1833196, 128: 1833196, 129: 1833196, 130: 1833196,
            131: 1833196, 132: 1833196, 133: 1833196, 134: 1833196, 135: 1833196,
            136: 1833196, 137: 1833196,
        },
        "S2": {
    1: 80, 2: 90, 3: 90, 4: 90, 5: 90,
    6: 90, 7: 90, 8: 90, 9: 100, 10: 350,
    11: 355, 12: 360, 13: 370, 14: 375, 15: 390,
    16: 400, 17: 450, 18: 500, 19: 500, 20: 1483,
    21: 1844, 22: 1865, 23: 1916, 24: 2043, 25: 2067,
    26: 2169, 27: 2437, 28: 2536, 29: 2860, 30: 2995,
    31: 3607, 32: 3794, 33: 3876, 34: 3996, 35: 4261,
    36: 4289, 37: 4510, 38: 4928, 39: 5086, 40: 17203,
    41: 19189, 42: 21484, 43: 21509, 44: 23052, 45: 24627,
    46: 25480, 47: 26852, 48: 29068, 49: 32008, 50: 33168,
    51: 33332, 52: 34095, 53: 35628, 54: 35929, 55: 37680,
    56: 38331, 57: 38878, 58: 39016, 59: 41731, 60: 43128,
    61: 45042, 62: 45412, 63: 47152, 64: 47282, 65: 47340,
    66: 50487, 67: 53076, 68: 54257, 69: 54405, 70: 197114,
    71: 310414, 72: 330204, 73: 334735, 74: 348791, 75: 360389,
    76: 360701, 77: 362826, 78: 378632, 79: 379059, 80: 408765,
    81: 440713, 82: 464670, 83: 467234, 84: 477970, 85: 484690,
    86: 509874, 87: 513879, 88: 527583, 89: 532378, 90: 583801,
    91: 612907, 92: 643189, 93: 644274, 94: 670957, 95: 678226,
    96: 706678, 97: 712891, 98: 749807, 99: 751452, 100: 886000,
    101: 3027527, 102: 3032011, 103: 3117883, 104: 3191855, 105: 3220513,
    106: 3258763, 107: 3346658, 108: 3389858, 109: 3548753, 110: 3631694,
    111: 3771824, 112: 3796167, 113: 3866624, 114: 3924404, 115: 4029348,
    116: 4101565, 117: 4245434, 118: 4245686, 119: 4514881, 120: 4566377,
    121: 4752888, 122: 4860000, 123: 5012377, 124: 5016341, 125: 5178619,
    126: 5229563, 127: 5423881, 128: 5459728, 129: 6335318, 130: 6342809,
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
        },
        "S3": {
    1: 80, 2: 90, 3: 90, 4: 90, 5: 90, 6: 90, 7: 90, 8: 90, 9: 100, 10: 350,
    11: 355, 12: 360, 13: 370, 14: 375, 15: 390, 16: 400, 17: 450, 18: 500, 19: 500, 20: 1483,
    21: 1844, 22: 1865, 23: 1916, 24: 2043, 25: 2067, 26: 2169, 27: 2437, 28: 2536, 29: 2860, 30: 2995,
    31: 3607, 32: 3794, 33: 3876, 34: 3996, 35: 4261, 36: 4289, 37: 4510, 38: 4928, 39: 5086, 40: 17203,
    41: 19189, 42: 21484, 43: 21509, 44: 23052, 45: 24627, 46: 25480, 47: 26852, 48: 29068, 49: 32008, 50: 33168,
    51: 33332, 52: 34095, 53: 35628, 54: 35929, 55: 37680, 56: 38331, 57: 38878, 58: 39016, 59: 41731, 60: 43128,
    61: 45042, 62: 45412, 63: 47152, 64: 47282, 65: 47340, 66: 50487, 67: 53076, 68: 54257, 69: 54405, 70: 197114,
    71: 310414, 72: 330204, 73: 334735, 74: 348791, 75: 360389, 76: 360701, 77: 362826, 78: 378632, 79: 379059, 80: 408765,
    81: 440713, 82: 464670, 83: 467234, 84: 477970, 85: 484690, 86: 509874, 87: 513879, 88: 527583, 89: 532378, 90: 583801,
    91: 612907, 92: 643189, 93: 644274, 94: 670957, 95: 678226, 96: 706678, 97: 712891, 98: 749807, 99: 751452, 100: 2904398,
    101: 3027527, 102: 3032011, 103: 3117883, 104: 3191855, 105: 3220513, 106: 3258763, 107: 3346658, 108: 3389858, 109: 3548753, 110: 3631694,
    111: 3771824, 112: 3796167, 113: 3866624, 114: 3924404, 115: 4029348, 116: 4101565, 117: 4245434, 118: 4245686, 119: 4514881, 120: 4566377,
    121: 4752888, 122: 4866448, 123: 5012377, 124: 5016341, 125: 5178619, 126: 5229563, 127: 5423881, 128: 5459728, 129: 6335318, 130: 22859655,
    131: 23541185, 132: 23587156, 133: 24290510, 134: 24337860, 135: 25112507, 136: 25161277, 137: 25962089, 138: 26062556, 139: 26920314, 140: 27780149,
    141: 28608441, 142: 28773140, 143: 29687769, 144: 29800863, 145: 30864506, 146: 30980992, 147: 32025290, 148: 32205262, 149: 33270698, 150: 34387276,
    151: 35609150, 152: 35871344, 153: 37143639, 154: 37211154, 155: 38460179, 156: 38529719, 157: 39822474, 158: 40037353, 159: 43248083, 160: 44969859,
    161: 48762878, 162: 52604320, 163: 56396556, 164: 60225668, 165: 63980989, 166: 67994521, 167: 71934262, 168: 76039985, 169: 80194876, 170: 80600630,
    171: 81009637, 172: 81415408, 173: 81685922, 174: 81821179, 175: 82226950, 176: 82632720, 177: 82903234, 178: 83309005, 179: 83714776, 180: 83985290,
    181: 84388130, 182: 84658635, 183: 84929139, 184: 85334896, 185: 85605400, 186: 85875905, 187: 86281661, 188: 86552166, 189: 86822670, 190: 86957923,
    191: 87237117, 192: 87507648, 193: 87913445, 194: 103526684, 195: 114131779, 196: 114434891, 197: 114586448, 198: 114889559, 199: 115192672, 200: 115344229,
    201: 115928916, 202: 116231965, 203: 116686535, 204: 116838059, 205: 117444154, 206: 117747201, 207: 117898726, 208: 118353296, 209: 118656343, 210: 118807868,
    211: 119120332, 212: 119271871, 213: 119726482, 214: 120029557, 215: 120181095, 216: 120484169, 217: 120787245, 218: 121090319, 219: 105899150, 220: 106656837,
    221: 106969019, 222: 107120569, 223: 107423670, 224: 107726771, 225: 108332972, 226: 108484523, 227: 109242275, 228: 109545375, 229: 109696926, 230: 110000026,
    231: 110293284, 232: 110444820, 233: 110747894, 234: 111050968, 235: 111657115, 236: 111808652, 237: 111960189, 238: 112263263, 239: 112414799, 240: 112717873,
    241: 113019510, 242: 113322580, 243: 113625650, 244: 113777185, 245: 114080255, 246: 114080255, 247: 114231790, 248: 114231790, 249: 114383325, 250: 114498509,
    251: 114534860, 252: 114649996, 253: 114649996, 254: 114649996, 255: 114649996, 256: 114649996, 257: 114649996, 258: 114649996, 259: 114649996, 260: 114649996,
    261: 114649996, 262: 114649996, 263: 114649996, 264: 114649996, 265: 114649996, 266: 114649996, 267: 114649996, 268: 114649996, 269: 114649996, 270: 114649996,
    271: 114649996, 272: 114649996, 273: 114649996, 274: 114649996, 275: 114649996, 276: 114649996, 277: 114649996, 278: 114649996, 279: 114649996, 280: 114649996,
    281: 114649996, 282: 114649996, 283: 114649996, 284: 114649996, 285: 114649996, 286: 114649996, 287: 114649996, 288: 114649996, 289: 114649996, 290: 114649996,
    291: 114649996, 292: 114649996, 293: 114649996, 294: 114649996, 295: 114649996, 296: 114649996, 297: 114649996, 298: 114649996, 299: 114649996, 300: 114649996,
    301: 114649996, 302: 114649996, 303: 114649996, 304: 114649996, 305: 114649996, 306: 114649996, 307: 114649996, 308: 114649996, 309: 114649996, 310: 114649996,
    311: 114649996, 312: 114649996, 313: 114649996, 314: 114649996, 315: 114649996, 316: 114649996, 317: 114649996, 318: 114649996, 319: 114649996, 320: 114649996,
        },
        "S4": {
  1: 80, 2: 90, 3: 90, 4: 90, 5: 90, 6: 90, 7: 90, 8: 90, 9: 100, 10: 350,
  11: 355, 12: 360, 13: 370, 14: 375, 15: 390, 16: 400, 17: 450, 18: 500, 19: 500, 20: 1483,
  21: 1844, 22: 1865, 23: 1916, 24: 2043, 25: 2067, 26: 2169, 27: 2437, 28: 2536, 29: 2860, 30: 2995,
  31: 3607, 32: 3794, 33: 3876, 34: 3996, 35: 4261, 36: 4289, 37: 4510, 38: 4928, 39: 5086, 40: 17203,
  41: 19189, 42: 21484, 43: 21509, 44: 23052, 45: 24627, 46: 25480, 47: 26852, 48: 29068, 49: 32008, 50: 33168,
  51: 33332, 52: 34095, 53: 35628, 54: 35929, 55: 37680, 56: 38331, 57: 38878, 58: 39016, 59: 41731, 60: 43128,
  61: 45042, 62: 45412, 63: 47152, 64: 47282, 65: 47340, 66: 50487, 67: 53076, 68: 54257, 69: 54405, 70: 197114,
  71: 310414, 72: 330204, 73: 334735, 74: 348791, 75: 360389, 76: 360701, 77: 362826, 78: 378632, 79: 379059, 80: 408765,
  81: 440713, 82: 464670, 83: 467234, 84: 477970, 85: 484690, 86: 509874, 87: 513879, 88: 527583, 89: 532378, 90: 583801,
  91: 612907, 92: 643189, 93: 644274, 94: 670957, 95: 678226, 96: 706678, 97: 712891, 98: 749807, 99: 751452, 100: 2904398,
  101: 3027527, 102: 3032011, 103: 3117883, 104: 3191855, 105: 3220513, 106: 3258763, 107: 3346658, 108: 3389858, 109: 3548753, 110: 3631694,
  111: 3771824, 112: 3796167, 113: 3866624, 114: 3924404, 115: 4029348, 116: 4101565, 117: 4245434, 118: 4245686, 119: 4514881, 120: 4566377,
  121: 4752888, 122: 4866448, 123: 5012377, 124: 5016341, 125: 5178619, 126: 5229563, 127: 5423881, 128: 5459728, 129: 6335318, 130: 22859655,
  131: 23541185, 132: 23587156, 133: 24290510, 134: 24337860, 135: 25112507, 136: 25161277, 137: 25962089, 138: 26062556, 139: 26920314, 140: 27780149,
  141: 28608441, 142: 28773140, 143: 29687769, 144: 29800863, 145: 30864506, 146: 30980992, 147: 32025290, 148: 32205262, 149: 33270698, 150: 34387276,
  151: 35609150, 152: 35871344, 153: 37143639, 154: 37211154, 155: 38460179, 156: 38529719, 157: 39822474, 158: 40037353, 159: 43248083, 160: 384397189,
  161: 395865205, 162: 396350698, 163: 409177436, 164: 409177436, 165: 422418979, 166: 422934039, 167: 437149695, 168: 438210719, 169: 453833849, 170: 468396986,
  171: 484113075, 172: 485851805, 173: 502143700, 174: 503337628, 175: 519592952, 176: 520822698, 177: 538272785, 178: 540172742, 179: 557963011, 180: 576777448,
  181: 595380011, 182: 596764450, 183: 617434129, 184: 620286073, 185: 641012583, 186: 642481335, 187: 663183389, 188: 665452610, 189: 744690971, 190: 804233453,
  191: 864436925, 192: 925029631, 193: 986011570, 194: 1047382743, 195: 1110376404, 196: 1173889043, 197: 1235194660, 198: 1298187639, 199: 1302471254, 200: 1305533399,
  201: 1306961497, 202: 1309817693, 203: 1312673889, 204: 1315530085, 205: 1318386280, 206: 1321242476, 207: 1322670574, 208: 1325526770, 209: 1328382966, 210: 1331308702,
  211: 1334165048, 212: 1337021393, 213: 1339877738, 214: 1342734083, 215: 1345590428, 216: 1348446774, 217: 1351303119, 218: 1354159464, 219: 1357015809, 220: 1359833971,
  221: 1362690236, 222: 1365546501, 223: 1368402766, 224: 1369830899, 225: 1372687164, 226: 1375543428, 227: 1378399693, 228: 1381255958, 229: 1384112223, 230: 1385490351,
  231: 1388346513, 232: 1391202675, 233: 1392630756, 234: 1395486917, 235: 1398343079, 236: 1401199241, 237: 1404055402, 238: 1406911564, 239: 1408339645, 240: 1411302011,
  241: 1414158388, 242: 1417014765, 243: 1419871142, 244: 1422727519, 245: 1425583895, 246: 1427012084, 247: 1429868461, 248: 1432724838, 249: 1435581215, 250: 1436995360,
  251: 1439851709, 252: 1442708058, 253: 1445564407, 254: 1448420756, 255: 1451277105, 256: 1454133454, 257: 1455561628, 258: 1458417977, 259: 1461274326, 260: 1463946577,
  261: 1466802567, 262: 1469658556, 263: 1472514546, 264: 1473942540, 265: 1476798530, 266: 1479654519, 267: 1482510509, 268: 1485366498, 269: 1488222487, 270: 1491390587,
  271: 1494247175, 272: 1497103763, 273: 1498532057, 274: 1501388645, 275: 1504245233, 276: 1507101820, 277: 1509958408, 278: 1511386702, 279: 1514243290, 280: 1516329564,
  281: 1519184700, 282: 1522039835, 283: 1522039835, 284: 1522039835, 285: 1522039835, 286: 1522039835, 287: 1522039835, 288: 1522039835, 289: 1522039835, 290: 1522039835,
  291: 1522039835, 292: 1522039835, 293: 1522039835, 294: 1522039835, 295: 1522039835, 296: 1522039835, 297: 1522039835, 298: 1522039835, 299: 1522039835, 300: 1522039835,
  301: 1522039835, 302: 1522039835, 303: 1522039835, 304: 1522039835, 305: 1522039835, 306: 1522039835, 307: 1522039835, 308: 1522039835, 309: 1522039835, 310: 1522039835,
  311: 1522039835, 312: 1522039835, 313: 1522039835, 314: 1522039835, 315: 1522039835, 316: 1522039835, 317: 1522039835, 318: 1522039835, 319: 1522039835, 320: 1522039835,
  321: 1522039835, 322: 1522039835, 323: 1522039835, 324: 1522039835, 325: 1522039835, 326: 1522039835, 327: 1522039835, 328: 1522039835, 329: 1522039835, 330: 1522039835,
  331: 1522039835, 332: 1522039835, 333: 1522039835, 334: 1522039835, 335: 1522039835, 336: 1522039835, 337: 1522039835, 338: 1522039835, 339: 1522039835, 340: 1522039835,
  341: 1522039835, 342: 1522039835, 343: 1522039835, 344: 1522039835, 345: 1522039835, 346: 1522039835, 347: 1522039835, 348: 1522039835, 349: 1522039835, 350: 1522039835,
  351: 1522039835, 352: 1522039835, 353: 1522039835, 354: 1522039835, 355: 1522039835, 356: 1522039835, 357: 1522039835, 358: 1522039835, 359: 1522039835, 360: 1522039835,
  361: 1522039835, 362: 1522039835, 363: 1522039835, 364: 1522039835, 365: 1522039835, 366: 1522039835, 367: 1522039835, 368: 1522039835, 369: 1522039835, 370: 1522039835,
  371: 1522039835, 372: 1522039835, 373: 1522039835, 374: 1522039835, 375: 1522039835, 376: 1522039835, 377: 1522039835, 378: 1522039835, 379: 1522039835, 380: 1522039835,
  381: 1522039835, 382: 1522039835, 383: 1522039835, 384: 1522039835, 385: 1522039835, 386: 1522039835, 387: 1522039835, 388: 1522039835, 389: 1522039835, 390: 1522039835,
  391: 1522039835, 392: 1522039835, 393: 1522039835, 394: 1522039835, 395: 1522039835, 396: 1522039835, 397: 1522039835, 398: 1522039835, 399: 1522039835, 400: 1522039835,
  401: 1522039835, 402: 1522039835, 403: 1522039835, 404: 1522039835, 405: 1522039835, 406: 1522039835, 407: 1522039835, 408: 1522039835, 409: 1522039835, 410: 1522039835,
  411: 1522039835, 412: 1522039835, 413: 1522039835, 414: 1522039835, 415: 1522039835, 416: 1522039835, 417: 1522039835, 418: 1522039835, 419: 1522039835, 420: 1522039835,
  421: 1522039835, 422: 1522039835, 423: 1522039835, 424: 1522039835, 425: 1522039835, 426: 1522039835, 427: 1522039835, 428: 1522039835, 429: 1522039835, 430: 1522039835,
  431: 1522039835, 432: 1522039835, 433: 1522039835, 434: 1522039835, 435: 1522039835, 436: 1522039835, 437: 1522039835, 438: 1522039835, 439: 1522039835, 440: 1522039835,
  441: 1522039835, 442: 1522039835, 443: 1522039835, 444: 1522039835, 445: 1522039835, 446: 1522039835, 447: 1522039835, 448: 1522039835, 449: 1522039835, 450: 1522039835,
  451: 1522039835, 452: 1522039835, 453: 1522039835, 454: 1522039835, 455: 1522039835, 456: 1522039835, 457: 1522039835, 458: 1522039835, 459: 1522039835, 460: 1522039835,
  461: 1522039835, 462: 1522039835, 463: 1522039835, 464: 1522039835, 465: 1522039835, 466: 1522039835, 467: 1522039835, 468: 1522039835, 469: 1522039835, 470: 1522039835,
  471: 1522039835, 472: 1522039835, 473: 1522039835, 474: 1522039835, 475: 1522039835, 476: 1522039835, 477: 1522039835, 478: 1522039835, 479: 1522039835, 480: 1522039835,
  481: 1522039835, 482: 1522039835, 483: 1522039835, 484: 1522039835, 485: 1522039835, 486: 1522039835, 487: 1522039835, 488: 1522039835, 489: 1522039835, 490: 1522039835,
  491: 1522039835, 492: 1522039835, 493: 1522039835, 494: 1522039835, 495: 1522039835, 496: 1522039835, 497: 1522039835, 498: 1522039835, 499: 1522039835, 500: 1522039835
        },
    }

    # =========================
    # 2) 小工具：把等級內經驗 + 新增經驗，推算到哪個等級
    # =========================
    def simulate_level(version_key: str, cur_lv: int, cur_exp_in_lv: int, add_exp: int):
        table = EXP_TABLES.get(version_key, {})
        lv = int(cur_lv)
        exp_in_lv = max(0, int(cur_exp_in_lv)) + max(0, int(add_exp))

        # 如果表沒有這個等級的升級需求，就停（避免 KeyError）
        # 規則：需要用 lv 這一列（lv->lv+1 的需求）
        while True:
            need = table.get(lv)
            if need is None:
                break
            if exp_in_lv < need:
                break
            exp_in_lv -= need
            lv += 1
        return lv, exp_in_lv

    # =========================
    # 3) UI
    # =========================
    vcol1, vcol2, vcol3 = st.columns(3)
    with vcol1:
        version = st.selectbox("經驗表版本", ["S1", "S2", "S3", "S4"], index=1)
    with vcol2:
        cur_lv = st.number_input("現在等級（現Lv）", min_value=1, value=98, step=1)
    with vcol3:
        cur_exp_in_lv = st.number_input("現有經驗（現Exp，等級內）", min_value=0, value=50000, step=100)

    hcol1, hcol2, hcol3 = st.columns(3)
    with hcol1:
        exp_per_hour = st.number_input("每小時經驗（EXP/h）", min_value=0, value=20000, step=100)
    with hcol2:
        daily_boost_count = st.number_input("日常加速次數（每日免費一顆）", min_value=0, value=1, step=1)
    with hcol3:
        crystal_count = st.number_input("時光結晶次數", min_value=0, value=0, step=1)

    dcol1, dcol2 = st.columns(2)
    with dcol1:
        target_date = st.date_input("目標日期（輸出計算到該日 08:00）", value=dt.date.today())
    with dcol2:
        now_mode = st.selectbox("起算時間", ["現在", "今天 08:00"], index=0)

    # =========================
    # 4) 計算：從起算時間累積到目標日 08:00
    # =========================
    def get_start_dt():
        now = dt.datetime.now()
        if now_mode == "今天 08:00":
            start = dt.datetime(now.year, now.month, now.day, 8, 0, 0)
            # 如果現在已經超過今天 08:00，仍從今天 08:00 起算（符合你頁面示意）
            return start
        return now

    start_dt = get_start_dt()
    end_dt = dt.datetime(target_date.year, target_date.month, target_date.day, 8, 0, 0)

    if end_dt <= start_dt:
        st.warning("目標日期 08:00 必須晚於起算時間。")
    else:
        # 基本累積：依小時
        total_hours = (end_dt - start_dt).total_seconds() / 3600.0
        base_gain = int(total_hours * int(exp_per_hour))

        # 日常加速：每「整天」+2 小時產量/天
        # 這裡用日期差（含跨日）來估算每天一次的加速
        # 你如果想要嚴格對齊「每天 08:00 發放」，我也可以再幫你改成更精準的發放點模擬
        day_span = (end_dt.date() - start_dt.date()).days
        # 若起算時間在同一天，且 end_dt 在隔天 08:00 前，day_span=1 表示跨到下一天
        daily_boost_gain = int(day_span * int(daily_boost_count) * 2 * int(exp_per_hour))

        # 時光結晶：一次性加總（不算每日）
        crystal_gain = int(int(crystal_count) * 2 * int(exp_per_hour))

        total_gain = base_gain + daily_boost_gain + crystal_gain

        # 推算等級
        pred_lv, pred_exp_in_lv = simulate_level(version, int(cur_lv), int(cur_exp_in_lv), total_gain)

        # =========================
        # 5) 顯示
        # =========================
        st.markdown("### ✅ 推算結果（到目標日 08:00）")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("累積小時數", f"{total_hours:,.2f} h")
        m2.metric("總增加經驗", f"{total_gain:,}")
        m3.metric("預估等級", f"{pred_lv}")
        m4.metric("等級內經驗（現Exp）", f"{pred_exp_in_lv:,}")

        with st.expander("📌 明細（加成拆分）"):
            st.write({
                "起算時間": str(start_dt),
                "目標時間": str(end_dt),
                "基礎增加（依小時）": base_gain,
                "日常加速增加（每日+2h）": daily_boost_gain,
                "時光結晶一次性增加（+2h/顆）": crystal_gain,
                "總增加": total_gain,
            })

        st.info("⚠️ 提醒：如果 EXP_TABLES 尚未貼完整，遇到表中缺少的等級就會停止推算（等級不再往上升）。")
    # =========================
    #  Brand Footer（方案二）
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
    st.markdown(
        """
        <div class="donate-box">
          <div class="donate-title">☕ 支持開發者</div>
          <div class="donate-text">
            如果這個原初之星計算器幫助到你，<br>
            歡迎請我喝杯咖啡，讓工具持續更新 💛
          </div>
          <a href="https://buymeacoffee.com/katyjc"
             target="_blank"
             class="donate-btn">
            ☕ Buy Me a Coffee
          </a>
        </div>
        """,
        unsafe_allow_html=True
    )
