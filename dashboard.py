import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

st.set_page_config(
    page_title="EDA – משרד מודדים",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── סגנון ─────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .metric-card {
        background: linear-gradient(135deg, #1e3a5f 0%, #2d6a9f 100%);
        border-radius: 12px;
        padding: 24px 20px;
        text-align: center;
        color: white;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    .metric-label {
        font-size: 0.85rem;
        opacity: 0.8;
        margin-bottom: 6px;
        letter-spacing: 1px;
        text-transform: uppercase;
    }
    .metric-value {
        font-size: 2.4rem;
        font-weight: 700;
        line-height: 1;
    }
    .metric-sub {
        font-size: 0.8rem;
        opacity: 0.65;
        margin-top: 4px;
    }
    .section-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: #1e3a5f;
        border-right: 4px solid #2d6a9f;
        padding-right: 10px;
        margin-bottom: 12px;
    }
    div[data-testid="stSelectbox"] label { font-weight: 600; }
</style>
""", unsafe_allow_html=True)


# ── טעינת נתונים ──────────────────────────────────────────────────────────────
DEFAULT_CSV = Path(__file__).parent / "2025_cleaned.csv"

@st.cache_data
def load_data(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, encoding="utf-8-sig")

st.title("📊 ניתוח נתונים – EDA")
st.caption("מערכת ניתוח נתונים אינטראקטיבית – משרד מודדים")

uploaded = st.file_uploader("העלה קובץ CSV אחר (אופציונלי)", type="csv", label_visibility="collapsed")

if uploaded:
    df = pd.read_csv(uploaded, encoding="utf-8-sig")
    st.success(f"✅ נטען: {uploaded.name}")
elif DEFAULT_CSV.exists():
    df = load_data(DEFAULT_CSV)
else:
    st.error("לא נמצא קובץ 2025_cleaned.csv. אנא העלה קובץ.")
    st.stop()


# ── חישובים גלובליים ──────────────────────────────────────────────────────────
n_rows, n_cols = df.shape
total_cells = n_rows * n_cols
missing_cells = df.isna().sum().sum() + (df == "").sum().sum()
missing_pct = round(missing_cells / total_cells * 100, 1) if total_cells > 0 else 0.0

st.markdown("<br>", unsafe_allow_html=True)

# ── 3 מדדים בראש ──────────────────────────────────────────────────────────────
c1, c2, c3 = st.columns(3)

with c1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">🗂 שורות</div>
        <div class="metric-value">{n_rows:,}</div>
        <div class="metric-sub">רשומות בסיס</div>
    </div>""", unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">📋 עמודות</div>
        <div class="metric-value">{n_cols}</div>
        <div class="metric-sub">{', '.join(df.columns.tolist())}</div>
    </div>""", unsafe_allow_html=True)

with c3:
    color = "#e74c3c" if missing_pct > 10 else "#27ae60"
    st.markdown(f"""
    <div class="metric-card" style="background: linear-gradient(135deg, #1a3a2a 0%, {color} 100%);">
        <div class="metric-label">⚠️ ערכים חסרים</div>
        <div class="metric-value">{missing_pct}%</div>
        <div class="metric-sub">{missing_cells} תאים מתוך {total_cells:,}</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
st.divider()

# ── HISTOGRAM ─────────────────────────────────────────────────────────────────
st.markdown('<div class="section-title">📈 התפלגות עמודה</div>', unsafe_allow_html=True)

col_left, col_right = st.columns([1, 3])

with col_left:
    hist_col = st.selectbox("בחר עמודה להיסטוגרם", df.columns.tolist(), key="hist_col")

    is_numeric = pd.api.types.is_numeric_dtype(df[hist_col])
    n_unique = df[hist_col].nunique()
    n_missing_col = df[hist_col].isna().sum() + (df[hist_col] == "").sum()

    st.markdown(f"""
    **סוג:** {'מספרי 🔢' if is_numeric else 'קטגורי 🔤'}
    **ערכים ייחודיים:** {n_unique}
    **חסרים:** {n_missing_col}
    """)

    if is_numeric:
        n_bins = st.slider("מספר bins", 5, 50, 20, key="bins")
    else:
        top_n = st.slider("הצג Top N ערכים", 5, min(30, n_unique), min(15, n_unique), key="topn")

with col_right:
    if is_numeric:
        fig_hist = px.histogram(
            df, x=hist_col, nbins=n_bins,
            title=f"התפלגות: {hist_col}",
            color_discrete_sequence=["#2d6a9f"],
            template="plotly_white",
        )
        fig_hist.update_traces(marker_line_color="white", marker_line_width=0.5)
        fig_hist.update_layout(bargap=0.05, title_font_size=15,
                               xaxis_title=hist_col, yaxis_title="תדירות")
    else:
        counts = (
            df[hist_col].replace("", pd.NA).dropna()
            .value_counts().head(top_n).reset_index()
        )
        counts.columns = [hist_col, "count"]
        fig_hist = px.bar(
            counts, x=hist_col, y="count",
            title=f"תדירות ערכים: {hist_col}",
            color="count",
            color_continuous_scale="Blues",
            template="plotly_white",
        )
        fig_hist.update_layout(title_font_size=15, showlegend=False,
                               xaxis_title=hist_col, yaxis_title="כמות",
                               coloraxis_showscale=False)
        fig_hist.update_xaxes(tickangle=-35)

    st.plotly_chart(fig_hist, use_container_width=True)

st.divider()

# ── SCATTER PLOT ──────────────────────────────────────────────────────────────
st.markdown('<div class="section-title">🔵 Scatter Plot – השוואה בין שתי עמודות</div>',
            unsafe_allow_html=True)

sc1, sc2, sc3 = st.columns([1, 1, 1])

all_cols = df.columns.tolist()

with sc1:
    x_col = st.selectbox("ציר X", all_cols, index=0, key="sc_x")
with sc2:
    default_y = 1 if len(all_cols) > 1 else 0
    y_col = st.selectbox("ציר Y", all_cols, index=default_y, key="sc_y")
with sc3:
    color_options = ["ללא"] + all_cols
    color_col = st.selectbox("צבע לפי (אופציונלי)", color_options, key="sc_color")

color_arg = None if color_col == "ללא" else color_col

if x_col == y_col:
    st.warning("⚠️ בחר שתי עמודות שונות.")
else:
    scatter_df = df[[x_col, y_col] + ([color_col] if color_arg else [])].copy()
    scatter_df = scatter_df.replace("", pd.NA).dropna()

    if scatter_df.empty:
        st.error("אין נתונים לאחר הסרת ערכים חסרים.")
    else:
        x_num = pd.api.types.is_numeric_dtype(scatter_df[x_col])
        y_num = pd.api.types.is_numeric_dtype(scatter_df[y_col])

        if x_num and y_num:
            fig_sc = px.scatter(
                scatter_df, x=x_col, y=y_col,
                color=color_arg,
                trendline="ols",
                title=f"{x_col}  ↔  {y_col}",
                template="plotly_white",
                opacity=0.75,
                color_discrete_sequence=px.colors.qualitative.Set2,
            )
        else:
            fig_sc = px.strip(
                scatter_df, x=x_col, y=y_col,
                color=color_arg,
                title=f"{x_col}  ↔  {y_col}",
                template="plotly_white",
                color_discrete_sequence=px.colors.qualitative.Set2,
            )

        fig_sc.update_layout(title_font_size=15)
        st.plotly_chart(fig_sc, use_container_width=True)

        n_shown = len(scatter_df)
        st.caption(f"מוצגות {n_shown:,} רשומות מתוך {n_rows:,} (לאחר הסרת חסרים)")

st.divider()

# ── טבלת נתונים ───────────────────────────────────────────────────────────────
with st.expander("🗃 הצג טבלת נתונים מלאה"):
    st.dataframe(df, use_container_width=True, height=400)
