import streamlit as st

st.set_page_config(
    page_title="第2季 原初之星計算器",
    page_icon="⭐",
    layout="wide"
)

# =========================
# Helper Functions
# =========================
def get_grade(score: int) -> str:
    if score >= 15900:
        return "SSS"
    elif 14500 <= score <= 15899:
        return "SS"
    elif 13100 <= score <= 14499:
        return "S"
    elif 10400 <= score <= 13099:
        return "A"
    elif 7600 <= score <= 10399:
        return "B"
    elif 4800 <= score <= 7599:
        return "C"
    else:
        return "D"

def sum_list(nums):
    return int(sum(nums))

# =========================
# Title
# =========================
st.title("⭐ 第 2 季｜原初之星計算器")
st.caption(
    "輸入目前角色等級與本季養成提升，自動計算："
    "本季養成總分、評級，以及原初之星（可加總上季）。"
)

# =========================
# Sidebar Settings
# =========================
st.sidebar.header("⚙️ 設定")

base_stars = st.sidebar.number_input(
    "本季初始原初之星",
    min_value=0,
    value=45,
    step=1
)

convert_div = st.sidebar.number_input(
    "原初之星換算除數（總分 ÷ X 取整）",
    min_value=1,
    value=27,
    step=1
)

st.sidebar.markdown("---")
st.sidebar.subheader("📈 加分規則（可調）")

p_char = st.sidebar.number_input("角色等級：每 +1 加分", value=100)
p_equip = st.sidebar.number_input("裝備：每 +1 加分", value=18)
p_skill = st.sidebar.number_input("技能：每 +1 加分", value=7)
p_beast = st.sidebar.number_input("幻獸：每 +1 加分", value=8)
p_relic = st.sidebar.number_input("古遺物：每 +1 加分", value=33)

# =========================
# Inputs
# =========================
col1, col2 = st.columns(2)

with col1:
    prev_season_stars = st.number_input(
        "上季原初之星",
        min_value=0,
        value=0,
        step=1
    )

with col2:
    char_current_lv = st.number_input(
        "目前角色等級（130 等以上才計分）",
        min_value=1,
        value=130,
        step=1
    )

# ---------- Character Score ----------
effective_char_lv = max(0, char_current_lv - 130)
score_char = effective_char_lv * p_char

st.caption(
    f"角色等級計分：max(0, {char_current_lv} − 130) = "
    f"{effective_char_lv} 級 → {score_char} 分"
)

# =========================
# Equipment (5)
# =========================
st.subheader("🛡 裝備（5 欄）")
equip_cols = st.columns(5)
equip_ups = []

for i in range(5):
    with equip_cols[i]:
        equip_ups.append(
            st.number_input(f"裝備 {i+1}", min_value=0, value=0, step=1)
        )

# =========================
# Skills (8)
# =========================
st.subheader("📘 技能（8 欄）")
skill_cols = st.columns(4)
skill_ups = []

for i in range(8):
    with skill_cols[i % 4]:
        skill_ups.append(
            st.number_input(f"技能 {i+1}", min_value=0, value=0, step=1)
        )

# =========================
# Beasts (4)
# =========================
st.subheader("🐉 幻獸（4 欄）")
beast_cols = st.columns(4)
beast_ups = []

for i in range(4):
    with beast_cols[i]:
        beast_ups.append(
            st.number_input(f"幻獸 {i+1}", min_value=0, value=0, step=1)
        )

# =========================
# Relics (光暗風水火 × 4)
# =========================
st.subheader("🔮 古遺物（5 組 × 4 欄）")

elements = ["光", "暗", "風", "水", "火"]
relic_ups = []

for element in elements:
    st.markdown(f"### {element}")
    cols = st.columns(4)
    for i in range(4):
        with cols[i]:
            relic_ups.append(
                st.number_input(
                    f"{element}-{i+1}",
                    min_value=0,
                    value=0,
                    step=1
                )
            )

# =========================
# Compute Scores
# =========================
score_equip = sum_list(equip_ups) * p_equip
score_skill = sum_list(skill_ups) * p_skill
score_beast = sum_list(beast_ups) * p_beast
score_relic = sum_list(relic_ups) * p_relic

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
st.subheader("📌 第 2 季結果")

m1, m2, m3, m4 = st.columns(4)
m1.metric("本季養成總分", f"{season_score:,}")
m2.metric("本季評級", season_grade)
m3.metric("本季獲得原初之星", f"{earned_stars:,}")
m4.metric("本季原初之星合計", f"{season_total_stars:,}")

st.markdown("### ⭐ 原初之星總計")
g1, g2 = st.columns(2)
g1.metric("上季原初之星", f"{prev_season_stars:,}")
g2.metric("總原初之星（上季 + 本季）", f"{grand_total_stars:,}")

with st.expander("📊 本季得分明細"):
    st.write({
        "角色等級得分": score_char,
        "裝備得分": score_equip,
        "技能得分": score_skill,
        "幻獸得分": score_beast,
        "古遺物得分": score_relic,
        "本季總分": season_score,
        "本季評級": season_grade
    })
