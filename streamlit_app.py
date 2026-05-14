import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
import io
import re
try:
    import joblib
    JOBLIB_OK = True
except ImportError:
    JOBLIB_OK = False

st.set_page_config(
    page_title="EDA – משרד מודדים",
    page_icon="📐",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Heebo:wght@300;400;600;800&display=swap');
html, body, [class*="css"]  { font-family:'Heebo',sans-serif; direction:rtl; }

[data-testid="stSidebar"]             { background:#0d1f38; }
[data-testid="stSidebar"] *           { color:#cfe2f7 !important; }
[data-testid="stSidebar"] hr          { border-color:#1e3f66; }
[data-testid="stSidebar"] .stMultiSelect [data-baseweb="tag"] span
                                       { color:#0d1f38 !important; }

.hero {
    background: linear-gradient(135deg,#0d1f38 0%,#1a4a7a 60%,#0d3b6e 100%);
    border-radius:18px; padding:48px 40px; text-align:center;
    color:#fff; margin-bottom:14px;
}
.hero-title { font-size:2.6rem; font-weight:800; margin:0 0 10px; }
.hero-sub   { font-size:1rem; opacity:.75; max-width:560px;
              margin:0 auto; line-height:1.7; }

.kpi-wrap { display:flex; gap:14px; margin:10px 0; }
.kpi {
    flex:1; border-radius:14px; padding:22px 16px;
    background:linear-gradient(135deg,#1e3a5f,#2d6a9f);
    color:#fff; box-shadow:0 4px 18px rgba(0,0,0,.25); text-align:center;
}
.kpi.ok   { background:linear-gradient(135deg,#0d3320,#1e8449); }
.kpi.warn { background:linear-gradient(135deg,#4a1010,#c0392b); }
.kpi-lbl  { font-size:.73rem; letter-spacing:1.2px; text-transform:uppercase;
            opacity:.75; margin-bottom:6px; }
.kpi-val  { font-size:2.4rem; font-weight:800; line-height:1; }
.kpi-sub  { font-size:.7rem; opacity:.6; margin-top:4px; }

.sec {
    font-size:1rem; font-weight:700; color:#1e3a5f;
    border-right:4px solid #2d6a9f; padding-right:10px;
    margin:14px 0 12px;
}
.insight {
    background:#f0f5fc; border-right:4px solid #2d6a9f;
    border-radius:8px; padding:14px 16px; margin:10px 0;
    font-size:.9rem; color:#1e3a5f; line-height:1.75;
}
.badge-wrap { display:flex; flex-wrap:wrap; gap:8px; margin-top:10px; }
.badge {
    background:#e3eef9; border:1px solid #cfe0f7;
    border-radius:8px; padding:5px 13px;
    font-size:.82rem; font-weight:600; color:#1e3a5f;
}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# DATA LOADING
# ══════════════════════════════════════════════════════════════════════════════
DEFAULT_CSV = Path(__file__).parent / "2025_cleaned.csv"
MODEL_PATH  = Path(__file__).parent / "models" / "model.pkl"


def _first_number(val: str) -> int:
    m = re.search(r"\d+", str(val))
    return int(m.group()) if m else 0


def _count_numbers(val: str) -> int:
    return len(re.findall(r"\d+", str(val)))


@st.cache_resource
def load_model():
    if not JOBLIB_OK or not MODEL_PATH.exists():
        return None
    return joblib.load(MODEL_PATH)

@st.cache_data
def read_csv_bytes(raw: bytes) -> pd.DataFrame:
    for enc in ("utf-8-sig", "utf-8", "cp1255", "iso-8859-8"):
        try:
            return pd.read_csv(io.BytesIO(raw), encoding=enc)
        except Exception:
            pass
    return pd.read_csv(io.BytesIO(raw), encoding="utf-8", errors="replace")

@st.cache_data
def read_default() -> pd.DataFrame:
    return pd.read_csv(DEFAULT_CSV, encoding="utf-8-sig")

with st.sidebar:
    st.markdown("## 📂 מקור נתונים")
    upload = st.file_uploader("העלה קובץ CSV", type="csv")

    if upload:
        df = read_csv_bytes(upload.getvalue())
        st.success(f"✅ {upload.name}")
    elif DEFAULT_CSV.exists():
        df = read_default()
        st.caption("ברירת מחדל: 2025_cleaned.csv")
    else:
        st.error("לא נמצא קובץ נתונים. העלה CSV.")
        st.stop()

    st.caption(f"{len(df):,} שורות · {df.shape[1]} עמודות")
    st.divider()

    st.markdown("## 🎯 סינון גלובלי")
    cat_cols = df.select_dtypes(include="object").columns.tolist()
    if cat_cols:
        flt_col = st.selectbox("סנן לפי עמודה:", cat_cols)
        opts    = sorted(df[flt_col].replace("", pd.NA).dropna().unique())
        chosen  = st.multiselect(f"ערכים – {flt_col}:", opts, default=list(opts))
        fdf = df[df[flt_col].isin(chosen)].copy() if chosen else df.copy()
        if not chosen:
            st.warning("אין ערכים נבחרים – מוצג הכל")
            fdf = df.copy()
    else:
        fdf = df.copy()
        flt_col, chosen, opts = None, [], []

    pct = int(len(fdf) / len(df) * 100) if len(df) else 100
    st.progress(pct / 100, text=f"{len(fdf):,} / {len(df):,} ({pct}%)")

# ══════════════════════════════════════════════════════════════════════════════
# HERO
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="hero">
    <div class="hero-title">📐 EDA – משרד מודדים</div>
    <div class="hero-sub">
        ניתוח מקיף של נתוני עבודות המדידה – סטטיסטיקות, התפלגויות,
        ניתוח קטגורי וניתוח צולב אינטראקטיבי
    </div>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# COMPUTED BASICS (used in multiple tabs)
# ══════════════════════════════════════════════════════════════════════════════
nr, nc     = fdf.shape
tot_cells  = nr * nc
miss_cells = int(fdf.isna().sum().sum() + (fdf == "").sum().sum())
miss_pct   = round(miss_cells / tot_cells * 100, 1) if tot_cells else 0.0
dup_rows   = int(fdf.duplicated().sum())
num_cols   = fdf.select_dtypes(include="number").columns.tolist()

# ══════════════════════════════════════════════════════════════════════════════
# TABS
# ══════════════════════════════════════════════════════════════════════════════
t1, t2, t3, t4, t5, t6 = st.tabs([
    "📊 סקירה כללית",
    "🔍 איכות נתונים",
    "📈 התפלגויות",
    "🥧 ניתוח קטגורי",
    "📊 ניתוח צולב",
    "🤖 חיזוי AI",
])

# ─────────────────────────────────────────────────────────────────────────────
# TAB 1 – OVERVIEW
# ─────────────────────────────────────────────────────────────────────────────
with t1:
    st.markdown('<div class="sec">📌 מדדי מפתח</div>', unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        sub = f"(מסונן מ-{len(df):,})" if len(fdf) < len(df) else "רשומות סה\"כ"
        st.markdown(f"""<div class="kpi">
          <div class="kpi-lbl">🗂 שורות</div>
          <div class="kpi-val">{nr:,}</div>
          <div class="kpi-sub">{sub}</div></div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class="kpi">
          <div class="kpi-lbl">📋 עמודות</div>
          <div class="kpi-val">{nc}</div>
          <div class="kpi-sub">{', '.join(fdf.columns[:3])}…</div></div>""", unsafe_allow_html=True)
    with c3:
        klass = "warn" if miss_pct > 10 else "ok"
        st.markdown(f"""<div class="kpi {klass}">
          <div class="kpi-lbl">⚠️ ערכים חסרים</div>
          <div class="kpi-val">{miss_pct}%</div>
          <div class="kpi-sub">{miss_cells:,} / {tot_cells:,} תאים</div></div>""",
          unsafe_allow_html=True)
    with c4:
        klass2 = "warn" if dup_rows > 0 else "ok"
        st.markdown(f"""<div class="kpi {klass2}">
          <div class="kpi-lbl">🔁 שורות כפולות</div>
          <div class="kpi-val">{dup_rows}</div>
          <div class="kpi-sub">{"נמצאו כפילויות!" if dup_rows else "אין כפילויות"}</div></div>""",
          unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown('<div class="sec">📋 תצוגה מקדימה</div>', unsafe_allow_html=True)
    view_n = st.slider("מספר שורות להצגה", 5, 50, 10)
    st.dataframe(fdf.head(view_n), use_container_width=True)

    st.markdown('<div class="sec">🗂 מידע על עמודות</div>', unsafe_allow_html=True)
    col_info = pd.DataFrame({
        "עמודה":          fdf.columns,
        "סוג נתון":       fdf.dtypes.astype(str).values,
        "ערכים ייחודיים": [fdf[c].nunique() for c in fdf.columns],
        "ערכים חסרים":    [int(fdf[c].isna().sum() + (fdf[c] == "").sum())
                           for c in fdf.columns],
        "דוגמה":          [str(fdf[c].replace("", pd.NA).dropna().iloc[0])
                           if fdf[c].replace("", pd.NA).dropna().shape[0] > 0 else "–"
                           for c in fdf.columns],
    })
    st.dataframe(col_info, use_container_width=True, hide_index=True)

    if num_cols:
        st.markdown('<div class="sec">📐 סטטיסטיקה תיאורית (עמודות מספריות)</div>',
                    unsafe_allow_html=True)
        desc = fdf[num_cols].describe().T.rename(columns={
            "count": "ספירה", "mean": "ממוצע", "std": "סטיית תקן",
            "min": "מינ", "25%": "Q1", "50%": "חציון", "75%": "Q3", "max": "מקס",
        })
        st.dataframe(desc.round(2), use_container_width=True)
    else:
        st.info("אין עמודות מספריות בנתונים.")

    st.markdown('<div class="sec">📥 הורדת נתונים מסוננים</div>', unsafe_allow_html=True)
    csv_dl = fdf.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")
    st.download_button(
        "⬇️ הורד CSV מסונן",
        data=csv_dl,
        file_name="filtered_data.csv",
        mime="text/csv",
    )


# ─────────────────────────────────────────────────────────────────────────────
# TAB 2 – DATA QUALITY
# ─────────────────────────────────────────────────────────────────────────────
with t2:
    st.markdown('<div class="sec">🔍 דוח איכות נתונים</div>', unsafe_allow_html=True)

    q_left, q_right = st.columns(2)

    with q_left:
        miss_per_col = pd.DataFrame({
            "עמודה": fdf.columns,
            "חסרים": [int(fdf[c].isna().sum() + (fdf[c] == "").sum()) for c in fdf.columns],
            "אחוז":  [round((fdf[c].isna().sum() + (fdf[c] == "").sum()) / len(fdf) * 100, 1)
                      for c in fdf.columns],
        })
        fig_miss = px.bar(
            miss_per_col, x="עמודה", y="אחוז",
            title="אחוז ערכים חסרים לפי עמודה",
            color="אחוז",
            color_continuous_scale=["#1e8449", "#f39c12", "#c0392b"],
            range_color=[0, 100],
            text_auto=".1f",
            template="plotly_white",
        )
        fig_miss.update_layout(title_font_size=14, coloraxis_showscale=False,
                               yaxis_range=[0, 110])
        fig_miss.update_traces(textposition="outside")
        st.plotly_chart(fig_miss, use_container_width=True)

    with q_right:
        completeness = pd.DataFrame({
            "עמודה":     fdf.columns,
            "שלמות (%)": [round((1 - (fdf[c].isna().sum() + (fdf[c] == "").sum()) / len(fdf)) * 100, 1)
                          for c in fdf.columns],
        })
        fig_comp = px.bar(
            completeness, x="שלמות (%)", y="עמודה",
            orientation="h",
            title="אחוז שלמות לכל עמודה",
            color="שלמות (%)",
            color_continuous_scale=["#c0392b", "#f39c12", "#1e8449"],
            range_color=[0, 100],
            text_auto=".1f",
            template="plotly_white",
        )
        fig_comp.update_layout(title_font_size=14, coloraxis_showscale=False,
                               xaxis_range=[0, 110],
                               yaxis=dict(autorange="reversed"))
        fig_comp.update_traces(textposition="outside")
        st.plotly_chart(fig_comp, use_container_width=True)

    st.markdown('<div class="sec">📊 ערכים ייחודיים לפי עמודה</div>', unsafe_allow_html=True)
    unique_df = pd.DataFrame({
        "עמודה":            fdf.columns,
        "ערכים ייחודיים":   [fdf[c].nunique() for c in fdf.columns],
        "אחוז ייחודיות (%)": [round(fdf[c].nunique() / len(fdf) * 100, 1) for c in fdf.columns],
    })
    fig_uniq = px.bar(
        unique_df, x="עמודה", y="ערכים ייחודיים",
        title="מספר ערכים ייחודיים לפי עמודה",
        color="אחוז ייחודיות (%)",
        color_continuous_scale="Blues",
        text_auto=True,
        template="plotly_white",
    )
    fig_uniq.update_layout(title_font_size=14, coloraxis_showscale=True)
    fig_uniq.update_traces(textposition="outside")
    st.plotly_chart(fig_uniq, use_container_width=True)

    with st.expander("📋 טבלת ערכי הנפוצים ביותר לפי עמודה"):
        for col in fdf.columns:
            vc = fdf[col].replace("", pd.NA).dropna().value_counts().head(5)
            st.markdown(f"**{col}:**  " +
                        " · ".join([f"`{v}` ({c})" for v, c in vc.items()]))


# ─────────────────────────────────────────────────────────────────────────────
# TAB 3 – DISTRIBUTIONS
# ─────────────────────────────────────────────────────────────────────────────
with t3:
    st.markdown('<div class="sec">📈 היסטוגרם – התפלגות עמודה מספרית</div>',
                unsafe_allow_html=True)

    if not num_cols:
        st.info("אין עמודות מספריות בנתונים המסוננים.")
    else:
        d_left, d_right = st.columns([1, 3])
        with d_left:
            h_col  = st.selectbox("עמודה מספרית:", num_cols)
            n_bins = st.slider("מספר Bins", 5, 80, 25)
            col_s  = fdf[h_col].replace("", pd.NA).dropna()
            st.markdown(f"""
| מדד | ערך |
|-----|-----|
| ממוצע | {col_s.mean():.2f} |
| חציון | {col_s.median():.2f} |
| סטיית תקן | {col_s.std():.2f} |
| מינ | {col_s.min():.2f} |
| מקס | {col_s.max():.2f} |
| טווח | {col_s.max()-col_s.min():.2f} |
| Q1 | {col_s.quantile(.25):.2f} |
| Q3 | {col_s.quantile(.75):.2f} |
| IQR | {col_s.quantile(.75)-col_s.quantile(.25):.2f} |
""")
        with d_right:
            fig_h = px.histogram(
                fdf, x=h_col, nbins=n_bins,
                title=f"התפלגות: {h_col}",
                color_discrete_sequence=["#2d6a9f"],
                template="plotly_white", marginal="box",
            )
            fig_h.update_traces(marker_line_color="white", marker_line_width=0.6)
            fig_h.update_layout(bargap=0.04, title_font_size=14,
                                xaxis_title=h_col, yaxis_title="תדירות",
                                showlegend=False)
            st.plotly_chart(fig_h, use_container_width=True)

    st.divider()

    st.markdown('<div class="sec">📊 ספירת שכיחות – עמודה קטגורית</div>',
                unsafe_allow_html=True)

    if not cat_cols:
        st.info("אין עמודות קטגוריאליות.")
    else:
        vc1, vc2, vc3 = st.columns([1, 1, 1])
        with vc1:
            vc_col  = st.selectbox("עמודה קטגורית:", cat_cols, key="vc")
        with vc2:
            vc_topk = st.slider("Top K", 3, min(40, fdf[vc_col].nunique()), 15, key="vck")
        with vc3:
            orient  = st.radio("כיוון:", ["אופקי", "אנכי"], horizontal=True, key="vco")

        vc_df = (
            fdf[vc_col].replace("", pd.NA).dropna()
            .value_counts().head(vc_topk).reset_index()
        )
        vc_df.columns = [vc_col, "ספירה"]

        if orient == "אופקי":
            fig_vc = px.bar(vc_df, y=vc_col, x="ספירה", orientation="h",
                            title=f"שכיחות – {vc_col}",
                            color="ספירה", color_continuous_scale="Blues",
                            text_auto=True, template="plotly_white")
            fig_vc.update_layout(yaxis=dict(autorange="reversed"))
        else:
            fig_vc = px.bar(vc_df, x=vc_col, y="ספירה",
                            title=f"שכיחות – {vc_col}",
                            color="ספירה", color_continuous_scale="Blues",
                            text_auto=True, template="plotly_white")
            fig_vc.update_xaxes(tickangle=-40)

        fig_vc.update_traces(marker_line_color="white", marker_line_width=0.5)
        fig_vc.update_layout(title_font_size=14, coloraxis_showscale=False,
                             uniformtext_minsize=9, uniformtext_mode="hide")
        st.plotly_chart(fig_vc, use_container_width=True)
        st.caption(f"{fdf[vc_col].nunique()} ערכים ייחודיים · {len(fdf):,} רשומות")


# ─────────────────────────────────────────────────────────────────────────────
# TAB 4 – CATEGORICAL ANALYSIS
# ─────────────────────────────────────────────────────────────────────────────
with t4:
    if not cat_cols:
        st.info("אין עמודות קטגוריאליות.")
        st.stop()

    st.markdown('<div class="sec">🥧 גרף עוגה – התפלגות קטגוריה</div>',
                unsafe_allow_html=True)

    p1, p2, p3 = st.columns([1, 1, 1])
    with p1:
        pie_col  = st.selectbox("עמודה:", cat_cols, key="pie")
    with p2:
        pie_topk = st.slider("Top K", 3, min(18, fdf[pie_col].nunique()), 8, key="piek")
    with p3:
        pie_hole = st.slider("חור (דונאט)", 0.0, 0.65, 0.35, 0.05, key="pieh")

    pie_df = (
        fdf[pie_col].replace("", pd.NA).dropna()
        .value_counts().head(pie_topk).reset_index()
    )
    pie_df.columns = [pie_col, "ספירה"]
    fig_pie = px.pie(pie_df, names=pie_col, values="ספירה",
                     title=f"התפלגות: {pie_col} (Top {pie_topk})",
                     hole=pie_hole,
                     color_discrete_sequence=px.colors.sequential.Blues_r,
                     template="plotly_white")
    fig_pie.update_traces(textinfo="percent+label", textfont_size=12,
                           pull=[0.03]*len(pie_df))
    fig_pie.update_layout(title_font_size=14)
    st.plotly_chart(fig_pie, use_container_width=True)

    st.divider()

    st.markdown('<div class="sec">📊 השוואת כל העמודות הקטגוריות</div>',
                unsafe_allow_html=True)

    cols_grid = st.columns(min(len(cat_cols), 3))
    for i, col in enumerate(cat_cols):
        with cols_grid[i % 3]:
            vc = fdf[col].replace("", pd.NA).dropna().value_counts().head(8).reset_index()
            vc.columns = [col, "ספירה"]
            fig_mini = px.bar(
                vc, x=col, y="ספירה",
                title=col,
                color="ספירה", color_continuous_scale="Blues",
                template="plotly_white",
            )
            fig_mini.update_layout(
                title_font_size=13,
                showlegend=False, coloraxis_showscale=False,
                margin=dict(t=40, b=60, l=20, r=20),
                height=280,
            )
            fig_mini.update_xaxes(tickangle=-40, tickfont_size=9)
            fig_mini.update_yaxes(title_text="")
            fig_mini.update_traces(marker_line_color="white", marker_line_width=0.5)
            st.plotly_chart(fig_mini, use_container_width=True)


# ─────────────────────────────────────────────────────────────────────────────
# TAB 5 – CROSS ANALYSIS
# ─────────────────────────────────────────────────────────────────────────────
with t5:
    st.markdown('<div class="sec">📊 Bar Chart – ממוצע / ספירה לפי קטגוריה</div>',
                unsafe_allow_html=True)

    b1, b2, b3, b4 = st.columns(4)
    with b1:
        agg_mode = st.radio("סוג אגרגציה:", ["ממוצע", "ספירה", "סכום", "חציון"],
                            horizontal=True)
    with b2:
        if agg_mode != "ספירה":
            x_num = st.selectbox("עמודה מספרית:", num_cols if num_cols else cat_cols)
        else:
            x_num = None
    with b3:
        y_cat = st.selectbox("עמודה לקיבוץ:", cat_cols if cat_cols else fdf.columns.tolist())
    with b4:
        top_k = st.slider("Top K", 3, min(40, fdf[y_cat].nunique()), 15)

    agg_funcs = {"ממוצע": "mean", "ספירה": "count", "סכום": "sum", "חציון": "median"}

    if agg_mode == "ספירה":
        bar_df = (
            fdf[y_cat].replace("", pd.NA).dropna()
            .value_counts().head(top_k).reset_index()
        )
        bar_df.columns = [y_cat, "ספירה"]
        y_label = "ספירה"
        val_col = "ספירה"
    else:
        if not num_cols:
            st.warning("אין עמודות מספריות לאגרגציה.")
            st.stop()
        agg_label = f"{agg_mode} {x_num}"
        bar_df = (
            fdf[[x_num, y_cat]].replace("", pd.NA).dropna()
            .groupby(y_cat, as_index=False)[x_num]
            .agg(agg_funcs[agg_mode])
            .rename(columns={x_num: agg_label})
            .sort_values(agg_label, ascending=False)
            .head(top_k)
        )
        y_label = agg_label
        val_col = agg_label

    if bar_df.empty:
        st.warning("אין נתונים לגרף.")
    else:
        fig_b = px.bar(
            bar_df, x=y_cat, y=val_col,
            title=f"{y_label} לפי {y_cat}  (Top {top_k})",
            color=val_col, color_continuous_scale="Blues",
            text_auto=".2f" if agg_mode != "ספירה" else True,
            template="plotly_white",
        )
        fig_b.update_traces(textposition="outside",
                            marker_line_color="white", marker_line_width=0.5)
        fig_b.update_layout(
            title_font_size=14,
            xaxis_title=y_cat, yaxis_title=val_col,
            coloraxis_showscale=False,
            uniformtext_minsize=9, uniformtext_mode="hide",
        )
        fig_b.update_xaxes(tickangle=-40)
        st.plotly_chart(fig_b, use_container_width=True)
        st.caption(f"{len(bar_df)} קבוצות מוצגות · {len(fdf):,} רשומות בסיס")

    st.divider()

    with st.expander("🗃 טבלת נתונים מלאה (לאחר סינון)"):
        st.dataframe(fdf.reset_index(drop=True), use_container_width=True, height=420)

# ─────────────────────────────────────────────────────────────────────────────
# TAB 6 – AI PREDICTION
# ─────────────────────────────────────────────────────────────────────────────
with t6:
    model_data = load_model()

    if model_data is None:
        st.warning("המודל טרם אומן.", icon="⚠️")
        st.markdown("""
**כדי להפעיל את דף החיזוי:**

1. פתח **Terminal** ב-VS Code (`Ctrl+\``)
2. נווט לתיקיית הפרויקט
3. הרץ:
```bash
pip install scikit-learn joblib
python train_model.py
```
4. רענן את הדשבורד — הטאב יתעורר אוטומטית.
""")
    else:
        # ── inputs ────────────────────────────────────────────────────────────
        st.markdown('<div class="sec">🔮 הזן פרטי עבודה לחיזוי מיקום</div>',
                    unsafe_allow_html=True)

        inp1, inp2, inp3 = st.columns(3)
        with inp1:
            gush_val = st.number_input(
                "מספר גוש:", min_value=10000, max_value=25000,
                value=17000, step=100,
            )
        with inp2:
            year_val = st.radio("שנה:", [2025, 2026], horizontal=True)
        with inp3:
            parcels_val = st.slider("מספר חלקות בעבודה:", 1, 6, 1)

        # ── prediction ────────────────────────────────────────────────────────
        clf      = model_data["clf"]
        classes  = model_data["classes"]
        X_inp    = [[gush_val, year_val, parcels_val]]
        pred     = clf.predict(X_inp)[0]
        proba    = clf.predict_proba(X_inp)[0]
        conf     = float(max(proba))

        res_col, chart_col = st.columns([1, 2])

        with res_col:
            conf_color = "#1e8449" if conf >= 0.6 else "#e67e22" if conf >= 0.35 else "#c0392b"
            st.markdown(f"""
<div style="background:linear-gradient(135deg,#0d1f38,#1a4a7a);
     border-radius:18px; padding:36px 24px; text-align:center; color:#fff; margin-top:8px;">
  <div style="font-size:.78rem; letter-spacing:1.5px; opacity:.65; margin-bottom:8px;">
    מיקום חזוי
  </div>
  <div style="font-size:2.6rem; font-weight:800; line-height:1.1; margin-bottom:12px;">
    {pred}
  </div>
  <div style="background:rgba(255,255,255,.12); border-radius:30px;
       display:inline-block; padding:4px 18px; font-size:.88rem;">
    ביטחון: <strong style="color:{conf_color};">{conf*100:.1f}%</strong>
  </div>
</div>
""", unsafe_allow_html=True)

        with chart_col:
            top_idx  = proba.argsort()[-10:][::-1]
            prob_df  = pd.DataFrame({
                "עיר":         [classes[i] for i in top_idx],
                "הסתברות (%)": [round(proba[i] * 100, 1) for i in top_idx],
            })
            fig_prob = px.bar(
                prob_df, y="עיר", x="הסתברות (%)",
                orientation="h",
                title="הסתברות לכל עיר (Top 10)",
                color="הסתברות (%)",
                color_continuous_scale="Blues",
                text_auto=".1f",
                template="plotly_white",
            )
            fig_prob.update_layout(
                yaxis=dict(autorange="reversed"),
                coloraxis_showscale=False,
                title_font_size=14,
                margin=dict(t=40),
            )
            fig_prob.update_traces(marker_line_color="white", marker_line_width=0.5)
            st.plotly_chart(fig_prob, use_container_width=True)

        st.divider()

        # ── model metrics ─────────────────────────────────────────────────────
        st.markdown('<div class="sec">📊 מדדי המודל</div>', unsafe_allow_html=True)

        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.metric("דיוק – Test set",
                      f"{model_data['accuracy']*100:.1f}%")
        with m2:
            st.metric("דיוק – CV (5-fold)",
                      f"{model_data['cv_mean']*100:.1f}%",
                      delta=f"±{model_data['cv_std']*100:.1f}%")
        with m3:
            st.metric("Train samples", model_data["train_size"])
        with m4:
            st.metric("Test samples", model_data["test_size"])

        # ── feature importance ────────────────────────────────────────────────
        imp_df = pd.DataFrame({
            "פיצ'ר":  list(model_data["importances"].keys()),
            "חשיבות": list(model_data["importances"].values()),
        }).sort_values("חשיבות")

        fi1, fi2 = st.columns([1, 1])
        with fi1:
            fig_imp = px.bar(
                imp_df, x="חשיבות", y="פיצ'ר",
                orientation="h",
                title="חשיבות פיצ'רים (Feature Importance)",
                color="חשיבות",
                color_continuous_scale="Blues",
                text_auto=".3f",
                template="plotly_white",
            )
            fig_imp.update_layout(coloraxis_showscale=False, title_font_size=14)
            st.plotly_chart(fig_imp, use_container_width=True)

        with fi2:
            dist_df = pd.DataFrame(
                model_data["class_dist"].items(),
                columns=["עיר", "ספירה"],
            ).sort_values("ספירה", ascending=False).head(15)
            fig_dist = px.bar(
                dist_df, x="עיר", y="ספירה",
                title="התפלגות קלאסים בנתוני האימון",
                color="ספירה",
                color_continuous_scale="Blues",
                text_auto=True,
                template="plotly_white",
            )
            fig_dist.update_layout(coloraxis_showscale=False, title_font_size=14)
            fig_dist.update_xaxes(tickangle=-40)
            fig_dist.update_traces(marker_line_color="white", marker_line_width=0.5)
            st.plotly_chart(fig_dist, use_container_width=True)

        with st.expander("ℹ️ מהו המודל?"):
            st.markdown("""
**Random Forest Classifier** – יער של 200 עצי החלטה.

| פיצ'ר | תיאור |
|--------|--------|
| גוש (ראשי) | מספר הגוש הקדסטרלי הראשון – פרדיקטור גיאוגרפי חזק |
| שנה | 2025 / 2026 – מזהה טרנד זמן |
| מספר חלקות | כמות החלקות בעבודה – מחיר מורכבות |

**Target:** עיר / יישוב (Top 15 + "אחר")
""")


# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown("""
<hr style="border-color:#e8edf4; margin:24px 0 16px">
<div style="text-align:center; color:#aaa; font-size:.8rem;">
    📐 EDA Dashboard · משרד מודדים 2025 · Streamlit + Plotly + Pandas
</div>
""", unsafe_allow_html=True)
