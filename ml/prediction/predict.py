"""Explainable prediction: probability + which features pushed it up or down."""
from pathlib import Path

import joblib

from preprocessing.features import FEATURES

MODEL_PATH = Path(__file__).resolve().parent.parent / "models" / "model.joblib"
NOTE = "Model output reflects patterns in the training dataset only. It is NOT a guarantee of selection."


def predict(row: dict):
    if not MODEL_PATH.exists():
        raise FileNotFoundError("No trained model. Run ml/train.py with a real dataset first.")
    model = joblib.load(MODEL_PATH)
    scaler, clf = model.steps[0][1], model.steps[1][1]
    x = scaler.transform([[row[f] for f in FEATURES]])[0]
    contrib = sorted(zip(FEATURES, (x * clf.coef_[0]).tolist()), key=lambda t: -abs(t[1]))
    prob = float(model.predict_proba([[row[f] for f in FEATURES]])[0][1])
    return {"probability": prob, "top_factors": [{"feature": f, "effect": round(c, 3)} for f, c in contrib[:5]], "note": NOTE}
