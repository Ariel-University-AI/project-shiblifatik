import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
import io

st.set_page_config(
    page_title="EDA – שיבלי-משרדית",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ══════════════════════════════════════════════════════════════════════════════
# CSS
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
/* ── Sidebar ── */
[data-testid="stSidebar"]               { background:#0d1f38; }
[data-testid="stSidebar"] *             { color:#cfe2f7 !important; }
[data-testid="stSidebar"] hr           { border-color:#1e3f66; }
[data-testid="stSidebar"] .stMultiSelect [data-baseweb="tag"] span
                                        { color:#0d1f38 !important; }
[data-testid="stSidebar"] .stFileUploader label { color:#cfe2f7 !important; }

/* ── Metric cards ── */
.kpi-wrap { display:flex; gap:16px; margin-bottom:8px; }
.kpi {
    flex:1; border-radius:14px; padding:22px 18px;
    background:linear-gradient(135deg,#1e3a5f,#2d6a9f);
    color:#fff; box-shadow:0 4px 18px rgba(0,0,0,.25);
    text-align:center;
}
.kpi.warn { background:linear-gradient(135deg,#4a1010,#c0392b); }
.kpi.ok   { background:linear-gradient(135deg,#0d3320,#1e8449); }
.kpi-lbl  { font-size:.75rem; letter-spacing:1.2px;
            text-transform:uppercase; opacity:.75; margin-bottom:6px; }
.kpi-val  { font-size:2.6rem; font-weight:800; line-height:1; }
.kpi-sub  { font-size:.72rem; opacity:.6; margin-top:4px; }

/* ── Section titles ── */
.sec {
    font-size:1rem; font-weight:700; color:#1e3a5f;
    border-right:4px solid #2d6a9f; padding-right:10px;
    margin:6px 0 14px;
}

/* ── Active-filter chip ── */
.chip {
    display:inline-block; background:#2d6a9f; color:#fff;
    border-radius:20px; padding:3px 14px; font-size:.78rem; margin-top:8px;
}
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════════════════
DEFAULT_CSV = Path(__file__).parent.parent / "data" / "2025_cleaned.csv"

@st.cache_data
def read_default() -> pd.DataFrame:
    return pd.read_csv(DEFAULT_CSV, encoding="utf-8-sig")

@st.cache_data
def read_upload(raw: bytes) -> pd.DataFrame:
    for enc in ("utf-8-sig", "utf-8", "cp1255", "iso-8859-8"):
        try:
            return pd.read_csv(io.BytesIO(raw), encoding=enc)
        except Exception:
            pass
    return pd.read_csv(io.BytesIO(raw), encoding="utf-8", errors="replace")


# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:

    # ── קובץ ──────────────────────────────────────────────────────────────────
    st.markdown("## 📂 מקור נתונים")
    upload = st.file_uploader("גרור / בחר קובץ CSV", type="csv", key="upload")

    # איפוס פקדי סינון כשמשתנה הקובץ
    src_key = upload.name if upload else "__default__"
    if st.session_state.get("_src") != src_key:
        for k in ("flt_col", "flt_vals"):
            st.session_state.pop(k, None)
        st.session_state["_src"] = src_key

    if upload:
        df = read_upload(upload.getvalue())
        st.success(f"✅ {upload.name}")
    elif DEFAULT_CSV.exists():
        df = read_default()
        st.caption("ברירת מחדל: 2025_cleaned.csv")
    else:
        st.error("לא נמצא קובץ. העלה CSV.")
        st.stop()

    st.caption(f"{len(df):,} שורות · {df.shape[1]} עמודות")
    st.divider()

    # ── סינון גלובלי ──────────────────────────────────────────────────────────
    st.markdown("## 🎯 סינון גלובלי")
    cat_cols = df.select_dtypes(include="object").columns.tolist()

    if cat_cols:
        flt_col = st.selectbox("סנן לפי עמודה:", cat_cols, key="flt_col")
        opts    = sorted(df[flt_col].replace("", pd.NA).dropna().unique())
        chosen  = st.multiselect(
            f"ערכים – {flt_col}:", opts, default=list(opts), key="flt_vals"
        )
        fdf = df[df[flt_col].isin(chosen)].copy() if chosen else df.copy()
        if not chosen:
            st.warning("אין ערכים נבחרים – מוצג הכל")
    else:
        fdf, flt_col, chosen = df.copy(), None, []
        st.info("אין עמודות קטגוריאליות")

    st.divider()
    pct = int(len(fdf) / len(df) * 100) if len(df) else 100
    st.progress(pct / 100, text=f"{len(fdf):,} / {len(df):,} שורות ({pct}%)")


# ══════════════════════════════════════════════════════════════════════════════
# HEADER
# ══════════════════════════════════════════════════════════════════════════════
st.title("📊 ניתוח נתונים – EDA")
src_label = upload.name if upload else "2025_cleaned.csv"
st.caption(f"קובץ: **{src_label}**" +
           (f"  ·  מסנן פעיל: **{flt_col}**" if flt_col and chosen and len(chosen) < len(opts) else ""))


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 1 – 3 KPI METRICS
# ══════════════════════════════════════════════════════════════════════════════
nr, nc = fdf.shape
tot     = nr * nc
miss    = int(fdf.isna().sum().sum() + (fdf == "").sum().sum())
miss_p  = round(miss / tot * 100, 1) if tot else 0.0
is_filt = len(fdf) < len(df)

c1, c2, c3 = st.columns(3)
with c1:
    sub = f"(מסונן מ-{len(df):,})" if is_filt else "רשומות"
    st.markdown(f"""
    <div class="kpi">
      <div class="kpi-lbl">🗂 שורות</div>
      <div class="kpi-val">{nr:,}</div>
      <div class="kpi-sub">{sub}</div>
    </div>""", unsafe_allow_html=True)

with c2:
    col_names = ", ".join(fdf.columns[:4]) + ("…" if nc > 4 else "")
    st.markdown(f"""
    <div class="kpi">
      <div class="kpi-lbl">📋 עמודות</div>
      <div class="kpi-val">{nc}</div>
      <div class="kpi-sub">{col_names}</div>
    </div>""", unsafe_allow_html=True)

with c3:
    klass = "warn" if miss_p > 10 else "ok"
    st.markdown(f"""
    <div class="kpi {klass}">
      <div class="kpi-lbl">⚠️ ערכים חסרים</div>
      <div class="kpi-val">{miss_p}%</div>
      <div class="kpi-sub">{miss:,} תאים מתוך {tot:,}</div>
    </div>""", unsafe_allow_html=True)

if is_filt and flt_col and chosen:
    n_chosen = len(chosen)
    st.markdown(
        f'<div class="chip">🔍 {flt_col}: {n_chosen} ערכים נבחרו</div>',
        unsafe_allow_html=True,
    )

st.markdown("<br>", unsafe_allow_html=True)
st.divider()


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 2 – HISTOGRAM (עמודות מספריות בלבד)
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="sec">📈 היסטוגרם – התפלגות עמודה מספרית</div>',
            unsafe_allow_html=True)

num_cols = fdf.select_dtypes(include="number").columns.tolist()

if not num_cols:
    st.info("אין עמודות מספריות בנתונים המסוננים.")
else:
    h_left, h_right = st.columns([1, 3])

    with h_left:
        h_col  = st.selectbox("עמודה מספרית:", num_cols, key="h_col")
        n_bins = st.slider("מספר Bins", 5, 60, 20, key="h_bins")

        col_data = fdf[h_col].replace("", pd.NA).dropna()
        st.markdown(f"""
| מדד | ערך |
|-----|-----|
| ממוצע | {col_data.mean():.2f} |
| חציון | {col_data.median():.2f} |
| סטיית תקן | {col_data.std():.2f} |
| מינימום | {col_data.min():.2f} |
| מקסימום | {col_data.max():.2f} |
""")

    with h_right:
        fig_h = px.histogram(
            fdf, x=h_col, nbins=n_bins,
            title=f"התפלגות: {h_col}",
            color_discrete_sequence=["#2d6a9f"],
            template="plotly_white",
            marginal="box",
        )
        fig_h.update_traces(marker_line_color="white", marker_line_width=0.6)
        fig_h.update_layout(
            bargap=0.04, title_font_size=15,
            xaxis_title=h_col, yaxis_title="תדירות",
            showlegend=False,
        )
        st.plotly_chart(fig_h, use_container_width=True)

st.divider()


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 3 – BAR CHART: ממוצע [X] לפי [Y]
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="sec">📊 Bar Chart – ממוצע [X] לפי [Y]</div>',
            unsafe_allow_html=True)

all_cols = fdf.columns.tolist()

b1, b2, b3 = st.columns([1, 1, 1])
with b1:
    x_num = st.selectbox(
        "עמודה מספרית [X] – לממוצע:",
        num_cols if num_cols else all_cols,
        key="b_x",
    )
with b2:
    cat_opts = cat_cols if cat_cols else all_cols
    y_cat = st.selectbox("עמודה קטגורית [Y] – לקיבוץ:", cat_opts, key="b_y")
with b3:
    top_k = st.slider("הצג Top K קבוצות", 3, min(30, fdf[y_cat].nunique()), 10, key="b_topk")

bar_df = (
    fdf[[x_num, y_cat]]
    .replace("", pd.NA).dropna()
    .groupby(y_cat, as_index=False)[x_num]
    .mean()
    .rename(columns={x_num: f"ממוצע {x_num}"})
    .sort_values(f"ממוצע {x_num}", ascending=False)
    .head(top_k)
)

if bar_df.empty:
    st.warning("אין נתונים לגרף.")
else:
    fig_b = px.bar(
        bar_df,
        x=y_cat, y=f"ממוצע {x_num}",
        title=f"ממוצע {x_num} לפי {y_cat}  (Top {top_k})",
        color=f"ממוצע {x_num}",
        color_continuous_scale="Blues",
        text_auto=".2f",
        template="plotly_white",
    )
    fig_b.update_traces(
        textposition="outside",
        marker_line_color="white", marker_line_width=0.5,
    )
    fig_b.update_layout(
        title_font_size=15,
        xaxis_title=y_cat, yaxis_title=f"ממוצע {x_num}",
        coloraxis_showscale=False,
        uniformtext_minsize=9, uniformtext_mode="hide",
    )
    fig_b.update_xaxes(tickangle=-35)
    st.plotly_chart(fig_b, use_container_width=True)
    st.caption(f"{len(bar_df)} קבוצות מוצגות · {len(fdf):,} רשומות בסיס")

st.divider()


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 4 – VALUE COUNTS: ספירת שכיחות לעמודה קטגורית
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="sec">🔢 ספירת שכיחות – מספר רשומות לפי קטגוריה</div>',
            unsafe_allow_html=True)

if not cat_cols:
    st.info("אין עמודות קטגוריאליות בנתונים המסוננים.")
else:
    vc1, vc2, vc3 = st.columns([1, 1, 1])
    with vc1:
        vc_col = st.selectbox("עמודה קטגורית:", cat_cols, key="vc_col")
    with vc2:
        vc_topk = st.slider("Top K", 3, min(30, fdf[vc_col].nunique()), 10, key="vc_topk")
    with vc3:
        vc_orient = st.radio("כיוון:", ["אנכי", "אופקי"], horizontal=True, key="vc_orient")

    vc_df = (
        fdf[vc_col].replace("", pd.NA).dropna()
        .value_counts().head(vc_topk)
        .reset_index()
    )
    vc_df.columns = [vc_col, "ספירה"]

    if vc_orient == "אופקי":
        fig_vc = px.bar(
            vc_df, y=vc_col, x="ספירה",
            orientation="h",
            title=f"ספירת שכיחות – {vc_col} (Top {vc_topk})",
            color="ספירה", color_continuous_scale="Blues",
            text_auto=True, template="plotly_white",
        )
        fig_vc.update_layout(yaxis=dict(autorange="reversed"))
    else:
        fig_vc = px.bar(
            vc_df, x=vc_col, y="ספירה",
            title=f"ספירת שכיחות – {vc_col} (Top {vc_topk})",
            color="ספירה", color_continuous_scale="Blues",
            text_auto=True, template="plotly_white",
        )
        fig_vc.update_xaxes(tickangle=-35)

    fig_vc.update_traces(marker_line_color="white", marker_line_width=0.5)
    fig_vc.update_layout(
        title_font_size=15, coloraxis_showscale=False,
        uniformtext_minsize=9, uniformtext_mode="hide",
    )
    st.plotly_chart(fig_vc, use_container_width=True)
    st.caption(f"{fdf[vc_col].nunique()} ערכים ייחודיים · {len(fdf):,} רשומות")

st.divider()


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 5 – PIE CHART: התפלגות עמודה קטגורית
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="sec">🥧 גרף עוגה – התפלגות קטגוריה</div>',
            unsafe_allow_html=True)

if not cat_cols:
    st.info("אין עמודות קטגוריאליות.")
else:
    p_left, p_right = st.columns([1, 3])
    with p_left:
        pie_col  = st.selectbox("עמודה:", cat_cols, key="pie_col")
        pie_topk = st.slider("Top K", 3, min(15, fdf[pie_col].nunique()), 8, key="pie_topk")
        pie_hole = st.slider("חור – דונאט", 0.0, 0.6, 0.3, 0.05, key="pie_hole")
    with p_right:
        pie_df = (
            fdf[pie_col].replace("", pd.NA).dropna()
            .value_counts().head(pie_topk)
            .reset_index()
        )
        pie_df.columns = [pie_col, "ספירה"]
        fig_pie = px.pie(
            pie_df, names=pie_col, values="ספירה",
            title=f"התפלגות: {pie_col} (Top {pie_topk})",
            hole=pie_hole,
            color_discrete_sequence=px.colors.sequential.Blues_r,
            template="plotly_white",
        )
        fig_pie.update_traces(
            textinfo="percent+label", textfont_size=12,
            pull=[0.03] * len(pie_df),
        )
        fig_pie.update_layout(title_font_size=15, showlegend=True)
        st.plotly_chart(fig_pie, use_container_width=True)

st.divider()


# ── טבלה ──────────────────────────────────────────────────────────────────────
with st.expander("🗃 טבלת נתונים (לאחר סינון)"):
    st.dataframe(fdf.reset_index(drop=True), use_container_width=True, height=380)
