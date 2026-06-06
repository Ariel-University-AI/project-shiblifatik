import pandas as pd
import numpy as np

def clean_survey_data(file_path):
    print(f"--- טוען נתונים מהקובץ: {file_path} ---")
    # טעינת הקובץ. הערה: הוספנו את '/' כערך חסר כי ראינו שככה זה מופיע בקובץ שלך.
    try:
        df = pd.read_csv(file_path, na_values=['/'])
    except Exception as e:
        print(f"שגיאה בקריאת הקובץ: {e}")
        return

    # הצג סיכום לפני
    print("\n--- סיכום לפני ניקוי ---")
    print(f"מספר שורות: {len(df)}")
    print(f"מספר עמודות: {len(df.columns)}")
    print("\nערכים חסרים לפי עמודה:")
    missing_before = df.isna().sum()
    print(missing_before)

    # === בדיקת שכפולים (כפילויות) ===
    print("\n--- בדיקת שכפולים ---")
    # מחפש שורות שזהות לחלוטין אחת לשנייה
    duplicate_rows = df[df.duplicated(keep=False)] 
    num_duplicates = df.duplicated().sum() # סופר כמה שורות מיותרות יש (מעבר לפעם הראשונה)
    
    print(f"כמה שורות כפולות נמצאו? {num_duplicates}")
    if num_duplicates > 0:
        print("מציג את השורות הזהות:")
        print(duplicate_rows)
        # מחיקת השכפולים ושמירת השורה הראשונה בלבד
        df.drop_duplicates(keep='first', inplace=True)
        print("✅ הקוד מחק את תרשומות הכפולות, שמרתי רק את הראשונה.")
        
        # עדכון ספירת החסרים אחרי מחיקת השורות הכפולות כדי שהחישובים הבאים יהיו מדויקים
        missing_before = df.isna().sum()
    else:
        print("✅ לא נמצאו שורות כפולות בקובץ.")

    # מחיקת עמודות עם יותר מ-50% ערכים חסרים
    threshold = 0.5 * len(df) # מחצית מהשורות
    columns_to_drop = missing_before[missing_before > threshold].index
    if len(columns_to_drop) > 0:
        print(f"\nמוחק עמודות עם יותר מ-50% ערכים חסרים: {list(columns_to_drop)}")
        df.drop(columns=columns_to_drop, inplace=True)
    else:
        print("\nלא נמצאו עמודות עם מעל 50% חסרים.")

    # מילוי ערכים חסרים בעמודות שנשארו
    for col in df.columns:
        if df[col].isna().sum() > 0: # אם יש ערכים חסרים בעמודה
            if pd.api.types.is_numeric_dtype(df[col]):
                # אם העמודה מספרית - מלא בממוצע
                mean_val = df[col].mean()
                df[col] = df[col].fillna(mean_val) # סוגר ישירות על העמודה למניעת שגיאות FutureWarning
                print(f"עמודה '{col}' (מספרית) התמלאה בממוצע: {mean_val:.2f}")
            else:
                # אם העמודה קטגורית/טקסט - מלא בערך השכיח
                mode_val = df[col].mode()[0]
                df[col] = df[col].fillna(mode_val) # סוגר ישירות על העמודה
                print(f"עמודה '{col}' (קטגורית) התמלאה בערך השכיח: '{mode_val}'")

    # הצג סיכום אחרי
    print("\n--- סיכום אחרי ניקוי ---")
    print(f"מספר שורות: {len(df)}")
    print(f"מספר עמודות: {len(df.columns)}")
    print("\nערכים חסרים לפי עמודה:")
    print(df.isna().sum())

    # שמירת הקובץ הנקי בסיום בקידוד התומך בעברית
    output_path = file_path.replace('.csv', '_cleaned.csv')
    df.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f"\nהקובץ הנקי נשמר כ- {output_path}")

# הפעלת הפונקציה על קובץ הניסוי שלנו
clean_survey_data('ניסוי.csv')
# ניתן להוסיף כאן גם את הקובץ הגדול:
# clean_survey_data('04-2026-יומן עבודות.csv')
