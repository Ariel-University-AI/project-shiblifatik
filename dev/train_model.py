"""
Train a Random Forest classifier to predict job location (מקום) from
cadastral block number (גוש), year, and parcel count.

Run once from the project root:
    python train_model.py

Outputs:  models/model.pkl
"""

import re
import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import joblib

CSV_PATH   = Path("2025_cleaned.csv")
MODEL_DIR  = Path("models")
MODEL_PATH = MODEL_DIR / "model.pkl"
TOP_N      = 15          # keep top-N cities; rest → "אחר"
RANDOM_STATE = 42


# ── feature helpers ──────────────────────────────────────────────────────────

def first_number(val: str) -> int:
    m = re.search(r"\d+", str(val))
    return int(m.group()) if m else 0

def count_numbers(val: str) -> int:
    return len(re.findall(r"\d+", str(val)))

def build_features(df: pd.DataFrame) -> pd.DataFrame:
    X = pd.DataFrame()
    X["first_gush"]  = df["גוש"].apply(first_number)
    X["year"]        = df["מס עבודה"].astype(str).str[:2].astype(int) + 2000
    X["n_parcels"]   = df["חלקה"].apply(count_numbers)
    return X


# ── main ─────────────────────────────────────────────────────────────────────

def main():
    print("Loading data …")
    df = pd.read_csv(CSV_PATH, encoding="utf-8-sig")
    print(f"  {len(df)} rows, columns: {list(df.columns)}")

    # Target: top-N cities, everything else → "אחר"
    top_cities = df["מקום"].value_counts().head(TOP_N).index.tolist()
    df["target"] = df["מקום"].apply(lambda x: x if x in top_cities else "אחר")
    print(f"\nClass distribution (top {TOP_N} + אחר):")
    print(df["target"].value_counts().to_string())

    X = build_features(df)
    y = df["target"]

    print(f"\nFeatures:\n{X.describe().to_string()}")

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=RANDOM_STATE
    )
    print(f"\nTrain: {len(X_train)}  |  Test: {len(X_test)}")

    clf = RandomForestClassifier(
        n_estimators=200,
        max_depth=12,
        min_samples_leaf=2,
        class_weight="balanced",
        random_state=RANDOM_STATE,
        n_jobs=-1,
    )
    clf.fit(X_train, y_train)

    # ── evaluation ────────────────────────────────────────────────────────────
    y_pred = clf.predict(X_test)
    acc    = accuracy_score(y_test, y_pred)
    print(f"\nTest Accuracy : {acc:.4f}")
    print(classification_report(y_test, y_pred, zero_division=0))

    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)
    cv_scores = cross_val_score(clf, X, y, cv=cv, scoring="accuracy")
    print(f"CV (5-fold)   : {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")

    # ── feature importance ────────────────────────────────────────────────────
    feat_labels = ["גוש (ראשי)", "שנה", "מספר חלקות"]
    importances = dict(zip(feat_labels, clf.feature_importances_.tolist()))
    print(f"\nFeature importances: {importances}")

    # ── class distribution for chart ─────────────────────────────────────────
    class_dist = df["target"].value_counts().to_dict()

    # ── confusion matrix ──────────────────────────────────────────────────────
    cm_labels = sorted(y.unique())
    cm        = confusion_matrix(y_test, y_pred, labels=cm_labels)

    # ── save ─────────────────────────────────────────────────────────────────
    MODEL_DIR.mkdir(exist_ok=True)
    payload = {
        "clf":           clf,
        "feature_names": ["first_gush", "year", "n_parcels"],
        "feature_labels": feat_labels,
        "classes":        clf.classes_.tolist(),
        "top_cities":     top_cities,
        "accuracy":       round(float(acc), 4),
        "cv_mean":        round(float(cv_scores.mean()), 4),
        "cv_std":         round(float(cv_scores.std()), 4),
        "train_size":     int(len(X_train)),
        "test_size":      int(len(X_test)),
        "importances":    importances,
        "class_dist":     class_dist,
        "cm":             cm.tolist(),
        "cm_labels":      cm_labels,
    }
    joblib.dump(payload, MODEL_PATH)
    print(f"\nModel saved → {MODEL_PATH}")
    print("Done.")


if __name__ == "__main__":
    main()
