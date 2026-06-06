import streamlit as st

st.set_page_config(
    page_title="אודות – שיבלי-משרדית",
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

/* ── Hero ── */
.hero {
    background: linear-gradient(135deg, #0d1f38 0%, #1a4a7a 60%, #0d3b6e 100%);
    border-radius: 20px;
    padding: 56px 48px;
    text-align: center;
    color: #fff;
    position: relative;
    overflow: hidden;
    margin-bottom: 8px;
}
.hero::before {
    content:"";
    position:absolute; inset:0;
    background: radial-gradient(circle at 20% 50%, rgba(45,106,159,.35) 0%, transparent 60%),
                radial-gradient(circle at 80% 30%, rgba(29,185,84,.12) 0%, transparent 50%);
}
.hero-badge {
    display:inline-block;
    background:rgba(255,255,255,.12);
    border:1px solid rgba(255,255,255,.2);
    border-radius:20px; padding:5px 18px;
    font-size:.78rem; letter-spacing:2px; text-transform:uppercase;
    margin-bottom:18px; position:relative;
}
.hero-title  { font-size:2.8rem; font-weight:800; line-height:1.15;
               position:relative; margin:0 0 12px; }
.hero-sub    { font-size:1.05rem; opacity:.75; position:relative;
               max-width:560px; margin:0 auto; line-height:1.6; }

/* ── Section card ── */
.card {
    background:#fff;
    border:1px solid #e8edf4;
    border-radius:16px;
    padding:32px 28px;
    height:100%;
    box-shadow:0 2px 12px rgba(0,0,0,.06);
    transition: box-shadow .2s;
}
.card:hover { box-shadow:0 6px 24px rgba(0,0,0,.11); }
.card-icon  { font-size:2.2rem; margin-bottom:10px; }
.card-title { font-size:1.1rem; font-weight:700; color:#1e3a5f;
              margin-bottom:12px; border-bottom:2px solid #e8edf4;
              padding-bottom:10px; }
.card-body  { font-size:.93rem; color:#444; line-height:1.75; }

/* ── Architecture flow ── */
.arch-wrap {
    display:flex; align-items:center; justify-content:center;
    flex-wrap:wrap; gap:0; margin:12px 0;
}
.arch-node {
    background: linear-gradient(135deg,#1e3a5f,#2d6a9f);
    color:#fff; border-radius:12px;
    padding:14px 20px; min-width:130px;
    text-align:center; position:relative;
}
.arch-node .n-icon { font-size:1.6rem; display:block; margin-bottom:4px; }
.arch-node .n-lbl  { font-size:.82rem; font-weight:600; line-height:1.3; }
.arch-node .n-sub  { font-size:.7rem; opacity:.7; margin-top:3px; }

.arch-node.green { background:linear-gradient(135deg,#0d3320,#1e8449); }
.arch-node.teal  { background:linear-gradient(135deg,#0d3333,#148a72); }
.arch-node.purple{ background:linear-gradient(135deg,#2d1b5e,#6c3fc1); }

.arch-arrow {
    font-size:1.5rem; color:#2d6a9f; padding:0 6px;
    flex-shrink:0; align-self:center;
}

/* ── Tech badges ── */
.badges { display:flex; flex-wrap:wrap; gap:10px; margin-top:14px; }
.badge {
    display:flex; align-items:center; gap:7px;
    background:#f0f5fc; border:1px solid #cfe0f7;
    border-radius:8px; padding:6px 14px;
    font-size:.82rem; font-weight:600; color:#1e3a5f;
}

/* ── Divider with title ── */
.sec-hdr {
    text-align:center; font-size:1.35rem; font-weight:700;
    color:#1e3a5f; margin:36px 0 18px;
    display:flex; align-items:center; gap:10px; justify-content:center;
}
.sec-hdr::before, .sec-hdr::after {
    content:""; flex:1; height:1px; background:#dde5ef;
}
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# HERO
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="hero">
    <div class="hero-badge">📐 סמסטר 22 · AI</div>
    <div class="hero-title">מערכת ניתוח נתונים<br>שיבלי-משרדית</div>
    <div class="hero-sub">
        פלטפורמת EDA אינטראקטיבית לניתוח עבודות מדידה,<br>
        ניקוי נתונים אוטומטי וויזואליזציה מתקדמת
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# 3 CARDS — בעיה · נתונים · יעדים
# ══════════════════════════════════════════════════════════════════════════════
c1, c2, c3 = st.columns(3)

with c1:
    st.markdown("""
    <div class="card">
        <div class="card-icon">🔍</div>
        <div class="card-title">הבעיה</div>
        <div class="card-body">
            שיבלי-משרדית מנהל מאות עבודות מדידה בשנה פרוסות על פני
            יישובים, גושים וחלקות ברחבי הצפון.
            <br><br>
            <b>אתגרים מרכזיים:</b>
            <ul>
                <li>נתונים מבוזרים בקבצי Excel/CSV ידניים</li>
                <li>ערכים חסרים ושכפולים שמקשים על ניתוח</li>
                <li>אין תמונת מצב מיידית על פעילות המשרד</li>
                <li>קשה לזהות מגמות ועומסים לפי אזורים</li>
            </ul>
        </div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown("""
    <div class="card">
        <div class="card-icon">📂</div>
        <div class="card-title">מקור הנתונים</div>
        <div class="card-body">
            <b>קובץ גולמי:</b> <code>2025.csv</code><br>
            רשימת עבודות שנת 2025 של שיבלי-משרדית
            <br><br>
            <b>שדות עיקריים:</b>
            <ul>
                <li>🔑 מס' עבודה (מזהה ייחודי)</li>
                <li>👤 שם לקוח</li>
                <li>🗺️ גוש + חלקה (מיקום קדסטרלי)</li>
                <li>📍 מקום (יישוב)</li>
            </ul>
            <b>לאחר ניקוי:</b> <code>2025_cleaned.csv</code><br>
            310 רשומות · 5 עמודות · 0% חסרים
        </div>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown("""
    <div class="card">
        <div class="card-icon">🎯</div>
        <div class="card-title">יעדי המערכת</div>
        <div class="card-body">
            <ul>
                <li>✅ ניקוי אוטומטי – טיפול בחסרים ושכפולים</li>
                <li>✅ מדדי EDA מיידיים (שורות, עמודות, חסרים)</li>
                <li>✅ סינון גלובלי שמשפיע על כל הגרפים</li>
                <li>✅ היסטוגרם לכל עמודה מספרית</li>
                <li>✅ Bar Chart ממוצעים לפי קטגוריה</li>
                <li>✅ תמיכה בהעלאת CSV חיצוני</li>
            </ul>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# ARCHITECTURE
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="sec-hdr">🏗️ ארכיטקטורה</div>', unsafe_allow_html=True)

st.markdown("""
<div class="arch-wrap">

  <div class="arch-node">
    <span class="n-icon">📄</span>
    <div class="n-lbl">קובץ גולמי</div>
    <div class="n-sub">2025.csv / Upload</div>
  </div>

  <div class="arch-arrow">→</div>

  <div class="arch-node teal">
    <span class="n-icon">🧹</span>
    <div class="n-lbl">שלב ניקוי</div>
    <div class="n-sub">Pandas · clean_data.py</div>
  </div>

  <div class="arch-arrow">→</div>

  <div class="arch-node green">
    <span class="n-icon">🗃️</span>
    <div class="n-lbl">נתונים נקיים</div>
    <div class="n-sub">2025_cleaned.csv</div>
  </div>

  <div class="arch-arrow">→</div>

  <div class="arch-node purple">
    <span class="n-icon">⚙️</span>
    <div class="n-lbl">מנוע EDA</div>
    <div class="n-sub">Pandas · NumPy</div>
  </div>

  <div class="arch-arrow">→</div>

  <div class="arch-node" style="background:linear-gradient(135deg,#4a2000,#c0621b)">
    <span class="n-icon">📊</span>
    <div class="n-lbl">ויזואליזציה</div>
    <div class="n-sub">Plotly Express</div>
  </div>

  <div class="arch-arrow">→</div>

  <div class="arch-node" style="background:linear-gradient(135deg,#1a0d38,#6930c3)">
    <span class="n-icon">🖥️</span>
    <div class="n-lbl">ממשק משתמש</div>
    <div class="n-sub">Streamlit Dashboard</div>
  </div>

</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── שלבי ניקוי ────────────────────────────────────────────────────────────────
with st.expander("📋 פירוט שלבי ניקוי הנתונים", expanded=False):
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("""
**שלב 1 – זיהוי מבנה**
- טעינת 2025.csv (134 עמודות, 310 שורות)
- זיהוי 6 עמודות עם נתונים בלבד

**שלב 2 – מחיקת עמודות עודפות**
- 128 עמודות ריקות לחלוטין ← נמחקו
- עמודת **מגרש** (52.3% חסרים) ← נמחקה
""")
    with col_b:
        st.markdown("""
**שלב 3 – מילוי ערכים חסרים**
- עמודת **גוש** (4 חסרים) ← ערך שכיח: `17216`
- עמודת **חלקה** (4 חסרים) ← ערך שכיח: `3`

**שלב 4 – בדיקת שכפולים**
- 0 שורות כפולות לחלוטין
- 2 מקרי חפיפה חלקית (ID שונה – נשמרו)
""")

st.markdown("<br>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TECH STACK
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="sec-hdr">🛠️ טכנולוגיות</div>', unsafe_allow_html=True)

st.markdown("""
<div class="badges">
  <div class="badge">🐍 Python 3.x</div>
  <div class="badge">📊 Streamlit</div>
  <div class="badge">🐼 Pandas</div>
  <div class="badge">🔢 NumPy</div>
  <div class="badge">📈 Plotly Express</div>
  <div class="badge">📁 CSV / Excel</div>
  <div class="badge">🎨 HTML + CSS</div>
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown("""
<hr style="border-color:#e8edf4; margin:8px 0 20px">
<div style="text-align:center; color:#999; font-size:.8rem;">
    סמסטר 22 · AI · ניתוח נתונים עם בינה מלאכותית &nbsp;|&nbsp;
    שיבלי-משרדית 2025
</div>
""", unsafe_allow_html=True)
