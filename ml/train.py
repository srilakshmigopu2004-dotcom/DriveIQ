"""Train an explainable (logistic regression) model on a REAL dataset you provide.

    python ml/train.py --data ml/datasets/your_real_data.csv --target placed

DriveIQ ships NO dataset and NO trained model: fabricated data would give meaningless metrics.
Metrics printed here come from a held-out test split and are saved to ml/evaluation/metrics.json.
"""
import argparse
import json
from pathlib import Path

import joblib
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, f1_score, precision_score, recall_score
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from preprocessing.features import FEATURES, load_dataset

HERE = Path(__file__).parent


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default=str(HERE / "datasets" / "placement_data.csv"))
    ap.add_argument("--target", default="placed")
    args = ap.parse_args()
    if not Path(args.data).exists():
        raise SystemExit(f"No dataset at {args.data}.\nAdd a legitimate dataset (see ml/README.md) and run again. "
                         "DriveIQ will not train on made-up data.")
    X, y = load_dataset(args.data, args.target)
    if len(X) < 100:
        print(f"WARNING: only {len(X)} rows. Metrics will be unreliable.")
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    model = make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000, class_weight="balanced"))
    model.fit(Xtr, ytr)
    pred = model.predict(Xte)
    avg = "binary" if y.nunique() == 2 else "weighted"
    metrics = {
        "rows": len(X), "test_rows": len(Xte),
        "accuracy": accuracy_score(yte, pred),
        "precision": precision_score(yte, pred, average=avg, zero_division=0),
        "recall": recall_score(yte, pred, average=avg, zero_division=0),
        "f1": f1_score(yte, pred, average=avg, zero_division=0),
        "cv_accuracy_mean": float(cross_val_score(model, X, y, cv=5).mean()),
        "features": FEATURES, "target": args.target,
    }
    print(classification_report(yte, pred, zero_division=0))
    print(json.dumps(metrics, indent=2))
    (HERE / "models").mkdir(exist_ok=True)
    joblib.dump(model, HERE / "models" / "model.joblib")
    (HERE / "evaluation" / "metrics.json").write_text(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
