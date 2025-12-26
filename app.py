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
BASE_LV = 130
RELIC_BASE_LV = 13

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
      .bulk-title {
        font-weight: 800;
        font-size: 0.98rem;
      }
      .bulk-hint {
        color: rgba(0,0,0,0.6);
        font-size: 0.85rem;
      }
      .brand-footer {
        margin-top: 48px;
        padding: 18px 12px;
        background: linear-gradient(90deg, rgba(255,193,7,0.15), rgba(255,193,7,0.04));
        border-top: 2px solid rgba(255,193,7,0.85);
        text-align: center;
      }
      .brand-title {
        font-size: 1.05rem;
        font-weight: 700;
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
    bulk_key = f"{prefix}_bulk"
    last_key = f"{prefix}_last_bulk"
    bulk_val = st.session_state.get(bulk_key)

    # bulk 沒變 → 不覆蓋，允許微調
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
st.caption("快速輸入只在改變時套用，之後可自由微調。")

# =========================
# Sidebar
# =========================
st.sidebar.header("⚙️ 設定")
base_stars = st.sidebar.number_input("本季初始原初之星", value=45)
convert_div = st.sidebar.number_input("原初之星換算除數", value=27)

p_char  = st.sidebar.number_input("角色 +1 加分", value=100)
p_equip = st.sidebar.number_input("裝備 +1 加分", value=18)
p_skill = st.sidebar.number_input("技能 +1 加分", value=7)
p_beast = st.sidebar.number_input("幻獸 +1 加分", value=8)
p_relic = st.sidebar.number_input("古遺物 +1 加分", value=33)

# =========================
# Character
# =========================
char_lv = st.number_input("目前角色等級（基礎 130）", value=130, min_value=1)
score_char = effective_lv(char_lv) * p_char

# =========================
# Equipment (5)
# =========================
st.subheader("🛡 裝備")
bulk_ui("裝備快速輸入", "只在你改變此值時才會覆蓋 5 欄")

st.number_input(
    "equip_bulk_label",
    key="equip_bulk",
    value=130,
    on_change=apply_bulk,
    kwargs={"prefix": "equip", "count": 5},
    label_visibility="collapsed"
)

equip_eff = []
cols = st.columns(5)
for i in range(5):
    with cols[i]:
        lv = st.number_input(f"裝備{i+1}", key=f"equip_{i}", value=130)
        equip_eff.append(effective_lv(lv))
score_equip = sum(equip_eff) * p_equip

# =========================
# Relic (20)
# =========================
st.subheader("🔮 古遺物")
bulk_ui("古遺物總快速輸入", "基礎 13，可先套用再微調")

st.number_input(
    "relic_bulk_label",
    key="relic_bulk",
    value=13,
    on_change=apply_bulk,
    kwargs={"prefix": "relic", "count": 20},
    label_visibility="collapsed"
)

relic_eff = []
cols = st.columns(4)
for i in range(20):
    with cols[i % 4]:
        lv = st.number_input(f"古遺物{i+1}", key=f"relic_{i}", value=13)
        relic_eff.append(effective_relic_lv(lv))
score_relic = sum(relic_eff) * p_relic

# =========================
# Compute
# =========================
season_score = score_char + score_equip + score_relic
season_grade = get_grade(season_score)

# =========================
# Output
# =========================
st.metric("本季養成總分", season_score)
st.metric("本季評級", season_grade)

with st.expander("📊 得分明細"):
    st.write({
        "角色": score_char,
        "裝備": score_equip,
        "古遺物": score_relic
    })

st.markdown(
    """
    <div class="brand-footer">
        <div class="brand-title">原初之星計算器｜Season 2</div>
        <div class="brand-author">by 甜蝦麵(浮世千澤：夢 熱烈招生中！)</div>
    </div>
    """,
    unsafe_allow_html=True,
)
