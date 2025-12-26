import streamlit as st

st.set_page_config(
    page_title="第2季 原初之星計算器",
    page_icon="⭐",
    layout="wide"
)

# =========================
# Helper Functions
# =========================
BASE_LV = 130

def effective_lv(current_lv: int) -> int:
    return max(0, current_lv - BASE_LV)

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

# =========================
# Title
# =========================
st.title("⭐ 第 2 季｜原初之星計算器")
st.caption(
    "所有欄位皆以 130 為基礎等級，僅計算超過 130 的部分。"
)

# =========================
# Sidebar Settings
# =========================
st.sidebar.header("⚙️ 賽季設定")

base_stars = st.sidebar.number_input(
    "本季初始原初之星",
    min_value=0,
    value=45,
    step=1
)

convert_div = st.sidebar.number_input(
    "原初之星換算除數（總分 ÷ X）",
    min_value=1,
    value=27,
    step=1
)

st.sidebar.markdown("---")
st.sidebar.subheader("📈 加分規則")

p_char  = st.sidebar.number_input("角色：每 +1 加分", value=100)
p_equip = st.sidebar.number_input("裝備：每 +1 加分", value=18)
p_skill = st.sidebar.number_input("技能：每 +1 加分", value=7)
p_beast = st.sidebar.number_input("幻獸：每 +1 加分", value=8)
p_relic = st.sidebar.number_input("古遺物：每 +1 加分", value=33)

# =========================
# Basic Inputs
# =========================
c1, c2 = st.columns(2)

with c1:
    prev_season_stars = st.number_input(
        "上季原初之星",
        min_value=0,
        value=0,
        step=1
    )

with c2:
    char_lv = st.number_input(
        "目前角色等級",
        min_value=1,
        value=130,
        step=1
    )

char_eff = effective_lv(char_lv)
score_char = char_eff * p_char

st.caption(f"角色計分：max(0, {char_lv} − 130) = {char_eff} 級 → {score_char} 分")

# =========================
# Equipment (5)
# =========================
st.subheader("🛡 裝備（5 欄，輸入目前等級）")
equip_cols = st.columns(5)
equip_scores = []

for i in range(5):
    with equip_cols[i]:
        lv = st.number_input(f"裝備 {i+1}", min_value=1, value=130)
        equip_scores.append(effective_lv(lv))

score_equip = sum(equip_scores) * p_equip

# =========================
# Skills (8)
# =========================
st.subheader("📘 技能（8 欄，輸入目前等級）")
skill_cols = st.columns(4)
skill_scores = []

for i in range(8):
    with skill_cols[i % 4]:
        lv = st.number_input(f"技能 {i+1}", min_value=1, value=130)
        skill_scores.append(effective_lv(lv))

score_skill = sum(skill_scores) * p_skill

# =========================
# Beasts (4)
# =========================
st.subheader("🐉 幻獸（4 欄，輸入目前等級）")
beast_cols = st.columns(4)
beast_scores = []

for i in range(4):
    with beast_cols[i]:
        lv = st.number_input(f"幻獸 {i+1}", min_value=1, value=130)
        beast_scores.append(effective_lv(lv))

score_beast = sum(beast_scores) * p_beast

# =========================
# Relics (光暗風水火 × 4)
# =========================
st.subheader("🔮 古遺物（光 / 暗 / 風 / 水 / 火 × 4）")

elements = ["光", "暗", "風", "水", "火"]
relic_scores = []

for element in elements:
    st.markdown(f"### {element}")
    cols = st.columns(4)
    for i in range(4):
        with cols[i]:
            lv = st.number_input(f"{element}-{i+1}", min_value=1, value=130)
            relic_scores.append(effective_lv(lv))

score_relic = sum(relic_scores) * p_relic

# =========================
# Compute
# =========================
season_score = (
    score_char
    + score_equip
    + score_skill
    + score_beast
    + score_relic
)

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

with st.expander("📊 得分明細"):
    st.write({
        "角色": score_char,
        "裝備": score_equip,
        "技能": score_skill,
        "幻獸": score_beast,
        "古遺物": score_relic,
        "本季總分": season_score,
        "本季評級": season_grade
    })
