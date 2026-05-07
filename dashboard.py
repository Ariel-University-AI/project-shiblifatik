import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from pathlib import Path

st.set_page_config(
    page_title="EDA – משרד מודדים",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── סגנון ─────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    [data-testid="stSidebar"] { background: #0f2540; }
    [data-testid="stSidebar"] * { color: #d6e4f7 !important; }
    [data-testid="stSidebar"] .stMultiSelect span { color: #0f2540 !important; }
    [data-testid="stSidebar"] hr { border-color: #2d6a9f; }

    .metric-card {
        background: linear-gradient(135deg, #1e3a5f 0%, #2d6a9f 100%);
        border-radius: 12px;
        padding: 24px 20px;
        text-align: center;
        color: white;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    .metric-label { font-size:0.82rem; opacity:0.8; margin-bottom:6px;
                    letter-spacing:1px; text-transform:uppercase; }
    .metric-value { font-size:2.4rem; font-weight:700; line-height:1; }
    .metric-sub   { font-size:0.78rem; opacity:0.65; margin-top:4px; }

    .section-title {
        font-size: 1.1rem; font-weight: 600; color: #1e3a5f;
        border-right: 4px solid #2d6a9f;
        padding-right: 10px; margin-bottom: 12px;
    }
    .filter-badge {
        background:#2d6a9f; color:white; border-radius:20px;
        padding:3px 12px; font-size:0.8rem; display:inline-block;
    }
</style>
""", unsafe_allow_html=True)


# ── טעינת נתונים ──────────────────────────────────────────────────────────────
DEFAULT_CSV = Path(__file__).parent / "2025_cleaned.csv"

@st.cache_data
def load_default() -> pd.DataFrame:
    return pd.read_csv(DEFAULT_CSV, encoding="utf-8-sig")

@st.cache_data
def load_uploaded(data: bytes) -> pd.DataFrame:
    import io
    for enc in ("utf-8-sig", "utf-8", "cp1255", "iso-8859-8"):
        try:
            return pd.read_csv(io.BytesIO(data), encoding=enc)
        except Exception:
            continue
    return pd.read_csv(io.BytesIO(data), encoding="utf-8", errors="replace")


# ════════════════════════════════════════════════════════════════════════════════
# SIDEBAR – העלאת קובץ + סינון גלובלי
# ════════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    # ── העלאת קובץ ────────────────────────────────────────────────────────────
    st.markdown("## 📂 מקור נתונים")
    uploaded = st.file_uploader(
        "גרור קובץ CSV לכאן",
        type="csv",
        help="תומך ב-UTF-8, UTF-8-BOM, CP1255 ו-ISO-8859-8",
        key="csv_upload",
    )

    # זיהוי החלפת קובץ – אפס פקדי סינון כדי שלא יתנגשו עם עמודות חדשות
    new_name = uploaded.name if uploaded else "__default__"
    if st.session_state.get("_active_file") != new_name:
        for k in ("filter_col", "filter_vals"):
            st.session_state.pop(k, None)
        st.session_state["_active_file"] = new_name

    if uploaded:
        df = load_uploaded(uploaded.getvalue())
        st.success(f"✅ {uploaded.name}")
        st.caption(f"{len(df):,} שורות · {df.shape[1]} עמודות")
    elif DEFAULT_CSV.exists():
        df = load_default()
        st.caption(f"ברירת מחדל: 2025_cleaned.csv  ({len(df):,} שורות)")
    else:
        st.error("לא נמצא קובץ ברירת מחדל.")
        st.stop()

    st.divider()

    # ── סינון גלובלי ──────────────────────────────────────────────────────────
    st.markdown("## 🎯 סינון גלובלי")
    st.markdown("הסינון משפיע על **כל הגרפים**")

    cat_cols = df.select_dtypes(include="object").columns.tolist()

    if cat_cols:
        filter_col = st.selectbox("סנן לפי עמודה:", cat_cols, key="filter_col")
        all_vals   = sorted(
            df[filter_col].replace("", pd.NA).dropna().unique().tolist()
        )
        selected = st.multiselect(
            f"בחר ערכים ({filter_col}):",
            options=all_vals,
            default=all_vals,
            key="filter_vals",
        )
        fdf = df[df[filter_col].isin(selected)].copy() if selected else df.copy()
        if not selected:
            st.warning("לא נבחרו ערכים – מוצגים כל הנתונים")
    else:
        fdf = df.copy()
        filter_col, selected = None, []
        st.info("אין עמודות קטגוריאליות לסינון")

    st.divider()
    st.markdown(f"**שורות לאחר סינון:** `{len(fdf):,}` / `{len(df):,}`")
    pct_shown = round(len(fdf) / len(df) * 100) if len(df) else 0
    st.progress(pct_shown / 100, text=f"{pct_shown}% מהנתונים")


# ════════════════════════════════════════════════════════════════════════════════
# 3 מדדים – מחושבים על הנתונים המסוננים
# ════════════════════════════════════════════════════════════════════════════════
n_rows_f, n_cols_f = fdf.shape
total_cells  = n_rows_f * n_cols_f
missing_cells = fdf.isna().sum().sum() + (fdf == "").sum().sum()
missing_pct   = round(missing_cells / total_cells * 100, 1) if total_cells > 0 else 0.0

is_filtered = len(fdf) < len(df)
filter_note = f" (מסונן מ-{len(df):,})" if is_filtered else ""

st.markdown("<br>", unsafe_allow_html=True)
c1, c2, c3 = st.columns(3)

with c1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">🗂 שורות</div>
        <div class="metric-value">{n_rows_f:,}</div>
        <div class="metric-sub">רשומות{filter_note}</div>
    </div>""", unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">📋 עמודות</div>
        <div class="metric-value">{n_cols_f}</div>
        <div class="metric-sub">{', '.join(fdf.columns.tolist())}</div>
    </div>""", unsafe_allow_html=True)

with c3:
    card_color = "#e74c3c" if missing_pct > 10 else "#27ae60"
    st.markdown(f"""
    <div class="metric-card"
         style="background:linear-gradient(135deg,#1a3a2a 0%,{card_color} 100%);">
        <div class="metric-label">⚠️ ערכים חסרים</div>
        <div class="metric-value">{missing_pct}%</div>
        <div class="metric-sub">{missing_cells} תאים מתוך {total_cells:,}</div>
    </div>""", unsafe_allow_html=True)

if is_filtered:
    st.markdown(
        f'<div style="margin-top:10px">'
        f'<span class="filter-badge">🔍 מסנן פעיל: {filter_col} → '
        f'{len(selected)} ערכים נבחרו</span></div>',
        unsafe_allow_html=True,
    )

st.markdown("<br>", unsafe_allow_html=True)
st.divider()


# ════════════════════════════════════════════════════════════════════════════════
# HISTOGRAM
# ════════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-title">📈 התפלגות עמודה</div>',
            unsafe_allow_html=True)

col_left, col_right = st.columns([1, 3])

with col_left:
    hist_col   = st.selectbox("בחר עמודה להיסטוגרם",
                               fdf.columns.tolist(), key="hist_col")
    is_numeric = pd.api.types.is_numeric_dtype(fdf[hist_col])
    n_unique   = fdf[hist_col].nunique()
    n_miss     = int(fdf[hist_col].isna().sum() + (fdf[hist_col] == "").sum())

    st.markdown(f"""
**סוג:** {'מספרי 🔢' if is_numeric else 'קטגורי 🔤'}
**ייחודיים:** {n_unique}
**חסרים:** {n_miss}
""")
    if is_numeric:
        n_bins = st.slider("מספר bins", 5, 50, 20, key="bins")
    else:
        top_n = st.slider("Top N ערכים",
                          5, max(5, min(30, n_unique)),
                          min(15, max(5, n_unique)), key="topn")

with col_right:
    if is_numeric:
        fig_hist = px.histogram(
            fdf, x=hist_col, nbins=n_bins,
            title=f"התפלגות: {hist_col}",
            color_discrete_sequence=["#2d6a9f"],
            template="plotly_white",
        )
        fig_hist.update_traces(marker_line_color="white", marker_line_width=0.5)
        fig_hist.update_layout(bargap=0.05, title_font_size=15,
                                xaxis_title=hist_col, yaxis_title="תדירות")
    else:
        counts = (fdf[hist_col].replace("", pd.NA).dropna()
                  .value_counts().head(top_n).reset_index())
        counts.columns = [hist_col, "count"]
        fig_hist = px.bar(
            counts, x=hist_col, y="count",
            title=f"תדירות ערכים: {hist_col}",
            color="count", color_continuous_scale="Blues",
            template="plotly_white",
        )
        fig_hist.update_layout(title_font_size=15, showlegend=False,
                                xaxis_title=hist_col, yaxis_title="כמות",
                                coloraxis_showscale=False)
        fig_hist.update_xaxes(tickangle=-35)

    st.plotly_chart(fig_hist, use_container_width=True)

st.divider()


# ════════════════════════════════════════════════════════════════════════════════
# SCATTER PLOT
# ════════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-title">🔵 Scatter Plot – השוואה בין שתי עמודות</div>',
            unsafe_allow_html=True)

all_cols = fdf.columns.tolist()
sc1, sc2, sc3 = st.columns(3)

with sc1:
    x_col = st.selectbox("ציר X", all_cols, index=0, key="sc_x")
with sc2:
    y_col = st.selectbox("ציר Y", all_cols,
                          index=min(1, len(all_cols) - 1), key="sc_y")
with sc3:
    color_col = st.selectbox("צבע לפי", ["ללא"] + all_cols, key="sc_color")

color_arg = None if color_col == "ללא" else color_col

if x_col == y_col:
    st.warning("⚠️ בחר שתי עמודות שונות.")
else:
    needed = [x_col, y_col] + ([color_col] if color_arg else [])
    scatter_df = fdf[needed].replace("", pd.NA).dropna()

    if scatter_df.empty:
        st.error("אין נתונים לאחר הסרת ערכים חסרים.")
    else:
        x_num = pd.api.types.is_numeric_dtype(scatter_df[x_col])
        y_num = pd.api.types.is_numeric_dtype(scatter_df[y_col])

        if x_num and y_num:
            fig_sc = px.scatter(
                scatter_df, x=x_col, y=y_col, color=color_arg,
                trendline="ols",
                title=f"{x_col}  ↔  {y_col}",
                template="plotly_white", opacity=0.75,
                color_discrete_sequence=px.colors.qualitative.Set2,
            )
        else:
            fig_sc = px.strip(
                scatter_df, x=x_col, y=y_col, color=color_arg,
                title=f"{x_col}  ↔  {y_col}",
                template="plotly_white",
                color_discrete_sequence=px.colors.qualitative.Set2,
            )

        fig_sc.update_layout(title_font_size=15)
        st.plotly_chart(fig_sc, use_container_width=True)
        st.caption(
            f"מוצגות {len(scatter_df):,} רשומות מתוך {n_rows_f:,} (לאחר הסרת חסרים)"
        )

st.divider()


# ════════════════════════════════════════════════════════════════════════════════
# HEATMAP קורלציה
# ════════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-title">🔥 Heatmap – מפת קורלציות</div>',
            unsafe_allow_html=True)

def cramers_v(a: pd.Series, b: pd.Series) -> float:
    """Cramér's V – מידת הקשר בין שתי עמודות קטגוריאליות (0=אין, 1=מלא)."""
    ct = pd.crosstab(a, b)
    n  = ct.sum().sum()
    if n == 0:
        return 0.0
    chi2 = 0.0
    row_totals = ct.sum(axis=1)
    col_totals = ct.sum(axis=0)
    for i in ct.index:
        for j in ct.columns:
            expected = row_totals[i] * col_totals[j] / n
            if expected > 0:
                chi2 += (ct.loc[i, j] - expected) ** 2 / expected
    phi2 = chi2 / n
    r, k = ct.shape
    v = np.sqrt(phi2 / max(min(k - 1, r - 1), 1))
    return round(float(np.clip(v, 0, 1)), 3)


@st.cache_data
def build_corr_matrix(data: pd.DataFrame) -> tuple[pd.DataFrame, str]:
    """
    מחשב מטריצת קשרים:
    - עמודות מספריות: Pearson r
    - עמודות קטגוריאליות: Cramér's V
    - עמודה מספרית + קטגוריאלית: Eta (קורלציה נקודה-בי-סריאל)
    מחזיר גם טקסט הסבר.
    """
    cols = data.columns.tolist()
    mat = pd.DataFrame(np.nan, index=cols, columns=cols)

    for i, ci in enumerate(cols):
        for j, cj in enumerate(cols):
            if i == j:
                mat.loc[ci, cj] = 1.0
                continue
            ai = data[ci].replace("", pd.NA).dropna()
            aj = data[cj].replace("", pd.NA).dropna()
            common = ai.index.intersection(aj.index)
            if len(common) < 3:
                mat.loc[ci, cj] = 0.0
                continue
            si, sj = data.loc[common, ci], data.loc[common, cj]
            ni = pd.api.types.is_numeric_dtype(si)
            nj = pd.api.types.is_numeric_dtype(sj)

            if ni and nj:
                corr = si.corr(sj)
                mat.loc[ci, cj] = round(float(corr) if not np.isnan(corr) else 0, 3)
            elif not ni and not nj:
                mat.loc[ci, cj] = cramers_v(si, sj)
            else:
                # Eta: variance explained by category on numeric
                num_s = si if ni else sj
                cat_s = si if not ni else sj
                grand_mean = num_s.mean()
                ss_total = ((num_s - grand_mean) ** 2).sum()
                ss_between = sum(
                    len(grp) * (grp.mean() - grand_mean) ** 2
                    for _, grp in num_s.groupby(cat_s)
                )
                eta = np.sqrt(ss_between / ss_total) if ss_total > 0 else 0.0
                mat.loc[ci, cj] = round(float(np.clip(eta, 0, 1)), 3)

    method_note = (
        "Pearson r (מספרי↔מספרי) | Cramér's V (קטגורי↔קטגורי) | Eta (מספרי↔קטגורי)"
    )
    return mat.astype(float), method_note


hm_df, method_note = build_corr_matrix(fdf)

hm_cols  = st.columns([3, 1])
with hm_cols[1]:
    st.markdown("**הסבר מדדים:**")
    st.markdown("""
- **Pearson r** – קורלציה לינארית (מספרי ↔ מספרי)
- **Cramér's V** – עוצמת קשר (קטגורי ↔ קטגורי)
- **Eta** – שונות מוסברת (מספרי ↔ קטגורי)

**ספק ערכים:**
- `1.0` = קשר מושלם
- `0.0` = אין קשר
""")
    show_vals = st.toggle("הצג ערכים על המפה", value=True, key="hm_vals")

with hm_cols[0]:
    fig_hm = px.imshow(
        hm_df.round(2),
        text_auto=show_vals,
        color_continuous_scale="RdBu",
        zmin=-1, zmax=1,
        title="מפת קורלציות / קשרים בין עמודות",
        aspect="auto",
    )
    fig_hm.update_layout(
        title_font_size=15,
        template="plotly_white",
        height=420,
    )
    st.plotly_chart(fig_hm, use_container_width=True)
    st.caption(f"שיטות: {method_note}")

st.divider()

# ── טבלת נתונים ───────────────────────────────────────────────────────────────
with st.expander("🗃 הצג טבלת נתונים מלאה (לאחר סינון)"):
    st.dataframe(fdf, use_container_width=True, height=400)
