import streamlit as st

st.set_page_config(page_title="第2季 原初之星計算器", page_icon="⭐", layout="wide")

# ---------- Helpers ----------
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

# ---------- Title ----------
st.title("⭐ 第 2 季｜原初之星計算器（賽季養成評分）")
st.caption("輸入本季提升等級，自動計算：本季養成總分、評級、換得原初之星，並可加總上季原初之星。")

# ---------- Sidebar settings ----------
st.sidebar.header("設定")
base_stars = st.sidebar.number_input("本季初始原初之星", min_value=0, value=45, step=1)
convert_div = st.sidebar.number_input("原初之星換算除數（總分 / X 取整）", min_value=1, value=27, step=1)

st.sidebar.markdown("---")
st.sidebar.subheader("加分規則（可調）")
p_char = st.sidebar.number_input("角色等級：每 +1 加分", min_value=0, value=100, step=1)
p_equip = st.sidebar.number_input("裝備強化：每 +1 加分", min_value=0, value=18, step=1)
p_skill = st.sidebar.number_input("技能等級：每 +1 加分", min_value=0, value=7, step=1)
p_beast = st.sidebar.number_input("幻獸等級：每 +1 加分", min_value=0, value=8, step=1)
p_relic = st.sidebar.number_input("古遺物等級：每 +1 加分", min_value=0, value=33, step=1)

# ---------- Main inputs ----------
top_left, top_right = st.columns([1, 1])

with top_left:
    st.subheader("0) 上季結餘")
    prev_season_stars = st.number_input("上個賽季原初之星（帶入加總）", min_value=0, value=0, step=1)

with top_right:
    st.subheader("1) 角色等級")
    char_lv_up = st.number_input("本賽季角色等級提升（+幾級）", min_value=0, value=0, step=1)

st.markdown("---")

# Equipment (5)
st.subheader("2) 裝備（5 欄）")
equip_cols = st.columns(5)
equip_ups = []
for i in range(5):
    with equip_cols[i]:
        equip_ups.append(st.number_input(f"裝備{i+1}", min_value=0, value=0, step=1))

# Skills (8)
st.subheader("3) 技能（8 欄）")
skill_cols = st.columns(4)
skill_ups = []
for i in range(8):
    with skill_cols[i % 4]:
        skill_ups.append(st.number_input(f"技能{i+1}", min_value=0, value=0, step=1))

# Beasts (4)
st.subheader("4) 幻獸（4 欄）")
beast_cols = st.columns(4)
beast_ups = []
for i in range(4):
    with beast_cols[i]:
        beast_ups.append(st.number_input(f"幻獸{i+1}", min_value=0, value=0, step=1))

# Relics (20)
st.subheader("5) 古遺物（4 × 5 = 20 欄）")
st.caption("以第 1 組～第 4 組，每組 5 欄呈現。")
relic_ups = []
for group in range(4):
    st.markdown(f"**第 {group+1} 組（5 欄）**")
    relic_cols = st.columns(5)
    for j in range(5):
        with relic_cols[j]:
            relic_ups.append(st.number_input(f"G{group+1}-{j+1}", min_value=0, value=0, step=1))

st.markdown("---")

# ---------- Compute ----------
score_char = int(char_lv_up) * int(p_char)
score_equip = sum_list(equip_ups) * int(p_equip)
score_skill = sum_list(skill_ups) * int(p_skill)
score_beast = sum_list(beast_ups) * int(p_beast)
score_relic = sum_list(relic_ups) * int(p_relic)

season_score = score_char + score_equip + score_skill + score_beast + score_relic
season_grade = get_grade(season_score)

earned_stars = season_score // int(convert_div)
season_total_stars = int(base_stars) + int(earned_stars)

grand_total_stars = int(prev_season_stars) + int(season_total_stars)

# ---------- Output ----------
st.subheader("📌 第 2 季計算結果（含評級）")

c1, c2, c3, c4 = st.columns(4)
c1.metric("本季養成總分", f"{season_score:,}")
c2.metric("本季總分評級", season_grade)
c3.metric("本季換得原初之星", f"{earned_stars:,}")
c4.metric("本季原初之星合計（含初始）", f"{season_total_stars:,}")

st.markdown("### ⭐ 原初之星總計（上季 + 本季）")
t1, t2 = st.columns(2)
t1.metric("上季原初之星", f"{int(prev_season_stars):,}")
t2.metric("總原初之星（上季 + 本季）", f"{grand_total_stars:,}")

with st.expander("查看本季得分明細"):
    st.write(
        {
            "角色等級得分": score_char,
            "裝備得分": score_equip,
            "技能得分": score_skill,
            "幻獸得分": score_beast,
            "古遺物得分": score_relic,
            "本季總分": season_score,
            "本季評級": season_grade,
            "本季原初之星（總分/除數取整）": earned_stars,
            "本季初始原初之星": base_stars,
            "本季原初之星合計": season_total_stars,
            "上季原初之星": prev_season_stars,
            "上季+本季總原初之星": grand_total_stars,
        }
    )

st.caption("若你有『賽季結束保底原初之星』或『超出等級上限按比例計分』等規則，我也能幫你加進去。")
