import streamlit as st

# =========================
# Page config
# =========================
st.set_page_config(
    page_title="原初之星計算器｜Season 2",
    page_icon="⭐",
    layout="wide"
)

# =========================
# Constants
# =========================
BASE_LV = 130          # 角色 / 裝備 / 技能 / 幻獸
RELIC_BASE_LV = 13     # 古遺物

# =========================
# Styling
# =========================
st.markdown(
    """
    <style>
      /* 快速輸入卡片 */
      .bulk-box {
        background: rgba(255, 193, 7, 0.10);
        border: 1px solid rgba(255, 193, 7, 0.35);
        border-left: 6px solid rgba(255, 193, 7, 0.85);
        padding: 12px 14px;
        border-radius: 12px;
        margin: 6px 0 10px 0;
      }
      .bulk-title {
        font-weight: 800;
        font-size: 0.98rem;
        margin-bottom: 2px;
      }
      .bulk-hint {
        color: rgba(0,0,0,0.6);
        font-size: 0.85rem;
        margin-bottom: 10px;
      }

      /* Brand Footer（方案二） */
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

def apply_bulk(prefix: str, count: int):
    bulk_val = st.session_state.get(f"{prefix}_bulk")
    for i in range(count):
        st.session_state[f"{prefix}_{i}"] = bulk_val

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
st.caption("所有項目僅計算『超過基礎等級』的部分。")

# =========================
# Sidebar
# =========================
st.sidebar.header("⚙️ 設定")

base_stars = st.sidebar.number_input("本季初始原初之星", min_value=0, value=45, step=1)
convert_div = st.sidebar.number_input("原初之星換算除數（總分 ÷ X）", min_value=1, value=27, step=1)

st.sidebar.markdown("---")
st.sidebar.subheader("📈 加分規則")
p_char  = st.sidebar.number_input("角色 +1 加分", value=100)
p_equip = st.sidebar.number_input("裝備 +1 加分", value=18)
p_skill = st.sidebar.number_input("技能 +1 加分", value=7)
p_beast = st.sidebar.number_input("幻獸 +1 加分", value=8)
p_relic = st.sidebar.number_input("古遺物 +1 加分", value=33)

# =========================
# Basic inputs
# =========================
c1, c2 = st.columns(2)
with c1:
    prev_season_stars = st.number_input("上季原初之星", min_value=0, value=0, step=1)
with c2:
    char_lv = st.number_input("目前角色等級（基礎 130）", min_value=1, value=130, step=1)

char_eff = effective_lv(char_lv)
score_char = char_eff * p_char
st.caption(f"角色計分：max(0, {char_lv} − 130) = {char_eff} 級 → {score_char} 分")

# =========================
# 裝備（5）
# =========================
st.subheader("🛡 裝備（5 欄）")
bulk_ui("裝備快速輸入（套用到 5 欄）", "基礎等級 130")

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

equip_cols = st.columns(5)
equip_eff = []
for i in range(5):
    with equip_cols[i]:
        lv = st.number_input(f"裝備 {i+1}", key=f"equip_{i}", value=130, min_value=1)
        equip_eff.append(effective_lv(lv))
score_equip = sum(equip_eff) * p_equip

# =========================
# 技能（8）
# =========================
st.subheader("📘 技能（8 欄）")
bulk_ui("技能快速輸入（套用到 8 欄）", "基礎等級 130")

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

skill_cols = st.columns(4)
skill_eff = []
for i in range(8):
    with skill_cols[i % 4]:
        lv = st.number_input(f"技能 {i+1}", key=f"skill_{i}", value=130, min_value=1)
        skill_eff.append(effective_lv(lv))
score_skill = sum(skill_eff) * p_skill

# =========================
# 幻獸（4）
# =========================
st.subheader("🐉 幻獸（4 欄）")
bulk_ui("幻獸快速輸入（套用到 4 欄）", "基礎等級 130")

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

beast_cols = st.columns(4)
beast_eff = []
for i in range(4):
    with beast_cols[i]:
        lv = st.number_input(f"幻獸 {i+1}", key=f"beast_{i}", value=130, min_value=1)
        beast_eff.append(effective_lv(lv))
score_beast = sum(beast_eff) * p_beast

# =========================
# 古遺物（20，基礎 13）
# =========================
st.subheader("🔮 古遺物")
bulk_ui("古遺物總快速輸入（套用到全部 20 欄）", "基礎等級 13")

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
            lv = st.number_input(f"{element}-{i+1}", key=f"relic_{idx}", value=13, min_value=1)
            relic_eff.append(effective_relic_lv(lv))
            idx += 1

score_relic = sum(relic_eff) * p_relic

# =========================
# Compute
# =========================
season_score = score_char + score_equip + score_skill + score_beast + score_relic
season_grade = get_grade(season_score)

earned_stars = season_score // convert_div
season_total_stars = base_stars + earned_stars
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

# =========================
# 得分明細（回復）
# =========================
with st.expander("📊 得分明細（各系統貢獻）"):
    st.write({
        "角色等級得分": score_char,
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
        <div class="brand-author">by 甜蝦麵</div>
    </div>
    """,
    unsafe_allow_html=True,
)
