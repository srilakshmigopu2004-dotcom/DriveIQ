"""Feature definitions shared by training and prediction."""
FEATURES = ["cgpa", "backlogs", "dsa_level", "aptitude_level", "communication_level",
            "projects_count", "internships_count", "sql_level", "programming_level"]


def load_dataset(path, target):
    import pandas as pd
    df = pd.read_csv(path)
    missing = [c for c in FEATURES + [target] if c not in df.columns]
    if missing:
        raise SystemExit(f"Dataset is missing required columns: {missing}\nRequired: {FEATURES + [target]}")
    df = df[FEATURES + [target]].dropna()
    if df[target].nunique() < 2:
        raise SystemExit("Target column needs at least two classes.")
    return df[FEATURES], df[target]
