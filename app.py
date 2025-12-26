import streamlit as st

st.set_page_config(
    page_title="第2季 原初之星計算器",
    page_icon="⭐",
    layout="wide"
)

BASE_LV = 130

# =========================
# Helper Functions
# =========================
def effective_lv(lv: int) -> int:
    return max(0, lv - BASE_LV)

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
    """把 bulk 值實際寫入該項目的所有欄位"""
    bulk_val = st.session_state.get(f"{prefix}_bulk", BASE_LV)
    for i in range(count):
        st.session_state[f"{prefix}_{i}"] = bulk_val

# =========================
# Title
# =========================
st.title("⭐ 第 2 季｜原初之星計算器")
st.caption("快速輸入會『實際套用』到所有欄位（使用 session_state）。")

# =========================
# Sidebar
# =========================
st.sidebar.header("⚙️ 設定")

base_stars = st.sidebar.number_input("本季初始原初之星", value=45)
convert_div = st.sidebar.number_input("原初之星換算除數", value=27)

st.sidebar.markdown("---")
st.sidebar.subheader("📈 加分規則")

p_char  = st.sidebar.number_input("角色 +1 加分", value=100)
p_equip = st.sidebar.number_input("裝備 +1 加分", value=18)
p_skill = st.sidebar.number_input("技能 +1 加分", value=7)
p_beast = st.sidebar.number_input("幻獸 +1 加分", value=8)
p_relic = st.sidebar.number_input("古遺物 +1 加分", value=33)

# =========================
# Basic Inputs
# =========================
c1, c2 = st.columns(2)

with c1:
    prev_season_stars = st.number_input("上季原初之星", min_value=0, value=0)

with c2:
    char_lv = st.number_input("目前角色等級", min_value=1, value=130)

score_char = effective_lv(char_lv) * p_char

# =========================
# 裝備（5）
# =========================
st.subheader("🛡 裝備（5 欄）")

st.number_input(
    "快速輸入裝備等級（套用到全部）",
    key="equip_bulk",
    value=130,
    on_change=apply_bulk,
    kwargs={"prefix": "equip", "count": 5}
)

equip_cols = st.columns(5)
equip_eff = []

for i in range(5):
    with equip_cols[i]:
        lv = st.number_input(
            f"裝備 {i+1}",
            key=f"equip_{i}",
            value=130
        )
        equip_eff.append(effective_lv(lv))

score_equip = sum(equip_eff) * p_equip

# =========================
# 技能（8）
# =========================
st.subheader("📘 技能（8 欄）")

st.number_input(
    "快速輸入技能等級（套用到全部）",
    key="skill_bulk",
    value=130,
    on_change=apply_bulk,
    kwargs={"prefix": "skill", "count": 8}
)

skill_cols = st.columns(4)
skill_eff = []

for i in range(8):
    with skill_cols[i % 4]:
        lv = st.number_input(
            f"技能 {i+1}",
            key=f"skill_{i}",
            value=130
        )
        skill_eff.append(effective_lv(lv))

score_skill = sum(skill_eff) * p_skill

# =========================
# 幻獸（4）
# =========================
st.subheader("🐉 幻獸（4 欄）")

st.number_input(
    "快速輸入幻獸等級（套用到全部）",
    key="beast_bulk",
    value=130,
    on_change=apply_bulk,
    kwargs={"prefix": "beast", "count": 4}
)

beast_cols = st.columns(4)
beast_eff = []

for i in range(4):
    with beast_cols[i]:
        lv = st.number_input(
            f"幻獸 {i+1}",
            key=f"beast_{i}",
            value=130
        )
        beast_eff.append(effective_lv(lv))

score_beast = sum(beast_eff) * p_beast

# =========================
# 古遺物（5 屬性 × 4）
# =========================
st.subheader("🔮 古遺物")

elements = ["光", "暗", "風", "水", "火"]
relic_eff = []

for element in elements:
    st.markdown(f"### {element}")

    st.number_input(
        f"{element}系快速輸入",
        key=f"{element}_bulk",
        value=130,
        on_change=apply_bulk,
        kwargs={"prefix": element, "count": 4}
    )

    cols = st.columns(4)
    for i in range(4):
        with cols[i]:
            lv = st.number_input(
                f"{element}-{i+1}",
                key=f"{element}_{i}",
                value=130
            )
            relic_eff.append(effective_lv(lv))

score_relic = sum(relic_eff) * p_relic

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
g2.metric("總原初之星", f"{grand_total_stars:,}")
