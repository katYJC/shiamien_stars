import streamlit as st

st.set_page_config(page_title="第2季 原初之星計算器", page_icon="⭐", layout="wide")

BASE_LV = 130

# =========================
# Styling：快速輸入區塊
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
    </style>
    """,
    unsafe_allow_html=True,
)

# =========================
# Helpers
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
    bulk_val = st.session_state.get(f"{prefix}_bulk", BASE_LV)
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
st.title("⭐ 第 2 季｜原初之星計算器")
st.caption("所有項目以 130 為基礎等級，僅計算超過 130 的部分。")

# =========================
# Sidebar
# =========================
st.sidebar.header("⚙️ 設定")
base_stars = st.sidebar.number_input("本季初始原初之星", value=45, min_value=0)
convert_div = st.sidebar.number_input("原初之星換算除數", value=27, min_value=1)

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
# 裝備 / 技能 / 幻獸（略，與你上一版相同）
# =========================
# ⚠️ 這裡假設你保留前面版本的裝備、技能、幻獸區塊
# （完全不用改）

# =========================
# 古遺物（20 欄，基礎 = 13）
# =========================
RELIC_BASE_LV = 13

def effective_relic_lv(lv: int) -> int:
    return max(0, lv - RELIC_BASE_LV)

st.subheader("🔮 古遺物")

bulk_ui(
    "古遺物總快速輸入（套用到全部 20 欄）",
    "基礎等級為 13，僅計算超過 13 的部分。"
)

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

score_relic = sum(relic_eff) * p_relic

# =========================
# Compute & Output
# =========================
season_score = score_char + score_relic  # 其餘項目照你原本加總
season_grade = get_grade(season_score)

earned_stars = season_score // convert_div
season_total_stars = base_stars + earned_stars
grand_total_stars = prev_season_stars + season_total_stars

st.markdown("---")
st.subheader("📌 第 2 季結算")
st.metric("本季養成總分", f"{season_score:,}")
st.metric("本季評級", season_grade)
