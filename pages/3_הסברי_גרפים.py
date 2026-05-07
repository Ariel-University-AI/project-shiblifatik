import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from pathlib import Path

st.set_page_config(
    page_title="הסברי גרפים – משרד מודדים",
    page_icon="📖",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ══════════════════════════════════════════════════════════════════════════════
# CSS
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Heebo:wght@300;400;600;800&display=swap');
html, body, [class*="css"] { font-family:'Heebo',sans-serif; direction:rtl; }

.hero-exp {
    background: linear-gradient(135deg,#0d1f38 0%,#1a4a7a 60%,#0d3b6e 100%);
    border-radius:18px; padding:44px 40px; text-align:center;
    color:#fff; margin-bottom:10px;
}
.hero-exp-title { font-size:2.4rem; font-weight:800; margin:0 0 10px; }
.hero-exp-sub   { font-size:1rem; opacity:.75; max-width:540px; margin:0 auto; line-height:1.65; }

.exp-card {
    background:#fff; border:1px solid #dde5ef; border-radius:16px;
    padding:26px 24px; box-shadow:0 2px 14px rgba(0,0,0,.07);
    margin-bottom:6px; height:100%;
}
.exp-card h3 { color:#1e3a5f; margin:0 0 10px; font-size:1.05rem; }
.exp-card p, .exp-card li { color:#444; font-size:.92rem; line-height:1.75; }
.exp-card ul { padding-right:18px; margin:8px 0 0; }

.tag {
    display:inline-block; border-radius:20px; padding:3px 13px;
    font-size:.74rem; font-weight:700; letter-spacing:.5px;
    margin-bottom:12px;
}
.tag-blue   { background:#e3eef9; color:#1e5a99; }
.tag-green  { background:#e3f4eb; color:#1a7a3f; }
.tag-orange { background:#fef0e3; color:#c05e10; }
.tag-purple { background:#ede3f9; color:#5a1eb5; }
.tag-red    { background:#fde9e9; color:#b51e1e; }

.insight-box {
    background:#f0f5fc; border-right:4px solid #2d6a9f;
    border-radius:8px; padding:14px 16px; margin-top:14px;
    font-size:.88rem; color:#1e3a5f; line-height:1.7;
}
.insight-box strong { font-size:.82rem; letter-spacing:1px;
    text-transform:uppercase; opacity:.7; display:block; margin-bottom:4px; }

.step {
    display:flex; align-items:flex-start; gap:12px;
    background:#f7fafd; border-radius:10px;
    padding:12px 14px; margin-bottom:8px;
}
.step-num {
    background:#2d6a9f; color:#fff; border-radius:50%;
    width:28px; height:28px; min-width:28px;
    display:flex; align-items:center; justify-content:center;
    font-weight:700; font-size:.85rem;
}
.step-text { font-size:.9rem; color:#333; line-height:1.6; }

.sec-hdr {
    text-align:center; font-size:1.3rem; font-weight:700; color:#1e3a5f;
    margin:32px 0 18px;
    display:flex; align-items:center; gap:10px; justify-content:center;
}
.sec-hdr::before, .sec-hdr::after { content:""; flex:1; height:1px; background:#dde5ef; }
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# DATA (for demo charts)
# ══════════════════════════════════════════════════════════════════════════════
DEFAULT_CSV = Path(__file__).parent.parent / "2025_cleaned.csv"

@st.cache_data
def load_data() -> pd.DataFrame | None:
    if DEFAULT_CSV.exists():
        return pd.read_csv(DEFAULT_CSV, encoding="utf-8-sig")
    return None

df = load_data()


# ══════════════════════════════════════════════════════════════════════════════
# HERO
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="hero-exp">
    <div class="hero-exp-title">📖 הסברי גרפים ומדדים</div>
    <div class="hero-exp-sub">
        כל ויזואליזציה בדף EDA – מה היא מציגה, כיצד לקרוא אותה,<br>
        ומה ניתן להסיק ממנה בהקשר נתוני משרד המודדים
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# TABS
# ══════════════════════════════════════════════════════════════════════════════
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 KPI – מדדי מפתח",
    "📈 היסטוגרם",
    "📊 Bar Chart – ממוצע",
    "🔢 ספירת שכיחות",
    "🥧 גרף עוגה",
])


# ─────────────────────────────────────────────────────────────────────────────
# TAB 1 – KPI CARDS
# ─────────────────────────────────────────────────────────────────────────────
with tab1:
    st.markdown('<div class="sec-hdr">📊 KPI – כרטיסי מדדי מפתח</div>', unsafe_allow_html=True)

    L, R = st.columns([1, 1])

    with L:
        st.markdown("""
<div class="exp-card">
    <span class="tag tag-blue">סוג: מדד סיכום</span>
    <h3>מה זה KPI Card?</h3>
    <p>
        כרטיסיית KPI (Key Performance Indicator) מציגה מספר יחיד שמסכם
        מימד קריטי של הנתונים. שלושת הכרטיסיות בדשבורד מציגות:
    </p>
    <ul>
        <li><strong>🗂 שורות</strong> – מספר הרשומות הכולל (לאחר סינון)</li>
        <li><strong>📋 עמודות</strong> – כמות השדות בקובץ</li>
        <li><strong>⚠️ ערכים חסרים</strong> – אחוז תאים ריקים מהסה"כ</li>
    </ul>
</div>
""", unsafe_allow_html=True)

    with R:
        st.markdown("""
<div class="exp-card">
    <span class="tag tag-green">כיצד לקרוא</span>
    <h3>צבעי הכרטיסיה – מה הם מסמנים?</h3>
    <div class="step">
        <div class="step-num">🔵</div>
        <div class="step-text"><strong>כחול</strong> – מדד רגיל, אינפורמטיבי בלבד (שורות, עמודות)</div>
    </div>
    <div class="step">
        <div class="step-num">🟢</div>
        <div class="step-text"><strong>ירוק</strong> – ערכים חסרים <strong>מתחת ל-10%</strong> → הנתונים אמינים</div>
    </div>
    <div class="step">
        <div class="step-num">🔴</div>
        <div class="step-text"><strong>אדום</strong> – ערכים חסרים <strong>מעל 10%</strong> → יש לטפל לפני ניתוח</div>
    </div>
    <div class="insight-box">
        <strong>💡 תובנה – נתוני המשרד</strong>
        נתוני 2025 לאחר ניקוי: 310 שורות, 5 עמודות, 0% חסרים → כרטיסיה ירוקה.
        פירושו שניתן לסמוך על ניתוחי ה-EDA ללא עיוות.
    </div>
</div>
""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("""
<div class="exp-card">
    <span class="tag tag-orange">מה לבדוק ראשון</span>
    <h3>סדר קריאה מומלץ</h3>
    <div class="step">
        <div class="step-num">1</div>
        <div class="step-text">בדוק <strong>שורות</strong> – האם הסינון הצמצם יותר מדי? (מתחת ל-20% מהמקור = אזהרה)</div>
    </div>
    <div class="step">
        <div class="step-num">2</div>
        <div class="step-text">בדוק <strong>עמודות</strong> – האם הקובץ הנכון נטען? (מספר שדות תואם לציפייה)</div>
    </div>
    <div class="step">
        <div class="step-num">3</div>
        <div class="step-text">בדוק <strong>ערכים חסרים</strong> – אם אדום, כדאי לבצע ניקוי לפני שמסיקים מסקנות מהגרפים</div>
    </div>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# TAB 2 – HISTOGRAM
# ─────────────────────────────────────────────────────────────────────────────
with tab2:
    st.markdown('<div class="sec-hdr">📈 היסטוגרם – התפלגות עמודה מספרית</div>', unsafe_allow_html=True)

    h_L, h_R = st.columns([1, 1])

    with h_L:
        st.markdown("""
<div class="exp-card">
    <span class="tag tag-blue">סוג: גרף התפלגות</span>
    <h3>מה זה היסטוגרם?</h3>
    <p>
        היסטוגרם מחלק את ערכי העמודה המספרית לתחומים (bins) ומציג כמה
        רשומות נופלות בכל תחום. ציר X = ערכים; ציר Y = כמות רשומות.
    </p>
    <p>
        <strong>Marginal box</strong> (מעל הגרף) מציג:
    </p>
    <ul>
        <li>קו אנכי = חציון</li>
        <li>הקופסה = IQR (25%–75%)</li>
        <li>נקודות חיצוניות = outliers (ערכי קיצון)</li>
    </ul>
    <div class="insight-box">
        <strong>💡 תובנה – נתוני המשרד</strong>
        עמודות גוש וחלקה הן מספריות. היסטוגרמה על גוש תגלה אם
        רוב העבודות מרוכזות בגושים ספציפיים (שכיחות גבוהה = גוש עמוס).
    </div>
</div>
""", unsafe_allow_html=True)

    with h_R:
        st.markdown("""
<div class="exp-card">
    <span class="tag tag-green">כיצד לקרוא</span>
    <h3>פענוח צורת ההתפלגות</h3>
    <div class="step">
        <div class="step-num">🔔</div>
        <div class="step-text"><strong>פעמון סימטרי (Normal)</strong> – ממוצע ≈ חציון. נפוץ בנתונים "טבעיים"</div>
    </div>
    <div class="step">
        <div class="step-num">→</div>
        <div class="step-text"><strong>זנב ימני (Right-skewed)</strong> – כמה ערכים גבוהים מאוד מושכים את הממוצע. חלקה 1–10 נפוצה, אבל יש גם 100+</div>
    </div>
    <div class="step">
        <div class="step-num">←</div>
        <div class="step-text"><strong>זנב שמאלי (Left-skewed)</strong> – ערכים נמוכים נדירים. פחות נפוץ בנתוני מדידה</div>
    </div>
    <div class="step">
        <div class="step-num">⛰</div>
        <div class="step-text"><strong>דו-שיאית (Bimodal)</strong> – שתי קבוצות שונות בנתונים. למשל: גושים בצפון מול גושים במרכז</div>
    </div>
</div>
""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Demo chart
    if df is not None:
        num_cols = df.select_dtypes(include="number").columns.tolist()
        if num_cols:
            demo_col = num_cols[0]
            fig_demo = px.histogram(
                df, x=demo_col, nbins=25,
                title=f"דוגמה: היסטוגרמה – {demo_col}",
                color_discrete_sequence=["#2d6a9f"],
                template="plotly_white",
                marginal="box",
            )
            fig_demo.update_traces(marker_line_color="white", marker_line_width=0.6)
            fig_demo.update_layout(
                bargap=0.04, title_font_size=14,
                xaxis_title=demo_col, yaxis_title="תדירות",
                showlegend=False,
            )
            st.plotly_chart(fig_demo, use_container_width=True)
            st.caption(f"דוגמה מנתוני 2025 האמיתיים – עמודה: {demo_col}")

    st.markdown("""
<div class="exp-card">
    <span class="tag tag-orange">פרמטרים אינטראקטיביים</span>
    <h3>מה עושה כל פרמטר?</h3>
    <ul>
        <li><strong>עמודה מספרית</strong> – בחר איזה שדה לנתח (גוש / חלקה)</li>
        <li><strong>מספר Bins</strong> – פחות bins = תמונה כוללת; יותר bins = דיוק גבוה יותר. המלצה: להתחיל עם 20</li>
        <li><strong>טבלת מדדים</strong> (שמאל) – ממוצע, חציון, סטיית תקן, מינ/מקס. השוואה בין ממוצע לחציון מגלה skewness</li>
    </ul>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# TAB 3 – BAR CHART (MEAN)
# ─────────────────────────────────────────────────────────────────────────────
with tab3:
    st.markdown('<div class="sec-hdr">📊 Bar Chart – ממוצע [X] לפי [Y]</div>', unsafe_allow_html=True)

    b_L, b_R = st.columns([1, 1])

    with b_L:
        st.markdown("""
<div class="exp-card">
    <span class="tag tag-blue">סוג: גרף השוואה</span>
    <h3>מה זה Bar Chart ממוצע?</h3>
    <p>
        גרף זה מקבץ את הנתונים לפי קטגוריה (למשל: מקום) ומחשב את
        <strong>הממוצע</strong> של עמודה מספרית בכל קבוצה.
        הגובה של כל עמוד = ממוצע הערך המספרי בקבוצה זו.
    </p>
    <p>ציר X = קטגוריות; ציר Y = ממוצע.</p>
    <div class="insight-box">
        <strong>💡 תובנה – נתוני המשרד</strong>
        ממוצע גוש לפי מקום → מגלה אם יישובים מסוימים קשורים למספרי גוש גבוהים/נמוכים.
        ממוצע חלקה לפי שם לקוח → לקוחות עם ממוצע חלקה גבוה = עבודות על חלקות מספר 100+.
    </div>
</div>
""", unsafe_allow_html=True)

    with b_R:
        st.markdown("""
<div class="exp-card">
    <span class="tag tag-green">כיצד לקרוא</span>
    <h3>קריאת גרף הממוצע</h3>
    <div class="step">
        <div class="step-num">1</div>
        <div class="step-text">העמוד <strong>הגבוה ביותר</strong> = הקטגוריה עם ממוצע X הגדול ביותר</div>
    </div>
    <div class="step">
        <div class="step-num">2</div>
        <div class="step-text"><strong>צבע העמוד</strong> – כהה יותר = ערך גבוה יותר (סקאלת Blues)</div>
    </div>
    <div class="step">
        <div class="step-num">3</div>
        <div class="step-text"><strong>הסתכל על פערים</strong> – אם עמוד אחד גבוה פי 3 מהשאר, יש שונות גבוהה בין הקטגוריות</div>
    </div>
    <div class="step">
        <div class="step-num">⚠️</div>
        <div class="step-text"><strong>מגבלה חשובה:</strong> ממוצע מושפע מ-outliers. קטגוריה עם 2 רשומות קיצוניות תיראה שונה מאשר קטגוריה עם 50 רשומות</div>
    </div>
</div>
""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    if df is not None:
        num_cols = df.select_dtypes(include="number").columns.tolist()
        cat_cols = df.select_dtypes(include="object").columns.tolist()
        if num_cols and cat_cols:
            x_c, y_c = num_cols[0], cat_cols[-1]  # מקום
            bar_demo = (
                df[[x_c, y_c]].replace("", pd.NA).dropna()
                .groupby(y_c, as_index=False)[x_c].mean()
                .rename(columns={x_c: f"ממוצע {x_c}"})
                .sort_values(f"ממוצע {x_c}", ascending=False)
                .head(12)
            )
            fig_bar = px.bar(
                bar_demo, x=y_c, y=f"ממוצע {x_c}",
                title=f"דוגמה: ממוצע {x_c} לפי {y_c}",
                color=f"ממוצע {x_c}", color_continuous_scale="Blues",
                text_auto=".1f", template="plotly_white",
            )
            fig_bar.update_traces(textposition="outside",
                                  marker_line_color="white", marker_line_width=0.5)
            fig_bar.update_layout(
                title_font_size=14, coloraxis_showscale=False,
                uniformtext_minsize=9, uniformtext_mode="hide",
            )
            fig_bar.update_xaxes(tickangle=-35)
            st.plotly_chart(fig_bar, use_container_width=True)
            st.caption(f"דוגמה מנתוני 2025 – ממוצע {x_c} לפי {y_c}")


# ─────────────────────────────────────────────────────────────────────────────
# TAB 4 – VALUE COUNTS
# ─────────────────────────────────────────────────────────────────────────────
with tab4:
    st.markdown('<div class="sec-hdr">🔢 ספירת שכיחות – Value Counts</div>', unsafe_allow_html=True)

    v_L, v_R = st.columns([1, 1])

    with v_L:
        st.markdown("""
<div class="exp-card">
    <span class="tag tag-purple">סוג: גרף תדירות</span>
    <h3>מה זה ספירת שכיחות?</h3>
    <p>
        הגרף סופר כמה פעמים <strong>כל ערך</strong> מופיע בעמודה קטגורית.
        שלאחר מכן מציג את ה-Top K הנפוצים ביותר.
    </p>
    <p>
        ההבדל מ-Bar Chart ממוצע: כאן ציר Y = <strong>ספירה (Count)</strong>,
        לא ממוצע של עמודה אחרת.
    </p>
    <div class="insight-box">
        <strong>💡 תובנה – נתוני המשרד</strong>
        ספירת שכיחות על <em>מקום</em> תגלה: אילו יישובים מקבלים הכי הרבה עבודות מדידה.
        ספירה על <em>שם לקוח</em> תגלה: מי הלקוחות החוזרים (לקוחות נאמנים) של המשרד.
    </div>
</div>
""", unsafe_allow_html=True)

    with v_R:
        st.markdown("""
<div class="exp-card">
    <span class="tag tag-green">כיצד לקרוא</span>
    <h3>קריאת גרף השכיחות</h3>
    <div class="step">
        <div class="step-num">1</div>
        <div class="step-text">ה<strong>עמוד הראשון</strong> (הגבוה ביותר) = הקטגוריה הנפוצה ביותר = "הפייבוריט"</div>
    </div>
    <div class="step">
        <div class="step-num">2</div>
        <div class="step-text"><strong>ירידה חדה</strong> בין העמוד הראשון לשני = פרטו (20/80): קבוצה אחת שולטת</div>
        </div>
    <div class="step">
        <div class="step-num">3</div>
        <div class="step-text"><strong>ירידה הדרגתית</strong> = פיזור שווה יחסית בין הקטגוריות</div>
    </div>
    <div class="step">
        <div class="step-num">↔</div>
        <div class="step-text">כיוון <strong>אופקי</strong> עדיף כשיש שמות ארוכים (שם לקוח / יישוב)</div>
    </div>
</div>
""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    if df is not None:
        cat_cols = df.select_dtypes(include="object").columns.tolist()
        if cat_cols:
            vc_demo_col = cat_cols[-1]
            vc_demo = (
                df[vc_demo_col].replace("", pd.NA).dropna()
                .value_counts().head(12).reset_index()
            )
            vc_demo.columns = [vc_demo_col, "ספירה"]
            fig_vc = px.bar(
                vc_demo, y=vc_demo_col, x="ספירה",
                orientation="h",
                title=f"דוגמה: שכיחות – {vc_demo_col}",
                color="ספירה", color_continuous_scale="Blues",
                text_auto=True, template="plotly_white",
            )
            fig_vc.update_layout(yaxis=dict(autorange="reversed"),
                                 title_font_size=14, coloraxis_showscale=False)
            fig_vc.update_traces(marker_line_color="white", marker_line_width=0.5)
            st.plotly_chart(fig_vc, use_container_width=True)
            st.caption(f"דוגמה מנתוני 2025 – שכיחות ערכים בעמודת {vc_demo_col}")


# ─────────────────────────────────────────────────────────────────────────────
# TAB 5 – PIE CHART
# ─────────────────────────────────────────────────────────────────────────────
with tab5:
    st.markdown('<div class="sec-hdr">🥧 גרף עוגה – Pie / Donut Chart</div>', unsafe_allow_html=True)

    p_L, p_R = st.columns([1, 1])

    with p_L:
        st.markdown("""
<div class="exp-card">
    <span class="tag tag-red">סוג: גרף יחסים</span>
    <h3>מה זה גרף עוגה?</h3>
    <p>
        גרף עוגה מציג את <strong>החלק היחסי</strong> של כל קטגוריה מתוך הסה"כ.
        כל פרוסה = קטגוריה אחת. גודל הפרוסה ∝ שיעורה מהסה"כ.
    </p>
    <p>
        <strong>דונאט (Donut)</strong> = גרף עוגה עם חור באמצע.
        ויזואלית נחשב נוח יותר לקריאה של אחוזים.
    </p>
    <div class="insight-box">
        <strong>💡 תובנה – נתוני המשרד</strong>
        עוגה על <em>מקום</em>: כמה אחוז מעבודות המשרד מגיעות מכל יישוב?
        אם יישוב אחד ≥ 30% = תלות גבוהה. גיוון ≥ 10 יישובים = בסיס לקוחות מפוזר.
    </div>
</div>
""", unsafe_allow_html=True)

    with p_R:
        st.markdown("""
<div class="exp-card">
    <span class="tag tag-green">כיצד לקרוא</span>
    <h3>קריאת גרף העוגה</h3>
    <div class="step">
        <div class="step-num">%</div>
        <div class="step-text">כל פרוסה מציגה <strong>שם + אחוז</strong>. סכום כל האחוזים = 100%</div>
    </div>
    <div class="step">
        <div class="step-num">🎨</div>
        <div class="step-text"><strong>צבע</strong> – כהה יותר = קטגוריה גדולה יותר (סקאלת Blues_r)</div>
    </div>
    <div class="step">
        <div class="step-num">⚠️</div>
        <div class="step-text"><strong>מגבלה:</strong> מעל 8–10 קטגוריות קשה לקרוא. השתמש ב-Top K להגבלה</div>
    </div>
    <div class="step">
        <div class="step-num">vs</div>
        <div class="step-text"><strong>עוגה vs ספירת שכיחות:</strong> עוגה מדגישה יחסים (30% מול 20%); ספירה מדגישה מספרים מוחלטים (60 רשומות מול 40)</div>
    </div>
</div>
""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    if df is not None:
        cat_cols = df.select_dtypes(include="object").columns.tolist()
        if cat_cols:
            pie_demo_col = cat_cols[-1]
            pie_demo = (
                df[pie_demo_col].replace("", pd.NA).dropna()
                .value_counts().head(10).reset_index()
            )
            pie_demo.columns = [pie_demo_col, "ספירה"]
            fig_pie = px.pie(
                pie_demo, names=pie_demo_col, values="ספירה",
                title=f"דוגמה: התפלגות {pie_demo_col}",
                hole=0.35,
                color_discrete_sequence=px.colors.sequential.Blues_r,
                template="plotly_white",
            )
            fig_pie.update_traces(
                textinfo="percent+label", textfont_size=12,
                pull=[0.03] * len(pie_demo),
            )
            fig_pie.update_layout(title_font_size=14, showlegend=True)
            st.plotly_chart(fig_pie, use_container_width=True)
            st.caption(f"דוגמה מנתוני 2025 – התפלגות {pie_demo_col}")


# ══════════════════════════════════════════════════════════════════════════════
# SUMMARY TABLE
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("<br>", unsafe_allow_html=True)
st.markdown('<div class="sec-hdr">📋 טבלת השוואה – מתי להשתמש בכל גרף?</div>', unsafe_allow_html=True)

summary_df = pd.DataFrame({
    "גרף": ["KPI Cards", "היסטוגרם", "Bar Chart ממוצע", "ספירת שכיחות", "גרף עוגה"],
    "שאלה שהוא עונה עליה": [
        "מה גודל הנתונים? כמה חסרים?",
        "מה ההתפלגות של עמודה מספרית?",
        "מה הממוצע של X לפי כל קטגוריה?",
        "כמה רשומות יש לכל קטגוריה?",
        "מה החלק היחסי של כל קטגוריה?",
    ],
    "סוג נתון נדרש": [
        "כל סוג",
        "עמודה מספרית",
        "מספרי + קטגורי",
        "עמודה קטגורית",
        "עמודה קטגורית",
    ],
    "מגבלה עיקרית": [
        "לא מציג פרטים",
        "מושפע מ-bins",
        "ממוצע ≠ מדיאנה",
        "לא מציג יחסים",
        "קשה מעל 10 קטגוריות",
    ],
})

st.dataframe(summary_df, use_container_width=True, hide_index=True)

# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("""
<hr style="border-color:#e8edf4; margin:8px 0 20px">
<div style="text-align:center; color:#999; font-size:.8rem;">
    סמסטר 22 · AI · הסברי גרפים &nbsp;|&nbsp; משרד מודדים 2025
</div>
""", unsafe_allow_html=True)
